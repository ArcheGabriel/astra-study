from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Team:
    id: int
    organisation_id: int
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "Team":
        return cls(
            id=data["id"],
            organisation_id=data["organisation_id"],
            name=data["name"],
        )


@dataclass(slots=True)
class TeamRosterMember:
    """
    One member of a team roster, as returned by
    ``GET /teams/{team_id}/members``.

    ``role`` here is the member's ``TeamRole`` on this specific team --
    never to be confused with ``frontend.models.user.User.role``
    (``OrgRole``).
    """

    user_id: int
    username: str
    email: str
    role: str

    @classmethod
    def from_dict(cls, data: dict) -> "TeamRosterMember":
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            email=data["email"],
            role=data["role"],
        )
