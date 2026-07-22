from __future__ import annotations

from collections.abc import Iterator

from app.ai.title_generator import TitleGenerator
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
    - Execute document retrieval.
    - Delegate answer generation.
    - Preserve title generation.
    - Provide streaming responses.
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
        conversation: list[ChatMessage],
    ) -> str:
        """
        Generate an assistant response using Retrieval-Augmented Generation.
        """

        if not conversation:
            raise ValueError(
                "Conversation cannot be empty."
            )

        latest_message = conversation[-1]

        retrieval = self._retrieval_service.retrieve(
            latest_message.content,
        )

        request = GenerationRequest(
            query=latest_message.content,
            retrieval=retrieval,
            conversation=self._to_conversation_messages(
                conversation,
            ),
        )

        response = self._generation_service.generate(
            request,
        )

        return response.answer

    def stream_response(
        self,
        conversation: list[ChatMessage],
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
            latest_message.content,
        )

        request = GenerationRequest(
            query=latest_message.content,
            retrieval=retrieval,
            conversation=self._to_conversation_messages(
                conversation,
            ),
        )

        yield from self._generation_service.stream(
            request,
        )

    def generate_title(
        self,
        first_message: str,
    ) -> str:
        """
        Generate a title for a newly created conversation.
        """

        prompt = TitleGenerator.build_prompt(
            first_message=first_message,
        )

        return self._llm_service.generate_title(
            messages=prompt,
        )

    @staticmethod
    def _to_conversation_messages(
        conversation: list[ChatMessage],
    ) -> list[ConversationMessage]:
        """
        Convert ORM ChatMessage objects into generation domain models.
        """

        return [
            ConversationMessage(
                role=message.role,
                content=message.content,
            )
            for message in conversation
        ]