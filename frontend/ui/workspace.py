from __future__ import annotations

import streamlit as st

from frontend.api.api_client import (
    ApiClient,
    ApiException,
    GENERATION_TIMEOUT,
)
from frontend.api.chat_service import ChatService
from frontend.api.message_service import MessageService

from frontend.models.chat import Chat
from frontend.models.conversation import Conversation
from frontend.models.message import Message


def _client() -> ApiClient:
    """
    Create an authenticated API client.
    """

    return ApiClient(
        base_url=st.session_state.api_url,
        access_token=st.session_state.token,
    )


def _refresh_chat_list() -> None:
    """
    Refresh the sidebar chat list.
    """

    chat_service = ChatService(
        _client()
    )

    st.session_state.chats = (
        chat_service.list_chats()
    )


def _send_message(
    chat_id: int,
    prompt: str,
) -> Conversation:
    """
    Send a message to the backend.
    """

    client = ApiClient(
        base_url=st.session_state.api_url,
        access_token=st.session_state.token,
        timeout=GENERATION_TIMEOUT,
    )

    return MessageService(
        client
    ).send_message(
        chat_id=chat_id,
        content=prompt,
    )


def _active_chat() -> Chat | None:
    """
    Return the selected chat.
    """

    active = (
        st.session_state.active_chat
    )

    for chat in st.session_state.chats:

        if chat.id == active:

            return chat

    return None


def _render_header(
    chat: Chat | None,
) -> None:
    """
    Render workspace heading.
    """

    title = (
        chat.title
        if chat
        else "Study Conversation"
    )

    st.markdown(
        f"""
<div class="chat-title">
{title}
</div>

<div class="chat-subtitle">
Ask questions grounded in your uploaded documents.
</div>
""",
        unsafe_allow_html=True,
    )


def _render_history() -> None:
    """
    Render conversation history.
    """

    if not st.session_state.messages:

        st.info(
            "Start a conversation by asking a question about your uploaded documents."
        )

        return

    for message in (
        st.session_state.messages
    ):

        role = (
            "user"
            if message.role.lower() == "user"
            else "assistant"
        )

        with st.chat_message(
            role
        ):

            st.markdown(
                message.content
            )

def workspace() -> None:
    """
    Main workspace.
    """

    chat = _active_chat()

    #
    # Workspace Header
    #

    _render_header(chat)

    #
    # Conversation Area
    #

    conversation_container = st.container()

    with conversation_container:

        _render_history()

    #
    # Chat Input
    #

    prompt = st.chat_input(
        "Ask Astra Study anything...",
        disabled=chat is None,
    )

    if not prompt:

        return

    #
    # Temporary user message
    #

    user_message = Message(
        id=-1,
        role="user",
        content=prompt,
        created_at=None,
    )

    #
    # Immediately display the user message.
    #

    with st.chat_message("user"):

        st.markdown(
            prompt,
        )

    #
    # Assistant placeholder
    #

    assistant_placeholder = st.empty()

    try:

        with assistant_placeholder.container():

            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "Astra is thinking..."
                ):

                    conversation = _send_message(
                        chat.id,
                        prompt,
                    )

        #
        # Replace placeholder
        #

        assistant_placeholder.empty()

        with assistant_placeholder.container():

            with st.chat_message(
                "assistant"
            ):

                st.markdown(
                    conversation.assistant_message.content,
                )

        #
        # Persist conversation
        #

        st.session_state.messages.append(
            user_message,
        )

        st.session_state.messages.append(
            conversation.assistant_message,
        )

        st.session_state.citations = (
            conversation.citations
        )

        #
        # Refresh sidebar chat titles
        #

        _refresh_chat_list()

    except ApiException as exc:

        assistant_placeholder.empty()

        with st.chat_message(
            "assistant"
        ):

            st.error(
                str(exc),
            )

    except Exception as exc:

        assistant_placeholder.empty()

        with st.chat_message(
            "assistant"
        ):

            st.error(
                f"Unexpected error: {exc}"
            )