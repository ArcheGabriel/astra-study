"""Offline structural evaluation of the chunking pipeline.

Stage 5 tooling. This module NEVER writes to Qdrant, the database, or any
application state. It consumes the production ``DoclingProcessor`` and
``ChunkPipeline`` unchanged and reports structural metrics about the chunks
they produce.

Design notes
------------
* The Docling extraction step and the chunking step are decoupled: ``extract``
  serialises the source blocks to JSON so the *identical* input can be fed to
  two different checkouts of the chunking code (pre-refactor vs frozen
  Stage 1-4). This isolates the comparison to chunking behaviour and removes
  Docling/OCR run-to-run noise from the diff.
* Every reader of chunk metadata uses ``getattr(..., default)`` so the module
  also runs against the pre-refactor tree, where ``ChunkMetadata.section_key``
  and the token-based ``ChunkingConfig`` do not exist.
* ``EMBED_MAX_REFERENCE`` is an *evaluation* constant (the embedding contract
  ceiling), deliberately fixed so "over the limit" means the same thing for
  both trees regardless of their ``ChunkingConfig``.

CLI
---
    uv run python -m evaluation.chunking_report extract --doc <path> --out <blocks.json>
    uv run python -m evaluation.chunking_report analyze --blocks <blocks.json> \
        --out <report.json> [--runs 2]
    uv run python -m evaluation.chunking_report compare --baseline <a.json> \
        --after <b.json> --out-json <c.json> --out-text <c.txt>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.chunking.models import DocumentChunk
from app.chunking.pipeline import ChunkPipeline
from app.chunking.stages.filter import FilterStage
from app.document.models import BlockProvenance, DocumentBlock
from app.enums.block import BlockType
from app.ingestion.models import DocumentMetadata, ExtractionResult
from app.ingestion.processors.docling import DoclingProcessor

# The embedding contract ceiling. Fixed here (not read from ChunkingConfig) so
# the "over the limit" metric is comparable across the pre-refactor tree (whose
# ChunkingConfig is character-based and has no embed_max) and the frozen tree.
EMBED_MAX_REFERENCE = 700

# Report schema version -- bump when the metric surface changes.
SCHEMA_VERSION = 1


# ======================================================================
# Serialisation of the Docling extraction (shared input for both trees)
# ======================================================================


def _provenance_to_dict(ref: BlockProvenance) -> dict[str, Any]:
    return {
        "page_number": ref.page_number,
        "bbox": ref.bbox,
        "source_item_id": ref.source_item_id,
        "charspan": list(ref.charspan) if ref.charspan is not None else None,
        "sheet_name": ref.sheet_name,
        "table_index": ref.table_index,
    }


def _provenance_from_dict(data: dict[str, Any]) -> BlockProvenance:
    charspan = data.get("charspan")
    return BlockProvenance(
        page_number=data.get("page_number"),
        bbox=data.get("bbox"),
        source_item_id=data.get("source_item_id"),
        charspan=tuple(charspan) if charspan is not None else None,
        sheet_name=data.get("sheet_name"),
        table_index=data.get("table_index"),
    )


def _block_to_dict(block: DocumentBlock) -> dict[str, Any]:
    return {
        "text": block.text,
        "block_type": block.block_type.value,
        "level": block.level,
        "page_number": block.page_number,
        "block_index": block.block_index,
        "metadata": dict(block.metadata),
        "provenance": [_provenance_to_dict(ref) for ref in block.provenance],
    }


def _block_from_dict(data: dict[str, Any]) -> DocumentBlock:
    return DocumentBlock(
        text=data["text"],
        block_type=BlockType(data["block_type"]),
        level=data.get("level", 0),
        page_number=data.get("page_number"),
        block_index=data.get("block_index"),
        metadata=dict(data.get("metadata", {})),
        provenance=[_provenance_from_dict(r) for r in data.get("provenance", [])],
    )


def extract(doc_path: Path) -> dict[str, Any]:
    """Run the production Docling extraction and return a JSON-serialisable
    payload (document identity + source blocks). No chunking here."""

    processor = DoclingProcessor()
    result = processor.extract(doc_path)

    raw = doc_path.read_bytes()

    return {
        "schema_version": SCHEMA_VERSION,
        "document": {
            "name": doc_path.name,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw),
            "page_count": result.metadata.page_count,
            "file_extension": result.metadata.file_extension,
        },
        "blocks": [_block_to_dict(b) for b in result.blocks],
    }


def _extraction_from_payload(payload: dict[str, Any]) -> ExtractionResult:
    doc = payload["document"]
    blocks = [_block_from_dict(b) for b in payload["blocks"]]
    metadata = DocumentMetadata(
        file_name=doc["name"],
        file_extension=doc.get("file_extension"),
        file_size=doc.get("size_bytes", 0),
        page_count=doc.get("page_count", 0),
        checksum=doc["sha256"],
    )
    return ExtractionResult(metadata=metadata, blocks=blocks, tables=[])


# ======================================================================
# Instrumented pipeline run
# ======================================================================


@dataclass
class StageTrace:
    final_chunks: list[DocumentChunk]
    stage_output_counts: list[tuple[str, int]]
    pre_filter_chunks: list[DocumentChunk]
    post_filter_chunks: list[DocumentChunk]


def _run_instrumented(extraction: ExtractionResult) -> StageTrace:
    """Mirror ``ChunkPipeline.run`` but record per-stage output counts and the
    chunk lists immediately before / after ``FilterStage``."""

    stages = ChunkPipeline().stages

    data: Any = extraction
    counts: list[tuple[str, int]] = []
    pre_filter: list[DocumentChunk] = []
    post_filter: list[DocumentChunk] = []

    for stage in stages:
        if isinstance(stage, FilterStage):
            pre_filter = list(data)

        data = stage.run(data)

        length = len(data.blocks) if isinstance(data, ExtractionResult) else len(data)
        counts.append((stage.__class__.__name__, length))

        if isinstance(stage, FilterStage):
            post_filter = list(data)

    return StageTrace(
        final_chunks=list(data),
        stage_output_counts=counts,
        pre_filter_chunks=pre_filter,
        post_filter_chunks=post_filter,
    )


# ======================================================================
# Metric helpers (pure; unit-tested without Docling)
# ======================================================================


def _tok(text: str) -> int:
    from app.chunking.utils.tokens import count_tokens

    return count_tokens(text)


def _num_stats(values: list[int]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None,
                "median": None, "p90": None, "p99": None}
    ordered = sorted(values)

    def pct(p: float) -> int:
        idx = max(0, min(len(ordered) - 1, round(p / 100 * (len(ordered) - 1))))
        return ordered[idx]

    return {
        "count": len(values),
        "min": ordered[0],
        "max": ordered[-1],
        "mean": round(statistics.fmean(ordered), 2),
        "median": round(statistics.median(ordered), 2),
        "p90": pct(90),
        "p99": pct(99),
    }


def _heading_candidates(chunk: DocumentChunk) -> set[str]:
    section_title = getattr(chunk.metadata, "section_title", None)
    heading_path = getattr(chunk.metadata, "heading_path", None) or []
    values = ([section_title] if section_title else []) + list(heading_path)
    return {v.strip().lstrip("#").strip().casefold() for v in values if v}


def _chunk_body(chunk: DocumentChunk) -> str:
    """The text with a leading folded-heading line removed (evaluator view)."""
    text = chunk.text.strip()
    if "\n\n" in text:
        first, _, rest = text.partition("\n\n")
        if first.strip().lstrip("#").strip().casefold() in _heading_candidates(chunk):
            return rest.strip()
    return text


def _is_content_free(chunk: DocumentChunk) -> bool:
    """Evaluator-only heuristic: the chunk carries no body beyond its heading."""
    if not chunk.text.strip():
        return True
    body = _chunk_body(chunk)
    if not body:
        return True
    return body.casefold() in _heading_candidates(chunk)


def _expected_prefix(chunk: DocumentChunk) -> str | None:
    path = [p.strip() for p in (getattr(chunk.metadata, "heading_path", None) or [])
            if p and p.strip()]
    if not path:
        return None
    if len(path) >= 3:
        return f"{path[-2]} › {path[-1]}"
    return path[-1]


def _prefix_status(chunk: DocumentChunk) -> str:
    """'absent-ok' | 'present' | 'missing' | 'duplicated'.

    "duplicated" means the heading appears as its own *paragraph* more than
    once (a genuine double-fold), not merely as a substring of body prose such
    as a figure caption that repeats the heading phrase.
    """
    prefix = _expected_prefix(chunk)
    if prefix is None:
        return "absent-ok"
    path = [p.strip() for p in (getattr(chunk.metadata, "heading_path", None) or [])
            if p and p.strip()]
    deepest = path[-1] if path else ""

    paragraphs = [p.strip().lstrip("#").strip() for p in chunk.text.split("\n\n")]
    targets = {t for t in (prefix, deepest) if t}
    para_hits = sum(1 for p in paragraphs if p in targets)

    leads = chunk.text.startswith(prefix + "\n\n") or (
        deepest and chunk.text.startswith(deepest + "\n\n"))

    if para_hits >= 2:
        return "duplicated"
    if leads:
        return "present"
    if para_hits == 1 or (deepest and deepest in chunk.text) or prefix in chunk.text:
        return "present-not-leading"
    return "missing"


def _page_range_valid(chunk: DocumentChunk) -> bool:
    ps = getattr(chunk.metadata, "page_start", None)
    pe = getattr(chunk.metadata, "page_end", None)
    if ps is None or pe is None:
        return True
    if ps <= 0 or pe <= 0:
        return False
    return ps <= pe


def _block_range_valid(chunk: DocumentChunk) -> bool:
    ps = getattr(chunk.metadata, "page_start", None)
    pe = getattr(chunk.metadata, "page_end", None)
    bs = getattr(chunk.metadata, "block_start", None)
    be = getattr(chunk.metadata, "block_end", None)
    if bs is None or be is None:
        return True
    if ps is not None and pe is not None and ps != pe:
        return True  # block numbering restarts per page
    return bs <= be


def _prov_pages(chunk: DocumentChunk) -> list[int]:
    return [r.page_number for r in getattr(chunk.metadata, "provenance", []) or []
            if getattr(r, "page_number", None) is not None]


def _page_range_matches_provenance(chunk: DocumentChunk) -> bool:
    """The reported page range must not fall outside the pages named by the
    chunk's own provenance (heading context may add extra pages but must not
    widen beyond the union)."""
    ps = getattr(chunk.metadata, "page_start", None)
    pe = getattr(chunk.metadata, "page_end", None)
    pages = _prov_pages(chunk)
    if ps is None or pe is None or not pages:
        return True
    return min(pages) <= ps <= pe <= max(pages)


def _looks_like_md_table_row(line: str) -> bool:
    return line.count("|") >= 2


def _table_content_audit(
    source_blocks: list[DocumentBlock],
    chunks: list[DocumentChunk],
) -> dict[str, Any]:
    """For every source TABLE block, follow its ``source_item_id`` into the
    chunks that carry it and check whether its markdown rows survived intact
    (no chunk boundary fell mid-row) -- regardless of the carrier chunk's
    effective ``block_type``."""

    per_table = []
    total_rows = 0
    total_intact = 0

    for block in source_blocks:
        if block.block_type != BlockType.TABLE:
            continue
        item_id = block.provenance[0].source_item_id if block.provenance else None
        rows = [ln.strip() for ln in block.text.split("\n") if ln.strip()]

        carriers = [
            c for c in chunks
            if item_id is not None and any(
                getattr(r, "source_item_id", None) == item_id
                for r in (getattr(c.metadata, "provenance", []) or [])
            )
        ]
        carrier_lines: set[str] = set()
        for c in carriers:
            for ln in _chunk_body(c).split("\n"):
                carrier_lines.add(ln.strip())

        intact = sum(1 for r in rows if r in carrier_lines)
        total_rows += len(rows)
        total_intact += intact

        per_table.append({
            "source_item_id": item_id,
            "page": block.page_number,
            "row_count": len(rows),
            "rows_intact": intact,
            "rows_split": len(rows) - intact,
            "carrier_chunk_indexes": [c.chunk_index for c in carriers],
            "carrier_block_types": sorted({
                (getattr(c.metadata, "block_type", None).value
                 if getattr(c.metadata, "block_type", None) else None)
                for c in carriers
            }),
            "any_carrier_typed_table": any(
                getattr(c.metadata, "block_type", None) == BlockType.TABLE
                for c in carriers
            ),
        })

    return {
        "source_table_blocks": len(per_table),
        "total_rows": total_rows,
        "total_rows_intact": total_intact,
        "total_rows_split": total_rows - total_intact,
        "tables": per_table,
    }


def _list_content_audit(
    source_blocks: list[DocumentBlock],
    chunks: list[DocumentChunk],
) -> dict[str, Any]:
    """For every source LIST block, follow its ``source_item_id`` into the
    chunks that carry it and check whether the item survived as one intact
    unit (its whole text is a substring of a single carrier chunk). An item
    larger than the reference budget is an accepted indivisible exception."""

    split_items = []
    no_carrier = []
    total = 0
    intact = 0
    oversized = 0

    norm_bodies = {id(c): _norm_ws(_chunk_body(c)) for c in chunks}

    for block in source_blocks:
        if block.block_type != BlockType.LIST:
            continue
        item_id = block.provenance[0].source_item_id if block.provenance else None
        item_text = _norm_ws(block.text)
        if not item_text:
            continue
        total += 1
        item_oversized = _tok(block.text) > EMBED_MAX_REFERENCE
        if item_oversized:
            oversized += 1

        carriers = [
            c for c in chunks
            if item_id is not None and any(
                getattr(r, "source_item_id", None) == item_id
                for r in (getattr(c.metadata, "provenance", []) or [])
            )
        ]
        if item_oversized:
            intact += 1
        elif not carriers:
            # provenance for this item was not attributed to any chunk
            no_carrier.append({"source_item_id": item_id, "page": block.page_number})
        elif any(item_text in norm_bodies[id(c)] for c in carriers):
            intact += 1
        else:
            split_items.append({
                "source_item_id": item_id,
                "page": block.page_number,
                "carrier_chunk_indexes": [c.chunk_index for c in carriers],
            })

    return {
        "source_list_blocks": total,
        "items_intact_or_oversized": intact,
        "items_split_across_chunks": len(split_items),
        "items_without_carrier": len(no_carrier),
        "oversized_items": oversized,
        "split_items": split_items,
        "no_carrier_items": no_carrier,
    }


def _norm_ws(text: str) -> str:
    return " ".join(text.split())


def _table_rows_intact(chunk: DocumentChunk) -> bool:
    """A TABLE chunk must contain only whole markdown rows (no line that starts
    or ends mid-cell). We approximate: every non-empty body line has >= 2 pipes
    or is a prose/heading line (the folded prefix)."""
    body = _chunk_body(chunk)
    lines = [ln for ln in body.split("\n") if ln.strip()]
    table_lines = [ln for ln in lines if "|" in ln]
    return all(_looks_like_md_table_row(ln) for ln in table_lines)


# ======================================================================
# Report
# ======================================================================


def _sample(chunk: DocumentChunk, note: str = "") -> dict[str, Any]:
    text = chunk.text
    return {
        "chunk_index": chunk.chunk_index,
        "parent_chunk": chunk.parent_chunk,
        "block_type": getattr(chunk.metadata, "block_type", None).value
        if getattr(chunk.metadata, "block_type", None) is not None else None,
        "heading_path": list(getattr(chunk.metadata, "heading_path", None) or []),
        "section_id": getattr(chunk.metadata, "section_id", None),
        "section_title": getattr(chunk.metadata, "section_title", None),
        "pages": [getattr(chunk.metadata, "page_start", None),
                  getattr(chunk.metadata, "page_end", None)],
        "blocks": [getattr(chunk.metadata, "block_start", None),
                   getattr(chunk.metadata, "block_end", None)],
        "tokens": _tok(text),
        "provenance_entries": len(getattr(chunk.metadata, "provenance", []) or []),
        "provenance_item_ids": sorted({
            r.source_item_id for r in (getattr(chunk.metadata, "provenance", []) or [])
            if getattr(r, "source_item_id", None) is not None
        }),
        "quality_score": getattr(chunk.metadata, "quality_score", None),
        "retrieval_priority": getattr(chunk.metadata, "retrieval_priority", None),
        "prefix_status": _prefix_status(chunk),
        "text_head": text[:400],
        "text_tail": text[-200:] if len(text) > 600 else "",
        "note": note,
    }


def _pick_samples(
    chunks: list[DocumentChunk],
    table_item_ids: set[str] | None = None,
) -> dict[str, Any]:
    table_item_ids = table_item_ids or set()

    def first(pred, note=""):
        for c in chunks:
            if pred(c):
                return _sample(c, note)
        return "absent"

    def bt(c):
        v = getattr(c.metadata, "block_type", None)
        return v.value if v is not None else None

    def carries_table(c):
        return any(getattr(r, "source_item_id", None) in table_item_ids
                   for r in (getattr(c.metadata, "provenance", []) or []))

    return {
        "ordinary_prose": first(
            lambda c: bt(c) == "text" and c.parent_chunk is None
            and _tok(c.text) > 120 and len(getattr(c.metadata, "heading_path", []) or []) >= 1),
        "heading_folded": first(
            lambda c: _prefix_status(c) == "present" and not _is_content_free(c)
            and "\n\n" in c.text),
        "nested_section": first(
            lambda c: len(getattr(c.metadata, "heading_path", []) or []) >= 2),
        "table_content": first(carries_table,
                               note="chunk carrying a source TABLE block's provenance"),
        "oversized_table_content": first(
            lambda c: carries_table(c) and c.parent_chunk is not None,
            note="table content that was split across recursive children"),
        "list": first(lambda c: bt(c) == "list"),
        "caption": first(lambda c: bt(c) == "caption"),
        "multi_page": first(
            lambda c: getattr(c.metadata, "page_start", None) is not None
            and getattr(c.metadata, "page_end", None) is not None
            and c.metadata.page_start != c.metadata.page_end),
        "hard_boundary_continuation": first(
            lambda c: c.parent_chunk is not None and bt(c) == "text",
            note="recursive child of an oversized section"),
        "reference_or_appendix": first(
            lambda c: getattr(c.metadata, "is_reference", False)
            or getattr(c.metadata, "is_appendix", False)),
    }


def analyze(payload: dict[str, Any], runs: int = 2) -> dict[str, Any]:
    """Full structural report for one document's serialised blocks."""

    extraction = _extraction_from_payload(payload)
    source_blocks = list(extraction.blocks)

    trace = _run_instrumented(_extraction_from_payload(payload))
    chunks = trace.final_chunks

    # ---- determinism: re-run chunking N times on the same blocks ----
    signatures = []
    for _ in range(max(runs, 1)):
        t = _run_instrumented(_extraction_from_payload(payload))
        signatures.append([
            (
                c.chunk_index, c.parent_chunk, c.text,
                str(getattr(c.metadata, "chunk_uuid", None)),
                getattr(c.metadata, "page_start", None),
                getattr(c.metadata, "page_end", None),
                getattr(c.metadata, "block_start", None),
                getattr(c.metadata, "block_end", None),
                getattr(c.metadata, "quality_score", None),
                tuple(sorted(
                    r.source_item_id for r in (getattr(c.metadata, "provenance", []) or [])
                    if getattr(r, "source_item_id", None) is not None
                )),
            )
            for c in t.final_chunks
        ])
    deterministic = all(s == signatures[0] for s in signatures)

    # ---- source-block metrics ----
    src_type_dist = Counter(b.block_type.value for b in source_blocks)
    src_item_ids = {
        r.source_item_id for b in source_blocks for r in b.provenance
        if r.source_item_id is not None
    }
    table_item_ids = {
        r.source_item_id for b in source_blocks if b.block_type == BlockType.TABLE
        for r in b.provenance if r.source_item_id is not None
    }

    # ---- chunk token metrics ----
    tokens = [_tok(c.text) for c in chunks]
    over = [c for c in chunks if _tok(c.text) > EMBED_MAX_REFERENCE]

    def bt(c):
        v = getattr(c.metadata, "block_type", None)
        return v.value if v is not None else None

    eff_type_dist = Counter(bt(c) for c in chunks)
    content_free = [c for c in chunks if _is_content_free(c)]

    # ---- filter behaviour ----
    pre_norm = Counter(" ".join(c.text.split()) for c in trace.pre_filter_chunks)
    exact_dupes_in = sum(v - 1 for v in pre_norm.values() if v > 1)
    removed = len(trace.pre_filter_chunks) - len(trace.post_filter_chunks)

    # ---- provenance ----
    with_prov = [c for c in chunks if getattr(c.metadata, "provenance", None)]
    chunk_item_ids = {
        r.source_item_id for c in chunks
        for r in (getattr(c.metadata, "provenance", []) or [])
        if getattr(r, "source_item_id", None) is not None
    }
    fabricated = sorted(chunk_item_ids - src_item_ids)
    # Proxy for the documented "keep full provenance list" fallback: all of an
    # oversized section's recursive children carry the *identical* multi-item
    # provenance set (partitioning would have narrowed at least one child).
    fallback_suspected = 0
    by_parent: dict[int, list[DocumentChunk]] = {}
    for c in chunks:
        if c.parent_chunk is not None:
            by_parent.setdefault(c.parent_chunk, []).append(c)
    for sibs in by_parent.values():
        if len(sibs) < 2:
            continue
        prov_sets = [
            frozenset(
                r.source_item_id for r in (getattr(c.metadata, "provenance", []) or [])
                if getattr(r, "source_item_id", None) is not None
            )
            for c in sibs
        ]
        if prov_sets and all(ps == prov_sets[0] for ps in prov_sets) and len(prov_sets[0]) > 1:
            fallback_suspected += len(sibs)

    # ---- ranges ----
    page_bad = [c.chunk_index for c in chunks if not _page_range_valid(c)]
    block_bad = [c.chunk_index for c in chunks if not _block_range_valid(c)]
    page_vs_prov_bad = [
        c.chunk_index for c in chunks if not _page_range_matches_provenance(c)
    ]

    # ---- heading prefix ----
    prefix_dist = Counter(_prefix_status(c) for c in chunks)

    # ---- section boundary ----
    section_keys = [tuple(getattr(c.metadata, "section_key", ()) or ()) for c in chunks]
    distinct_keys = len({k for k in section_keys})

    # ---- atomicity ----
    table_chunks = [c for c in chunks if bt(c) == "table"]
    list_chunks = [c for c in chunks if bt(c) == "list"]
    caption_chunks = [c for c in chunks if bt(c) == "caption"]
    text_chunks = [c for c in chunks if bt(c) == "text"]
    tables_rows_ok = sum(_table_rows_intact(c) for c in table_chunks)

    # ---- quality / priority ----
    q_dist = Counter(round(getattr(c.metadata, "quality_score", 0.0) or 0.0, 2) for c in chunks)
    p_dist = Counter(getattr(c.metadata, "retrieval_priority", None) for c in chunks)
    flag_counts = {
        "is_reference": sum(getattr(c.metadata, "is_reference", False) for c in chunks),
        "is_appendix": sum(getattr(c.metadata, "is_appendix", False) for c in chunks),
        "is_metadata": sum(getattr(c.metadata, "is_metadata", False) for c in chunks),
        "is_caption": sum(getattr(c.metadata, "is_caption", False) for c in chunks),
        "is_table": sum(getattr(c.metadata, "is_table", False) for c in chunks),
        "is_formula": sum(getattr(c.metadata, "is_formula", False) for c in chunks),
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "document": payload["document"],
        "source_blocks": {
            "count": len(source_blocks),
            "type_distribution": dict(sorted(src_type_dist.items())),
            "unique_source_item_ids": len(src_item_ids),
        },
        "pipeline_stage_counts": trace.stage_output_counts,
        "chunks": {
            "count": len(chunks),
            "token_distribution": _num_stats(tokens),
            "over_embed_max_reference": {
                "reference": EMBED_MAX_REFERENCE,
                "count": len(over),
                "pct": round(100 * len(over) / len(chunks), 2) if chunks else 0.0,
                "details": [
                    {"chunk_index": c.chunk_index, "tokens": _tok(c.text),
                     "block_type": bt(c), "parent_chunk": c.parent_chunk,
                     "section_title": getattr(c.metadata, "section_title", None)}
                    for c in over
                ],
            },
            "content_free_or_heading_only": {
                "count": len(content_free),
                "details": [
                    {"chunk_index": c.chunk_index, "block_type": bt(c),
                     "text_head": c.text[:160]}
                    for c in content_free
                ],
            },
            "effective_block_type_distribution": dict(sorted(
                (k or "none", v) for k, v in eff_type_dist.items())),
            "type_counts": {
                "table": len(table_chunks),
                "list": len(list_chunks),
                "caption": len(caption_chunks),
                "text": len(text_chunks),
            },
            "quality_score_distribution": dict(sorted(q_dist.items())),
            "retrieval_priority_distribution": dict(sorted(
                (str(k), v) for k, v in p_dist.items())),
            "classification_flag_counts": flag_counts,
        },
        "filter": {
            "chunks_before_filter": len(trace.pre_filter_chunks),
            "chunks_after_filter": len(trace.post_filter_chunks),
            "removed": removed,
            "exact_duplicate_groups_before_filter": sum(
                1 for v in pre_norm.values() if v > 1),
            "exact_duplicate_extra_copies_before_filter": exact_dupes_in,
        },
        "provenance": {
            "chunks_total": len(chunks),
            "chunks_with_provenance": len(with_prov),
            "coverage_pct": round(100 * len(with_prov) / len(chunks), 2) if chunks else 0.0,
            "unique_source_item_ids_in_chunks": len(chunk_item_ids),
            "unique_source_item_ids_in_source": len(src_item_ids),
            "source_item_id_coverage_pct": round(
                100 * len(chunk_item_ids & src_item_ids) / len(src_item_ids), 2
            ) if src_item_ids else None,
            "fabricated_source_item_ids": fabricated,
            "full_list_fallback_suspected_chunks": fallback_suspected,
        },
        "ranges": {
            "page_range_invalid_chunks": page_bad,
            "block_range_invalid_chunks": block_bad,
            "page_range_outside_provenance_chunks": page_vs_prov_bad,
        },
        "heading_prefix": {
            "status_distribution": dict(sorted(prefix_dist.items())),
        },
        "section_boundary": {
            "distinct_section_keys": distinct_keys,
            "chunks_with_section_key": sum(1 for k in section_keys if k),
        },
        "atomicity": {
            "table_chunks": len(table_chunks),
            "table_chunks_with_intact_rows": tables_rows_ok,
            "list_chunks": len(list_chunks),
        },
        "table_content_audit": _table_content_audit(source_blocks, chunks),
        "list_content_audit": _list_content_audit(source_blocks, chunks),
        "determinism": {
            "runs": max(runs, 1),
            "identical": deterministic,
        },
        "samples": _pick_samples(chunks, table_item_ids),
    }


