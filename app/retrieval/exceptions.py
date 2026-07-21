class RetrievalError(Exception):
    """
    Base exception for retrieval failures.
    """


class EmptyQueryError(RetrievalError):
    """
    Raised when the supplied query is empty.
    """


class NoRetrievalResultsError(RetrievalError):
    """
    Raised when no relevant contexts could be retrieved.
    """


class RetrievalConfigurationError(RetrievalError):
    """
    Raised when the retrieval pipeline is improperly configured.
    """


class ContextFormattingError(RetrievalError):
    """
    Raised when retrieved contexts cannot be formatted for
    downstream generation.
    """