from __future__ import annotations

from abc import ABC, abstractmethod

from app.retrieval.access import AccessContext
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
        access: AccessContext,
    ) -> RetrievalResult:
        """
        Execute the complete retrieval pipeline.

        Retrieval is keyword-only and always tenant-scoped: results are
        restricted to documents owned by ``access.user_id``. ``access`` is
        the single trusted authorization-context input -- it is not yet
        used for organisation/team/role-based filtering (that is RBAC-5C).
        An empty result is returned as an empty ``RetrievalResult`` rather
        than raising.
        """

    def __call__(
        self,
        *,
        query: str,
        access: AccessContext,
    ) -> RetrievalResult:
        """
        Allow the service to be invoked like a function.
        """

        return self.retrieve(
            query=query,
            access=access,
        )
