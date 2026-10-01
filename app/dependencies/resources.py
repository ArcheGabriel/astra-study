"""
Application-scoped AI resources.

Heavy resources (models, vector clients, LLM clients, etc.) should
be created only once and reused for the lifetime of the application.
"""

from __future__ import annotations

from functools import lru_cache

from app.cache.semantic import SemanticRetrievalCache
from app.reranking.service import RerankingService
from app.services.llm import LLMService


@lru_cache(maxsize=1)
def get_llm_resource() -> LLMService:
    """
    Return the shared LLM service.
    """

    return LLMService()


@lru_cache(maxsize=1)
def get_reranking_resource() -> RerankingService:
    """
    Return the shared reranking service.

    The underlying CrossEncoder model is loaded only once.
    """

    return RerankingService()


@lru_cache(maxsize=1)
def get_semantic_cache_resource() -> SemanticRetrievalCache:
    """
    Return the shared semantic retrieval cache (RBAC/C.3).

    Unlike ``RetrievalService``/``HybridService`` (constructed fresh per
    request, see ``app/dependencies/services.py``), the cache itself
    must be a process-wide singleton to ever have a hit across requests
    -- otherwise every request would build and discard its own empty
    cache. Mirrors the exact singleton-factory idiom already established
    above for the LLM/reranking resources.
    """

    return SemanticRetrievalCache()