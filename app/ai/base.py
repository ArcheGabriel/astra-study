from abc import ABC, abstractmethod


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
        Generate a response from the language model.
        """
        raise NotImplementedError