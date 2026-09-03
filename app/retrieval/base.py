from __future__ import annotations

from abc import ABC, abstractmethod

from app.retrieval.models import RetrievalResult


class BaseRetrievalService(ABC):
    """
    Base contract for all retrieval implementations.
    """

    @abstractmethod
    def retrieve(
        self,
        *,
        query: str,
        user_id: int,
    ) -> RetrievalResult:
        """
        Execute the complete retrieval pipeline.

        Retrieval is keyword-only and always tenant-scoped: results are
        restricted to documents owned by ``user_id``. An empty result is
        returned as an empty ``RetrievalResult`` rather than raising.
        """

    def __call__(
        self,
        *,
        query: str,
        user_id: int,
    ) -> RetrievalResult:
        """
        Allow the service to be invoked like a function.
        """

        return self.retrieve(
            query=query,
            user_id=user_id,
        )
