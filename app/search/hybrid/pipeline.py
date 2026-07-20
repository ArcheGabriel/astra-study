from __future__ import annotations

from app.chunking.models import DocumentChunk
from app.embeddings.pipeline import EmbeddingPipeline
from app.search.dense.repository import DenseRepository
from app.search.hybrid.mapper import HybridMapper
from app.search.sparse.pipeline import SparsePipeline


class HybridPipeline:
    """
    Production Hybrid Indexing Pipeline.

    Responsibilities
    ----------------

    DocumentChunks
            │
            ▼
    EmbeddingPipeline
            │
            ▼
    SparsePipeline
            │
            ▼
    HybridMapper
            │
            ▼
    DenseRepository (Qdrant)
    """

    def __init__(
        self,
        embedding_pipeline: EmbeddingPipeline | None = None,
        sparse_pipeline: SparsePipeline | None = None,
        repository: DenseRepository | None = None,
    ) -> None:

        self.embedding_pipeline = (
            embedding_pipeline
            or EmbeddingPipeline()
        )

        self.sparse_pipeline = (
            sparse_pipeline
            or SparsePipeline()
        )

        self.repository = (
            repository
            or DenseRepository()
        )

    #
    # --------------------------------------------------------
    # Collection Management
    # --------------------------------------------------------
    #

    def create_collection(
        self,
    ) -> None:

        self.repository.create_collection()

    def recreate_collection(
        self,
    ) -> None:

        self.repository.recreate_collection()

    def delete_collection(
        self,
    ) -> None:

        self.repository.delete_collection()

    #
    # --------------------------------------------------------
    # Indexing
    # --------------------------------------------------------
    #

    def index(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        """
        Index document chunks using
        hybrid dense+sparse vectors.
        """

        if not chunks:

            return

        dense_chunks = self.embedding_pipeline.run(
            chunks,
        )

        sparse_chunks = self.sparse_pipeline.encode(
            chunks,
        )

        points = HybridMapper.to_points(

            dense_chunks=dense_chunks,

            sparse_chunks=sparse_chunks,

        )

        self.repository.upsert(
            points,
        )

    #
    # --------------------------------------------------------
    # Utilities
    # --------------------------------------------------------
    #

    def count(
        self,
    ) -> int:

        return self.repository.count()

    def scroll(
        self,
        limit: int = 10,
    ):

        return self.repository.scroll(
            limit=limit,
        )

    def collection_info(
        self,
    ):

        return self.repository.collection_info()

    def is_empty(
        self,
    ) -> bool:

        return self.repository.is_empty()