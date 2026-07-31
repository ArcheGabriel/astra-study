from __future__ import annotations

import streamlit as st

from frontend.api.api_client import ApiClient, ApiException
from frontend.api.chat_service import ChatService
from frontend.api.document_service import DocumentService
from frontend.api.message_service import MessageService
from frontend.ui.state import logout


def _client() -> ApiClient:
    """
    Create an authenticated API client.
    """

    return ApiClient(
        base_url=st.session_state.api_url,
        access_token=st.session_state.token,
    )


def _refresh_workspace() -> None:
    """
    Refresh chats and documents.
    """

    client = _client()

    chat_service = ChatService(client)
    document_service = DocumentService(client)

    st.session_state.chats = chat_service.list_chats()
    st.session_state.documents = (
        document_service.list_documents()
    )


def _load_chat(chat_id: int) -> None:
    """
    Load a chat and its messages.
    """

    client = _client()

    message_service = MessageService(client)

    st.session_state.active_chat = chat_id
    st.session_state.messages = (
        message_service.list_messages(chat_id)
    )
    st.session_state.citations = []


def _create_chat() -> None:
    """
    Create a new chat.
    """

    client = _client()

    chat_service = ChatService(client)

    chat = chat_service.create_chat()

    _refresh_workspace()

    st.session_state.active_chat = chat.id
    st.session_state.messages = []
    st.session_state.citations = []

    st.rerun()


def _upload_documents(uploaded_files: list) -> None:
    """
    Upload selected documents.
    """

    client = _client()

    document_service = DocumentService(client)

    with st.spinner("Uploading documents..."):
        document_service.upload_documents(
            uploaded_files,
        )

    _refresh_workspace()

    st.success(
        "Documents uploaded successfully."
    )

    st.rerun()


def sidebar() -> None:
    """
    Left navigation panel.
    """

    panel = st.container()

    with panel:

        st.markdown(
            """
<div class="brand">
Astra <span>Study</span>
</div>
""",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(
            [4, 1],
        )

        with col1:

            if st.button(
                "＋ New Chat",
                type="primary",
                use_container_width=True,
            ):
                try:
                    _create_chat()

                except ApiException as exc:
                    st.error(str(exc))

        with col2:

            if st.button(
                "⎋",
                help="Logout",
                use_container_width=True,
            ):
                logout()
                st.rerun()

        st.markdown(
            "<div class='eyebrow'>Chats</div>",
            unsafe_allow_html=True,
        )

        if not st.session_state.chats:

            st.caption(
                "No chats available."
            )

        else:

            for chat in st.session_state.chats:

                is_active = (
                    chat.id
                    == st.session_state.active_chat
                )

                if st.button(
                    chat.title,
                    key=f"chat_{chat.id}",
                    type=(
                        "primary"
                        if is_active
                        else "secondary"
                    ),
                    use_container_width=True,
                ):
                    try:

                        _load_chat(chat.id)

                        st.rerun()

                    except ApiException as exc:

                        st.error(str(exc))

        st.markdown(
            "<div class='eyebrow'>Documents</div>",
            unsafe_allow_html=True,
        )

        if st.session_state.documents:

            for document in st.session_state.documents:

                if st.button(
                    f"📄 {document.filename}",
                    key=f"doc_sidebar_{document.id}",
                    use_container_width=True,
                ):
                    st.session_state.active_document = (
                        document
                    )

                    st.rerun()

        else:

            st.caption(
                "No uploaded documents."
            )

        uploaded_files = st.file_uploader(
            "Upload Documents",
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if (
            uploaded_files
            and st.button(
                "Upload",
                use_container_width=True,
            )
        ):
            try:

                _upload_documents(
                    uploaded_files,
                )

            except ApiException as exc:

                st.error(str(exc))