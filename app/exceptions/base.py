from starlette import status


class AppException(Exception):
    """
    Base exception for all application-specific errors.
    """

    status_code = status.HTTP_400_BAD_REQUEST

    detail = "Application error."

    def __init__(
        self,
        message: str | None = None,
    ) -> None:
        """
        Initialize the exception.

        If no message is supplied, use the class-level
        `detail` attribute.
        """

        self.message = message or self.detail

        self.status_code = self.__class__.status_code

        super().__init__(self.message)