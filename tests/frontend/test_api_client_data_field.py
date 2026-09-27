"""
Executable specification for ``ApiClient``'s ``data`` parameter, added so
document uploads can send ``access_scope``/``team_id`` as extra multipart
form fields alongside ``files`` -- something the previous ``files`` XOR
``json`` client structurally could not do.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from frontend.api.api_client import ApiClient


def _fake_response(status_code=200, json_body=None):
    response = MagicMock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 300
    response.json.return_value = json_body if json_body is not None else []
    return response


def test_post_forwards_data_alongside_files():
    client = ApiClient(base_url="http://testserver")

    with patch("requests.request", return_value=_fake_response()) as mock_request:

        client.post(
            "/documents/upload",
            files=[("files", ("a.pdf", b"bytes", "application/pdf"))],
            data={"access_scope": "team", "team_id": "1"},
        )

    _, kwargs = mock_request.call_args

    assert kwargs["files"] == [
        ("files", ("a.pdf", b"bytes", "application/pdf")),
    ]
    assert kwargs["data"] == {"access_scope": "team", "team_id": "1"}


def test_post_with_files_and_no_data_omits_data_kwarg():
    """
    Existing files-only callers (pre-RBAC-Phase-A behavior) must be
    unaffected -- no ``data`` kwarg should be sent to ``requests`` at
    all when none was supplied.
    """

    client = ApiClient(base_url="http://testserver")

    with patch("requests.request", return_value=_fake_response()) as mock_request:

        client.post(
            "/documents/upload",
            files=[("files", ("a.pdf", b"bytes", "application/pdf"))],
        )

    _, kwargs = mock_request.call_args

    assert "data" not in kwargs


def test_post_with_json_only_is_unaffected_by_data_param():
    client = ApiClient(base_url="http://testserver")

    with patch("requests.request", return_value=_fake_response()) as mock_request:

        client.post(
            "/auth/login",
            json={"email": "a@example.com", "password": "secret"},
        )

    _, kwargs = mock_request.call_args

    assert kwargs["json"] == {"email": "a@example.com", "password": "secret"}
    assert "files" not in kwargs
    assert "data" not in kwargs
