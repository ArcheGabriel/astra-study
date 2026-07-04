from app.ai.prompts import PromptBuilder
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
        user_message: str,
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