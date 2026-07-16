from __future__ import annotations

from app.embeddings.models import EmbeddedChunk
from app.search.dense.mapper import DenseMapper
from app.search.dense.models import DenseSearchResult
from app.search.dense.repository import DenseRepository


class DensePipeline:
    """
    Production dense search pipeline.

    Responsibilities
    ----------------

    EmbeddedChunks
            │
            ▼
    DenseMapper
            │
            ▼
    DenseRepository
            │
            ▼
    Qdrant
    """

    def __init__(
        self,
        repository: DenseRepository | None = None,
    ) -> None:

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
        chunks: list[EmbeddedChunk],
    ) -> None:
        """
        Index embedded chunks into Qdrant.
        """

        if not chunks:

            return

        points = DenseMapper.to_points(
            chunks,
        )

        self.repository.upsert(
            points,
        )

    #
    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------
    #

    def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[DenseSearchResult]:
        """
        Execute dense vector similarity search.
        """

        return self.repository.search(

            query_vector=query_vector,

            limit=limit,

            score_threshold=score_threshold,

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