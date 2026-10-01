from __future__ import annotations

import streamlit as st

from frontend.access_scope import (
    INDIVIDUAL,
    ORGANISATION,
    TEAM,
    can_select_organisation_scope,
    selectable_teams,
    validate_upload_scope,
)
from frontend.api.api_client import ApiClient, ApiException
from frontend.api.auth_service import AuthService
from frontend.api.chat_service import ChatService
from frontend.api.document_service import DocumentService
from frontend.api.message_service import MessageService
from frontend.api.team_service import TeamService
from frontend.team_membership import can_create_team, is_org_admin, is_team_manager
from frontend.ui.org_manager_management import render_org_manager_management
from frontend.ui.role_management import render_role_management
from frontend.ui.state import logout
from frontend.ui.team_management import render_team_management

_SCOPE_LABELS = {
    "Individual": INDIVIDUAL,
    "Team": TEAM,
    "Organisation": ORGANISATION,
}


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


def _list_teams(client: ApiClient):
    """
    Return every team in the requester's own organisation (visibility
    only -- does not imply membership).
    """

    return TeamService(client).list_teams()


def _create_team(name: str) -> None:
    """
    Create a new team in the requester's own organisation.
    """

    client = _client()

    TeamService(client).create_team(name)

    # The creator becomes that team's TeamRole.MANAGER server-side in the
    # same transaction (TeamRepository.create_with_initial_manager), but
    # st.session_state.current_user is otherwise only populated once, at
    # login. Without this refresh, current_user.teams stays stale and
    # is_team_manager() incorrectly reports the creator as not a manager
    # of the team they just created -- refetch the same profile shape
    # login.py already uses, rather than duplicating GET /users/me here.
    st.session_state.current_user = (
        AuthService(client).get_current_user_profile()
    )


def _upload_documents(
    uploaded_files: list,
    access_scope: str | None = None,
    team_id: int | None = None,
) -> None:
    """
    Upload selected documents.
    """

    client = _client()

    document_service = DocumentService(client)

    with st.spinner("Uploading documents..."):
        document_service.upload_documents(
            uploaded_files,
            access_scope=access_scope,
            team_id=team_id,
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

    st.markdown(
        '<span class="layout-marker sidebar-panel"></span>',
        unsafe_allow_html=True,
    )

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

        current_user = st.session_state.current_user

        if current_user is not None:

            st.caption(
                f"{current_user.username} · "
                f"Org #{current_user.organisation_id} · "
                f"{current_user.role}"
            )

            with st.expander("Account"):

                if current_user.teams:

                    st.markdown("**Team memberships**")

                    for membership in current_user.teams:
                        st.caption(
                            f"{membership.team_name} — {membership.role}"
                        )

                else:
                    st.caption("No team memberships.")

                if current_user.managed_teams:

                    st.markdown("**Managed teams (Org Manager)**")

                    for managed in current_user.managed_teams:
                        st.caption(managed.team_name)

                else:
                    st.caption("No managed teams.")

            if is_org_admin(current_user):

                with st.expander("Org Manager Jurisdiction"):
                    render_org_manager_management()

                with st.expander("Role Administration"):
                    render_role_management()

            st.markdown(
                "<div class='eyebrow'>Teams</div>",
                unsafe_allow_html=True,
            )

            if can_create_team(current_user):

                with st.expander("Create Team"):

                    new_team_name = st.text_input(
                        "Team name",
                        key="new_team_name",
                        label_visibility="collapsed",
                        placeholder="Team name",
                    )

                    if st.button(
                        "Create Team",
                        key="create_team_button",
                        use_container_width=True,
                    ):
                        try:

                            _create_team(new_team_name)

                            st.success("Team created.")
                            st.rerun()

                        except ApiException as exc:
                            st.error(str(exc))

            try:

                organisation_teams = _list_teams(
                    _client(),
                )

            except ApiException as exc:

                st.error(str(exc))
                organisation_teams = []

            if organisation_teams:

                membership_by_team_id = {
                    membership.team_id: membership.role
                    for membership in current_user.teams
                }

                for team in organisation_teams:

                    role = membership_by_team_id.get(team.id)

                    label = (
                        f"{team.name} — {role}"
                        if role
                        else team.name
                    )

                    is_active_team = (
                        team.id
                        == st.session_state.active_team
                    )

                    if st.button(
                        label,
                        key=f"team_{team.id}",
                        type=(
                            "primary"
                            if is_active_team
                            else "secondary"
                        ),
                        use_container_width=True,
                    ):
                        st.session_state.active_team = team.id
                        st.rerun()

                if (
                    st.session_state.active_team is not None
                    and is_team_manager(
                        current_user,
                        st.session_state.active_team,
                    )
                ):
                    render_team_management(
                        st.session_state.active_team,
                    )

            else:

                st.caption("No teams in your organisation.")

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

        current_user = st.session_state.current_user

        upload_teams = selectable_teams(current_user)

        scope_options = ["Individual"]

        if upload_teams:
            scope_options.append("Team")

        if can_select_organisation_scope(current_user):
            scope_options.append("Organisation")

        scope_choice = st.selectbox(
            "Visibility",
            scope_options,
            key="upload_scope_choice",
            label_visibility="collapsed",
        )

        team_id_choice: int | None = None

        if scope_choice == "Team":

            team_names_by_id = {
                team.team_id: team.team_name
                for team in upload_teams
            }

            selected_team_id = st.selectbox(
                "Team",
                list(team_names_by_id.keys()),
                format_func=lambda team_id: team_names_by_id[team_id],
                key="upload_team_choice",
                label_visibility="collapsed",
            )

            team_id_choice = selected_team_id

        uploaded_files = st.file_uploader(
            "Upload Documents",
            accept_multiple_files=True,
            type=["pdf", "docx", "xlsx", "csv", "jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )

        if (
            uploaded_files
            and st.button(
                "Upload",
                use_container_width=True,
            )
        ):

            scope_value = _SCOPE_LABELS[scope_choice]

            validation_error = validate_upload_scope(
                scope=scope_value,
                team_id=team_id_choice,
                user=current_user,
            )

            if validation_error:

                st.error(validation_error)

            else:

                try:

                    _upload_documents(
                        uploaded_files,
                        access_scope=scope_value,
                        team_id=team_id_choice,
                    )

                except ApiException as exc:

                    st.error(str(exc))
