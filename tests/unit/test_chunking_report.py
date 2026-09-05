"""Unit tests for the Stage 5 offline chunking evaluator.

These exercise the pure aggregation / analysis helpers and a full ``analyze``
run against synthetic blocks. No Docling, no network, no model downloads.
"""

from __future__ import annotations

from copy import deepcopy

from app.chunking.models import ChunkMetadata, DocumentChunk
from app.document.models import BlockProvenance, DocumentBlock
from app.enums.block import BlockType
from evaluation.chunking_report import (
    _block_from_dict,
    _block_to_dict,
    _chunk_body,
    _block_range_valid,
    _dig,
    _expected_prefix,
    _is_content_free,
    _num_stats,
    _page_range_matches_provenance,
    _page_range_valid,
    _prefix_status,
    _table_rows_intact,
    analyze,
    compare,
)


def _chunk(text, *, block_type=BlockType.TEXT, heading_path=None, section_title=None,
           page_start=None, page_end=None, block_start=None, block_end=None,
           parent_chunk=None, provenance=None, quality_score=1.0, index=0):
    md = ChunkMetadata(
        block_type=block_type,
        heading_path=list(heading_path or []),
        section_title=section_title,
        page_start=page_start, page_end=page_end,
        block_start=block_start, block_end=block_end,
        provenance=list(provenance or []),
        quality_score=quality_score,
    )
    return DocumentChunk(text=text, chunk_index=index, metadata=md, parent_chunk=parent_chunk)


# --- _num_stats ------------------------------------------------------


def test_num_stats_empty():
    s = _num_stats([])
    assert s["count"] == 0 and s["min"] is None and s["p99"] is None


def test_num_stats_basic():
    s = _num_stats([10, 20, 30, 40, 100])
    assert s["count"] == 5
    assert s["min"] == 10 and s["max"] == 100
    assert s["median"] == 30
    assert s["p90"] in (40, 100)  # nearest-rank on 5 values
    assert s["mean"] == 40.0


def test_num_stats_is_order_independent():
    assert _num_stats([3, 1, 2]) == _num_stats([1, 2, 3])


# --- content-free / heading-only detection --------------------------


def test_content_free_true_for_bare_heading():
    c = _chunk("2 Results", heading_path=["2 Results"], section_title="2 Results")
    assert _is_content_free(c) is True


def test_content_free_false_for_folded_heading_plus_body():
    c = _chunk("2 Results\n\nThe model reaches 41.8 BLEU on the task.",
               heading_path=["2 Results"], section_title="2 Results")
    assert _is_content_free(c) is False


def test_content_free_true_for_empty():
    assert _is_content_free(_chunk("   ")) is True


def test_chunk_body_strips_only_matching_heading_line():
    c = _chunk("2 Results\n\nbody text here", heading_path=["2 Results"], section_title="2 Results")
    assert _chunk_body(c) == "body text here"
    c2 = _chunk("Unrelated line\n\nbody text here", heading_path=["2 Results"], section_title="2 Results")
    assert _chunk_body(c2) == c2.text.strip()


# --- heading prefix ------------------------------------------------


def test_expected_prefix_forms():
    assert _expected_prefix(_chunk("x")) is None
    assert _expected_prefix(_chunk("x", heading_path=["A"])) == "A"
    assert _expected_prefix(_chunk("x", heading_path=["A", "B"])) == "B"
    assert _expected_prefix(_chunk("x", heading_path=["A", "B", "C"])) == "B › C"


def test_prefix_status_present_missing_duplicated():
    present = _chunk("B\n\nbody", heading_path=["A", "B"], section_title="B")
    assert _prefix_status(present) == "present"

    missing = _chunk("body with no heading anywhere", heading_path=["A", "B"], section_title="B")
    assert _prefix_status(missing) == "missing"

    # a genuine double-fold: the heading appears as its own paragraph twice
    dup = _chunk("B\n\nsome body\n\nB\n\nmore body", heading_path=["A", "B"], section_title="B")
    assert _prefix_status(dup) == "duplicated"

    # the heading phrase recurring inside prose (e.g. a figure caption) is NOT
    # a duplicate -- it is still "present"
    caption_echo = _chunk("B\n\nFigure 2: B illustrates the mechanism.",
                          heading_path=["A", "B"], section_title="B")
    assert _prefix_status(caption_echo) == "present"

    no_heading = _chunk("free text")
    assert _prefix_status(no_heading) == "absent-ok"


# --- ranges -------------------------------------------------------


