"""
Executable specification for the RBAC-4 Phase 1 SQL foundation.

Covers, with no live services and no Qdrant:

- the three new enums (``OrgRole``, ``TeamRole``, ``DocumentAccessScope``);
- ``Organisation`` / ``Team`` / ``TeamMembership`` creation and their
  uniqueness constraints;
- multi-team membership and the membership-role vs. org-role distinction;
- that ``documents`` supports the new RBAC columns while ``user_id``
  remains the uploader/owner, exactly as before RBAC;
- the two compatibility fixes required to keep ``UserService.register``
  and ``DocumentService.upload_documents`` working now that
  ``users.organisation_id`` / ``documents.organisation_id`` are NOT NULL
  (found by the SQLite compatibility audit -- neither constructor set the
  new required column, so both would raise ``IntegrityError`` in
  production once the RBAC migration is applied).

This phase adds no authorization logic and no retrieval behaviour -- these
tests only verify the relational model itself, plus the minimal wiring
fix that keeps the existing registration/upload paths working under it.
"""

from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from starlette.datastructures import Headers

from app.database.base import Base
from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.document import Document
from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.services.document import DocumentService
from app.services.user import DEFAULT_ORGANISATION_SLUG, UserService
from app.storage.base import BaseStorageService


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


def make_organisation(db, *, slug: str = "acme", name: str = "Acme Inc.") -> Organisation:
    organisation = Organisation(name=name, slug=slug)
    db.add(organisation)
    db.commit()
    db.refresh(organisation)
    return organisation


