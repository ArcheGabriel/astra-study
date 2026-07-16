from __future__ import annotations


class DenseSearchError(Exception):
    """
    Base exception for all dense search errors.
    """


class DenseSearchConfigurationError(DenseSearchError):
    """
    Raised when the dense search system has an
    invalid or missing configuration.
    """


class CollectionAlreadyExistsError(DenseSearchError):
    """
    Raised when attempting to create a collection
    that already exists.
    """


class CollectionNotFoundError(DenseSearchError):
    """
    Raised when a collection cannot be found.
    """


class CollectionCreationError(DenseSearchError):
    """
    Raised when a collection cannot be created.
    """


class CollectionDeletionError(DenseSearchError):
    """
    Raised when a collection cannot be deleted.
    """


class PointInsertionError(DenseSearchError):
    """
    Raised when vectors cannot be inserted into
    Qdrant.
    """


class SearchExecutionError(DenseSearchError):
    """
    Raised when similarity search fails.
    """


class InvalidSearchQueryError(DenseSearchError):
    """
    Raised when an invalid query is supplied.
    """


class InvalidPayloadError(DenseSearchError):
    """
    Raised when a payload cannot be converted into
    a Qdrant point.
    """