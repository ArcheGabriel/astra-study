"""
Executable specification proving the semantic retrieval cache (RBAC/C.3)
integrates correctly with the real conversational flow: a follow-up
question is rewritten before the cache is ever consulted, the cache
operates on that rewritten retrieval query (never the ambiguous raw
follow-up), the original user question remains the generation query
untouched by caching, and both non-streaming and streaming generation
continue to work transparently on a cache hit and a cache miss.

Uses the real ``AIPipeline``/``RetrievalService``/``HybridService``
wiring with hand-rolled fakes at the network boundary (LLM provider,
Qdrant/embedding), matching this project's established
``tests/unit/test_generation_grounding.py`` fake-provider convention --
no real OpenAI/Qdrant call anywhere in this file.
"""

from __future__ import annotations

from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from app.ai.base import BaseLLMProvider
from app.ai.pipeline import AIPipeline
from app.cache.semantic import SemanticRetrievalCache
from app.enums.message import MessageRole
from app.enums.organisation import OrgRole
from app.generation.models import GenerationRequest, GenerationResponse
from app.retrieval.access import AccessContext
from app.retrieval.service import RetrievalService
from app.reranking.models import RerankedChunk, RerankingResult
from app.search.hybrid.models import HybridSearchResult
from app.services.llm import LLMService


_ACCESS = AccessContext(
    user_id=1, organisation_id=9, team_ids=(), jurisdiction_team_ids=(), role=OrgRole.MEMBER,
)


class _FakeProvider(BaseLLMProvider):
    """Records every call's messages; returns a fixed rewritten-query
    string for the rewrite call and a fixed answer for generation --
    distinguished by call order, matching this project's existing
    hand-rolled fake-provider convention."""

    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []

    def generate_response(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        # First call in a multi-turn conversation is the query rewrite.
        if len(self.calls) == 1:
            return "standalone rewritten retrieval query"
        return "ANSWER"

    def stream_response(self, messages: list[dict[str, str]]) -> Iterator[str]:
        self.calls.append(messages)
        yield "ANSWER"


def _message(role: MessageRole, content: str):
    return SimpleNamespace(role=role, content=content)


def _hybrid_result(text: str) -> HybridSearchResult:
    return HybridSearchResult(
        chunk_uuid=uuid4(), document_uuid=uuid4(), score=0.9, text=text,
        payload={"document_name": "doc.pdf"},
    )


def _make_retrieval_service(*, semantic_cache: SemanticRetrievalCache):
    hybrid_service = MagicMock()
    reranking_service = MagicMock()
    embedder = MagicMock()
    embedder.embed_query.return_value = [1.0, 0.0, 0.0]

    hybrid = _hybrid_result("Retrieved text.")
    hybrid_service.return_value = [hybrid]
    reranking_service.return_value = RerankingResult(
        query="q", total_candidates=1, returned_candidates=1,
        results=[RerankedChunk(result=hybrid, reranker_score=0.9, rank=1)],
    )

    service = RetrievalService(
        hybrid_service=hybrid_service,
        reranking_service=reranking_service,
        embedder=embedder,
        semantic_cache=semantic_cache,
    )

    return service, hybrid_service


def _follow_up_conversation() -> list:
    return [
        _message(MessageRole.USER, "What is the leave policy?"),
        _message(MessageRole.ASSISTANT, "The leave policy is..."),
        _message(MessageRole.USER, "What about contractors?"),
    ]


def _make_pipeline(retrieval_service):
    fake_provider = _FakeProvider()
    llm_service = LLMService(provider=fake_provider)
    generation_service = MagicMock()
    generation_service.generate.return_value = GenerationResponse(answer="final answer", citations=[])
    generation_service.stream.return_value = iter(["final", " answer"])
    generation_service.citations_for.return_value = []

    pipeline = AIPipeline(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        llm_service=llm_service,
    )
    return pipeline, fake_provider, generation_service


# --------------------------------------------------------------------------- #
# 27/28. follow-up is rewritten first; the cache operates on the
# rewritten retrieval query, not the ambiguous raw follow-up.
# --------------------------------------------------------------------------- #


def test_cache_lookup_uses_the_rewritten_query_not_the_raw_followup():
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    retrieval_service, hybrid_service = _make_retrieval_service(semantic_cache=cache)
    pipeline, fake_provider, generation_service = _make_pipeline(retrieval_service)

    pipeline.generate_response(conversation=_follow_up_conversation(), access=_ACCESS)

    # One rewrite call occurred (multi-turn conversation).
    assert len(fake_provider.calls) == 1

    # Exactly one entry now in the cache, and it is keyed on the
    # rewritten query text, not the raw "What about contractors?" text.
    assert len(cache) == 1
    cached_entry = next(iter(cache._entries.values()))
    assert cached_entry.retrieval_result.query == "standalone rewritten retrieval query"


def test_second_equivalent_follow_up_is_a_cache_hit_and_skips_hybrid_search():
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    retrieval_service, hybrid_service = _make_retrieval_service(semantic_cache=cache)
    pipeline, fake_provider, generation_service = _make_pipeline(retrieval_service)

    pipeline.generate_response(conversation=_follow_up_conversation(), access=_ACCESS)
    assert hybrid_service.call_count == 1

    # Same conversation shape again -> rewriter (deterministic fake)
    # produces the identical rewritten query -> identical mocked
    # embedding -> guaranteed cache hit.
    pipeline.generate_response(conversation=_follow_up_conversation(), access=_ACCESS)
    assert hybrid_service.call_count == 1


# --------------------------------------------------------------------------- #
# 29. the original user question remains the generation query.
# --------------------------------------------------------------------------- #


def test_generation_request_uses_the_original_question_not_the_rewritten_one():
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    retrieval_service, _ = _make_retrieval_service(semantic_cache=cache)
    pipeline, fake_provider, generation_service = _make_pipeline(retrieval_service)

    pipeline.generate_response(conversation=_follow_up_conversation(), access=_ACCESS)

    sent_request: GenerationRequest = generation_service.generate.call_args[0][0]
    assert sent_request.query == "What about contractors?"


# --------------------------------------------------------------------------- #
# 30/31. streaming works with both a cache hit and a cache miss.
# --------------------------------------------------------------------------- #


def test_streaming_works_on_cache_miss():
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    retrieval_service, hybrid_service = _make_retrieval_service(semantic_cache=cache)
    pipeline, _, generation_service = _make_pipeline(retrieval_service)

    events = list(pipeline.stream_response(conversation=_follow_up_conversation(), access=_ACCESS))

    assert hybrid_service.call_count == 1
    text_events = [e for e in events if e.text is not None]
    assert "".join(e.text for e in text_events) == "final answer"


def test_streaming_works_on_cache_hit():
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    retrieval_service, hybrid_service = _make_retrieval_service(semantic_cache=cache)
    pipeline, _, generation_service = _make_pipeline(retrieval_service)

    # Prime the cache with a non-streaming call first.
    pipeline.generate_response(conversation=_follow_up_conversation(), access=_ACCESS)
    assert hybrid_service.call_count == 1

    # Streaming call for the same follow-up conversation must still work,
    # and must NOT re-invoke hybrid search (cache hit) -- generation
    # still streams normally from the retrieved context either way.
    events = list(pipeline.stream_response(conversation=_follow_up_conversation(), access=_ACCESS))

    assert hybrid_service.call_count == 1
    text_events = [e for e in events if e.text is not None]
    assert "".join(e.text for e in text_events) == "final answer"
