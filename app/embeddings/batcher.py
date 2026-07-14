from __future__ import annotations

from app.chunking.models import DocumentChunk
from app.config.settings import settings
from app.embeddings.exceptions import (
    EmbeddingBatchError,
)
from app.embeddings.models import (
    EmbeddingBatch,
)
from app.embeddings.validator import (
    validate_batch,
)


class EmbeddingBatcher:
    """
    Splits document chunks into batches suitable for the
    embedding provider.

    The batcher preserves chunk ordering and ensures that
    each batch satisfies the configured limits.
    """

    def __init__(
        self,
        batch_size: int | None = None,
    ) -> None:

        self.batch_size = (
            batch_size
            or settings.EMBEDDING_MAX_BATCH_SIZE
        )

        if self.batch_size <= 0:

            raise EmbeddingBatchError(
                "Embedding batch size must be greater than zero."
            )

    def create_batches(
        self,
        chunks: list[DocumentChunk],
    ) -> list[EmbeddingBatch]:
        """
        Split chunks into embedding batches.
        """

        if not chunks:

            raise EmbeddingBatchError(
                "No chunks supplied for embedding."
            )

        batches: list[EmbeddingBatch] = []

        for index in range(
            0,
            len(chunks),
            self.batch_size,
        ):

            batch = EmbeddingBatch(
                chunks=chunks[
                    index:index + self.batch_size
                ]
            )

            validate_batch(
                batch,
            )

            batches.append(
                batch,
            )

        return batches

    def __call__(
        self,
        chunks: list[DocumentChunk],
    ) -> list[EmbeddingBatch]:
        """
        Convenience wrapper allowing the batcher to be
        called directly.
        """

        return self.create_batches(
            chunks,
        )