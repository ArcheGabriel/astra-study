"""
Executable specification for the semantic-retrieval-cache invalidation
hooks (RBAC/C.3) wired into document upload/ingestion and deletion.

Mirrors the existing ``IngestionService``/``DocumentService`` unit-test
construction patterns (``tests/unit/test_rbac_5c_payload.py``,
``tests/unit/test_rbac_5d_document_authorization.py``) rather than
inventing a new one.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.chunking.models import ChunkMetadata, DocumentChunk
from app.database.base import Base
from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.document import Document
from app.models.organisation import Organisation
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.retrieval.access import AccessContext
from app.services.document import DocumentService
from app.services.ingestion import IngestionService


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


def make_user(db, organisation: Organisation, *, username: str = "alice") -> User:
    user = User(
        username=username, email=f"{username}@example.com", hashed_password="hashed",
        organisation_id=organisation.id, role=OrgRole.MEMBER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_document(db, *, owner: User, organisation: Organisation) -> Document:
    document = Document(
        user_id=owner.id, organisation_id=organisation.id, team_id=None,
        access_scope=DocumentAccessScope.INDIVIDUAL, filename="doc.pdf",
        stored_filename=f"stored-{uuid4()}.pdf", content_type="application/pdf",
        file_size=1024, status=DocumentStatus.INDEXED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def build_access(db, user: User) -> AccessContext:
    team_ids = TeamMembershipRepository(db).get_team_ids_by_user_id(user.id)
    return AccessContext(
        user_id=user.id, organisation_id=user.organisation_id,
        team_ids=tuple(team_ids), jurisdiction_team_ids=(), role=user.role,
    )


# --------------------------------------------------------------------------- #
# 20. upload/ingestion invalidates affected cache entries (organisation-scoped)
# --------------------------------------------------------------------------- #


def test_successful_ingestion_invalidates_the_documents_organisation(monkeypatch):
    document = SimpleNamespace(
        id=101, user_id=7, organisation_id=3, team_id=None,
        access_scope=DocumentAccessScope.INDIVIDUAL,
        filename="doc.pdf", stored_filename="stored.pdf",
    )

    document_repository = MagicMock()
    document_repository.get_by_id.return_value = document

    storage_service = MagicMock()
    storage_service.get_file_path.return_value = "irrelevant/path.pdf"

    cache = MagicMock()

    service = IngestionService(
        document_repository=document_repository,
        storage_service=storage_service,
        hybrid_pipeline=MagicMock(),
        semantic_cache=cache,
    )
    service.chunking_pipeline = MagicMock()
    service.chunking_pipeline.run.return_value = [
        DocumentChunk("chunk text", 0, ChunkMetadata()),
    ]

    processor = MagicMock()
    processor.extract.return_value = SimpleNamespace(
        blocks=[], metadata=SimpleNamespace(file_name=None),
    )
    monkeypatch.setattr(
        "app.services.ingestion.ProcessorFactory.get_processor",
        lambda path: processor,
    )

    service.ingest_document(document_id=101)

    cache.invalidate_organisation.assert_called_once_with(3)


def test_ingestion_without_a_cache_does_not_raise(monkeypatch):
    document = SimpleNamespace(
        id=101, user_id=7, organisation_id=3, team_id=None,
        access_scope=DocumentAccessScope.INDIVIDUAL,
        filename="doc.pdf", stored_filename="stored.pdf",
    )

    document_repository = MagicMock()
    document_repository.get_by_id.return_value = document

    storage_service = MagicMock()
    storage_service.get_file_path.return_value = "irrelevant/path.pdf"

    service = IngestionService(
        document_repository=document_repository,
        storage_service=storage_service,
        hybrid_pipeline=MagicMock(),
    )
    service.chunking_pipeline = MagicMock()
    service.chunking_pipeline.run.return_value = [
        DocumentChunk("chunk text", 0, ChunkMetadata()),
    ]

    processor = MagicMock()
    processor.extract.return_value = SimpleNamespace(
        blocks=[], metadata=SimpleNamespace(file_name=None),
    )
    monkeypatch.setattr(
        "app.services.ingestion.ProcessorFactory.get_processor",
        lambda path: processor,
    )

    service.ingest_document(document_id=101)

    document_repository.update_status.assert_any_call(
        document_id=101, status=DocumentStatus.INDEXED,
    )


# --------------------------------------------------------------------------- #
# 21. deletion invalidates affected cache entries (organisation-scoped)
# --------------------------------------------------------------------------- #


def test_delete_document_invalidates_its_organisation_before_and_after(db):
    """
    C.3 audit finding: a single post-delete-only invalidation leaves a
    real (not microsecond-only) staleness window spanning Qdrant/file/SQL
    I/O in which a concurrent retrieval could serve a pre-existing cached
    result that still includes the about-to-be-deleted document. Delete
    must therefore invalidate the organisation's cache both BEFORE any
    destructive operation and AGAIN after the SQL row is gone -- neither
    call is a substitute for the other (see the C.3 audit report).
    """
    org = make_organisation(db)
    owner = make_user(db, org)
    doc = make_document(db, owner=owner, organisation=org)

    events: list[str] = []

    cache = MagicMock()
    cache.invalidate_organisation.side_effect = lambda organisation_id: events.append(
        "invalidate",
    )

    dense_repository = MagicMock()
    dense_repository.delete_by_document_id.side_effect = lambda document_id: events.append(
        "qdrant_delete",
    )

    service = DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=MagicMock(delete_file=AsyncMock()),
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=dense_repository,
        team_repository=MagicMock(),
        semantic_cache=cache,
    )

    asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, owner)))

    # Invalidated exactly twice, both times for the correct organisation.
    assert cache.invalidate_organisation.call_count == 2
    assert cache.invalidate_organisation.call_args_list == [
        call(org.id), call(org.id),
    ]

    # Ordering: invalidate (before) -> Qdrant delete -> invalidate (after).
    assert events == ["invalidate", "qdrant_delete", "invalidate"]


def test_delete_document_without_a_cache_does_not_raise(db):
    org = make_organisation(db)
    owner = make_user(db, org)
    doc = make_document(db, owner=owner, organisation=org)

    service = DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=MagicMock(delete_file=AsyncMock()),
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=MagicMock(),
        team_repository=MagicMock(),
    )

    # Must not raise even with no semantic_cache injected.
    asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, owner)))
