from __future__ import annotations

from dataclasses import dataclass

from frontend.models.user import User


@dataclass(slots=True)
class TokenResponse:
    access_token: str
    refresh_token: str
    token_type: str
    user: User

    @classmethod
    def from_dict(cls, data: dict) -> "TokenResponse":
        return cls(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            token_type=data["token_type"],
            user=User.from_dict(data["user"]),
        )