from __future__ import annotations

from frontend.api.api_client import ApiClient
from frontend.models.auth import TokenResponse


class AuthService:

    def __init__(
        self,
        client: ApiClient,
    ) -> None:

        self.client = client

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