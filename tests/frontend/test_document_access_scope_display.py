"""
Executable specification for ``frontend.ui.sources._format_access_scope``
-- the RBAC-8 display-formatting helper for a document's access scope in
the document preview panel.

Deliberately a pure-function test: ``_format_access_scope`` makes no
Streamlit calls itself (only the surrounding ``_render_document_preview``
does), so it is directly callable and assertable without a Streamlit
runtime, matching this project's existing convention of testing frontend
logic as plain functions wherever possible.
"""

from __future__ import annotations

from frontend.models.document import Document
from frontend.ui.sources import _format_access_scope


def _document(**overrides: object) -> Document:
    base = dict(
        id=1,
        filename="report.pdf",
        content_type="application/pdf",
        file_size=1024,
        status="indexed",
        created_at=None,
        access_scope=None,
        team_id=None,
        organisation_id=None,
    )
    base.update(overrides)
    return Document(**base)


def test_individual_scope_formats_as_individual():
    document = _document(access_scope="individual")

    assert _format_access_scope(document) == "Individual"


def test_team_scope_formats_with_team_id():
    document = _document(access_scope="team", team_id=42)

    assert _format_access_scope(document) == "Team — Team ID 42"


def test_organisation_scope_formats_as_organisation():
    document = _document(access_scope="organisation")

    assert _format_access_scope(document) == "Organisation"


def test_missing_access_scope_returns_none_never_a_fabricated_scope():
    document = _document(access_scope=None)

    assert _format_access_scope(document) is None
