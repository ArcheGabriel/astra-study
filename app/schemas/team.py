from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.enums.team import TeamRole


class TeamCreate(BaseModel):
    """
    Schema used when creating a team.

    Deliberately has no ``organisation_id`` field at all -- not merely
    unvalidated, structurally absent, so a client can never supply one
    under any name. The organisation is always taken from the
    authenticated requester's ``AccessContext``.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    model_config = ConfigDict(
        extra="forbid",
    )

    @field_validator("name", mode="before")
    @classmethod
    def _trim(cls, value: object) -> object:
        """
        Trim before length constraints are applied (mode="before" runs
        ahead of Field's min_length/max_length), so a whitespace-only
        name trims to "" and is rejected by min_length=1, and length is
        judged on the trimmed value rather than the raw input.
        """

        if isinstance(value, str):
            return value.strip()

        return value


class TeamResponse(BaseModel):
    """
    Schema returned for a team. Deliberately carries no membership/role
    information -- that belongs to a future team-membership milestone.
    """

    id: int

    organisation_id: int

    name: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class AddTeamMemberRequest(BaseModel):
    """
    Schema used to add an existing user to a team.

    Deliberately has no ``role`` field -- a newly added member always
    starts as ``TeamRole.MEMBER`` (see ``TeamMembershipRepository.add_membership``);
    promotion to ``TeamRole.MANAGER`` is a separate, explicit operation.
    No ``team_id``/``organisation_id`` field either -- ``team_id`` comes
    from the URL path and ``organisation_id`` is never client-supplied
    anywhere in this API, matching ``TeamCreate``'s existing precedent.
    """

    user_id: int

    model_config = ConfigDict(
        extra="forbid",
    )


class TeamMemberResponse(BaseModel):
    """
    Schema returned for one team membership after a direct
    membership-management operation (add/promote).

    Deliberately a distinct class from
    ``app.schemas.user.TeamMembershipResponse`` (the ``GET /users/me``
    shape, which carries ``team_name`` and no ``user_id``) -- this one
    is keyed the other way, by ``user_id`` within one ``team_id``, and
    carries no team name.
    """

    user_id: int

    team_id: int

    role: TeamRole

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class TeamRosterMemberResponse(BaseModel):
    """
    One member of a team roster, as returned by
    ``GET /teams/{team_id}/members``.

    Distinct from ``TeamMemberResponse`` (the result of a single
    add/promote mutation, keyed by ``user_id``/``team_id``/``role`` only,
    with no username/email) -- this is the read shape for browsing an
    entire team's membership, so it carries enough identity
    (``username``/``email``) to support a management UI deciding whom to
    promote/remove. This exposes nothing beyond what ``UserResponse``
    (and the organisation-scoped user-lookup endpoint) already exposes
    for the same users -- no password hash or other internal field.
    """

    user_id: int

    username: str

    email: EmailStr

    role: TeamRole

    model_config = ConfigDict(
        extra="forbid",
    )


class OrgManagerTeamResponse(BaseModel):
    """
    Schema returned for one Org Manager jurisdiction grant (RBAC-5J).

    Deliberately carries no ``role`` field -- jurisdiction is a single
    binary state, structurally independent of ``TeamMembership``/
    ``TeamRole``. Distinct from ``TeamMemberResponse`` (which represents
    operational team membership, not supervisory jurisdiction).
    """

    user_id: int

    team_id: int

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )
