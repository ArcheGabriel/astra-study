from __future__ import annotations

from app.ingestion.processors.docling import DoclingProcessor


class PDFProcessor(DoclingProcessor):
    """
    Backward-compatible PDF processor.

    PDF ingestion is now handled by DoclingProcessor.
    This wrapper exists so older tests and integrations that
    still import PDFProcessor continue to work.
    """

    pass
