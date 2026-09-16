"""
Executable specification for RBAC-5E: CREATE-time authorization for
document upload (INDIVIDUAL / TEAM / ORGANISATION), and a downstream
regression proving the already-existing ingestion/Qdrant-payload path
(RBAC-5C) requires no change to support a newly-created TEAM/ORGANISATION
document.

Covers, with no live Qdrant connection, no live filesystem, and an
isolated in-memory SQLite database (never the real dev ``astra_study.db``):

- ``DocumentService.upload_documents`` / ``_can_create`` authorize scope
  selection against the trusted ``AccessContext`` -- never against a
  client-supplied ``organisation_id``, which does not exist as a
  parameter anywhere in this path;
- INDIVIDUAL creation is unconditional for any authenticated user, and is
  exactly what an omitted ``access_scope`` produces (backward
  compatibility for every existing files-only client);
- TEAM creation is a *membership* check, not a role check -- MEMBER,
  MANAGER, and ADMIN all qualify, provided they actually belong to the
  requested team, that team exists, and that team belongs to the
  requester's own organisation (nonexistent and cross-organisation teams
  are deliberately indistinguishable -- both raise ``TeamNotFoundError``
  -- so a requester can never enumerate another organisation's teams);
- ORGANISATION creation requires ``OrgRole.ADMIN`` -- MEMBER and MANAGER
  are both rejected, mirroring the identical precedent already proven in
  ``tests/unit/test_rbac_5c_authorization_filter.py`` for the retrieval
  filter's ORGANISATION branch;
- invalid scope/team_id combinations (INDIVIDUAL+team_id,
  ORGANISATION+team_id, TEAM with no team_id, an unrecognised scope
  string) are rejected before any ``Document`` row is constructed;
- a document created via this path still flows correctly through
  ``IngestionService.ingest_document`` and ``HybridMapper.build_payload``
  with no change to either -- the mechanism RBAC-5C already built and
  tested generically, exercised here end-to-end from a real creation call
  instead of a hand-built ``Document``-like object.
"""

from __future__ import annotations

import asyncio
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import UploadFile
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from starlette.datastructures import Headers

from app.chunking.models import ChunkMetadata, DocumentChunk
from app.database.base import Base
from app.embeddings.models import EmbeddedChunk, EmbeddingMetadata, EmbeddingVector
from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.exceptions.document import (
    InvalidAccessScopeError,
    OrganisationScopeForbiddenError,
    TeamMembershipRequiredError,
    TeamNotFoundError,
)
from app.retrieval.access import AccessContext
from app.search.hybrid.mapper import HybridMapper
from app.services.ingestion import IngestionService
from app.storage.base import BaseStorageService

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.document import Document
from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.repositories.team import TeamRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.services.document import DocumentService


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


def make_organisation(db, *, slug: str) -> Organisation:
    organisation = Organisation(name=slug.title(), slug=slug)
    db.add(organisation)
    db.commit()
    db.refresh(organisation)
    return organisation


def make_user(
    db, organisation: Organisation, *, username: str, role: OrgRole = OrgRole.MEMBER,
) -> User:
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


