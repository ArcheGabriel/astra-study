from pathlib import Path

from app.ingestion.base import BaseProcessor
from app.ingestion.processors.docling import DoclingProcessor


class ProcessorFactory:
    """
    Returns the correct processor for a document.
    """

    @staticmethod
    def get_processor(
        file_path: Path,
    ) -> BaseProcessor:

        suffix = file_path.suffix.lower()

        if suffix in {".pdf", ".docx", ".xlsx", ".csv", ".jpg", ".jpeg", ".png"}:
            return DoclingProcessor()

        raise ValueError(
            f"No processor registered for '{suffix}'."
        )
