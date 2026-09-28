from __future__ import annotations

import streamlit as st

from frontend.api.api_client import ApiClient, ApiException
from frontend.api.membership_service import MembershipService
from frontend.api.user_service import UserService

_MEMBER_ROLE = "member"


def _client() -> ApiClient:
    """
    Create an authenticated API client.
    """

    return ApiClient(
        base_url=st.session_state.api_url,
        access_token=st.session_state.token,
    )


def _load_roster(team_id: int) -> None:
    """
    Fetch the roster for ``team_id`` and cache it, tagged with the
    team_id it belongs to.
    """

    roster = MembershipService(_client()).list_roster(team_id)

    st.session_state.team_roster = roster
    st.session_state.team_roster_team_id = team_id


def _ensure_roster_loaded(team_id: int) -> None:
    """
    Fetch the roster only if it isn't already cached for this exact
    team -- never on an unrelated rerun (e.g. the search box).
    """

    if st.session_state.team_roster_team_id != team_id:
        _load_roster(team_id)


def _invalidate_roster() -> None:
    """
    Force the next render to refetch the roster.

    No in-place ("optimistic") edit of ``team_roster`` is ever
    performed -- the backend remains the sole source of truth for what
    the roster actually contains after a mutation.
    """

    st.session_state.team_roster_team_id = None


def _promote(team_id: int, user_id: int) -> None:
    MembershipService(_client()).promote_member(team_id, user_id)
    _invalidate_roster()


def _remove(team_id: int, user_id: int) -> None:
    MembershipService(_client()).remove_member(team_id, user_id)
    _invalidate_roster()


def _add(team_id: int, user_id: int) -> None:
    MembershipService(_client()).add_member(team_id, user_id)
    _invalidate_roster()
    st.session_state.member_search_results = []


def _search(query: str) -> None:
    st.session_state.member_search_results = (
        UserService(_client()).search_users(query)
    )


def render_team_management(
    team_id: int,
) -> None:
    """
    Roster display + membership management for ``team_id``.

    Callers must have already verified
    ``frontend.team_membership.is_team_manager(current_user, team_id)``
    before calling this -- it performs no authorization of its own.
    This is a UX gate only: the backend independently and
    authoritatively re-enforces the identical ``TeamRole.MANAGER``
    requirement on every request this function makes.
    """

    st.markdown(
        "<div class='eyebrow'>Team Management</div>",
        unsafe_allow_html=True,
    )

    try:
        _ensure_roster_loaded(team_id)

    except ApiException as exc:
        st.error(str(exc))
        return

    st.markdown("**Roster**")

    for member in st.session_state.team_roster:

        label_col, action_col_1, action_col_2 = st.columns(
            [3, 1, 1],
        )

        with label_col:
            st.caption(
                f"{member.username} — {member.role}"
            )

        if member.role == _MEMBER_ROLE:

            with action_col_1:

                if st.button(
                    "Promote",
                    key=f"promote_{team_id}_{member.user_id}",
                ):
                    try:
                        _promote(team_id, member.user_id)
                        st.rerun()

                    except ApiException as exc:
                        st.error(str(exc))

            with action_col_2:

                if st.button(
                    "Remove",
                    key=f"remove_{team_id}_{member.user_id}",
                ):
                    try:
                        _remove(team_id, member.user_id)
                        st.rerun()

                    except ApiException as exc:
                        st.error(str(exc))

        else:

            with action_col_1:

                if st.button(
                    "Remove",
                    key=f"remove_{team_id}_{member.user_id}",
                ):
                    try:
                        _remove(team_id, member.user_id)
                        st.rerun()

                    except ApiException as exc:
                        st.error(str(exc))

    st.markdown("**Add member**")

    query = st.text_input(
        "Search users",
        key="member_search_query",
        label_visibility="collapsed",
        placeholder="Search by username or email",
    )

    if st.button(
        "Search",
        key="member_search_button",
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
        "member_search_results",
        [],
    )

    if search_results:

        for result in search_results:

            result_col, add_col = st.columns(
                [3, 1],
            )

            with result_col:
                st.caption(
                    f"{result.username} ({result.email})"
                )

            with add_col:

                if st.button(
                    "Add",
                    key=f"add_{team_id}_{result.id}",
                ):
                    try:
                        _add(team_id, result.id)
                        st.rerun()

                    except ApiException as exc:
                        st.error(str(exc))
