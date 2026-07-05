from collections.abc import Iterator

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
        Generate a complete response using OpenAI.
        """

        response = self.client.responses.create(
            model=settings.OPENAI_CHAT_MODEL,
            input=messages,
        )

        return response.output_text

    def stream_response(
        self,
        messages: list[dict[str, str]],
    ) -> Iterator[str]:
        """
        Stream a response from OpenAI.
        """

        stream = self.client.responses.create(
            model=settings.OPENAI_CHAT_MODEL,
            input=messages,
            stream=True,
        )

        for event in stream:

            if event.type == "response.output_text.delta":
                if event.delta:
                    yield event.delta

            elif event.type == "response.completed":
                break