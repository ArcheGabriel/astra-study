from __future__ import annotations

from app.generation.exceptions import EmptyPromptError
from app.generation.models import (
    ConversationMessage,
    GenerationRequest,
    LLMMessage,
)
from app.generation.prompts import (
    CONTEXT_TEMPLATE,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)
from app.enums.message import MessageRole


class PromptBuilder:
    """
    Builds provider-agnostic prompts for the Generation layer.

    Responsibilities
    ----------------
    - Convert retrieved contexts into a readable context block.
    - Preserve conversation history.
    - Append the current user question.
    - Produce provider-agnostic LLM messages.
    """

    def build(
        self,
        request: GenerationRequest,
    ) -> list[LLMMessage]:
        """
        Build the complete prompt sent to the LLM.
        """

        messages: list[LLMMessage] = [
            LLMMessage(
                role=MessageRole.SYSTEM,
                content=SYSTEM_PROMPT.strip(),
            )
        ]

        context = self._build_context(
            request,
        )

        if context:
            messages.append(
                LLMMessage(
                    role=MessageRole.SYSTEM,
                    content=context,
                )
            )

        messages.extend(
            self._build_history(
                request.conversation,
            )
        )

        messages.append(
            LLMMessage(
                role=MessageRole.USER,
                content=USER_PROMPT_TEMPLATE.format(
                    question=request.query.strip(),
                ).strip(),
            )
        )

        if not messages:
            raise EmptyPromptError(
                "Prompt builder produced an empty prompt."
            )

        return messages

    def _build_context(
        self,
        request: GenerationRequest,
    ) -> str:
        """
        Convert retrieved contexts into a formatted block.
        """

        if len(request.retrieval) == 0:
            return ""

        parts: list[str] = []

        for index, context in enumerate(
            request.retrieval,
            start=1,
        ):
            metadata: list[str] = [
                f"Source: {context.source}"
            ]

            if context.page is not None:
                metadata.append(
                    f"Page: {context.page}"
                )

            if context.section:
                metadata.append(
                    f"Section: {context.section}"
                )

            parts.append(
                (
                    f"[Context {index}]\n"
                    f"{' | '.join(metadata)}\n\n"
                    f"{context.text}"
                )
            )

        return CONTEXT_TEMPLATE.format(
            context="\n\n------------------------------\n\n".join(parts)
        ).strip()

    def _build_history(
        self,
        conversation: list[ConversationMessage],
    ) -> list[LLMMessage]:
        """
        Convert conversation history into LLM messages.
        """

        return [
            LLMMessage(
                role=message.role,
                content=message.content,
            )
            for message in conversation
        ]