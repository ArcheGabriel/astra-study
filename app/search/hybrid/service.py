from __future__ import annotations

from app.embeddings.embedder import OpenAIEmbedder
from app.retrieval.access import AccessContext
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
        access: AccessContext,
        query: str,
        limit: int = 10,
        dense_vector: list[float] | None = None,
    ) -> list[HybridSearchResult]:
        """
        Execute Hybrid Retrieval.

        ``dense_vector``, if supplied, is used as-is and this method
        does NOT call ``embed_query`` itself -- lets a caller that has
        already computed the query's dense embedding (``RetrievalService``,
        for its semantic-cache lookup, RBAC/C.3) pass it through rather
        than paying for a second embedding request. When omitted (the
        default), behavior is identical to before this parameter
        existed: this method computes its own embedding.
        """

        if not query.strip():

            return []

        if dense_vector is None:
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

            access=access,

            limit=limit,

        )

        return results

    def __call__(
        self,
        query: str,
        access: AccessContext,
        limit: int = 10,
        dense_vector: list[float] | None = None,
    ) -> list[HybridSearchResult]:

        return self.search(
            query=query,
            access=access,
            limit=limit,
            dense_vector=dense_vector,
        )