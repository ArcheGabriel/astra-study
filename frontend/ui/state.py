from __future__ import annotations

import os

import streamlit as st

DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1"


def initialize_session_state() -> None:
    """
    Initialize all Streamlit session state variables.

    This function is safe to call multiple times.
    """

    defaults = {
        "api_url": os.getenv(
            "ASTRA_API_URL",
            DEFAULT_API_URL,
        ),
        "token": None,
        "current_user": None,
        "active_chat": None,
        "active_document": None,
        "messages": [],
        "chats": [],
        "documents": [],
        "citations": [],
    }

    for key, value in defaults.items():
        st.session_state.setdefault(
            key,
            value,
        )


def clear_workspace() -> None:
    """
    Clears workspace-specific state.
    """

    st.session_state.active_chat = None
    st.session_state.active_document = None
    st.session_state.messages = []
    st.session_state.citations = []
    st.session_state.chats = []
    st.session_state.documents = []


def logout() -> None:
    """
    Logout the current user.
    """

    st.session_state.token = None
    st.session_state.current_user = None

    clear_workspace()