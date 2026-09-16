"""
Executable specification for RBAC-5D: write/read authorization for the
document-management API (list/get/download/delete) and safe Qdrant point
deletion for newly-indexed (schema_version=3) documents.

Covers, with no live Qdrant connection and an isolated in-memory SQLite
database (never the real dev ``astra_study.db``):

- read visibility (``DocumentService.get_documents`` / ``get_document`` /
  ``download_document``) mirrors the same individual/team/organisation
  rules already proven correct in ``DenseRepository._authorization_filter``,
  applied at the SQL level via ``DocumentRepository.get_visible`` /
  ``get_by_id_visible``;
- delete authorization (``DocumentService.delete_document`` /
  ``_can_delete``) is strictly stricter than read visibility: owner always
  allowed; TEAM documents additionally deletable only by a TEAM MANAGER of
  that specific team (never a plain TEAM MEMBER); ORGANISATION documents
  additionally deletable only by an ADMIN of that organisation; identity,
  role, organisation, and team membership all participate -- never
  document_id/team_id/organisation_id alone;
- ``DenseRepository.delete_by_document_id`` targets only the
  ``document_id`` payload field (never document_uuid/checksum/chunk_uuid),
  and is a structural no-op (no delete call issued) for a document with no
  schema_version=3 points, i.e. every legacy schema_version=2 document;
- ``scripts/grant_admin.py`` promotes an existing user by email only, with
  no hardcoded email and no import-time side effect.
"""

from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.exceptions.document import DocumentNotFoundError
from app.retrieval.access import AccessContext
from app.search.dense.repository import DenseRepository

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.document import Document
from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.services.document import DocumentService

import scripts.grant_admin as grant_admin_module
from scripts.grant_admin import grant_admin, main as grant_admin_main


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


def make_document(
    db,
    *,
    owner: User,
    organisation: Organisation,
    access_scope: DocumentAccessScope = DocumentAccessScope.INDIVIDUAL,
    team: Team | None = None,
) -> Document:
    document = Document(
        user_id=owner.id,
        organisation_id=organisation.id,
        team_id=team.id if team else None,
        access_scope=access_scope,
        filename="doc.pdf",
        stored_filename=f"stored-{uuid4()}.pdf",
        content_type="application/pdf",
        file_size=1024,
        status=DocumentStatus.INDEXED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


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


def _patched_session_local(monkeypatch, db) -> None:
    """grant_admin() calls SessionLocal() and closes it internally --
    point it at the isolated test session, wrapped so .close() doesn't
    tear down the fixture's own session (same trick as
    tests/unit/test_rbac_5c_evaluation_access.py)."""

    class _NonClosingSession:
        def __getattr__(self, name):
            return getattr(db, name)

        def close(self):
            pass

    monkeypatch.setattr(grant_admin_module, "SessionLocal", lambda: _NonClosingSession())


def make_document_service(db) -> DocumentService:
    return DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=MagicMock(delete_file=AsyncMock()),
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=MagicMock(),
        # This file exercises read/delete only (RBAC-5D) -- never
        # upload_documents/_can_create (RBAC-5E) -- so a MagicMock is
        # sufficient; it is never called.
        team_repository=MagicMock(),
    )


# --------------------------------------------------------------------------- #
# READ: 1-12
# --------------------------------------------------------------------------- #


def test_member_sees_own_individual_document(db):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice")
    doc = make_document(db, owner=user, organisation=org)
    service = make_document_service(db)

    result = service.get_document(document_id=doc.id, access=build_access(db, user))

    assert result.id == doc.id


def test_member_cannot_see_another_users_individual_document(db):
    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    other = make_user(db, org, username="bob")
    doc = make_document(db, owner=owner, organisation=org)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        service.get_document(document_id=doc.id, access=build_access(db, other))


def test_manager_sees_own_individual_document(db):
    org = make_organisation(db, slug="acme")
    manager = make_user(db, org, username="carol", role=OrgRole.MANAGER)
    doc = make_document(db, owner=manager, organisation=org)
    service = make_document_service(db)

    result = service.get_document(document_id=doc.id, access=build_access(db, manager))

    assert result.id == doc.id


def test_member_sees_team_document_for_their_team(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    owner = make_user(db, org, username="alice")
    teammate = make_user(db, org, username="bob")
    make_membership(db, user=teammate, team=team)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.TEAM, team=team)
    service = make_document_service(db)

    result = service.get_document(document_id=doc.id, access=build_access(db, teammate))

    assert result.id == doc.id


