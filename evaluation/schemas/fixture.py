from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class EvaluationExample(BaseModel):
    """
    Represents a single evaluation example stored inside a fixture.
    """

    id: str = Field(
        description="Unique example identifier."
    )

    question: str = Field(
        min_length=1,
        description="Evaluation question.",
    )

    answer: str = Field(
        min_length=1,
        description="Expected reference answer.",
    )

    category: str = Field(
        default="general",
        description="Question category.",
    )

    difficulty: Literal[
        "easy",
        "medium",
        "hard",
    ] = "medium"


class EvaluationFixture(BaseModel):
    """
    Represents an evaluation fixture.
    """

    name: str

    description: str

    version: int = Field(
        ge=1,
    )

    document: str

    domain: str

    examples: list[EvaluationExample]