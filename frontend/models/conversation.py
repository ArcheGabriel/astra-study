from __future__ import annotations

from dataclasses import dataclass, field

from frontend.models.message import Message


@dataclass(slots=True)
class Citation:
    source: str
    page: int | None = None
    section: str | None = None
    score: float | None = None
    chunk_id: str | None = None
    source_type: str | None = None
    sheet_name: str | None = None
    heading_path: list[str] | None = None
    block_type: str | None = None
    provenance: list[dict] | None = None
    page_end: int | None = None
    parser: str | None = None
    excerpt: str | None = None
    answer_support: float | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Citation":
        import inspect
        fields = inspect.signature(cls).parameters
        filtered = {k: v for k, v in data.items() if k in fields}
        return cls(**filtered)


@dataclass(slots=True)
class Conversation:
    user_message: Message
    assistant_message: Message
    citations: list[Citation] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        return cls(
            user_message=Message.from_dict(data["user_message"]),
            assistant_message=Message.from_dict(data["assistant_message"]),
            citations=[
                Citation.from_dict(item)
                for item in data.get("citations", [])
            ],
        )
