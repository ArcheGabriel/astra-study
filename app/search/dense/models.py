from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class DenseSearchResult:
    """
    Represents one result returned from the
    dense vector search.
    """

    chunk_uuid: UUID

    document_uuid: UUID

    score: float

    text: str

    payload: dict[str, Any] = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class DenseSearchResponse:
    """
    Represents the complete response returned
    from the dense search pipeline.
    """

    query: str

    results: list[DenseSearchResult] = field(
        default_factory=list,
    )

    retrieval_time_ms: float = 0.0

    @property
    def result_count(
        self,
    ) -> int:
        """
        Number of retrieved results.
        """

        return len(
            self.results,
        )

    @property
    def best_score(
        self,
    ) -> float:
        """
        Highest similarity score.
        """

        if not self.results:

            return 0.0

        return max(
            result.score
            for result in self.results
        )