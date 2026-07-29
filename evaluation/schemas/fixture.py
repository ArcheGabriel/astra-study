from __future__ import annotations

from pydantic import BaseModel, Field


class EvaluationExample(BaseModel):
    """
    Represents a single evaluation question.
    """

    id: str = Field(
        description="Unique example identifier.",
    )

    question: str = Field(
        min_length=1,
        description="Evaluation question.",
    )


class EvaluationFixture(BaseModel):
    """
    Represents a version-controlled evaluation fixture.
    """

    name: str

    version: int = Field(
        ge=1,
    )

    document: str

    domain: str

    examples: list[EvaluationExample]