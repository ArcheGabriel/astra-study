from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.auth import TokenResponse
from frontend.models.user import User


class AuthService:

    def __init__(
        self,
        client: ApiClient,
    ) -> None:

        self.client = client

    def get_current_user_profile(
        self,
    ) -> User:
        """
        Fetch the richer RBAC profile (organisation_id, role, team
        memberships) for the currently authenticated user.

        Distinct from the ``user`` embedded in ``login()``'s
        ``TokenResponse``, which only carries id/username/email --
        ``GET /users/me`` returns the extended shape.
        """

        data = self.client.get(
            "/users/me",
        )

        return User.from_dict(data)

    def login(
        self,
        email: str,
        password: str,
    ) -> TokenResponse:

        data = self.client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

        return TokenResponse.from_dict(data)

    def register(
        self,
        username: str,
        email: str,
        password: str,
    ) -> None:

        self.client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )