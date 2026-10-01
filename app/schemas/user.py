from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.enums.organisation import OrgRole
from app.enums.team import TeamRole


class UserCreate(BaseModel):
    """
    Schema used when a new user registers.
    """

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    model_config = ConfigDict(
        extra="forbid",
    )


class UserResponse(BaseModel):
    """
    Schema returned after a successful registration.
    """

    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class TeamMembershipResponse(BaseModel):
    """
    One of the requester's team memberships, as returned by
    ``GET /users/me``.
    """

    team_id: int
    team_name: str
    role: TeamRole

    model_config = ConfigDict(
        extra="forbid",
    )


class ManagedTeamResponse(BaseModel):
    """
    One team the requester holds Org Manager jurisdiction over (RBAC-5J),
    as returned by ``GET /users/me``.

    Deliberately carries no ``role`` field -- jurisdiction is a single
    binary state, structurally independent of ``TeamMembership``/
    ``TeamRole``. Kept as its own class, distinct from
    ``TeamMembershipResponse``, so ``teams`` (membership) and
    ``managed_teams`` (jurisdiction) can never be conflated: a user may
    independently appear in both, neither, or only one.
    """

    team_id: int
    team_name: str

    model_config = ConfigDict(
        extra="forbid",
    )


class RoleUpdateRequest(BaseModel):
    """
    Request body for ``POST /users/{user_id}/role`` (RBAC Phase C.2).

    ``role`` is the requested target ``OrgRole`` -- Pydantic's enum
    validation rejects any value outside ``member``/``manager``/``admin``
    before the handler ever runs. ``extra="forbid"`` means
    ``organisation_id`` (or any other field) can never be supplied by the
    client -- the target's organisation is always resolved server-side
    from the authenticated caller's own ``AccessContext``.
    """

    role: OrgRole

    model_config = ConfigDict(
        extra="forbid",
    )


class RoleManagementUserResponse(BaseModel):
    """
    Response for ``POST /users/{user_id}/role`` (RBAC Phase C.2).

    Deliberately minimal -- ``id``/``username``/``role`` only, no
    ``email``. A separate, purpose-built shape from ``UserResponse``
    (used by registration and ``GET /users?q=``) so that endpoint's
    response never needs to expose ``role`` to team-membership-management
    callers who have no need to see it.
    """

    id: int
    username: str
    role: OrgRole

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class RoleManagementUserSearchResult(BaseModel):
    """
    One user returned by ``GET /users/role-management?q=`` (RBAC Phase
    C.2, ADMIN-only organisation role-administration search).

    A separate, purpose-built contract from both ``UserResponse`` (used
    by ``GET /users?q=`` for team-membership search -- deliberately never
    given a ``role`` field, since that endpoint is reachable by any
    ``TeamRole.MANAGER``, not only an ``OrgRole.ADMIN``) and
    ``RoleManagementUserResponse`` (the ``POST /users/{user_id}/role``
    mutation response, which intentionally has no ``email``). This
    search response carries ``email`` (useful for disambiguating search
    results, matching ``UserResponse``'s existing precedent) and
    ``role`` (the whole reason this endpoint exists -- the
    role-administration UI needs to know a candidate's current
    ``OrgRole`` before it can decide which single promotion action, if
    any, to offer).
    """

    id: int
    username: str
    email: EmailStr
    role: OrgRole

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class UserProfileResponse(UserResponse):
    """
    ``GET /users/me`` response only -- extends ``UserResponse`` with RBAC
    context (organisation role, team memberships, and Org Manager
    jurisdiction).

    Deliberately kept as its own schema, never merged into ``UserResponse``
    itself: ``UserResponse`` is also the exact type ``POST /auth/register``
    returns and that ``TokenResponse.user`` embeds for
    ``POST /auth/login``/``POST /auth/token`` -- extending it in place
    would leak this profile data into those three responses and would
    break their existing ``UserResponse.model_validate(user)`` calls,
    since ``User`` has no ``teams`` attribute (only the lazy
    ``team_memberships`` relationship, which carries no team name).
    """

    organisation_id: int
    role: OrgRole
    teams: list[TeamMembershipResponse]
    managed_teams: list[ManagedTeamResponse]

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )