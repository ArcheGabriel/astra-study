from __future__ import annotations

from copy import deepcopy

from app.chunking.config import DEFAULT_CHUNKING_CONFIG, ChunkingConfig
from app.chunking.models import DocumentChunk, section_contains
from app.chunking.stages.base import BaseChunkStage
from app.chunking.utils.tokens import count_tokens
from app.enums.block import BlockType


class SemanticStage(BaseChunkStage):
    """
    Narrow post-split cleanup.

    Responsibilities
    ----------------
    - concatenate a *tiny* chunk into its same-section neighbour
    - attach a caption to the block that follows it (existing design intent)
    - when it does merge: union provenance and recompute page / block ranges

    It never merges across a section boundary and it is deliberately not a
    general-purpose chunker.
    """

    def __init__(
        self,
        config: ChunkingConfig | None = None,
    ) -> None:

        self._config = config or DEFAULT_CHUNKING_CONFIG

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        if not chunks:
            return []

        refined: list[DocumentChunk] = []

        i = 0

        while i < len(chunks):

            current = chunks[i]

            while (
                i + 1 < len(chunks)
                and self._should_merge(
                    current,
                    chunks[i + 1],
                )
            ):

                current = self._merge(
                    current,
                    chunks[i + 1],
                )

                i += 1

            refined.append(current)

            i += 1

        return refined

    def _should_merge(
        self,
        current: DocumentChunk,
        nxt: DocumentChunk,
    ) -> bool:

        #
        # Section safety: only concatenate within the SAME section.
        # ``section_contains`` both ways == identical section identity;
        # a descendant / ancestor / sibling relationship is never merged
        # here. ``parent_chunk`` differences alone no longer block a merge.
        #
        if not (
            section_contains(
                current.metadata.section_key,
                nxt.metadata.section_key,
            )
            and section_contains(
                nxt.metadata.section_key,
                current.metadata.section_key,
            )
        ):
            return False

        current_tokens = count_tokens(current.text)

        next_tokens = count_tokens(nxt.text)

        #
        # Never exceed the embedding limit.
        #
        if (
            current_tokens + next_tokens
            > self._config.embed_max
        ):
            return False

        #
        # Structural-atomicity guard (Stage 6).
        #
        # A TABLE / LIST chunk is an atomic structural unit produced by
        # RecursiveStage. It may only be concatenated with another chunk of the
        # SAME structural type in the same section -- never with prose, a
        # caption, or the other structural type -- so its rows / items and its
        # effective ``block_type`` are never muddied after the fact.
        #
        structural = {BlockType.TABLE, BlockType.LIST}
        current_type = current.metadata.block_type
        next_type = nxt.metadata.block_type

        if (
            current_type in structural or next_type in structural
        ) and current_type != next_type:
            return False

        #
        # A caption owns the block that follows it.
        #
        if (
            current.metadata.block_type
            == BlockType.CAPTION
            and nxt.metadata.block_type
            != BlockType.HEADING
        ):
            return True

        #
        # A residual heading-typed chunk owns the following text. Rare --
        # MergeStage now folds headings into their section content -- kept
        # as a defensive fallback.
        #
        if (
            current.metadata.block_type
            == BlockType.HEADING
            and nxt.metadata.block_type
            != BlockType.HEADING
        ):
            return True

        #
        # Otherwise only absorb a genuinely tiny neighbour.
        #
        if current_tokens < self._config.merge_min:
            return True

        return False

    def _merge(
        self,
        left: DocumentChunk,
        right: DocumentChunk,
    ) -> DocumentChunk:

        merged = deepcopy(left)

        merged.text = (
            left.text
            + "\n\n"
            + right.text
        )

        #
        # Union provenance -- value-dedup, document order preserved.
        # Neither side's provenance may be lost.
        #
        for reference in right.metadata.provenance:
            if reference not in merged.metadata.provenance:
                merged.metadata.provenance.append(reference)

        #
        # Page range from the union of contributing provenance.
        #
        pages = [
            entry.page_number
            for entry in merged.metadata.provenance
            if entry.page_number is not None
        ]

        merged.metadata.page_start = (
            min(pages) if pages else None
        )
        merged.metadata.page_end = (
            max(pages) if pages else None
        )

        #
        # Block range from the union of both chunks' own ranges.
        #
        starts = [
            value
            for value in (
                left.metadata.block_start,
                right.metadata.block_start,
            )
            if value is not None
        ]
        ends = [
            value
            for value in (
                left.metadata.block_end,
                right.metadata.block_end,
            )
            if value is not None
        ]

        merged.metadata.block_start = (
            min(starts) if starts else None
        )
        merged.metadata.block_end = (
            max(ends) if ends else None
        )

        return merged
