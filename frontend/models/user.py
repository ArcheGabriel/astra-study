from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class User:
    id: int
    username: str
    email: str

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
        )