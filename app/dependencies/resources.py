"""
Application-scoped AI resources.

Heavy resources (models, vector clients, LLM clients, etc.) should
be created only once and reused for the lifetime of the application.
"""

from __future__ import annotations

from functools import lru_cache

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