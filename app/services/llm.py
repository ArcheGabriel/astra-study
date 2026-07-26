from collections.abc import Iterator

from app.ai.base import BaseLLMProvider
from app.ai.openai_provider import OpenAIProvider
from app.generation.models import LLMMessage


class LLMService:
    """
    Service responsible for interacting with language models.
    """

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self.provider = provider or OpenAIProvider()

    @staticmethod
    def _convert_messages(
        messages: list[LLMMessage],
    ) -> list[dict[str, str]]:
        """
        Convert provider-agnostic messages into the format
        expected by the LLM provider.
        """

        return [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in messages
        ]

    def generate_response(
        self,
        messages: list[LLMMessage],
    ) -> str:
        """
        Generate an assistant response.
        """

        return self.provider.generate_response(
            messages=self._convert_messages(messages),
        )

    def generate_title(
        self,
        messages: list[LLMMessage],
    ) -> str:
        """
        Generate a concise title.
        """

        return self.provider.generate_response(
            messages=self._convert_messages(messages),
        ).strip()

    def generate_summary(
        self,
        messages: list[LLMMessage],
    ) -> str:
        """
        Generate or update a rolling conversation summary.
        """

        return self.provider.generate_response(
            messages=self._convert_messages(messages),
        ).strip()

    def stream_response(
        self,
        messages: list[LLMMessage],
    ) -> Iterator[str]:
        """
        Stream an assistant response.
        """

        return self.provider.stream_response(
            messages=self._convert_messages(messages),
        )