"""
Executable specification for the frontend ``RoleManagementService``
(RBAC Phase C.2) -- confirms ``search_users``/``update_role`` hit the
exact backend endpoints/verbs/payloads (``app/api/v1/user.py``:
``GET /users/role-management``, ``POST /users/{user_id}/role``), that
``search_users`` parses the response into ``RoleManagementSearchResult``,
and that a non-2xx response propagates as ``ApiException`` without being
swallowed -- mirrors ``tests/frontend/test_org_manager_service.py``'s
exact structure and fake-client convention.
"""

from __future__ import annotations

import pytest

from frontend.api.api_client import ApiException
from frontend.api.role_management_service import RoleManagementService
from frontend.models.user import RoleManagementSearchResult


class _FakeApiClient:
    """
    Duck-typed stand-in for ``ApiClient`` -- records every call made and
    returns a canned response, or raises a canned ``ApiException`` if
    one was configured.
    """

    def __init__(self, response=None, raises: ApiException | None = None):
        self.response = response
        self.raises = raises
        self.calls: list[dict] = []

    def _record(self, method, endpoint, **kwargs):
        self.calls.append({"method": method, "endpoint": endpoint, **kwargs})
        if self.raises is not None:
            raise self.raises
        return self.response

    def get(self, endpoint, *, params=None):
        return self._record("GET", endpoint, params=params)

    def post(self, endpoint, *, json=None, data=None, files=None):
        return self._record("POST", endpoint, json=json, data=data, files=files)


def test_search_users_calls_the_role_management_endpoint_with_query():
    client = _FakeApiClient(response=[])

    RoleManagementService(client).search_users("bob")

    assert client.calls == [
        {"method": "GET", "endpoint": "/users/role-management", "params": {"q": "bob"}},
    ]


def test_search_users_parses_response_into_role_management_search_result():
    client = _FakeApiClient(
        response=[
            {"id": 1, "username": "alice", "email": "alice@example.com", "role": "member"},
            {"id": 2, "username": "bob", "email": "bob@example.com", "role": "manager"},
        ],
    )

    results = RoleManagementService(client).search_users("a")

    assert results == [
        RoleManagementSearchResult(id=1, username="alice", email="alice@example.com", role="member"),
        RoleManagementSearchResult(id=2, username="bob", email="bob@example.com", role="manager"),
    ]


def test_search_users_returns_empty_list_for_no_matches():
    client = _FakeApiClient(response=[])

    results = RoleManagementService(client).search_users("nobody")

    assert results == []


def test_update_role_posts_the_requested_role():
    client = _FakeApiClient(response={"id": 5, "username": "carol", "role": "manager"})

    RoleManagementService(client).update_role(5, "manager")

    assert client.calls == [
        {
            "method": "POST",
            "endpoint": "/users/5/role",
            "json": {"role": "manager"},
            "data": None,
            "files": None,
        },
    ]


def test_search_users_propagates_api_exception():
    client = _FakeApiClient(
        raises=ApiException("Only an organisation administrator may change another user's role."),
    )

    with pytest.raises(ApiException):
        RoleManagementService(client).search_users("bob")


def test_update_role_propagates_api_exception():
    client = _FakeApiClient(
        raises=ApiException("The requested role transition is not permitted."),
    )

    with pytest.raises(ApiException):
        RoleManagementService(client).update_role(5, "admin")
