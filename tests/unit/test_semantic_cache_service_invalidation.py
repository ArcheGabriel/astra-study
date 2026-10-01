"""
Executable specification for the semantic-retrieval-cache invalidation
hooks (RBAC/C.3) wired into the services whose mutations change what a
user can retrieve: role administration, team membership, Org Manager
jurisdiction, document ingestion, and document deletion.

Each service takes an optional ``semantic_cache`` constructor parameter
(default ``None``, so every existing direct construction of these
services elsewhere in this project's test suite is unaffected) and, when
given one, invalidates the affected namespace after its mutation
commits. These tests inject a ``MagicMock`` cache and assert the exact
invalidation call -- never the cache's internal behavior, which is
covered by ``tests/unit/cache/test_semantic_retrieval_cache.py``.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.document import Document
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
from app.services.org_manager_team import OrgManagerTeamService
from app.services.team_membership import TeamMembershipService
from app.services.user import UserService


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


def make_user(db, organisation: Organisation, *, username: str, role: OrgRole = OrgRole.MEMBER) -> User:
    user = User(
        username=username, email=f"{username}@example.com", hashed_password="hashed",
        organisation_id=organisation.id, role=role,
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


def make_membership(db, *, user: User, team: Team, role: TeamRole = TeamRole.MANAGER) -> TeamMembership:
    membership = TeamMembership(user_id=user.id, team_id=team.id, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def build_access(db, user: User) -> AccessContext:
    team_ids = TeamMembershipRepository(db).get_team_ids_by_user_id(user.id)
    jurisdiction_team_ids = OrgManagerTeamRepository(db).get_team_ids_by_user_id(user.id)
    return AccessContext(
        user_id=user.id, organisation_id=user.organisation_id,
        team_ids=tuple(team_ids), jurisdiction_team_ids=tuple(jurisdiction_team_ids),
        role=user.role,
    )


# --------------------------------------------------------------------------- #
# Role administration (RBAC C.2) -> invalidate_user
# --------------------------------------------------------------------------- #


def test_role_promotion_invalidates_target_users_cache(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    member = make_user(db, org, username="member", role=OrgRole.MEMBER)

    cache = MagicMock()
    service = UserService(
        user_repository=UserRepository(db),
        team_membership_repository=TeamMembershipRepository(db),
        org_manager_team_repository=OrgManagerTeamRepository(db),
        semantic_cache=cache,
    )

    service.update_role(
        access=build_access(db, admin),
        target_user_id=member.id,
        requested_role=OrgRole.MANAGER,
    )

    cache.invalidate_user.assert_called_once_with(member.id)


def test_role_promotion_without_a_cache_does_not_raise(db):
    """No semantic_cache injected (the default) must behave exactly as
    before this feature -- no AttributeError, no behavior change."""
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    member = make_user(db, org, username="member", role=OrgRole.MEMBER)

    service = UserService(
        user_repository=UserRepository(db),
        team_membership_repository=TeamMembershipRepository(db),
        org_manager_team_repository=OrgManagerTeamRepository(db),
    )

    result = service.update_role(
        access=build_access(db, admin),
        target_user_id=member.id,
        requested_role=OrgRole.MANAGER,
    )

    assert result.role == OrgRole.MANAGER


def test_cache_invalidation_failure_does_not_fail_an_otherwise_successful_role_change(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    member = make_user(db, org, username="member", role=OrgRole.MEMBER)

    cache = MagicMock()
    cache.invalidate_user.side_effect = RuntimeError("boom")

    service = UserService(
        user_repository=UserRepository(db),
        team_membership_repository=TeamMembershipRepository(db),
        org_manager_team_repository=OrgManagerTeamRepository(db),
        semantic_cache=cache,
    )

    result = service.update_role(
        access=build_access(db, admin),
        target_user_id=member.id,
        requested_role=OrgRole.MANAGER,
    )

    assert result.role == OrgRole.MANAGER


# --------------------------------------------------------------------------- #
# Team membership management (RBAC-5I) -> invalidate_user
# --------------------------------------------------------------------------- #


def test_add_member_invalidates_the_added_users_cache(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    target = make_user(db, org, username="target")
    team = make_team(db, org)
    make_membership(db, user=manager, team=team, role=TeamRole.MANAGER)

    cache = MagicMock()
    service = TeamMembershipService(
        team_membership_repository=TeamMembershipRepository(db),
        team_repository=TeamRepository(db),
        user_repository=UserRepository(db),
        semantic_cache=cache,
    )

    service.add_member(access=build_access(db, manager), team_id=team.id, user_id=target.id)

    cache.invalidate_user.assert_called_once_with(target.id)


def test_promote_member_invalidates_the_promoted_users_cache(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    target = make_user(db, org, username="target")
    team = make_team(db, org)
    make_membership(db, user=manager, team=team, role=TeamRole.MANAGER)
    make_membership(db, user=target, team=team, role=TeamRole.MEMBER)

    cache = MagicMock()
    service = TeamMembershipService(
        team_membership_repository=TeamMembershipRepository(db),
        team_repository=TeamRepository(db),
        user_repository=UserRepository(db),
        semantic_cache=cache,
    )

    service.promote_member(access=build_access(db, manager), team_id=team.id, user_id=target.id)

    cache.invalidate_user.assert_called_once_with(target.id)


def test_remove_member_invalidates_the_removed_users_cache(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="manager")
    target = make_user(db, org, username="target")
    team = make_team(db, org)
    make_membership(db, user=manager, team=team, role=TeamRole.MANAGER)
    make_membership(db, user=target, team=team, role=TeamRole.MEMBER)

    cache = MagicMock()
    service = TeamMembershipService(
        team_membership_repository=TeamMembershipRepository(db),
        team_repository=TeamRepository(db),
        user_repository=UserRepository(db),
        semantic_cache=cache,
    )

    service.remove_member(access=build_access(db, manager), team_id=team.id, user_id=target.id)

    cache.invalidate_user.assert_called_once_with(target.id)


# --------------------------------------------------------------------------- #
# Org Manager jurisdiction (RBAC-5J) -> invalidate_user
# --------------------------------------------------------------------------- #


def test_grant_jurisdiction_invalidates_the_managers_cache(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="manager", role=OrgRole.MANAGER)
    team = make_team(db, org)

    cache = MagicMock()
    service = OrgManagerTeamService(
        org_manager_team_repository=OrgManagerTeamRepository(db),
        team_repository=TeamRepository(db),
        user_repository=UserRepository(db),
        semantic_cache=cache,
    )

    service.grant_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)

    cache.invalidate_user.assert_called_once_with(manager.id)


def test_revoke_jurisdiction_invalidates_the_managers_cache(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="manager", role=OrgRole.MANAGER)
    team = make_team(db, org)
    OrgManagerTeamRepository(db).grant(user_id=manager.id, team_id=team.id)

    cache = MagicMock()
    service = OrgManagerTeamService(
        org_manager_team_repository=OrgManagerTeamRepository(db),
        team_repository=TeamRepository(db),
        user_repository=UserRepository(db),
        semantic_cache=cache,
    )

    service.revoke_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)

    cache.invalidate_user.assert_called_once_with(manager.id)