# ======================================================================
# Comparison
# ======================================================================

_SCALAR_PATHS = [
    ("source_blocks.count", "source block count"),
    ("source_blocks.unique_source_item_ids", "unique source item ids"),
    ("chunks.count", "final chunk count"),
    ("chunks.token_distribution.min", "token min"),
    ("chunks.token_distribution.median", "token median"),
    ("chunks.token_distribution.mean", "token mean"),
    ("chunks.token_distribution.max", "token max"),
    ("chunks.token_distribution.p90", "token p90"),
    ("chunks.token_distribution.p99", "token p99"),
    ("chunks.over_embed_max_reference.count", "chunks over 700 tokens"),
    ("chunks.content_free_or_heading_only.count", "content-free / heading-only vectors"),
    ("chunks.type_counts.table", "table chunks"),
    ("chunks.type_counts.list", "list chunks"),
    ("chunks.type_counts.caption", "caption chunks"),
    ("chunks.type_counts.text", "text chunks"),
    ("filter.removed", "chunks removed by FilterStage"),
    ("filter.exact_duplicate_extra_copies_before_filter", "exact duplicate copies pre-filter"),
    ("provenance.coverage_pct", "provenance coverage %"),
    ("provenance.unique_source_item_ids_in_chunks", "unique source item ids in chunks"),
    ("provenance.source_item_id_coverage_pct", "source item id coverage %"),
    ("provenance.full_list_fallback_suspected_chunks", "full-list-fallback suspected chunks"),
    ("section_boundary.distinct_section_keys", "distinct section keys"),
    ("atomicity.table_chunks", "atomicity: table-typed chunks"),
    ("table_content_audit.source_table_blocks", "source table blocks"),
    ("table_content_audit.total_rows", "table rows (total)"),
    ("table_content_audit.total_rows_split", "table rows split across chunks"),
    ("list_content_audit.source_list_blocks", "source list blocks"),
    ("list_content_audit.items_split_across_chunks", "list items split across chunks"),
    ("list_content_audit.items_without_carrier", "list items with no carrier chunk"),
    ("list_content_audit.oversized_items", "list items over budget (exception)"),
]


