from __future__ import annotations

from collections.abc import Iterator

from app.generation.base import BaseGenerationService
from app.generation.exceptions import EmptyResponseError
from app.generation.models import (
    GenerationRequest,
    GenerationResponse,
)
from app.generation.prompt_builder import PromptBuilder
from app.services.llm import LLMService


class GenerationService(BaseGenerationService):
    """
    Production implementation of the Generation layer.

    Responsibilities
    ----------------
    - Build prompts using the PromptBuilder.
    - Delegate response generation to the LLMService.
    - Convert provider responses into GenerationResponse.

    This service intentionally contains no provider-specific logic.
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm_service: LLMService,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._llm_service = llm_service

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """
        Generate a complete assistant response.
        """

        messages = self._prompt_builder.build(
            request=request,
        )

        response = self._llm_service.generate_response(
            messages=messages,
        )

        response = response.strip()

        if not response:
            raise EmptyResponseError(
                "The language model returned an empty response."
            )

        return GenerationResponse(
            answer=response,
        )

    def stream(
        self,
        request: GenerationRequest,
    ) -> Iterator[str]:
        """
        Stream the assistant response.
        """

        messages = self._prompt_builder.build(
            request=request,
        )

        for chunk in self._llm_service.stream_response(
            messages=messages,
        ):
            yield chunk