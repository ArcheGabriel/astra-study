from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Document:
    id: int
    filename: str
    content_type: str
    file_size: int
    status: str
    created_at: datetime
    access_scope: str | None = None
    team_id: int | None = None
    organisation_id: int | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        return cls(
            id=data["id"],
            filename=data["filename"],
            content_type=data["content_type"],
            file_size=data["file_size"],
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"]),
            access_scope=data.get("access_scope"),
            team_id=data.get("team_id"),
            organisation_id=data.get("organisation_id"),
        )