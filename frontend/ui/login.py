from __future__ import annotations

import streamlit as st

from frontend.api.api_client import ApiClient, ApiException
from frontend.api.auth_service import AuthService
from frontend.api.chat_service import ChatService
from frontend.api.document_service import DocumentService


def _load_workspace(
    client: ApiClient,
) -> None:
    """
    Load chats and documents immediately after login.
    """

    chat_service = ChatService(client)
    document_service = DocumentService(client)

    chats = chat_service.list_chats()
    documents = document_service.list_documents()

    st.session_state.chats = chats
    st.session_state.documents = documents

    if chats:
        st.session_state.active_chat = chats[0].id
    else:
        st.session_state.active_chat = None

    st.session_state.active_document = None
    st.session_state.messages = []
    st.session_state.citations = []


def login_screen() -> None:
    """
    Render the login / registration page.
    """

    _, center, _ = st.columns(
        [1, 1.25, 1],
    )

    with center:

        # Keep the login heading below Streamlit's fixed top toolbar.
        st.markdown(
            '<div class="login-top-spacer"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='login-brand'>Astra <span>Study</span></div>",
            unsafe_allow_html=True,
        )

        st.caption(
            "Your focused AI study workspace",
        )

        login_tab, register_tab = st.tabs(
            [
                "Sign In",
                "Create Account",
            ]
        )

        with login_tab:

            with st.form("login_form"):

                email = st.text_input(
                    "Email",
                    placeholder="you@example.com",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                )

                submitted = st.form_submit_button(
                    "Sign In",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:

                try:

                    client = ApiClient(
                        st.session_state.api_url,
                    )

                    auth_service = AuthService(
                        client,
                    )

                    token = auth_service.login(
                        email=email,
                        password=password,
                    )

                    client.set_access_token(
                        token.access_token,
                    )

                    st.session_state.token = (
                        token.access_token
                    )

                    st.session_state.current_user = (
                        token.user
                    )

                    _load_workspace(
                        client,
                    )

                    st.rerun()

                except ApiException as exc:

                    st.error(str(exc))

        with register_tab:

            with st.form("register_form"):

                username = st.text_input(
                    "Username",
                )

                email = st.text_input(
                    "Email",
                    key="register_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="register_password",
                )

                submitted = st.form_submit_button(
                    "Create Account",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:

                try:

                    client = ApiClient(
                        st.session_state.api_url,
                    )

                    auth_service = AuthService(
                        client,
                    )

                    auth_service.register(
                        username=username,
                        email=email,
                        password=password,
                    )

                    st.success(
                        "Registration successful. Please sign in."
                    )

                except ApiException as exc:

                    st.error(
                        str(exc),
                    )
