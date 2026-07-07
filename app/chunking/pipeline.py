from app.chunking.models import DocumentChunk
from app.chunking.stages.base import BaseChunkStage
from app.chunking.stages.paragraph import ParagraphStage
from app.ingestion.models import ExtractionResult


class ChunkPipeline:
    """
    Executes the configured chunking stages.
    """

    def __init__(
        self,
        stages: list[BaseChunkStage] | None = None,
    ) -> None:

        self.stages = stages or [
            ParagraphStage(),
        ]

    def run(
        self,
        extraction_result: ExtractionResult,
    ) -> list[DocumentChunk]:

        data: ExtractionResult | list[DocumentChunk]

        data = extraction_result

        for stage in self.stages:

            data = stage.run(
                data,
            )

        return data