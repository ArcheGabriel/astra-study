from starlette import status

from app.exceptions.base import AppException


class InvalidCredentialsError(AppException):
    """
    Raised when the provided email or password is incorrect.
    """

    status_code = status.HTTP_401_UNAUTHORIZED

    detail = "Invalid email or password."


class InactiveUserError(AppException):
    """
    Raised when an inactive user attempts to log in.
    """

    status_code = status.HTTP_403_FORBIDDEN

    detail = "Your account has been deactivated."


class AuthenticationError(AppException):
    """
    Raised when authentication fails because the access token
    is invalid, expired, or missing.
    """

    status_code = status.HTTP_401_UNAUTHORIZED

    detail = "Could not validate credentials."