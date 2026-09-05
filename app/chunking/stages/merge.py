from copy import deepcopy
from dataclasses import dataclass, field

from app.chunking.config import DEFAULT_CHUNKING_CONFIG, ChunkingConfig
from app.chunking.models import (
    ChunkMetadata,
    ContentSegment,
    DocumentChunk,
    section_contains,
)
from app.chunking.stages.base import BaseChunkStage
from app.chunking.utils.tokens import count_tokens
from app.enums.block import BlockType


def _segment_of(chunk: DocumentChunk) -> ContentSegment:
    """One ContentSegment for a source block as it enters MergeStage (each
    chunk is still 1:1 with a Docling ``DocumentBlock`` at this point)."""
    return ContentSegment(
        block_type=chunk.metadata.block_type,
        text=chunk.text.strip(),
        provenance=tuple(chunk.metadata.provenance),
        is_heading=chunk.metadata.block_type == BlockType.HEADING,
        source_block_index=chunk.metadata.block_start,
    )


@dataclass(slots=True)
class SemanticChunkBuilder:
    """
    Incrementally builds one heading-anchored section chunk.

    A heading may *seed* a builder so its title becomes the section's
    context prefix, but a builder that never receives content
    (``has_content`` stays ``False``) is dropped rather than emitted --
    a heading is context, not a retrieval vector.
    """

    chunk_index: int

    metadata: ChunkMetadata

    parts: list[str] = field(
        default_factory=list,
    )

    # One entry per contributing source block, document order. Retains the
    # per-block structural type + provenance that ``parts`` flattens away.
    segments: list[ContentSegment] = field(
        default_factory=list,
    )

    token_count: int = 0

    # True once a non-heading block carrying text has been added.
    has_content: bool = False

    # True once the effective content type is fixed. The first non-heading
    # contributor wins; the heading prefix never sets it.
    content_type_locked: bool = False

    def add(
        self,
        chunk: DocumentChunk,
    ) -> None:

        text = chunk.text.strip()

        is_heading = (
            chunk.metadata.block_type
            == BlockType.HEADING
        )

        if text:

            self.parts.append(
                text,
            )

            self.segments.append(
                _segment_of(chunk),
            )

            self.token_count += count_tokens(
                text,
            )

            if not is_heading:

                self.has_content = True

                if not self.content_type_locked:

                    self.metadata.block_type = (
                        chunk.metadata.block_type
                    )

                    self.content_type_locked = True

        #
        # Union provenance -- value-dedup, document order preserved.
        #
        for reference in chunk.metadata.provenance:
            if reference not in self.metadata.provenance:
                self.metadata.provenance.append(reference)

        #
        # Advance ranges.
        #
        if (
            chunk.metadata.page_end is not None
        ):
            self.metadata.page_end = (
                chunk.metadata.page_end
            )

        if (
            chunk.metadata.block_end is not None
        ):
            self.metadata.block_end = (
                chunk.metadata.block_end
            )

    def build(
        self,
    ) -> DocumentChunk:

        self.metadata.content_segments = tuple(self.segments)

        return DocumentChunk(

            text="\n\n".join(
                self.parts,
            ),

            chunk_index=self.chunk_index,

            metadata=self.metadata,

        )


class MergeStage(BaseChunkStage):
    """
    Group neighbouring blocks into heading-anchored *section* chunks.

    Boundaries are decided structurally with ``section_key`` containment
    (see ``section_contains``): content of the same section -- or of a
    descendant section that Docling never gave its own heading -- stays
    together; a sibling or ancestor section starts a new chunk. Every
    heading also starts a new chunk and folds into that chunk's text as its
    context prefix. A heading that never gains content is not emitted.

    This stage still produces pre-embedding "sections" up to
    ``section_hard`` tokens; RecursiveStage windows them down to the
    embedding limit.
    """

    def __init__(
        self,
        config: ChunkingConfig | None = None,
    ) -> None:

        self._config = config or DEFAULT_CHUNKING_CONFIG

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[DocumentChunk]:

        if not chunks:

            return []

        merged: list[
            DocumentChunk
        ] = []

        builder: SemanticChunkBuilder | None = None

        for chunk in chunks:

            if builder is None:

                builder = self._start_builder(
                    chunk,
                )

                continue

            if self._should_flush(
                builder,
                chunk,
            ):

                self._emit(
                    builder,
                    merged,
                )

                builder = self._start_builder(
                    chunk,
                )

                continue

            builder.add(
                chunk,
            )

        self._emit(
            builder,
            merged,
        )

        return merged

    def _emit(
        self,
        builder: SemanticChunkBuilder | None,
        merged: list[DocumentChunk],
    ) -> None:
        """
        Emit ``builder`` -- unless it only ever held a heading (or nothing),
        in which case it is context, not a retrieval vector, and is dropped.
        The heading's title still survives in the ``heading_path`` of every
        descendant chunk.
        """

        if (
            builder is not None
            and builder.has_content
        ):

            merged.append(
                builder.build(),
            )

    def _start_builder(
        self,
        chunk: DocumentChunk,
    ) -> SemanticChunkBuilder:
        """
        Start a new section chunk.

        Every metadata field is preserved by deep-copying the seed rather
        than reconstructing ChunkMetadata.
        """

        metadata = deepcopy(
            chunk.metadata,
        )

        is_heading = (
            chunk.metadata.block_type
            == BlockType.HEADING
        )

        text = chunk.text.strip()

        return SemanticChunkBuilder(

            chunk_index=chunk.chunk_index,

            metadata=metadata,

            parts=[text] if text else [],

            segments=[_segment_of(chunk)] if text else [],

            token_count=count_tokens(
                chunk.text,
            ),

            has_content=bool(text) and not is_heading,

            content_type_locked=not is_heading,

        )

    def _should_flush(
        self,
        builder: SemanticChunkBuilder,
        incoming: DocumentChunk,
    ) -> bool:
        """
        Decide whether ``incoming`` starts a new section chunk.
        """

        current = builder.metadata

        metadata = incoming.metadata

        #
        # Absolute size ceiling for a pre-split section.
        #
        if (
            builder.token_count
            >= self._config.section_hard
        ):
            return True

        #
        # A heading always starts a new (sub)section chunk. It never merges
        # backwards into accumulated content -- a descendant heading must
        # not absorb its parent's text.
        #
        if (
            metadata.block_type
            == BlockType.HEADING
        ):
            return True

        #
        # Structural boundary: content that is not within the builder's
        # section -- a sibling or ancestor section -- starts a new chunk.
        #
        if not section_contains(
            current.section_key,
            metadata.section_key,
        ):
            return True

        #
        # Keep tables / lists / captions / page-number blocks out of an
        # already-large prose section (existing intent).
        #
        if (
            builder.token_count
            >= self._config.section_soft
        ):

            if metadata.block_type in {

                BlockType.TABLE,

                BlockType.CAPTION,

                BlockType.LIST,

                BlockType.PAGE_NUMBER,

            }:

                return True

        return False
