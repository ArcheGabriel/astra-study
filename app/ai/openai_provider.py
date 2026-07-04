from openai import OpenAI

from app.ai.base import BaseLLMProvider
from app.config.settings import settings


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI implementation of the LLM provider.
    """

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    def generate_response(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate a response using OpenAI.
        """

        response = self.client.responses.create(
            model=settings.OPENAI_CHAT_MODEL,
            input=messages,
        )

        return response.output_text