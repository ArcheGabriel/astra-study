from abc import ABC, abstractmethod

from app.chunking.models import DocumentChunk
from app.ingestion.models import ExtractionResult


class BaseChunkStage(ABC):
    """
    Base interface for every chunking stage.
    """

    @abstractmethod
    def run(
        self,
        data: ExtractionResult | list[DocumentChunk],
    ) -> list[DocumentChunk]:
        """
        Process the incoming data and return chunks.
        """
        raise NotImplementedError