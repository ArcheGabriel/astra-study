from openai import OpenAI

from app.config.settings import settings


def get_openai_client() -> OpenAI:
    """
    Create and return an OpenAI client.

    The client is configured using application settings.
    """

    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )