from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from app.config.settings import settings

# Hugging Face model caches use symlinks by default. Disable them before
# Docling imports Hugging Face so first-run model downloads work on standard
# Windows developer accounts without Developer Mode or administrator rights.
if settings.DOCLING_DISABLE_HF_SYMLINKS:
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import (
    CsvFormatOption,
    DocumentConverter,
    ExcelFormatOption,
    ImageFormatOption,
    PdfFormatOption,
    WordFormatOption,
)

from app.document.models import DocumentBlock
from app.enums.block import BlockType
from app.ingestion.base import BaseProcessor
from app.ingestion.models import DocumentMetadata, ExtractionResult, ExtractedTable
from app.utils.hash import calculate_sha256

logger = logging.getLogger(__name__)


class DoclingProcessor(BaseProcessor):
    """Convert every supported upload into Astra Study's existing block contract."""

    def __init__(self, converter: Any | None = None) -> None:
        self.converter = converter or self._build_converter()

    @staticmethod
    def _build_converter() -> DocumentConverter:
        pdf_options = PdfPipelineOptions()
        pdf_options.do_ocr = settings.DOCLING_OCR_ENABLED
        pdf_options.ocr_options = RapidOcrOptions(
            lang=list(settings.DOCLING_OCR_LANGUAGES),
            force_full_page_ocr=settings.DOCLING_FORCE_FULL_PAGE_OCR,
        )
        pdf_options.do_table_structure = True

        return DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.DOCX,
                InputFormat.XLSX,
                InputFormat.CSV,
                InputFormat.IMAGE,
            ],
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
                InputFormat.DOCX: WordFormatOption(),
                InputFormat.XLSX: ExcelFormatOption(),
                InputFormat.CSV: CsvFormatOption(),
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pdf_options),
            },
        )

    def extract(self, file_path: Path) -> ExtractionResult:
        try:
            conversion = self.converter.convert(file_path)
        except Exception as exc:
            logger.exception("Docling conversion failed for %s", file_path.name)
            raise ValueError("The document could not be processed.") from exc

        document = conversion.document
        metadata = DocumentMetadata(
            title=getattr(document, "name", None),
            file_name=file_path.name,
            file_extension=file_path.suffix.lower(),
            file_size=file_path.stat().st_size,
            page_count=len(getattr(document, "pages", {}) or {}),
            checksum=calculate_sha256(file_path),
        )

        blocks: list[DocumentBlock] = []
        tables: list[ExtractedTable] = []
        for item, level in document.iterate_items():
            block = self._to_block(
                item=item,
                level=level,
                document=document,
                paginated=file_path.suffix.lower() == ".pdf",
                file_extension=file_path.suffix.lower(),
            )
            if block is None:
                continue
            block.block_index = len(blocks)
            blocks.append(block)
            if block.block_type is BlockType.TABLE:
                tables.append(
                    ExtractedTable(
                        table_index=len(tables),
                        page_number=block.page_number,
                        markdown=block.text,
                        metadata=dict(block.metadata),
                    )
                )

        if not blocks:
            raise ValueError("No extractable text was found in the uploaded document.")

        return ExtractionResult(metadata=metadata, blocks=blocks, tables=tables)

    def _to_block(
        self,
        *,
        item: Any,
        level: int,
        document: Any,
        paginated: bool,
        file_extension: str,
    ) -> DocumentBlock | None:
        label = getattr(getattr(item, "label", None), "value", "")
        page_number = self._page_number(item)
        metadata = {"source_type": file_extension, "parser": "docling"}
        sheet_name = self._sheet_name(item, document)
        if sheet_name:
            metadata["sheet_name"] = sheet_name

        if label == "table":
            text = item.export_to_markdown(doc=document).strip()
            block_type = BlockType.TABLE
        else:
            text = str(getattr(item, "text", "")).strip()
            if label == "section_header":
                block_type = BlockType.HEADING
            elif label in {"list_item", "checkbox_selected", "checkbox_unselected"}:
                block_type = BlockType.LIST
            elif label in {"caption", "footnote"}:
                block_type = BlockType.CAPTION
            elif label in {"page_header", "page_footer"}:
                block_type = BlockType.HEADER if label == "page_header" else BlockType.FOOTER
            else:
                block_type = BlockType.TEXT

        if not text:
            return None
        if not paginated:
            page_number = None
        return DocumentBlock(
            text=text,
            block_type=block_type,
            level=max(level, 1) if block_type is BlockType.HEADING else 0,
            page_number=page_number,
            metadata=metadata,
        )

    @staticmethod
    def _page_number(item: Any) -> int | None:
        provenance = getattr(item, "prov", None) or []
        page_no = getattr(provenance[0], "page_no", None) if provenance else None
        return page_no if isinstance(page_no, int) and page_no > 0 else None

    @staticmethod
    def _sheet_name(item: Any, document: Any) -> str | None:
        parent = getattr(item, "parent", None)
        if parent is None:
            return None
        try:
            group = parent.resolve(document)
        except Exception:
            return None
        return getattr(group, "name", None) if getattr(getattr(group, "label", None), "value", "") == "sheet" else None
