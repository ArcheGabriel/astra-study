"""
Astra Study Reranking Package.

This package provides the public API for document reranking.

The reranking subsystem is responsible for improving the ranking
of retrieved documents before they are passed to the LLM.

Architecture
------------
Hybrid Search
      │
      ▼
RerankingService
      │
      ▼
CrossEncoderReranker
      │
      ▼
Cross Encoder Model
      │
      ▼
RerankingResult
"""

from app.reranking.base import BaseReranker
from app.reranking.cross_encoder import CrossEncoderReranker
from app.reranking.models import (
    RerankedChunk,
    RerankingResult,
)
from app.reranking.service import RerankingService

__all__ = [
    "BaseReranker",
    "CrossEncoderReranker",
    "RerankedChunk",
    "RerankingResult",
    "RerankingService",
]