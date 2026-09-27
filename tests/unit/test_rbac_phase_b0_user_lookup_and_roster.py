"""
Executable specification for RBAC Phase B.0: the two backend contract
gaps needed before frontend team-membership management can be built --
organisation-scoped user lookup (``GET /users``) and team roster
retrieval (``GET /teams/{team_id}/members``).

Covers, with no live Qdrant connection and an isolated in-memory SQLite
database (never the real dev ``astra_study.db``):

- ``UserService.search_organisation_users`` matches by username or email
  substring, is strictly scoped to ``access.organisation_id`` (a user in
  a different organisation never appears, regardless of how good the
  match is), is capped by an explicit limit, returns only
  ``UserResponse``'s minimal id/username/email shape (never a password
  hash), and orders results by username ascending;
- ``TeamMembershipService.list_members`` returns every member of one
  team (user_id/username/email/role), ordered by username ascending,
  and reuses the *exact* authorization boundary already established for
  add/remove/promote: only that specific team's own ``TeamRole.MANAGER``
  may call it -- explicitly not ``OrgRole.ADMIN``, not ``OrgRole.MANAGER``
  alone, not Org Manager jurisdiction (``OrgManagerTeam``), and not a
  plain ``TeamRole.MEMBER``;
- both endpoints are enumeration-safe: a nonexistent or cross-organisation
  team/user is indistinguishable from "no match" (never a distinct signal
  that something exists elsewhere).

Neither capability touches the existing add/remove/promote mutation
endpoints, migrations, Qdrant, or the frontend.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.exceptions.document import TeamNotFoundError
from app.exceptions.team import TeamMembershipOperationForbiddenError
from app.schemas.team import TeamRosterMemberResponse
from app.schemas.user import UserResponse

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.api.v1.user import search_users
from app.models.organisation import Organisation
from app.models.org_manager_team import OrgManagerTeam
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.org_manager_team import OrgManagerTeamRepository
from app.repositories.team import TeamRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.repositories.user import UserRepository
from app.retrieval.access import AccessContext
from app.services.team_membership import TeamMembershipService
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
    email: str | None = None, role: OrgRole = OrgRole.MEMBER,
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


def make_team(db, organisation: Organisation, *, name: str = "Research") -> Team:
    team = Team(organisation_id=organisation.id, name=name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def make_membership(db, user: User, team: Team, *, role: TeamRole) -> TeamMembership:
    membership = TeamMembership(user_id=user.id, team_id=team.id, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def make_jurisdiction(db, user: User, team: Team) -> OrgManagerTeam:
    jurisdiction = OrgManagerTeam(user_id=user.id, team_id=team.id)
    db.add(jurisdiction)
    db.commit()
    db.refresh(jurisdiction)
    return jurisdiction


def build_access(user: User) -> AccessContext:
    return AccessContext(
        user_id=user.id,
        organisation_id=user.organisation_id,
        team_ids=(),
        jurisdiction_team_ids=(),
        role=user.role,
    )


def make_user_service(db) -> UserService:
    return UserService(
        user_repository=UserRepository(db),
        team_membership_repository=TeamMembershipRepository(db),
        org_manager_team_repository=OrgManagerTeamRepository(db),
    )


def make_membership_service(db) -> TeamMembershipService:
    return TeamMembershipService(
        team_membership_repository=TeamMembershipRepository(db),
        team_repository=TeamRepository(db),
        user_repository=UserRepository(db),
    )


# --------------------------------------------------------------------------- #
# User lookup: matching
# --------------------------------------------------------------------------- #


def test_search_matches_by_username_substring(db):
    org = make_organisation(db)
    requester = make_user(db, org, username="requester")
    make_user(db, org, username="carolina")
    service = make_user_service(db)

    results = service.search_organisation_users(
        access=build_access(requester), query="carol",
    )

    assert [r.username for r in results] == ["carolina"]


def test_search_matches_by_email_substring(db):
    org = make_organisation(db)
    requester = make_user(db, org, username="requester")
    make_user(db, org, username="bob", email="bob@example.com")
    service = make_user_service(db)

    results = service.search_organisation_users(
        access=build_access(requester), query="bob@example",
    )

    assert [r.username for r in results] == ["bob"]


def test_search_is_case_insensitive(db):
    org = make_organisation(db)
    requester = make_user(db, org, username="requester")
    make_user(db, org, username="CaroLina")
    service = make_user_service(db)

    results = service.search_organisation_users(
        access=build_access(requester), query="CAROL",
    )

    assert [r.username for r in results] == ["CaroLina"]


def test_search_no_match_returns_empty_list(db):
    org = make_organisation(db)
    requester = make_user(db, org, username="requester")
    service = make_user_service(db)

    results = service.search_organisation_users(
        access=build_access(requester), query="nonexistent",
    )

    assert results == []


def test_search_returns_multiple_results_ordered_by_username(db):
    org = make_organisation(db)
    requester = make_user(db, org, username="requester")
    make_user(db, org, username="zeta_search")
    make_user(db, org, username="alpha_search")
    service = make_user_service(db)

    results = service.search_organisation_users(
        access=build_access(requester), query="_search",
    )

    assert [r.username for r in results] == ["alpha_search", "zeta_search"]


def test_search_results_are_capped_at_the_configured_limit(db):
    org = make_organisation(db)
    for i in range(5):
        make_user(db, org, username=f"capped_user_{i}")
    repository = UserRepository(db)

    results = repository.search_by_organisation(
        organisation_id=org.id, query="capped_user", limit=2,
    )

    assert len(results) == 2


# --------------------------------------------------------------------------- #
# User lookup: organisation scoping / enumeration safety
# --------------------------------------------------------------------------- #


def test_search_never_returns_users_from_another_organisation(db):
    org_a = make_organisation(db, slug="org-a")
    org_b = make_organisation(db, slug="org-b")
    requester = make_user(db, org_a, username="requester")
    make_user(db, org_b, username="carolina_other_org")
    service = make_user_service(db)

    results = service.search_organisation_users(
        access=build_access(requester), query="carolina",
    )

    assert results == []


# --------------------------------------------------------------------------- #
# User lookup: response shape
# --------------------------------------------------------------------------- #


def test_search_response_contains_no_sensitive_fields(db):
    org = make_organisation(db)
    requester = make_user(db, org, username="requester")
    make_user(db, org, username="dana")
    service = make_user_service(db)

    results = service.search_organisation_users(
        access=build_access(requester), query="dana",
    )

    assert len(results) == 1
    assert isinstance(results[0], UserResponse)
    assert results[0].model_dump().keys() == {"id", "username", "email"}


def test_search_users_route_delegates_to_service(db):
    """
    Calls the real route function directly (this project's established
    convention -- no TestClient anywhere in tests/unit) to confirm the
    dependency wiring produces the same result as calling the service
    directly.
    """

    org = make_organisation(db)
    requester = make_user(db, org, username="requester")
    make_user(db, org, username="erin")
    service = make_user_service(db)

    result = search_users(
        q="erin", access=build_access(requester), user_service=service,
    )

    assert [r.username for r in result] == ["erin"]


# --------------------------------------------------------------------------- #
# Team roster: content
# --------------------------------------------------------------------------- #


def test_manager_lists_roster_with_all_members(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    member = make_user(db, org, username="carol")
    make_membership(db, member, team, role=TeamRole.MEMBER)
    service = make_membership_service(db)

    roster = service.list_members(access=build_access(manager), team_id=team.id)

    assert len(roster) == 2
    by_username = {r.username: r for r in roster}
    assert by_username["manager"].user_id == manager.id
    assert by_username["manager"].role == TeamRole.MANAGER
    assert by_username["carol"].user_id == member.id
    assert by_username["carol"].role == TeamRole.MEMBER
    assert by_username["carol"].email == member.email


def test_roster_of_single_manager_team(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="solo_manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    service = make_membership_service(db)

    roster = service.list_members(access=build_access(manager), team_id=team.id)

    assert [r.user_id for r in roster] == [manager.id]


def test_roster_is_ordered_by_username_ascending(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="zeta_manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    member_b = make_user(db, org, username="bravo")
    member_a = make_user(db, org, username="alpha")
    make_membership(db, member_b, team, role=TeamRole.MEMBER)
    make_membership(db, member_a, team, role=TeamRole.MEMBER)
    service = make_membership_service(db)

    roster = service.list_members(access=build_access(manager), team_id=team.id)

    assert [r.username for r in roster] == ["alpha", "bravo", "zeta_manager"]


def test_roster_response_contains_no_sensitive_fields(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    service = make_membership_service(db)

    roster = service.list_members(access=build_access(manager), team_id=team.id)

    assert isinstance(roster[0], TeamRosterMemberResponse)
    assert roster[0].model_dump().keys() == {"user_id", "username", "email", "role"}


# --------------------------------------------------------------------------- #
# Team roster: same-org / cross-org / nonexistent team
# --------------------------------------------------------------------------- #


def test_cross_org_team_roster_access_rejected(db):
    org_a = make_organisation(db, slug="org-a")
    org_b = make_organisation(db, slug="org-b")
    manager_a = make_user(db, org_a, username="manager_a")
    team_b = make_team(db, org_b)
    manager_b = make_user(db, org_b, username="manager_b")
    make_membership(db, manager_b, team_b, role=TeamRole.MANAGER)
    service = make_membership_service(db)

    with pytest.raises(TeamNotFoundError):
        service.list_members(access=build_access(manager_a), team_id=team_b.id)


def test_nonexistent_team_roster_rejected(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    service = make_membership_service(db)

    with pytest.raises(TeamNotFoundError):
        service.list_members(access=build_access(manager), team_id=999_999)


# --------------------------------------------------------------------------- #
# Team roster: RBAC authorization boundary
# --------------------------------------------------------------------------- #


def test_team_member_cannot_list_roster(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    plain_member = make_user(db, org, username="plain_member")
    make_membership(db, plain_member, team, role=TeamRole.MEMBER)
    service = make_membership_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.list_members(access=build_access(plain_member), team_id=team.id)


def test_org_admin_alone_cannot_list_roster(db):
    """
    OrgRole.ADMIN grants no direct membership-mutation OR roster-viewing
    authority -- it is not a blanket bypass of per-team TeamRole.MANAGER
    authorization anywhere in this service.
    """

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    service = make_membership_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.list_members(access=build_access(admin), team_id=team.id)


def test_org_manager_without_team_role_cannot_list_roster(db):
    """
    OrgRole.MANAGER (org-wide) alone, without also being this specific
    team's TeamRole.MANAGER, has no roster-viewing authority either.
    """

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    org_manager = make_user(db, org, username="org_manager", role=OrgRole.MANAGER)
    service = make_membership_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.list_members(access=build_access(org_manager), team_id=team.id)


def test_org_manager_jurisdiction_does_not_grant_roster_access(db):
    """
    Org Manager jurisdiction (OrgManagerTeam, RBAC-5J) governs Qdrant/SQL
    TEAM-document *read visibility* only -- it grants no membership
    authority, and must not grant roster access either.
    """

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    org_manager = make_user(db, org, username="jurisdiction_holder", role=OrgRole.MANAGER)
    make_jurisdiction(db, org_manager, team)
    service = make_membership_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.list_members(access=build_access(org_manager), team_id=team.id)


def test_team_manager_can_list_roster(db):
    """
    Positive control for the authorization tests above: the team's own
    TeamRole.MANAGER is the one role that succeeds.
    """

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    service = make_membership_service(db)

    roster = service.list_members(access=build_access(manager), team_id=team.id)

    assert len(roster) == 1
