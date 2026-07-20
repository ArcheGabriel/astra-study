from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class HybridSearchResult(BaseModel):
    """
    Represents one retrieved chunk from
    hybrid search.
    """

    chunk_uuid: UUID

    document_uuid: UUID

    score: float = Field(
        description="Hybrid relevance score."
    )

    text: str

    payload: dict


class HybridSearchResponse(BaseModel):
    """
    Collection of hybrid search results.
    """

    results: list[HybridSearchResult]