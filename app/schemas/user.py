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