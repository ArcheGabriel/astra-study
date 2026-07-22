from app.enums.message import MessageRole
from app.generation.models import LLMMessage


class TitleGenerator:
    """
    Responsible for generating prompts used to create chat titles.
    """

    SYSTEM_PROMPT = """
You generate concise titles for conversations.

Rules:

- Maximum 5 words.
- Do not use quotation marks.
- Do not end with punctuation.
- Return only the title.
"""

    @classmethod
    def build_prompt(
        cls,
        first_message: str,
    ) -> list[LLMMessage]:
        """
        Build the prompt used to generate a chat title.
        """

        return [
            LLMMessage(
                role=MessageRole.SYSTEM,
                content=cls.SYSTEM_PROMPT,
            ),
            LLMMessage(
                role=MessageRole.USER,
                content=first_message,
            ),
        ]