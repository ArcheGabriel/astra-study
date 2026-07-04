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
    ) -> list[dict[str, str]]:
        """
        Build the prompt used to generate a chat title.
        """

        return [
            {
                "role": "system",
                "content": cls.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": first_message,
            },
        ]