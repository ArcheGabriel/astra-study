"""
Executable specification for RBAC-5F: scripts/reingest_document.py must
source all five RBAC fields (document_id, user_id, organisation_id,
team_id, access_scope) from the authoritative SQLite Document row before
indexing -- never leaving any of them None for a real re-ingest, and
never independently accepting them as CLI input.

Covers, with no live Qdrant connection, no live Docling/OpenAI, and (for
the full-script tests) an isolated in-memory SQLite database (never the
real dev astra_study.db):

- ``_stamp_rbac_fields`` copies all five fields exactly from the loaded
  Document row, including a legitimately-None ``team_id`` for
  INDIVIDUAL/ORGANISATION documents (never coerced/defaulted);
- the real, unmodified ``HybridMapper.build_payload`` produces a correct
  schema_version=3 payload from chunks stamped this way;
- ``main()`` refuses to index (and never even imports/constructs
  ``HybridPipeline``) when ``--document-id`` does not resolve to a row;
- the dry-run path (no ``--commit``) never touches Qdrant either;
- the script never writes to the ``documents`` table -- confirmed via
  the test session's own dirty/new/deleted tracking after a full run.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.chunking.models import ChunkMetadata, DocumentChunk
from app.database.base import Base
from app.embeddings.models import EmbeddedChunk, EmbeddingMetadata, EmbeddingVector
from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole
from app.search.hybrid.mapper import HybridMapper

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.document import Document
from app.models.organisation import Organisation
from app.models.user import User

import scripts.reingest_document as reingest_module
from scripts.reingest_document import _stamp_rbac_fields, main as reingest_main


# --------------------------------------------------------------------------- #
# Fixtures / factories
# --------------------------------------------------------------------------- #


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    try:
        yield session
    finally:
        session.close()


def make_organisation(db, *, slug: str = "acme") -> Organisation:
    organisation = Organisation(name=slug.title(), slug=slug)
    db.add(organisation)
    db.commit()
    db.refresh(organisation)
    return organisation


def make_user(db, organisation: Organisation, *, username: str = "alice",
              role: OrgRole = OrgRole.MEMBER) -> User:
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password="hashed",
        organisation_id=organisation.id,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_document(
    db,
    *,
    owner: User,
    organisation: Organisation,
    access_scope: DocumentAccessScope = DocumentAccessScope.INDIVIDUAL,
    team_id: int | None = None,
    stored_filename: str = "stored-report.pdf",
) -> Document:
    document = Document(
        user_id=owner.id,
        organisation_id=organisation.id,
        team_id=team_id,
        access_scope=access_scope,
        filename="report.pdf",
        stored_filename=stored_filename,
        content_type="application/pdf",
        file_size=1024,
        status=DocumentStatus.INDEXED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def make_document_like(
    *, id: int = 101, user_id: int = 7, organisation_id: int = 3,
    team_id: int | None = None,
    access_scope: DocumentAccessScope = DocumentAccessScope.INDIVIDUAL,
) -> SimpleNamespace:
    """A Document-like stand-in for the unit-level stamping/payload
    tests (A-C), which need no database at all -- same technique
    tests/unit/test_rbac_5c_payload.py already uses for IngestionService."""

    return SimpleNamespace(
        id=id, user_id=user_id, organisation_id=organisation_id,
        team_id=team_id, access_scope=access_scope,
    )


def _embedded(metadata: ChunkMetadata) -> EmbeddedChunk:
    return EmbeddedChunk(
        DocumentChunk("chunk text", 0, metadata),
        EmbeddingVector([0.1, 0.2]),
        EmbeddingMetadata("test-model", 2),
    )


class _NonClosingSession:
    """main() calls SessionLocal() and closes it internally -- point it
    at the isolated test session, wrapped so .close() doesn't tear down
    the fixture's own session (same trick as
    tests/unit/test_rbac_5d_document_authorization.py's grant_admin
    tests)."""

    def __init__(self, db):
        self._db = db

    def __getattr__(self, name):
        return getattr(self._db, name)

    def close(self):
        pass


def _patched_session_local(monkeypatch, db) -> None:
    monkeypatch.setattr(reingest_module, "SessionLocal", lambda: _NonClosingSession(db))


class _FakeProcessor:
    def __init__(self, blocks):
        self._blocks = blocks

    def extract(self, path):
        return SimpleNamespace(blocks=self._blocks, metadata=SimpleNamespace(file_name=None))


class _FakeChunkPipeline:
    """Stand-in for the real (frozen) ChunkPipeline -- these tests exercise
    RBAC-field sourcing, not chunking behaviour itself."""

    def __init__(self, chunks):
        self._chunks = chunks

    def run(self, extraction):
        return self._chunks


def _one_chunk() -> list[DocumentChunk]:
    return [DocumentChunk("some extracted text", 0, ChunkMetadata())]


def _patch_extraction_and_chunking(monkeypatch, *, chunks):
    monkeypatch.setattr(
        reingest_module.ProcessorFactory, "get_processor",
        staticmethod(lambda path: _FakeProcessor(blocks=[SimpleNamespace()])),
    )
    monkeypatch.setattr(
        reingest_module, "ChunkPipeline", lambda: _FakeChunkPipeline(chunks),
    )


def _patch_storage(monkeypatch, tmp_path, *, stored_filename: str):
    file_path = tmp_path / stored_filename
    file_path.write_bytes(b"%PDF-1.4 minimal fake pdf content")

    class _FakeStorage:
        def get_file_path(self, name):
            return file_path

    monkeypatch.setattr(reingest_module, "LocalStorageService", _FakeStorage)
    return file_path


# --------------------------------------------------------------------------- #
# A. RBAC metadata stamping
# --------------------------------------------------------------------------- #


def test_stamp_rbac_fields_copies_all_five_fields_exactly():
    document = make_document_like(
        id=101, user_id=7, organisation_id=3, team_id=55,
        access_scope=DocumentAccessScope.TEAM,
    )
    metadata_a = ChunkMetadata()
    metadata_b = ChunkMetadata()
    chunks = [
        DocumentChunk("first chunk", 0, metadata_a),
        DocumentChunk("second chunk", 1, metadata_b),
    ]

    _stamp_rbac_fields(chunks, document)

    for metadata in (metadata_a, metadata_b):
        assert metadata.document_id == 101
        assert metadata.user_id == 7
        assert metadata.organisation_id == 3
        assert metadata.team_id == 55
        assert metadata.access_scope == DocumentAccessScope.TEAM


# --------------------------------------------------------------------------- #
# B. Nullable team_id
# --------------------------------------------------------------------------- #


def test_stamp_rbac_fields_preserves_none_team_id_for_individual_document():
    document = make_document_like(
        team_id=None, access_scope=DocumentAccessScope.INDIVIDUAL,
    )
    metadata = ChunkMetadata()
    chunks = [DocumentChunk("chunk text", 0, metadata)]

    _stamp_rbac_fields(chunks, document)

    assert metadata.team_id is None
    assert metadata.access_scope == DocumentAccessScope.INDIVIDUAL


def test_stamp_rbac_fields_preserves_none_team_id_for_organisation_document():
    document = make_document_like(
        team_id=None, access_scope=DocumentAccessScope.ORGANISATION,
    )
    metadata = ChunkMetadata()
    chunks = [DocumentChunk("chunk text", 0, metadata)]

    _stamp_rbac_fields(chunks, document)

    assert metadata.team_id is None
    assert metadata.access_scope == DocumentAccessScope.ORGANISATION


# --------------------------------------------------------------------------- #
# C. Payload correctness (real, unmodified HybridMapper.build_payload)
# --------------------------------------------------------------------------- #


def test_stamped_chunk_produces_correct_v3_payload_for_team_document():
    document = make_document_like(
        id=42, user_id=9, organisation_id=5, team_id=17,
        access_scope=DocumentAccessScope.TEAM,
    )
    metadata = ChunkMetadata()
    chunks = [DocumentChunk("chunk text", 0, metadata)]

    _stamp_rbac_fields(chunks, document)

    payload = HybridMapper.build_payload(_embedded(metadata))

    assert payload["schema_version"] == 3
    assert payload["document_id"] == 42
    assert payload["organisation_id"] == 5
    assert payload["team_id"] == 17
    assert payload["access_scope"] == "team"
    assert payload["user_id"] == 9


def test_stamped_chunk_produces_correct_v3_payload_for_individual_document_with_null_team():
    document = make_document_like(
        id=200, user_id=3, organisation_id=1, team_id=None,
        access_scope=DocumentAccessScope.INDIVIDUAL,
    )
    metadata = ChunkMetadata()
    chunks = [DocumentChunk("chunk text", 0, metadata)]

    _stamp_rbac_fields(chunks, document)

    payload = HybridMapper.build_payload(_embedded(metadata))

    assert payload["schema_version"] == 3
    assert payload["document_id"] == 200
    assert payload["organisation_id"] == 1
    assert payload["team_id"] is None
    assert payload["access_scope"] == "individual"
    assert payload["user_id"] == 3


# --------------------------------------------------------------------------- #
# D. Missing document
# --------------------------------------------------------------------------- #


def test_missing_document_refuses_to_index(db, monkeypatch, tmp_path):
    _patched_session_local(monkeypatch, db)

    fake_hybrid_pipeline_class = MagicMock()
    monkeypatch.setattr(
        "app.search.hybrid.pipeline.HybridPipeline", fake_hybrid_pipeline_class,
    )

    # If the missing-document check didn't short-circuit, these would be
    # hit next -- fail loudly rather than silently proceeding.
    def _unexpected_processor(path):
        raise AssertionError("ProcessorFactory.get_processor must not be called")

    monkeypatch.setattr(
        reingest_module.ProcessorFactory, "get_processor",
        staticmethod(_unexpected_processor),
    )

    exit_code = reingest_main([
        "--document-id", "999999",
        "--commit", "--yes-write-to-qdrant",
    ])

    assert exit_code != 0
    fake_hybrid_pipeline_class.assert_not_called()


# --------------------------------------------------------------------------- #
# E. Dry-run behaviour
# --------------------------------------------------------------------------- #


def test_dry_run_does_not_invoke_qdrant_indexing(db, monkeypatch, tmp_path):
    org = make_organisation(db)
    user = make_user(db, org)
    document = make_document(db, owner=user, organisation=org, stored_filename="doc.pdf")

    _patched_session_local(monkeypatch, db)
    _patch_extraction_and_chunking(monkeypatch, chunks=_one_chunk())
    _patch_storage(monkeypatch, tmp_path, stored_filename="doc.pdf")

    fake_hybrid_pipeline_class = MagicMock()
    monkeypatch.setattr(
        "app.search.hybrid.pipeline.HybridPipeline", fake_hybrid_pipeline_class,
    )

    exit_code = reingest_main(["--document-id", str(document.id)])  # no --commit

    assert exit_code == 0
    fake_hybrid_pipeline_class.assert_not_called()


def test_commit_without_yes_write_flag_does_not_invoke_qdrant_indexing(db, monkeypatch, tmp_path):
    org = make_organisation(db)
    user = make_user(db, org)
    document = make_document(db, owner=user, organisation=org, stored_filename="doc.pdf")

    _patched_session_local(monkeypatch, db)
    _patch_extraction_and_chunking(monkeypatch, chunks=_one_chunk())
    _patch_storage(monkeypatch, tmp_path, stored_filename="doc.pdf")

    fake_hybrid_pipeline_class = MagicMock()
    monkeypatch.setattr(
        "app.search.hybrid.pipeline.HybridPipeline", fake_hybrid_pipeline_class,
    )

    exit_code = reingest_main(["--document-id", str(document.id), "--commit"])

    assert exit_code != 0
    fake_hybrid_pipeline_class.assert_not_called()


# --------------------------------------------------------------------------- #
# F. SQL is read-only
# --------------------------------------------------------------------------- #


def test_script_never_writes_to_the_documents_table(db, monkeypatch, tmp_path):
    org = make_organisation(db)
    user = make_user(db, org)
    document = make_document(
        db, owner=user, organisation=org,
        access_scope=DocumentAccessScope.TEAM, team_id=None,  # deliberately mismatched-looking; only id is used for lookup
        stored_filename="doc.pdf",
    )

    _patched_session_local(monkeypatch, db)
    _patch_extraction_and_chunking(monkeypatch, chunks=_one_chunk())
    _patch_storage(monkeypatch, tmp_path, stored_filename="doc.pdf")

    fake_hybrid_pipeline_instance = MagicMock()
    fake_hybrid_pipeline_class = MagicMock(return_value=fake_hybrid_pipeline_instance)
    monkeypatch.setattr(
        "app.search.hybrid.pipeline.HybridPipeline", fake_hybrid_pipeline_class,
    )

    exit_code = reingest_main([
        "--document-id", str(document.id),
        "--commit", "--yes-write-to-qdrant",
    ])

    assert exit_code == 0
    fake_hybrid_pipeline_instance.index.assert_called_once()

    # The script's own SessionLocal() calls were transparently routed to
    # this exact `db` session (via _NonClosingSession) -- no add/update/
    # delete was ever staged against it.
    assert not db.dirty
    assert not db.new
    assert not db.deleted

    # And the row itself is unchanged when re-read.
    reloaded = db.get(Document, document.id)
    assert reloaded.access_scope == DocumentAccessScope.TEAM
    assert reloaded.team_id is None
    assert reloaded.stored_filename == "doc.pdf"
