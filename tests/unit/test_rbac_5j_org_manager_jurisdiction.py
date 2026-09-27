"""
Executable specification for RBAC-5J: Org Manager <-> Team jurisdiction.

Covers, with no live Qdrant connection and an isolated in-memory SQLite
database (never the real dev ``astra_study.db``):

- ``OrgManagerTeamRepository``: grant/revoke, duplicate-grant handling,
  jurisdiction/team-id lookups;
- ``OrgManagerTeamService``: only ``OrgRole.ADMIN`` may grant/revoke;
  the target user must currently hold ``OrgRole.MANAGER``; strict
  enumeration-safe authorization ordering; cross-organisation isolation;
- the two new API routes (``POST``/``DELETE /teams/{team_id}/managers/{user_id}``);
- SQL/Qdrant TEAM-visibility parity for the same actor/document inputs;
- ``GET /users/me``'s ``managed_teams`` stays structurally independent
  of ``teams``;
- jurisdiction never creates a ``TeamMembership`` row, and
  ``TeamMembership``/``TeamRole`` never affect jurisdiction
  authorization;
- a permanent, repository-tracked concurrency regression test for
  duplicate jurisdiction grants, mirroring RBAC-5I's established
  file-backed-SQLite/real-threads/Barrier pattern.
"""

from __future__ import annotations

import threading

import pytest
from qdrant_client.models import (
    FieldCondition,
    Filter,
    IsEmptyCondition,
    MatchAny,
    MatchValue,
)
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.enums.document import DocumentAccessScope, DocumentStatus
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.exceptions.document import TeamNotFoundError
from app.exceptions.team import (
    OrgManagerJurisdictionAlreadyExistsError,
    OrgManagerJurisdictionForbiddenError,
    OrgManagerJurisdictionNotFoundError,
    TargetNotOrgManagerError,
)
from app.exceptions.user import UserNotFoundError
from app.schemas.team import OrgManagerTeamResponse

# Import every model module so Base.metadata is complete before create_all.
import app.models  # noqa: F401

from app.models.document import Document
from app.models.org_manager_team import OrgManagerTeam
from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.repositories.org_manager_team import OrgManagerTeamRepository
from app.repositories.team import TeamRepository
from app.repositories.team_membership import TeamMembershipRepository
from app.repositories.user import UserRepository
from app.retrieval.access import AccessContext
from app.search.dense.repository import DenseRepository
from app.services.org_manager_team import OrgManagerTeamService
from app.api.v1.team import grant_org_manager_jurisdiction, revoke_org_manager_jurisdiction


# --------------------------------------------------------------------------- #
# Fixtures / factories
# --------------------------------------------------------------------------- #


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
    organisation = Organisation(name=slug.title(), slug=slug)
    db.add(organisation)
    db.commit()
    db.refresh(organisation)
    return organisation


