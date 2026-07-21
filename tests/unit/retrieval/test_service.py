from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.retrieval.exceptions import (
    EmptyQueryError,
    NoRetrievalResultsError,
)
from app.retrieval.service import RetrievalService
from app.reranking.models import (
    RerankedChunk,
    RerankingResult,
)
from app.search.hybrid.models import HybridSearchResult


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
        service.retrieve("")


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
        "semantic chunking",
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


def test_no_results_raise_exception() -> None:

    (
        service,
        hybrid_service,
        reranking_service,
    ) = make_service()

    hybrid = make_hybrid_result()

    hybrid_service.return_value = [
        hybrid,
    ]

    reranking_service.return_value = RerankingResult(
        query="query",
        total_candidates=1,
        returned_candidates=0,
        results=[],
    )

    with pytest.raises(
        NoRetrievalResultsError,
    ):
        service.retrieve(
            "query",
        )


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

    result = service(
        "semantic chunking",
    )

    assert len(result.contexts) == 1