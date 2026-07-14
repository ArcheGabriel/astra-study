from __future__ import annotations

from app.chunking.models import DocumentChunk
from app.embeddings.batcher import EmbeddingBatcher
from app.embeddings.embedder import OpenAIEmbedder
from app.embeddings.models import EmbeddedChunk


class EmbeddingPipeline:
    """
    Production embedding pipeline.

    Pipeline

    DocumentChunks

            │

            ▼

    EmbeddingBatcher

            │

            ▼

    OpenAIEmbedder

            │

            ▼

    EmbeddedChunks
    """

    def __init__(
        self,
        batcher: EmbeddingBatcher | None = None,
        embedder: OpenAIEmbedder | None = None,
    ) -> None:

        self.batcher = (
            batcher
            or EmbeddingBatcher()
        )

        self.embedder = (
            embedder
            or OpenAIEmbedder()
        )

    def run(
        self,
        chunks: list[DocumentChunk],
    ) -> list[EmbeddedChunk]:
        """
        Execute the complete embedding pipeline.
        """

        if not chunks:

            return []

        batches = self.batcher.create_batches(
            chunks,
        )

        embedded_chunks = self.embedder.embed(
            batches,
        )

        return embedded_chunks

    def __call__(
        self,
        chunks: list[DocumentChunk],
    ) -> list[EmbeddedChunk]:
        """
        Convenience wrapper.

        Allows

            pipeline(chunks)

        instead of

            pipeline.run(chunks)
        """

        return self.run(
            chunks,
        )