def make_user(
    db, organisation: Organisation, *, username: str = "alice",
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


def make_membership(db, *, user: User, team: Team, role: TeamRole = TeamRole.MEMBER) -> TeamMembership:
    membership = TeamMembership(user_id=user.id, team_id=team.id, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def make_jurisdiction(db, *, user: User, team: Team) -> OrgManagerTeam:
    jurisdiction = OrgManagerTeam(user_id=user.id, team_id=team.id)
    db.add(jurisdiction)
    db.commit()
    db.refresh(jurisdiction)
    return jurisdiction


def make_document(
    db, *, owner: User, organisation: Organisation,
    access_scope: DocumentAccessScope = DocumentAccessScope.TEAM,
    team: Team | None = None,
) -> Document:
    from uuid import uuid4

    document = Document(
        user_id=owner.id,
        organisation_id=organisation.id,
        team_id=team.id if team else None,
        access_scope=access_scope,
        filename="doc.pdf",
        stored_filename=f"stored-{uuid4()}.pdf",
        content_type="application/pdf",
        file_size=1024,
        status=DocumentStatus.INDEXED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def build_access(db, user: User) -> AccessContext:
    """Mirrors get_access_context's real logic -- genuine team-membership
    and jurisdiction lookups, never fabricated tuples."""

    team_ids = TeamMembershipRepository(db).get_team_ids_by_user_id(user.id)
    jurisdiction_team_ids = OrgManagerTeamRepository(db).get_team_ids_by_user_id(user.id)
    return AccessContext(
        user_id=user.id,
        organisation_id=user.organisation_id,
        team_ids=tuple(team_ids),
        jurisdiction_team_ids=tuple(jurisdiction_team_ids),
        role=user.role,
    )


def make_service(db) -> OrgManagerTeamService:
    return OrgManagerTeamService(
        org_manager_team_repository=OrgManagerTeamRepository(db),
        team_repository=TeamRepository(db),
        user_repository=UserRepository(db),
    )


def get_jurisdiction(db, user: User, team: Team) -> OrgManagerTeam | None:
    statement = select(OrgManagerTeam).where(
        OrgManagerTeam.user_id == user.id,
        OrgManagerTeam.team_id == team.id,
    )
    return db.execute(statement).scalar_one_or_none()


def all_jurisdictions(db) -> list[OrgManagerTeam]:
    return list(db.execute(select(OrgManagerTeam)).scalars().all())


# --------------------------------------------------------------------------- #
# A. Repository
# --------------------------------------------------------------------------- #


def test_repository_grant_creates_one_row(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    repo = OrgManagerTeamRepository(db)

    jurisdiction = repo.grant(user_id=manager.id, team_id=team.id)

    assert jurisdiction.user_id == manager.id
    assert jurisdiction.team_id == team.id
    assert len(all_jurisdictions(db)) == 1


def test_repository_duplicate_grant_rejected(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    repo = OrgManagerTeamRepository(db)
    repo.grant(user_id=manager.id, team_id=team.id)

    with pytest.raises(OrgManagerJurisdictionAlreadyExistsError):
        repo.grant(user_id=manager.id, team_id=team.id)

    assert len(all_jurisdictions(db)) == 1


def test_repository_revoke_deletes_the_row(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    repo = OrgManagerTeamRepository(db)
    repo.grant(user_id=manager.id, team_id=team.id)

    repo.revoke(user_id=manager.id, team_id=team.id)

    assert get_jurisdiction(db, manager, team) is None
    assert all_jurisdictions(db) == []


def test_repository_revoke_nonexistent_raises(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    repo = OrgManagerTeamRepository(db)

    with pytest.raises(OrgManagerJurisdictionNotFoundError):
        repo.revoke(user_id=manager.id, team_id=team.id)


def test_repository_get_jurisdiction_lookup(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    repo = OrgManagerTeamRepository(db)

    assert repo.get_jurisdiction(user_id=manager.id, team_id=team.id) is None

    repo.grant(user_id=manager.id, team_id=team.id)

    found = repo.get_jurisdiction(user_id=manager.id, team_id=team.id)
    assert found is not None
    assert found.team_id == team.id


def test_repository_get_team_ids_by_user_id(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team_a = make_team(db, org, name="Research")
    team_b = make_team(db, org, name="Support")
    repo = OrgManagerTeamRepository(db)
    repo.grant(user_id=manager.id, team_id=team_a.id)
    repo.grant(user_id=manager.id, team_id=team_b.id)

    assert set(repo.get_team_ids_by_user_id(manager.id)) == {team_a.id, team_b.id}


def test_repository_get_team_ids_never_leaks_another_users_jurisdiction(db):
    org = make_organisation(db)
    manager_a = make_user(db, org, username="mgr-a", role=OrgRole.MANAGER)
    manager_b = make_user(db, org, username="mgr-b", role=OrgRole.MANAGER)
    team = make_team(db, org)
    repo = OrgManagerTeamRepository(db)
    repo.grant(user_id=manager_a.id, team_id=team.id)

    assert repo.get_team_ids_by_user_id(manager_a.id) == [team.id]
    assert repo.get_team_ids_by_user_id(manager_b.id) == []


# --------------------------------------------------------------------------- #
# B. Service
# --------------------------------------------------------------------------- #


def test_admin_can_grant_jurisdiction(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)

    result = service.grant_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)

    assert isinstance(result, OrgManagerTeamResponse)
    assert result.user_id == manager.id
    assert result.team_id == team.id
    assert get_jurisdiction(db, manager, team) is not None


def test_admin_can_revoke_jurisdiction(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)
    service.grant_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)

    service.revoke_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)

    assert get_jurisdiction(db, manager, team) is None


def test_member_cannot_grant_jurisdiction(db):
    org = make_organisation(db)
    member = make_user(db, org, username="bob", role=OrgRole.MEMBER)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)

    with pytest.raises(OrgManagerJurisdictionForbiddenError):
        service.grant_jurisdiction(access=build_access(db, member), team_id=team.id, user_id=manager.id)

    assert all_jurisdictions(db) == []


def test_org_manager_cannot_grant_jurisdiction(db):
    """OrgRole.MANAGER alone -- even the target's own role -- never
    confers authority to grant/revoke jurisdiction. Only ADMIN may."""

    org = make_organisation(db)
    acting_manager = make_user(db, org, username="mgr-a", role=OrgRole.MANAGER)
    target_manager = make_user(db, org, username="mgr-b", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)

    with pytest.raises(OrgManagerJurisdictionForbiddenError):
        service.grant_jurisdiction(
            access=build_access(db, acting_manager), team_id=team.id, user_id=target_manager.id,
        )

    assert all_jurisdictions(db) == []


def test_team_manager_cannot_grant_jurisdiction(db):
    """A TeamRole.MANAGER of the target team has no jurisdiction-granting
    authority either -- only OrgRole.ADMIN does."""

    org = make_organisation(db)
    team = make_team(db, org)
    team_manager = make_user(db, org, username="carol", role=OrgRole.MEMBER)
    make_membership(db, user=team_manager, team=team, role=TeamRole.MANAGER)
    target_manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    service = make_service(db)

    with pytest.raises(OrgManagerJurisdictionForbiddenError):
        service.grant_jurisdiction(
            access=build_access(db, team_manager), team_id=team.id, user_id=target_manager.id,
        )

    assert all_jurisdictions(db) == []


def test_target_must_be_org_manager(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    plain_member = make_user(db, org, username="bob", role=OrgRole.MEMBER)
    team = make_team(db, org)
    service = make_service(db)

    with pytest.raises(TargetNotOrgManagerError):
        service.grant_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=plain_member.id)

    assert all_jurisdictions(db) == []


def test_target_admin_is_not_org_manager(db):
    """ADMIN is a distinct role from OrgRole.MANAGER -- an ADMIN target
    does not qualify for jurisdiction either."""

    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    other_admin = make_user(db, org, username="root2", role=OrgRole.ADMIN)
    team = make_team(db, org)
    service = make_service(db)

    with pytest.raises(TargetNotOrgManagerError):
        service.grant_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=other_admin.id)


def test_cross_org_team_rejected(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    admin_a = make_user(db, org_a, username="root", role=OrgRole.ADMIN)
    manager = make_user(db, org_a, username="mgr", role=OrgRole.MANAGER)
    team_b = make_team(db, org_b, name="Support")
    service = make_service(db)

    with pytest.raises(TeamNotFoundError):
        service.grant_jurisdiction(access=build_access(db, admin_a), team_id=team_b.id, user_id=manager.id)


def test_cross_org_target_user_rejected(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    admin_a = make_user(db, org_a, username="root", role=OrgRole.ADMIN)
    team_a = make_team(db, org_a)
    manager_b = make_user(db, org_b, username="mgr", role=OrgRole.MANAGER)
    service = make_service(db)

    with pytest.raises(UserNotFoundError):
        service.grant_jurisdiction(access=build_access(db, admin_a), team_id=team_a.id, user_id=manager_b.id)


def test_duplicate_grant_rejected_at_service_level(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)
    service.grant_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)

    with pytest.raises(OrgManagerJurisdictionAlreadyExistsError):
        service.grant_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)


def test_revoke_nonexistent_rejected_at_service_level(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)

    with pytest.raises(OrgManagerJurisdictionNotFoundError):
        service.revoke_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)


def test_authorization_runs_before_target_resolution(db):
    """A non-ADMIN actor must be rejected before the target team/user is
    even resolved -- proven by supplying a nonexistent team_id/user_id
    and confirming the forbidden error still fires (not a not-found
    error), matching the enumeration-safety ordering established by
    RBAC-5H/5I."""

    org = make_organisation(db)
    member = make_user(db, org, username="bob", role=OrgRole.MEMBER)
    service = make_service(db)

    with pytest.raises(OrgManagerJurisdictionForbiddenError):
        service.grant_jurisdiction(access=build_access(db, member), team_id=999999, user_id=999999)


# --------------------------------------------------------------------------- #
# C. API
# --------------------------------------------------------------------------- #


def test_api_grant_route_returns_jurisdiction(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)

    result = grant_org_manager_jurisdiction(
        team_id=team.id, user_id=manager.id, access=build_access(db, admin), org_manager_team_service=service,
    )

    assert isinstance(result, OrgManagerTeamResponse)
    assert result.team_id == team.id
    assert result.user_id == manager.id


def test_api_revoke_route_removes_jurisdiction(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)
    service.grant_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)

    revoke_org_manager_jurisdiction(
        team_id=team.id, user_id=manager.id, access=build_access(db, admin), org_manager_team_service=service,
    )

    assert get_jurisdiction(db, manager, team) is None


def test_api_grant_route_forbidden_for_non_admin(db):
    org = make_organisation(db)
    member = make_user(db, org, username="bob", role=OrgRole.MEMBER)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)

    with pytest.raises(OrgManagerJurisdictionForbiddenError):
        grant_org_manager_jurisdiction(
            team_id=team.id, user_id=manager.id, access=build_access(db, member), org_manager_team_service=service,
        )


def test_api_grant_route_rejects_non_org_manager_target(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    plain_member = make_user(db, org, username="bob", role=OrgRole.MEMBER)
    team = make_team(db, org)
    service = make_service(db)

    with pytest.raises(TargetNotOrgManagerError):
        grant_org_manager_jurisdiction(
            team_id=team.id, user_id=plain_member.id, access=build_access(db, admin), org_manager_team_service=service,
        )


# --------------------------------------------------------------------------- #
# D/E/F. SQL/Qdrant visibility + parity
#
# The Qdrant side of every parity test below calls the REAL, production
# ``DenseRepository._authorization_filter(access)`` (a ``@staticmethod`` --
# no client, no instance, no network needed) and then walks the actual
# ``Filter`` object it returns against a document's own payload shape,
# using Qdrant's own must=AND / should=OR-at-least-one / must_not=NOT-any
# semantics. Nothing here reimplements the authorization branch logic --
# a real regression in ``_authorization_filter`` (dropping the
# jurisdiction branch, swapping MANAGER for MEMBER, dropping an
# organisation_id condition, changing MatchAny contents, incorrect
# must/should nesting, or widening the ADMIN branch) changes the actual
# Filter object produced, which this evaluator faithfully reflects, so
# any such regression fails these tests.
# --------------------------------------------------------------------------- #


def _document_payload(document: Document) -> dict:
    """The subset of a real Qdrant point payload that
    ``_authorization_filter`` conditions against, built from an actual
    ``Document`` row -- never independently re-derived authorization
    logic, just the raw field values a real indexed point would carry."""

    return {
        "user_id": document.user_id,
        "organisation_id": document.organisation_id,
        "team_id": document.team_id,
        "access_scope": document.access_scope.value,
        "is_reference": False,
        "is_appendix": False,
    }


def _evaluate_qdrant_condition(condition, payload: dict) -> bool:
    """Evaluate one condition node (a nested Filter, a FieldCondition, or
    an IsEmptyCondition) from a real qdrant_client Filter tree against a
    payload dict."""

    if isinstance(condition, Filter):
        return _evaluate_qdrant_filter(condition, payload)

    if isinstance(condition, FieldCondition):
        match = condition.match
        if isinstance(match, MatchValue):
            return payload.get(condition.key) == match.value
        if isinstance(match, MatchAny):
            return payload.get(condition.key) in match.any
        raise NotImplementedError(f"Unsupported match type in parity evaluator: {type(match)!r}")

    if isinstance(condition, IsEmptyCondition):
        key = condition.is_empty.key
        return key not in payload or payload[key] is None

    raise NotImplementedError(f"Unsupported condition type in parity evaluator: {type(condition)!r}")


def _evaluate_qdrant_filter(filter_obj: Filter, payload: dict) -> bool:
    """Evaluate a real qdrant_client ``Filter`` object against a payload
    dict, following Qdrant's own filter semantics: ``must`` is AND
    (vacuously true if empty), ``should`` is OR-at-least-one (vacuously
    true if empty/absent -- it imposes no restriction on its own),
    ``must_not`` is NOT-any (vacuously true if empty). This is the exact
    same walking technique ``test_rbac_5c_authorization_filter.py``
    already uses to inspect branch structure -- applied here to actually
    *evaluate* the tree against one document's payload instead of just
    inspecting its shape."""

    def _as_list(group):
        if group is None:
            return []
        return group if isinstance(group, list) else [group]

    must = _as_list(filter_obj.must)
    should = _as_list(filter_obj.should)
    must_not = _as_list(filter_obj.must_not)

    must_ok = all(_evaluate_qdrant_condition(c, payload) for c in must)
    should_ok = any(_evaluate_qdrant_condition(c, payload) for c in should) if should else True
    must_not_ok = not any(_evaluate_qdrant_condition(c, payload) for c in must_not)

    return must_ok and should_ok and must_not_ok


def _qdrant_would_include_document(access: AccessContext, document: Document) -> bool:
    """Build the REAL production Qdrant authorization filter for
    ``access`` and evaluate it against ``document``'s real payload shape
    -- exercises ``DenseRepository._authorization_filter`` itself, not a
    reimplementation of its logic."""

    real_filter = DenseRepository._authorization_filter(access)
    return _evaluate_qdrant_filter(real_filter, _document_payload(document))


def _sql_would_include_document(db, access: AccessContext, document_id: int) -> bool:
    return DocumentRepository(db).get_by_id_visible(document_id=document_id, access=access) is not None


@pytest.mark.parametrize(
    "role,is_member,has_jurisdiction,same_org",
    [
        (OrgRole.MEMBER, True, False, True),       # 1. Team MEMBER + own team -> visible
        (OrgRole.MANAGER, True, False, True),      # 2. Team MANAGER (via TeamRole) + own team -> visible
        (OrgRole.MANAGER, False, True, True),      # 3. Org MANAGER + jurisdiction team -> visible
        (OrgRole.MANAGER, False, False, True),     # 4. Org MANAGER + non-jurisdiction team -> denied
        (OrgRole.ADMIN, False, False, True),       # 5. ADMIN + same-org TEAM document -> visible
        (OrgRole.ADMIN, False, False, False),      # 6. ADMIN + different-org TEAM document -> denied
        (OrgRole.MEMBER, False, False, True),      # 7. Same-org unrelated MEMBER -> denied
        (OrgRole.MEMBER, True, False, False),      # 8. Cross-org "team MEMBER" (different org entirely) -> denied
    ],
)
def test_sql_and_qdrant_visibility_parity(db, role, is_member, has_jurisdiction, same_org):
    """For every actor/document combination in the matrix, SQL
    (``DocumentRepository.get_by_id_visible``, real production code) and
    Qdrant (the real ``DenseRepository._authorization_filter`` Filter,
    evaluated against the document's actual payload) must agree on
    visibility. Case 8 places the actor in a wholly different
    organisation from the document/team -- a genuine cross-org actor,
    not merely a membership row that happens to not apply."""

    org = make_organisation(db, slug="acme")
    other_org = make_organisation(db, slug="globex")
    doc_org = org if same_org else other_org
    team = make_team(db, doc_org, name="Research")
    owner = make_user(db, doc_org, username="owner")
    doc = make_document(db, owner=owner, organisation=doc_org, access_scope=DocumentAccessScope.TEAM, team=team)

    actor_org = org if same_org else other_org
    actor = make_user(db, actor_org, username="actor", role=role)
    if is_member and same_org:
        role_for_membership = TeamRole.MANAGER if role == OrgRole.MANAGER else TeamRole.MEMBER
        make_membership(db, user=actor, team=team, role=role_for_membership)
    if has_jurisdiction and same_org:
        make_jurisdiction(db, user=actor, team=team)

    access = build_access(db, actor)

    sql_result = _sql_would_include_document(db, access, doc.id)
    qdrant_result = _qdrant_would_include_document(access, doc)

    assert sql_result == qdrant_result


def test_sql_and_qdrant_parity_empty_team_ids_and_jurisdiction(db):
    """9/10. An actor with empty team_ids and empty jurisdiction_team_ids
    (a plain MEMBER with no memberships/jurisdiction at all) must be
    denied by both real authorization paths -- and must never
    accidentally produce a broad/empty-list match in either."""

    org = make_organisation(db, slug="acme")
    team = make_team(db, org, name="Research")
    owner = make_user(db, org, username="owner")
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.TEAM, team=team)

    actor = make_user(db, org, username="actor", role=OrgRole.MANAGER)
    # Deliberately no membership, no jurisdiction -- team_ids and
    # jurisdiction_team_ids both resolve to the empty tuple.
    access = build_access(db, actor)
    assert access.team_ids == ()
    assert access.jurisdiction_team_ids == ()

    assert _sql_would_include_document(db, access, doc.id) is False
    assert _qdrant_would_include_document(access, doc) is False


def test_sql_and_qdrant_parity_different_team_ids(db):
    """11. An Org Manager with jurisdiction over Team A must not be able
    to see Team B's document -- different team ids must not collide in
    either authorization path."""

    org = make_organisation(db, slug="acme")
    team_a = make_team(db, org, name="Research")
    team_b = make_team(db, org, name="Support")
    owner = make_user(db, org, username="owner")
    doc_b = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.TEAM, team=team_b)

    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    make_jurisdiction(db, user=manager, team=team_a)
    access = build_access(db, manager)

    assert _sql_would_include_document(db, access, doc_b.id) is False
    assert _qdrant_would_include_document(access, doc_b) is False


