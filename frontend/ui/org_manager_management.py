from __future__ import annotations

import streamlit as st

from frontend.api.api_client import ApiClient, ApiException
from frontend.api.org_manager_service import OrgManagerService
from frontend.api.team_service import TeamService
from frontend.api.user_service import UserService


def _client() -> ApiClient:
    """
    Create an authenticated API client.
    """

    return ApiClient(
        base_url=st.session_state.api_url,
        access_token=st.session_state.token,
    )


def _load_jurisdiction(team_id: int) -> None:
    """
    Fetch the current Org Manager jurisdiction assignments for
    ``team_id`` and cache them, tagged with the team_id they belong to.
    """

    assignments = OrgManagerService(_client()).list_managers(team_id)

    st.session_state.org_manager_jurisdiction = assignments
    st.session_state.org_manager_jurisdiction_team_id = team_id


def _ensure_jurisdiction_loaded(team_id: int) -> None:
    """
    Fetch jurisdiction only if it isn't already cached for this exact
    team -- never on an unrelated rerun (e.g. the search box), mirroring
    ``frontend.ui.team_management._ensure_roster_loaded``.
    """

    if st.session_state.org_manager_jurisdiction_team_id != team_id:
        _load_jurisdiction(team_id)


def _invalidate_jurisdiction() -> None:
    """
    Force the next render to refetch jurisdiction.

    No in-place ("optimistic") edit of ``org_manager_jurisdiction`` is
    ever performed -- current jurisdiction state is never inferred from
    a grant/revoke's success or failure, only from a fresh
    ``GET /teams/{team_id}/managers``.
    """

    st.session_state.org_manager_jurisdiction_team_id = None


def _grant(team_id: int, user_id: int) -> None:
    OrgManagerService(_client()).grant(team_id, user_id)
    _invalidate_jurisdiction()
    st.session_state.manager_search_results = []


def _revoke(team_id: int, user_id: int) -> None:
    OrgManagerService(_client()).revoke(team_id, user_id)
    _invalidate_jurisdiction()


def _search(query: str) -> None:
    st.session_state.manager_search_results = (
        UserService(_client()).search_users(query)
    )


def render_org_manager_management() -> None:
    """
    ADMIN-only Org Manager jurisdiction management: pick a team, view
    its current jurisdiction assignments (authoritative, from
    ``GET /teams/{team_id}/managers``), grant jurisdiction to a
    searched-up user, or revoke it from a currently assigned manager.

    Callers must have already verified ``current_user.role == "admin"``
    before calling this -- it performs no authorization of its own.
    This is a UX gate only: the backend independently and
    authoritatively re-enforces ``OrgRole.ADMIN`` on every
    grant/revoke request this function makes, and re-validates
    ``OrgRole.MANAGER`` on every grant attempt regardless of what this
    function shows.
    """

    st.markdown(
        "<div class='eyebrow'>Org Manager Jurisdiction</div>",
        unsafe_allow_html=True,
    )

    try:
        teams = TeamService(_client()).list_teams()

    except ApiException as exc:
        st.error(str(exc))
        return

    if not teams:
        st.caption("No teams in your organisation.")
        return

    team_names_by_id = {
        team.id: team.name
        for team in teams
    }

    selected_team_id = st.selectbox(
        "Team",
        list(team_names_by_id.keys()),
        format_func=lambda team_id: team_names_by_id[team_id],
        key="org_manager_team_choice",
        label_visibility="collapsed",
    )

    try:
        _ensure_jurisdiction_loaded(selected_team_id)

    except ApiException as exc:
        st.error(str(exc))
        return

    st.markdown("**Current Org Managers**")

    if st.session_state.org_manager_jurisdiction:

        for assignment in st.session_state.org_manager_jurisdiction:

            label_col, action_col = st.columns(
                [3, 1],
            )

            with label_col:
                st.caption(
                    f"User ID {assignment.user_id}"
                )

            with action_col:

                if st.button(
                    "Revoke",
                    key=f"revoke_manager_{selected_team_id}_{assignment.user_id}",
                ):
                    try:
                        _revoke(selected_team_id, assignment.user_id)
                        st.rerun()

                    except ApiException as exc:
                        st.error(str(exc))

    else:
        st.caption("No Org Managers currently assigned to this team.")

    st.markdown("**Grant jurisdiction**")

    query = st.text_input(
        "Search users",
        key="manager_search_query",
        label_visibility="collapsed",
        placeholder="Search by username or email",
    )

    if st.button(
        "Search",
        key="manager_search_button",
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
        "manager_search_results",
        [],
    )

    if search_results:

        for result in search_results:

            result_col, grant_col = st.columns(
                [3, 1],
            )

            with result_col:
                st.caption(
                    f"{result.username} ({result.email})"
                )

            with grant_col:

                if st.button(
                    "Grant",
                    key=f"grant_manager_{selected_team_id}_{result.id}",
                ):
                    try:
                        _grant(selected_team_id, result.id)
                        st.rerun()

                    except ApiException as exc:
                        st.error(str(exc))
