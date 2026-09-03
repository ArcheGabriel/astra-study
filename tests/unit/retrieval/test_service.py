from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.config.settings import settings
from app.retrieval.base import BaseRetrievalService
from app.retrieval.exceptions import EmptyQueryError
from app.retrieval.models import RetrievalResult
from app.retrieval.service import RetrievalService
from app.reranking.models import (
    RerankedChunk,
    RerankingResult,
)
from app.search.hybrid.models import HybridSearchResult

# ``RetrievalService.retrieve`` / ``__call__`` are keyword-only
# (``*, query, user_id``) and always scoped to a tenant: this was made
# deliberate in commit b5d8d4b ("tenant isolation and graceful empty
# retrieval"), and every production caller (app/ai/pipeline.py) invokes it
# that way. That same commit also replaced the ``NoRetrievalResultsError``
# raised on an empty rerank with a graceful empty ``RetrievalResult`` that
# the generation layer relies on. These tests encode that current contract.

_USER_ID = 7


def make_hybrid_result() -> HybridSearchResult:

    return HybridSearchResult(
        chunk_uuid=uuid4(),
        document_uuid=uuid4(),
        score=0.92,
        text="Semantic chunking improves retrieval quality.",
        payload={
            "document_name": "paper.pdf",
            "page_start": 5,
            "section_title": "Semantic Chunking",
        },
    )


def make_reranking_result(
    hybrid_result: HybridSearchResult,
) -> RerankingResult:

    return RerankingResult(
        query="semantic chunking",
        total_candidates=1,
        returned_candidates=1,
        results=[
            RerankedChunk(
                result=hybrid_result,
                reranker_score=0.98,
                rank=1,
            ),
        ],
    )


def make_service() -> tuple[
    RetrievalService,
    MagicMock,
    MagicMock,
]:

    hybrid_service = MagicMock()

    reranking_service = MagicMock()

    service = RetrievalService(
        hybrid_service=hybrid_service,
        reranking_service=reranking_service,
    )

    return (
        service,
        hybrid_service,
        reranking_service,
    )


def test_empty_query_raises_error() -> None:

    service, _, _ = make_service()

    with pytest.raises(
        EmptyQueryError,
    ):
        service.retrieve(query="", user_id=_USER_ID)


def test_retrieve_success() -> None:

    (
        service,
        hybrid_service,
        reranking_service,
    ) = make_service()

    hybrid = make_hybrid_result()

    hybrid_service.return_value = [
        hybrid,
    ]

    reranking_service.return_value = make_reranking_result(
        hybrid,
    )

    result = service.retrieve(
        query="semantic chunking",
        user_id=_USER_ID,
    )

    assert result.query == "semantic chunking"

    assert len(result.contexts) == 1

    context = result.contexts[0]

    assert context.text == hybrid.text
    assert context.source == "paper.pdf"
    assert context.page == 5
    assert context.section == "Semantic Chunking"
    assert context.retrieval_score == hybrid.score
    assert context.reranker_score == 0.98

    hybrid_service.assert_called_once()

    reranking_service.assert_called_once()

    # Retrieval is tenant-scoped: the authenticated user_id must reach the
    # hybrid search, together with the configured candidate limit.
    assert hybrid_service.call_args.kwargs["user_id"] == _USER_ID
    assert (
        hybrid_service.call_args.kwargs["limit"]
        == settings.QDRANT_HYBRID_CANDIDATE_LIMIT
    )
    assert reranking_service.call_args.kwargs["top_k"] == settings.RETRIEVAL_TOP_K


def test_empty_rerank_results_return_empty_retrieval() -> None:
    """Graceful empty retrieval (commit b5d8d4b): when every candidate is
    filtered out during reranking the service returns an empty
    ``RetrievalResult`` rather than raising -- the generation layer depends
    on this to emit its "no relevant information" answer."""

    (
        service,
        hybrid_service,
        reranking_service,
    ) = make_service()

    hybrid_service.return_value = [make_hybrid_result()]

    reranking_service.return_value = RerankingResult(
        query="query",
        total_candidates=1,
        returned_candidates=0,
        results=[],
    )

    result = service.retrieve(query="query", user_id=_USER_ID)

    assert result.query == "query"
    assert result.contexts == []
    assert len(result) == 0


def test_empty_hybrid_results_return_empty_retrieval() -> None:
    """The other half of graceful empty retrieval: no hybrid candidates at
    all short-circuits to an empty ``RetrievalResult`` without reranking."""

    (
        service,
        hybrid_service,
        reranking_service,
    ) = make_service()

    hybrid_service.return_value = []

    result = service.retrieve(query="query", user_id=_USER_ID)

    assert result.contexts == []
    reranking_service.assert_not_called()


def test_callable_wrapper() -> None:

    (
        service,
        hybrid_service,
        reranking_service,
    ) = make_service()

    hybrid = make_hybrid_result()

    hybrid_service.return_value = [
        hybrid,
    ]

    reranking_service.return_value = make_reranking_result(
        hybrid,
    )

    result = service(query="semantic chunking", user_id=_USER_ID)

    assert len(result.contexts) == 1
    assert result.query == "semantic chunking"
    assert hybrid_service.call_args.kwargs["user_id"] == _USER_ID


def test_base_contract_is_keyword_only_and_tenant_scoped() -> None:
    """The abstract base's ``__call__`` fallback must forward the keyword-only,
    tenant-scoped contract to ``retrieve`` for any subclass that does not
    override it."""

    seen: dict[str, object] = {}

    class _Impl(BaseRetrievalService):
        def retrieve(self, *, query: str, user_id: int) -> RetrievalResult:
            seen["query"] = query
            seen["user_id"] = user_id
            return RetrievalResult(query=query, contexts=[], retrieval_latency=0.0)

    _Impl()(query="hello", user_id=_USER_ID)
    assert seen == {"query": "hello", "user_id": _USER_ID}

    with pytest.raises(TypeError):
        _Impl()("hello")  # type: ignore[call-arg]  # positional call is rejected