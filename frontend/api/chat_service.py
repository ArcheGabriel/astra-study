from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.chat import Chat


class ChatService:

    def __init__(self, client: ApiClient):
        self.client = client

    def list_chats(self) -> list[Chat]:
        data = self.client.get("/chats")
        return [Chat.from_dict(chat) for chat in data]

    def create_chat(self) -> Chat:
        data = self.client.post("/chats", json={})
        return Chat.from_dict(data)

    def get_chat(self, chat_id: int) -> Chat:
        data = self.client.get(f"/chats/{chat_id}")
        return Chat.from_dict(data)

    def rename_chat(
        self,
        chat_id: int,
        title: str,
    ) -> Chat:

        data = self.client.patch(
            f"/chats/{chat_id}",
            json={"title": title},
        )

        return Chat.from_dict(data)

    def delete_chat(
        self,
        chat_id: int,
    ) -> None:

        self.client.delete(f"/chats/{chat_id}")