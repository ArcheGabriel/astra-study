import re

from app.chunking.models import DocumentChunk
from app.chunking.stages.base import BaseChunkStage
from app.enums.block import BlockType


class QualityStage(BaseChunkStage):
    """
    Assigns retrieval quality metadata to chunks.

    This stage NEVER removes chunks.

    Instead it enriches them with metadata that is
    later used during embedding, retrieval and
    reranking.

    The scores are heuristics and can later be
    replaced by an ML-based quality estimator.
    """

    # -----------------------------
    # Scores
    # -----------------------------

    DEFAULT_SCORE = 1.00
    DEFAULT_PRIORITY = 100

    HEADING_SCORE = 0.95
    HEADING_PRIORITY = 100

    CAPTION_SCORE = 0.70
    CAPTION_PRIORITY = 70

    TABLE_SCORE = 0.75
    TABLE_PRIORITY = 75

    FORMULA_SCORE = 0.80
    FORMULA_PRIORITY = 80

    METADATA_SCORE = 0.55
    METADATA_PRIORITY = 45

    APPENDIX_SCORE = 0.40
    APPENDIX_PRIORITY = 35

    REFERENCE_SCORE = 0.30
    REFERENCE_PRIORITY = 20

    # -----------------------------
    # Patterns
    # -----------------------------

    REFERENCE_PATTERN = re.compile(
        r"^(references|bibliography)$",
        re.IGNORECASE,
    )

    APPENDIX_PATTERN = re.compile(
        r"^appendix(\s+[A-Z0-9]+)?",
        re.IGNORECASE,
    )

    METADATA_PATTERN = re.compile(
        (
            r"^(author|authors|affiliation|"
            r"publisher|copyright|isbn|doi)"
        ),
        re.IGNORECASE,
    )

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        for chunk in chunks:

            self._score_chunk(chunk)

        return chunks

    @staticmethod
    def _body_without_heading(
        text: str,
        heading: str,
    ) -> str:
        """Return ``text`` with a leading folded-heading line removed.

        RecursiveStage prepends the section heading as ``"{heading}\\n\\n"``.
        When the first block of ``text`` is exactly that heading, strip it so
        content heuristics see the real body; otherwise return ``text``
        unchanged.
        """

        heading = (heading or "").strip().lstrip("#").strip()

        if not heading:
            return text

        first, sep, rest = text.partition("\n\n")

        if sep and first.strip().lstrip("#").strip().casefold() == heading.casefold():
            return rest.strip()

        return text

    def _score_chunk(
        self,
        chunk: DocumentChunk,
    ) -> None:

        metadata = chunk.metadata

        metadata.quality_score = (
            self.DEFAULT_SCORE
        )

        metadata.retrieval_priority = (
            self.DEFAULT_PRIORITY
        )

        text = chunk.text.strip()

        heading = (
            metadata.section_title
            or ""
        )

        #
        # References
        #

        if self.REFERENCE_PATTERN.match(
            heading,
        ):

            metadata.is_reference = True

            metadata.quality_score = (
                self.REFERENCE_SCORE
            )

            metadata.retrieval_priority = (
                self.REFERENCE_PRIORITY
            )

            return

        #
        # Appendix
        #

        if self.APPENDIX_PATTERN.match(
            heading,
        ):

            metadata.is_appendix = True

            metadata.quality_score = (
                self.APPENDIX_SCORE
            )

            metadata.retrieval_priority = (
                self.APPENDIX_PRIORITY
            )

            return

        #
        # Metadata
        #
        # Match the chunk BODY, not a folded heading prefix. MergeStage folds
        # the section heading in as the chunk's first line, so a section merely
        # titled e.g. "Authorization" / "DOI Routing" / "Author Contributions"
        # would otherwise be misclassified as front-matter. The genuine case
        # (a standalone "Authors: ..." / "Copyright ..." block) is unchanged:
        # when there is no folded heading line the whole text is still tested.
        #

        if self.METADATA_PATTERN.match(
            self._body_without_heading(text, heading),
        ):

            metadata.is_metadata = True

            metadata.quality_score = (
                self.METADATA_SCORE
            )

            metadata.retrieval_priority = (
                self.METADATA_PRIORITY
            )

        #
        # Heading
        #

        if (
            metadata.block_type
            == BlockType.HEADING
        ):

            metadata.quality_score = (
                self.HEADING_SCORE
            )

            metadata.retrieval_priority = (
                self.HEADING_PRIORITY
            )

        #
        # Caption
        #

        elif (
            metadata.block_type
            == BlockType.CAPTION
        ):

            metadata.is_caption = True

            metadata.quality_score = (
                self.CAPTION_SCORE
            )

            metadata.retrieval_priority = (
                self.CAPTION_PRIORITY
            )

        #
        # Table
        #

        elif (
            metadata.block_type
            == BlockType.TABLE
        ):

            metadata.is_table = True

            metadata.quality_score = (
                self.TABLE_SCORE
            )

            metadata.retrieval_priority = (
                self.TABLE_PRIORITY
            )

        #
        # Formula
        #

        elif (
            metadata.block_type
            == BlockType.FORMULA
        ):

            metadata.is_formula = True

            metadata.quality_score = (
                self.FORMULA_SCORE
            )

            metadata.retrieval_priority = (
                self.FORMULA_PRIORITY
            )