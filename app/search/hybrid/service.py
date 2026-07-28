from __future__ import annotations

from app.embeddings.embedder import OpenAIEmbedder
from app.search.dense.repository import DenseRepository
from app.search.hybrid.models import HybridSearchResult
from app.search.sparse.encoder import SparseEncoder
from langsmith import traceable


class HybridService:
    """
    Production Hybrid Retriever.

    Responsibilities
    ----------------

    • Generate dense query embedding

    • Generate sparse query embedding

    • Execute native Qdrant Hybrid Search

    • Return ranked HybridSearchResult objects
    """

    def __init__(
        self,
        embedder: OpenAIEmbedder | None = None,
        sparse_encoder: SparseEncoder | None = None,
        repository: DenseRepository | None = None,
    ) -> None:

        self.embedder = (
            embedder
            or OpenAIEmbedder()
        )

        self.sparse_encoder = (
            sparse_encoder
            or SparseEncoder()
        )

        self.repository = (
            repository
            or DenseRepository()
        )

    @traceable(
        name="Hybrid Search",
        run_type="retriever",
    )
    def search(
        self,
        user_id: int,
        query: str,
        limit: int = 10,
    ) -> list[HybridSearchResult]:
        """
        Execute Hybrid Retrieval.
        """

        if not query.strip():

            return []

        dense_vector = self.embedder.embed_query(
            query,
        )

        sparse_vector = self.sparse_encoder.encode_query(
            query,
        )

        results = self.repository.hybrid_search(

            dense_vector=dense_vector,

            sparse_indices=sparse_vector.indices,

            sparse_values=sparse_vector.values,
            
            user_id=user_id,

            limit=limit,

        )
        
        return results

    def __call__(
        self,
        query: str,
        user_id: int,
        limit: int = 10,
    ) -> list[HybridSearchResult]:

        return self.search(
            query=query,
            user_id=user_id,
            limit=limit,
        )