def test_sql_and_qdrant_parity_individual_scope(db):
    """Preserve INDIVIDUAL-scope parity coverage alongside the TEAM-scope
    matrix above -- owner sees their own document, a non-owner does not,
    in both real authorization paths."""

    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="owner")
    other = make_user(db, org, username="other")
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.INDIVIDUAL)

    owner_access = build_access(db, owner)
    other_access = build_access(db, other)

    assert _sql_would_include_document(db, owner_access, doc.id) is True
    assert _qdrant_would_include_document(owner_access, doc) is True
    assert _sql_would_include_document(db, other_access, doc.id) is False
    assert _qdrant_would_include_document(other_access, doc) is False


def test_sql_and_qdrant_parity_organisation_scope(db):
    """Preserve ORGANISATION-scope parity coverage -- ADMIN sees an
    ORGANISATION-scoped document in their own org, a plain MEMBER does
    not, in both real authorization paths."""

    org = make_organisation(db, slug="acme")
    owner = make_user(db, org, username="owner")
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    member = make_user(db, org, username="bob", role=OrgRole.MEMBER)
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.ORGANISATION)

    admin_access = build_access(db, admin)
    member_access = build_access(db, member)

    assert _sql_would_include_document(db, admin_access, doc.id) is True
    assert _qdrant_would_include_document(admin_access, doc) is True
    assert _sql_would_include_document(db, member_access, doc.id) is False
    assert _qdrant_would_include_document(member_access, doc) is False


