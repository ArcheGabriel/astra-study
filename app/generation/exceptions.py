"""
Exceptions raised by the Generation module.
"""


class GenerationError(Exception):
    """
    Base exception for all generation-related errors.
    """


class EmptyPromptError(GenerationError):
    """
    Raised when prompt generation results in no messages.
    """


class EmptyResponseError(GenerationError):
    """
    Raised when the LLM returns an empty response.
    """


class GenerationTimeoutError(GenerationError):
    """
    Raised when the configured LLM times out.
    """


class InvalidGenerationResponseError(GenerationError):
    """
    Raised when the provider returns an invalid response.
    """


class TokenLimitExceededError(GenerationError):
    """
    Raised when the prompt exceeds the configured token limit.
    """