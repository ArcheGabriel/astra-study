from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.enums.message import MessageRole
from app.retrieval.models import RetrievalResult


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    """
    Domain representation of a conversation message.

    This model is intentionally independent of both the
    database ORM model and any LLM provider implementation.
    """

    role: MessageRole
    content: str


@dataclass(frozen=True, slots=True)
class LLMMessage:
    """
    Provider-agnostic message exchanged between the
    Prompt Builder and the LLM layer.

    The LLM provider is responsible for converting this
    model into the provider-specific request format.
    """

    role: MessageRole
    content: str


@dataclass(frozen=True, slots=True)
class Citation:
    """
    Represents a source citation supporting the generated answer.
    """

    source: str
    page: int | None = None
    section: str | None = None
    source_type: str | None = None
    sheet_name: str | None = None
    heading_path: list[str] | None = None
    block_type: str | None = None
    chunk_id: str | None = None
    provenance: list[dict[str, Any]] | None = None


@dataclass(frozen=True, slots=True)
class StreamEvent:
    """Internal streaming event; text and citations never share a payload."""
    text: str | None = None
    citations: list[Citation] | None = None


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """
    Token usage statistics returned by the LLM provider.
    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """
    Input required by the Prompt Builder and Generation layer.
    """

    query: str

    retrieval: RetrievalResult

    conversation: list[ConversationMessage] = field(default_factory=list)

    # Long-term conversational memory.
    # This is optional and is injected only when the AI pipeline
    # determines that the conversation is long enough to benefit
    # from summarized history.
    summary: str | None = None

    temperature: float = 0.2

    max_tokens: int = 2048


@dataclass(frozen=True, slots=True)
class GenerationResponse:
    """
    Structured response produced by the Generation layer.
    """

    answer: str

    citations: list[Citation] = field(default_factory=list)

    usage: TokenUsage | None = None

    model: str | None = None

    finish_reason: str | None = None

    latency_ms: int | None = None
