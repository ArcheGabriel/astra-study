from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TeamMembership:
    team_id: int
    team_name: str
    role: str

    @classmethod
    def from_dict(cls, data: dict) -> "TeamMembership":
        return cls(
            team_id=data["team_id"],
            team_name=data["team_name"],
            role=data["role"],
        )


@dataclass(slots=True)
class User:
    id: int
    username: str
    email: str
    organisation_id: int | None = None
    role: str | None = None
    teams: list[TeamMembership] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            organisation_id=data.get("organisation_id"),
            role=data.get("role"),
            teams=[
                TeamMembership.from_dict(team)
                for team in data.get("teams", [])
            ],
        )
