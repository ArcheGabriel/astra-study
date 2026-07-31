from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Message:
    id: int
    role: str
    content: str
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            id=data["id"],
            role=data["role"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )