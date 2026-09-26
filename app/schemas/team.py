from pydantic import BaseModel, ConfigDict, Field, field_validator


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
