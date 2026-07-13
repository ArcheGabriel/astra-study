from copy import deepcopy
from dataclasses import dataclass, field

from app.chunking.models import (
    ChunkMetadata,
    DocumentChunk,
)
from app.chunking.stages.base import BaseChunkStage
from app.chunking.utils.tokens import count_tokens
from app.enums.block import BlockType


@dataclass(slots=True)
class SemanticChunkBuilder:
    """
    Incrementally builds one semantic chunk while preserving
    metadata from the originating blocks.
    """

    chunk_index: int

    metadata: ChunkMetadata

    parts: list[str] = field(
        default_factory=list,
    )

    token_count: int = 0

    def add(
        self,
        chunk: DocumentChunk,
    ) -> None:

        text = chunk.text.strip()

        if text:

            self.parts.append(
                text,
            )

            self.token_count += count_tokens(
                text,
            )

        #
        # Update ranges
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

        return DocumentChunk(

            text="\n\n".join(
                self.parts,
            ),

            chunk_index=self.chunk_index,

            metadata=self.metadata,

        )


class MergeStage(BaseChunkStage):
    """
    Merge neighbouring document blocks into semantic sections.

    This stage intentionally creates semantic chunks that are
    larger than embedding chunks.

    RecursiveStage will later split them into embedding-sized
    windows.
    """

    #
    # Preferred semantic section size.
    #
    SOFT_LIMIT = 1200

    #
    # Never exceed this size.
    #
    HARD_LIMIT = 1600

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

                merged.append(
                    builder.build(),
                )

                builder = self._start_builder(
                    chunk,
                )

                continue

            builder.add(
                chunk,
            )

        if builder is not None:

            merged.append(
                builder.build(),
            )

        return merged

    def _start_builder(
        self,
        chunk: DocumentChunk,
    ) -> SemanticChunkBuilder:
        """
        Start a new semantic chunk.

        IMPORTANT:
        Preserve every metadata field by deep-copying
        instead of reconstructing ChunkMetadata manually.
        """

        metadata = deepcopy(
            chunk.metadata,
        )

        return SemanticChunkBuilder(

            chunk_index=chunk.chunk_index,

            metadata=metadata,

            parts=[
                chunk.text.strip(),
            ],

            token_count=count_tokens(
                chunk.text,
            ),

        )

    def _should_flush(
        self,
        builder: SemanticChunkBuilder,
        incoming: DocumentChunk,
    ) -> bool:
        """
        Decide whether the current semantic chunk
        should be finalized.
        """

        current = builder.metadata

        metadata = incoming.metadata

        #
        # Hard limit.
        #
        if (
            builder.token_count
            >= self.HARD_LIMIT
        ):
            return True

        #
        # Every heading begins a new semantic section.
        #
        if (
            metadata.block_type
            == BlockType.HEADING
        ):
            return True

        #
        # Section changed.
        #
        if (
            metadata.section_id
            != current.section_id
        ):
            return True

        #
        # Heading hierarchy changed.
        #
        if (
            metadata.heading_path
            != current.heading_path
        ):
            return True

        #
        # Natural split after soft limit.
        #
        if (
            builder.token_count
            >= self.SOFT_LIMIT
        ):

            if metadata.block_type in {

                BlockType.TABLE,

                BlockType.CAPTION,

                BlockType.LIST,

                BlockType.PAGE_NUMBER,

            }:

                return True

        return False