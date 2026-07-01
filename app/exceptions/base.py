from starlette import status


class AppException(Exception):
    """
    Base exception for all application-specific errors.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.message = message
        self.status_code = status_code

        super().__init__(message)