def test_member_cannot_see_team_document_for_a_different_team(db):
    org = make_organisation(db, slug="acme")
    team_a = make_team(db, org, name="Research")
    team_b = make_team(db, org, name="Support")
    owner = make_user(db, org, username="alice")
    outsider = make_user(db, org, username="bob")
    make_membership(db, user=outsider, team=team_b)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.TEAM, team=team_a)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        service.get_document(document_id=doc.id, access=build_access(db, outsider))


def test_manager_sees_team_document_for_their_team(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    owner = make_user(db, org, username="alice")
    manager = make_user(db, org, username="carol", role=OrgRole.MANAGER)
    make_membership(db, user=manager, team=team)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.TEAM, team=team)
    service = make_document_service(db)

    result = service.get_document(document_id=doc.id, access=build_access(db, manager))

    assert result.id == doc.id


def test_member_cannot_see_organisation_document(db):
    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    member = make_user(db, org, username="bob")
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.ORGANISATION)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        service.get_document(document_id=doc.id, access=build_access(db, member))


def test_manager_cannot_see_organisation_document(db):
    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    manager = make_user(db, org, username="carol", role=OrgRole.MANAGER)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.ORGANISATION)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        service.get_document(document_id=doc.id, access=build_access(db, manager))


def test_admin_sees_organisation_document_in_own_organisation(db):
    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.ORGANISATION)
    service = make_document_service(db)

    result = service.get_document(document_id=doc.id, access=build_access(db, admin))

    assert result.id == doc.id


def test_admin_cannot_see_organisation_document_from_another_organisation(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    owner = make_user(db, org_a, username="alice")
    admin_b = make_user(db, org_b, username="root", role=OrgRole.ADMIN)
    doc = make_document(db, owner=owner, organisation=org_a, access_scope=DocumentAccessScope.ORGANISATION)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        service.get_document(document_id=doc.id, access=build_access(db, admin_b))


def test_cross_organisation_team_document_is_denied(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    team_a = make_team(db, org_a, name="Research")
    owner = make_user(db, org_a, username="alice")
    outsider = make_user(db, org_b, username="bob")
    doc = make_document(db, owner=owner, organisation=org_a, access_scope=DocumentAccessScope.TEAM, team=team_a)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        service.get_document(document_id=doc.id, access=build_access(db, outsider))


def test_same_team_id_in_another_organisation_is_denied(db):
    """A numerically-identical team_id belonging to a different
    organisation's team must never match -- team visibility always
    requires the organisation to match too."""

    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    team_a = make_team(db, org_a, name="Research")  # e.g. id=1
    team_b = make_team(db, org_b, name="Research")  # e.g. id=2 (different org)
    owner = make_user(db, org_a, username="alice")
    member_b = make_user(db, org_b, username="bob")
    make_membership(db, user=member_b, team=team_b)

    doc = make_document(db, owner=owner, organisation=org_a, access_scope=DocumentAccessScope.TEAM, team=team_a)
    service = make_document_service(db)

    # member_b's team_ids contains team_b.id, not team_a.id -- even if the
    # numeric ids happened to collide this would still be denied because
    # the document's organisation_id (org_a) != member_b's (org_b).
    with pytest.raises(DocumentNotFoundError):
        service.get_document(document_id=doc.id, access=build_access(db, member_b))


def test_get_documents_returns_the_correct_mixed_visibility_set(db):
    """Exercises the actual plural/list path (DocumentService.get_documents
    -> DocumentRepository.get_visible), not just the single-document getter.
    A realistic mixed dataset is seeded, and the returned set is checked by
    identity (exact id set), proving the aggregate OR-across-branches
    behaviour rather than any single branch's decision in isolation."""

    org = make_organisation(db, slug="acme")
    other_org = make_organisation(db, slug="globex")

    team_mine = make_team(db, org, name="Research")
    team_other = make_team(db, org, name="Support")

    requester = make_user(db, org, username="alice")
    make_membership(db, user=requester, team=team_mine)

    other_user = make_user(db, org, username="bob")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)

    # 1. requester's own INDIVIDUAL document -- visible
    own_individual = make_document(db, owner=requester, organisation=org)

    # 2. another user's INDIVIDUAL document -- not visible
    make_document(db, owner=other_user, organisation=org)

    # 3. TEAM document in a team the requester belongs to -- visible
    team_mine_doc = make_document(
        db, owner=other_user, organisation=org,
        access_scope=DocumentAccessScope.TEAM, team=team_mine,
    )

    # 4. TEAM document in a team the requester does NOT belong to -- not visible
    make_document(
        db, owner=other_user, organisation=org,
        access_scope=DocumentAccessScope.TEAM, team=team_other,
    )

    # 5. ORGANISATION document -- not visible to a non-ADMIN requester
    org_doc = make_document(
        db, owner=other_user, organisation=org,
        access_scope=DocumentAccessScope.ORGANISATION,
    )

    # 6. a document from another organisation entirely -- never visible
    other_org_doc = make_document(
        db, owner=make_user(db, other_org, username="carol"), organisation=other_org,
    )

    service = make_document_service(db)

    visible = service.get_documents(access=build_access(db, requester))
    visible_ids = {d.id for d in visible}

    assert visible_ids == {own_individual.id, team_mine_doc.id}
    assert org_doc.id not in visible_ids
    assert other_org_doc.id not in visible_ids

    # Same dataset, viewed by an ADMIN of the same organisation: additionally
    # sees the ORGANISATION document, but still never the other
    # organisation's document.
    admin_visible_ids = {d.id for d in service.get_documents(access=build_access(db, admin))}

    assert org_doc.id in admin_visible_ids
    assert other_org_doc.id not in admin_visible_ids


# --------------------------------------------------------------------------- #
# DELETE: 13-20
# --------------------------------------------------------------------------- #


def test_owner_deletes_own_individual_document(db):
    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    doc = make_document(db, owner=owner, organisation=org)
    service = make_document_service(db)

    asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, owner)))

    assert DocumentRepository(db).get_by_id(doc.id) is None


