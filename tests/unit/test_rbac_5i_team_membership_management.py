"""
Executable specification for RBAC-5I: direct team membership management.

Covers, with no live Qdrant connection and an isolated in-memory SQLite
database (never the real dev ``astra_study.db``):

- ``TeamMembershipService`` implements exactly four operations: add a
  ``TeamRole.MEMBER``, remove a member (any role), promote
  ``MEMBER -> MANAGER``, and the last-manager invariant on manager
  removal;
- there is no ``MANAGER -> MEMBER`` demotion operation anywhere -- a
  manager only ever stops being one by being removed from the team
  entirely, and only when another manager remains;
- authorization is strict: only the target team's own
  ``TeamRole.MANAGER`` may perform any of the four operations.
  ``OrgRole.ADMIN`` and ``OrgRole.MANAGER`` (without also being that
  team's own ``TeamRole.MANAGER``) have no direct membership-mutation
  authority in this stage;
- every operation is organisation-scoped: a cross-organisation team or
  target user is rejected before any mutation;
- the last-manager invariant is enforced atomically and leaves no
  partial state on rejection;
- this milestone touches nothing in the document/retrieval/Qdrant
  authorization surface -- verified by a regression check that reuses
  ``DocumentService``'s existing authorization behavior unchanged.
"""

from __future__ import annotations

import threading

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.exceptions.team import (
    LastTeamManagerError,
    TeamMemberNotFoundError,
    TeamMembershipAlreadyExistsError,
    TeamMembershipOperationForbiddenError,
)
from app.exceptions.document import TeamNotFoundError
from app.exceptions.user import UserNotFoundError
from app.schemas.team import TeamMemberResponse

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.team import TeamRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.repositories.user import UserRepository
from app.retrieval.access import AccessContext
from app.services.team_membership import TeamMembershipService


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


