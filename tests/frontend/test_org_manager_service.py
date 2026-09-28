"""
Executable specification for the frontend ``OrgManagerService`` (RBAC-9)
-- confirms ``list_managers``/``grant``/``revoke`` hit the exact backend
endpoints/verbs/payloads (``app/api/v1/team.py``:
``GET /teams/{team_id}/managers``, ``POST /teams/{team_id}/managers/{user_id}``,
``DELETE /teams/{team_id}/managers/{user_id}``), that ``list_managers``
parses the response into ``OrgManagerAssignment``, and that a non-2xx
response propagates as ``ApiException`` without being swallowed --
mirrors ``tests/frontend/test_membership_service.py``'s exact structure
and fake-client convention.
"""

from __future__ import annotations

import pytest

from frontend.api.api_client import ApiException
from frontend.api.org_manager_service import OrgManagerService
from frontend.models.team import OrgManagerAssignment


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

    def delete(self, endpoint):
        return self._record("DELETE", endpoint)


def test_list_managers_calls_the_managers_endpoint():
    client = _FakeApiClient(response=[])

    OrgManagerService(client).list_managers(7)

    assert client.calls == [{"method": "GET", "endpoint": "/teams/7/managers", "params": None}]


def test_list_managers_parses_response_shape():
    client = _FakeApiClient(
        response=[
            {"user_id": 1, "team_id": 7},
            {"user_id": 2, "team_id": 7},
        ],
    )

    assignments = OrgManagerService(client).list_managers(7)

    assert assignments == [
        OrgManagerAssignment(user_id=1, team_id=7),
        OrgManagerAssignment(user_id=2, team_id=7),
    ]


def test_list_managers_returns_empty_list_for_no_assignments():
    client = _FakeApiClient(response=[])

    assignments = OrgManagerService(client).list_managers(7)

    assert assignments == []


def test_grant_posts_to_the_managers_endpoint():
    client = _FakeApiClient(response={"user_id": 5, "team_id": 7})

    OrgManagerService(client).grant(7, 5)

    assert client.calls == [
        {
            "method": "POST",
            "endpoint": "/teams/7/managers/5",
            "json": {},
            "data": None,
            "files": None,
        },
    ]


def test_revoke_calls_delete_with_both_ids():
    client = _FakeApiClient(response=None)

    OrgManagerService(client).revoke(7, 5)

    assert client.calls == [{"method": "DELETE", "endpoint": "/teams/7/managers/5"}]


def test_list_managers_propagates_api_exception():
    client = _FakeApiClient(raises=ApiException("Team not found."))

    with pytest.raises(ApiException):
        OrgManagerService(client).list_managers(7)


def test_grant_propagates_api_exception():
    client = _FakeApiClient(
        raises=ApiException("Target user must currently hold OrgRole.MANAGER to receive jurisdiction."),
    )

    with pytest.raises(ApiException):
        OrgManagerService(client).grant(7, 5)


def test_revoke_propagates_api_exception():
    client = _FakeApiClient(raises=ApiException("This Org Manager has no jurisdiction over this team."))

    with pytest.raises(ApiException):
        OrgManagerService(client).revoke(7, 5)