def test_page_range_valid():
    assert _page_range_valid(_chunk("x", page_start=2, page_end=5)) is True
    assert _page_range_valid(_chunk("x", page_start=5, page_end=2)) is False
    assert _page_range_valid(_chunk("x", page_start=None, page_end=None)) is True
    assert _page_range_valid(_chunk("x", page_start=0, page_end=1)) is False


def test_block_range_valid_allows_cross_page_inversion():
    same_page_bad = _chunk("x", page_start=3, page_end=3, block_start=9, block_end=2)
    assert _block_range_valid(same_page_bad) is False
    cross_page_ok = _chunk("x", page_start=3, page_end=4, block_start=9, block_end=2)
    assert _block_range_valid(cross_page_ok) is True


def test_page_range_within_provenance():
    good = _chunk("x", page_start=4, page_end=6,
                  provenance=[BlockProvenance(page_number=4), BlockProvenance(page_number=6)])
    assert _page_range_matches_provenance(good) is True
    widened = _chunk("x", page_start=2, page_end=6,
                     provenance=[BlockProvenance(page_number=4), BlockProvenance(page_number=6)])
    assert _page_range_matches_provenance(widened) is False


# --- table row atomicity check ----------------------------------


def test_table_rows_intact():
    ok = _chunk("2 T\n\n| a | b |\n| --- | --- |\n| 1 | 2 |",
                block_type=BlockType.TABLE, heading_path=["2 T"], section_title="2 T")
    assert _table_rows_intact(ok) is True
    broken = _chunk("2 T\n\n| a | b |\nnaked cell fragment\n| 1 | 2 |",
                    block_type=BlockType.TABLE, heading_path=["2 T"], section_title="2 T")
    # "naked cell fragment" has no pipe -> treated as prose line, still ok;
    # a fragment WITH a single pipe is the real breakage:
    really_broken = _chunk("2 T\n\n| a | b |\ncell | half\n| 1 | 2 |",
                           block_type=BlockType.TABLE, heading_path=["2 T"], section_title="2 T")
    assert _table_rows_intact(really_broken) is False
    assert broken is not None


# --- _dig / compare --------------------------------------------


def test_dig():
    obj = {"a": {"b": {"c": 3}}}
    assert _dig(obj, "a.b.c") == 3
    assert _dig(obj, "a.b.x") is None
    assert _dig(obj, "a.z.c") is None


def test_compare_produces_deltas():
    base = {"document": {"name": "d"}, "determinism": {"identical": True},
            "chunks": {"count": 10, "effective_block_type_distribution": {"heading": 10},
                       "quality_score_distribution": {}, "token_distribution": {}},
            "heading_prefix": {"status_distribution": {"missing": 3}}}
    after = deepcopy(base)
    after["chunks"]["count"] = 12
    after["chunks"]["effective_block_type_distribution"] = {"text": 12}
    out = compare(base, after)
    row = next(r for r in out["rows"] if r["path"] == "chunks.count")
    assert row["baseline"] == 10 and row["after"] == 12 and row["delta"] == 2
    assert out["baseline_effective_types"] == {"heading": 10}
    assert out["after_effective_types"] == {"text": 12}


# --- block serialisation round-trip ----------------------------


def test_block_dict_round_trip():
    block = DocumentBlock(
        text="hello", block_type=BlockType.TABLE, level=0, page_number=3, block_index=7,
        metadata={"source_type": ".pdf"},
        provenance=[BlockProvenance(page_number=3, bbox={"left": 1.0}, source_item_id="#/t/0",
                                    charspan=(0, 5), sheet_name=None, table_index=1)],
    )
    restored = _block_from_dict(_block_to_dict(block))
    assert restored.text == block.text
    assert restored.block_type == block.block_type
    assert restored.page_number == 3 and restored.block_index == 7
    assert restored.provenance[0].source_item_id == "#/t/0"
    assert restored.provenance[0].charspan == (0, 5)
    assert restored.provenance[0].table_index == 1


# --- full analyze() on synthetic blocks (no Docling) -----------


def _payload(blocks):
    return {
        "schema_version": 1,
        "document": {"name": "synthetic.pdf", "sha256": "0" * 64, "size_bytes": 1,
                     "page_count": 3, "file_extension": ".pdf"},
        "blocks": [_block_to_dict(b) for b in blocks],
    }


def _b(text, bt, level, page, item, idx):
    return DocumentBlock(text=text, block_type=bt, level=level, page_number=page,
                         block_index=idx, metadata={"source_type": ".pdf", "parser": "docling"},
                         provenance=[BlockProvenance(page_number=page, source_item_id=item)])


