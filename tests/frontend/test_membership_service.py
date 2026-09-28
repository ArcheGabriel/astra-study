"""
Executable specification for the frontend ``MembershipService`` --
confirms roster retrieval and the three mutation calls hit the exact
backend endpoints/verbs/payloads (``app/api/v1/team.py``:
``GET /teams/{team_id}/members``, ``POST /teams/{team_id}/members``
with ``{"user_id": ...}``, ``DELETE /teams/{team_id}/members/{user_id}``,
``POST /teams/{team_id}/members/{user_id}/promote``), and that a
non-2xx response propagates as ``ApiException`` without being swallowed.
"""

from __future__ import annotations

from frontend.api.api_client import ApiException
from frontend.api.membership_service import MembershipService
from frontend.models.team import TeamRosterMember

import pytest


class _FakeApiClient:
    """
    Duck-typed stand-in for ``ApiClient`` -- records every call made and
    returns a canned response, or raises a canned ``ApiException`` if
    one was configured (matching this project's existing fake-client
    convention).
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


def test_list_roster_calls_the_roster_endpoint():
    client = _FakeApiClient(response=[])

    MembershipService(client).list_roster(7)

    assert client.calls == [{"method": "GET", "endpoint": "/teams/7/members", "params": None}]


def test_list_roster_parses_response_shape():
    client = _FakeApiClient(
        response=[
            {"user_id": 1, "username": "alice", "email": "alice@example.com", "role": "manager"},
            {"user_id": 2, "username": "bob", "email": "bob@example.com", "role": "member"},
        ],
    )

    roster = MembershipService(client).list_roster(7)

    assert roster == [
        TeamRosterMember(user_id=1, username="alice", email="alice@example.com", role="manager"),
        TeamRosterMember(user_id=2, username="bob", email="bob@example.com", role="member"),
    ]


def test_add_member_posts_exactly_user_id():
    client = _FakeApiClient(response={"user_id": 5, "team_id": 7, "role": "member"})

    MembershipService(client).add_member(7, 5)

    assert client.calls == [
        {
            "method": "POST",
            "endpoint": "/teams/7/members",
            "json": {"user_id": 5},
            "data": None,
            "files": None,
        },
    ]


def test_remove_member_calls_delete_with_both_ids():
    client = _FakeApiClient(response=None)

    MembershipService(client).remove_member(7, 5)

    assert client.calls == [{"method": "DELETE", "endpoint": "/teams/7/members/5"}]


def test_promote_member_calls_the_promote_endpoint():
    client = _FakeApiClient(response={"user_id": 5, "team_id": 7, "role": "manager"})

    MembershipService(client).promote_member(7, 5)

    assert client.calls == [
        {
            "method": "POST",
            "endpoint": "/teams/7/members/5/promote",
            "json": {},
            "data": None,
            "files": None,
        },
    ]


def test_add_member_propagates_api_exception():
    client = _FakeApiClient(raises=ApiException("This team membership already exists."))

    with pytest.raises(ApiException):
        MembershipService(client).add_member(7, 5)


def test_remove_member_propagates_api_exception():
    client = _FakeApiClient(raises=ApiException("Cannot remove the team's last remaining manager."))

    with pytest.raises(ApiException):
        MembershipService(client).remove_member(7, 5)


def test_promote_member_propagates_api_exception():
    client = _FakeApiClient(raises=ApiException("Only that team's manager may manage its membership."))

    with pytest.raises(ApiException):
        MembershipService(client).promote_member(7, 5)


def test_list_roster_propagates_api_exception():
    client = _FakeApiClient(raises=ApiException("Only that team's manager may manage its membership."))

    with pytest.raises(ApiException):
        MembershipService(client).list_roster(7)