def make_team(db, organisation: Organisation, *, name: str) -> Team:
    team = Team(organisation_id=organisation.id, name=name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def make_membership(db, *, user: User, team: Team, role: TeamRole = TeamRole.MEMBER) -> TeamMembership:
    membership = TeamMembership(user_id=user.id, team_id=team.id, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def build_access(db, user: User) -> AccessContext:
    """Mirrors get_access_context's real logic (RBAC-5A, unchanged) --
    a genuine team-membership lookup, not a fabricated team_ids tuple."""

    team_ids = TeamMembershipRepository(db).get_team_ids_by_user_id(user.id)
    return AccessContext(
        user_id=user.id,
        organisation_id=user.organisation_id,
        team_ids=tuple(team_ids),
        role=user.role,
    )


class FakeStorageService(BaseStorageService):
    """In-memory stand-in for LocalStorageService -- no filesystem access,
    so this stays a fast, isolated unit test (same pattern as
    tests/unit/test_rbac_foundation.py)."""

    async def save_file(self, file):
        content = await file.read()
        return (f"stored-{file.filename}-{uuid4()}", len(content))

    async def delete_file(self, stored_filename: str) -> None:
        pass

    def get_file_path(self, stored_filename):
        from pathlib import Path
        return Path(stored_filename)


def make_upload_file(*, filename: str = "report.pdf", content_type: str = "application/pdf") -> UploadFile:
    return UploadFile(
        file=BytesIO(b"%PDF-1.4 minimal fake pdf content"),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


def make_document_service(db) -> DocumentService:
    return DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=FakeStorageService(),
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=MagicMock(),
        team_repository=TeamRepository(db),
    )


def make_document_service_with_storage_spy(db) -> tuple[DocumentService, MagicMock]:
    """Same wiring as make_document_service, but with a mocked
    storage_service (AsyncMock save_file) instead of FakeStorageService --
    FakeStorageService performs real in-memory file handling with no
    call-tracking of its own, so a test asserting "save_file was never
    called" needs a spy here instead."""

    storage_service = MagicMock(save_file=AsyncMock())
    service = DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=storage_service,
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=MagicMock(),
        team_repository=TeamRepository(db),
    )
    return service, storage_service


def _persisted_document_count(db) -> int:
    """Direct SQL count of every Document row in the isolated test
    database -- independent of any visibility/authorization filtering,
    so it proves a rejected creation truly persisted nothing at all."""

    return len(db.execute(select(Document)).scalars().all())


def upload(service: DocumentService, *, access: AccessContext, access_scope=None, team_id=None):
    """Drives the async DocumentService.upload_documents synchronously --
    no pytest-asyncio/anyio plugin is configured for this project (plain
    pytest only), matching every other async-service test in this repo."""

    return asyncio.run(
        service.upload_documents(
            files=[make_upload_file()],
            access=access,
            access_scope=access_scope,
            team_id=team_id,
        )
    )


# --------------------------------------------------------------------------- #
# INDIVIDUAL: 1-7
# --------------------------------------------------------------------------- #


def test_member_can_create_individual_document(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="individual")

    assert len(documents) == 1
    assert documents[0].access_scope == DocumentAccessScope.INDIVIDUAL


def test_manager_can_create_individual_document(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="bob", role=OrgRole.MANAGER)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="individual")

    assert documents[0].access_scope == DocumentAccessScope.INDIVIDUAL


def test_admin_can_create_individual_document(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="carol", role=OrgRole.ADMIN)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="individual")

    assert documents[0].access_scope == DocumentAccessScope.INDIVIDUAL


def test_omitted_access_scope_defaults_to_individual(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="dave")
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user))  # access_scope omitted entirely

    assert documents[0].access_scope == DocumentAccessScope.INDIVIDUAL
    assert documents[0].team_id is None


def test_individual_document_persists_team_id_none(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="erin")
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="individual")

    assert documents[0].team_id is None


def test_individual_organisation_id_comes_from_access_context(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="frank")
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="individual")

    assert documents[0].organisation_id == org.id


def test_client_cannot_influence_organisation_id_for_individual(db):
    """There is no organisation_id parameter anywhere in this path -- the
    persisted value is always access.organisation_id, proven here by
    creating two organisations and confirming each user's document lands
    only in their own, never the other."""

    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    user_a = make_user(db, org_a, username="alice")
    user_b = make_user(db, org_b, username="bob")
    service = make_document_service(db)

    doc_a = upload(service, access=build_access(db, user_a), access_scope="individual")[0]
    doc_b = upload(service, access=build_access(db, user_b), access_scope="individual")[0]

    assert doc_a.organisation_id == org_a.id
    assert doc_b.organisation_id == org_b.id
    assert doc_a.organisation_id != doc_b.organisation_id


# --------------------------------------------------------------------------- #
# TEAM: 8-19
# --------------------------------------------------------------------------- #


def test_team_member_can_create_team_document(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    make_membership(db, user=user, team=team, role=TeamRole.MEMBER)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="team", team_id=team.id)

    assert documents[0].access_scope == DocumentAccessScope.TEAM
    assert documents[0].team_id == team.id


