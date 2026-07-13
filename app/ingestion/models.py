from dataclasses import dataclass, field

from app.document.models import DocumentBlock


@dataclass(slots=True)
class DocumentMetadata:
    """
    Metadata extracted from a document.
    """

    title: str | None = None

    author: str | None = None

    subject: str | None = None

    keywords: str | None = None

    creator: str | None = None

    producer: str | None = None

    file_name: str | None = None

    file_extension: str |None = None

    file_size: int = 0

    page_count: int = 0

    checksum: str | None = None

    language: str | None = None


@dataclass(slots=True)
class ExtractedImage:
    """
    Represents an extracted image.

    Images will later be processed by OCR,
    caption generation and multimodal models.
    """

    image_index: int

    page_number: int | None = None

    file_path: str | None = None

    caption: str | None = None

    metadata: dict = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class ExtractedTable:
    """
    Represents one extracted table.

    Future parsers (Docling etc.)
    will populate this.
    """

    table_index: int

    page_number: int | None = None

    markdown: str = ""

    metadata: dict = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class ExtractionResult:
    """
    Canonical output produced by every processor.

    Every processor converts its native representation
    into semantic DocumentBlocks.
    """

    metadata: DocumentMetadata = field(
        default_factory=DocumentMetadata,
    )

    blocks: list[DocumentBlock] = field(
        default_factory=list,
    )

    images: list[ExtractedImage] = field(
        default_factory=list,
    )

    tables: list[ExtractedTable] = field(
        default_factory=list,
    )