from __future__ import annotations

import math

from app.embeddings.exceptions import (
    EmbeddingBatchError,
    EmbeddingValidationError,
)
from app.embeddings.models import (
    EmbeddedChunk,
    EmbeddingBatch,
    EmbeddingVector,
)


def validate_vector(
    vector: EmbeddingVector,
    expected_dimensions: int,
) -> None:
    """
    Validate an embedding vector.
    """

    if not vector.values:

        raise EmbeddingValidationError(
            "Embedding vector is empty."
        )

    if vector.dimensions != expected_dimensions:

        raise EmbeddingValidationError(
            "Embedding dimensions do not match "
            "the expected dimensions."
        )

    for value in vector.values:

        if math.isnan(value):

            raise EmbeddingValidationError(
                "Embedding contains NaN values."
            )

        if math.isinf(value):

            raise EmbeddingValidationError(
                "Embedding contains infinite values."
            )


def validate_embedded_chunk(
    chunk: EmbeddedChunk,
) -> None:
    """
    Validate a single embedded chunk.
    """

    if not chunk.text.strip():

        raise EmbeddingValidationError(
            "Chunk text is empty."
        )

    if chunk.chunk_uuid is None:

        raise EmbeddingValidationError(
            "Chunk UUID is missing."
        )

    if chunk.document_uuid is None:

        raise EmbeddingValidationError(
            "Document UUID is missing."
        )

    validate_vector(

        vector=chunk.vector,

        expected_dimensions=chunk.metadata.dimensions,

    )


def validate_batch(
    batch: EmbeddingBatch,
) -> None:
    """
    Validate an embedding batch before sending it
    to the embedding provider.
    """

    if not batch.chunks:

        raise EmbeddingBatchError(
            "Embedding batch is empty."
        )

    uuids = []

    for chunk in batch.chunks:

        uuid = chunk.metadata.chunk_uuid

        if uuid is None:

            raise EmbeddingBatchError(
                "Chunk UUID is missing."
            )

        uuids.append(
            uuid,
        )

    if len(uuids) != len(set(uuids)):

        raise EmbeddingBatchError(
            "Duplicate chunk UUIDs detected "
            "inside embedding batch."
        )


def validate_embedded_chunks(
    chunks: list[EmbeddedChunk],
) -> None:
    """
    Validate an entire collection of embedded chunks.
    """

    if not chunks:

        raise EmbeddingValidationError(
            "No embedded chunks provided."
        )

    seen = set()

    for chunk in chunks:

        validate_embedded_chunk(
            chunk,
        )

        if chunk.chunk_uuid in seen:

            raise EmbeddingValidationError(
                "Duplicate embedded chunk UUID "
                "detected."
            )

        seen.add(
            chunk.chunk_uuid,
        )