from __future__ import annotations


class RerankerError(Exception):
    """
    Base exception for all reranker related errors.
    """

    pass


class ModelLoadError(RerankerError):
    """
    Raised when the reranker model cannot be loaded.

    Possible causes
    ---------------
    - Invalid model identifier
    - Missing internet connection
    - Corrupted HuggingFace cache
    - Unsupported model architecture
    - Missing dependencies
    """

    def __init__(
        self,
        model_name: str,
        reason: str,
    ) -> None:
        self.model_name = model_name
        self.reason = reason

        super().__init__(
            f"Failed to load reranker model "
            f"'{model_name}'. {reason}"
        )


class PredictionError(RerankerError):
    """
    Raised when the reranker fails while computing scores.
    """

    def __init__(
        self,
        reason: str,
    ) -> None:
        self.reason = reason

        super().__init__(
            f"Failed to compute reranker scores. {reason}"
        )


class EmptyCandidateError(RerankerError):
    """
    Raised when reranking is attempted on an empty
    candidate list.

    Normally this indicates that retrieval returned
    no relevant documents.
    """

    def __init__(self) -> None:
        super().__init__(
            "Cannot rerank an empty candidate list."
        )


class InvalidTopKError(RerankerError):
    """
    Raised when an invalid top_k value is supplied.
    """

    def __init__(
        self,
        top_k: int,
    ) -> None:
        self.top_k = top_k

        super().__init__(
            f"top_k must be greater than zero. "
            f"Received {top_k}."
        )


class InvalidQueryError(RerankerError):
    """
    Raised when the supplied query is empty.
    """

    def __init__(self) -> None:
        super().__init__(
            "Query cannot be empty."
        )


class CandidateFormatError(RerankerError):
    """
    Raised when one or more retrieved candidates are malformed.

    Examples
    --------
    - Missing document
    - Missing text
    - Invalid metadata
    - Invalid score
    """

    def __init__(
        self,
        reason: str,
    ) -> None:
        self.reason = reason

        super().__init__(
            f"Invalid retrieval candidate. {reason}"
        )