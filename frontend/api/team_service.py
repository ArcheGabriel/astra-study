from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.team import Team


class TeamService:
    """
    Service responsible for team-discovery operations.

    Read-only in this milestone: membership/role management, jurisdiction
    grants, and any other team mutation are out of scope.
    """

    def __init__(
        self,
        client: ApiClient,
    ) -> None:
        self.client = client

    def list_teams(
        self,
    ) -> list[Team]:
        """
        Return every team in the requester's own organisation.

        Visibility only -- does not imply membership. Use
        ``frontend.models.user.User.teams`` for the requester's actual
        memberships.
        """

        data = self.client.get(
            "/teams",
        )

        return [
            Team.from_dict(item)
            for item in data
        ]
