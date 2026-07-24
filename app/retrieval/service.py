from __future__ import annotations

import logging
from time import perf_counter

from app.config.settings import settings
from app.retrieval.base import BaseRetrievalService
from app.retrieval.exceptions import (
    EmptyQueryError,
    NoRetrievalResultsError,
)
from app.retrieval.models import (
    RetrievedContext,
    RetrievalResult,
)
from app.reranking.service import RerankingService
from app.search.hybrid.service import HybridService

logger = logging.getLogger(__name__)


class RetrievalService(BaseRetrievalService):
    """
    Production Retrieval Orchestrator.

    Pipeline
    --------

    User Query
        │
        ▼
    Hybrid Search
        │
        ▼
    CrossEncoder Reranking
        │
        ▼
    RetrievedContext
        │
        ▼
    RetrievalResult

    This service is intentionally lightweight.
    It orchestrates the retrieval pipeline without
    containing search or reranking logic itself.
    """

    def __init__(
        self,
        hybrid_service: HybridService,
        reranking_service: RerankingService,
    ) -> None:
        self._hybrid_service = hybrid_service
        self._reranking_service = reranking_service

    def retrieve(
        self,
        *,
        query: str,
        user_id: int,
    ) -> RetrievalResult:
        """
        Execute the complete retrieval pipeline.
        """

        query = query.strip()

        if not query:
            raise EmptyQueryError(
                "Query cannot be empty."
            )

        logger.info(
            "Starting retrieval for query='%s' for user_id=%d.",
            query,
            user_id,
        )

        start = perf_counter()

        #
        # Hybrid Retrieval
        #
        hybrid_results = self._hybrid_service(
            query=query,
            user_id=user_id,
            limit=settings.QDRANT_HYBRID_CANDIDATE_LIMIT,
        )

        logger.info(
            "Hybrid retrieval returned %d candidates.",
            len(hybrid_results),
        )
        
        if not hybrid_results:
            latency = perf_counter() - start

            logger.info(
                "No contexts retrieved for query='%s'.",
                query,
            )

            return RetrievalResult(
                query=query,
                contexts=[],
                retrieval_latency=latency,
            )

        #
        # Cross Encoder Reranking
        #
        reranked = self._reranking_service(
            query=query,
            candidates=hybrid_results,
            top_k=settings.RETRIEVAL_TOP_K,
        )

        if not reranked.results:
            latency = perf_counter() - start

            logger.info(
                "All candidates filtered out during reranking."
            )

            return RetrievalResult(
                query=query,
                contexts=[],
                retrieval_latency=latency,
            )

        contexts: list[RetrievedContext] = []

        for reranked_chunk in reranked.results:

            result = reranked_chunk.result

            payload = result.payload or {}

            context = RetrievedContext(
                text=result.text,

                source=payload.get(
                    "document_name",
                    "Unknown Document",
                ),

                chunk_uuid=result.chunk_uuid,

                retrieval_score=result.score,

                reranker_score=reranked_chunk.reranker_score,

                page=payload.get(
                    "page_start",
                ),

                section=payload.get(
                    "section_title",
                ),
            )

            contexts.append(
                context,
            )

        latency = perf_counter() - start

        logger.info(
            (
                "Retrieval completed successfully. "
                "%d contexts returned in %.3f seconds."
            ),
            len(contexts),
            latency,
        )

        return RetrievalResult(
            query=query,
            contexts=contexts,
            retrieval_latency=latency,
        )

    def __call__(
        self,
        *,
        query: str,
        user_id: int,
    ) -> RetrievalResult:
        """
        Callable wrapper.
        """

        return self.retrieve(
            query=query,
            user_id=user_id,
        )