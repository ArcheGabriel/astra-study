from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.user import UserSearchResult


class UserService:
    """
    Service responsible for organisation-scoped user lookup, used to
    resolve a ``user_id`` for team membership management.

    Read-only. Organisation scoping is enforced by the backend from the
    authenticated requester's identity -- this service never accepts or
    sends an organisation id.
    """

    def __init__(
        self,
        client: ApiClient,
    ) -> None:
        self.client = client

    def search_users(
        self,
        query: str,
    ) -> list[UserSearchResult]:
        """
        Search for users within the requester's own organisation by a
        partial, case-insensitive match on username or email.
        """

        data = self.client.get(
            "/users",
            params={
                "q": query,
            },
        )

        return [
            UserSearchResult.from_dict(item)
            for item in data
        ]
