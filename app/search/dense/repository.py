from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    IsEmptyCondition,
    MatchAny,
    MatchValue,
    PayloadField,
    PointStruct,
    Prefetch,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from app.config.settings import settings
from app.enums.document import DocumentAccessScope
from app.enums.organisation import OrgRole
from app.retrieval.access import AccessContext
from app.search.dense.exceptions import (
    CollectionAlreadyExistsError,
    CollectionCreationError,
    CollectionDeletionError,
    CollectionNotFoundError,
)

from app.search.dense.mapper import DenseMapper
from app.search.dense.models import DenseSearchResult
from app.search.hybrid.mapper import HybridMapper
from app.search.hybrid.models import HybridSearchResult

from langsmith import traceable


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
                sparse_vectors_config={

                    settings.QDRANT_SPARSE_VECTOR_NAME: SparseVectorParams(),

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
    # Delete
    # --------------------------------------------------------
    #

    def delete_by_document_id(
        self,
        document_id: int,
    ) -> int:
        """
        Delete every point belonging to one schema_version=3 document.

        Scoped exclusively to the ``document_id`` payload field -- the
        real SQL ``Document.id`` -- never ``document_uuid``, ``checksum``,
        ``chunk_uuid``, or an owner-only (``user_id``) match as a
        substitute. ``document_id`` is written only by the current
        (schema_version=3) payload builder (``HybridMapper.build_payload``);
        legacy schema_version=2 points never had it, so this filter is
        structurally incapable of matching a legacy point.

        An explicit existence check (a filtered count) runs before any
        delete call, so a legacy document never even triggers a delete
        attempt -- not merely relies on the filter being a harmless
        no-op. This makes the v2/v3 boundary explicit in code without
        requiring a new SQL column or any schema_version heuristic:
        Qdrant itself -- the only system that actually knows which points
        carry ``document_id`` -- is asked directly.

        Returns the number of points found and deleted. ``0`` means
        either the document was never indexed, or its points are legacy
        schema_version=2 -- in both cases no Qdrant write occurs.
        """

        document_filter = Filter(

            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                ),
            ],

        )

        existing = self.client.count(

            collection_name=self.COLLECTION_NAME,

            count_filter=document_filter,

            exact=True,

        )

        if existing.count == 0:
            return 0

        self.client.delete(

            collection_name=self.COLLECTION_NAME,

            points_selector=document_filter,

            wait=True,

        )

        return existing.count

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
    # Authorization
    # --------------------------------------------------------
    #

    @staticmethod
    def _authorization_filter(
        access: AccessContext,
    ) -> Filter:
        """
        Build the document-visibility filter for ``access``.

        Structural constraints (``is_reference``/``is_appendix``) are
        combined via AND with the union (OR) of every scope branch the
        requester qualifies for:

        - INDIVIDUAL: ``access.user_id`` owns the document. Legacy
          (schema_version=2) points never wrote an ``access_scope`` field
          at all -- ``IsEmptyCondition`` grandfathers those points in as
          individually visible to their owner (and only their owner; the
          ``user_id`` condition is never relaxed). This is the sole
          accommodation for legacy points -- they can never satisfy the
          TEAM or ORGANISATION branches below, which both require an
          explicit, present ``access_scope`` value legacy points don't have.
        - TEAM: only constructed when ``access.team_ids`` is non-empty
          (never ``MatchAny(any=[])``); requires the same organisation
          *and* team membership, so a numerically-matching team id in a
          different organisation can never match.
        - ORGANISATION: only constructed when ``access.role`` is
          ``OrgRole.ADMIN`` -- this is a Python-level decision about
          which branches exist, never a ``role`` condition inside the
          Qdrant filter itself.
        """

        structural = [
            FieldCondition(
                key="is_reference",
                match=MatchValue(value=False),
            ),
            FieldCondition(
                key="is_appendix",
                match=MatchValue(value=False),
            ),
        ]

        individual_branch = Filter(
            must=[
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=access.user_id),
                ),
            ],
            should=[
                FieldCondition(
                    key="access_scope",
                    match=MatchValue(
                        value=DocumentAccessScope.INDIVIDUAL.value,
                    ),
                ),
                IsEmptyCondition(
                    is_empty=PayloadField(key="access_scope"),
                ),
            ],
        )

        branches: list[Filter] = [individual_branch]

        if access.team_ids:
            branches.append(
                Filter(
                    must=[
                        FieldCondition(
                            key="access_scope",
                            match=MatchValue(
                                value=DocumentAccessScope.TEAM.value,
                            ),
                        ),
                        FieldCondition(
                            key="organisation_id",
                            match=MatchValue(value=access.organisation_id),
                        ),
                        FieldCondition(
                            key="team_id",
                            match=MatchAny(any=list(access.team_ids)),
                        ),
                    ],
                )
            )

        if access.role == OrgRole.ADMIN:
            branches.append(
                Filter(
                    must=[
                        FieldCondition(
                            key="access_scope",
                            match=MatchValue(
                                value=DocumentAccessScope.ORGANISATION.value,
                            ),
                        ),
                        FieldCondition(
                            key="organisation_id",
                            match=MatchValue(value=access.organisation_id),
                        ),
                    ],
                )
            )

        return Filter(
            must=[
                *structural,
                Filter(should=branches),
            ],
        )

    @traceable(
        name="Qdrant Hybrid Search",
        run_type="retriever",
    )
    def hybrid_search(
        self,
        *,
        dense_vector: list[float],
        sparse_indices: list[int],
        sparse_values: list[float],
        access: AccessContext,
        limit: int = 10,
    ) -> list[HybridSearchResult]:
        """
        Execute native Qdrant Hybrid Search
        using Reciprocal Rank Fusion (RRF).

        Parameters
        ----------
        dense_vector
            Dense embedding generated by OpenAI.

        sparse_indices
            Sparse vector indices.

        sparse_values
            Sparse vector values.

        access
            Trusted authorization context. Document visibility is the
            union of three branches (individual / team / organisation),
            each requiring ``access.organisation_id`` where relevant --
            see ``_authorization_filter``.

        limit
            Number of documents to return.

        Returns
        -------
        list[ScoredPoint]
        """

        retrieval_filter = self._authorization_filter(access)

        candidate_limit = max(
            limit * 5,
            settings.QDRANT_HYBRID_CANDIDATE_LIMIT,
        )

        response = self.client.query_points(

            collection_name=self.COLLECTION_NAME,

            prefetch=[

                Prefetch(

                    query=dense_vector,

                    using=settings.QDRANT_VECTOR_NAME,

                    limit=candidate_limit,
                    
                    filter=retrieval_filter,

                ),

                Prefetch(

                    query=SparseVector(

                        indices=sparse_indices,

                        values=sparse_values,

                    ),

                    using=settings.QDRANT_SPARSE_VECTOR_NAME,

                    limit=candidate_limit,
                    
                    filter=retrieval_filter,

                ),

            ],

            query=FusionQuery(

                fusion=Fusion.RRF,

            ),

            limit=limit,

            with_payload=True,

            with_vectors=False,

        )

        return HybridMapper.from_scored_points(
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