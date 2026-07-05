from abc import ABC, abstractmethod
from collections.abc import Iterator


class BaseLLMProvider(ABC):
    """
    Base interface for all LLM providers.
    """

    @abstractmethod
    def generate_response(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate a complete response from the language model.
        """
        raise NotImplementedError

    @abstractmethod
    def stream_response(
        self,
        messages: list[dict[str, str]],
    ) -> Iterator[str]:
        """
        Stream a response from the language model.
        """
        raise NotImplementedError