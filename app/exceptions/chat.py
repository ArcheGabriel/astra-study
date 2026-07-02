from starlette import status

from app.exceptions.base import AppException


class ChatNotFoundError(AppException):
    """
    Raised when the requested chat session
    does not exist or is inaccessible.
    """

    def __init__(self) -> None:
        super().__init__(
            message="Chat session not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )