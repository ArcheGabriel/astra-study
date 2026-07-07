from dataclasses import dataclass

from app.enums.block import BlockType


@dataclass(slots=True)
class ChunkMetadata:
    """
    Metadata associated with a document chunk.
    """

    page_number: int

    block_index: int

    block_type: BlockType

    title: str | None = None

    author: str | None = None

    subject: str | None = None

    language: str | None = None

    checksum: str | None = None

    source: str | None = None

    document_id: int | None = None


@dataclass(slots=True)
class DocumentChunk:
    """
    Represents a chunk extracted from a document.
    """

    text: str

    chunk_index: int

    metadata: ChunkMetadata