class SparseSearchError(Exception):
    """
    Base exception for all sparse search errors.
    """


class SparseEncoderError(SparseSearchError):
    """
    Raised when sparse embeddings cannot be generated.
    """


class SparseConfigurationError(SparseSearchError):
    """
    Raised when the sparse encoder configuration
    is invalid.
    """


class SparseCollectionError(SparseSearchError):
    """
    Raised when a sparse vector collection operation
    fails.
    """


class SparseSearchExecutionError(SparseSearchError):
    """
    Raised when sparse retrieval fails.
    """