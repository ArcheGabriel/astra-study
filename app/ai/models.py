from enum import Enum


class OpenAIModel(str, Enum):
    """
    Supported OpenAI chat models.
    """

    GPT_5 = "gpt-5"

    GPT_5_MINI = "gpt-5-mini"

    GPT_5_NANO = "gpt-5-nano"