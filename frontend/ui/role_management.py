from __future__ import annotations

import streamlit as st

from frontend.api.api_client import ApiClient, ApiException
from frontend.api.role_management_service import RoleManagementService
from frontend.role_management import ACTION_TARGET_ROLE, available_action


def _client() -> ApiClient:
    """
    Create an authenticated API client.
    """

    return ApiClient(
        base_url=st.session_state.api_url,
        access_token=st.session_state.token,
    )


def _search(query: str) -> None:
    st.session_state.role_management_search_results = (
        RoleManagementService(_client()).search_users(query)
    )


def _promote(user_id: int, role: str) -> None:
    RoleManagementService(_client()).update_role(user_id, role)

    # Never an optimistic local edit -- force the next render to
    # re-fetch the same query from the backend, so the displayed role
    # and the recalculated available action always reflect persisted
    # state, mirroring org_manager_management.py's identical discipline.
    query = st.session_state.get("role_management_search_query", "")

    if query:
        st.session_state.role_management_search_results = (
            RoleManagementService(_client()).search_users(query)
        )
    else:
        st.session_state.role_management_search_results = []


def render_role_management() -> None:
    """
    ADMIN-only organisation role administration: search organisation
    users, view their current ``OrgRole``, and promote exactly
    ``MEMBER -> MANAGER`` or ``MANAGER -> ADMIN`` -- never a free-form
    role selector, never a demotion, never self-targeting.

    Callers must have already verified ``is_org_admin(current_user)``
    before calling this -- it performs no authorization of its own.
    This is a UX gate only: the backend independently and
    authoritatively re-enforces ``OrgRole.ADMIN`` on both
    ``GET /users/role-management`` and ``POST /users/{user_id}/role``,
    plus the self-modification and transition-matrix checks on the
    latter, regardless of what this function shows.
    """

    st.markdown(
        "<div class='eyebrow'>Role Administration</div>",
        unsafe_allow_html=True,
    )

    current_user = st.session_state.current_user

    query = st.text_input(
        "Search users",
        key="role_management_search_query",
        label_visibility="collapsed",
        placeholder="Search by username or email",
    )

    if st.button(
        "Search",
        key="role_management_search_button",
    ):

        stripped_query = query.strip()

        if not stripped_query:
            st.error("Enter a username or email to search.")

        else:
            try:
                _search(stripped_query)

            except ApiException as exc:
                st.error(str(exc))

    search_results = st.session_state.get(
        "role_management_search_results",
        [],
    )

    if search_results:

        for result in search_results:

            is_self = (
                current_user is not None
                and result.id == current_user.id
            )

            label_col, action_col = st.columns(
                [3, 1],
            )

            with label_col:
                st.caption(
                    f"{result.username} ({result.email}) — {result.role}"
                )

            action = available_action(result.role, is_self)

            if action is not None:

                with action_col:

                    if st.button(
                        action,
                        key=f"role_action_{result.id}",
                    ):
                        try:
                            _promote(
                                result.id,
                                ACTION_TARGET_ROLE[action],
                            )
                            st.success("Role updated.")
                            st.rerun()

                        except ApiException as exc:
                            st.error(str(exc))
