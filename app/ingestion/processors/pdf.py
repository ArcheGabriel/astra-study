from pathlib import Path

import fitz

from app.document.converter import DocumentConverter
from app.document.parser import DocumentParser
from app.ingestion.base import BaseProcessor
from app.ingestion.extractors.markdown import (
    MarkdownExtractor,
)
from app.ingestion.models import (
    DocumentMetadata,
    ExtractionResult,
)
from app.utils.hash import calculate_sha256


class PDFProcessor(BaseProcessor):
    """
    PDF processor.

    Responsibilities
    ----------------
    1. Read PDF metadata
    2. Extract page-wise Markdown
    3. Parse each page
    4. Convert tokens into semantic DocumentBlocks
    5. Return ExtractionResult
    """

    def __init__(
        self,
    ) -> None:

        self.markdown_extractor = (
            MarkdownExtractor()
        )

        self.parser = (
            DocumentParser()
        )

        self.converter = (
            DocumentConverter()
        )

    def extract(
        self,
        file_path: Path,
    ) -> ExtractionResult:

        pdf = fitz.open(
            file_path,
        )

        metadata = DocumentMetadata(
            title=pdf.metadata.get(
                "title",
            ),
            author=pdf.metadata.get(
                "author",
            ),
            subject=pdf.metadata.get(
                "subject",
            ),
            keywords=pdf.metadata.get(
                "keywords",
            ),
            creator=pdf.metadata.get(
                "creator",
            ),
            producer=pdf.metadata.get(
                "producer",
            ),
            file_name=file_path.name,
            file_extension=file_path.suffix.lower(),
            file_size=file_path.stat().st_size,
            page_count=len(pdf),
            checksum=calculate_sha256(
                file_path,
            ),
            language=None,
        )

        pdf.close()

        markdown_pages = (
            self.markdown_extractor.extract(
                file_path,
            )
        )

        blocks = []

        for page in markdown_pages:

            tokens = (
                self.parser.parse(
                    page.markdown,
                )
            )

            page_blocks = (
                self.converter.convert(
                    tokens,
                    page,
                )
            )

            blocks.extend(
                page_blocks,
            )

        return ExtractionResult(
            metadata=metadata,
            blocks=blocks,
        )