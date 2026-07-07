from dataclasses import dataclass, field

from app.enums.block import BlockType


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

    file_extension: str | None = None

    file_size: int = 0

    page_count: int = 0

    checksum: str | None = None

    language: str | None = None


@dataclass(slots=True)
class ExtractedParagraph:
    """
    Represents a logical text block extracted from a page.
    """

    text: str

    block_index: int

    block_type: BlockType = BlockType.UNKNOWN


@dataclass(slots=True)
class ExtractedImage:
    """
    Represents an extracted image.
    """

    page_number: int

    image_index: int

    file_path: str | None = None

    caption: str | None = None


@dataclass(slots=True)
class ExtractedTable:
    """
    Represents an extracted table.
    """

    page_number: int

    table_index: int

    markdown: str = ""


@dataclass(slots=True)
class ExtractedPage:
    """
    Represents one page inside a document.
    """

    page_number: int

    text: str = ""

    paragraphs: list[ExtractedParagraph] = field(
        default_factory=list,
    )

    images: list[ExtractedImage] = field(
        default_factory=list,
    )

    tables: list[ExtractedTable] = field(
        default_factory=list,
    )


@dataclass(slots=True)
class ExtractionResult:
    """
    Result produced by a document processor.
    """

    metadata: DocumentMetadata = field(
        default_factory=DocumentMetadata,
    )

    pages: list[ExtractedPage] = field(
        default_factory=list,
    )