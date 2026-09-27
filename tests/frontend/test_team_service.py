"""
Executable specification for the frontend ``TeamService`` -- confirms it
calls ``GET /teams`` through the existing ``ApiClient`` conventions and
parses the response into ``Team`` objects, without any club/role fields
that ``TeamResponse`` deliberately doesn't carry.
"""

from __future__ import annotations

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

    def get(self, endpoint, *, params=None):
        self.requested_endpoints.append(endpoint)
        return self.payload


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
