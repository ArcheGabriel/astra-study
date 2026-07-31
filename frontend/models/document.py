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

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        return cls(
            id=data["id"],
            filename=data["filename"],
            content_type=data["content_type"],
            file_size=data["file_size"],
            status=data["status"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )