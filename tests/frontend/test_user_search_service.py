"""
Executable specification for the frontend ``UserService`` (organisation
user lookup) -- confirms ``search_users`` calls ``GET /users`` with the
query as the ``q`` param (matching the backend's
``GET /users?q=<query>`` contract) and parses the response into
``UserSearchResult`` objects.
"""

from __future__ import annotations

from frontend.api.user_service import UserService
from frontend.models.user import UserSearchResult


class _FakeApiClient:
    """
    Duck-typed stand-in for ``ApiClient`` -- records the endpoint/params
    it was called with and returns a fixed payload.
    """

    def __init__(self, payload):
        self.payload = payload
        self.calls: list[dict] = []

    def get(self, endpoint, *, params=None):
        self.calls.append({"endpoint": endpoint, "params": params})
        return self.payload


def test_search_users_calls_the_users_endpoint_with_query_param():
    client = _FakeApiClient(payload=[])

    UserService(client).search_users("carol")

    assert client.calls == [{"endpoint": "/users", "params": {"q": "carol"}}]


def test_search_users_parses_response_shape():
    client = _FakeApiClient(
        payload=[
            {"id": 1, "username": "carol", "email": "carol@example.com"},
        ],
    )

    results = UserService(client).search_users("carol")

    assert results == [
        UserSearchResult(id=1, username="carol", email="carol@example.com"),
    ]


def test_search_users_returns_empty_list_for_no_matches():
    client = _FakeApiClient(payload=[])

    results = UserService(client).search_users("nonexistent")

    assert results == []
