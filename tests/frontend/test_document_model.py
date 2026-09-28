"""
Executable specification for the RBAC-8 additions to the frontend
``Document`` model -- confirms ``access_scope``/``team_id``/
``organisation_id`` parse correctly when present, default to ``None``
when absent (response-shape resilience, never fabricated), and that the
pre-existing fields remain unaffected.
"""

from __future__ import annotations

from datetime import datetime

from frontend.models.document import Document


def _payload(**overrides: object) -> dict:
    base = {
        "id": 1,
        "filename": "report.pdf",
        "content_type": "application/pdf",
        "file_size": 1024,
        "status": "indexed",
        "created_at": "2026-01-01T00:00:00",
    }
    base.update(overrides)
    return base


def test_existing_fields_still_parse_correctly():
    document = Document.from_dict(_payload())

    assert document.id == 1
    assert document.filename == "report.pdf"
    assert document.content_type == "application/pdf"
    assert document.file_size == 1024
    assert document.status == "indexed"
    assert document.created_at == datetime.fromisoformat("2026-01-01T00:00:00")


def test_rbac_fields_default_to_none_when_absent():
    document = Document.from_dict(_payload())

    assert document.access_scope is None
    assert document.team_id is None
    assert document.organisation_id is None


def test_individual_payload_parses_with_team_id_none():
    document = Document.from_dict(
        _payload(access_scope="individual", team_id=None, organisation_id=7),
    )

    assert document.access_scope == "individual"
    assert document.team_id is None
    assert document.organisation_id == 7


def test_team_payload_parses_with_team_id_populated():
    document = Document.from_dict(
        _payload(access_scope="team", team_id=3, organisation_id=7),
    )

    assert document.access_scope == "team"
    assert document.team_id == 3
    assert document.organisation_id == 7


def test_organisation_payload_parses_with_team_id_none():
    document = Document.from_dict(
        _payload(access_scope="organisation", team_id=None, organisation_id=7),
    )

    assert document.access_scope == "organisation"
    assert document.team_id is None
    assert document.organisation_id == 7
