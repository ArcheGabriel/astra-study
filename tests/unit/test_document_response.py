"""
Executable specification for RBAC-8: the ``DocumentResponse`` schema's
exposure of existing document RBAC metadata (``access_scope``, ``team_id``,
``organisation_id``).

Covers, with no live Qdrant connection and an isolated in-memory SQLite
database (never the real dev ``astra_study.db``):

- ``DocumentResponse.model_validate(document)`` -- the existing, unmodified
  conversion path used by every route -- correctly serializes the three
  RBAC fields for each of the three ``DocumentAccessScope`` values;
- ``team_id`` is ``None`` for INDIVIDUAL/ORGANISATION documents and
  populated for TEAM documents, never fabricated either way;
- the real production call sites (``DocumentService.get_documents`` /
  ``get_document``) -- not just direct schema construction -- also
  produce the correct fields, proving the exposure works through the
  actual service layer, not merely in isolation.

This file is deliberately separate from
``tests/unit/test_rbac_5d_document_authorization.py``: that file proves
*authorization* (who may see/delete which document); this file proves
*response shape* only. Neither authorization logic nor the SQL/Qdrant
authorization filters are touched or exercised here.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole
from app.retrieval.access import AccessContext
from app.schemas.document import DocumentResponse

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.database.base import Base
from app.enums.team import TeamRole
from app.models.document import Document
from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.document import DocumentRepository
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


def make_organisation(db, *, slug: str = "acme") -> Organisation:
    organisation = Organisation(name=slug.title(), slug=slug)
    db.add(organisation)
    db.commit()
    db.refresh(organisation)
    return organisation


def make_user(
    db, organisation: Organisation, *, username: str = "alice",
    role: OrgRole = OrgRole.MEMBER,
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


def make_team(db, organisation: Organisation, *, name: str = "Research") -> Team:
    team = Team(organisation_id=organisation.id, name=name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def make_membership(
    db, *, user: User, team: Team, role: TeamRole = TeamRole.MEMBER,
) -> TeamMembership:
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
        stored_filename=f"stored-{owner.id}-{access_scope.value}.pdf",
        content_type="application/pdf",
        file_size=1024,
        status=DocumentStatus.INDEXED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def build_access(db, user: User) -> AccessContext:
    team_ids = TeamMembershipRepository(db).get_team_ids_by_user_id(user.id)
    return AccessContext(
        user_id=user.id,
        organisation_id=user.organisation_id,
        team_ids=tuple(team_ids),
        jurisdiction_team_ids=(),
        role=user.role,
    )


def make_document_service(db) -> DocumentService:
    return DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=MagicMock(delete_file=AsyncMock()),
        team_membership_repository=TeamMembershipRepository(db),
        dense_repository=MagicMock(),
        team_repository=MagicMock(),
    )


# --------------------------------------------------------------------------- #
# Direct schema construction: 1-3
# --------------------------------------------------------------------------- #


def test_individual_document_response_fields(db):
    org = make_organisation(db)
    owner = make_user(db, org)
    document = make_document(db, owner=owner, organisation=org)

    response = DocumentResponse.model_validate(document)

    assert response.access_scope == DocumentAccessScope.INDIVIDUAL
    assert response.access_scope.value == "individual"
    assert response.team_id is None
    assert response.organisation_id == org.id


def test_team_document_response_fields(db):
    org = make_organisation(db)
    owner = make_user(db, org)
    team = make_team(db, org)
    document = make_document(
        db, owner=owner, organisation=org,
        access_scope=DocumentAccessScope.TEAM, team=team,
    )

    response = DocumentResponse.model_validate(document)

    assert response.access_scope == DocumentAccessScope.TEAM
    assert response.access_scope.value == "team"
    assert response.team_id == team.id
    assert response.organisation_id == org.id


def test_organisation_document_response_fields(db):
    org = make_organisation(db)
    owner = make_user(db, org)
    document = make_document(
        db, owner=owner, organisation=org,
        access_scope=DocumentAccessScope.ORGANISATION,
    )

    response = DocumentResponse.model_validate(document)

    assert response.access_scope == DocumentAccessScope.ORGANISATION
    assert response.access_scope.value == "organisation"
    assert response.team_id is None
    assert response.organisation_id == org.id


# --------------------------------------------------------------------------- #
# model_validate serialization: 4
# --------------------------------------------------------------------------- #


def test_model_validate_produces_json_serializable_string_for_access_scope(db):
    """
    ``DocumentAccessScope`` is a ``str, Enum`` -- confirms the actual JSON
    representation (via ``model_dump(mode="json")``) is the plain lowercase
    string value, matching the frontend's existing hardcoded constants
    (``frontend/access_scope.py``), not the Python enum repr.
    """

    org = make_organisation(db)
    owner = make_user(db, org)
    document = make_document(db, owner=owner, organisation=org)

    response = DocumentResponse.model_validate(document)
    dumped = response.model_dump(mode="json")

    assert dumped["access_scope"] == "individual"
    assert dumped["team_id"] is None
    assert dumped["organisation_id"] == org.id


# --------------------------------------------------------------------------- #
# Real production call sites: 5
# --------------------------------------------------------------------------- #


def test_get_documents_service_call_site_includes_rbac_fields(db):
    org = make_organisation(db)
    owner = make_user(db, org)
    team = make_team(db, org)
    # TEAM read visibility requires actual TeamMembership -- ownership
    # alone is not sufficient (DocumentRepository._visibility_conditions
    # requires the TEAM branch's team_id to be in access.team_ids).
    make_membership(db, user=owner, team=team)
    make_document(db, owner=owner, organisation=org)
    make_document(
        db, owner=owner, organisation=org,
        access_scope=DocumentAccessScope.TEAM, team=team,
    )
    service = make_document_service(db)

    results = service.get_documents(access=build_access(db, owner))

    individual_result = next(r for r in results if r.access_scope == DocumentAccessScope.INDIVIDUAL)
    team_result = next(r for r in results if r.access_scope == DocumentAccessScope.TEAM)

    assert individual_result.team_id is None
    assert individual_result.organisation_id == org.id
    assert team_result.team_id == team.id
    assert team_result.organisation_id == org.id


def test_get_document_service_call_site_includes_rbac_fields(db):
    org = make_organisation(db)
    owner = make_user(db, org)
    team = make_team(db, org)
    make_membership(db, user=owner, team=team)
    document = make_document(
        db, owner=owner, organisation=org,
        access_scope=DocumentAccessScope.TEAM, team=team,
    )
    service = make_document_service(db)

    result = service.get_document(document_id=document.id, access=build_access(db, owner))

    assert result.access_scope == DocumentAccessScope.TEAM
    assert result.team_id == team.id
    assert result.organisation_id == org.id