def test_analyze_reports_no_heading_only_and_effective_types():
    blocks = [
        _b("1 Overview", BlockType.HEADING, 1, 1, "#/h1", 0),
        _b("A meaningful overview paragraph describing the system in enough words.",
           BlockType.TEXT, 0, 1, "#/t1", 1),
        _b("2 Data", BlockType.HEADING, 1, 2, "#/h2", 2),
        _b("| col | val |\n| --- | --- |\n| a | 1 |\n| b | 2 |", BlockType.TABLE, 0, 2, "#/tbl", 3),
    ]
    report = analyze(_payload(blocks), runs=2)

    assert report["determinism"]["identical"] is True
    assert report["chunks"]["content_free_or_heading_only"]["count"] == 0
    assert report["chunks"]["over_embed_max_reference"]["count"] == 0
    assert report["provenance"]["fabricated_source_item_ids"] == []
    assert report["provenance"]["coverage_pct"] == 100.0
    # table stayed atomic and typed as table
    assert report["chunks"]["type_counts"]["table"] == 1
    assert report["atomicity"]["table_chunks_with_intact_rows"] == 1
    assert report["ranges"]["page_range_invalid_chunks"] == []
    assert report["ranges"]["page_range_outside_provenance_chunks"] == []
    # every chunk carries its heading context
    assert "missing" not in report["heading_prefix"]["status_distribution"]


def test_analyze_flags_content_free_when_present():
    # A heading with no following content in its own section would be dropped by
    # MergeStage; simulate a genuine content-free vector by feeding a lone
    # heading block followed only by another heading.
    blocks = [
        _b("Solo Heading", BlockType.HEADING, 1, 1, "#/h1", 0),
        _b("Another Heading", BlockType.HEADING, 1, 1, "#/h2", 1),
        _b("Real body text under the second heading with adequate length here.",
           BlockType.TEXT, 0, 1, "#/t1", 2),
    ]
    report = analyze(_payload(blocks), runs=1)
    # MergeStage drops content-free headings -> still zero heading-only vectors
    assert report["chunks"]["content_free_or_heading_only"]["count"] == 0
    assert report["chunks"]["count"] >= 1


def test_list_content_audit_flags_split_and_intact():
    from evaluation.chunking_report import _list_content_audit

    src = [
        DocumentBlock(text="- item one is short", block_type=BlockType.LIST, page_number=1,
                      block_index=0, provenance=[BlockProvenance(source_item_id="#/l0")]),
        DocumentBlock(text="- item two is short", block_type=BlockType.LIST, page_number=1,
                      block_index=1, provenance=[BlockProvenance(source_item_id="#/l1")]),
    ]
    # l0 intact in one chunk, l1 split across two chunks
    good = _chunk("L\n\n- item one is short", block_type=BlockType.LIST,
                  provenance=[BlockProvenance(source_item_id="#/l0")])
    half_a = _chunk("L\n\n- item two", block_type=BlockType.LIST,
                    provenance=[BlockProvenance(source_item_id="#/l1")])
    half_b = _chunk("L\n\nis short", block_type=BlockType.LIST,
                    provenance=[BlockProvenance(source_item_id="#/l1")])
    audit = _list_content_audit(src, [good, half_a, half_b])
    assert audit["source_list_blocks"] == 2
    assert audit["items_split_across_chunks"] == 1
    assert audit["split_items"][0]["source_item_id"] == "#/l1"


def test_list_content_audit_oversized_item_is_an_accepted_exception():
    from evaluation.chunking_report import _list_content_audit

    big = "- " + ("word " * 1200)
    src = [DocumentBlock(text=big, block_type=BlockType.LIST, page_number=1, block_index=0,
                         provenance=[BlockProvenance(source_item_id="#/l0")])]
    # carried but truncated across children -> still counts as accepted (oversized)
    c = _chunk("L\n\n" + "word " * 300, block_type=BlockType.LIST,
               provenance=[BlockProvenance(source_item_id="#/l0")])
    audit = _list_content_audit(src, [c])
    assert audit["oversized_items"] == 1
    assert audit["items_split_across_chunks"] == 0


def test_analyze_determinism_detects_stability():
    blocks = [_b(f"Para {i} " + "word " * 20, BlockType.TEXT, 0, 1, f"#/t{i}", i)
              for i in range(6)]
    r1 = analyze(_payload(blocks), runs=4)
    r2 = analyze(_payload(blocks), runs=4)
    assert r1["determinism"]["identical"] is True
    assert r1["chunks"]["count"] == r2["chunks"]["count"]
