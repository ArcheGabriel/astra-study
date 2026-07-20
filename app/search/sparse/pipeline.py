from __future__ import annotations

from app.chunking.models import DocumentChunk
from app.search.sparse.encoder import SparseEncoder
from app.search.sparse.models import SparseEmbeddedChunk


class SparsePipeline:
    """
    Generates sparse embeddings for document chunks.

    Responsibilities
    ----------------
    DocumentChunk
            ↓
    SparseEncoder
            ↓
    SparseEmbeddedChunk
    """

    def __init__(
        self,
        encoder: SparseEncoder | None = None,
    ) -> None:

        self.encoder = encoder or SparseEncoder()

    def encode(
        self,
        chunks: list[DocumentChunk],
    ) -> list[SparseEmbeddedChunk]:
        """
        Generate sparse vectors for multiple chunks.
        """

        if not chunks:
            return []

        return self.encoder.encode_chunks(
            chunks,
        )

    def encode_query(
        self,
        query: str,
    ):
        """
        Generate a sparse vector for a search query.
        """

        return self.encoder.encode_query(
            query,
        )

    def __call__(
        self,
        chunks: list[DocumentChunk],
    ) -> list[SparseEmbeddedChunk]:
        """
        Convenience wrapper around encode().
        """

        return self.encode(
            chunks,
        )