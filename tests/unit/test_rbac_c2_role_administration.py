"""
Executable specification for RBAC Phase C.2: organisation role
administration (``POST /users/{user_id}/role``).

Covers, with no live Qdrant connection and an isolated in-memory SQLite
database (never the real dev ``astra_study.db``):

- ``UserService.update_role``: only ``OrgRole.ADMIN`` may call it; the
  caller cannot target themselves; the target must belong to the
  caller's own organisation (enumeration-safe otherwise); only
  ``MEMBER -> MANAGER`` and ``MANAGER -> ADMIN`` are permitted, every
  other requested transition -- including both same-role transitions and
  every downward transition -- is rejected;
- the minimum-one-ADMIN invariant is structurally enforced (an existing
  ADMIN can never be demoted through this endpoint, since
  ``(OrgRole.ADMIN, *)`` never appears in the allowed-transition set);
- a role change is visible on the very next request's ``AccessContext``,
  with no extra wiring (``get_access_context`` rebuilds ``role`` fresh
  from the ``User`` row on every call);
- ``RoleUpdateRequest``'s Pydantic-level validation (rejects unknown
  role strings, rejects unexpected fields via ``extra="forbid"``).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.enums.organisation import OrgRole
from app.exceptions.user import (
    InvalidRoleTransitionError,
    RoleAdministrationForbiddenError,
    SelfRoleModificationForbiddenError,
    UserNotFoundError,
)
from app.schemas.user import RoleUpdateRequest

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.organisation import Organisation
from app.models.user import User
from app.repositories.org_manager_team import OrgManagerTeamRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.repositories.user import UserRepository
from app.retrieval.access import AccessContext
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


def build_access(db, user: User) -> AccessContext:
    """Mirrors get_access_context's real logic -- genuine team-membership
    and jurisdiction lookups, never fabricated tuples."""

    team_ids = TeamMembershipRepository(db).get_team_ids_by_user_id(user.id)
    jurisdiction_team_ids = OrgManagerTeamRepository(db).get_team_ids_by_user_id(user.id)
    return AccessContext(
        user_id=user.id,
        organisation_id=user.organisation_id,
        team_ids=tuple(team_ids),
        jurisdiction_team_ids=tuple(jurisdiction_team_ids),
        role=user.role,
    )


def make_service(db) -> UserService:
    return UserService(
        user_repository=UserRepository(db),
        team_membership_repository=TeamMembershipRepository(db),
        org_manager_team_repository=OrgManagerTeamRepository(db),
    )


def refetch(db, user: User) -> User:
    """Re-fetch a user row fresh from the database -- never trust a
    stale in-memory reference when asserting post-mutation state."""

    return UserRepository(db).get_by_id(user.id)


# --------------------------------------------------------------------------- #
# A. Valid transitions
# --------------------------------------------------------------------------- #


def test_admin_promotes_member_to_manager(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    member = make_user(db, org, username="member", role=OrgRole.MEMBER)
    service = make_service(db)

    result = service.update_role(
        access=build_access(db, admin),
        target_user_id=member.id,
        requested_role=OrgRole.MANAGER,
    )

    assert result.role == OrgRole.MANAGER
    assert refetch(db, member).role == OrgRole.MANAGER


def test_admin_promotes_manager_to_admin(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="manager", role=OrgRole.MANAGER)
    service = make_service(db)

    result = service.update_role(
        access=build_access(db, admin),
        target_user_id=manager.id,
        requested_role=OrgRole.ADMIN,
    )

    assert result.role == OrgRole.ADMIN
    assert refetch(db, manager).role == OrgRole.ADMIN


# --------------------------------------------------------------------------- #
# B. Invalid transitions
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("current_role", "requested_role"),
    [
        pytest.param(OrgRole.MEMBER, OrgRole.ADMIN, id="member_to_admin"),
        pytest.param(OrgRole.MANAGER, OrgRole.MEMBER, id="manager_to_member"),
        pytest.param(OrgRole.MANAGER, OrgRole.MANAGER, id="manager_to_manager"),
        pytest.param(OrgRole.ADMIN, OrgRole.MEMBER, id="admin_to_member"),
        pytest.param(OrgRole.ADMIN, OrgRole.MANAGER, id="admin_to_manager"),
        pytest.param(OrgRole.ADMIN, OrgRole.ADMIN, id="admin_to_admin"),
        pytest.param(OrgRole.MEMBER, OrgRole.MEMBER, id="member_to_member"),
    ],
)
def test_invalid_transitions_are_rejected(db, current_role, requested_role):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    target = make_user(db, org, username="target", role=current_role)
    service = make_service(db)

    with pytest.raises(InvalidRoleTransitionError):
        service.update_role(
            access=build_access(db, admin),
            target_user_id=target.id,
            requested_role=requested_role,
        )

    # The target's role must be untouched by a rejected transition.
    assert refetch(db, target).role == current_role


# --------------------------------------------------------------------------- #
# C. Authorization
# --------------------------------------------------------------------------- #


def test_member_caller_cannot_modify_roles(db):
    org = make_organisation(db)
    caller = make_user(db, org, username="caller", role=OrgRole.MEMBER)
    target = make_user(db, org, username="target", role=OrgRole.MEMBER)
    service = make_service(db)

    with pytest.raises(RoleAdministrationForbiddenError):
        service.update_role(
            access=build_access(db, caller),
            target_user_id=target.id,
            requested_role=OrgRole.MANAGER,
        )

    assert refetch(db, target).role == OrgRole.MEMBER


def test_manager_caller_cannot_modify_roles(db):
    org = make_organisation(db)
    caller = make_user(db, org, username="caller", role=OrgRole.MANAGER)
    target = make_user(db, org, username="target", role=OrgRole.MEMBER)
    service = make_service(db)

    with pytest.raises(RoleAdministrationForbiddenError):
        service.update_role(
            access=build_access(db, caller),
            target_user_id=target.id,
            requested_role=OrgRole.MANAGER,
        )

    assert refetch(db, target).role == OrgRole.MEMBER


def test_admin_caller_can_modify_roles(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    target = make_user(db, org, username="target", role=OrgRole.MEMBER)
    service = make_service(db)

    result = service.update_role(
        access=build_access(db, admin),
        target_user_id=target.id,
        requested_role=OrgRole.MANAGER,
    )

    assert result.role == OrgRole.MANAGER


def test_admin_cannot_modify_own_role(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    service = make_service(db)

    with pytest.raises(SelfRoleModificationForbiddenError):
        service.update_role(
            access=build_access(db, admin),
            target_user_id=admin.id,
            requested_role=OrgRole.MANAGER,
        )

    assert refetch(db, admin).role == OrgRole.ADMIN


def test_cross_organisation_target_returns_user_not_found(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    admin = make_user(db, org_a, username="admin", role=OrgRole.ADMIN)
    outsider = make_user(db, org_b, username="outsider", role=OrgRole.MEMBER)
    service = make_service(db)

    with pytest.raises(UserNotFoundError):
        service.update_role(
            access=build_access(db, admin),
            target_user_id=outsider.id,
            requested_role=OrgRole.MANAGER,
        )

    assert refetch(db, outsider).role == OrgRole.MEMBER


def test_missing_target_returns_user_not_found(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    service = make_service(db)

    with pytest.raises(UserNotFoundError):
        service.update_role(
            access=build_access(db, admin),
            target_user_id=999999,
            requested_role=OrgRole.MANAGER,
        )


# --------------------------------------------------------------------------- #
# D. ADMIN invariant -- an existing ADMIN can never be demoted or
# self-modified through this endpoint, so the organisation's ADMIN count
# can never be reduced by any call this service exposes.
# --------------------------------------------------------------------------- #


def test_admin_to_member_rejected_preserves_admin_count(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    other_admin = make_user(db, org, username="other_admin", role=OrgRole.ADMIN)
    service = make_service(db)

    with pytest.raises(InvalidRoleTransitionError):
        service.update_role(
            access=build_access(db, admin),
            target_user_id=other_admin.id,
            requested_role=OrgRole.MEMBER,
        )

    assert refetch(db, other_admin).role == OrgRole.ADMIN


def test_admin_to_manager_rejected_preserves_admin_count(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    other_admin = make_user(db, org, username="other_admin", role=OrgRole.ADMIN)
    service = make_service(db)

    with pytest.raises(InvalidRoleTransitionError):
        service.update_role(
            access=build_access(db, admin),
            target_user_id=other_admin.id,
            requested_role=OrgRole.MANAGER,
        )

    assert refetch(db, other_admin).role == OrgRole.ADMIN


# --------------------------------------------------------------------------- #
# E. Downstream AccessContext -- the new role is visible on the very
# next request, with no extra cache/refresh wiring.
# --------------------------------------------------------------------------- #


def test_access_context_reflects_manager_after_member_to_manager_promotion(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    member = make_user(db, org, username="member", role=OrgRole.MEMBER)
    service = make_service(db)

    service.update_role(
        access=build_access(db, admin),
        target_user_id=member.id,
        requested_role=OrgRole.MANAGER,
    )

    next_request_access = build_access(db, refetch(db, member))

    assert next_request_access.role == OrgRole.MANAGER


def test_access_context_reflects_admin_after_manager_to_admin_promotion(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="admin", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="manager", role=OrgRole.MANAGER)
    service = make_service(db)

    service.update_role(
        access=build_access(db, admin),
        target_user_id=manager.id,
        requested_role=OrgRole.ADMIN,
    )

    next_request_access = build_access(db, refetch(db, manager))

    assert next_request_access.role == OrgRole.ADMIN


# --------------------------------------------------------------------------- #
# F. Schema-level validation
# --------------------------------------------------------------------------- #


def test_role_update_request_rejects_invalid_role_value():
    with pytest.raises(ValidationError):
        RoleUpdateRequest(role="owner")


def test_role_update_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        RoleUpdateRequest(role="manager", organisation_id=1)


def test_role_update_request_accepts_valid_role():
    request = RoleUpdateRequest(role="manager")

    assert request.role == OrgRole.MANAGER
