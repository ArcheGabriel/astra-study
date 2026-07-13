from uuid import uuid5, NAMESPACE_URL

from app.chunking.models import (
    ChunkMetadata,
    DocumentChunk,
)
from app.chunking.stages.base import BaseChunkStage
from app.chunking.utils.tokens import count_tokens
from app.ingestion.models import ExtractionResult


class ParagraphStage(BaseChunkStage):
    """
    Converts extracted document blocks into DocumentChunks.

    This is the first stage of the chunking pipeline.

    Responsibilities
    ----------------
    • Create one DocumentChunk per DocumentBlock
    • Generate stable document UUID
    • Generate stable chunk UUID
    • Populate token count
    • Populate character count

    No semantic processing occurs here.
    """

    def run(
        self,
        data: ExtractionResult | list[DocumentChunk],
    ) -> list[DocumentChunk]:

        if not isinstance(
            data,
            ExtractionResult,
        ):
            raise TypeError(
                "ParagraphStage expects ExtractionResult."
            )

        chunks: list[DocumentChunk] = []

        #
        # Stable document UUID.
        #
        # Same checksum -> same UUID forever.
        #
        document_uuid = uuid5(
            NAMESPACE_URL,
            data.metadata.checksum,
        )

        for chunk_index, block in enumerate(
            data.blocks,
        ):

            text = block.text.strip()

            #
            # Stable chunk UUID.
            #
            # Depends only on:
            #
            # document
            # page
            # block
            #
            chunk_uuid = uuid5(
                document_uuid,
                f"{block.page_number}:{block.block_index}",
            )

            metadata = ChunkMetadata(

                #
                # Document
                #
                document_uuid=document_uuid,

                document_name=data.metadata.file_name,

                checksum=data.metadata.checksum,

                language=data.metadata.language,

                #
                # Chunk
                #
                chunk_uuid=chunk_uuid,

                #
                # Statistics
                #
                token_count=count_tokens(
                    text,
                ),

                character_count=len(
                    text,
                ),

                #
                # Original metadata
                #
                title=data.metadata.title,

                author=data.metadata.author,

                subject=data.metadata.subject,

                #
                # Position
                #
                page_start=block.page_number,

                page_end=block.page_number,

                block_start=block.block_index,

                block_end=block.block_index,

                #
                # Semantic
                #
                block_type=block.block_type,

                heading_level=block.level,

            )

            chunks.append(

                DocumentChunk(

                    text=text,

                    chunk_index=chunk_index,

                    metadata=metadata,

                )

            )

        return chunks