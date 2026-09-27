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
