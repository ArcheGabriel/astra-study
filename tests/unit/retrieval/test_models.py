from __future__ import annotations

from uuid import uuid4

from app.retrieval.models import (
    RetrievedContext,
    RetrievalResult,
)


def make_context(
    *,
    source: str = "paper.pdf",
    page: int = 5,
    section: str = "Introduction",
    retrieval_score: float = 0.81,
    reranker_score: float = 0.92,
) -> RetrievedContext:
    """
    Helper factory.
    """

    return RetrievedContext(
        text="Semantic chunking improves retrieval.",
        source=source,
        page=page,
        section=section,
        chunk_uuid=uuid4(),
        retrieval_score=retrieval_score,
        reranker_score=reranker_score,
    )


def test_best_context_returns_first() -> None:

    result = RetrievalResult(
        query="semantic chunking",
        contexts=[
            make_context(),
            make_context(source="another.pdf"),
        ],
        retrieval_latency=0.54,
    )

    assert result.best_context is result.contexts[0]


def test_sources_returns_unique_sources() -> None:

    result = RetrievalResult(
        query="query",
        contexts=[
            make_context(source="a.pdf"),
            make_context(source="b.pdf"),
            make_context(source="a.pdf"),
        ],
        retrieval_latency=0.1,
    )

    assert result.sources == [
        "a.pdf",
        "b.pdf",
    ]


def test_pages_returns_unique_pages() -> None:

    result = RetrievalResult(
        query="query",
        contexts=[
            make_context(page=1),
            make_context(page=5),
            make_context(page=1),
        ],
        retrieval_latency=0.2,
    )

    assert result.pages == [
        1,
        5,
    ]


def test_sections_returns_unique_sections() -> None:

    result = RetrievalResult(
        query="query",
        contexts=[
            make_context(section="Intro"),
            make_context(section="Methods"),
            make_context(section="Intro"),
        ],
        retrieval_latency=0.2,
    )

    assert result.sections == [
        "Intro",
        "Methods",
    ]


def test_top_k_returns_requested_number() -> None:

    result = RetrievalResult(
        query="query",
        contexts=[
            make_context(),
            make_context(),
            make_context(),
        ],
        retrieval_latency=0.1,
    )

    assert len(result.top_k(2)) == 2


def test_len_returns_number_of_contexts() -> None:

    result = RetrievalResult(
        query="query",
        contexts=[
            make_context(),
            make_context(),
        ],
        retrieval_latency=0.1,
    )

    assert len(result) == 2


def test_iter_returns_context_iterator() -> None:

    result = RetrievalResult(
        query="query",
        contexts=[
            make_context(),
            make_context(),
        ],
        retrieval_latency=0.1,
    )

    assert list(iter(result)) == result.contexts


def test_getitem_returns_context() -> None:

    result = RetrievalResult(
        query="query",
        contexts=[
            make_context(),
            make_context(),
        ],
        retrieval_latency=0.1,
    )

    assert result[1] == result.contexts[1]