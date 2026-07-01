from starlette import status

from app.exceptions.base import AppException


class EmailAlreadyExistsError(AppException):
    """
    Raised when an email is already registered.
    """

    def __init__(self) -> None:
        super().__init__(
            message="Email is already registered.",
            status_code=status.HTTP_409_CONFLICT,
        )


class UsernameAlreadyExistsError(AppException):
    """
    Raised when a username is already taken.
    """

    def __init__(self) -> None:
        super().__init__(
            message="Username is already taken.",
            status_code=status.HTTP_409_CONFLICT,
        )