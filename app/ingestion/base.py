from abc import ABC, abstractmethod
from pathlib import Path

from app.ingestion.models import ExtractionResult


class BaseProcessor(ABC):
    """
    Base class for every document processor.
    """

    @abstractmethod
    def extract(
        self,
        file_path: Path,
    ) -> ExtractionResult:
        """
        Extract structured information from a document.
        """
        raise NotImplementedError