"""
Executable specification for RBAC-5H: team creation and organisation-scoped
team listing.

Covers, with no live Qdrant connection and an isolated in-memory SQLite
database (never the real dev ``astra_study.db``):

- ``TeamService.create_team`` authorizes strictly before any database read
  tied to the request (``OrgRole.ADMIN``/``MANAGER`` only, ``MEMBER``
  rejected before the duplicate-name lookup even runs);
- the creator is installed as the team's sole initial
  ``TeamRole.MANAGER`` via ``TeamRepository.create_with_initial_manager``,
  which persists the ``Team`` and its ``TeamMembership`` atomically -- a
  failure between the two can never leave a team with zero managers;
- ``organisation_id`` always comes from ``AccessContext``, never the
  client -- cross-organisation creation is impossible, and
  ``TeamCreate``'s ``extra="forbid"`` makes an ``organisation_id`` field
  structurally unsupplyable;
- duplicate team names within one organisation are rejected (pre-check),
  the same name in a different organisation is allowed, and the
  commit-time ``IntegrityError`` guard for the pre-check/commit race
  translates cleanly without leaking a raw ``IntegrityError`` or leaving
  the session in a failed-transaction state;
- ``TeamService.list_teams`` returns every team in the requester's own
  organisation (membership is never a filter), ordered by ``id``
  ascending, `[]` for an empty organisation, and never leaks another
  organisation's teams;
- ``TeamCreate``'s validation: required, 1-255 characters after
  trimming, whitespace-only rejected, ``extra="forbid"``.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.exceptions.team import (
    InvalidTeamNameError,
    TeamCreationForbiddenError,
    TeamNameAlreadyExistsError,
)
from app.schemas.team import TeamCreate, TeamResponse

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.team import TeamRepository
from app.retrieval.access import AccessContext
from app.services.team import TeamService


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


def build_access(user: User) -> AccessContext:
    return AccessContext(
        user_id=user.id,
        organisation_id=user.organisation_id,
        team_ids=(),
        jurisdiction_team_ids=(),
        role=user.role,
    )


def make_team_service(db) -> TeamService:
    return TeamService(team_repository=TeamRepository(db))


def all_teams(db) -> list[Team]:
    return list(db.execute(select(Team)).scalars().all())


def all_memberships(db) -> list[TeamMembership]:
    return list(db.execute(select(TeamMembership)).scalars().all())


# --------------------------------------------------------------------------- #
# 1-4: Creation authorization
# --------------------------------------------------------------------------- #


def test_admin_can_create_a_team(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    result = service.create_team(access=build_access(admin), name="Research")

    assert isinstance(result, TeamResponse)
    assert result.name == "Research"


def test_manager_can_create_a_team(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="bob", role=OrgRole.MANAGER)
    service = make_team_service(db)

    result = service.create_team(access=build_access(manager), name="Research")

    assert result.name == "Research"


def test_member_cannot_create_a_team(db):
    org = make_organisation(db)
    member = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    service = make_team_service(db)

    with pytest.raises(TeamCreationForbiddenError):
        service.create_team(access=build_access(member), name="Research")


def test_member_rejected_before_duplicate_lookup_or_mutation(db):
    """A MEMBER's request must never even reach the duplicate-name query
    or the database -- proven here by pre-creating a team with the exact
    same name a MEMBER then attempts to "duplicate": if authorization ran
    after the lookup, this would raise TeamNameAlreadyExistsError instead
    of TeamCreationForbiddenError."""

    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    member = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    service = make_team_service(db)

    service.create_team(access=build_access(admin), name="Research")

    with pytest.raises(TeamCreationForbiddenError):
        service.create_team(access=build_access(member), name="Research")


# --------------------------------------------------------------------------- #
# 5-8: Initial manager membership
# --------------------------------------------------------------------------- #


def test_creator_becomes_team_role_manager(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    result = service.create_team(access=build_access(admin), name="Research")

    memberships = all_memberships(db)
    assert len(memberships) == 1
    assert memberships[0].user_id == admin.id
    assert memberships[0].team_id == result.id
    assert memberships[0].role == TeamRole.MANAGER


def test_created_team_has_exactly_one_membership(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    service.create_team(access=build_access(admin), name="Research")

    assert len(all_memberships(db)) == 1


def test_initial_membership_fields_are_exact(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="bob", role=OrgRole.MANAGER)
    service = make_team_service(db)

    result = service.create_team(access=build_access(manager), name="Research")

    membership = all_memberships(db)[0]
    assert membership.user_id == manager.id
    assert membership.team_id == result.id
    assert membership.role == TeamRole.MANAGER


def test_organisation_id_comes_from_access_context(db):
    org = make_organisation(db, slug="acme")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    result = service.create_team(access=build_access(admin), name="Research")

    assert result.organisation_id == org.id


# --------------------------------------------------------------------------- #
# 9-10: Cross-organisation isolation on create
# --------------------------------------------------------------------------- #


def test_admin_cannot_create_team_in_another_organisation(db):
    """There is no organisation_id parameter anywhere in this path -- the
    persisted value is always access.organisation_id, proven here by
    creating teams for two different admins in two different
    organisations and confirming isolation."""

    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    admin_a = make_user(db, org_a, username="root-a", role=OrgRole.ADMIN)
    admin_b = make_user(db, org_b, username="root-b", role=OrgRole.ADMIN)
    service = make_team_service(db)

    team_a = service.create_team(access=build_access(admin_a), name="Research")
    team_b = service.create_team(access=build_access(admin_b), name="Research")

    assert team_a.organisation_id == org_a.id
    assert team_b.organisation_id == org_b.id
    assert team_a.organisation_id != team_b.organisation_id


def test_manager_cannot_create_team_in_another_organisation(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    manager_a = make_user(db, org_a, username="bob-a", role=OrgRole.MANAGER)
    manager_b = make_user(db, org_b, username="bob-b", role=OrgRole.MANAGER)
    service = make_team_service(db)

    team_a = service.create_team(access=build_access(manager_a), name="Support")
    team_b = service.create_team(access=build_access(manager_b), name="Support")

    assert team_a.organisation_id == org_a.id
    assert team_b.organisation_id == org_b.id


# --------------------------------------------------------------------------- #
# 11-12: Duplicate name handling (pre-check)
# --------------------------------------------------------------------------- #


def test_duplicate_team_name_in_same_organisation_is_rejected(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    service.create_team(access=build_access(admin), name="Research")

    with pytest.raises(TeamNameAlreadyExistsError):
        service.create_team(access=build_access(admin), name="Research")


def test_same_team_name_in_different_organisations_is_allowed(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    admin_a = make_user(db, org_a, username="root-a", role=OrgRole.ADMIN)
    admin_b = make_user(db, org_b, username="root-b", role=OrgRole.ADMIN)
    service = make_team_service(db)

    team_a = service.create_team(access=build_access(admin_a), name="Research")
    team_b = service.create_team(access=build_access(admin_b), name="Research")

    assert team_a.name == team_b.name == "Research"
    assert team_a.id != team_b.id


# --------------------------------------------------------------------------- #
# 13-16: Listing
# --------------------------------------------------------------------------- #


def test_list_teams_returns_only_requesters_organisation(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    admin_a = make_user(db, org_a, username="root-a", role=OrgRole.ADMIN)
    admin_b = make_user(db, org_b, username="root-b", role=OrgRole.ADMIN)
    service = make_team_service(db)

    service.create_team(access=build_access(admin_a), name="Research")
    service.create_team(access=build_access(admin_b), name="Support")

    teams = service.list_teams(access=build_access(admin_a))

    assert len(teams) == 1
    assert teams[0].organisation_id == org_a.id


def test_list_teams_includes_teams_requester_is_not_a_member_of(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    member = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    service = make_team_service(db)

    created = service.create_team(access=build_access(admin), name="Research")

    # member never joined "Research" -- has zero memberships at all.
    teams = service.list_teams(access=build_access(member))

    assert len(teams) == 1
    assert teams[0].id == created.id


def test_list_teams_returns_empty_list_for_organisation_with_no_teams(db):
    org = make_organisation(db)
    member = make_user(db, org, username="alice")
    service = make_team_service(db)

    assert service.list_teams(access=build_access(member)) == []


def test_list_teams_ordering_is_id_ascending(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    # Create in an order that would not already be ascending alphabetically.
    service.create_team(access=build_access(admin), name="Zulu")
    service.create_team(access=build_access(admin), name="Alpha")

    teams = service.list_teams(access=build_access(admin))

    assert [t.id for t in teams] == sorted(t.id for t in teams)
    assert teams[0].name == "Zulu"
    assert teams[1].name == "Alpha"


# --------------------------------------------------------------------------- #
# 17: Atomicity
# --------------------------------------------------------------------------- #


def test_creation_is_atomic_no_partial_persistence_on_failure(db, monkeypatch):
    """Simulates a failure between the Team flush and the final commit --
    neither the Team nor the TeamMembership may survive."""

    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    repository = TeamRepository(db)

    original_add = db.add

    def failing_add(instance):
        if isinstance(instance, TeamMembership):
            raise RuntimeError("simulated failure before commit")
        return original_add(instance)

    monkeypatch.setattr(db, "add", failing_add)

    with pytest.raises(RuntimeError, match="simulated failure before commit"):
        repository.create_with_initial_manager(
            organisation_id=org.id, name="Research", creator_user_id=admin.id,
        )

    db.rollback()

    assert all_teams(db) == []
    assert all_memberships(db) == []


# --------------------------------------------------------------------------- #
# 18-21: Team name validation
# --------------------------------------------------------------------------- #


def test_whitespace_around_valid_name_is_trimmed(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    result = service.create_team(access=build_access(admin), name="  Research  ")

    assert result.name == "Research"


def test_whitespace_only_name_is_rejected():
    with pytest.raises(ValidationError):
        TeamCreate(name="   ")


def test_name_over_255_characters_is_rejected():
    with pytest.raises(ValidationError):
        TeamCreate(name="x" * 256)


def test_missing_name_is_rejected():
    with pytest.raises(ValidationError):
        TeamCreate()


# --------------------------------------------------------------------------- #
# 22: organisation_id structurally unsupplyable
# --------------------------------------------------------------------------- #


def test_client_supplied_organisation_id_is_rejected_by_schema():
    with pytest.raises(ValidationError):
        TeamCreate(name="Research", organisation_id=999)


# --------------------------------------------------------------------------- #
# 23: Duplicate-name IntegrityError race/commit-path translation
# --------------------------------------------------------------------------- #


def test_duplicate_name_race_at_commit_is_translated_safely(db):
    """Bypasses the service-level pre-check by calling the repository
    directly twice for the same (organisation_id, name) -- exercises the
    commit-time IntegrityError guard exactly as a genuine TOCTOU race
    would. Must not leak a raw IntegrityError, and must not leave the
    session in a failed-transaction state (proven by a normal query
    succeeding immediately afterward)."""

    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    other_admin = make_user(db, org, username="root2", role=OrgRole.ADMIN)
    repository = TeamRepository(db)

    repository.create_with_initial_manager(
        organisation_id=org.id, name="Research", creator_user_id=admin.id,
    )

    with pytest.raises(TeamNameAlreadyExistsError):
        repository.create_with_initial_manager(
            organisation_id=org.id, name="Research", creator_user_id=other_admin.id,
        )

    # Session must still be usable -- not left in a failed-transaction state.
    teams = repository.list_by_organisation(org.id)
    assert len(teams) == 1
    assert len(all_memberships(db)) == 1


# --------------------------------------------------------------------------- #
# N-1 fix: TeamService.create_team independently validates the trimmed name
# --------------------------------------------------------------------------- #


def test_service_rejects_whitespace_only_name_called_directly(db):
    """Bypasses TeamCreate entirely -- calling the service directly with a
    single space must be rejected, and must not persist a blank-named
    team."""

    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    with pytest.raises(InvalidTeamNameError):
        service.create_team(access=build_access(admin), name=" ")

    assert all_teams(db) == []
    assert all_memberships(db) == []


def test_service_rejects_tab_and_newline_only_name_called_directly(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    with pytest.raises(InvalidTeamNameError):
        service.create_team(access=build_access(admin), name="\t\n")

    assert all_teams(db) == []
    assert all_memberships(db) == []


def test_service_rejects_name_over_255_after_trim_called_directly(db):
    """256 characters remain 256 after stripping leading/trailing padding
    that itself trims away -- the trimmed body alone already exceeds the
    limit."""

    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    with pytest.raises(InvalidTeamNameError):
        service.create_team(access=build_access(admin), name="x" * 256)

    assert all_teams(db) == []
    assert all_memberships(db) == []


def test_service_accepts_padded_valid_name_and_stores_trimmed(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_team_service(db)

    result = service.create_team(access=build_access(admin), name="   Research   ")

    assert result.name == "Research"
    stored = all_teams(db)
    assert len(stored) == 1
    assert stored[0].name == "Research"


def test_member_with_invalid_name_still_gets_forbidden_before_validation(db):
    """Authorization must still run first: a MEMBER supplying a
    blank/whitespace-only name must receive TeamCreationForbiddenError, not
    InvalidTeamNameError, and nothing may be persisted."""

    org = make_organisation(db)
    member = make_user(db, org, username="alice", role=OrgRole.MEMBER)
    service = make_team_service(db)

    with pytest.raises(TeamCreationForbiddenError):
        service.create_team(access=build_access(member), name="   ")

    assert all_teams(db) == []
    assert all_memberships(db) == []
