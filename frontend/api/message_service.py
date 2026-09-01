from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Callable

import requests

from frontend.api.api_client import ApiClient, ApiException
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

    def stream_message(
        self,
        chat_id: int,
        content: str,
        on_citations: Callable[[list], None] | None = None,
    ) -> Iterator[str]:
        """
        Yield assistant text chunks from the message SSE endpoint.
        """

        response = self.client.stream_post(
            f"/chats/{chat_id}/messages/stream",
            json={"content": content},
        )

        event = "message"

        try:
            for line in response.iter_lines(decode_unicode=True):

                if not line:
                    event = "message"
                    continue

                if line.startswith("event:"):
                    event = line.removeprefix("event:").strip()
                    continue

                if not line.startswith("data:"):
                    continue

                payload = json.loads(line.removeprefix("data:").strip())

                if event == "error":
                    raise ApiException(
                        payload.get("detail", "Streaming failed."),
                    )

                if event == "done":
                    return

                if event == "citations":
                    if on_citations is not None:
                        on_citations(payload.get("citations", []))
                    continue

                text = payload.get("text")

                if text:
                    yield text

        except (ValueError, requests.RequestException) as exc:
            raise ApiException("Invalid streaming response from backend.") from exc
        finally:
            response.close()
