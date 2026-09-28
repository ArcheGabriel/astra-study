from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.team import TeamRosterMember


class MembershipService:
    """
    Service responsible for team membership management: roster
    retrieval, add, remove, and promote.

    Deliberately separate from ``TeamService`` (organisation-wide team
    discovery only) -- mirrors the backend's own split between
    ``TeamService`` and ``TeamMembershipService``, which authorize
    against different models (org-wide ``OrgRole`` vs. per-team
    ``TeamRole``).

    The backend remains the sole authority for every operation here --
    this service performs no authorization of its own.
    """

    def __init__(
        self,
        client: ApiClient,
    ) -> None:
        self.client = client

    def list_roster(
        self,
        team_id: int,
    ) -> list[TeamRosterMember]:
        """
        Return every member of ``team_id``, ordered by username
        ascending (backend contract).
        """

        data = self.client.get(
            f"/teams/{team_id}/members",
        )

        return [
            TeamRosterMember.from_dict(item)
            for item in data
        ]

    def add_member(
        self,
        team_id: int,
        user_id: int,
    ) -> None:
        """
        Add ``user_id`` to ``team_id`` as a plain ``TeamRole.MEMBER``.

        The backend response (``TeamMemberResponse``) carries no
        username/email, so it isn't mapped to a model here -- the caller
        re-fetches the roster (``list_roster``) after a successful add,
        which is the only place username/email are needed.
        """

        self.client.post(
            f"/teams/{team_id}/members",
            json={
                "user_id": user_id,
            },
        )

    def remove_member(
        self,
        team_id: int,
        user_id: int,
    ) -> None:
        """
        Remove ``user_id``'s membership from ``team_id`` entirely.
        """

        self.client.delete(
            f"/teams/{team_id}/members/{user_id}",
        )

    def promote_member(
        self,
        team_id: int,
        user_id: int,
    ) -> None:
        """
        Promote ``user_id``'s existing membership on ``team_id`` from
        ``TeamRole.MEMBER`` to ``TeamRole.MANAGER``.
        """

        self.client.post(
            f"/teams/{team_id}/members/{user_id}/promote",
            json={},
        )
