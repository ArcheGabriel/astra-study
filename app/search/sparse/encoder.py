from __future__ import annotations

from fastembed import SparseTextEmbedding

from app.chunking.models import DocumentChunk
from app.config.settings import settings
from app.search.sparse.models import (
    SparseEmbeddedChunk,
    SparseVector,
)


class SparseEncoder:
    """
    Generates sparse embeddings for document chunks
    using FastEmbed.

    Responsibilities
    ----------------

    • Initialize sparse embedding model

    • Encode document chunks

    • Encode user queries

    • Produce SparseEmbeddedChunk objects
    """

    def __init__(
        self,
    ) -> None:

        self.model_name = (
            settings.SPARSE_EMBEDDING_MODEL
        )

        self.model = SparseTextEmbedding(

            model_name=self.model_name,

        )

    def encode_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> list[SparseEmbeddedChunk]:
        """
        Generate sparse embeddings for document chunks.
        """

        if not chunks:

            return []

        texts = [

            chunk.text

            for chunk in chunks

        ]

        embeddings = list(

            self.model.embed(
                texts,
            )

        )

        sparse_chunks: list[
            SparseEmbeddedChunk
        ] = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
            strict=True,
        ):

            sparse_chunks.append(

                SparseEmbeddedChunk(

                    chunk=chunk,

                    vector=SparseVector(

                        indices=list(
                            embedding.indices,
                        ),

                        values=list(
                            embedding.values,
                        ),

                    ),

                )

            )

        return sparse_chunks

    def encode_query(
        self,
        query: str,
    ) -> SparseVector:
        """
        Generate sparse embedding for a user query.
        """

        if not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        embedding = next(

            self.model.query_embed(

                query,

            )

        )

        return SparseVector(

            indices=list(
                embedding.indices,
            ),

            values=list(
                embedding.values,
            ),

        )

    def __call__(
        self,
        chunks: list[DocumentChunk],
    ) -> list[SparseEmbeddedChunk]:
        """
        Convenience wrapper.
        """

        return self.encode_chunks(
            chunks,
        )
    