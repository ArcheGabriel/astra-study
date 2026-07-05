from collections.abc import Iterator

from app.ai.prompts import PromptBuilder
from app.ai.title_generator import TitleGenerator
from app.models.message import ChatMessage
from app.services.llm import LLMService


class AIPipeline:
    """
    Coordinates the AI workflow for generating assistant responses.
    """

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    def generate_response(
        self,
        conversation: list[ChatMessage],
    ) -> str:
        """
        Generate an assistant response for the current conversation.
        """

        prompt = PromptBuilder.build_chat_prompt(
            conversation=conversation,
        )

        return self.llm_service.generate_response(
            messages=prompt,
        )

    def generate_title(
        self,
        first_message: str,
    ) -> str:
        """
        Generate a title for a new conversation.
        """

        prompt = TitleGenerator.build_prompt(
            first_message=first_message,
        )

        return self.llm_service.generate_title(
            messages=prompt,
        )

    def stream_response(
        self,
        conversation: list[ChatMessage],
    ) -> Iterator[str]:
        """
        Stream an assistant response.
        """

        prompt = PromptBuilder.build_chat_prompt(
            conversation=conversation,
        )

        return self.llm_service.stream_response(
            messages=prompt,
        )