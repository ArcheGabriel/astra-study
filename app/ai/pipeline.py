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
    StreamEvent,
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

        resolved_summary = self._resolve_summary(
            conversation=conversation,
            summary=summary,
        )

        request = GenerationRequest(
            query=latest_message.content,
            retrieval=retrieval,
            conversation=self._to_conversation_messages(
                self._generation_history(
                    conversation=conversation,
                    summary=resolved_summary,
                ),
            ),
            summary=resolved_summary,
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
    ) -> Iterator[StreamEvent]:
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

        resolved_summary = self._resolve_summary(
            conversation=conversation,
            summary=summary,
        )

        request = GenerationRequest(
            query=latest_message.content,
            retrieval=retrieval,
            conversation=self._to_conversation_messages(
                self._generation_history(
                    conversation=conversation,
                    summary=resolved_summary,
                ),
            ),
            summary=resolved_summary,
        )

        answer_parts: list[str] = []
        for text in self._generation_service.stream(request):
            answer_parts.append(text)
            yield StreamEvent(text=text)
        # Citations are still emitted exactly once, after all answer text --
        # now with the assembled answer so answer-grounding can be scored.
        yield StreamEvent(
            citations=self._generation_service.citations_for(
                request, "".join(answer_parts),
            )
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

        if not rewritten_query:
            return latest_message.content

        return rewritten_query

    def _generation_history(
        self,
        *,
        conversation: list[ChatMessage],
        summary: str | None,
    ) -> list[ChatMessage]:
        """
        Select the conversation messages sent verbatim to the answer LLM.

        Before summarization is active (no usable summary) the full history is
        used, exactly as before. Once a summary is available it already
        represents the older conversation, so only the rolling recent window
        is kept: ``RECENT_MESSAGE_WINDOW`` messages plus the current user
        message (which ``PromptBuilder`` strips back off and appends as the
        question). This is what keeps answer-generation token usage flat as a
        conversation grows.
        """

        if not summary:
            return conversation

        window = settings.RECENT_MESSAGE_WINDOW + 1

        return conversation[-window:]

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
            < settings.INITIAL_SUMMARY_THRESHOLD
        ):
            return None

        return summary
