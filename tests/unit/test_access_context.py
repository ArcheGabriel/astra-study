"""
Executable specification for the RBAC-5A AccessContext foundation.

Covers, with no live services and no Qdrant:

- ``AccessContext``: immutability, required-identity validation, and the
  deterministic canonical form of ``team_ids``;
- ``TeamMembershipRepository``: returns exactly (and only) the requesting
  user's team ids;
- ``get_access_context``: every field is derived from server-side
  authenticated state (``current_user`` / the database), never from
  anything a client could supply, and a team-membership lookup failure is
  never swallowed.

This phase does not touch retrieval, Qdrant, or any API route -- these
tests only verify the AccessContext foundation itself.
"""

from __future__ import annotations

import dataclasses
import inspect

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.dependencies.access import get_access_context
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.retrieval.access import AccessContext

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.team_membership import TeamMembershipRepository


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


def make_team(db, organisation: Organisation, *, name: str = "Engineering") -> Team:
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


# --------------------------------------------------------------------------- #
# AccessContext
# --------------------------------------------------------------------------- #


def test_access_context_valid_construction():
    access = AccessContext(
        user_id=1,
        organisation_id=2,
        team_ids=(3, 4),
        role=OrgRole.MEMBER,
    )

    assert access.user_id == 1
    assert access.organisation_id == 2
    assert access.team_ids == (3, 4)
    assert access.role == OrgRole.MEMBER


def test_access_context_is_frozen():
    access = AccessContext(user_id=1, organisation_id=2, team_ids=(), role=OrgRole.MEMBER)

    with pytest.raises(dataclasses.FrozenInstanceError):
        access.user_id = 999


def test_access_context_missing_organisation_id_is_rejected():
    with pytest.raises(ValueError):
        AccessContext(user_id=1, organisation_id=None, team_ids=(), role=OrgRole.MEMBER)


def test_access_context_required_identity_cannot_silently_become_none():
    with pytest.raises(ValueError):
        AccessContext(user_id=None, organisation_id=2, team_ids=(), role=OrgRole.MEMBER)

    with pytest.raises(ValueError):
        AccessContext(user_id=1, organisation_id=2, team_ids=(), role=None)

    with pytest.raises(ValueError):
        AccessContext(user_id=1, organisation_id=2, team_ids=None, role=OrgRole.MEMBER)


def test_access_context_zero_team_context_is_valid():
    access = AccessContext(user_id=1, organisation_id=2, team_ids=(), role=OrgRole.MEMBER)

    assert access.team_ids == ()


def test_access_context_team_ids_are_deterministic_and_deduplicated():
    # Unsorted, duplicated, and supplied as a list rather than a tuple --
    # the stored representation must always be the same canonical,
    # immutable, deduplicated, sorted tuple regardless of input shape.
    access = AccessContext(
        user_id=1,
        organisation_id=2,
        team_ids=[5, 3, 5, 1],
        role=OrgRole.MEMBER,
    )

    assert access.team_ids == (1, 3, 5)
    assert isinstance(access.team_ids, tuple)


# --------------------------------------------------------------------------- #
# TeamMembershipRepository
# --------------------------------------------------------------------------- #


def test_team_membership_repository_returns_only_the_users_team_ids(db):
    organisation = make_organisation(db)
    user = make_user(db, organisation, username="alice")
    team_a = make_team(db, organisation, name="Engineering")
    team_b = make_team(db, organisation, name="Design")
    make_membership(db, user=user, team=team_a)
    make_membership(db, user=user, team=team_b)

    repository = TeamMembershipRepository(db)

    assert set(repository.get_team_ids_by_user_id(user.id)) == {team_a.id, team_b.id}


def test_team_membership_repository_does_not_return_another_users_teams(db):
    organisation = make_organisation(db)
    user_a = make_user(db, organisation, username="alice")
    user_b = make_user(db, organisation, username="bob")
    team = make_team(db, organisation)
    make_membership(db, user=user_a, team=team)

    repository = TeamMembershipRepository(db)

    assert repository.get_team_ids_by_user_id(user_a.id) == [team.id]
    assert repository.get_team_ids_by_user_id(user_b.id) == []


def test_team_membership_repository_zero_memberships_returns_empty_collection(db):
    organisation = make_organisation(db)
    user = make_user(db, organisation)

    repository = TeamMembershipRepository(db)

    assert repository.get_team_ids_by_user_id(user.id) == []


# --------------------------------------------------------------------------- #
# get_access_context
# --------------------------------------------------------------------------- #


def test_get_access_context_derives_identity_from_current_user(db):
    organisation = make_organisation(db)
    user = make_user(db, organisation, username="alice", role=OrgRole.MANAGER)

    access = get_access_context(current_user=user, db=db)

    assert access.user_id == user.id
    assert access.organisation_id == organisation.id
    assert access.role == OrgRole.MANAGER


def test_get_access_context_resolves_team_ids_from_repository(db):
    organisation = make_organisation(db)
    user = make_user(db, organisation)
    team_a = make_team(db, organisation, name="Engineering")
    team_b = make_team(db, organisation, name="Design")
    make_membership(db, user=user, team=team_a)
    make_membership(db, user=user, team=team_b)

    access = get_access_context(current_user=user, db=db)

    assert set(access.team_ids) == {team_a.id, team_b.id}


def test_get_access_context_zero_teams_produces_empty_team_ids(db):
    organisation = make_organisation(db)
    user = make_user(db, organisation)

    access = get_access_context(current_user=user, db=db)

    assert access.team_ids == ()


def test_get_access_context_propagates_team_membership_lookup_failure(db, monkeypatch):
    organisation = make_organisation(db)
    user = make_user(db, organisation)

    def _boom(self, user_id):
        raise RuntimeError("team membership lookup failed")

    monkeypatch.setattr(
        TeamMembershipRepository,
        "get_team_ids_by_user_id",
        _boom,
    )

    # Must propagate -- never swallowed into an empty/broad AccessContext.
    with pytest.raises(RuntimeError):
        get_access_context(current_user=user, db=db)


def test_get_access_context_signature_accepts_no_client_controllable_input():
    # The dependency's only parameters are server-resolved (current_user via
    # get_current_user's JWT decode, db via get_db) -- there is structurally
    # no parameter through which a client could supply organisation_id,
    # role, or team_ids.
    parameters = inspect.signature(get_access_context).parameters

    assert set(parameters) == {"current_user", "db"}

    for name in ("organisation_id", "team_ids", "role"):
        assert name not in parameters
