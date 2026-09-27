"""
Executable specification for ``DocumentService.upload_documents``'s new
``access_scope``/``team_id`` form fields -- confirms the exact field names
and values sent alongside the multipart ``files``, matching the backend's
``POST /documents/upload`` contract (``app/api/v1/document.py``:
``access_scope: str | None = Form(None)``, ``team_id: int | None =
Form(None)``).
"""

from __future__ import annotations

import io

from frontend.api.document_service import DocumentService


class _FakeUploadedFile(io.BytesIO):
    """
    Minimal stand-in for Streamlit's ``UploadedFile`` -- needs ``.name``,
    ``.type``, and a seekable stream, matching what
    ``DocumentService.upload_documents`` already relies on.
    """

    def __init__(self, name: str, content_type: str = "application/pdf"):
        super().__init__(b"fake bytes")
        self.name = name
        self.type = content_type


class _FakeApiClient:
    """
    Duck-typed stand-in for ``ApiClient`` -- records the exact keyword
    arguments ``post`` was called with, so the test can assert on the
    form fields sent alongside the upload.
    """

    def __init__(self, response):
        self.response = response
        self.calls: list[dict] = []

    def post(self, endpoint, *, json=None, data=None, files=None):
        self.calls.append(
            {
                "endpoint": endpoint,
                "json": json,
                "data": data,
                "files": files,
            }
        )
        return self.response


def test_individual_upload_sends_no_access_scope_or_team_by_default():
    client = _FakeApiClient(response=[])

    DocumentService(client).upload_documents(
        [_FakeUploadedFile("a.pdf")],
    )

    assert client.calls[0]["data"] is None


def test_individual_upload_sends_access_scope_without_team_id():
    client = _FakeApiClient(response=[])

    DocumentService(client).upload_documents(
        [_FakeUploadedFile("a.pdf")],
        access_scope="individual",
    )

    assert client.calls[0]["data"] == {"access_scope": "individual"}


def test_team_upload_sends_access_scope_and_team_id():
    client = _FakeApiClient(response=[])

    DocumentService(client).upload_documents(
        [_FakeUploadedFile("a.pdf")],
        access_scope="team",
        team_id=42,
    )

    assert client.calls[0]["data"] == {
        "access_scope": "team",
        "team_id": "42",
    }


def test_organisation_upload_sends_access_scope_without_team_id():
    client = _FakeApiClient(response=[])

    DocumentService(client).upload_documents(
        [_FakeUploadedFile("a.pdf")],
        access_scope="organisation",
    )

    assert client.calls[0]["data"] == {"access_scope": "organisation"}


def test_upload_still_sends_files_field():
    client = _FakeApiClient(response=[])

    DocumentService(client).upload_documents(
        [_FakeUploadedFile("a.pdf")],
        access_scope="team",
        team_id=1,
    )

    files = client.calls[0]["files"]

    assert len(files) == 1
    assert files[0][0] == "files"
    assert files[0][1][0] == "a.pdf"
