from starlette import status

from app.exceptions.base import AppException


class InvalidCredentialsError(AppException):
    """
    Raised when the provided email or password is incorrect.
    """

    def __init__(self) -> None:
        super().__init__(
            message="Invalid email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InactiveUserError(AppException):
    """
    Raised when an inactive user attempts to log in.
    """

    def __init__(self) -> None:
        super().__init__(
            message="Your account has been deactivated.",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class AuthenticationError(AppException):
    """
    Raised when authentication fails because the access token
    is invalid, expired, or missing.
    """

    def __init__(self) -> None:
        super().__init__(
            message="Could not validate credentials.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )