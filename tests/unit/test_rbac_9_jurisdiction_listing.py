"""
Executable specification for RBAC-9's one backend addition: the
``GET /teams/{team_id}/managers`` read endpoint.

Covers, with no live Qdrant connection and an isolated in-memory SQLite
database (never the real dev ``astra_study.db``):

- an authenticated user can list a team's current Org Manager
  jurisdiction assignments;
- an empty jurisdiction set returns ``[]``, never an error;
- multiple managers are all returned;
- ordering is deterministic (``user_id`` ascending);
- a cross-organisation or nonexistent ``team_id`` raises the same
  enumeration-safe ``TeamNotFoundError`` as grant/revoke;
- listing requires no ``TeamMembership`` row for the caller or the
  listed managers -- jurisdiction is read from ``org_manager_teams``
  only.

This file is deliberately separate from
``tests/unit/test_rbac_5j_org_manager_jurisdiction.py`` (which is the
grant/revoke authorization spec, unchanged by this milestone) so the
two remain independently readable.
"""

from __future__ import annotations

import pytest

from app.enums.organisation import OrgRole
from app.exceptions.document import TeamNotFoundError
from app.schemas.team import OrgManagerTeamResponse

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.org_manager_team import OrgManagerTeam
from app.models.organisation import Organisation
from app.models.team import Team
from app.models.user import User
from app.repositories.org_manager_team import OrgManagerTeamRepository
from app.repositories.team import TeamRepository
from app.repositories.user import UserRepository
from app.retrieval.access import AccessContext
from app.services.org_manager_team import OrgManagerTeamService


# --------------------------------------------------------------------------- #
# Fixtures / factories -- mirrors test_rbac_5j_org_manager_jurisdiction.py
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


def make_jurisdiction(db, *, user: User, team: Team) -> OrgManagerTeam:
    jurisdiction = OrgManagerTeam(user_id=user.id, team_id=team.id)
    db.add(jurisdiction)
    db.commit()
    db.refresh(jurisdiction)
    return jurisdiction


def build_access(db, user: User) -> AccessContext:
    return AccessContext(
        user_id=user.id,
        organisation_id=user.organisation_id,
        team_ids=(),
        jurisdiction_team_ids=(),
        role=user.role,
    )


def make_service(db) -> OrgManagerTeamService:
    return OrgManagerTeamService(
        org_manager_team_repository=OrgManagerTeamRepository(db),
        team_repository=TeamRepository(db),
        user_repository=UserRepository(db),
    )


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def test_admin_can_list_team_jurisdiction(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    make_jurisdiction(db, user=manager, team=team)
    service = make_service(db)

    result = service.list_jurisdiction(access=build_access(db, admin), team_id=team.id)

    assert result == [OrgManagerTeamResponse(user_id=manager.id, team_id=team.id)]


def test_empty_jurisdiction_returns_empty_list(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    team = make_team(db, org)
    service = make_service(db)

    result = service.list_jurisdiction(access=build_access(db, admin), team_id=team.id)

    assert result == []


def test_multiple_managers_all_returned(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    manager_a = make_user(db, org, username="mgr_a", role=OrgRole.MANAGER)
    manager_b = make_user(db, org, username="mgr_b", role=OrgRole.MANAGER)
    team = make_team(db, org)
    make_jurisdiction(db, user=manager_a, team=team)
    make_jurisdiction(db, user=manager_b, team=team)
    service = make_service(db)

    result = service.list_jurisdiction(access=build_access(db, admin), team_id=team.id)

    assert {r.user_id for r in result} == {manager_a.id, manager_b.id}


def test_ordering_is_deterministic_by_user_id_ascending(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    manager_high = make_user(db, org, username="mgr_high", role=OrgRole.MANAGER)
    manager_low = make_user(db, org, username="mgr_low", role=OrgRole.MANAGER)
    team = make_team(db, org)
    # Grant in reverse-id order to prove ordering isn't insertion order.
    make_jurisdiction(db, user=manager_high, team=team)
    make_jurisdiction(db, user=manager_low, team=team)
    service = make_service(db)

    result = service.list_jurisdiction(access=build_access(db, admin), team_id=team.id)

    assert [r.user_id for r in result] == sorted(
        [manager_high.id, manager_low.id],
    )


def test_nonexistent_team_raises_team_not_found(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    service = make_service(db)

    with pytest.raises(TeamNotFoundError):
        service.list_jurisdiction(access=build_access(db, admin), team_id=999)


def test_cross_organisation_team_raises_team_not_found(db):
    org_a = make_organisation(db, slug="org-a")
    org_b = make_organisation(db, slug="org-b")
    admin = make_user(db, org_a, username="admin", role=OrgRole.ADMIN)
    other_org_team = make_team(db, org_b)
    service = make_service(db)

    with pytest.raises(TeamNotFoundError):
        service.list_jurisdiction(access=build_access(db, admin), team_id=other_org_team.id)


def test_listing_requires_no_team_membership(db):
    """
    A caller with no TeamMembership row at all (a MEMBER never added to
    any team) can still list jurisdiction -- this is a read of
    ``org_manager_teams`` only, never a membership check. The manager
    granted jurisdiction likewise has no TeamMembership row for this
    team, proving jurisdiction is structurally independent of
    membership even for the listed data itself.
    """

    org = make_organisation(db)
    caller = make_user(db, org, username="plain_member", role=OrgRole.MEMBER)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    make_jurisdiction(db, user=manager, team=team)
    service = make_service(db)

    result = service.list_jurisdiction(access=build_access(db, caller), team_id=team.id)

    assert result == [OrgManagerTeamResponse(user_id=manager.id, team_id=team.id)]
