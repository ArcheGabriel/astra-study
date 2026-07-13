from app.chunking.models import DocumentChunk
from app.chunking.stages.base import BaseChunkStage
from app.chunking.utils.filters import (
    is_copyright,
    is_doi,
    is_empty,
    is_isbn,
    is_numeric_only,
    is_page_number,
    is_punctuation_only,
    is_short_noise,
)
from app.enums.block import BlockType


class FilterStage(BaseChunkStage):
    """
    Removes only truly useless chunks.

    Philosophy
    ----------
    Never remove information that could help retrieval.

    Remove only obvious parser artefacts.

    Examples removed
    ----------------
    • Empty chunks
    • Standalone page numbers
    • Standalone DOI
    • Standalone ISBN
    • Standalone copyright
    • Pure punctuation
    • Duplicate chunks
    """

    MIN_TEXT_LENGTH = 3

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        filtered: list[DocumentChunk] = []

        seen: set[str] = set()

        for chunk in chunks:

            text = chunk.text.strip()

            #
            # ----------------------------------
            # Empty
            # ----------------------------------
            #
            if is_empty(text):
                continue

            #
            # ----------------------------------
            # Duplicate
            # ----------------------------------
            #
            normalized = " ".join(
                text.split(),
            )

            if normalized in seen:
                continue

            seen.add(
                normalized,
            )

            #
            # ----------------------------------
            # Never remove headings.
            # ----------------------------------
            #
            if (
                chunk.metadata.block_type
                == BlockType.HEADING
            ):

                filtered.append(chunk)
                continue

            #
            # ----------------------------------
            # Standalone page number
            # ----------------------------------
            #
            if is_page_number(text):
                continue

            #
            # ----------------------------------
            # Tiny numeric artefacts
            # ----------------------------------
            #
            if (

                len(text) <= 4

                and

                is_numeric_only(text)

            ):

                continue

            #
            # ----------------------------------
            # Pure punctuation
            # ----------------------------------
            #
            if is_punctuation_only(text):
                continue

            #
            # ----------------------------------
            # Standalone DOI
            # ----------------------------------
            #
            if (

                len(text) < 100

                and

                is_doi(text)

            ):

                continue

            #
            # ----------------------------------
            # Standalone ISBN
            # ----------------------------------
            #
            if (

                len(text) < 100

                and

                is_isbn(text)

            ):

                continue

            #
            # ----------------------------------
            # Copyright notice
            # ----------------------------------
            #
            if (

                len(text) < 150

                and

                is_copyright(text)

            ):

                continue

            #
            # ----------------------------------
            # Extremely tiny parser artefacts
            # ----------------------------------
            #
            if (

                len(text) < self.MIN_TEXT_LENGTH

                and

                is_short_noise(text)

            ):

                continue

            filtered.append(
                chunk,
            )

        return filtered