def test_team_manager_org_role_can_create_team_document(db):
    """A user with OrgRole.MANAGER (org-level) -- not to be confused with
    TeamRole.MANAGER -- may create a TEAM document, exactly like a plain
    OrgRole.MEMBER, provided they belong to the team."""

    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="bob", role=OrgRole.MANAGER)
    make_membership(db, user=user, team=team, role=TeamRole.MEMBER)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="team", team_id=team.id)

    assert documents[0].access_scope == DocumentAccessScope.TEAM


def test_org_admin_who_is_team_member_can_create_team_document(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    make_membership(db, user=admin, team=team, role=TeamRole.MEMBER)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, admin), access_scope="team", team_id=team.id)

    assert documents[0].access_scope == DocumentAccessScope.TEAM
    assert documents[0].team_id == team.id


def test_non_member_cannot_create_team_document(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice")  # never joined the team
    service = make_document_service(db)

    with pytest.raises(TeamMembershipRequiredError):
        upload(service, access=build_access(db, user), access_scope="team", team_id=team.id)


def test_admin_who_is_not_team_member_cannot_create_team_document(db):
    """Closes the audit's ADMIN-membership coverage gap: TEAM creation is
    a membership check, never a role check (RBAC-5E's explicit product
    decision) -- so OrgRole.ADMIN must not bypass it. Companion to
    test_org_admin_who_is_team_member_can_create_team_document (the
    positive case, where the same ADMIN *is* a member and succeeds)."""

    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)  # never joined the team
    service, storage_service = make_document_service_with_storage_spy(db)

    with pytest.raises(TeamMembershipRequiredError):
        asyncio.run(
            service.upload_documents(
                files=[make_upload_file()],
                access=build_access(db, admin),
                access_scope="team",
                team_id=team.id,
            )
        )

    storage_service.save_file.assert_not_called()
    assert _persisted_document_count(db) == 0


def test_invalid_team_id_is_rejected(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice")
    service = make_document_service(db)

    with pytest.raises(TeamNotFoundError):
        upload(service, access=build_access(db, user), access_scope="team", team_id=999999)


def test_cross_organisation_team_is_rejected(db):
    org = make_organisation(db, slug="acme")
    other_org = make_organisation(db, slug="globex")
    foreign_team = make_team(db, other_org, name="Research")
    user = make_user(db, org, username="alice")
    service = make_document_service(db)

    with pytest.raises(TeamNotFoundError):
        upload(service, access=build_access(db, user), access_scope="team", team_id=foreign_team.id)


def test_team_without_team_id_is_rejected(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice")
    service = make_document_service(db)

    with pytest.raises(InvalidAccessScopeError):
        upload(service, access=build_access(db, user), access_scope="team", team_id=None)


def test_team_document_persists_correct_organisation_id(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice")
    make_membership(db, user=user, team=team)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="team", team_id=team.id)

    assert documents[0].organisation_id == org.id


def test_team_document_persists_correct_team_id(db):
    org = make_organisation(db, slug="acme")
    team_a = make_team(db, org, name="Research")
    team_b = make_team(db, org, name="Support")
    user = make_user(db, org, username="alice")
    make_membership(db, user=user, team=team_a)
    make_membership(db, user=user, team=team_b)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="team", team_id=team_b.id)

    assert documents[0].team_id == team_b.id
    assert documents[0].team_id != team_a.id


def test_team_document_persists_access_scope_team(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice")
    make_membership(db, user=user, team=team)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="team", team_id=team.id)

    assert documents[0].access_scope == DocumentAccessScope.TEAM


def test_team_role_member_is_explicitly_allowed(db):
    """Varies TeamRole (holding OrgRole.MEMBER constant) -- distinct axis
    from test_team_member_can_create_team_document, which varies OrgRole."""

    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    make_membership(db, user=user, team=team, role=TeamRole.MEMBER)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="team", team_id=team.id)

    assert documents[0].access_scope == DocumentAccessScope.TEAM


def test_team_role_manager_is_explicitly_allowed(db):
    """TeamRole.MANAGER is not required for TEAM creation, but it must not
    be forbidden either -- a team manager is still just a member."""

    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    make_membership(db, user=user, team=team, role=TeamRole.MANAGER)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, user), access_scope="team", team_id=team.id)

    assert documents[0].access_scope == DocumentAccessScope.TEAM


