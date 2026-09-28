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
class ManagedTeam:
    """
    One team the user holds Org Manager jurisdiction over.

    Deliberately carries no ``role`` -- jurisdiction is a single binary
    state, structurally independent of ``TeamMembership``/``TeamRole``.
    Never conflate this with ``TeamMembership``: a user may hold
    jurisdiction over a team without being one of its members, and vice
    versa.
    """

    team_id: int
    team_name: str

    @classmethod
    def from_dict(cls, data: dict) -> "ManagedTeam":
        return cls(
            team_id=data["team_id"],
            team_name=data["team_name"],
        )


@dataclass(slots=True)
class UserSearchResult:
    """
    One user returned by ``GET /users?q=`` (organisation-scoped lookup,
    used to resolve a ``user_id`` for team membership management).
    """

    id: int
    username: str
    email: str

    @classmethod
    def from_dict(cls, data: dict) -> "UserSearchResult":
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
        )


@dataclass(slots=True)
class User:
    id: int
    username: str
    email: str
    organisation_id: int | None = None
    role: str | None = None
    teams: list[TeamMembership] = field(default_factory=list)
    managed_teams: list[ManagedTeam] = field(default_factory=list)

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
            managed_teams=[
                ManagedTeam.from_dict(team)
                for team in data.get("managed_teams", [])
            ],
        )
