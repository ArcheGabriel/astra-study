"""
Executable specification for the generation grounding contract.

Astra Study is intended to be strictly document-grounded: when the
retrieved context does not contain enough information to answer the
user's question, the model must abstain rather than answer from
general/pretrained/world knowledge, and must never offer or suggest
providing information beyond the retrieved context.

Manual acceptance testing found a real gap: ``SYSTEM_PROMPT``
(``app/generation/prompts.py``) told the model to state when the
documents were insufficient, but never told it not to *then* offer a
general explanation anyway -- which the model did. This is a prompt-only
gap: nothing in ``GenerationService``/``RetrievalService`` distinguishes
"context exists but doesn't answer the question" from "context exists
and does answer it" (that judgment is left entirely to the LLM); the
only lever this codebase has to constrain that judgment is the system
prompt actually sent on the call. These tests therefore verify the real,
current ``SYSTEM_PROMPT`` -- via the real ``PromptBuilder`` ->
``GenerationService`` flow, never a hand-copied string -- rather than
asserting an invented sentence never actually enforced.

No OpenAI call is ever made: ``GenerationService`` is exercised with a
deterministic fake ``BaseLLMProvider`` (matching this project's existing
hand-rolled-fake convention, e.g. ``tests/unit/test_conversation_memory.py``),
which records exactly the messages it was called with.
"""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import pytest

from app.ai.base import BaseLLMProvider
from app.enums.message import MessageRole
from app.generation.models import GenerationRequest
from app.generation.prompt_builder import PromptBuilder
from app.generation.prompts import SYSTEM_PROMPT
from app.generation.service import GenerationService
from app.retrieval.models import RetrievalResult, RetrievedContext
from app.services.llm import LLMService


# --------------------------------------------------------------------------- #
# Fakes
# --------------------------------------------------------------------------- #


