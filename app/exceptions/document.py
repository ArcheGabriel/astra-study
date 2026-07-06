from fastapi import status

from app.exceptions.base import AppException


class InvalidDocumentTypeError(AppException):
    """
    Raised when an unsupported file type is uploaded.
    """

    status_code = status.HTTP_400_BAD_REQUEST

    detail = (
        "Unsupported document type. "
        "Supported types are PDF, DOCX, PPTX, TXT, Markdown, PNG and JPEG."
    )


class EmptyDocumentError(AppException):
    """
    Raised when an empty document is uploaded.
    """

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "Uploaded document is empty."


class DocumentTooLargeError(AppException):
    """
    Raised when a document exceeds the allowed size.
    """

    status_code = status.HTTP_413_CONTENT_TOO_LARGE

    detail = "Uploaded document exceeds the maximum allowed size."


class DocumentNotFoundError(AppException):
    """
    Raised when a requested document does not exist
    or does not belong to the current user.
    """

    status_code = status.HTTP_404_NOT_FOUND

    detail = "Document not found."