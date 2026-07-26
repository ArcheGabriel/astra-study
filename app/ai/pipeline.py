from __future__ import annotations

from collections.abc import Iterator

from app.ai.schemas import AIResponse
from app.ai.summary_generator import SummaryGenerator
from app.ai.title_generator import TitleGenerator
from app.config.settings import settings
from app.generation.models import (
    ConversationMessage,
    GenerationRequest,
)
from app.generation.service import GenerationService
from app.models.message import ChatMessage
from app.retrieval.service import RetrievalService
from app.services.llm import LLMService


class AIPipeline:
    """
    Production AI orchestration layer.

    Responsibilities
    ----------------
    - Convert ORM chat messages into domain conversation messages.
    - Execute Retrieval-Augmented Generation.
    - Decide when long-term conversation memory should be injected.
    - Generate assistant responses.
    - Stream assistant responses.
    - Generate chat titles.
    - Generate conversation summaries.
    """

    def __init__(
        self,
        retrieval_service: RetrievalService,
        generation_service: GenerationService,
        llm_service: LLMService,
    ) -> None:
        self._retrieval_service = retrieval_service
        self._generation_service = generation_service
        self._llm_service = llm_service

    def generate_response(
        self,
        *,
        conversation: list[ChatMessage],
        user_id: int,
        summary: str | None = None,
    ) -> AIResponse:
        """
        Generate an assistant response using Retrieval-Augmented Generation.
        """

        if not conversation:
            raise ValueError(
                "Conversation cannot be empty."
            )

        latest_message = conversation[-1]

        retrieval = self._retrieval_service.retrieve(
            query=latest_message.content,
            user_id=user_id,
        )

        request = GenerationRequest(
            query=latest_message.content,
            retrieval=retrieval,
            conversation=self._to_conversation_messages(
                conversation,
            ),
            summary=self._resolve_summary(
                conversation=conversation,
                summary=summary,
            ),
        )

        response = self._generation_service.generate(
            request,
        )

        return AIResponse(
            answer=response.answer,
            citations=response.citations,
        )

    def stream_response(
        self,
        *,
        conversation: list[ChatMessage],
        user_id: int,
        summary: str | None = None,
    ) -> Iterator[str]:
        """
        Stream an assistant response using Retrieval-Augmented Generation.
        """

        if not conversation:
            raise ValueError(
                "Conversation cannot be empty."
            )

        latest_message = conversation[-1]

        retrieval = self._retrieval_service.retrieve(
            query=latest_message.content,
            user_id=user_id,
        )

        request = GenerationRequest(
            query=latest_message.content,
            retrieval=retrieval,
            conversation=self._to_conversation_messages(
                conversation,
            ),
            summary=self._resolve_summary(
                conversation=conversation,
                summary=summary,
            ),
        )

        yield from self._generation_service.stream(
            request,
        )

    def generate_title(
        self,
        *,
        first_message: str,
    ) -> str:
        """
        Generate a short AI title for a new conversation.
        """

        prompt = TitleGenerator.build_prompt(
            first_message=first_message,
        )

        return self._llm_service.generate_title(
            messages=prompt,
        )

    def generate_summary(
        self,
        *,
        existing_summary: str | None,
        conversation: list[ChatMessage],
    ) -> str:
        """
        Generate or update the conversation summary.
        """

        prompt = SummaryGenerator.build_prompt(
            existing_summary=existing_summary,
            conversation=self._to_conversation_messages(
                conversation,
            ),
        )

        return self._llm_service.generate_summary(
            messages=prompt,
        )

    @staticmethod
    def _to_conversation_messages(
        conversation: list[ChatMessage],
    ) -> list[ConversationMessage]:
        """
        Convert ORM ChatMessage models into generation domain models.
        """

        return [
            ConversationMessage(
                role=message.role,
                content=message.content,
            )
            for message in conversation
        ]

    @staticmethod
    def _resolve_summary(
        *,
        conversation: list[ChatMessage],
        summary: str | None,
    ) -> str | None:
        """
        Decide whether the conversation summary should be
        injected into the prompt.

        The summary is only used when:

        - A summary exists.
        - The conversation length exceeds the configured threshold.
        """

        if not summary:
            return None

        summary = summary.strip()

        if not summary:
            return None

        if (
            len(conversation)
            < settings.SUMMARY_INJECTION_THRESHOLD
        ):
            return None

        return summary