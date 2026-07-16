from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from app.config.settings import settings
from app.search.dense.exceptions import (
    CollectionAlreadyExistsError,
    CollectionCreationError,
    CollectionDeletionError,
    CollectionNotFoundError,
)

from app.search.dense.mapper import DenseMapper
from app.search.dense.models import DenseSearchResult


class DenseRepository:
    """
    Repository responsible for all communication
    with Qdrant.

    Responsibilities
    ----------------

    • Create collections

    • Delete collections

    • Upsert vectors

    • Search vectors

    • Count vectors

    • Scroll vectors

    The repository knows everything about Qdrant.

    The rest of the application knows nothing
    about the database.
    """

    COLLECTION_NAME = settings.QDRANT_COLLECTION_NAME

    VECTOR_NAME = settings.QDRANT_VECTOR_NAME

    def __init__(
        self,
    ) -> None:

        self.client = QdrantClient(

            url=settings.QDRANT_URL,

            api_key=(
                settings.QDRANT_API_KEY
                or None
            ),

        )

    #
    # --------------------------------------------------------
    # Collection
    # --------------------------------------------------------
    #

    def collection_exists(
        self,
    ) -> bool:

        collections = self.client.get_collections()

        return any(

            collection.name
            == self.COLLECTION_NAME

            for collection
            in collections.collections

        )

    def create_collection(
        self,
    ) -> None:
        """
        Create the Astra Study collection.
        """

        if self.collection_exists():

            raise CollectionAlreadyExistsError(

                f"Collection "

                f"'{self.COLLECTION_NAME}' "

                f"already exists."

            )

        try:

            self.client.create_collection(

                collection_name=self.COLLECTION_NAME,

                vectors_config={

                    self.VECTOR_NAME:

                    VectorParams(

                        size=settings.EMBEDDING_DIMENSIONS,

                        distance=Distance.COSINE,

                    )

                },

            )

        except Exception as exc:

            raise CollectionCreationError(

                str(exc)

            ) from exc

    def delete_collection(
        self,
    ) -> None:
        """
        Delete the Astra Study collection.
        """

        if not self.collection_exists():

            raise CollectionNotFoundError(

                f"Collection "

                f"'{self.COLLECTION_NAME}' "

                f"does not exist."

            )

        try:

            self.client.delete_collection(

                collection_name=self.COLLECTION_NAME,

            )

        except Exception as exc:

            raise CollectionDeletionError(

                str(exc)

            ) from exc

    def recreate_collection(
        self,
    ) -> None:
        """
        Drop and recreate the collection.
        Useful during development.
        """

        if self.collection_exists():

            self.delete_collection()

        self.create_collection()
        
    #
    # --------------------------------------------------------
    # Upsert
    # --------------------------------------------------------
    #

    def upsert(
        self,
        points: list[PointStruct],
    ) -> None:
        """
        Insert or update points in the collection.
        """

        if not points:
            return

        self.client.upsert(

            collection_name=self.COLLECTION_NAME,

            points=points,

            wait=True,

        )

    #
    # --------------------------------------------------------
    # Count
    # --------------------------------------------------------
    #

    def count(
        self,
    ) -> int:
        """
        Return the number of vectors stored in the
        collection.
        """

        response = self.client.count(

            collection_name=self.COLLECTION_NAME,

            exact=True,

        )

        return response.count

    #
    # --------------------------------------------------------
    # Scroll
    # --------------------------------------------------------
    #

    def scroll(
        self,
        limit: int = 10,
    ):
        """
        Scroll through stored points.

        Useful for debugging.
        """

        points, _ = self.client.scroll(

            collection_name=self.COLLECTION_NAME,

            limit=limit,

            with_payload=True,

            with_vectors=False,

        )

        return points
    
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
        Perform dense similarity search.
        """

        response = self.client.query_points(

            collection_name=self.COLLECTION_NAME,

            query=query_vector,

            using=self.VECTOR_NAME,

            limit=limit,

            score_threshold=score_threshold,

            with_payload=True,

            with_vectors=False,

        )

        return DenseMapper.from_scored_points(
            response.points,
        )
    #
    # --------------------------------------------------------
    # Retrieve Point
    # --------------------------------------------------------
    #

    def get_point(
        self,
        point_id: str,
    ):
        """
        Retrieve a single point by its ID.
        """

        result = self.client.retrieve(

            collection_name=self.COLLECTION_NAME,

            ids=[point_id],

            with_payload=True,

            with_vectors=False,

        )

        if not result:

            return None

        return result[0]

    #
    # --------------------------------------------------------
    # Collection Information
    # --------------------------------------------------------
    #

    def collection_info(
        self,
    ):
        """
        Return information about the collection.
        """

        return self.client.get_collection(

            self.COLLECTION_NAME,

        )

    #
    # --------------------------------------------------------
    # Convenience
    # --------------------------------------------------------
    #

    def is_empty(
        self,
    ) -> bool:
        """
        Returns True if the collection contains
        no vectors.
        """

        return self.count() == 0