from uuid import uuid4

from app.chunking.models import ChunkMetadata, DocumentChunk
from app.document.models import BlockProvenance
from app.embeddings.models import EmbeddedChunk, EmbeddingMetadata, EmbeddingVector
from app.enums.block import BlockType
from app.generation.models import GenerationRequest
from app.generation.service import GenerationService
from app.retrieval.models import RetrievedContext, RetrievalResult
from app.search.dense.mapper import DenseMapper


def test_qdrant_payload_and_citation_preserve_docling_provenance():
    chunk_id = uuid4()
    metadata = ChunkMetadata(
        document_uuid=uuid4(), chunk_uuid=chunk_id, document_name="metrics.xlsx",
        source="metrics.xlsx", source_type=".xlsx", parser="docling",
        sheet_name="Segments", section_title="Customers", block_type=BlockType.TABLE,
        provenance=[BlockProvenance(sheet_name="Segments", table_index=0)],
    )
    embedded = EmbeddedChunk(DocumentChunk("data", 0, metadata), EmbeddingVector([0.1]), EmbeddingMetadata("test", 1))
    payload = DenseMapper.to_point(embedded).payload
    assert payload["source"] == "metrics.xlsx"
    assert payload["sheet_name"] == "Segments"
    assert payload["parser"] == "docling"
    assert payload["provenance"][0]["table_index"] == 0

    context = RetrievedContext("data", "metrics.xlsx", chunk_id, .8, .9, sheet_name="Segments", block_type="table", provenance=payload["provenance"])
    request = GenerationRequest("question", RetrievalResult("question", [context], .1))
    citation = GenerationService.citations_for(request)[0]
    assert citation.sheet_name == "Segments"
    assert citation.block_type == "table"
    assert citation.provenance == payload["provenance"]


def test_old_payload_optional_provenance_defaults_are_safe():
    context = RetrievedContext("legacy", "old.pdf", uuid4(), .8, .9, page=2)
    request = GenerationRequest("question", RetrievalResult("question", [context], .1))
    citation = GenerationService.citations_for(request)[0]
    assert citation.page == 2
    assert citation.provenance is None