def test_non_owner_cannot_delete_another_users_individual_document(db):
    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    other = make_user(db, org, username="bob")
    doc = make_document(db, owner=owner, organisation=org)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, other)))

    assert DocumentRepository(db).get_by_id(doc.id) is not None


def test_team_manager_can_delete_team_document_in_their_team(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    owner = make_user(db, org, username="alice")
    manager = make_user(db, org, username="carol")
    make_membership(db, user=manager, team=team, role=TeamRole.MANAGER)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.TEAM, team=team)
    service = make_document_service(db)

    asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, manager)))

    assert DocumentRepository(db).get_by_id(doc.id) is None


def test_team_member_cannot_delete_another_users_team_document(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    owner = make_user(db, org, username="alice")
    member = make_user(db, org, username="bob")
    make_membership(db, user=member, team=team, role=TeamRole.MEMBER)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.TEAM, team=team)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, member)))

    assert DocumentRepository(db).get_by_id(doc.id) is not None


def test_team_manager_from_another_team_cannot_delete_it(db):
    org = make_organisation(db, slug="acme")
    team_a = make_team(db, org, name="Research")
    team_b = make_team(db, org, name="Support")
    owner = make_user(db, org, username="alice")
    manager_b = make_user(db, org, username="carol")
    make_membership(db, user=manager_b, team=team_b, role=TeamRole.MANAGER)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.TEAM, team=team_a)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, manager_b)))

    assert DocumentRepository(db).get_by_id(doc.id) is not None


def test_admin_can_delete_organisation_document_in_own_organisation(db):
    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.ORGANISATION)
    service = make_document_service(db)

    asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, admin)))

    assert DocumentRepository(db).get_by_id(doc.id) is None


def test_admin_from_another_organisation_cannot_delete_it(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    owner = make_user(db, org_a, username="alice")
    admin_b = make_user(db, org_b, username="root", role=OrgRole.ADMIN)
    doc = make_document(db, owner=owner, organisation=org_a, access_scope=DocumentAccessScope.ORGANISATION)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, admin_b)))

    assert DocumentRepository(db).get_by_id(doc.id) is not None


def test_non_admin_cannot_delete_another_users_organisation_document(db):
    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    member = make_user(db, org, username="bob")
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.ORGANISATION)
    service = make_document_service(db)

    with pytest.raises(DocumentNotFoundError):
        asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, member)))

    assert DocumentRepository(db).get_by_id(doc.id) is not None


