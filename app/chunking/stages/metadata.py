import re

from app.chunking.models import DocumentChunk
from app.chunking.stages.base import BaseChunkStage
from app.enums.block import BlockType


class MetadataStage(BaseChunkStage):
    """
    Enriches chunks with semantic / structural metadata.

    Responsibilities
    ----------------
    • Build the heading hierarchy (``heading_path``)
    • Populate ``section_title``, ``section_id`` and the internal
      ``section_key``
    • Propagate the enclosing section's identity onto *every* chunk, not
      just heading chunks

    Section numbering is derived from the heading text and supports both the
    LaTeX style ("1 Title", "2.1.3 Title") and the Word / Markdown style
    ("1. Title", "1.2. Title" -- trailing dot optional). Unnumbered headings
    fall back to their Markdown heading level for depth and to their title
    for identity.
    """

    # Numbered-section prefix:
    #   "1"  "1.2"  "2.1.3"   with an optional trailing dot ("1.", "1.2.")
    # followed by whitespace and a title.
    SECTION_PATTERN = re.compile(
        r"^(\d+(?:\.\d+)*)\.?\s+(\S.*)$"
    )

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        heading_stack: list[str] = []   # cleaned heading titles
        depth_stack: list[int] = []     # semantic depth per level
        key_stack: list[str] = []       # stable per-level identity

        for chunk in chunks:

            metadata = chunk.metadata

            if metadata.block_type == BlockType.HEADING:

                cleaned = self._clean_heading(chunk.text)

                section_id = self._extract_section_id(cleaned)
                metadata.section_id = section_id

                depth = self._calculate_depth(
                    section_id,
                    metadata.heading_level,
                )

                # Drop sibling / deeper levels.
                while depth_stack and depth_stack[-1] >= depth:
                    depth_stack.pop()
                    heading_stack.pop()
                    key_stack.pop()

                # Collapse a consecutive duplicate title. Docling sometimes
                # emits the same heading at two adjacent levels (e.g.
                # "Executive Summary" as both an H2 and an H3); the second
                # occurrence must not deepen the path.
                if not (heading_stack and heading_stack[-1] == cleaned):
                    heading_stack.append(cleaned)
                    depth_stack.append(depth)
                    key_stack.append(section_id or cleaned)

            metadata.heading_path = list(heading_stack)
            metadata.section_title = (
                heading_stack[-1] if heading_stack else None
            )
            metadata.section_key = tuple(key_stack)

            # Content chunks inherit the enclosing section's number so that
            # downstream stages can tell "this paragraph belongs to 3.1" from
            # "this is a different section" (previously content chunks always
            # had section_id = None, which orphaned every numbered heading).
            if (
                metadata.block_type != BlockType.HEADING
                and heading_stack
            ):
                metadata.section_id = self._extract_section_id(
                    heading_stack[-1]
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

        match = self.SECTION_PATTERN.match(heading)

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
        1        -> 1
        2.1      -> 2
        2.1.3    -> 3

        Falls back to the Markdown heading level when numbering is
        unavailable.
        """

        if section_id:
            return section_id.count(".") + 1

        return max(markdown_level, 1)
