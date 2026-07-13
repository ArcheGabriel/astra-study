from copy import deepcopy

from app.chunking.models import DocumentChunk
from app.chunking.stages.base import BaseChunkStage
from app.chunking.utils.tokens import count_tokens
from app.enums.block import BlockType


class SemanticStage(BaseChunkStage):
    """
    Final semantic cleanup after RecursiveStage.

    Responsibilities
    ----------------
    ✓ Merge tiny chunks
    ✓ Keep headings attached
    ✓ Keep captions attached
    ✓ Never cross section boundaries
    ✓ Never exceed embedding size
    """

    MIN_TOKENS = 120

    MAX_TOKENS = 700

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

            refined.append(
                current,
            )

            i += 1

        return refined

    def _should_merge(
        self,
        current: DocumentChunk,
        nxt: DocumentChunk,
    ) -> bool:

        #
        # Never merge across sections.
        #
        if (
            current.metadata.heading_path
            != nxt.metadata.heading_path
        ):
            return False

        #
        # Never merge different recursive parents.
        #
        if (
            current.parent_chunk
            != nxt.parent_chunk
        ):
            return False

        current_tokens = count_tokens(
            current.text,
        )

        next_tokens = count_tokens(
            nxt.text,
        )

        #
        # Stay within embedding limit.
        #
        if (
            current_tokens + next_tokens
            > self.MAX_TOKENS
        ):
            return False

        #
        # Heading owns following text.
        #
        if (

            current.metadata.block_type
            == BlockType.HEADING

            and

            nxt.metadata.block_type
            != BlockType.HEADING

        ):

            return True

        #
        # Caption owns following text.
        #
        if (

            current.metadata.block_type
            == BlockType.CAPTION

            and

            nxt.metadata.block_type
            != BlockType.HEADING

        ):

            return True

        #
        # Tiny chunks should disappear.
        #
        if current_tokens < self.MIN_TOKENS:

            return True

        return False

    def _merge(
        self,
        left: DocumentChunk,
        right: DocumentChunk,
    ) -> DocumentChunk:

        merged = deepcopy(
            left,
        )

        merged.text = (

            left.text

            + "\n\n"

            + right.text

        )

        merged.metadata.page_end = (
            right.metadata.page_end
        )

        merged.metadata.block_end = (
            right.metadata.block_end
        )

        return merged