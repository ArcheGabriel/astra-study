from starlette import status

from app.exceptions.base import AppException


class EmailAlreadyExistsError(AppException):
    """
    Raised when an email is already registered.
    """

    status_code = status.HTTP_409_CONFLICT

    detail = "Email is already registered."


class UsernameAlreadyExistsError(AppException):
    """
    Raised when a username is already taken.
    """

    status_code = status.HTTP_409_CONFLICT

    detail = "Username is already taken."