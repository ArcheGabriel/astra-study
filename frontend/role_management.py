from __future__ import annotations

MEMBER_ROLE = "member"
MANAGER_ROLE = "manager"
ADMIN_ROLE = "admin"

PROMOTE_TO_MANAGER = "Promote to Manager"
PROMOTE_TO_ADMIN = "Promote to Admin"

# Maps each available action label to the role value to request via
# POST /users/{user_id}/role -- kept alongside available_action() so the
# UI never hand-constructs a role string itself.
ACTION_TARGET_ROLE = {
    PROMOTE_TO_MANAGER: MANAGER_ROLE,
    PROMOTE_TO_ADMIN: ADMIN_ROLE,
}


def available_action(
    target_role: str,
    is_self: bool,
) -> str | None:
    """
    The single promotion action, if any, an ADMIN may take on a search
    result (RBAC Phase C.2).

    A pure function -- no Streamlit, no network -- encoding exactly the
    backend's allowed-transition set
    (``app/services/user.py::_ALLOWED_ROLE_TRANSITIONS``:
    ``MEMBER -> MANAGER``, ``MANAGER -> ADMIN`` only) as a lookup, never
    a free-form role selector. This is a UX gate only -- the backend
    independently and authoritatively re-enforces the identical
    transition matrix, plus the self-modification check, on every
    ``POST /users/{user_id}/role`` request regardless of what this
    function returns.

    ``is_self`` always wins, regardless of ``target_role``: a caller may
    never promote themselves, mirroring the backend's
    ``SelfRoleModificationForbiddenError`` precedent exactly.
    """

    if is_self:
        return None

    if target_role == MEMBER_ROLE:
        return PROMOTE_TO_MANAGER

    if target_role == MANAGER_ROLE:
        return PROMOTE_TO_ADMIN

    return None
