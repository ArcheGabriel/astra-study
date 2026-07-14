"""
Custom exceptions for the embeddings module.
"""


class EmbeddingError(Exception):
    """
    Base exception for all embedding-related errors.
    """


class EmbeddingConfigurationError(EmbeddingError):
    """
    Raised when the embedding configuration is invalid.

    Examples:
    - Missing API key
    - Unsupported embedding model
    - Invalid batch configuration
    """


class EmbeddingValidationError(EmbeddingError):
    """
    Raised when an embedding fails validation.

    Examples:
    - Empty embedding
    - Incorrect dimensions
    - NaN values
    """


class EmbeddingGenerationError(EmbeddingError):
    """
    Raised when the embedding provider fails to
    generate embeddings.
    """


class EmbeddingBatchError(EmbeddingError):
    """
    Raised when an embedding batch is invalid.

    Examples:
    - Empty batch
    - Batch exceeds configured limits
    """


class EmbeddingCacheError(EmbeddingError):
    """
    Raised when the embedding cache encounters an error.
    """


class EmbeddingRateLimitError(EmbeddingError):
    """
    Raised when the embedding provider rate limits
    requests.
    """


class EmbeddingTimeoutError(EmbeddingError):
    """
    Raised when an embedding request times out.
    """