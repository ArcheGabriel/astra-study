from pathlib import Path

import fitz

from app.ingestion.base import BaseProcessor
from app.ingestion.models import (
    DocumentMetadata,
    ExtractedPage,
    ExtractedParagraph,
    ExtractionResult,
)
from app.utils.hash import calculate_sha256
from app.enums.block import BlockType


class PDFProcessor(BaseProcessor):
    """
    Handles PDF document extraction using PyMuPDF.
    """

    def _classify_block(
        self,
        text: str,
        page_number: int,
    ) -> BlockType:
        """
        Classify an extracted text block.
        """

        stripped = text.strip()

        if not stripped:
            return BlockType.UNKNOWN

        if stripped == str(page_number):
            return BlockType.FOOTER

        if stripped.lower().startswith(
            "figure "
        ):
            return BlockType.CAPTION

        if stripped.startswith(
            "•"
        ):
            return BlockType.LIST

        return BlockType.TEXT

    def extract(
        self,
        file_path: Path,
    ) -> ExtractionResult:
        """
        Extract text and metadata from a PDF.
        """

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

        pages: list[ExtractedPage] = []

        for page_number, page in enumerate(
            pdf,
            start=1,
        ):

            page_dict = page.get_text(
                "dict",
            )

            paragraphs: list[
                ExtractedParagraph
            ] = []

            block_index = 0

            for block in page_dict["blocks"]:

                if block["type"] != 0:
                    continue

                paragraph_lines: list[str] = []

                for line in block["lines"]:

                    line_text: list[str] = []

                    for span in line["spans"]:

                        text = span["text"].strip()

                        if text:
                            line_text.append(
                                text,
                            )

                    if line_text:

                        paragraph_lines.append(
                            " ".join(
                                line_text,
                            )
                        )

                paragraph_text = "\n".join(
                    paragraph_lines,
                ).strip()

                if not paragraph_text:
                    continue

                paragraphs.append(
                    ExtractedParagraph(
                        text=paragraph_text,
                        block_index=block_index,
                        block_type=self._classify_block(
                            paragraph_text,
                            page_number,
                        ),
                    )
                )

                block_index += 1

            page_text = "\n\n".join(
                paragraph.text
                for paragraph in paragraphs
            )

            pages.append(
                ExtractedPage(
                    page_number=page_number,
                    text=page_text,
                    paragraphs=paragraphs,
                )
            )

        pdf.close()

        return ExtractionResult(
            metadata=metadata,
            pages=pages,
        )