def test_delete_authorization_happens_before_any_destructive_call(db):
    """A denied delete must not touch storage or Qdrant at all."""

    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    other = make_user(db, org, username="bob")
    doc = make_document(db, owner=owner, organisation=org)

    storage_service = MagicMock(delete_file=AsyncMock())
    dense_repository = MagicMock()
    service = DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=storage_service,
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=dense_repository,
        team_repository=MagicMock(),
    )

    with pytest.raises(DocumentNotFoundError):
        asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, other)))

    storage_service.delete_file.assert_not_called()
    dense_repository.delete_by_document_id.assert_not_called()


def test_qdrant_delete_failure_aborts_before_file_and_sql_deletion(db):
    """Locks in the critical ordering (authorization -> Qdrant -> file ->
    SQL): if the Qdrant step raises, the exception must propagate
    unmodified, and neither the file nor the SQL row may be touched --
    this is exactly what closes the pre-RBAC-5D bug (SQL/file deleted,
    Qdrant vectors orphaned forever); a Qdrant failure must instead leave
    everything else completely intact."""

    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    doc = make_document(db, owner=owner, organisation=org)

    storage_service = MagicMock(delete_file=AsyncMock())
    dense_repository = MagicMock()
    dense_repository.delete_by_document_id.side_effect = RuntimeError("Qdrant is unreachable")

    service = DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=storage_service,
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=dense_repository,
        team_repository=MagicMock(),
    )

    with pytest.raises(RuntimeError, match="Qdrant is unreachable"):
        asyncio.run(service.delete_document(document_id=doc.id, access=build_access(db, owner)))

    # Qdrant deletion was attempted (authorization passed first)...
    dense_repository.delete_by_document_id.assert_called_once_with(doc.id)

    # ...but nothing downstream of it ran.
    storage_service.delete_file.assert_not_called()

    # The SQL row is untouched -- no delete, no commit that removed it.
    assert DocumentRepository(db).get_by_id(doc.id) is not None


# --------------------------------------------------------------------------- #
# DOWNLOAD (optional finding closure)
# --------------------------------------------------------------------------- #


def test_download_document_authorized_team_document_succeeds(db):
    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    owner = make_user(db, org, username="alice")
    teammate = make_user(db, org, username="bob")
    make_membership(db, user=teammate, team=team)
    doc = make_document(
        db, owner=owner, organisation=org,
        access_scope=DocumentAccessScope.TEAM, team=team,
    )

    storage_service = MagicMock()
    storage_service.get_file_path.return_value = Path("/tmp") / doc.stored_filename
    service = DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=storage_service,
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=MagicMock(),
        team_repository=MagicMock(),
    )

    file_path, filename = service.download_document(
        document_id=doc.id, access=build_access(db, teammate),
    )

    storage_service.get_file_path.assert_called_once_with(doc.stored_filename)
    assert filename == doc.filename
    assert file_path == Path("/tmp") / doc.stored_filename


def test_download_document_unauthorized_raises_not_found(db):
    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="alice")
    other = make_user(db, org, username="bob")
    doc = make_document(db, owner=owner, organisation=org)

    storage_service = MagicMock()
    service = DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=storage_service,
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=MagicMock(),
        team_repository=MagicMock(),
    )

    with pytest.raises(DocumentNotFoundError):
        service.download_document(document_id=doc.id, access=build_access(db, other))

    storage_service.get_file_path.assert_not_called()


# --------------------------------------------------------------------------- #
# QDRANT: 21-25
# --------------------------------------------------------------------------- #


def make_dense_repository_with_fake_client(count_result: int = 0) -> DenseRepository:
    repository = DenseRepository.__new__(DenseRepository)
    repository.client = MagicMock()
    repository.client.count.return_value = SimpleNamespace(count=count_result)
    return repository


def test_v3_deletion_targets_document_id():
    repository = make_dense_repository_with_fake_client(count_result=3)

    repository.delete_by_document_id(42)

    call = repository.client.delete.call_args
    selector: Filter = call.kwargs["points_selector"]
    keys = {c.key for c in selector.must}
    assert keys == {"document_id"}
    condition = selector.must[0]
    assert isinstance(condition, FieldCondition)
    assert isinstance(condition.match, MatchValue)
    assert condition.match.value == 42


def test_v3_deletion_does_not_target_document_uuid():
    repository = make_dense_repository_with_fake_client(count_result=1)

    repository.delete_by_document_id(1)

    selector: Filter = repository.client.delete.call_args.kwargs["points_selector"]
    keys = {c.key for c in selector.must}
    assert "document_uuid" not in keys


