"""
Abstract interface for all rerankers.

Every reranker implementation (CrossEncoder, Cohere, Jina AI, Voyage AI, OpenAI, etc.) must inherit from BaseReranker.

The purpose of this abstraction is to decouple the rest of the application from any specific reranking implementation.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.reranking.models import RerankingResult
from app.search.hybrid.models import HybridSearchResult


class BaseReranker(ABC):
    """
    Abstract base class for reranking implementations.
    """

    @abstractmethod
    def rerank(
        self,
        *,
        query: str,
        candidates: list[HybridSearchResult],
        top_k: int,
    ) -> RerankingResult:
        """
        Rerank retrieved candidates.

        Parameters
        ----------
        query:
            User query.

        candidates:
            Retrieved candidates from Hybrid Search.

        top_k:
            Number of results to return after reranking.

        Returns
        -------
        RerankingResult

        Raises
        ------
        RerankerError
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Returns the underlying reranker model name.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def device(self) -> str:
        """
        Returns the execution device.

        Example
        -------
        cpu
        cuda
        cuda:0
        mps
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def batch_size(self) -> int:
        """
        Batch size used for inference.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def max_length(self) -> int:
        """
        Maximum sequence length accepted by the reranker.
        """
        raise NotImplementedError

    @property
    def is_gpu_enabled(self) -> bool:
        """
        Returns whether GPU acceleration is enabled.
        """

        return (
            self.device.startswith("cuda")
            or self.device == "mps"
        )

    def __call__(
        self,
        *,
        query: str,
        candidates: list[HybridSearchResult],
        top_k: int,
    ) -> RerankingResult:
        """
        Allows the reranker instance to be invoked like a function.

        Example
        -------
        result = reranker(
            query=query,
            candidates=docs,
            top_k=5,
        )
        """

        return self.rerank(
            query=query,
            candidates=candidates,
            top_k=top_k,
        )