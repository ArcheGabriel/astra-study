from app.chunking.models import (
    ChunkMetadata,
    DocumentChunk,
)
from app.chunking.stages.base import BaseChunkStage
from app.enums.block import BlockType
from app.ingestion.models import ExtractionResult


class ParagraphStage(BaseChunkStage):
    """
    Creates one chunk from each extracted paragraph.
    """

    def run(
        self,
        data: ExtractionResult | list[DocumentChunk],
    ) -> list[DocumentChunk]:

        if not isinstance(data, ExtractionResult):
            raise TypeError(
                "ParagraphStage expects an ExtractionResult."
            )

        chunks: list[DocumentChunk] = []

        chunk_index = 0

        for page in data.pages:

            for paragraph in page.paragraphs:

                if paragraph.block_type == BlockType.FOOTER:
                    continue

                chunks.append(
                    DocumentChunk(
                        text=paragraph.text,
                        chunk_index=chunk_index,
                        metadata=ChunkMetadata(
                            page_number=page.page_number,
                            block_index=paragraph.block_index,
                            block_type=paragraph.block_type,
                            title=data.metadata.title,
                            author=data.metadata.author,
                            subject=data.metadata.subject,
                            language=data.metadata.language,
                            checksum=data.metadata.checksum,
                        ),
                    )
                )

                chunk_index += 1

        return chunks