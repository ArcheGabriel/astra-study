from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.team import OrgManagerAssignment


class OrgManagerService:
    """
    Service responsible for Org Manager jurisdiction management
    (RBAC-9): listing a team's current jurisdiction assignments, and
    granting/revoking jurisdiction.

    Deliberately separate from ``TeamService`` (organisation-wide team
    discovery) and ``MembershipService`` (per-team ``TeamRole``
    membership) -- mirrors the backend's own three-way split
    (``TeamService``/``TeamMembershipService``/``OrgManagerTeamService``),
    which authorize against different models. The backend remains the
    sole authority for every operation here -- this service performs no
    authorization of its own.
    """

    def __init__(
        self,
        client: ApiClient,
    ) -> None:
        self.client = client

    def list_managers(
        self,
        team_id: int,
    ) -> list[OrgManagerAssignment]:
        """
        Return every Org Manager jurisdiction assignment for
        ``team_id``, ordered by ``user_id`` ascending (backend
        contract). Authoritative current state -- never inferred from a
        failed grant/revoke.
        """

        data = self.client.get(
            f"/teams/{team_id}/managers",
        )

        return [
            OrgManagerAssignment.from_dict(item)
            for item in data
        ]

    def grant(
        self,
        team_id: int,
        user_id: int,
    ) -> None:
        """
        Grant ``user_id`` jurisdiction over ``team_id``.

        The backend remains authoritative about whether ``user_id``
        currently holds ``OrgRole.MANAGER`` -- this call does no
        eligibility pre-check.
        """

        self.client.post(
            f"/teams/{team_id}/managers/{user_id}",
            json={},
        )

    def revoke(
        self,
        team_id: int,
        user_id: int,
    ) -> None:
        """
        Revoke ``user_id``'s jurisdiction over ``team_id``.
        """

        self.client.delete(
            f"/teams/{team_id}/managers/{user_id}",
        )