def test_sql_and_qdrant_parity_across_full_matrix(db):
    """A denser sweep across role x membership x jurisdiction x same-org,
    asserting SQL/Qdrant agreement -- against the real production Qdrant
    filter -- for every combination in one pass."""

    org = make_organisation(db, slug="acme")
    other_org = make_organisation(db, slug="globex")
    team = make_team(db, org, name="Research")
    owner = make_user(db, org, username="owner")
    doc = make_document(db, owner=owner, organisation=org, access_scope=DocumentAccessScope.TEAM, team=team)

    combos = []
    for role in (OrgRole.MEMBER, OrgRole.MANAGER, OrgRole.ADMIN):
        for is_member in (True, False):
            for has_jurisdiction in (True, False):
                for user_org in (org, other_org):
                    combos.append((role, is_member, has_jurisdiction, user_org))

    for index, (role, is_member, has_jurisdiction, user_org) in enumerate(combos):
        actor = make_user(db, user_org, username=f"actor{index}", role=role)
        if is_member and user_org is org:
            make_membership(db, user=actor, team=team, role=TeamRole.MEMBER)
        if has_jurisdiction and user_org is org:
            make_jurisdiction(db, user=actor, team=team)

        access = build_access(db, actor)

        sql_result = _sql_would_include_document(db, access, doc.id)
        qdrant_result = _qdrant_would_include_document(access, doc)

        assert sql_result == qdrant_result, (
            f"parity mismatch: role={role}, is_member={is_member}, "
            f"has_jurisdiction={has_jurisdiction}, same_org={user_org is org}, "
            f"sql={sql_result}, qdrant={qdrant_result}"
        )


