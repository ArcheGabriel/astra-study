from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(slots=True)
class ApiResponse(Generic[T]):
    """
    Standard API response returned by Astra Study.
    """

    success: bool

    message: str

    data: T | None