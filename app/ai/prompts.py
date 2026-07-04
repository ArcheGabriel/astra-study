from app.models.message import ChatMessage


class PromptBuilder:
    """
    Responsible for constructing prompts sent to the LLM.
    """

    SYSTEM_PROMPT = """
You are Astra Study, an AI-powered multimodal study assistant.

Your responsibilities:

- Help students understand concepts.
- Explain topics clearly.
- Answer accurately.
- Never invent information.
- If you don't know something, say so.
- Format answers using Markdown.
- Use headings and bullet points where appropriate.
"""

    @classmethod
    def build_chat_prompt(
        cls,
        conversation: list[ChatMessage],
    ) -> list[dict[str, str]]:
        """
        Build a chat conversation for the OpenAI Responses API.
        """

        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": cls.SYSTEM_PROMPT,
            }
        ]

        for message in conversation:
            messages.append(
                {
                    "role": message.role.value,
                    "content": message.content,
                }
            )

        return messages