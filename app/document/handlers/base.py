from abc import ABC, abstractmethod
from dataclasses import dataclass

from markdown_it.token import Token

from app.document.models import DocumentBlock


@dataclass(slots=True)
class HandlerResult:
    """
    Result returned by every document handler.
    """

    block: DocumentBlock | None

    next_index: int


class BaseHandler(ABC):
    """
    Base class for all document handlers.
    """

    @abstractmethod
    def can_handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> bool:
        """
        Returns True if this handler can process the
        current token.
        """

        raise NotImplementedError

    @abstractmethod
    def handle(
        self,
        tokens: list[Token],
        index: int,
    ) -> HandlerResult:
        """
        Converts one logical markdown block into a
        DocumentBlock.
        """

        raise NotImplementedError