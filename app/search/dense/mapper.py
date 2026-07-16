from __future__ import annotations

from uuid import UUID

from qdrant_client.models import (
    PointStruct,
    ScoredPoint,
)

from app.embeddings.models import EmbeddedChunk
from app.search.dense.models import DenseSearchResult
from app.config.settings import settings


class DenseMapper:
    """
    Converts between Astra Study domain models and
    Qdrant models.

    Responsibilities
    ----------------
    EmbeddedChunk
            ↓
        PointStruct

    ScoredPoint
            ↓
    DenseSearchResult (implemented later)
    """

    @staticmethod
    def to_point(
        chunk: EmbeddedChunk,
    ) -> PointStruct:
        """
        Convert one EmbeddedChunk into a Qdrant PointStruct.
        """

        metadata = chunk.chunk.metadata

        payload = {
            
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

        return PointStruct(

            id=str(
                metadata.chunk_uuid,
            ),

            vector={
                settings.QDRANT_VECTOR_NAME:
                chunk.vector.values,
            },

            payload=payload,

        )

    @staticmethod
    def to_points(
        chunks: list[EmbeddedChunk],
    ) -> list[PointStruct]:
        """
        Convert multiple EmbeddedChunks into
        PointStructs.
        """

        return [

            DenseMapper.to_point(
                chunk,
            )

            for chunk in chunks

        ]
    
    @staticmethod
    def from_scored_point(
        point: ScoredPoint,
    ) -> DenseSearchResult:
        """
        Convert a Qdrant ScoredPoint into a
        DenseSearchResult.
        """

        payload = point.payload or {}

        return DenseSearchResult(

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
    ) -> list[DenseSearchResult]:
        """
        Convert multiple ScoredPoints into
        DenseSearchResults.
        """

        return [

            DenseMapper.from_scored_point(
                point,
            )

            for point in points

        ]