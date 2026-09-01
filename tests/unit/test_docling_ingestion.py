from pathlib import Path
from types import SimpleNamespace

import pytest

from app.chunking.pipeline import ChunkPipeline
from app.enums.block import BlockType
from app.ingestion.factory import ProcessorFactory
from app.ingestion.processors.docling import DoclingProcessor


class FakeItem:
    def __init__(self, label, text="", page_no=None, parent=None, bbox=None):
        self.label = SimpleNamespace(value=label)
        self.text = text
        self.prov = [] if page_no is None else [SimpleNamespace(page_no=page_no, bbox=bbox)]
        self.parent = parent

    def export_to_markdown(self, doc):
        return self.text


class FakeDocument:
    def __init__(self, items):
        self.name = "fixture"
        self.pages = {1: object()}
        self._items = items

    def iterate_items(self):
        return iter(self._items)


class FakeConverter:
    def __init__(self, document):
        self.document = document

    def convert(self, path):
        return SimpleNamespace(document=self.document)


class FailingConverter:
    def convert(self, path):
        raise RuntimeError("corrupt input")


@pytest.mark.parametrize("suffix", [".pdf", ".docx", ".xlsx", ".csv", ".jpg", ".jpeg", ".png"])
def test_supported_formats_normalize_to_existing_blocks(tmp_path, suffix):
    path = tmp_path / f"study{suffix}"
    path.write_bytes(b"fixture")
    items = [
        (FakeItem("section_header", "Overview", page_no=1), 1),
        (FakeItem("paragraph", "Useful extracted text", page_no=1), 2),
        (FakeItem("table", "| Name | Score |\n|---|---|\n| Ada | 10 |", page_no=1), 2),
    ]
    result = DoclingProcessor(FakeConverter(FakeDocument(items))).extract(path)

    assert result.metadata.file_extension == suffix
    assert [block.block_type for block in result.blocks] == [BlockType.HEADING, BlockType.TEXT, BlockType.TABLE]
    assert result.blocks[1].page_number == (1 if suffix == ".pdf" else None)
    assert result.tables[0].markdown.startswith("| Name")


def test_xlsx_sheet_metadata_reaches_vector_ready_chunk(tmp_path):
    path = tmp_path / "scores.xlsx"
    path.write_bytes(b"fixture")
    sheet = SimpleNamespace(label=SimpleNamespace(value="sheet"), name="Results")
    parent = SimpleNamespace(resolve=lambda document: sheet)
    result = DoclingProcessor(
        FakeConverter(FakeDocument([(FakeItem("table", "| Student | Mark |", parent=parent), 1)]))
    ).extract(path)

    chunks = ChunkPipeline().run(result)
    assert chunks[0].metadata.sheet_name == "Results"
    assert chunks[0].metadata.page_start is None


def test_pdf_page_and_section_metadata_survive_chunking(tmp_path):
    path = tmp_path / "notes.pdf"
    path.write_bytes(b"fixture")
    result = DoclingProcessor(
        FakeConverter(FakeDocument([
            (FakeItem("section_header", "1 Introduction", page_no=2), 1),
            (FakeItem("paragraph", "Citation-ready content.", page_no=2), 2),
        ]))
    ).extract(path)

    chunks = ChunkPipeline().run(result)
    assert chunks[-1].metadata.page_start == 2
    assert chunks[-1].metadata.section_title == "1 Introduction"


def test_docling_bbox_and_table_provenance_survive_chunking(tmp_path):
    path = tmp_path / "table.pdf"
    path.write_bytes(b"fixture")
    bbox = SimpleNamespace(l=10, t=20, r=30, b=40, coord_origin="TOPLEFT")
    result = DoclingProcessor(FakeConverter(FakeDocument([
        (FakeItem("table", "| A | B |", page_no=3, bbox=bbox), 1),
    ]))).extract(path)

    reference = result.blocks[0].provenance[0]
    assert reference.page_number == 3
    assert reference.bbox == {"left": 10.0, "top": 20.0, "right": 30.0, "bottom": 40.0, "coord_origin": "TOPLEFT"}
    assert reference.table_index == 0
    assert ChunkPipeline().run(result)[0].metadata.provenance[0].bbox == reference.bbox


def test_unsupported_extension_is_rejected_by_factory(tmp_path):
    with pytest.raises(ValueError, match="No processor"):
        ProcessorFactory.get_processor(tmp_path / "notes.exe")


def test_corrupt_or_empty_docling_output_fails_cleanly(tmp_path):
    path = tmp_path / "empty.pdf"
    path.write_bytes(b"fixture")
    processor = DoclingProcessor(FakeConverter(FakeDocument([])))
    with pytest.raises(ValueError, match="No extractable text"):
        processor.extract(path)


def test_docling_conversion_failure_is_sanitized(tmp_path):
    path = tmp_path / "corrupt.pdf"
    path.write_bytes(b"not a PDF")
    with pytest.raises(ValueError, match="could not be processed"):
        DoclingProcessor(FailingConverter()).extract(path)
