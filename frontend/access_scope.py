from __future__ import annotations

from frontend.models.user import TeamMembership, User

# Mirrors app/enums/document.py::DocumentAccessScope's exact string values --
# the backend upload endpoint expects these literal strings on the
# ``access_scope`` form field.
INDIVIDUAL = "individual"
TEAM = "team"
ORGANISATION = "organisation"

# Mirrors app/enums/organisation.py::OrgRole.ADMIN's exact string value.
ADMIN_ROLE = "admin"


def selectable_teams(
    user: User | None,
) -> list[TeamMembership]:
    """
    Teams the given user may upload a TEAM-scoped document to.

    Deliberately sourced from ``user.teams`` (actual ``TeamMembership``
    rows) only -- never from the organisation-wide team list (``GET
    /teams``, which carries no membership information) and never from
    ``user.managed_teams`` (Org Manager jurisdiction, which does not
    grant TEAM document creation). Both ``TeamRole.MEMBER`` and
    ``TeamRole.MANAGER`` memberships are valid.
    """

    if user is None:
        return []

    return list(user.teams)


def can_select_organisation_scope(
    user: User | None,
) -> bool:
    """
    True only for ``OrgRole.ADMIN``. Neither ``OrgRole.MANAGER`` nor Org
    Manager jurisdiction (``user.managed_teams``) grants ORGANISATION
    document creation.
    """

    if user is None:
        return False

    return user.role == ADMIN_ROLE


def validate_upload_scope(
    *,
    scope: str,
    team_id: int | None,
    user: User | None,
) -> str | None:
    """
    UX-level validation only -- the backend remains the authoritative
    authorization layer and is expected to reject anything this misses.

    Returns an error message if ``scope``/``team_id`` is not a valid
    selection for ``user``, or ``None`` if it is.
    """

    if scope == INDIVIDUAL:
        return None

    if scope == TEAM:

        if team_id is None:
            return "Select a team for a team-scoped upload."

        if not any(
            team.team_id == team_id
            for team in selectable_teams(user)
        ):
            return "You can only upload to a team you are a member of."

        return None

    if scope == ORGANISATION:

        if not can_select_organisation_scope(user):
            return (
                "Only organisation admins can upload "
                "organisation-scoped documents."
            )

        return None

    return f"Unknown access scope: {scope!r}"
