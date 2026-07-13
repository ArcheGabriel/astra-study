from dataclasses import dataclass, field

from app.enums.block import BlockType


@dataclass(slots=True)
class DocumentBlock:
    """
    Represents one semantic block extracted from a document.

    This is the canonical representation produced by the
    document layer and consumed by the chunking pipeline.

    Every parser (PyMuPDF4LLM, Docling, OCR, HTML, etc.)
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

    metadata: dict[str, str] = field(
        default_factory=dict,
    )