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
        query: str,
    ) -> RetrievalResult:
        """
        Execute the complete retrieval pipeline.
        """

    def __call__(
        self,
        query: str,
    ) -> RetrievalResult:
        """
        Allow the service to be invoked like a function.
        """

        return self.retrieve(query)