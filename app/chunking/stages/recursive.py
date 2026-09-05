from __future__ import annotations

from copy import deepcopy

from app.chunking.config import DEFAULT_CHUNKING_CONFIG, ChunkingConfig
from app.chunking.models import DocumentChunk
from app.chunking.stages.base import BaseChunkStage
from app.chunking.utils.splitter import (
    flatten_sentences,
    split_for_embeddings,
    split_paragraphs,
)
from app.chunking.utils.tokens import count_tokens, join_sentences
from app.enums.block import BlockType


# Number of consecutive words used to test whether a source segment's text
# is present in a child window. Comfortably smaller than the configured
# sentence overlap, so a segment that straddles two children is detected in
# both.
_PROBE_WORDS = 6


def _is_markdown_separator(line: str) -> bool:
    """A markdown table separator row, e.g. ``| --- | :--: |``."""
    stripped = line.strip()
    return (
        bool(stripped)
        and "-" in stripped
        and "|" in stripped
        and set(stripped) <= set("|:- ")
    )


def _norm(text: str) -> str:
    """Whitespace / case normalised form for deterministic text comparison."""
    return " ".join(text.split()).casefold()


def _segment_overlaps(segment: str, child_text: str) -> bool:
    """True when ``segment`` (a source block's text) actually contributes to
    ``child_text``.

    Deterministic: a child contributes to a segment if it contains a
    ``_PROBE_WORDS``-word run from the segment's head, tail, or a
    quarter/half/three-quarter interior point (or, for a short segment, the
    whole thing). Head/tail cover a fully-contained segment and a segment
    split across the intentional sentence overlap; the interior probes cover
    a single block that spans several child windows. False matches are only
    possible when two different blocks share a verbatim >= ``_PROBE_WORDS``
    run at a probe position -- mild over-attribution to an adjacent block,
    never fabrication or loss.
    """
    seg = _norm(segment)
    body = _norm(child_text)

    if not seg:
        return False

    words = seg.split()

    if len(words) <= _PROBE_WORDS:
        return seg in body

    last = len(words) - _PROBE_WORDS

    # Head, tail and three evenly-spaced interior probes -- enough to detect a
    # single source block split across up to ~five child windows.
    positions = {0, last}
    for quarter in (1, 2, 3):
        positions.add(min(max(len(words) * quarter // 4 - _PROBE_WORDS // 2, 0), last))

    return any(
        " ".join(words[start:start + _PROBE_WORDS]) in body
        for start in sorted(positions)
    )


class RecursiveStage(BaseChunkStage):
    """
    Split oversized section chunks into embedding-sized children.

    Characteristics
    ---------------
    - deterministic sentence-window splitting (nltk + tiktoken)
    - every child carries the section's heading context prefix, exactly once
    - every child's provenance is partitioned to the source blocks it
      actually contains (page / block ranges recomputed from that subset)
    - stable ``parent_chunk`` linkage across the children of one split
    """

    def __init__(
        self,
        config: ChunkingConfig | None = None,
    ) -> None:

        self._config = config or DEFAULT_CHUNKING_CONFIG

    # ------------------------------------------------------------------
    # pipeline entry point
    # ------------------------------------------------------------------

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        output: list[DocumentChunk] = []

        next_chunk_index = 0
        next_parent_index = 0

        for chunk in chunks:

            prefix = self._heading_prefix(
                chunk.metadata.heading_path,
            )

            # Not oversized: still ensure the heading context is present
            # exactly once (a MergeStage size-split can leave a heading-less
            # continuation chunk). The prefix costs tokens, so a chunk that
            # fits on its own can still overflow once prefixed -- in that case
            # fall through to the normal splitter rather than emit an
            # over-``embed_max`` child.
            prefixed_text = self._prefixed_text(chunk, prefix)

            if count_tokens(prefixed_text) <= self._config.embed_max:

                chunk.text = prefixed_text

                # Same structural-dominance rule as split children: a chunk
                # that carries a table (or a list and no table) is typed
                # accordingly so QualityStage / FilterStage see it correctly.
                self._apply_structural_type(
                    chunk.metadata,
                    [s for s in chunk.metadata.content_segments if not s.is_heading],
                )

                chunk.chunk_index = next_chunk_index
                next_chunk_index += 1

                output.append(chunk)

                continue

            parent_chunk = next_parent_index
            next_parent_index += 1

            children = self._split_chunk(
                chunk=chunk,
                prefix=prefix,
                parent_chunk=parent_chunk,
                start_chunk_index=next_chunk_index,
            )

            next_chunk_index += len(children)

            output.extend(children)

        return output

    # ------------------------------------------------------------------
    # heading prefix
    # ------------------------------------------------------------------

    def _heading_prefix(
        self,
        heading_path: list[str] | None,
    ) -> str:
        """Compact heading context: the deepest heading normally, or the
        deepest two joined for genuinely deep nesting. One line, added once.
        The stored ``heading_path`` is never changed.
        """

        path = [
            entry.strip()
            for entry in (heading_path or [])
            if entry and entry.strip()
        ]

        if not path:
            return ""

        if len(path) >= 3:
            return f"{path[-2]} › {path[-1]}"

        return path[-1]

    def _split_source(
        self,
        chunk: DocumentChunk,
    ) -> tuple[list[str], bool]:
        """Recover the source segments (one per contributing block) from the
        merged chunk text and report whether the first segment is the folded
        section heading.
        """

        paragraphs = split_paragraphs(chunk.text)

        path = [
            entry.strip()
            for entry in (chunk.metadata.heading_path or [])
            if entry and entry.strip()
        ]

        seeded_by_heading = bool(
            paragraphs
            and path
            and paragraphs[0].strip().lstrip("#").strip().casefold()
            == path[-1].casefold()
        )

        content_segments = (
            paragraphs[1:] if seeded_by_heading else paragraphs
        )

        return content_segments, seeded_by_heading

    def _prefixed_text(
        self,
        chunk: DocumentChunk,
        prefix: str,
    ) -> str:
        """The text a pass-through chunk would carry with ``prefix`` present
        exactly once. Pure -- it does not mutate ``chunk`` -- so the caller can
        measure the result before committing to the pass-through path.
        """

        if not prefix:
            return chunk.text

        if chunk.text.startswith(prefix + "\n\n"):
            return chunk.text

        content_segments, _ = self._split_source(chunk)

        body = "\n\n".join(content_segments).strip()

        if not body:
            return chunk.text

        return f"{prefix}\n\n{body}"

    # ------------------------------------------------------------------
    # window formation
    # ------------------------------------------------------------------

    def _child_bodies(
        self,
        content_segments: list[str],
        *,
        block_type: BlockType,
        max_tokens: int,
    ) -> tuple[list[str], list[list[int]] | None]:
        """Text of each child (before the heading prefix), plus -- for the
        structural paths -- the exact content-segment indices that went into
        each child (``None`` for the prose path, which falls back to the
        fuzzy ``_segment_overlaps`` matcher).

        Prose is sentence-windowed with the configured overlap. Structural
        content is split only at row / item boundaries so a table row or a
        list item is never divided.
        """

        if block_type == BlockType.TABLE:
            bodies = self._table_bodies("\n\n".join(content_segments), max_tokens)
            # The markdown table is one logical block; every fragment refers
            # back to all of its source segment(s).
            all_indices = list(range(len(content_segments)))
            return bodies, [list(all_indices) for _ in bodies]

        if block_type == BlockType.LIST:
            # Each content segment is already one whole list item.
            return self._pack_list_items(content_segments, max_tokens)

        body = "\n\n".join(content_segments)

        windows = split_for_embeddings(
            text=body,
            max_tokens=max_tokens,
            overlap_tokens=self._config.overlap,
        )

        if not windows:
            windows = [[body]]

        return [join_sentences(window) for window in windows], None

    def _pack_list_items(
        self,
        items: list[str],
        max_tokens: int,
    ) -> tuple[list[str], list[list[int]]]:
        """Pack whole list items into child bodies, never dividing one. A
        single item larger than ``max_tokens`` becomes its own child (an
        over-budget item is not split). Returns the item indices per child so
        provenance can be attributed exactly.
        """

        bodies: list[str] = []
        segment_map: list[list[int]] = []

        current_text: list[str] = []
        current_idx: list[int] = []

        for index, item in enumerate(items):

            item = item.strip()

            if not item:
                continue

            trial = current_text + [item]

            if current_text and count_tokens("\n\n".join(trial)) > max_tokens:
                bodies.append("\n\n".join(current_text))
                segment_map.append(current_idx)
                current_text, current_idx = [item], [index]
            else:
                current_text, current_idx = trial, current_idx + [index]

        if current_text:
            bodies.append("\n\n".join(current_text))
            segment_map.append(current_idx)

        if not bodies:
            bodies = ["\n\n".join(i for i in items if i.strip())]
            segment_map = [list(range(len(items)))]

        return bodies, segment_map

    def _table_bodies(
        self,
        grid_text: str,
        max_tokens: int,
        first_fragment_budget: int | None = None,
    ) -> list[str]:
        """Split a markdown table only at row boundaries. The header row (and
        a following markdown separator row, if present) is repeated on every
        fragment; no data row is ever divided.

        ``first_fragment_budget`` (< ``max_tokens``) leaves room for a caption
        that will be prepended to the first fragment only.
        """

        text = grid_text.strip()

        lines = [line for line in text.split("\n") if line.strip()]

        if len(lines) <= 1:
            return [text]

        header: list[str] = [lines[0]]
        start = 1

        if len(lines) > 1 and _is_markdown_separator(lines[1]):
            header.append(lines[1])
            start = 2

        header_text = "\n".join(header)
        header_tokens = count_tokens(header_text)

        data_rows = lines[start:]

        if not data_rows:
            return [text]

        bodies: list[str] = []
        current: list[str] = []

        def budget() -> int:
            if not bodies and first_fragment_budget is not None:
                return first_fragment_budget
            return max_tokens

        for row in data_rows:

            trial = current + [row]

            if current and header_tokens + count_tokens("\n".join(trial)) > budget():
                bodies.append(header_text + "\n" + "\n".join(current))
                current = [row]
            else:
                current = trial

        if current:
            bodies.append(header_text + "\n" + "\n".join(current))

        return bodies or [text]

    # ------------------------------------------------------------------
    # splitting
    # ------------------------------------------------------------------

    def _split_chunk(
        self,
        chunk: DocumentChunk,
        prefix: str,
        parent_chunk: int,
        start_chunk_index: int,
    ) -> list[DocumentChunk]:

        # Authoritative path: MergeStage recorded the per-source-block structure
        # (type + text + provenance). Route each structural element by its real
        # Docling ``block_type`` and attribute provenance to it exactly.
        if chunk.metadata.content_segments:
            return self._split_from_segments(
                chunk=chunk,
                prefix=prefix,
                parent_chunk=parent_chunk,
                start_chunk_index=start_chunk_index,
            )

        return self._split_chunk_legacy(
            chunk=chunk,
            prefix=prefix,
            parent_chunk=parent_chunk,
            start_chunk_index=start_chunk_index,
        )

    # ------------------------------------------------------------------
    # authoritative path -- driven by MergeStage ContentSegments
    # ------------------------------------------------------------------

    def _split_from_segments(
        self,
        *,
        chunk: DocumentChunk,
        prefix: str,
        parent_chunk: int,
        start_chunk_index: int,
    ) -> list[DocumentChunk]:

        segments = list(chunk.metadata.content_segments)

        heading_prov: list = []
        for seg in segments:
            if seg.is_heading:
                for ref in seg.provenance:
                    if ref not in heading_prov:
                        heading_prov.append(ref)

        body_segs = [seg for seg in segments if not seg.is_heading]

        if not body_segs:
            # Nothing but a heading -- MergeStage should never emit this, but
            # fall back rather than crash.
            return self._split_chunk_legacy(
                chunk=chunk,
                prefix=prefix,
                parent_chunk=parent_chunk,
                start_chunk_index=start_chunk_index,
            )

        prefix_tokens = count_tokens(prefix) if prefix else 0
        effective_max = max(self._config.embed_max - prefix_tokens - 4, 1)

        # --- structural runs -> atomic sub-bodies ---------------------
        sub_bodies = self._segment_sub_bodies(body_segs, effective_max)

        # --- pack sub-bodies into children ---------------------------
        packed = self._pack_sub_bodies(sub_bodies, prefix)

        children: list[DocumentChunk] = []

        for offset, group in enumerate(packed):

            child_body = "\n\n".join(sb_text for sb_text, _ in group)
            child_text = f"{prefix}\n\n{child_body}" if prefix else child_body

            contributing = sorted({i for _, indices in group for i in indices})
            contributing_segs = [body_segs[i] for i in contributing]

            metadata = deepcopy(chunk.metadata)
            metadata.chunk_uuid = None
            metadata.parent_chunk_uuid = None
            metadata.content_segments = tuple(contributing_segs)

            # provenance: heading context pointer first, then body segments in
            # document order, value-deduplicated. Never fabricated, never drops
            # a segment whose text is in this child.
            body_prov: list = []
            for seg in contributing_segs:
                for ref in seg.provenance:
                    if ref not in body_prov:
                        body_prov.append(ref)

            merged_prov: list = []
            for ref in list(heading_prov) + body_prov:
                if ref not in merged_prov:
                    merged_prov.append(ref)
            if merged_prov:
                metadata.provenance = merged_prov

            self._apply_structural_type(metadata, contributing_segs)

            # ranges: body-only -- the heading prefix's own page must not widen
            # the range (its page still lives in its provenance entry).
            self._ranges_from_segments(metadata, contributing_segs)

            children.append(
                DocumentChunk(
                    text=child_text,
                    chunk_index=start_chunk_index + offset,
                    metadata=metadata,
                    parent_chunk=parent_chunk,
                )
            )

        return children

    @staticmethod
    def _apply_structural_type(metadata, contributing_segs: list) -> None:
        """Stage 6 structural-dominance rule for an emitted chunk:
          1. contains a TABLE segment        -> block_type = TABLE
          2. else contains LIST and no TABLE -> block_type = LIST
          3. else keep the chunk's effective type (TEXT / CAPTION)
        An incidental prose lead-in packed into the same chunk never demotes a
        structurally-dominant table / list chunk.
        """
        types = {seg.block_type for seg in contributing_segs}
        if BlockType.TABLE in types:
            metadata.block_type = BlockType.TABLE
        elif BlockType.LIST in types:
            metadata.block_type = BlockType.LIST

    def _segment_sub_bodies(
        self,
        body_segs: list,
        max_tokens: int,
    ) -> list[tuple[str, list[int], bool]]:
        """Turn the body segments into atomic sub-bodies:
        ``(text, contributing_body_seg_indices, is_atomic)``.

        A structural element (table grid row-set / whole list item) is atomic
        and must never be divided when packing into children. Prose is
        sentence-windowed exactly as before.
        """

        sub_bodies: list[tuple[str, list[int], bool]] = []

        i = 0
        while i < len(body_segs):

            seg = body_segs[i]

            if seg.block_type == BlockType.TABLE:
                sub_bodies.extend(self._table_sub_bodies(seg.text, i, max_tokens))
                i += 1
                continue

            if seg.block_type == BlockType.LIST:
                j = i
                while j < len(body_segs) and body_segs[j].block_type == BlockType.LIST:
                    j += 1
                run = body_segs[i:j]
                bodies, seg_map = self._pack_list_items(
                    [s.text for s in run], max_tokens
                )
                for body, local_indices in zip(bodies, seg_map):
                    sub_bodies.append((body, [i + k for k in local_indices], True))
                i = j
                continue

            # prose run: gather consecutive non-structural segments
            j = i
            while j < len(body_segs) and body_segs[j].block_type not in (
                BlockType.TABLE,
                BlockType.LIST,
            ):
                j += 1
            run = body_segs[i:j]
            joined = "\n\n".join(s.text for s in run)
            windows = split_for_embeddings(
                text=joined,
                max_tokens=max_tokens,
                overlap_tokens=self._config.overlap,
            )
            if not windows:
                windows = [[joined]]

            # Attribute each window to the segments whose sentences it actually
            # contains -- exact whole-sentence identity, deterministic, never
            # the fuzzy substring matcher. A window that matches no segment
            # (heavy re-tokenisation) falls back to the whole run.
            seg_sentences = [
                frozenset(flatten_sentences([seg.text], max_tokens)) for seg in run
            ]
            for window in windows:
                wsents = set(window)
                hits = [i + k for k, ss in enumerate(seg_sentences) if ss & wsents]
                if not hits:
                    hits = list(range(i, j))
                sub_bodies.append((join_sentences(window), hits, False))
            i = j

        return sub_bodies

    def _table_sub_bodies(
        self,
        segment_text: str,
        seg_index: int,
        max_tokens: int,
    ) -> list[tuple[str, list[int], bool]]:
        """A TABLE segment's text is ``[caption paragraph(s)]`` + the markdown
        grid (the final paragraph). Keep the caption with the first fragment;
        row-split the grid; never divide a data row.
        """

        paragraphs = split_paragraphs(segment_text)
        if not paragraphs:
            return [(segment_text, [seg_index], True)]

        grid = paragraphs[-1]
        lead = "\n\n".join(paragraphs[:-1]).strip()

        # Reserve room in the first fragment for the caption prepended below,
        # so no fragment (caption included) exceeds the budget unless a single
        # row alone does.
        lead_tokens = count_tokens(lead) + 2 if lead else 0
        first_budget = max(max_tokens - lead_tokens, 1) if lead else None

        fragments = self._table_bodies(grid, max_tokens, first_budget)

        out: list[tuple[str, list[int], bool]] = []
        for k, fragment in enumerate(fragments):
            text = f"{lead}\n\n{fragment}" if (lead and k == 0) else fragment
            out.append((text, [seg_index], True))
        return out

    def _pack_sub_bodies(
        self,
        sub_bodies: list[tuple[str, list[int], bool]],
        prefix: str,
    ) -> list[list[tuple[str, list[int]]]]:
        """Greedily pack atomic sub-bodies into children. A sub-body is never
        split. A structural sub-body may share a child with adjacent content
        only when the whole combined child still fits ``embed_max``.
        """

        budget = self._config.embed_max
        packed: list[list[tuple[str, list[int]]]] = []
        current: list[tuple[str, list[int]]] = []

        def child_tokens(items: list[tuple[str, list[int]]]) -> int:
            body = "\n\n".join(text for text, _ in items)
            whole = f"{prefix}\n\n{body}" if prefix else body
            return count_tokens(whole)

        for text, indices, _atomic in sub_bodies:
            trial = current + [(text, indices)]
            if current and child_tokens(trial) > budget:
                packed.append(current)
                current = [(text, indices)]
            else:
                current = trial

        if current:
            packed.append(current)

        return packed or [[("", [])]]

    def _ranges_from_segments(self, metadata, contributing_segs: list) -> None:
        """Page range from the contributing (body) segments' provenance only;
        block range from their source ``block_index`` values."""

        pages = [
            ref.page_number
            for seg in contributing_segs
            for ref in seg.provenance
            if ref.page_number is not None
        ]
        metadata.page_start = min(pages) if pages else None
        metadata.page_end = max(pages) if pages else None

        blocks = [
            seg.source_block_index
            for seg in contributing_segs
            if seg.source_block_index is not None
        ]
        if blocks:
            metadata.block_start = min(blocks)
            metadata.block_end = max(blocks)

    # ------------------------------------------------------------------
    # legacy path -- text-derived (chunks without ContentSegments)
    # ------------------------------------------------------------------

    def _split_chunk_legacy(
        self,
        *,
        chunk: DocumentChunk,
        prefix: str,
        parent_chunk: int,
        start_chunk_index: int,
    ) -> list[DocumentChunk]:

        content_segments, seeded_by_heading = self._split_source(chunk)

        prefix_tokens = count_tokens(prefix) if prefix else 0

        # Reserve room for the prefix (+ the blank-line separator and a small
        # margin for tiktoken's non-additive merges).
        effective_max = max(
            self._config.embed_max - prefix_tokens - 4,
            1,
        )

        child_bodies, structural_segment_map = self._child_bodies(
            content_segments,
            block_type=chunk.metadata.block_type,
            max_tokens=effective_max,
        )

        heading_indices, segment_prov_groups = self._align_provenance(
            chunk.metadata.provenance,
            content_segments,
            seeded_by_heading,
        )

        children: list[DocumentChunk] = []

        for offset, child_body in enumerate(child_bodies):

            child_text = (
                f"{prefix}\n\n{child_body}"
                if prefix
                else child_body
            )

            metadata = deepcopy(chunk.metadata)

            # Recursive children receive fresh UUIDs during FinalizeStage.
            metadata.chunk_uuid = None
            metadata.parent_chunk_uuid = None

            if segment_prov_groups is None:

                # Last resort -- provenance could not be partitioned, so the
                # child keeps the full (already deep-copied) list and the
                # parent's page / block range. Documented fallback #3.
                pass

            else:

                full_prov = metadata.provenance

                if structural_segment_map is not None:
                    # Table / list: the child body is an exact concatenation
                    # of whole source segments, so attribution is exact.
                    hit_segments = list(structural_segment_map[offset])
                else:
                    hit_segments = [
                        index
                        for index, segment in enumerate(content_segments)
                        if _segment_overlaps(segment, child_body)
                    ]

                if not hit_segments:
                    # The child has body text but matched no segment head /
                    # interior / tail probe -- a single source block longer
                    # than several windows. Attribute it to all of the
                    # section's content blocks rather than to the heading
                    # alone (over-approximation, never fabrication).
                    hit_segments = list(range(len(content_segments)))

                body_indices: set[int] = set()
                for index in hit_segments:
                    body_indices.update(segment_prov_groups[index])

                selected = sorted(set(heading_indices) | body_indices)

                if selected:
                    metadata.provenance = [
                        full_prov[position] for position in selected
                    ]

                self._recompute_ranges(
                    metadata=metadata,
                    parent=chunk,
                    seeded_by_heading=seeded_by_heading,
                    hit_segments=hit_segments,
                    body_provenance=[
                        full_prov[position] for position in sorted(body_indices)
                    ],
                )

            children.append(
                DocumentChunk(
                    text=child_text,
                    chunk_index=start_chunk_index + offset,
                    metadata=metadata,
                    parent_chunk=parent_chunk,
                )
            )

        return children

    # ------------------------------------------------------------------
    # provenance / ranges
    # ------------------------------------------------------------------

    def _align_provenance(
        self,
        provenance: list,
        content_segments: list[str],
        seeded_by_heading: bool,
    ) -> tuple[list[int], list[list[int]] | None]:
        """Best-effort alignment of provenance entries to source segments.

        Fallback hierarchy:
          1. consecutive ``source_item_id`` runs, one run per segment
             (handles multi-record blocks such as a paragraph spanning two
             pages)
          2. -- no deterministic substring source is available here, the
             per-segment text match happens against the child later --
          3. return ``None`` -> caller keeps the full provenance list

        Returns ``(heading_indices, segment_groups)`` where ``segment_groups``
        is ``None`` for the last-resort case.
        """

        if not provenance:
            return [], None

        if any(entry.source_item_id is None for entry in provenance):
            return [], None

        groups: list[list[int]] = []

        for position, entry in enumerate(provenance):

            if (
                groups
                and provenance[groups[-1][-1]].source_item_id
                == entry.source_item_id
            ):
                groups[-1].append(position)
            else:
                groups.append([position])

        segment_count = len(content_segments)

        if seeded_by_heading and len(groups) == segment_count + 1:
            return groups[0], groups[1:]

        if not seeded_by_heading and len(groups) == segment_count:
            return [], groups

        return [], None

    def _recompute_ranges(
        self,
        *,
        metadata,
        parent: DocumentChunk,
        seeded_by_heading: bool,
        hit_segments: list[int],
        body_provenance: list,
    ) -> None:
        """Recompute page / block ranges from the *body* the child actually
        contains -- never inherit the parent's whole range for a partial
        child, and never let the heading prefix's own page widen the range
        (its page still lives in its own provenance entry).
        """

        pages = [
            entry.page_number
            for entry in body_provenance
            if entry.page_number is not None
        ]

        metadata.page_start = min(pages) if pages else None
        metadata.page_end = max(pages) if pages else None

        if hit_segments and parent.metadata.block_start is not None:

            base = parent.metadata.block_start + (
                1 if seeded_by_heading else 0
            )

            indices = [base + segment for segment in hit_segments]

            metadata.block_start = min(indices)
            metadata.block_end = max(indices)
