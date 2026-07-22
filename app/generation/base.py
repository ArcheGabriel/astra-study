from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from app.generation.models import (
    GenerationRequest,
    GenerationResponse,
)


class BaseGenerationService(ABC):
    """
    Abstract interface for the Generation layer.

    Implementations are responsible for generating responses
    from prepared GenerationRequests.

    The Generation layer is provider-agnostic. Concrete
    implementations may internally use OpenAI, Anthropic,
    Azure OpenAI, Gemini, Ollama, or any future provider.
    """

    @abstractmethod
    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """
        Generate a complete response.
        """

    @abstractmethod
    def stream(
        self,
        request: GenerationRequest,
    ) -> Iterator[str]:
        """
        Stream the generated response.

        Each yielded string represents the next chunk of the
        assistant response.

        The concrete implementation is responsible for
        reconstructing the final response if persistence
        is required.
        """