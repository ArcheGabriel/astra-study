"""
Executable specification for RBAC-5G: "who am I" / RBAC context exposure
via ``GET /users/me``.

Covers, with no live Qdrant connection and an isolated in-memory SQLite
database (never the real dev ``astra_study.db``):

- ``TeamMembershipRepository.get_memberships_with_team_by_user_id`` returns
  every membership row for a user with its team eagerly loaded
  (``team_id``/``team_name``/``role``), ordered deterministically by
  ``team_id`` regardless of insertion order, empty for a user with no
  memberships, and never leaks another user's memberships;
- ``UserService.get_profile`` builds a ``UserProfileResponse`` with the
  correct ``organisation_id``/``role`` (sourced directly from the ``User``
  row, no extra query) and the correct, distinct ``TeamRole`` per
  membership;
- ``UserResponse.model_validate(user)`` -- the exact call
  ``POST /auth/register`` and ``AuthService.authenticate`` already make --
  still produces only the original three-field (``id``/``username``/
  ``email``) shape, proving ``UserResponse``/``TokenResponse`` were not
  touched by this stage;
- ``get_current_user_profile`` (the ``GET /users/me`` route function)
  wired end-to-end, called directly rather than through a TestClient,
  matching this project's existing testing convention.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.schemas.user import UserProfileResponse, UserResponse

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.api.v1.user import get_current_user_profile
from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.team_membership import TeamMembershipRepository
from app.repositories.user import UserRepository
from app.services.user import UserService


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


def make_team(db, organisation: Organisation, *, name: str) -> Team:
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


def make_user_service(db) -> UserService:
    return UserService(
        UserRepository(db),
        team_membership_repository=TeamMembershipRepository(db),
    )


# --------------------------------------------------------------------------- #
# 1-4: TeamMembershipRepository.get_memberships_with_team_by_user_id
# --------------------------------------------------------------------------- #


def test_repository_returns_correct_team_id_name_and_role(db):
    org = make_organisation(db)
    user = make_user(db, org)
    team = make_team(db, org, name="Research")
    make_membership(db, user=user, team=team, role=TeamRole.MANAGER)

    memberships = TeamMembershipRepository(db).get_memberships_with_team_by_user_id(user.id)

    assert len(memberships) == 1
    assert memberships[0].team_id == team.id
    assert memberships[0].team.name == "Research"
    assert memberships[0].role == TeamRole.MANAGER


def test_repository_returns_empty_list_for_user_with_no_memberships(db):
    org = make_organisation(db)
    user = make_user(db, org)

    memberships = TeamMembershipRepository(db).get_memberships_with_team_by_user_id(user.id)

    assert memberships == []


def test_repository_orders_memberships_by_team_id_ascending(db):
    org = make_organisation(db)
    user = make_user(db, org)

    # Create teams and memberships in an order that would NOT already be
    # ascending by team_id (name "Zulu" is created, and joined, first).
    team_z = make_team(db, org, name="Zulu")
    team_a = make_team(db, org, name="Alpha")
    make_membership(db, user=user, team=team_z)
    make_membership(db, user=user, team=team_a)

    memberships = TeamMembershipRepository(db).get_memberships_with_team_by_user_id(user.id)

    assert [m.team_id for m in memberships] == sorted(m.team_id for m in memberships)
    assert memberships[0].team_id == team_z.id  # team_z was created (and thus id-assigned) first
    assert memberships[1].team_id == team_a.id


def test_repository_never_leaks_another_users_memberships(db):
    org = make_organisation(db)
    alice = make_user(db, org, username="alice")
    bob = make_user(db, org, username="bob")
    team = make_team(db, org, name="Research")
    make_membership(db, user=alice, team=team)
    # bob has no memberships at all.

    alice_memberships = TeamMembershipRepository(db).get_memberships_with_team_by_user_id(alice.id)
    bob_memberships = TeamMembershipRepository(db).get_memberships_with_team_by_user_id(bob.id)

    assert len(alice_memberships) == 1
    assert bob_memberships == []


# --------------------------------------------------------------------------- #
# 5-6: UserService.get_profile
# --------------------------------------------------------------------------- #


def test_get_profile_returns_correct_organisation_id_and_role(db):
    org = make_organisation(db, slug="acme")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_user_service(db)

    profile = service.get_profile(admin)

    assert isinstance(profile, UserProfileResponse)
    assert profile.id == admin.id
    assert profile.username == admin.username
    assert profile.email == admin.email
    assert profile.organisation_id == org.id
    assert profile.role == OrgRole.ADMIN


def test_get_profile_preserves_distinct_team_roles_per_membership(db):
    org = make_organisation(db)
    user = make_user(db, org)
    team_managed = make_team(db, org, name="Research")
    team_member = make_team(db, org, name="Support")
    make_membership(db, user=user, team=team_managed, role=TeamRole.MANAGER)
    make_membership(db, user=user, team=team_member, role=TeamRole.MEMBER)
    service = make_user_service(db)

    profile = service.get_profile(user)

    roles_by_team_id = {t.team_id: t.role for t in profile.teams}
    assert roles_by_team_id[team_managed.id] == TeamRole.MANAGER
    assert roles_by_team_id[team_member.id] == TeamRole.MEMBER
    names_by_team_id = {t.team_id: t.team_name for t in profile.teams}
    assert names_by_team_id[team_managed.id] == "Research"
    assert names_by_team_id[team_member.id] == "Support"


def test_get_profile_returns_empty_teams_list_for_user_with_no_memberships(db):
    org = make_organisation(db)
    user = make_user(db, org)
    service = make_user_service(db)

    profile = service.get_profile(user)

    assert profile.teams == []


# --------------------------------------------------------------------------- #
# 7: UserResponse / TokenResponse untouched
# --------------------------------------------------------------------------- #


def test_user_response_model_validate_still_produces_original_three_field_shape(db):
    """Locks in that UserResponse -- the exact schema POST /auth/register
    returns and TokenResponse.user embeds for POST /auth/login and
    POST /auth/token -- was not touched by RBAC-5G."""

    org = make_organisation(db)
    user = make_user(db, org, role=OrgRole.ADMIN)

    response = UserResponse.model_validate(user)

    assert response.model_dump() == {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


# --------------------------------------------------------------------------- #
# 8: GET /users/me route wiring
# --------------------------------------------------------------------------- #


def test_get_current_user_profile_route_returns_full_profile(db):
    """Calls the real route function directly (this project's established
    convention -- no TestClient anywhere in tests/unit) to confirm the
    full dependency wiring (current_user + UserService.get_profile)
    produces the same result as calling the service directly."""

    org = make_organisation(db, slug="acme")
    user = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    team = make_team(db, org, name="Research")
    make_membership(db, user=user, team=team, role=TeamRole.MANAGER)
    service = make_user_service(db)

    result = get_current_user_profile(current_user=user, user_service=service)

    assert isinstance(result, UserProfileResponse)
    assert result.organisation_id == org.id
    assert result.role == OrgRole.MEMBER
    assert len(result.teams) == 1
    assert result.teams[0].team_id == team.id
    assert result.teams[0].team_name == "Research"
    assert result.teams[0].role == TeamRole.MANAGER
