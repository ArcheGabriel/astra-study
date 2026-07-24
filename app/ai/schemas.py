from __future__ import annotations

from dataclasses import dataclass, field

from app.generation.models import Citation


@dataclass(frozen=True, slots=True)
class AIResponse:
    """
    Response returned by the AI orchestration layer.

    This model is intentionally independent of the Generation layer
    and represents the data exposed by the AI pipeline to the rest
    of the application.
    """

    answer: str

    citations: list[Citation] = field(default_factory=list)