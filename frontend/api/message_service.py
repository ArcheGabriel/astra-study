from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.conversation import Conversation
from frontend.models.message import Message


class MessageService:

    def __init__(
        self,
        client: ApiClient,
    ) -> None:

        self.client = client

    def list_messages(
        self,
        chat_id: int,
    ) -> list[Message]:

        data = self.client.get(
            f"/chats/{chat_id}/messages",
        )

        return [
            Message.from_dict(message)
            for message in data
        ]

    def send_message(
        self,
        chat_id: int,
        content: str,
    ) -> Conversation:

        data = self.client.post(
            f"/chats/{chat_id}/messages",
            json={
                "content": content,
            },
        )

        return Conversation.from_dict(data)