def make_user(
    db,
    organisation: Organisation,
    *,
    username: str = "alice",
    email: str | None = None,
    role: OrgRole = OrgRole.MEMBER,
) -> User:
    user = User(
        username=username,
        email=email or f"{username}@example.com",
        hashed_password="hashed",
        organisation_id=organisation.id,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_team(db, organisation: Organisation, *, name: str = "Engineering") -> Team:
    team = Team(organisation_id=organisation.id, name=name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def make_document(
    db,
    *,
    user: User,
    organisation: Organisation,
    filename: str = "report.pdf",
    stored_filename: str | None = None,
) -> Document:
    document = Document(
        user_id=user.id,
        organisation_id=organisation.id,
        filename=filename,
        stored_filename=stored_filename or f"{filename}-stored",
        content_type="application/pdf",
        file_size=1024,
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


# --------------------------------------------------------------------------- #
# 1-3. Enums
# --------------------------------------------------------------------------- #


def test_org_role_contains_member_manager_admin():
    assert {member.value for member in OrgRole} == {"member", "manager", "admin"}


def test_team_role_contains_member_manager():
    assert {member.value for member in TeamRole} == {"member", "manager"}


def test_document_access_scope_contains_individual_team_organisation():
    assert {member.value for member in DocumentAccessScope} == {
        "individual",
        "team",
        "organisation",
    }


# --------------------------------------------------------------------------- #
# 4-5. Organisation / Team
# --------------------------------------------------------------------------- #


def test_organisation_can_be_created(db):
    organisation = make_organisation(db, slug="acme", name="Acme Inc.")

    assert organisation.id is not None
    assert organisation.slug == "acme"
    assert organisation.name == "Acme Inc."


def test_team_belongs_to_organisation(db):
    organisation = make_organisation(db)
    team = make_team(db, organisation, name="Engineering")

    assert team.organisation_id == organisation.id
    assert team.organisation.id == organisation.id


# --------------------------------------------------------------------------- #
# 6-7. Team name uniqueness
# --------------------------------------------------------------------------- #


def test_duplicate_team_names_within_one_organisation_are_rejected(db):
    organisation = make_organisation(db)
    make_team(db, organisation, name="Engineering")

    db.add(Team(organisation_id=organisation.id, name="Engineering"))

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_same_team_name_across_different_organisations_is_allowed(db):
    org_a = make_organisation(db, slug="org-a", name="Org A")
    org_b = make_organisation(db, slug="org-b", name="Org B")

    team_a = make_team(db, org_a, name="Engineering")
    team_b = make_team(db, org_b, name="Engineering")

    assert team_a.id != team_b.id
    assert team_a.name == team_b.name == "Engineering"


# --------------------------------------------------------------------------- #
# 8-10. TeamMembership
# --------------------------------------------------------------------------- #


def test_user_can_belong_to_multiple_teams(db):
    organisation = make_organisation(db)
    user = make_user(db, organisation)
    team_a = make_team(db, organisation, name="Engineering")
    team_b = make_team(db, organisation, name="Design")

    db.add(TeamMembership(user_id=user.id, team_id=team_a.id, role=TeamRole.MEMBER))
    db.add(TeamMembership(user_id=user.id, team_id=team_b.id, role=TeamRole.MEMBER))
    db.commit()

    memberships = (
        db.query(TeamMembership).filter(TeamMembership.user_id == user.id).all()
    )
    assert {m.team_id for m in memberships} == {team_a.id, team_b.id}


def test_duplicate_user_team_membership_is_rejected(db):
    organisation = make_organisation(db)
    user = make_user(db, organisation)
    team = make_team(db, organisation)

    db.add(TeamMembership(user_id=user.id, team_id=team.id, role=TeamRole.MEMBER))
    db.commit()

    db.add(TeamMembership(user_id=user.id, team_id=team.id, role=TeamRole.MANAGER))

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_team_membership_role_distinguishes_member_and_manager(db):
    organisation = make_organisation(db)
    member_user = make_user(db, organisation, username="member-user")
    manager_user = make_user(db, organisation, username="manager-user")
    team = make_team(db, organisation)

    db.add(TeamMembership(user_id=member_user.id, team_id=team.id, role=TeamRole.MEMBER))
    db.add(TeamMembership(user_id=manager_user.id, team_id=team.id, role=TeamRole.MANAGER))
    db.commit()

    roles = {
        membership.user_id: membership.role
        for membership in db.query(TeamMembership).filter(TeamMembership.team_id == team.id)
    }
    assert roles[member_user.id] == TeamRole.MEMBER
    assert roles[manager_user.id] == TeamRole.MANAGER

    # Membership role is independent of the user's organisation-scoped role:
    # both users here are plain OrgRole.MEMBER at the org level (the default),
    # yet one is a TeamRole.MANAGER of this specific team.
    assert member_user.role == OrgRole.MEMBER
    assert manager_user.role == OrgRole.MEMBER


# --------------------------------------------------------------------------- #
# 11-12. Document RBAC fields / existing ownership
# --------------------------------------------------------------------------- #


def test_document_defaults_support_individual_scope(db):
    organisation = make_organisation(db)
    user = make_user(db, organisation)

    document = make_document(db, user=user, organisation=organisation)

    assert document.access_scope == DocumentAccessScope.INDIVIDUAL
    assert document.team_id is None
    assert document.organisation_id == organisation.id


def test_existing_document_ownership_via_user_id_remains_intact(db):
    organisation = make_organisation(db)
    user = make_user(db, organisation, username="owner")

    document = make_document(db, user=user, organisation=organisation)

    # user_id is still the uploader/owner -- unchanged by the RBAC columns.
    assert document.user_id == user.id
    assert document.user.id == user.id
    assert document in user.documents


# --------------------------------------------------------------------------- #
# Compatibility fixes: UserService.register / DocumentService.upload_documents
#
# users.organisation_id and documents.organisation_id are NOT NULL. Neither
# constructor originally set them, so both would raise IntegrityError against
# a migrated database. These are regression tests for that fix.
# --------------------------------------------------------------------------- #


class FakeStorageService(BaseStorageService):
    """
    In-memory stand-in for LocalStorageService -- no filesystem access, so
    this stays a fast, isolated unit test.
    """

    async def save_file(self, file):
        content = await file.read()
        return (f"stored-{file.filename}", len(content))

    async def delete_file(self, stored_filename: str) -> None:
        pass

    def get_file_path(self, stored_filename: str) -> Path:
        return Path(stored_filename)


def make_upload_file(*, filename: str = "report.pdf", content_type: str = "application/pdf") -> UploadFile:
    return UploadFile(
        file=BytesIO(b"%PDF-1.4 minimal fake pdf content"),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


def test_registration_attaches_default_organisation_and_member_role(db):
    make_organisation(db, slug=DEFAULT_ORGANISATION_SLUG, name="Default Organisation")

    service = UserService(UserRepository(db))

    user = service.register(
        UserCreate(username="newuser", email="newuser@example.com", password="password123")
    )

    assert user.id is not None
    assert user.organisation.slug == DEFAULT_ORGANISATION_SLUG
    assert user.role == OrgRole.MEMBER


def test_registration_fails_clearly_when_default_organisation_is_missing(db):
    # No organisation seeded -- simulates an unmigrated / misconfigured database.
    service = UserService(UserRepository(db))

    with pytest.raises(RuntimeError):
        service.register(
            UserCreate(username="orphan", email="orphan@example.com", password="password123")
        )

    # And no "default" organisation was silently created as a side effect.
    assert db.query(Organisation).count() == 0


def test_document_upload_receives_uploaders_organisation_id(db):
    organisation = make_organisation(db)
    other_organisation = make_organisation(db, slug="other-org", name="Other Org")
    user = make_user(db, organisation, username="uploader")

    service = DocumentService(
        document_repository=DocumentRepository(db),
        storage_service=FakeStorageService(),
    )

    # No pytest-asyncio/anyio plugin is configured for this project
    # (pyproject.toml's dev group is plain pytest only), so the async
    # service method is driven directly via asyncio.run rather than an
    # async test function -- the smallest approach that needs no new
    # dependency and matches the existing project setup.
    uploaded = asyncio.run(
        service.upload_documents(
            files=[make_upload_file()],
            current_user=user,
        )
    )

    assert len(uploaded) == 1
    document = uploaded[0]
    assert document.user_id == user.id
    assert document.organisation_id == user.organisation_id
    assert document.organisation_id == organisation.id
    assert document.organisation_id != other_organisation.id
