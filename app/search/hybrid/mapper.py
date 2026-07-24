from __future__ import annotations

from qdrant_client.models import (
    PointStruct,
    SparseVector as QdrantSparseVector,
)

from app.config.settings import settings
from app.embeddings.models import EmbeddedChunk
from app.search.sparse.models import SparseEmbeddedChunk

from uuid import UUID
from qdrant_client.models import ScoredPoint
from app.search.hybrid.models import HybridSearchResult


class HybridMapper:
    """
    Converts Astra Study domain models into
    hybrid Qdrant PointStruct objects.

    Responsibilities
    ----------------

    EmbeddedChunk
            +
    SparseEmbeddedChunk
            │
            ▼
        PointStruct

    The produced PointStruct contains both
    dense and sparse vectors while sharing
    a single payload.
    """

    @staticmethod
    def build_payload(
        chunk: EmbeddedChunk,
    ) -> dict:
        """
        Build the payload stored alongside every
        vector inside Qdrant.

        Payload construction lives here because
        hybrid indexing is now the primary indexing
        strategy of Astra Study.
        """

        metadata = chunk.chunk.metadata

        return {

            "schema_version": 1,

            #
            # Document
            #
            "document_uuid": (
                str(metadata.document_uuid)
                if metadata.document_uuid
                else None
            ),

            "document_name": metadata.document_name,
            
            "user_id": metadata.user_id,

            "checksum": metadata.checksum,

            "language": metadata.language,

            #
            # Chunk
            #
            "chunk_uuid": (
                str(metadata.chunk_uuid)
                if metadata.chunk_uuid
                else None
            ),

            "parent_chunk_uuid": (
                str(metadata.parent_chunk_uuid)
                if metadata.parent_chunk_uuid
                else None
            ),

            #
            # Text
            #
            "text": chunk.text,

            #
            # Pages
            #
            "page_start": metadata.page_start,

            "page_end": metadata.page_end,

            #
            # Blocks
            #
            "block_start": metadata.block_start,

            "block_end": metadata.block_end,

            #
            # Section
            #
            "section_title": metadata.section_title,

            "section_id": metadata.section_id,

            "heading_level": metadata.heading_level,

            "heading_path": metadata.heading_path,

            #
            # Retrieval
            #
            "token_count": metadata.token_count,

            "character_count": metadata.character_count,

            "quality_score": metadata.quality_score,

            "retrieval_priority": metadata.retrieval_priority,

            #
            # Classification
            #
            "block_type": metadata.block_type.value,

            "is_reference": metadata.is_reference,

            "is_appendix": metadata.is_appendix,

            "is_metadata": metadata.is_metadata,

            "is_caption": metadata.is_caption,

            "is_table": metadata.is_table,

            "is_formula": metadata.is_formula,
        }

    @staticmethod
    def to_point(
        dense_chunk: EmbeddedChunk,
        sparse_chunk: SparseEmbeddedChunk,
    ) -> PointStruct:
        """
        Combine dense and sparse representations
        into a single hybrid Qdrant point.
        """

        if dense_chunk.chunk_uuid != sparse_chunk.chunk_uuid:

            raise ValueError(
                "Dense and sparse chunks do not represent "
                "the same document chunk."
            )

        payload = HybridMapper.build_payload(
            dense_chunk,
        )

        metadata = dense_chunk.chunk.metadata

        return PointStruct(

            id=str(
                metadata.chunk_uuid,
            ),

            vector={

                settings.QDRANT_VECTOR_NAME:
                    dense_chunk.vector.values,

                settings.QDRANT_SPARSE_VECTOR_NAME:
                    QdrantSparseVector(

                        indices=sparse_chunk.vector.indices,

                        values=sparse_chunk.vector.values,

                    ),

            },

            payload=payload,

        )

    @staticmethod
    def to_points(
        dense_chunks: list[EmbeddedChunk],
        sparse_chunks: list[SparseEmbeddedChunk],
    ) -> list[PointStruct]:
        """
        Convert dense and sparse chunk collections
        into hybrid PointStructs.

        Both lists must be in identical order.
        """

        if len(dense_chunks) != len(sparse_chunks):

            raise ValueError(
                "Dense and sparse chunk counts do not match."
            )

        return [

            HybridMapper.to_point(
                dense_chunk,
                sparse_chunk,
            )

            for dense_chunk, sparse_chunk in zip(
                dense_chunks,
                sparse_chunks,
                strict=True,
            )

        ]
    
    @staticmethod
    def from_scored_point(
        point: ScoredPoint,
    ) -> HybridSearchResult:
        """
        Convert a Qdrant ScoredPoint into a
        HybridSearchResult.
        """

        payload = point.payload or {}

        return HybridSearchResult(

            chunk_uuid=UUID(
                payload["chunk_uuid"],
            ),

            document_uuid=UUID(
                payload["document_uuid"],
            ),

            score=point.score,

            text=payload["text"],

            payload=payload,

        )

    @staticmethod
    def from_scored_points(
        points: list[ScoredPoint],
    ) -> list[HybridSearchResult]:
        """
        Convert multiple ScoredPoints into
        HybridSearchResult objects.
        """

        return [

            HybridMapper.from_scored_point(
                point,
            )

            for point in points

        ]