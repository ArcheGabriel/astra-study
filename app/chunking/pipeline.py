from app.chunking.stages.finalize import FinalizeStage
from app.chunking.stages.quality import QualityStage
from app.chunking.stages.semantic import SemanticStage
from app.chunking.stages.recursive import RecursiveStage
from app.chunking.stages.metadata import MetadataStage
from app.chunking.stages.merge import MergeStage
from app.chunking.models import DocumentChunk
from app.chunking.stages.base import BaseChunkStage
from app.chunking.stages.filter import FilterStage
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
            MetadataStage(),
            MergeStage(),
            RecursiveStage(),
            SemanticStage(),
            FilterStage(),
            QualityStage(),
            FinalizeStage(),
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