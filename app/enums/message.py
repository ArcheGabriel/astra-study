from enum import Enum


class MessageRole(str, Enum):
    """
    Represents the sender of a chat message.
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"