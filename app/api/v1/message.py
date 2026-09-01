import json
from dataclasses import asdict

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from app.dependencies.auth import get_current_user
from app.dependencies.services import (
    get_conversation_service,
    get_message_service,
)
from app.models.user import User
from app.schemas.conversation import ConversationResponse
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
)
from app.services.conversation import ConversationService
from app.services.message import MessageService

router = APIRouter(
    prefix="/chats/{chat_id}/messages",
    tags=["Messages"],
)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(
        get_conversation_service,
    ),
) -> ConversationResponse:
    """
    Send a message and receive the assistant response.
    """

    return conversation_service.send_message(
        chat_id=chat_id,
        current_user=current_user,
        message_data=message_data,
    )


@router.post(
    "/stream",
    status_code=status.HTTP_200_OK,
)
def stream_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    conversation_service: ConversationService = Depends(
        get_conversation_service,
    ),
) -> StreamingResponse:
    """
    Stream an assistant response using Server-Sent Events (SSE).
    """

    def event_stream():
        try:
            for event in conversation_service.stream_message(
                chat_id=chat_id,
                current_user=current_user,
                message_data=message_data,
            ):
                if event.text is not None:
                    yield f"data: {json.dumps({'text': event.text})}\n\n"
                elif event.citations is not None:
                    data = [asdict(citation) for citation in event.citations]
                    yield f"event: citations\ndata: {json.dumps({'citations': data})}\n\n"

            yield "event: done\ndata: {}\n\n"

        except Exception as exc:
            yield (
                "event: error\n"
                f"data: {json.dumps({'detail': str(exc)})}\n\n"
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "",
    response_model=list[MessageResponse],
    status_code=status.HTTP_200_OK,
)
def get_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(
        get_message_service,
    ),
) -> list[MessageResponse]:
    """
    Retrieve all messages for a chat session.
    """

    return message_service.get_messages(
        chat_id=chat_id,
        current_user=current_user,
    )
