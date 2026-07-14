from __future__ import annotations

import time
from typing import Iterable

from openai import OpenAI
from openai import APITimeoutError
from openai import APIConnectionError
from openai import RateLimitError
from openai import APIStatusError

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.chunking.models import DocumentChunk
from app.config.settings import settings
from app.embeddings.exceptions import (
    EmbeddingConfigurationError,
    EmbeddingGenerationError,
    EmbeddingRateLimitError,
    EmbeddingTimeoutError,
)
from app.embeddings.models import (
    EmbeddedChunk,
    EmbeddingBatch,
    EmbeddingMetadata,
    EmbeddingVector,
)
from app.embeddings.validator import (
    validate_embedded_chunk,
)


class OpenAIEmbedder:
    """
    Generates OpenAI embeddings for DocumentChunks.

    Responsibilities
    ----------------
    • Manage OpenAI client
    • Batch embedding requests
    • Retry transient failures
    • Measure latency
    • Estimate embedding cost
    • Produce EmbeddedChunk objects
    """


    def __init__(
        self,
    ) -> None:

        if not settings.OPENAI_API_KEY:

            raise EmbeddingConfigurationError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.EMBEDDING_TIMEOUT_SECONDS,
        )

        self.model = settings.EMBEDDING_MODEL

        self.dimensions = (
            settings.EMBEDDING_DIMENSIONS
        )

        self.price_per_million = (
            settings.EMBEDDING_PRICE_PER_MILLION_INPUT_TOKENS
        )

    def _estimate_cost(
        self,
        token_count: int,
    ) -> float:
        """
        Estimate embedding cost in USD.

        Cost is calculated using the official
        OpenAI pricing for input tokens.
        """

        return (
            token_count
            / 1_000_000
        ) * self.price_per_million

    @retry(
        retry=retry_if_exception_type(
            (
                RateLimitError,
                APIConnectionError,
                APITimeoutError,
            )
        ),
        stop=stop_after_attempt(
            settings.EMBEDDING_MAX_RETRIES,
        ),
        wait=wait_exponential(
            multiplier=1,
            min=2,
            max=20,
        ),
        reraise=True,
    )
    def _embed_texts(
        self,
        texts: list[str],
    ):
        """
        Execute one embedding request.

        Retries automatically for transient
        OpenAI failures.
        """

        try:

            return self.client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self.dimensions,
            )

        except RateLimitError as exc:

            raise EmbeddingRateLimitError(
                "OpenAI rate limit exceeded."
            ) from exc

        except APITimeoutError as exc:

            raise EmbeddingTimeoutError(
                "Embedding request timed out."
            ) from exc

        except (
            APIConnectionError,
            APIStatusError,
        ) as exc:

            raise EmbeddingGenerationError(
                "Failed to generate embeddings."
            ) from exc

    def _build_embedded_chunks(
        self,
        chunks: list[DocumentChunk],
        vectors: Iterable[list[float]],
        processing_time_ms: float,
        total_cost: float,
    ) -> list[EmbeddedChunk]:
        """
        Convert raw vectors returned by OpenAI
        into EmbeddedChunk objects.
        """

        embedded_chunks: list[
            EmbeddedChunk
        ] = []

        chunk_count = len(
            chunks,
        )

        if chunk_count == 0:

            return embedded_chunks

        cost_per_chunk = (
            total_cost / chunk_count
        )

        latency_per_chunk = (
            processing_time_ms
            / chunk_count
        )

        for chunk, vector in zip(
            chunks,
            vectors,
            strict=True,
        ):

            embedded = EmbeddedChunk(

                chunk=chunk,

                vector=EmbeddingVector(
                    values=vector,
                ),

                metadata=EmbeddingMetadata(

                    model=self.model,

                    dimensions=self.dimensions,

                    processing_time_ms=latency_per_chunk,

                    cost_usd=cost_per_chunk,

                    cached=False,

                    validated=False,

                ),
            )

            validate_embedded_chunk(
                embedded,
            )

            embedded.metadata.validated = True

            embedded_chunks.append(
                embedded,
            )

        return embedded_chunks
    
    def embed_batch(
        self,
        chunks: list[DocumentChunk],
    ) -> list[EmbeddedChunk]:
        """
        Embed a single batch of document chunks.

        Parameters
        ----------
        chunks
            A batch of document chunks.

        Returns
        -------
        list[EmbeddedChunk]
            Embedded chunks in the same order as the
            supplied document chunks.
        """

        if not chunks:

            return []

        texts = [
            chunk.text
            for chunk in chunks
        ]

        total_tokens = sum(
            chunk.metadata.token_count
            for chunk in chunks
        )

        estimated_cost = self._estimate_cost(
            total_tokens,
        )

        start = time.perf_counter()

        response = self._embed_texts(
            texts,
        )

        processing_time_ms = (
            time.perf_counter() - start
        ) * 1000

        vectors = [
            item.embedding
            for item in response.data
        ]

        if len(vectors) != len(chunks):

            raise EmbeddingGenerationError(
                "OpenAI returned an unexpected "
                "number of embedding vectors."
            )

        return self._build_embedded_chunks(

            chunks=chunks,

            vectors=vectors,

            processing_time_ms=processing_time_ms,

            total_cost=estimated_cost,

        )

    def embed(
        self,
        batches: list[EmbeddingBatch],
    ) -> list[EmbeddedChunk]:
        """
        Embed multiple batches.

        Parameters
        ----------
        batches
            List of EmbeddingBatch objects.

        Returns
        -------
        list[EmbeddedChunk]
            Embedded chunks preserving the original
            document order.
        """

        embedded_chunks: list[
            EmbeddedChunk
        ] = []

        for batch in batches:

            embedded_chunks.extend(

                self.embed_batch(
                    batch.chunks,
                )

            )

        return embedded_chunks

    def __call__(
        self,
        batches: list[EmbeddingBatch],
    ) -> list[EmbeddedChunk]:
        """
        Convenience wrapper.

        Allows

            embedder(batches)

        instead of

            embedder.embed(batches)
        """

        return self.embed(
            batches,
        )