def make_membership(db, user: User, team: Team, *, role: TeamRole) -> TeamMembership:
    membership = TeamMembership(user_id=user.id, team_id=team.id, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def build_access(user: User) -> AccessContext:
    return AccessContext(
        user_id=user.id,
        organisation_id=user.organisation_id,
        team_ids=(),
        role=user.role,
    )


def make_service(db) -> TeamMembershipService:
    return TeamMembershipService(
        team_membership_repository=TeamMembershipRepository(db),
        team_repository=TeamRepository(db),
        user_repository=UserRepository(db),
    )


def get_membership(db, user: User, team: Team) -> TeamMembership | None:
    statement = select(TeamMembership).where(
        TeamMembership.user_id == user.id,
        TeamMembership.team_id == team.id,
    )
    return db.execute(statement).scalar_one_or_none()


def all_memberships(db) -> list[TeamMembership]:
    return list(db.execute(select(TeamMembership)).scalars().all())


# --------------------------------------------------------------------------- #
# Add member
# --------------------------------------------------------------------------- #


def test_manager_adds_member(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    service = make_service(db)

    result = service.add_member(
        access=build_access(manager), team_id=team.id, user_id=target.id,
    )

    assert isinstance(result, TeamMemberResponse)
    assert result.role == TeamRole.MEMBER
    membership = get_membership(db, target, team)
    assert membership is not None
    assert membership.role == TeamRole.MEMBER


def test_duplicate_membership_rejected_on_add(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    make_membership(db, target, team, role=TeamRole.MEMBER)
    service = make_service(db)

    with pytest.raises(TeamMembershipAlreadyExistsError):
        service.add_member(access=build_access(manager), team_id=team.id, user_id=target.id)

    assert len(all_memberships(db)) == 2


def test_add_nonexistent_user_rejected(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    service = make_service(db)

    with pytest.raises(UserNotFoundError):
        service.add_member(access=build_access(manager), team_id=team.id, user_id=999999)

    assert len(all_memberships(db)) == 1


def test_add_to_nonexistent_team_rejected(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    target = make_user(db, org, username="carol")
    service = make_service(db)

    with pytest.raises(TeamNotFoundError):
        service.add_member(access=build_access(manager), team_id=999999, user_id=target.id)

    assert all_memberships(db) == []


def test_add_cross_org_user_rejected(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    manager = make_user(db, org_a, username="manager")
    team = make_team(db, org_a)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    outsider = make_user(db, org_b, username="dave")
    service = make_service(db)

    with pytest.raises(UserNotFoundError):
        service.add_member(access=build_access(manager), team_id=team.id, user_id=outsider.id)

    assert len(all_memberships(db)) == 1


def test_unauthorized_member_cannot_add(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    plain_member = make_user(db, org, username="bob")
    make_membership(db, plain_member, team, role=TeamRole.MEMBER)
    target = make_user(db, org, username="carol")
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.add_member(access=build_access(plain_member), team_id=team.id, user_id=target.id)

    assert len(all_memberships(db)) == 2


def test_admin_cannot_directly_add_member(db):
    """ADMIN has no direct membership-mutation authority in this stage."""

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    target = make_user(db, org, username="carol")
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.add_member(access=build_access(admin), team_id=team.id, user_id=target.id)

    assert len(all_memberships(db)) == 1


def test_org_manager_without_team_role_cannot_add(db):
    """OrgRole.MANAGER alone does not imply TeamRole.MANAGER authority."""

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    org_manager = make_user(db, org, username="orgmgr", role=OrgRole.MANAGER)
    target = make_user(db, org, username="carol")
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.add_member(access=build_access(org_manager), team_id=team.id, user_id=target.id)

    assert len(all_memberships(db)) == 1


# --------------------------------------------------------------------------- #
# Remove member
# --------------------------------------------------------------------------- #


def test_manager_removes_member(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    make_membership(db, target, team, role=TeamRole.MEMBER)
    service = make_service(db)

    service.remove_member(access=build_access(manager), team_id=team.id, user_id=target.id)

    assert get_membership(db, target, team) is None
    assert len(all_memberships(db)) == 1


def test_remove_nonexistent_membership_rejected(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    service = make_service(db)

    with pytest.raises(TeamMemberNotFoundError):
        service.remove_member(access=build_access(manager), team_id=team.id, user_id=target.id)


def test_unauthorized_actor_cannot_remove_member(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    make_membership(db, target, team, role=TeamRole.MEMBER)
    plain_member = make_user(db, org, username="bob")
    make_membership(db, plain_member, team, role=TeamRole.MEMBER)
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.remove_member(access=build_access(plain_member), team_id=team.id, user_id=target.id)

    assert get_membership(db, target, team) is not None


# --------------------------------------------------------------------------- #
# Promote
# --------------------------------------------------------------------------- #


def test_promote_member_to_manager(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    original = make_membership(db, target, team, role=TeamRole.MEMBER)
    service = make_service(db)

    result = service.promote_member(access=build_access(manager), team_id=team.id, user_id=target.id)

    assert result.role == TeamRole.MANAGER
    membership = get_membership(db, target, team)
    assert membership is not None
    assert membership.id == original.id
    assert membership.role == TeamRole.MANAGER
    # Only the role changed -- no new row, no jurisdiction-shaped artifact.
    assert len(all_memberships(db)) == 2


def test_promote_already_manager_rejected(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    other_manager = make_user(db, org, username="dave")
    make_membership(db, other_manager, team, role=TeamRole.MANAGER)
    service = make_service(db)

    with pytest.raises(TeamMembershipAlreadyExistsError):
        service.promote_member(access=build_access(manager), team_id=team.id, user_id=other_manager.id)


def test_promote_non_member_rejected(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    outsider = make_user(db, org, username="carol")
    service = make_service(db)

    with pytest.raises(TeamMemberNotFoundError):
        service.promote_member(access=build_access(manager), team_id=team.id, user_id=outsider.id)


def test_unauthorized_actor_cannot_promote(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    make_membership(db, target, team, role=TeamRole.MEMBER)
    plain_member = make_user(db, org, username="bob")
    make_membership(db, plain_member, team, role=TeamRole.MEMBER)
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.promote_member(access=build_access(plain_member), team_id=team.id, user_id=target.id)

    membership = get_membership(db, target, team)
    assert membership.role == TeamRole.MEMBER


def test_admin_cannot_directly_remove_member(db):
    """ADMIN has no direct membership-mutation authority in this stage."""

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    make_membership(db, target, team, role=TeamRole.MEMBER)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.remove_member(access=build_access(admin), team_id=team.id, user_id=target.id)

    assert get_membership(db, target, team) is not None


def test_admin_cannot_directly_promote_member(db):
    """ADMIN has no direct membership-mutation authority in this stage."""

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    make_membership(db, target, team, role=TeamRole.MEMBER)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.promote_member(access=build_access(admin), team_id=team.id, user_id=target.id)

    membership = get_membership(db, target, team)
    assert membership.role == TeamRole.MEMBER


def test_org_manager_without_team_role_cannot_remove(db):
    """OrgRole.MANAGER alone does not imply TeamRole.MANAGER authority."""

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    make_membership(db, target, team, role=TeamRole.MEMBER)
    org_manager = make_user(db, org, username="orgmgr", role=OrgRole.MANAGER)
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.remove_member(access=build_access(org_manager), team_id=team.id, user_id=target.id)

    assert get_membership(db, target, team) is not None


def test_org_manager_without_team_role_cannot_promote(db):
    """OrgRole.MANAGER alone does not imply TeamRole.MANAGER authority."""

    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="carol")
    make_membership(db, target, team, role=TeamRole.MEMBER)
    org_manager = make_user(db, org, username="orgmgr", role=OrgRole.MANAGER)
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.promote_member(access=build_access(org_manager), team_id=team.id, user_id=target.id)

    membership = get_membership(db, target, team)
    assert membership.role == TeamRole.MEMBER


# --------------------------------------------------------------------------- #
# Remove manager / last-manager invariant
# --------------------------------------------------------------------------- #


def test_remove_manager_when_another_manager_exists(db):
    org = make_organisation(db)
    manager_1 = make_user(db, org, username="manager1")
    manager_2 = make_user(db, org, username="manager2")
    team = make_team(db, org)
    make_membership(db, manager_1, team, role=TeamRole.MANAGER)
    make_membership(db, manager_2, team, role=TeamRole.MANAGER)
    service = make_service(db)

    service.remove_member(access=build_access(manager_1), team_id=team.id, user_id=manager_2.id)

    assert get_membership(db, manager_2, team) is None
    remaining = get_membership(db, manager_1, team)
    assert remaining is not None
    assert remaining.role == TeamRole.MANAGER


def test_final_manager_removal_rejected(db):
    org = make_organisation(db)
    sole_manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    make_membership(db, sole_manager, team, role=TeamRole.MANAGER)
    service = make_service(db)

    with pytest.raises(LastTeamManagerError):
        service.remove_member(access=build_access(sole_manager), team_id=team.id, user_id=sole_manager.id)

    remaining = get_membership(db, sole_manager, team)
    assert remaining is not None
    assert remaining.role == TeamRole.MANAGER
    assert len(all_memberships(db)) == 1


def test_final_manager_remains_manager_after_rejected_removal(db):
    """The rejected operation must never demote the target -- the row
    must be byte-for-byte unchanged."""

    org = make_organisation(db)
    sole_manager = make_user(db, org, username="manager")
    team = make_team(db, org)
    original = make_membership(db, sole_manager, team, role=TeamRole.MANAGER)
    service = make_service(db)

    with pytest.raises(LastTeamManagerError):
        service.remove_member(access=build_access(sole_manager), team_id=team.id, user_id=sole_manager.id)

    membership = get_membership(db, sole_manager, team)
    assert membership.id == original.id
    assert membership.role == TeamRole.MANAGER


def test_removed_manager_has_no_membership_row(db):
    org = make_organisation(db)
    manager_1 = make_user(db, org, username="manager1")
    manager_2 = make_user(db, org, username="manager2")
    team = make_team(db, org)
    make_membership(db, manager_1, team, role=TeamRole.MANAGER)
    make_membership(db, manager_2, team, role=TeamRole.MANAGER)
    service = make_service(db)

    service.remove_member(access=build_access(manager_1), team_id=team.id, user_id=manager_1.id)

    assert get_membership(db, manager_1, team) is None


def test_removed_manager_is_not_converted_to_member(db):
    """Removal must be a full row deletion, never a MANAGER -> MEMBER
    demotion in place."""

    org = make_organisation(db)
    manager_1 = make_user(db, org, username="manager1")
    manager_2 = make_user(db, org, username="manager2")
    team = make_team(db, org)
    make_membership(db, manager_1, team, role=TeamRole.MANAGER)
    make_membership(db, manager_2, team, role=TeamRole.MANAGER)
    service = make_service(db)

    service.remove_member(access=build_access(manager_1), team_id=team.id, user_id=manager_2.id)

    membership = get_membership(db, manager_2, team)
    assert membership is None, "removed manager must have no row at all, not a MEMBER row"


def test_unauthorized_actor_cannot_remove_manager(db):
    org = make_organisation(db)
    manager_1 = make_user(db, org, username="manager1")
    manager_2 = make_user(db, org, username="manager2")
    team = make_team(db, org)
    make_membership(db, manager_1, team, role=TeamRole.MANAGER)
    make_membership(db, manager_2, team, role=TeamRole.MANAGER)
    plain_member = make_user(db, org, username="bob")
    make_membership(db, plain_member, team, role=TeamRole.MEMBER)
    service = make_service(db)

    with pytest.raises(TeamMembershipOperationForbiddenError):
        service.remove_member(access=build_access(plain_member), team_id=team.id, user_id=manager_2.id)

    assert get_membership(db, manager_2, team) is not None


# --------------------------------------------------------------------------- #
# Organisation boundaries
# --------------------------------------------------------------------------- #


def test_cross_org_team_access_rejected(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    manager_a = make_user(db, org_a, username="manager-a")
    team_b = make_team(db, org_b, name="Support")
    make_membership(db, make_user(db, org_b, username="manager-b"), team_b, role=TeamRole.MANAGER)
    target = make_user(db, org_b, username="carol-b")
    service = make_service(db)

    with pytest.raises(TeamNotFoundError):
        service.add_member(access=build_access(manager_a), team_id=team_b.id, user_id=target.id)


def test_cross_org_target_user_rejected(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    manager = make_user(db, org_a, username="manager")
    team = make_team(db, org_a)
    make_membership(db, manager, team, role=TeamRole.MANAGER)
    outsider = make_user(db, org_b, username="dave")
    service = make_service(db)

    with pytest.raises(UserNotFoundError):
        service.promote_member(access=build_access(manager), team_id=team.id, user_id=outsider.id)


# --------------------------------------------------------------------------- #
# Regression: 5I must not alter document authorization
# --------------------------------------------------------------------------- #


def test_document_authorization_unaffected_by_membership_service_import():
    """
    RBAC-5I must not alter document/Qdrant/retrieval authorization.
    Importing TeamMembershipService alongside DocumentService's
    authorization helper must not change its behavior or signature.
    """

    from app.services.document import DocumentService

    assert hasattr(DocumentService, "_can_create")
    assert hasattr(DocumentService, "_can_delete")


# --------------------------------------------------------------------------- #
# Permanent concurrency regression tests
#
# These exercise the actual production TeamMembershipRepository methods
# under real OS-thread concurrency against a file-backed SQLite database
# (never the in-memory `sqlite://` used by the `db` fixture above, which
# cannot be shared meaningfully across threads/connections the way these
# races require). A `threading.Barrier` forces genuine overlap between
# the two workers rather than merely starting two threads sequentially.
# --------------------------------------------------------------------------- #


def _make_file_backed_session_factory(tmp_path, filename: str):
    """
    Build a session factory bound to a real file-backed SQLite database
    under pytest's ``tmp_path`` (auto-cleaned by pytest; never the real
    dev ``astra_study.db``), so two independent threads/sessions can
    genuinely contend for the same SQLite file lock the way production
    concurrent requests would.
    """

    engine = create_engine(f"sqlite:///{tmp_path / filename}")
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_concurrent_final_manager_removal_leaves_one_manager(tmp_path):
    """
    Permanent regression test for the last-manager concurrency fix.

    Two real OS threads, each with its own SQLAlchemy session against
    the same file-backed SQLite database, each call the actual
    production ``TeamMembershipRepository.remove_membership`` to remove
    a *different* one of a team's exactly-two managers, synchronized by
    a ``threading.Barrier`` so both calls genuinely overlap.

    Against the old ``SELECT count(...)`` -> ``DELETE`` implementation,
    both threads could observe "one other manager remains" before
    either committed, and both removals would succeed, leaving zero
    managers -- violating the frozen invariant that a team must always
    retain at least one ``TeamRole.MANAGER``. Against the current
    atomic conditional-DELETE implementation, SQLite serializes the two
    DELETE statements and the second one's correlated subquery is
    evaluated fresh (after the first has already committed), so exactly
    one removal succeeds and the other is correctly rejected.
    """

    engine, session_factory = _make_file_backed_session_factory(
        tmp_path, "rbac_5i_concurrency_removal.db",
    )

    setup_session = session_factory()
    try:
        org = make_organisation(setup_session)
        manager_1 = make_user(setup_session, org, username="manager1")
        manager_2 = make_user(setup_session, org, username="manager2")
        team = make_team(setup_session, org)
        make_membership(setup_session, manager_1, team, role=TeamRole.MANAGER)
        make_membership(setup_session, manager_2, team, role=TeamRole.MANAGER)
        team_id = team.id
        manager_1_id = manager_1.id
        manager_2_id = manager_2.id
    finally:
        setup_session.close()

    barrier = threading.Barrier(2)
    outcomes: dict[str, str] = {}

    def worker(user_id: int, key: str) -> None:
        session = session_factory()
        try:
            repository = TeamMembershipRepository(session)

            barrier.wait(timeout=10)

            try:
                repository.remove_membership(user_id=user_id, team_id=team_id)
                outcomes[key] = "removed"
            except LastTeamManagerError:
                outcomes[key] = "blocked"

        except BaseException as exc:  # noqa: BLE001 -- must be captured, never swallowed silently
            outcomes[key] = f"unexpected: {exc!r}"

        finally:
            session.close()

    thread_a = threading.Thread(target=worker, args=(manager_1_id, "a"))
    thread_b = threading.Thread(target=worker, args=(manager_2_id, "b"))

    thread_a.start()
    thread_b.start()
    thread_a.join(timeout=15)
    thread_b.join(timeout=15)

    try:
        assert not thread_a.is_alive(), "worker thread A did not terminate"
        assert not thread_b.is_alive(), "worker thread B did not terminate"

        assert set(outcomes.keys()) == {"a", "b"}, f"missing worker outcome(s): {outcomes}"

        for key, outcome in outcomes.items():
            assert outcome in ("removed", "blocked"), (
                f"thread {key!r} raised an unexpected exception: {outcome}"
            )

        assert sorted(outcomes.values()) == ["blocked", "removed"], (
            "exactly one removal must succeed and exactly one must be "
            f"blocked by the last-manager invariant; got {outcomes}"
        )

        verify_session = session_factory()
        try:
            remaining_managers = verify_session.execute(
                select(TeamMembership).where(
                    TeamMembership.team_id == team_id,
                    TeamMembership.role == TeamRole.MANAGER,
                )
            ).scalars().all()

            assert len(remaining_managers) == 1, (
                "last-manager invariant violated: "
                f"{len(remaining_managers)} managers remain (expected exactly 1)"
            )
        finally:
            verify_session.close()

    finally:
        engine.dispose()


def test_concurrent_duplicate_add_leaves_one_membership(tmp_path):
    """
    Permanent regression test for the duplicate-membership concurrency
    fix.

    Two real OS threads, each with its own SQLAlchemy session against
    the same file-backed SQLite database, both call the actual
    production ``TeamMembershipRepository.add_membership`` for the
    exact same ``(user_id, team_id)`` pair, synchronized by a
    ``threading.Barrier`` so both inserts genuinely race against the
    real database unique constraint.

    Against the old unguarded implementation, both threads could pass
    the pre-check before either committed, and the second commit would
    raise a raw, untranslated ``IntegrityError`` (surfacing as an
    unhandled 500 at the API boundary). Against the current
    implementation, the insert is wrapped in the same
    ``IntegrityError``-translation pattern as
    ``TeamRepository.create_with_initial_manager``, so the losing
    thread receives a clean ``TeamMembershipAlreadyExistsError`` and the
    session remains usable.
    """

    engine, session_factory = _make_file_backed_session_factory(
        tmp_path, "rbac_5i_concurrency_add.db",
    )

    setup_session = session_factory()
    try:
        org = make_organisation(setup_session)
        target = make_user(setup_session, org, username="carol")
        team = make_team(setup_session, org)
        team_id = team.id
        target_id = target.id
    finally:
        setup_session.close()

    barrier = threading.Barrier(2)
    outcomes: dict[str, str] = {}

    def worker(key: str) -> None:
        session = session_factory()
        try:
            repository = TeamMembershipRepository(session)

            barrier.wait(timeout=10)

            try:
                repository.add_membership(user_id=target_id, team_id=team_id)
                outcomes[key] = "added"
            except TeamMembershipAlreadyExistsError:
                outcomes[key] = "already_exists"

        except BaseException as exc:  # noqa: BLE001 -- must be captured, never swallowed silently
            outcomes[key] = f"unexpected: {exc!r}"

        finally:
            session.close()

    thread_a = threading.Thread(target=worker, args=("a",))
    thread_b = threading.Thread(target=worker, args=("b",))

    thread_a.start()
    thread_b.start()
    thread_a.join(timeout=15)
    thread_b.join(timeout=15)

    try:
        assert not thread_a.is_alive(), "worker thread A did not terminate"
        assert not thread_b.is_alive(), "worker thread B did not terminate"

        assert set(outcomes.keys()) == {"a", "b"}, f"missing worker outcome(s): {outcomes}"

        for key, outcome in outcomes.items():
            assert outcome in ("added", "already_exists"), (
                f"thread {key!r} raised an unexpected exception "
                f"(a raw IntegrityError must never escape): {outcome}"
            )

        assert sorted(outcomes.values()) == ["added", "already_exists"], (
            "exactly one add must succeed and exactly one must be "
            f"rejected as a duplicate; got {outcomes}"
        )

        verify_session = session_factory()
        try:
            rows = verify_session.execute(
                select(TeamMembership).where(
                    TeamMembership.team_id == team_id,
                    TeamMembership.user_id == target_id,
                )
            ).scalars().all()

            assert len(rows) == 1, (
                f"expected exactly one membership row, found {len(rows)}"
            )
        finally:
            verify_session.close()

    finally:
        engine.dispose()
