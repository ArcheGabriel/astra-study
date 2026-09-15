"""
Executable specification for RBAC-5C: RBAC-aware Qdrant payloads for newly
indexed documents.

Covers, with no live Qdrant connection and no database:

- ``IngestionService.ingest_document`` stamps ``document_id``,
  ``organisation_id``, ``team_id``, ``access_scope`` onto every chunk's
  metadata from the single, already-loaded ``Document`` row (no repeated
  per-chunk query);
- ``HybridMapper.build_payload`` writes ``schema_version=3`` plus the new
  RBAC fields, while every pre-existing payload field is still present and
  unchanged;
- ``document_id`` in the payload is the real SQL ``Document.id`` -- never
  derived from ``document_uuid``/``checksum``/anything content-based;
- ``app/search/dense/mapper.py::DenseMapper`` (the dense-only,
  non-production-indexing path) is confirmed untouched -- it still writes
  ``schema_version=2`` and no RBAC fields, exactly as before RBAC-5C.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from app.chunking.models import ChunkMetadata, DocumentChunk
from app.embeddings.models import EmbeddedChunk, EmbeddingMetadata, EmbeddingVector
from app.enums.document import DocumentAccessScope
from app.search.dense.mapper import DenseMapper
from app.search.hybrid.mapper import HybridMapper
from app.services.ingestion import IngestionService


def _embedded(metadata: ChunkMetadata) -> EmbeddedChunk:
    return EmbeddedChunk(
        DocumentChunk("chunk text", 0, metadata),
        EmbeddingVector([0.1, 0.2]),
        EmbeddingMetadata("test-model", 2),
    )


def _document(
    *,
    id: int = 1,
    user_id: int = 7,
    organisation_id: int = 3,
    team_id: int | None = None,
    access_scope: DocumentAccessScope = DocumentAccessScope.INDIVIDUAL,
):
    return SimpleNamespace(
        id=id,
        user_id=user_id,
        organisation_id=organisation_id,
        team_id=team_id,
        access_scope=access_scope,
        filename=f"document-{id}.pdf",
        stored_filename=f"stored-{id}.pdf",
    )


# --------------------------------------------------------------------------- #
# Metadata stamping (IngestionService)
# --------------------------------------------------------------------------- #


def test_ingestion_stamps_rbac_fields_from_the_loaded_document(monkeypatch):
    document = _document(
        id=101,
        user_id=7,
        organisation_id=3,
        team_id=55,
        access_scope=DocumentAccessScope.TEAM,
    )

    document_repository = MagicMock()
    document_repository.get_by_id.return_value = document

    storage_service = MagicMock()
    storage_service.get_file_path.return_value = "irrelevant/path.pdf"

    metadata_a = ChunkMetadata()
    metadata_b = ChunkMetadata()
    chunks = [
        DocumentChunk("first chunk", 0, metadata_a),
        DocumentChunk("second chunk", 1, metadata_b),
    ]

    service = IngestionService(
        document_repository=document_repository,
        storage_service=storage_service,
        hybrid_pipeline=MagicMock(),
    )
    service.chunking_pipeline = MagicMock()
    service.chunking_pipeline.run.return_value = chunks

    processor = MagicMock()
    processor.extract.return_value = SimpleNamespace(
        blocks=[],
        metadata=SimpleNamespace(file_name=None),
    )
    monkeypatch.setattr(
        "app.services.ingestion.ProcessorFactory.get_processor",
        lambda path: processor,
    )

    service.ingest_document(document_id=101)

    # get_by_id is called exactly once -- no per-chunk re-query.
    document_repository.get_by_id.assert_called_once_with(101)

    for metadata in (metadata_a, metadata_b):
        assert metadata.user_id == 7
        assert metadata.document_id == 101
        assert metadata.organisation_id == 3
        assert metadata.team_id == 55
        assert metadata.access_scope == DocumentAccessScope.TEAM


def test_document_id_is_the_real_sql_id_not_content_derived(monkeypatch):
    """document_id must come from Document.id, never from document_uuid,
    checksum, or filename -- those remain independent, unrelated fields."""

    document = _document(id=999)

    document_repository = MagicMock()
    document_repository.get_by_id.return_value = document
    storage_service = MagicMock()

    metadata = ChunkMetadata(
        document_uuid=uuid4(),
        checksum="deadbeef",
        document_name="some-file.pdf",
    )
    chunks = [DocumentChunk("text", 0, metadata)]

    service = IngestionService(
        document_repository=document_repository,
        storage_service=storage_service,
        hybrid_pipeline=MagicMock(),
    )
    service.chunking_pipeline = MagicMock()
    service.chunking_pipeline.run.return_value = chunks

    processor = MagicMock()
    processor.extract.return_value = SimpleNamespace(
        blocks=[], metadata=SimpleNamespace(file_name=None),
    )
    monkeypatch.setattr(
        "app.services.ingestion.ProcessorFactory.get_processor",
        lambda path: processor,
    )

    service.ingest_document(document_id=999)

    assert metadata.document_id == 999
    # document_id is independent of the content-derived identity fields --
    # changing checksum/document_uuid must never change document_id.
    assert metadata.document_id != metadata.checksum
    assert str(metadata.document_id) != str(metadata.document_uuid)


# --------------------------------------------------------------------------- #
# Payload construction (HybridMapper)
# --------------------------------------------------------------------------- #


def _rbac_metadata(**overrides) -> ChunkMetadata:
    base = dict(
        document_id=42,
        document_uuid=uuid4(),
        document_name="report.pdf",
        chunk_uuid=uuid4(),
        user_id=7,
        organisation_id=3,
        team_id=None,
        access_scope=DocumentAccessScope.INDIVIDUAL,
        checksum="abc123",
    )
    base.update(overrides)
    return ChunkMetadata(**base)


def test_new_payload_has_schema_version_3():
    payload = HybridMapper.build_payload(_embedded(_rbac_metadata()))
    assert payload["schema_version"] == 3


def test_new_payload_contains_all_rbac_fields():
    metadata = _rbac_metadata(
        organisation_id=3, team_id=55, access_scope=DocumentAccessScope.TEAM,
    )
    payload = HybridMapper.build_payload(_embedded(metadata))

    assert payload["document_id"] == 42
    assert payload["organisation_id"] == 3
    assert payload["team_id"] == 55
    assert payload["access_scope"] == "team"
    assert payload["user_id"] == 7


def test_new_payload_access_scope_is_serialized_as_string_value():
    for scope in DocumentAccessScope:
        metadata = _rbac_metadata(access_scope=scope)
        payload = HybridMapper.build_payload(_embedded(metadata))
        assert payload["access_scope"] == scope.value


def test_new_payload_team_id_none_when_not_team_scoped():
    metadata = _rbac_metadata(team_id=None, access_scope=DocumentAccessScope.INDIVIDUAL)
    payload = HybridMapper.build_payload(_embedded(metadata))
    assert payload["team_id"] is None


def test_existing_payload_fields_still_present_and_unchanged():
    metadata = _rbac_metadata(
        document_name="report.pdf",
        section_title="Results",
    )
    payload = HybridMapper.build_payload(_embedded(metadata))

    # Spot-check a representative sample of pre-existing fields, none of
    # which RBAC-5C should have touched.
    assert payload["document_name"] == "report.pdf"
    assert payload["section_title"] == "Results"
    assert payload["is_reference"] is False
    assert payload["is_appendix"] is False
    assert "checksum" in payload
    assert "chunk_uuid" in payload


# --------------------------------------------------------------------------- #
# DenseMapper (dense-only path) must remain untouched
# --------------------------------------------------------------------------- #


def test_dense_mapper_is_unaffected_by_rbac_5c():
    """DenseMapper is not part of the production indexing path (only
    HybridPipeline.index -> HybridMapper is). Confirms it still writes the
    pre-RBAC-5C shape: schema_version=2, no RBAC fields."""

    metadata = _rbac_metadata(
        organisation_id=3, team_id=55, access_scope=DocumentAccessScope.TEAM,
    )
    point = DenseMapper.to_point(_embedded(metadata))

    assert point.payload["schema_version"] == 2
    assert "organisation_id" not in point.payload
    assert "team_id" not in point.payload
    assert "access_scope" not in point.payload
    assert "document_id" not in point.payload
