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
        Generate a response from the configured provider.
        """

        return self.provider.generate_response(
            messages,
        )