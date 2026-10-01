from __future__ import annotations

import logging
from time import perf_counter

from app.cache.models import Namespace
from app.cache.semantic import SemanticRetrievalCache, build_namespace
from app.config.settings import settings
from app.embeddings.embedder import OpenAIEmbedder
from app.retrieval.access import AccessContext
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
        embedder: OpenAIEmbedder | None = None,
        semantic_cache: SemanticRetrievalCache | None = None,
    ) -> None:
        self._hybrid_service = hybrid_service
        self._reranking_service = reranking_service

        # Owns the embedding call so it can be made exactly once per
        # query and reused for both the cache lookup and (on a miss)
        # Hybrid Search -- mirrors HybridService's own
        # `self.embedder = embedder or OpenAIEmbedder()` pattern, kept
        # separate rather than reaching into `hybrid_service.embedder`
        # so this class does not depend on HybridService's internal
        # attributes (and so a mocked `hybrid_service` in tests, e.g.
        # tests/unit/retrieval/test_service.py, is never implicitly
        # relied on for a real embedding call).
        self._embedder = embedder or OpenAIEmbedder()

        # Defaults to a private, unshared cache instance (never None) so
        # `retrieve()` never needs a None-check at every call site; any
        # direct/test/evaluation caller that does not explicitly inject
        # the process-wide singleton (see
        # app/dependencies/resources.py::get_semantic_cache_resource)
        # simply gets a cache that starts empty and is discarded with
        # this instance -- harmless, never shared, never a correctness
        # risk. `settings.SEMANTIC_CACHE_ENABLED` is checked separately
        # in `retrieve()` as the actual on/off switch.
        self._semantic_cache = (
            semantic_cache
            if semantic_cache is not None
            else SemanticRetrievalCache()
        )

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
                    page_end=payload.get("page_end"),
                    parser=payload.get("parser"),
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
        access: AccessContext,
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
            access.user_id,
        )

        start = perf_counter()

        #
        # Query embedding -- computed exactly once here, reused for both
        # the semantic-cache lookup below and (on a miss) Hybrid Search,
        # never a second embedding request solely for the cache.
        #
        dense_vector = self._embedder.embed_query(query)

        namespace = build_namespace(access)

        #
        # Semantic retrieval cache lookup (RBAC/C.3). Fail-open: any
        # exception here is logged and treated as a miss -- a cache bug
        # must never block retrieval, and must never silently return
        # unauthorized/stale data (so a lookup failure is always a MISS,
        # never a fabricated HIT).
        #
        cache_lookup = None

        if settings.SEMANTIC_CACHE_ENABLED:
            try:
                cache_lookup = self._semantic_cache.lookup(
                    namespace=namespace,
                    query_embedding=dense_vector,
                )
            except Exception:
                logger.exception(
                    "Semantic retrieval cache lookup failed; "
                    "continuing with normal retrieval."
                )
                cache_lookup = None

        if cache_lookup is not None:

            latency = perf_counter() - start

            run = get_current_run_tree()

            if run:
                run.metadata.update(
                    {
                        "query": query,
                        "cache_hit": True,
                        "cache_similarity_score": round(
                            cache_lookup.similarity_score,
                            4,
                        ),
                        "cache_age_seconds": round(
                            cache_lookup.cache_age_seconds,
                            3,
                        ),
                        "contexts_returned": len(
                            cache_lookup.retrieval_result.contexts,
                        ),
                        "retrieval_latency_ms": round(
                            latency * 1000,
                            2,
                        ),
                    }
                )

            logger.info(
                "Semantic retrieval cache HIT for query='%s' "
                "(similarity=%.4f, age=%.1fs).",
                query,
                cache_lookup.similarity_score,
                cache_lookup.cache_age_seconds,
            )

            # Preserve the RetrievalResult structure exactly -- same
            # dataclass, same contexts -- only `query`/`retrieval_latency`
            # reflect this specific call, never the cached call's own.
            return RetrievalResult(
                query=query,
                contexts=cache_lookup.retrieval_result.contexts,
                retrieval_latency=latency,
            )

        #
        # Best-effort miss-reason diagnosis (observability only, RBAC/C.3
        # follow-up). Never raises, never fabricates a reason or a score
        # it cannot determine (returns (None, None)) -- see
        # SemanticRetrievalCache.diagnose_miss's own docstring for exactly
        # which reasons it can and cannot distinguish.
        # `cache_best_similarity_score` is only ever non-None when the
        # reason is "below_threshold" -- for "empty"/"namespace_mismatch"/
        # "expired" no similarity comparison was meaningful, so no score
        # is fabricated for those cases.
        #
        cache_miss_reason = None
        cache_best_similarity_score = None

        if settings.SEMANTIC_CACHE_ENABLED:
            try:
                cache_miss_reason, cache_best_similarity_score = (
                    self._semantic_cache.diagnose_miss(
                        namespace=namespace,
                        query_embedding=dense_vector,
                    )
                )
            except Exception:
                logger.exception(
                    "Semantic retrieval cache miss-reason diagnosis "
                    "failed; continuing without it."
                )
                cache_miss_reason = None
                cache_best_similarity_score = None

        #
        # Hybrid Retrieval (cache MISS, or caching disabled/failed open)
        #
        hybrid_results = self._hybrid_service(
            query=query,
            access=access,
            limit=settings.QDRANT_HYBRID_CANDIDATE_LIMIT,
            dense_vector=dense_vector,
        )

        logger.info(
            "Hybrid retrieval returned %d candidates.",
            len(hybrid_results),
        )

        if not hybrid_results:

            latency = perf_counter() - start

            run = get_current_run_tree()

            if run:
                miss_metadata = {
                    "query": query,
                    "cache_hit": False,
                    "contexts_returned": 0,
                    "retrieval_latency_ms": round(
                        latency * 1000,
                        2,
                    ),
                }
                if cache_miss_reason is not None:
                    miss_metadata["cache_miss_reason"] = cache_miss_reason
                if cache_best_similarity_score is not None:
                    miss_metadata["cache_best_similarity_score"] = round(
                        cache_best_similarity_score,
                        4,
                    )
                run.metadata.update(miss_metadata)

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
                miss_metadata = {
                    "query": query,
                    "cache_hit": False,
                    "contexts_returned": 0,
                    "retrieval_latency_ms": round(
                        latency * 1000,
                        2,
                    ),
                }
                if cache_miss_reason is not None:
                    miss_metadata["cache_miss_reason"] = cache_miss_reason
                if cache_best_similarity_score is not None:
                    miss_metadata["cache_best_similarity_score"] = round(
                        cache_best_similarity_score,
                        4,
                    )
                run.metadata.update(miss_metadata)

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

            success_metadata = {
                "query": query,
                "cache_hit": False,
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
            if cache_miss_reason is not None:
                success_metadata["cache_miss_reason"] = cache_miss_reason
            if cache_best_similarity_score is not None:
                success_metadata["cache_best_similarity_score"] = round(
                    cache_best_similarity_score,
                    4,
                )
            run.metadata.update(success_metadata)

        logger.info(
            (
                "Retrieval completed successfully. "
                "%d contexts returned in %.3f seconds."
            ),
            len(contexts),
            latency,
        )

        result = RetrievalResult(
            query=query,
            contexts=contexts,
            retrieval_latency=latency,
        )

        if settings.SEMANTIC_CACHE_ENABLED:
            try:
                self._semantic_cache.store(
                    namespace=namespace,
                    query_embedding=dense_vector,
                    retrieval_result=result,
                )
            except Exception:
                logger.exception(
                    "Semantic retrieval cache store failed; "
                    "result was not cached."
                )

        return result

    def __call__(
        self,
        *,
        query: str,
        access: AccessContext,
    ) -> RetrievalResult:
        """
        Callable wrapper.

        Allows RetrievalService to be invoked like a function while
        preserving the tracing performed inside `retrieve()`.
        """

        return self.retrieve(
            query=query,
            access=access,
        )