def test_admin_from_other_organisation_cannot_read_team_document(db):
    """LOW-1: explicit standalone cross-org case -- ADMIN of organisation
    B must never see a TEAM-scoped document belonging to organisation A,
    via either the real SQL or the real Qdrant authorization path."""

    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    team_a = make_team(db, org_a, name="Research")
    owner = make_user(db, org_a, username="owner")
    doc = make_document(db, owner=owner, organisation=org_a, access_scope=DocumentAccessScope.TEAM, team=team_a)

    admin_b = make_user(db, org_b, username="root", role=OrgRole.ADMIN)
    access = build_access(db, admin_b)

    assert _sql_would_include_document(db, access, doc.id) is False
    assert _qdrant_would_include_document(access, doc) is False


# --------------------------------------------------------------------------- #
# H. Separation: TeamMembership vs jurisdiction
# --------------------------------------------------------------------------- #


def test_grant_does_not_create_team_membership(db):
    org = make_organisation(db)
    admin = make_user(db, org, username="root", role=OrgRole.ADMIN)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    service = make_service(db)

    service.grant_jurisdiction(access=build_access(db, admin), team_id=team.id, user_id=manager.id)

    statement = select(TeamMembership).where(
        TeamMembership.user_id == manager.id, TeamMembership.team_id == team.id,
    )
    assert db.execute(statement).scalar_one_or_none() is None


