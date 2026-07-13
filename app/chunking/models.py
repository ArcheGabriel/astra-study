from dataclasses import dataclass, field
from uuid import UUID

from app.enums.block import BlockType


@dataclass(slots=True)
class ChunkMetadata:
    """
    Metadata associated with a document chunk.

    This metadata flows through the entire RAG pipeline.

    Upload
        ↓
    Extraction
        ↓
    Chunking
        ↓
    Embeddings
        ↓
    Vector Database
        ↓
    Retrieval
        ↓
    Citation
    """

    # ==================================================
    # Document Information
    # ==================================================

    document_id: int | None = None

    document_uuid: UUID | None = None

    document_name: str | None = None

    checksum: str | None = None

    source: str | None = None

    language: str | None = None

    # ==================================================
    # Chunk Information
    # ==================================================

    chunk_uuid: UUID | None = None

    parent_chunk_uuid: UUID | None = None

    # ==================================================
    # Position Information
    # ==================================================

    page_start: int | None = None

    page_end: int | None = None

    block_start: int | None = None

    block_end: int | None = None

    # ==================================================
    # Semantic Information
    # ==================================================

    block_type: BlockType = BlockType.UNKNOWN

    heading_level: int = 0

    heading_path: list[str] = field(
        default_factory=list,
    )

    section_id: str | None = None

    section_title: str | None = None

    # ==================================================
    # Retrieval Information
    # ==================================================

    token_count: int = 0

    character_count: int = 0

    quality_score: float = 1.0

    retrieval_priority: int = 100

    # ==================================================
    # Classification Flags
    # ==================================================

    is_reference: bool = False

    is_appendix: bool = False

    is_metadata: bool = False

    is_caption: bool = False

    is_table: bool = False

    is_formula: bool = False

    # ==================================================
    # Original Document Metadata
    # ==================================================

    title: str | None = None

    author: str | None = None

    subject: str | None = None


@dataclass(slots=True)
class DocumentChunk:
    """
    Represents one chunk that will eventually
    be embedded and stored in the vector database.
    """

    text: str

    chunk_index: int

    metadata: ChunkMetadata

    parent_chunk: int | None = None