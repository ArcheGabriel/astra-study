import re

from app.chunking.models import DocumentChunk
from app.chunking.stages.base import BaseChunkStage
from app.enums.block import BlockType


class MetadataStage(BaseChunkStage):
    """
    Enriches chunks with semantic metadata.

    Responsibilities
    ----------------
    • Build heading hierarchy
    • Build heading_path
    • Populate section_title
    • Populate section_id

    The hierarchy is derived primarily from
    numbered section IDs rather than Markdown
    heading levels.

    This produces much better results for
    academic PDFs generated from LaTeX.
    """

    SECTION_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)*)\s+(.*)"
    )

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        heading_stack: list[str] = []

        depth_stack: list[int] = []

        for chunk in chunks:

            metadata = chunk.metadata

            if metadata.block_type == BlockType.HEADING:

                cleaned = self._clean_heading(
                    chunk.text,
                )

                metadata.section_id = (
                    self._extract_section_id(
                        cleaned,
                    )
                )

                depth = self._calculate_depth(
                    metadata.section_id,
                    metadata.heading_level,
                )

                while (
                    depth_stack
                    and depth_stack[-1] >= depth
                ):

                    depth_stack.pop()

                    heading_stack.pop()

                heading_stack.append(
                    cleaned,
                )

                depth_stack.append(
                    depth,
                )

            metadata.heading_path = list(
                heading_stack,
            )

            metadata.section_title = (
                heading_stack[-1]
                if heading_stack
                else None
            )

        return chunks

    def _clean_heading(
        self,
        heading: str,
    ) -> str:

        return (
            heading
            .lstrip("#")
            .strip()
        )

    def _extract_section_id(
        self,
        heading: str,
    ) -> str | None:

        match = self.SECTION_PATTERN.match(
            heading,
        )

        if match:
            return match.group(1)

        return None

    def _calculate_depth(
        self,
        section_id: str | None,
        markdown_level: int,
    ) -> int:
        """
        Calculate semantic heading depth.

        Examples
        --------
        2          -> 1
        2.1        -> 2
        2.1.3      -> 3

        Falls back to Markdown level when
        numbering is unavailable.
        """

        if section_id:

            return (
                section_id.count(".")
                + 1
            )

        return max(
            markdown_level,
            1,
        )