from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Standard success API response.
    """

    success: bool = Field(
        default=True,
        description="Indicates whether the request was successful.",
    )

    message: str = Field(
        ...,
        description="Human-readable success message.",
    )

    data: T | None = Field(
        default=None,
        description="Response payload.",
    )


class ErrorResponse(BaseModel):
    """
    Standard error API response.
    """

    success: bool = Field(
        default=False,
        description="Indicates whether the request failed.",
    )

    message: str = Field(
        ...,
        description="Human-readable error message.",
    )

    errors: list[dict] | None = Field(
        default=None,
        description="Additional validation or error details.",
    )