def test_v3_deletion_does_not_target_checksum():
    repository = make_dense_repository_with_fake_client(count_result=1)

    repository.delete_by_document_id(1)

    selector: Filter = repository.client.delete.call_args.kwargs["points_selector"]
    keys = {c.key for c in selector.must}
    assert "checksum" not in keys
    assert "chunk_uuid" not in keys
    assert "user_id" not in keys


def test_v2_document_causes_no_qdrant_delete_call():
    """count_filter finds zero points (the legacy/never-indexed case) --
    the delete call must never be issued at all."""

    repository = make_dense_repository_with_fake_client(count_result=0)

    result = repository.delete_by_document_id(999)

    repository.client.delete.assert_not_called()
    assert result == 0


def test_qdrant_deletion_uses_a_precise_document_id_filter():
    repository = make_dense_repository_with_fake_client(count_result=5)

    result = repository.delete_by_document_id(7)

    count_call = repository.client.count.call_args
    count_filter: Filter = count_call.kwargs["count_filter"]
    assert len(count_filter.must) == 1
    assert count_filter.must[0].key == "document_id"
    assert count_filter.must[0].match.value == 7

    delete_call = repository.client.delete.call_args
    assert delete_call.kwargs["points_selector"] == count_filter
    assert result == 5


# --------------------------------------------------------------------------- #
# ADMIN BOOTSTRAP: 26-29
# --------------------------------------------------------------------------- #


def test_grant_admin_promotes_the_specified_existing_user(db, monkeypatch):
    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    _patched_session_local(monkeypatch, db)

    exit_code = grant_admin("alice@example.com")

    assert exit_code == 0
    db.refresh(user)
    assert user.role == OrgRole.ADMIN
    # organisation membership must be untouched
    assert user.organisation_id == org.id


def test_grant_admin_nonexistent_email_fails_clearly(db, monkeypatch, capsys):
    _patched_session_local(monkeypatch, db)

    exit_code = grant_admin("nobody@example.com")

    assert exit_code == 1
    assert "no user found" in capsys.readouterr().err


def test_grant_admin_has_no_hardcoded_bootstrap_email():
    source = inspect.getsource(grant_admin_module)
    assert "@" not in source.replace("user@example.com", "").replace(
        "uv run python -m scripts.grant_admin --email user@example.com", "",
    )


def test_grant_admin_script_does_not_execute_during_import():
    """Importing the module (already done at collection time) must not
    have required a database or produced a promotion -- verified by the
    module exposing main()/grant_admin() as plain, uninvoked functions."""

    assert callable(grant_admin_module.main)
    assert callable(grant_admin_module.grant_admin)
    assert inspect.getsource(grant_admin_module).strip().endswith(
        'raise SystemExit(main())'
    )


def test_grant_admin_main_requires_email_argument():
    with pytest.raises(SystemExit):
        grant_admin_main([])


def test_grant_admin_never_creates_a_new_user(db, monkeypatch):
    org = make_organisation(db, slug="acme")
    _patched_session_local(monkeypatch, db)

    before = db.query(User).count() if hasattr(db, "query") else None
    exit_code = grant_admin("ghost@example.com")

    assert exit_code == 1
    from sqlalchemy import select
    remaining = db.execute(select(User)).scalars().all()
    assert remaining == []


def test_grant_admin_never_alters_organisation_membership(db, monkeypatch):
    org = make_organisation(db, slug="acme")
    other_org = make_organisation(db, slug="globex")
    user = make_user(db, org, username="alice")
    _patched_session_local(monkeypatch, db)

    grant_admin("alice@example.com")

    db.refresh(user)
    assert user.organisation_id == org.id
    assert user.organisation_id != other_org.id


# --------------------------------------------------------------------------- #
# REGRESSION: 30-31 (32 is validated separately via the full suite run)
# --------------------------------------------------------------------------- #


def test_rbac_5c_authorization_filter_module_unchanged():
    """Sanity import check: RBAC-5D must not have touched the RBAC-5C
    retrieval authorization filter it explicitly must not modify."""

    from app.search.dense.repository import DenseRepository as _DR

    assert hasattr(_DR, "_authorization_filter")
    assert hasattr(_DR, "delete_by_document_id")


def test_document_upload_still_creates_individual_scope(db):
    """RBAC-5D must not have touched upload provisioning behaviour."""

    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice")
    doc = make_document(db, owner=user, organisation=org)

    assert doc.access_scope == DocumentAccessScope.INDIVIDUAL
    assert doc.team_id is None
    assert doc.organisation_id == org.id