def test_team_membership_does_not_create_jurisdiction(db):
    org = make_organisation(db)
    manager = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    team = make_team(db, org)
    make_membership(db, user=manager, team=team, role=TeamRole.MANAGER)

    assert get_jurisdiction(db, manager, team) is None


def test_team_role_does_not_affect_grant_authorization(db):
    """Being a TeamRole.MANAGER of the exact target team still does not
    grant jurisdiction-mutation authority -- only OrgRole.ADMIN does."""

    org = make_organisation(db)
    team = make_team(db, org)
    team_manager = make_user(db, org, username="carol", role=OrgRole.MEMBER)
    make_membership(db, user=team_manager, team=team, role=TeamRole.MANAGER)
    target = make_user(db, org, username="mgr", role=OrgRole.MANAGER)
    service = make_service(db)

    with pytest.raises(OrgManagerJurisdictionForbiddenError):
        service.grant_jurisdiction(access=build_access(db, team_manager), team_id=team.id, user_id=target.id)


# --------------------------------------------------------------------------- #
# I. Cross-org security matrix
# --------------------------------------------------------------------------- #


def test_actor_and_team_different_orgs_denied(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    admin_a = make_user(db, org_a, username="root", role=OrgRole.ADMIN)
    team_b = make_team(db, org_b)
    manager_b = make_user(db, org_b, username="mgr", role=OrgRole.MANAGER)
    service = make_service(db)

    with pytest.raises(TeamNotFoundError):
        service.grant_jurisdiction(access=build_access(db, admin_a), team_id=team_b.id, user_id=manager_b.id)


def test_actor_and_target_different_orgs_denied(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    admin_a = make_user(db, org_a, username="root", role=OrgRole.ADMIN)
    team_a = make_team(db, org_a)
    manager_b = make_user(db, org_b, username="mgr", role=OrgRole.MANAGER)
    service = make_service(db)

    with pytest.raises(UserNotFoundError):
        service.grant_jurisdiction(access=build_access(db, admin_a), team_id=team_a.id, user_id=manager_b.id)


def test_team_belongs_to_actor_org_but_target_elsewhere_denied(db):
    org_a = make_organisation(db, slug="acme")
    org_b = make_organisation(db, slug="globex")
    admin_a = make_user(db, org_a, username="root", role=OrgRole.ADMIN)
    team_a = make_team(db, org_a)
    manager_b = make_user(db, org_b, username="mgr", role=OrgRole.MANAGER)
    service = make_service(db)

    with pytest.raises(UserNotFoundError):
        service.grant_jurisdiction(access=build_access(db, admin_a), team_id=team_a.id, user_id=manager_b.id)


# --------------------------------------------------------------------------- #
# Permanent concurrency regression test: duplicate jurisdiction grant
# --------------------------------------------------------------------------- #


def _make_file_backed_session_factory(tmp_path, filename: str):
    engine = create_engine(f"sqlite:///{tmp_path / filename}")
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_concurrent_duplicate_grant_leaves_one_jurisdiction(tmp_path):
    """Permanent regression test mirroring RBAC-5I's established
    concurrency-test pattern: two real OS threads, each with its own
    session against the same file-backed SQLite database, both call the
    actual production ``OrgManagerTeamRepository.grant`` for the exact
    same (user_id, team_id) pair, synchronized by a threading.Barrier so
    both inserts genuinely race against the real database unique
    constraint. Exactly one must succeed; the other must receive a clean
    ``OrgManagerJurisdictionAlreadyExistsError`` -- never a raw
    IntegrityError."""

    engine, session_factory = _make_file_backed_session_factory(
        tmp_path, "rbac_5j_concurrency_grant.db",
    )

    setup_session = session_factory()
    try:
        org = make_organisation(setup_session)
        manager = make_user(setup_session, org, username="mgr", role=OrgRole.MANAGER)
        team = make_team(setup_session, org)
        team_id = team.id
        manager_id = manager.id
    finally:
        setup_session.close()

    barrier = threading.Barrier(2)
    outcomes: dict[str, str] = {}

    def worker(key: str) -> None:
        session = session_factory()
        try:
            repository = OrgManagerTeamRepository(session)

            barrier.wait(timeout=10)

            try:
                repository.grant(user_id=manager_id, team_id=team_id)
                outcomes[key] = "granted"
            except OrgManagerJurisdictionAlreadyExistsError:
                outcomes[key] = "already_exists"

        except BaseException as exc:  # noqa: BLE001 -- must be captured, never swallowed silently
            outcomes[key] = f"unexpected: {exc!r}"

        finally:
            session.close()

    thread_a = threading.Thread(target=worker, args=("a",))
    thread_b = threading.Thread(target=worker, args=("b",))

    thread_a.start()
    thread_b.start()
    thread_a.join(timeout=15)
    thread_b.join(timeout=15)

    try:
        assert not thread_a.is_alive(), "worker thread A did not terminate"
        assert not thread_b.is_alive(), "worker thread B did not terminate"

        assert set(outcomes.keys()) == {"a", "b"}, f"missing worker outcome(s): {outcomes}"

        for key, outcome in outcomes.items():
            assert outcome in ("granted", "already_exists"), (
                f"thread {key!r} raised an unexpected exception "
                f"(a raw IntegrityError must never escape): {outcome}"
            )

        assert sorted(outcomes.values()) == ["already_exists", "granted"], (
            "exactly one grant must succeed and exactly one must be "
            f"rejected as a duplicate; got {outcomes}"
        )

        verify_session = session_factory()
        try:
            rows = verify_session.execute(
                select(OrgManagerTeam).where(
                    OrgManagerTeam.team_id == team_id,
                    OrgManagerTeam.user_id == manager_id,
                )
            ).scalars().all()

            assert len(rows) == 1, (
                f"expected exactly one jurisdiction row, found {len(rows)}"
            )
        finally:
            verify_session.close()

    finally:
        engine.dispose()