# --------------------------------------------------------------------------- #
# ORGANISATION: 20-24
# --------------------------------------------------------------------------- #


def test_admin_can_create_organisation_document(db):
    org = make_organisation(db, slug="acme")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, admin), access_scope="organisation")

    assert documents[0].access_scope == DocumentAccessScope.ORGANISATION


def test_member_cannot_create_organisation_document(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    service = make_document_service(db)

    with pytest.raises(OrganisationScopeForbiddenError):
        upload(service, access=build_access(db, user), access_scope="organisation")


def test_manager_cannot_create_organisation_document(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="bob", role=OrgRole.MANAGER)
    service = make_document_service(db)

    with pytest.raises(OrganisationScopeForbiddenError):
        upload(service, access=build_access(db, user), access_scope="organisation")


def test_organisation_document_persists_team_id_none(db):
    org = make_organisation(db, slug="acme")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, admin), access_scope="organisation")

    assert documents[0].team_id is None


def test_organisation_id_comes_from_access_context_for_organisation_scope(db):
    org = make_organisation(db, slug="acme")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_document_service(db)

    documents = upload(service, access=build_access(db, admin), access_scope="organisation")

    assert documents[0].organisation_id == org.id


# --------------------------------------------------------------------------- #
# INVALID COMBINATIONS: 25-28
# --------------------------------------------------------------------------- #


