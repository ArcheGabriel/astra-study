"""
Domain models for the reranking subsystem.

These models represent the output of the retrieval stage after cross-encoder reranking has been applied.

The reranker never modifies the retrieved document. Instead,
it wraps the retrieved document with a reranker score while
preserving the original retrieval score.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, SupportsIndex
from collections.abc import Iterator

from app.search.hybrid.models import HybridSearchResult


@dataclass(slots=True)
class RerankedChunk:
    """
    Represents a single reranked retrieval result.

    Attributes
    ----------
    result:
        Original retrieval result returned by Hybrid Search.

    reranker_score:
        Cross Encoder relevance score.

    rank:
        Final ranking after reranking.
    """

    result: HybridSearchResult

    reranker_score: float

    rank: int


@dataclass(slots=True, frozen=True)
class RerankingResult:
    """
    Represents the complete output of the reranking stage.

    Attributes
    ----------
    query:
        User query.

    total_candidates:
        Number of retrieved chunks before reranking.

    returned_candidates:
        Number of chunks returned after reranking.

    results:
        Ordered reranked chunks.
    """

    query: str

    total_candidates: int

    returned_candidates: int

    results: Sequence[RerankedChunk] = field(default_factory=tuple)

    @property
    def best_match(self) -> RerankedChunk | None:
        """
        Returns the highest ranked chunk.
        """

        if not self.results:
            return None

        return self.results[0]

    @property
    def reranker_scores(self) -> list[float]:
        """
        Returns all reranker scores.
        """

        return [
            result.reranker_score
            for result in self.results
        ]

    @property
    def retrieval_scores(self) -> list[float]:
        """
        Returns the original retrieval scores.
        """

        return [
            result.result.score
            for result in self.results
        ]

    def top_k(
        self,
        k: int,
    ) -> tuple[RerankedChunk, ...]:
        """
        Returns the top-k reranked chunks.

        Parameters
        ----------
        k:
            Number of chunks to return.
        """

        return tuple(self.results[:k])

    def __len__(self) -> int:
        return len(self.results)

    def __iter__(self) -> Iterator[RerankedChunk]:
        return iter(self.results)

    def __getitem__(
        self,
        item: SupportsIndex | slice,
    ) -> RerankedChunk | Sequence[RerankedChunk]:
        return self.results[item]