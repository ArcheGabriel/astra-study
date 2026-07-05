from collections.abc import Iterator

from app.ai.base import BaseLLMProvider
from app.ai.openai_provider import OpenAIProvider


class LLMService:
    """
    Service responsible for interacting with language models.
    """

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self.provider = provider or OpenAIProvider()

    def generate_response(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate an assistant response.
        """

        return self.provider.generate_response(
            messages=messages,
        )

    def generate_title(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate a concise title.
        """

        return self.provider.generate_response(
            messages=messages,
        ).strip()

    def stream_response(
        self,
        messages: list[dict[str, str]],
    ) -> Iterator[str]:
        """
        Stream an assistant response.
        """

        return self.provider.stream_response(
            messages=messages,
        )