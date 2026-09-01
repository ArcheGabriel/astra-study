from dataclasses import dataclass, field
from typing import Any

from app.enums.block import BlockType


@dataclass(slots=True)
class BlockProvenance:
    """A compact, parser-neutral reference to the source of one block."""

    page_number: int | None = None
    bbox: dict[str, float | str] | None = None
    source_item_id: str | None = None
    charspan: tuple[int, int] | None = None
    sheet_name: str | None = None
    table_index: int | None = None


@dataclass(slots=True)
class DocumentBlock:
    """
    Represents one semantic block extracted from a document.

    This is the canonical representation produced by the
    document layer and consumed by the chunking pipeline.

    Every parser (Docling, OCR, HTML, etc.)
    should map its output into this model.
    """

    # --------------------------------------------------
    # Content
    # --------------------------------------------------

    text: str

    block_type: BlockType

    level: int = 0

    # --------------------------------------------------
    # Position inside the document
    # --------------------------------------------------

    page_number: int | None = None

    block_index: int | None = None

    # --------------------------------------------------
    # Additional parser-specific information
    # --------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    provenance: list[BlockProvenance] = field(default_factory=list)
