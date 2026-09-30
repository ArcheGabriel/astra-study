"""
Executable specification for the frontend ``TeamService`` -- confirms it
calls ``GET /teams`` through the existing ``ApiClient`` conventions and
parses the response into ``Team`` objects, without any club/role fields
that ``TeamResponse`` deliberately doesn't carry.
"""

from __future__ import annotations

import pytest

from frontend.api.api_client import ApiException
from frontend.api.team_service import TeamService
from frontend.models.team import Team


class _FakeApiClient:
    """
    Duck-typed stand-in for ``ApiClient`` -- records the endpoint it was
    asked for and returns a fixed payload, matching this project's
    existing pattern of exercising services against a fake client rather
    than a real HTTP call.
    """

    def __init__(self, payload):
        self.payload = payload
        self.requested_endpoints: list[str] = []
        self.posted_endpoint: str | None = None
        self.posted_json: dict | None = None

    def get(self, endpoint, *, params=None):
        self.requested_endpoints.append(endpoint)
        return self.payload

    def post(self, endpoint, *, json=None, data=None, files=None):
        self.posted_endpoint = endpoint
        self.posted_json = json
        return self.payload


class _FakeErrorApiClient:
    """
    Duck-typed stand-in for ``ApiClient`` whose ``post`` always raises
    ``ApiException`` -- matching this project's existing convention for
    exercising error propagation without a real HTTP call.
    """

    def post(self, endpoint, *, json=None, data=None, files=None):
        raise ApiException("Only an OrgRole.ADMIN or OrgRole.MANAGER may create a team.")


def test_list_teams_calls_the_teams_endpoint():
    client = _FakeApiClient(payload=[])

    TeamService(client).list_teams()

    assert client.requested_endpoints == ["/teams"]


def test_list_teams_parses_team_response_shape():
    client = _FakeApiClient(
        payload=[
            {"id": 1, "organisation_id": 9, "name": "Research"},
            {"id": 2, "organisation_id": 9, "name": "Support"},
        ],
    )

    teams = TeamService(client).list_teams()

    assert teams == [
        Team(id=1, organisation_id=9, name="Research"),
        Team(id=2, organisation_id=9, name="Support"),
    ]


def test_list_teams_returns_empty_list_for_empty_organisation():
    client = _FakeApiClient(payload=[])

    teams = TeamService(client).list_teams()

    assert teams == []


def test_create_team_posts_to_the_teams_endpoint():
    client = _FakeApiClient(
        payload={"id": 3, "organisation_id": 9, "name": "New Team"},
    )

    TeamService(client).create_team("New Team")

    assert client.posted_endpoint == "/teams"


def test_create_team_sends_only_the_name_field():
    client = _FakeApiClient(
        payload={"id": 3, "organisation_id": 9, "name": "New Team"},
    )

    TeamService(client).create_team("New Team")

    assert client.posted_json == {"name": "New Team"}


def test_create_team_parses_team_response_shape():
    client = _FakeApiClient(
        payload={"id": 3, "organisation_id": 9, "name": "New Team"},
    )

    team = TeamService(client).create_team("New Team")

    assert team == Team(id=3, organisation_id=9, name="New Team")


def test_create_team_propagates_api_exception():
    client = _FakeErrorApiClient()

    with pytest.raises(ApiException):
        TeamService(client).create_team("New Team")
