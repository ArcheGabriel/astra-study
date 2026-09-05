from dataclasses import dataclass, field
from uuid import UUID

from app.enums.block import BlockType
from app.document.models import BlockProvenance


@dataclass(frozen=True, slots=True)
class ContentSegment:
    """One source ``DocumentBlock`` that ``MergeStage`` folded into a chunk.

    Internal chunking metadata only -- it retains the per-block structure that
    ``build()`` would otherwise flatten into a single string, so
    ``RecursiveStage`` can route each segment by its real Docling
    ``block_type`` (never by inspecting markdown / text) and attribute
    provenance to it exactly.

    NOT written to the vector payload. Order is document order.
    """

    block_type: BlockType

    text: str

    provenance: tuple[BlockProvenance, ...] = ()

    is_heading: bool = False

    # The source ``DocumentBlock.block_index`` this segment came from, so
    # RecursiveStage can recompute a child's block range from the exact blocks
    # it represents instead of by positional arithmetic.
    source_block_index: int | None = None


def section_contains(
    outer: tuple[str, ...],
    inner: tuple[str, ...],
) -> bool:
    """True when ``inner`` names the same section as ``outer`` or a subsection
    nested inside it -- i.e. content under ``inner`` still belongs in
    ``outer``'s chunk. A sibling or ancestor section returns ``False`` and is
    a hard chunk boundary.

    ``()`` means "no section context" and contains only itself.
    """
    if not outer:
        return not inner
    return inner[: len(outer)] == outer


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

    source_type: str | None = None

    sheet_name: str | None = None

    parser: str | None = None

    language: str | None = None
    
    # ==================================================
    # Ownership Information
    # ==================================================

    user_id: int | None = None

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

    # Internal, NOT written to the vector payload: a stable per-level section
    # identity (numbered id when available, else the heading title) used by
    # the chunker to classify a heading boundary as same / descendant /
    # sibling / ancestor. Populated by MetadataStage; compared with
    # ``section_contains``.
    section_key: tuple[str, ...] = ()

    # Internal, NOT written to the vector payload: the per-source-block
    # structure MergeStage folded into this chunk (type + text + provenance),
    # in document order. RecursiveStage uses it as the authoritative source for
    # structural routing (table row-atomic / list item-atomic splitting) and
    # exact per-segment provenance. Empty for chunks built outside MergeStage;
    # RecursiveStage then falls back to its text-derived path.
    content_segments: tuple[ContentSegment, ...] = ()

    # References are deliberately compact: one entry per source block, with
    # optional Docling page coordinates rather than copied parser objects.
    provenance: list[BlockProvenance] = field(default_factory=list)

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
