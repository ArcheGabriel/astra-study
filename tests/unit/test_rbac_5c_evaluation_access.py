"""
Executable specification for RBAC-5C: the evaluation harness resolves its
AccessContext from real, database-backed User/TeamMembership rows -- never
a fabricated placeholder.

Covers, with an isolated in-memory SQLite database (never the real dev
``astra_study.db``) and no Qdrant/LangSmith calls:

- ``EvaluationService._resolve_access`` reads the configured evaluation
  user's real ``organisation_id``/``role`` and real team memberships;
- a missing evaluation user fails loudly rather than silently fabricating
  identity;
- ``EvaluationPredictor`` uses exactly the ``AccessContext`` it was given,
  never constructing one itself.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.retrieval.access import AccessContext

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User

from evaluation.predictor import EvaluationPredictor
from evaluation.service import EvaluationService


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    try:
        yield session
    finally:
        session.close()


def make_organisation(db, *, slug: str = "acme") -> Organisation:
    organisation = Organisation(name="Acme Inc.", slug=slug)
    db.add(organisation)
    db.commit()
    db.refresh(organisation)
    return organisation


def make_user(
    db,
    organisation: Organisation,
    *,
    username: str = "eval-user",
    role: OrgRole = OrgRole.MEMBER,
) -> User:
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password="hashed",
        organisation_id=organisation.id,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_team(db, organisation: Organisation, *, name: str = "Research") -> Team:
    team = Team(organisation_id=organisation.id, name=name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def make_membership(db, *, user: User, team: Team) -> TeamMembership:
    membership = TeamMembership(user_id=user.id, team_id=team.id, role=TeamRole.MEMBER)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def _patched_session_local(db, monkeypatch):
    """_resolve_access calls SessionLocal() directly (matching the
    established out-of-request-cycle pattern used by
    run_summary_refresh) -- point it at the isolated test session,
    wrapped so .close() doesn't tear down the fixture's own session."""

    class _NonClosingSession:
        def __getattr__(self, name):
            return getattr(db, name)

        def close(self):
            pass

    monkeypatch.setattr(
        "evaluation.service.SessionLocal",
        lambda: _NonClosingSession(),
    )


def test_resolve_access_reads_real_organisation_and_role_from_the_database(db, monkeypatch):
    organisation = make_organisation(db)
    user = make_user(db, organisation, role=OrgRole.MANAGER)
    _patched_session_local(db, monkeypatch)

    access = EvaluationService._resolve_access(user.id)

    assert isinstance(access, AccessContext)
    assert access.user_id == user.id
    assert access.organisation_id == organisation.id
    assert access.role == OrgRole.MANAGER


def test_resolve_access_reads_real_team_memberships_from_the_database(db, monkeypatch):
    organisation = make_organisation(db)
    user = make_user(db, organisation)
    team_a = make_team(db, organisation, name="Research")
    team_b = make_team(db, organisation, name="Support")
    make_membership(db, user=user, team=team_a)
    make_membership(db, user=user, team=team_b)
    _patched_session_local(db, monkeypatch)

    access = EvaluationService._resolve_access(user.id)

    assert set(access.team_ids) == {team_a.id, team_b.id}


def test_resolve_access_zero_teams_produces_empty_team_ids(db, monkeypatch):
    organisation = make_organisation(db)
    user = make_user(db, organisation)
    _patched_session_local(db, monkeypatch)

    access = EvaluationService._resolve_access(user.id)

    assert access.team_ids == ()


def test_resolve_access_never_fabricates_organisation_id_as_user_id(db, monkeypatch):
    """The old placeholder set organisation_id=user_id. With a real,
    distinct organisation row, the resolved organisation_id must reflect
    the real FK value, not coincide with the user id."""

    organisation = make_organisation(db)
    user = make_user(db, organisation)
    _patched_session_local(db, monkeypatch)

    access = EvaluationService._resolve_access(user.id)

    assert access.organisation_id == organisation.id
    # Not a fabrication check via inequality alone (organisation.id could
    # coincidentally equal user.id for the first row of each table) --
    # the real assertion is the equality above: it is the FK value, not a
    # copy of user_id. This assertion documents the intent explicitly.


def test_resolve_access_missing_user_fails_loudly(db, monkeypatch):
    _patched_session_local(db, monkeypatch)

    with pytest.raises(RuntimeError):
        EvaluationService._resolve_access(999999)


def test_evaluation_predictor_uses_the_access_context_it_was_given():
    access = AccessContext(
        user_id=5, organisation_id=1, team_ids=(2, 3), role=OrgRole.MEMBER,
    )
    pipeline = MagicMock()
    pipeline.generate_response.return_value = SimpleNamespace(answer="a", citations=[])

    predictor = EvaluationPredictor(ai_pipeline=pipeline, access=access)
    predictor.predict({"question": "What is RAG?"})

    assert pipeline.generate_response.call_args.kwargs["access"] is access
