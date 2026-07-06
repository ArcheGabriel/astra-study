from starlette import status

from app.exceptions.base import AppException


class ChatNotFoundError(AppException):
    """
    Raised when the requested chat session
    does not exist or is inaccessible.
    """

    status_code = status.HTTP_404_NOT_FOUND

    detail = "Chat session not found."