class _FakeProvider(BaseLLMProvider):
    """
    Deterministic stand-in for ``OpenAIProvider`` -- never calls OpenAI.

    Records every call's messages so tests can inspect exactly what was
    sent to "the model", and whether it was called at all.
    """

    def __init__(self, response: str = "ANSWER") -> None:
        self.response = response
        self.calls: list[list[dict[str, str]]] = []

    def generate_response(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        return self.response

    def stream_response(self, messages: list[dict[str, str]]) -> Iterator[str]:
        self.calls.append(messages)
        yield self.response

    @property
    def called(self) -> bool:
        return bool(self.calls)

    @property
    def last_messages(self) -> list[dict[str, str]]:
        return self.calls[-1]


def _make_service(provider: _FakeProvider) -> GenerationService:
    return GenerationService(
        prompt_builder=PromptBuilder(),
        llm_service=LLMService(provider=provider),
    )


def _context(text: str) -> RetrievedContext:
    return RetrievedContext(
        text=text,
        source="doc.pdf",
        chunk_uuid=uuid4(),
        retrieval_score=0.9,
        reranker_score=0.9,
    )


def _retrieval(chunks: list[str], *, query: str = "query") -> RetrievalResult:
    return RetrievalResult(
        query=query,
        contexts=[_context(text) for text in chunks],
        retrieval_latency=0.0,
    )


def _request(*, query: str, retrieval: RetrievalResult) -> GenerationRequest:
    return GenerationRequest(query=query, retrieval=retrieval)


# --------------------------------------------------------------------------- #
# A. Supported answer -- generation path is unaffected by the new rules
# --------------------------------------------------------------------------- #


def test_generation_returns_llm_answer_when_context_supports_it():
    provider = _FakeProvider(response="Paris is the capital of France.")
    service = _make_service(provider)

    request = _request(
        query="What is the capital of France?",
        retrieval=_retrieval(["France's capital city is Paris."]),
    )

    response = service.generate(request)

    assert response.answer == "Paris is the capital of France."
    assert provider.called

    system_messages = [
        m for m in provider.last_messages if m["role"] == MessageRole.SYSTEM.value
    ]
    # The real, current SYSTEM_PROMPT constant is what was sent -- never a
    # hand-copied duplicate of it.
    assert system_messages[0]["content"] == SYSTEM_PROMPT.strip()


# --------------------------------------------------------------------------- #
# B/D. Insufficient context -- the grounding contract sent on this call
# must actually prohibit a general-knowledge fallback
# --------------------------------------------------------------------------- #


def test_system_prompt_sent_forbids_general_knowledge_and_offers_beyond_context():
    """
    GenerationService has no way to know, at build time, whether the
    retrieved context actually answers the question -- that judgment is
    the LLM's alone (confirmed by investigation: no relevance/sufficiency
    threshold exists anywhere in retrieval/reranking). The retrieved
    chunk below is real, non-empty, but topically unrelated to the
    question -- exactly the "insufficient context" case that previously
    produced an unprompted "I can give a general explanation..." offer.

    The only mechanism available to prevent that here is the system
    prompt itself, so this test inspects the real prompt actually
    delivered to the model on this exact call and requires it to name
    each of the two behaviors the investigation identified as missing:
    (1) a prohibition on using general/pretrained/outside knowledge, and
    (2) a prohibition on offering/suggesting anything beyond the
    retrieved context. It checks for the presence of these two distinct
    concepts via keyword matching, not a single hand-copied sentence, so
    it verifies the actual enforced contract rather than an invented one.
    """

    provider = _FakeProvider(
        response=(
            "The provided documents do not contain enough information "
            "to answer this question."
        ),
    )
    service = _make_service(provider)

    request = _request(
        query="What is RAG?",
        retrieval=_retrieval(["Unrelated chunk about BERT pretraining objectives."]),
    )

    service.generate(request)

    system_prompt_sent = next(
        m["content"]
        for m in provider.last_messages
        if m["role"] == MessageRole.SYSTEM.value
    )
    lowered = system_prompt_sent.lower()

    # Concept 1: no general/pretrained/outside knowledge as a factual source.
    assert "general" in lowered
    assert "knowledge" in lowered
    assert "pretrained" in lowered or "outside" in lowered

    # Concept 2: no offering/suggesting anything beyond the retrieved context.
    assert "offer" in lowered or "suggest" in lowered
    assert "beyond the retrieved context" in lowered

    # This is genuinely the same SYSTEM_PROMPT as the supported-answer case
    # -- the contract applies unconditionally, not via a separate
    # "insufficient context" branch that could be bypassed.
    assert system_prompt_sent == SYSTEM_PROMPT.strip()


def test_grounding_contract_applies_identically_regardless_of_context_relevance():
    """
    Proves there is exactly one grounding prompt path, not a
    relevance-dependent one: the system message sent is byte-identical
    whether the retrieved chunk happens to answer the question or not.
    (The absence of any relevance/sufficiency branch in the production
    code is exactly why the system prompt itself has to carry the whole
    grounding contract -- see the investigation this fix is based on.)
    """

    supported_provider = _FakeProvider(response="A")
    unsupported_provider = _FakeProvider(response="B")

    _make_service(supported_provider).generate(
        _request(
            query="What is the capital of France?",
            retrieval=_retrieval(["France's capital city is Paris."]),
        ),
    )
    _make_service(unsupported_provider).generate(
        _request(
            query="What is RAG?",
            retrieval=_retrieval(["Unrelated chunk about BERT pretraining."]),
        ),
    )

    supported_system = next(
        m["content"] for m in supported_provider.last_messages
        if m["role"] == MessageRole.SYSTEM.value
    )
    unsupported_system = next(
        m["content"] for m in unsupported_provider.last_messages
        if m["role"] == MessageRole.SYSTEM.value
    )

    assert supported_system == unsupported_system == SYSTEM_PROMPT.strip()


# --------------------------------------------------------------------------- #
# C. Zero retrieved context -- existing deterministic behavior, unchanged
# --------------------------------------------------------------------------- #


def test_zero_context_returns_deterministic_message_without_calling_llm():
    provider = _FakeProvider(response="should never be returned")
    service = _make_service(provider)

    request = _request(query="What is RAG?", retrieval=_retrieval([]))

    response = service.generate(request)

    assert not provider.called, "the LLM must not be called when retrieval is empty"
    assert response.answer == (
        "I couldn't find any relevant information in your uploaded "
        "documents that answers this question."
    )
    assert response.citations == []


def test_zero_context_stream_yields_deterministic_message_without_calling_llm():
    provider = _FakeProvider(response="should never be returned")
    service = _make_service(provider)

    request = _request(query="What is RAG?", retrieval=_retrieval([]))

    chunks = list(service.stream(request))

    assert not provider.called, "the LLM must not be called when retrieval is empty"
    assert chunks == [
        "I couldn't find any relevant information in your uploaded "
        "documents that answers this question."
    ]


def test_non_empty_context_does_invoke_the_llm():
    """
    Complements the two zero-context tests above: confirms the LLM *is*
    invoked as soon as retrieval returns at least one chunk, regardless
    of that chunk's actual relevance -- the boundary the grounding
    contract exists to police is entirely inside this branch, not at the
    empty/non-empty split.
    """

    provider = _FakeProvider(response="answer")
    service = _make_service(provider)

    request = _request(
        query="What is RAG?",
        retrieval=_retrieval(["A single, possibly unrelated chunk."]),
    )

    service.generate(request)

    assert provider.called
