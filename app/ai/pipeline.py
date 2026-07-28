from __future__ import annotations

from collections.abc import Iterator

from app.ai.query_rewriter import QueryRewriter
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
from app.enums.message import MessageRole
from langsmith import traceable


class AIPipeline:
    """
    Production AI orchestration layer.

    Responsibilities
    ----------------
    - Convert ORM chat messages into domain conversation messages.
    - Rewrite conversational queries into standalone retrieval queries.
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

    @traceable(
        name="Generate AI Response",
        run_type="chain",
    )
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

        retrieval_query = self._build_retrieval_query(
            conversation=conversation,
        )

        retrieval = self._retrieval_service.retrieve(
            query=retrieval_query,
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

    @traceable(
        name="Generate Streaming Response",
        run_type="chain",
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

        retrieval_query = self._build_retrieval_query(
            conversation=conversation,
        )

        retrieval = self._retrieval_service.retrieve(
            query=retrieval_query,
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

    @traceable(
        name="Generate Chat Title",
        run_type="llm",
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

    @traceable(
        name="Generate Conversation Summary",
        run_type="llm",
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

    @traceable(
        name="Build Retrieval Query",
        run_type="chain",
    )
    def _build_retrieval_query(
        self,
        *,
        conversation: list[ChatMessage],
    ) -> str:
        """
        Build the query used for document retrieval.

        Conversational follow-up questions are rewritten into
        standalone queries before retrieval.

        The original user question is preserved for generation.
        """

        latest_message = conversation[-1]

        user_message_count = sum(
            1
            for message in conversation
            if message.role == MessageRole.USER
        )

        if user_message_count <= 1:
            return latest_message.content

        history_window = conversation[
            -settings.QUERY_REWRITE_HISTORY_WINDOW :
        ]

        prompt = QueryRewriter.build_prompt(
            conversation=self._to_conversation_messages(
                history_window,
            ),
        )

        rewritten_query = (
            self._llm_service.rewrite_query(
                messages=prompt,
            )
        )
        
        print("\n==============================")
        print("Original Query :", latest_message.content)
        print("Retrieval Query:", rewritten_query)
        print("==============================\n")

        if not rewritten_query:
            return latest_message.content

        return rewritten_query

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

    @traceable(
        name="Resolve Conversation Summary",
        run_type="chain",
    )
    def _resolve_summary(
        self,
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