def _dig(obj: dict[str, Any], dotted: str) -> Any:
    cur: Any = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def compare(baseline: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for path, label in _SCALAR_PATHS:
        b = _dig(baseline, path)
        a = _dig(after, path)
        delta: Any
        if isinstance(b, (int, float)) and isinstance(a, (int, float)):
            delta = round(a - b, 2)
        elif b == a:
            delta = 0
        else:
            delta = f"{b} -> {a}"
        rows.append({"metric": label, "path": path, "baseline": b,
                     "after": a, "delta": delta})

    return {
        "document": after.get("document", {}).get("name"),
        "baseline_determinism": _dig(baseline, "determinism.identical"),
        "after_determinism": _dig(after, "determinism.identical"),
        "rows": rows,
        "baseline_prefix_status": _dig(baseline, "heading_prefix.status_distribution"),
        "after_prefix_status": _dig(after, "heading_prefix.status_distribution"),
        "baseline_effective_types": _dig(baseline, "chunks.effective_block_type_distribution"),
        "after_effective_types": _dig(after, "chunks.effective_block_type_distribution"),
        "baseline_quality_dist": _dig(baseline, "chunks.quality_score_distribution"),
        "after_quality_dist": _dig(after, "chunks.quality_score_distribution"),
    }


def render_comparison_text(comparisons: list[dict[str, Any]]) -> str:
    out: list[str] = []
    for cmp in comparisons:
        out.append("=" * 78)
        out.append(f"DOCUMENT: {cmp['document']}")
        out.append("=" * 78)
        out.append(f"determinism  baseline={cmp['baseline_determinism']}  "
                   f"after={cmp['after_determinism']}")
        out.append("")
        out.append(f"{'metric':<44}{'baseline':>12}{'after':>12}{'delta':>10}")
        out.append("-" * 78)
        for row in cmp["rows"]:
            out.append(f"{row['metric']:<44}{str(row['baseline']):>12}"
                       f"{str(row['after']):>12}{str(row['delta']):>10}")
        out.append("")
        out.append(f"effective block types  baseline={cmp['baseline_effective_types']}")
        out.append(f"effective block types  after   ={cmp['after_effective_types']}")
        out.append(f"heading-prefix status  baseline={cmp['baseline_prefix_status']}")
        out.append(f"heading-prefix status  after   ={cmp['after_prefix_status']}")
        out.append(f"quality distribution   baseline={cmp['baseline_quality_dist']}")
        out.append(f"quality distribution   after   ={cmp['after_quality_dist']}")
        out.append("")
    return "\n".join(out)


def render_report_text(report: dict[str, Any]) -> str:
    d = report["document"]
    c = report["chunks"]
    out = [
        "=" * 78,
        f"CHUNKING REPORT  {d['name']}  (sha256 {d['sha256'][:12]})",
        "=" * 78,
        f"pages={d.get('page_count')}  source_blocks={report['source_blocks']['count']}  "
        f"final_chunks={c['count']}  deterministic={report['determinism']['identical']}",
        "",
        f"source block types : {report['source_blocks']['type_distribution']}",
        f"effective types    : {c['effective_block_type_distribution']}",
        f"type counts        : {c['type_counts']}",
        "",
        f"tokens             : {c['token_distribution']}",
        f"over {EMBED_MAX_REFERENCE} tokens      : {c['over_embed_max_reference']['count']} "
        f"({c['over_embed_max_reference']['pct']}%)  {c['over_embed_max_reference']['details']}",
        f"content-free/head. : {c['content_free_or_heading_only']['count']}  "
        f"{c['content_free_or_heading_only']['details']}",
        "",
        f"filter             : {report['filter']}",
        f"provenance         : {report['provenance']}",
        f"ranges             : {report['ranges']}",
        f"heading prefix     : {report['heading_prefix']['status_distribution']}",
        f"section boundary   : {report['section_boundary']}",
        f"atomicity          : {report['atomicity']}",
        f"table content      : {report['table_content_audit']}",
        f"list content       : {report['list_content_audit']}",
        f"quality dist       : {c['quality_score_distribution']}",
        f"priority dist      : {c['retrieval_priority_distribution']}",
        f"flags              : {c['classification_flag_counts']}",
        "",
        "SAMPLES",
        "-" * 78,
    ]
    for name, s in report["samples"].items():
        out.append(f"[{name}]")
        if s == "absent":
            out.append("  absent in this document")
        else:
            out.append(f"  chunk={s['chunk_index']} parent={s['parent_chunk']} "
                       f"type={s['block_type']} pages={s['pages']} blocks={s['blocks']} "
                       f"tokens={s['tokens']} prov={s['provenance_entries']} "
                       f"prefix={s['prefix_status']} quality={s['quality_score']}")
            out.append(f"  heading_path={s['heading_path']}")
            out.append(f"  item_ids={s['provenance_item_ids']}")
            out.append(f"  text_head={s['text_head']!r}")
        out.append("")
    return "\n".join(out)


# ======================================================================
# CLI
# ======================================================================


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False),
                    encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="chunking_report")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ex = sub.add_parser("extract", help="Docling extraction -> blocks JSON")
    p_ex.add_argument("--doc", required=True, type=Path)
    p_ex.add_argument("--out", required=True, type=Path)

    p_an = sub.add_parser("analyze", help="blocks JSON -> structural report")
    p_an.add_argument("--blocks", required=True, type=Path)
    p_an.add_argument("--out", required=True, type=Path)
    p_an.add_argument("--out-text", type=Path)
    p_an.add_argument("--runs", type=int, default=2)

    p_cmp = sub.add_parser("compare", help="baseline + after reports -> comparison")
    p_cmp.add_argument("--baseline", required=True, nargs="+", type=Path)
    p_cmp.add_argument("--after", required=True, nargs="+", type=Path)
    p_cmp.add_argument("--out-json", required=True, type=Path)
    p_cmp.add_argument("--out-text", required=True, type=Path)

    args = parser.parse_args(argv)

    if args.cmd == "extract":
        payload = extract(args.doc)
        _write_json(args.out, payload)
        print(f"extracted {len(payload['blocks'])} blocks -> {args.out}")
        return 0

    if args.cmd == "analyze":
        payload = json.loads(args.blocks.read_text(encoding="utf-8"))
        report = analyze(payload, runs=args.runs)
        _write_json(args.out, report)
        if args.out_text:
            args.out_text.parent.mkdir(parents=True, exist_ok=True)
            args.out_text.write_text(render_report_text(report), encoding="utf-8")
        print(f"analyzed {report['chunks']['count']} chunks -> {args.out}  "
              f"deterministic={report['determinism']['identical']}")
        return 0

    if args.cmd == "compare":
        comparisons = []
        for b_path, a_path in zip(sorted(args.baseline), sorted(args.after)):
            b = json.loads(b_path.read_text(encoding="utf-8"))
            a = json.loads(a_path.read_text(encoding="utf-8"))
            comparisons.append(compare(b, a))
        _write_json(args.out_json, comparisons)
        args.out_text.parent.mkdir(parents=True, exist_ok=True)
        args.out_text.write_text(render_comparison_text(comparisons), encoding="utf-8")
        print(f"compared {len(comparisons)} documents -> {args.out_json}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
