"""
Service layer for document reranking.

The service is responsible for:
- Managing the reranker implementation
- Validating requests
- Delegating inference
- Logging execution
- Returning structured reranking results

The rest of the application should depend on this service instead of directly interacting with the CrossEncoder.
"""

from __future__ import annotations

import logging
import time

from app.reranking.base import BaseReranker
from app.reranking.cross_encoder import CrossEncoderReranker
from app.reranking.models import RerankingResult
from app.search.hybrid.models import HybridSearchResult

logger = logging.getLogger(__name__)


class RerankingService:
    """
    Public service for document reranking.

    The service hides the concrete reranker implementation from the rest of the application.

    Example
    -------
    >>> service = RerankingService()
    >>> result = service.rerank(
    ...     query=query,
    ...     candidates=candidates,
    ...     top_k=5,
    ... )
    """

    def __init__(
        self,
        reranker: BaseReranker | None = None,
    ) -> None:
        """
        Initialize the reranking service.

        Parameters
        ----------
        reranker:
            Optional reranker implementation.

            If provided, it will be used directly.
            Otherwise, the default CrossEncoderReranker will be lazily initialized on first use.
        """

        self._reranker = reranker

    @property
    def reranker(self) -> BaseReranker:
        """
        Returns the active reranker.

        The default CrossEncoderReranker is created only
        when first accessed, avoiding model loading during
        application startup.
        """

        if self._reranker is None:

            logger.info(
                "Initializing default CrossEncoderReranker."
            )

            self._reranker = CrossEncoderReranker()

        return self._reranker

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
            Retrieved hybrid search candidates.

        top_k:
            Number of documents to return.

        Returns
        -------
        RerankingResult
        """

        logger.info(
            "Starting reranking using '%s'.",
            self.reranker.model_name,
        )

        start = time.perf_counter()

        result = self.reranker.rerank(
            query=query,
            candidates=candidates,
            top_k=top_k,
        )

        elapsed = time.perf_counter() - start

        logger.info(
            (
                "Reranking completed in %.3f seconds. "
                "%d/%d candidates returned."
            ),
            elapsed,
            result.returned_candidates,
            result.total_candidates,
        )

        return result

    def __call__(
        self,
        *,
        query: str,
        candidates: list[HybridSearchResult],
        top_k: int,
    ) -> RerankingResult:
        """
        Callable wrapper.

        Example
        -------
        >>> result = service(
        ...     query=query,
        ...     candidates=candidates,
        ...     top_k=5,
        ... )
        """

        return self.rerank(
            query=query,
            candidates=candidates,
            top_k=top_k,
        )