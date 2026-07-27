from app.enums.message import MessageRole
from app.generation.models import (
    ConversationMessage,
    LLMMessage,
)


class QueryRewriter:
    """
    Responsible for rewriting conversational user queries into
    standalone search queries suitable for Retrieval-Augmented
    Generation (RAG).

    The rewritten query is used ONLY for document retrieval.

    It must preserve the user's intent while resolving references
    from the recent conversation.
    """

    SYSTEM_PROMPT = """
You are an expert query rewriting assistant for a Retrieval-Augmented Generation (RAG) system.

Your task is to rewrite the user's latest question into a standalone search query.

The rewritten query will ONLY be used for retrieving relevant documents.

It will NOT be shown to the user.

========================
OBJECTIVE
========================

Rewrite the latest user message so that it can be understood without reading the previous conversation.

Resolve references such as:

- it
- this
- that
- these
- those
- he
- she
- they
- them
- its
- previous concepts
- previous papers
- previous models

using the conversation history.

========================
RULES
========================

- Preserve the user's original intent.
- Do NOT answer the question.
- Do NOT summarize the conversation.
- Do NOT introduce new information.
- Do NOT change the meaning.
- Keep important technical terminology.
- Expand ambiguous references whenever possible.
- Produce a natural standalone query.
- If the latest question is already standalone, return it unchanged.
- If multiple interpretations are possible, choose the one most strongly supported by the conversation.

========================
EXAMPLES
========================

Conversation

User:
Explain Rotary Positional Embeddings.

Assistant:
...

User:
How is it different from ALiBi?

Output

How is Rotary Positional Embeddings (RoPE) different from ALiBi?


Conversation

User:
Explain Flash Attention.

Assistant:
...

User:
Can you explain that in more detail?

Output

Explain Flash Attention in more detail.


Conversation

User:
What is BERT?

Assistant:
...

User:
Who introduced it?

Output

Who introduced BERT?


Conversation

User:
Explain Transformer architecture.

Assistant:
...

User:
What are its advantages?

Output

What are the advantages of the Transformer architecture?


Conversation

User:
What is Retrieval-Augmented Generation?

Output

What is Retrieval-Augmented Generation?

========================
OUTPUT
========================

Return ONLY the rewritten standalone query.

Do not include explanations.

Do not use markdown.

Return only plain text.
"""

    @classmethod
    def build_prompt(
        cls,
        *,
        conversation: list[ConversationMessage],
    ) -> list[LLMMessage]:
        """
        Build the prompt used to rewrite the latest user
        message into a standalone retrieval query.
        """

        conversation_text = cls._format_conversation(
            conversation,
        )

        user_prompt = f"""
Conversation

{conversation_text}


Rewrite the latest user message into a standalone retrieval query.

Return ONLY the rewritten query.
"""

        return [
            LLMMessage(
                role=MessageRole.SYSTEM,
                content=cls.SYSTEM_PROMPT,
            ),
            LLMMessage(
                role=MessageRole.USER,
                content=user_prompt,
            ),
        ]

    @staticmethod
    def _format_conversation(
        conversation: list[ConversationMessage],
    ) -> str:
        """
        Convert structured conversation messages into
        a readable prompt format.
        """

        formatted_messages: list[str] = []

        for message in conversation:

            speaker = (
                "User"
                if message.role == MessageRole.USER
                else "Assistant"
            )

            formatted_messages.append(
                f"{speaker}: {message.content}"
            )

        return "\n\n".join(formatted_messages)