def test_individual_with_team_id_is_rejected(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice")
    make_membership(db, user=user, team=team)
    service = make_document_service(db)

    with pytest.raises(InvalidAccessScopeError):
        upload(service, access=build_access(db, user), access_scope="individual", team_id=team.id)


def test_organisation_with_team_id_is_rejected(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    make_membership(db, user=admin, team=team)
    service = make_document_service(db)

    with pytest.raises(InvalidAccessScopeError):
        upload(service, access=build_access(db, admin), access_scope="organisation", team_id=team.id)


def test_invalid_access_scope_value_is_rejected(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice")
    service = make_document_service(db)

    with pytest.raises(InvalidAccessScopeError):
        upload(service, access=build_access(db, user), access_scope="galaxy-wide")


def test_cross_organisation_team_assignment_is_rejected_even_with_own_valid_team(db):
    """A user who legitimately belongs to a team in their own organisation
    still cannot use a foreign org's team_id -- having *a* valid
    membership must never be treated as a bypass for an unrelated,
    unauthorized team_id."""

    org = make_organisation(db, slug="acme")
    other_org = make_organisation(db, slug="globex")
    own_team = make_team(db, org, name="Research")
    foreign_team = make_team(db, other_org, name="Secret Project")
    user = make_user(db, org, username="alice")
    make_membership(db, user=user, team=own_team)
    service = make_document_service(db)

    with pytest.raises(TeamNotFoundError):
        upload(service, access=build_access(db, user), access_scope="team", team_id=foreign_team.id)


# --------------------------------------------------------------------------- #
# ZERO SIDE EFFECTS ON REJECTED CREATION (LOW finding closure)
#
# Authorization must resolve before any destructive/persistent work --
# before storage, before SQL persistence, before background ingestion
# is ever scheduled (ingestion scheduling itself lives in the API route,
# not DocumentService, and is unreachable when upload_documents raises).
# One representative TEAM rejection and one representative ORGANISATION
# rejection are covered here rather than duplicating this assertion
# across every rejection test in this file.
# --------------------------------------------------------------------------- #


def test_team_rejection_persists_nothing_and_never_touches_storage(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice")  # never joined the team
    service, storage_service = make_document_service_with_storage_spy(db)

    with pytest.raises(TeamMembershipRequiredError):
        asyncio.run(
            service.upload_documents(
                files=[make_upload_file()],
                access=build_access(db, user),
                access_scope="team",
                team_id=team.id,
            )
        )

    storage_service.save_file.assert_not_called()
    assert _persisted_document_count(db) == 0


def test_organisation_rejection_persists_nothing_and_never_touches_storage(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    service, storage_service = make_document_service_with_storage_spy(db)

    with pytest.raises(OrganisationScopeForbiddenError):
        asyncio.run(
            service.upload_documents(
                files=[make_upload_file()],
                access=build_access(db, user),
                access_scope="organisation",
            )
        )

    storage_service.save_file.assert_not_called()
    assert _persisted_document_count(db) == 0


# --------------------------------------------------------------------------- #
# BACKWARD COMPATIBILITY: 29-30
# --------------------------------------------------------------------------- #


def test_files_only_upload_creates_individual_document(db):
    """The exact call shape an existing, unmodified client makes: only
    files, no access_scope/team_id keyword arguments passed at all."""

    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice")
    service = make_document_service(db)

    uploaded = asyncio.run(
        service.upload_documents(
            files=[make_upload_file()],
            access=build_access(db, user),
        )
    )

    assert uploaded[0].access_scope == DocumentAccessScope.INDIVIDUAL
    assert uploaded[0].team_id is None


def test_existing_upload_behavior_remains_intact(db):
    org = make_organisation(db, slug="acme")
    other_org = make_organisation(db, slug="globex")
    user = make_user(db, org, username="uploader")
    service = make_document_service(db)

    uploaded = upload(service, access=build_access(db, user))

    assert len(uploaded) == 1
    document = uploaded[0]
    assert document.user_id == user.id
    assert document.organisation_id == user.organisation_id
    assert document.organisation_id != other_org.id
    assert document.status == DocumentStatus.UPLOADED
    assert document.content_type == "application/pdf"
    assert document.file_size > 0


# --------------------------------------------------------------------------- #
# DOWNSTREAM REGRESSION: 31-33
# --------------------------------------------------------------------------- #


def _ingest_and_capture_metadata(db, document_id: int, monkeypatch) -> ChunkMetadata:
    """Runs the real, unmodified IngestionService.ingest_document against
    a document actually created via DocumentService.upload_documents --
    everything downstream of chunking is mocked (Docling/the chunking
    pipeline are frozen and untouched by RBAC-5E), but the RBAC-field
    stamping loop and the document lookup are exercised for real."""

    metadata = ChunkMetadata()
    chunks = [DocumentChunk("chunk text", 0, metadata)]

    service = IngestionService(
        document_repository=DocumentRepository(db),
        storage_service=MagicMock(),
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

    service.ingest_document(document_id=document_id)

    return metadata


def test_team_document_from_upload_receives_correct_metadata_during_ingestion(db, monkeypatch):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice")
    make_membership(db, user=user, team=team)
    service = make_document_service(db)

    document = upload(service, access=build_access(db, user), access_scope="team", team_id=team.id)[0]

    metadata = _ingest_and_capture_metadata(db, document.id, monkeypatch)

    assert metadata.user_id == user.id
    assert metadata.document_id == document.id
    assert metadata.organisation_id == org.id
    assert metadata.team_id == team.id
    assert metadata.access_scope == DocumentAccessScope.TEAM


def test_organisation_document_from_upload_receives_correct_metadata_during_ingestion(db, monkeypatch):
    org = make_organisation(db, slug="acme")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_document_service(db)

    document = upload(service, access=build_access(db, admin), access_scope="organisation")[0]

    metadata = _ingest_and_capture_metadata(db, document.id, monkeypatch)

    assert metadata.user_id == admin.id
    assert metadata.document_id == document.id
    assert metadata.organisation_id == org.id
    assert metadata.team_id is None
    assert metadata.access_scope == DocumentAccessScope.ORGANISATION


def test_team_document_v3_payload_contains_required_rbac_fields(db, monkeypatch):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    user = make_user(db, org, username="alice")
    make_membership(db, user=user, team=team)
    service = make_document_service(db)

    document = upload(service, access=build_access(db, user), access_scope="team", team_id=team.id)[0]
    metadata = _ingest_and_capture_metadata(db, document.id, monkeypatch)

    embedded = EmbeddedChunk(
        DocumentChunk("chunk text", 0, metadata),
        EmbeddingVector([0.1, 0.2]),
        EmbeddingMetadata("test-model", 2),
    )
    payload = HybridMapper.build_payload(embedded)

    assert payload["schema_version"] == 3
    assert payload["document_id"] == document.id
    assert payload["organisation_id"] == org.id
    assert payload["team_id"] == team.id
    assert payload["access_scope"] == "team"
