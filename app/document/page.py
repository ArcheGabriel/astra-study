from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MarkdownPage:
    """
    Represents one Markdown page produced by a parser.

    This is the canonical representation of a page before
    it is parsed into semantic DocumentBlocks.
    """

    # --------------------------------------------------
    # Page Information
    # --------------------------------------------------

    page_number: int

    page_count: int

    # --------------------------------------------------
    # Markdown Content
    # --------------------------------------------------

    markdown: str

    # --------------------------------------------------
    # Layout Information
    # --------------------------------------------------

    page_boxes: list[dict[str, Any]] = field(
        default_factory=list,
    )

    # --------------------------------------------------
    # Table of Contents Information
    # --------------------------------------------------

    toc_items: list[Any] = field(
        default_factory=list,
    )

    # --------------------------------------------------
    # Original page metadata
    # --------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
