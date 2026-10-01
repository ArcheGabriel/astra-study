"""
Executable specification for ``frontend.role_management.available_action``
(RBAC Phase C.2) -- the pure helper deciding which single promotion
action, if any, the role-administration UI offers for a search result.

This is a UX-only safeguard; the backend
(``UserService.update_role``'s ``_ALLOWED_ROLE_TRANSITIONS`` set plus its
``SelfRoleModificationForbiddenError`` check) remains the sole authority
and independently re-enforces the identical rules on every
``POST /users/{user_id}/role`` request. These tests exist to lock in
that the frontend gate never offers a demotion, a ``MEMBER -> ADMIN``
shortcut, or a self-targeting action -- mirroring
``tests/frontend/test_org_manager_authorization.py``'s structure for the
analogous backend-authoritative UX gate.
"""

from __future__ import annotations

from frontend.role_management import (
    ADMIN_ROLE,
    MANAGER_ROLE,
    MEMBER_ROLE,
    PROMOTE_TO_ADMIN,
    PROMOTE_TO_MANAGER,
    available_action,
)


def test_member_target_offers_promote_to_manager():
    assert available_action(MEMBER_ROLE, is_self=False) == PROMOTE_TO_MANAGER


def test_manager_target_offers_promote_to_admin():
    assert available_action(MANAGER_ROLE, is_self=False) == PROMOTE_TO_ADMIN


def test_admin_target_offers_no_action():
    assert available_action(ADMIN_ROLE, is_self=False) is None


def test_self_target_offers_no_action():
    assert available_action(MANAGER_ROLE, is_self=True) is None


def test_self_member_offers_no_action():
    assert available_action(MEMBER_ROLE, is_self=True) is None


def test_self_manager_offers_no_action():
    assert available_action(MANAGER_ROLE, is_self=True) is None


def test_self_admin_offers_no_action():
    assert available_action(ADMIN_ROLE, is_self=True) is None


def test_no_member_to_admin_shortcut_exists():
    """
    A MEMBER target must never be offered a direct path to ADMIN --
    only the single-step MEMBER -> MANAGER action, matching the
    backend's allowed-transition set exactly.
    """

    assert available_action(MEMBER_ROLE, is_self=False) != PROMOTE_TO_ADMIN


def test_no_demotion_action_exists_for_any_role():
    """
    There is no backend demotion operation (MANAGER -> MEMBER,
    ADMIN -> MANAGER, ADMIN -> MEMBER all forbidden), so the helper must
    never return anything other than the two upward promotion labels or
    None for any (role, is_self) combination.
    """

    for role in (MEMBER_ROLE, MANAGER_ROLE, ADMIN_ROLE):
        for is_self in (True, False):
            action = available_action(role, is_self=is_self)
            assert action in (None, PROMOTE_TO_MANAGER, PROMOTE_TO_ADMIN)
