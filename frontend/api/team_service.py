from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.team import Team


class TeamService:
    """
    Service responsible for team-discovery and team-creation operations.

    Membership/role management, jurisdiction grants, and any other team
    mutation remain out of scope -- see ``MembershipService`` and
    ``OrgManagerService`` for those.
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

    def create_team(
        self,
        name: str,
    ) -> Team:
        """
        Create a new team in the requester's own organisation.

        Mirrors ``TeamCreate`` exactly -- ``name`` only, never an
        ``organisation_id`` (the backend derives it from the
        authenticated ``AccessContext``). Authorization
        (``OrgRole.ADMIN``/``OrgRole.MANAGER`` only) is enforced solely by
        the backend; this method sends the request unconditionally and
        lets ``ApiException`` propagate on a 403/400/409.
        """

        data = self.client.post(
            "/teams",
            json={"name": name},
        )

        return Team.from_dict(data)
