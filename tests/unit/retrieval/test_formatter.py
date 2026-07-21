from __future__ import annotations

import json
from uuid import uuid4

from app.retrieval.formatter import ContextFormatter
from app.retrieval.models import (
    RetrievedContext,
    RetrievalResult,
)


def make_result() -> RetrievalResult:

    contexts = [
        RetrievedContext(
            text="Semantic chunking groups related sentences together.",
            source="paper.pdf",
            page=5,
            section="Semantic Chunking",
            chunk_uuid=uuid4(),
            retrieval_score=0.91,
            reranker_score=0.98,
        ),
        RetrievedContext(
            text="Hybrid retrieval combines dense and sparse search.",
            source="paper.pdf",
            page=8,
            section="Hybrid Retrieval",
            chunk_uuid=uuid4(),
            retrieval_score=0.82,
            reranker_score=0.90,
        ),
    ]

    return RetrievalResult(
        query="What is semantic chunking?",
        contexts=contexts,
        retrieval_latency=0.37,
    )


def test_to_plain_text() -> None:

    formatter = ContextFormatter()

    result = make_result()

    text = formatter.to_plain_text(result)

    assert "Semantic chunking groups related sentences together." in text
    assert "Hybrid retrieval combines dense and sparse search." in text
    assert "paper.pdf" in text
    assert "Page: 5" in text
    assert "Section: Semantic Chunking" in text


def test_to_markdown() -> None:

    formatter = ContextFormatter()

    result = make_result()

    markdown = formatter.to_markdown(result)

    assert "## Context 1" in markdown
    assert "**Source:** paper.pdf" in markdown
    assert "**Page:** 5" in markdown
    assert "**Section:** Semantic Chunking" in markdown
    assert "Hybrid retrieval combines dense and sparse search." in markdown


def test_to_json() -> None:

    formatter = ContextFormatter()

    result = make_result()

    payload = formatter.to_json(result)

    data = json.loads(payload)

    assert len(data) == 2

    assert data[0]["source"] == "paper.pdf"
    assert data[0]["page"] == 5
    assert data[0]["section"] == "Semantic Chunking"

    assert "retrieval_score" in data[0]
    assert "reranker_score" in data[0]
    assert "chunk_uuid" in data[0]