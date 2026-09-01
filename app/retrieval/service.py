from __future__ import annotations

import logging
from time import perf_counter

from app.config.settings import settings
from app.retrieval.base import BaseRetrievalService
from app.retrieval.exceptions import EmptyQueryError
from app.retrieval.models import (
    RetrievedContext,
    RetrievalResult,
)
from app.reranking.service import RerankingService
from app.search.hybrid.service import HybridService

from langsmith import (
    traceable,
    get_current_run_tree,
)

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

    This service intentionally contains no search logic.
    It orchestrates the retrieval pipeline while delegating
    the heavy lifting to the Hybrid Search and Reranking
    services.
    """

    def __init__(
        self,
        hybrid_service: HybridService,
        reranking_service: RerankingService,
    ) -> None:
        self._hybrid_service = hybrid_service
        self._reranking_service = reranking_service

    @traceable(
        name="Build Retrieved Context",
        run_type="chain",
    )
    def _build_contexts(
        self,
        *,
        reranked,
    ) -> list[RetrievedContext]:
        """
        Convert reranked search results into RetrievedContext
        objects consumed by downstream generation.

        This span exists purely to make LangSmith traces
        easier to inspect.
        """

        contexts: list[RetrievedContext] = []

        for reranked_chunk in reranked.results:

            result = reranked_chunk.result

            payload = result.payload or {}

            contexts.append(
                RetrievedContext(
                    text=result.text,
                    source=payload.get(
                        "source",
                        payload.get("document_name",
                        "Unknown Document",
                        ),
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
                    source_type=payload.get("source_type"),
                    sheet_name=payload.get("sheet_name"),
                    heading_path=payload.get("heading_path") or None,
                    block_type=payload.get("block_type"),
                    provenance=payload.get("provenance") or None,
                )
            )

        logger.info(
            "Constructed %d retrieved contexts.",
            len(contexts),
        )

        return contexts

    @traceable(
        name="Document Retrieval",
        run_type="retriever",
    )
    def retrieve(
        self,
        *,
        query: str,
        user_id: int,
    ) -> RetrievalResult:
        """
        Execute the complete retrieval pipeline.

        Steps
        -----
        1. Validate query
        2. Hybrid Search
        3. CrossEncoder reranking
        4. Build RetrievedContext objects
        5. Return RetrievalResult
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

            run = get_current_run_tree()

            if run:
                run.metadata.update(
                    {
                        "query": query,
                        "contexts_returned": 0,
                        "retrieval_latency_ms": round(
                            latency * 1000,
                            2,
                        ),
                    }
                )

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

            run = get_current_run_tree()

            if run:
                run.metadata.update(
                    {
                        "query": query,
                        "contexts_returned": 0,
                        "retrieval_latency_ms": round(
                            latency * 1000,
                            2,
                        ),
                    }
                )

            logger.info(
                "All candidates filtered out during reranking."
            )

            return RetrievalResult(
                query=query,
                contexts=[],
                retrieval_latency=latency,
            )

        #
        # Build Retrieved Contexts
        #
        contexts = self._build_contexts(
            reranked=reranked,
        )

        latency = perf_counter() - start

        run = get_current_run_tree()

        if run:

            scores = [
                context.reranker_score
                for context in contexts
                if context.reranker_score is not None
            ]

            run.metadata.update(
                {
                    "query": query,
                    "contexts_returned": len(contexts),
                    "unique_sources": len(
                        {
                            context.source
                            for context in contexts
                        }
                    ),
                    "sources": sorted(
                        {
                            context.source
                            for context in contexts
                        }
                    ),
                    "pages": sorted(
                        {
                            context.page
                            for context in contexts
                            if context.page is not None
                        }
                    ),
                    "sections": sorted(
                        {
                            context.section
                            for context in contexts
                            if context.section
                        }
                    ),
                    "retrieval_latency_ms": round(
                        latency * 1000,
                        2,
                    ),
                    "average_reranker_score": (
                        round(
                            sum(scores) / len(scores),
                            4,
                        )
                        if scores
                        else None
                    ),
                    "highest_reranker_score": (
                        round(
                            max(scores),
                            4,
                        )
                        if scores
                        else None
                    ),
                    "lowest_reranker_score": (
                        round(
                            min(scores),
                            4,
                        )
                        if scores
                        else None
                    ),
                    "total_context_characters": sum(
                        len(context.text)
                        for context in contexts
                    ),
                }
            )

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

        Allows RetrievalService to be invoked like a function while
        preserving the tracing performed inside `retrieve()`.
        """

        return self.retrieve(
            query=query,
            user_id=user_id,
        )
