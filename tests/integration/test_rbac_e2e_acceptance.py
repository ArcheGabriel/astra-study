"""
RBAC-10A/10B: end-to-end acceptance tests for the multi-step RBAC
workflows that no existing test exercises together:

1. document upload -> RBAC metadata -> retrieval
2. jurisdiction grant -> retrieval visibility
3. jurisdiction revoke -> retrieval visibility removal
4. team membership add -> retrieval visibility
5. team membership remove -> retrieval visibility removal
6. ORGANISATION document upload -> retrieval ALLOW/DENY (incl. a real
   second organisation) -> deletion -> SQL + Qdrant cleanup (RBAC-10B)
7. TEAM document deletion authorization (TeamRole.MANAGER vs MEMBER)
   -> SQL + Qdrant cleanup (RBAC-10B)
8. INDIVIDUAL document deletion -> SQL + Qdrant cleanup -> retrieval
   removed (RBAC-10B)
9. TEAM document uploader-leaves-team asymmetry: retrieval is lost,
   delete authority is retained -> SQL + Qdrant cleanup (RBAC-10B)

Every workflow below drives the REAL FastAPI application through
``fastapi.testclient.TestClient`` -- real routers, real services, real
repositories, real JWT authentication (``POST /auth/login`` +
``Authorization: Bearer`` headers) -- against an isolated in-memory
SQLite database and the isolated ``astra_study_test`` Qdrant collection.
No ``AccessContext`` is ever hand-constructed for a scenario under test;
every authorization decision is produced by calling the real production
functions (``get_current_user`` / ``get_access_context`` /
``DenseRepository._authorization_filter`` via ``hybrid_search``) with
real, server-derived state.

Isolation
---------
- SQLite: a fresh ``sqlite://`` in-memory database (SQLAlchemy
  ``StaticPool`` so every ``get_db()`` call across the whole TestClient
  session shares the one connection) is created per test function and
  disposed at teardown. The real dev database (``astra_study.db``) is
  never opened -- ``app.database.session.get_db`` is overridden via
  ``app.dependency_overrides`` before any request is made.
- Qdrant: ``tests/conftest.py`` (imported before this module, unmodified
  by this milestone) forces ``DenseRepository.COLLECTION_NAME`` to the
  dedicated ``astra_study_test`` collection and raises immediately if
  anything else is requested. Every fixture below re-asserts the
  collection name at every step, on top of that session-level guard,
  mirroring ``tests/integration/test_rbac_qdrant_authorization.py``'s
  existing precedent exactly. The production ``astra_study`` collection
  is never named, referenced, or constructed anywhere in this file.

Two deliberate, documented deviations from a literal "real end-to-end"
reading (both explained in full in the RBAC-10A implementation report):

1. **Indexing shortcut.** ``POST /documents/upload`` is exercised for
   real (real ``DocumentService.upload_documents``, real SQLite
   ``Document`` row, real RBAC-field stamping, real ``BackgroundTasks``
   scheduling). The background extraction step itself is substituted
   via ``app.dependency_overrides[get_ingestion_service]`` with
   ``_FakeIngestionService`` -- it loads the real ``Document`` row (via
   the real, unmodified ``DocumentRepository``), stamps a single
   deterministic chunk with that row's *real* ``document.id`` /
   ``user_id`` / ``organisation_id`` / ``team_id`` / ``access_scope``
   (the exact fields the real ``IngestionService.ingest_document``
   stamps), builds its Qdrant payload via the real, unmodified
   ``HybridMapper.build_payload``, and upserts it via the real,
   unmodified ``DenseRepository.upsert``. Real Docling extraction and
   real OpenAI embedding calls are skipped -- mirroring this
   repository's own established precedent in
   ``test_rbac_qdrant_authorization.py`` (small, deterministic,
   non-semantic vectors; "only payload fields participate in
   authorization filtering") for the same reason: determinism, speed,
   and no external API dependency, while still exercising the real
   production payload/indexing code the authorization filter depends
   on.
2. **No non-LLM retrieval endpoint exists.** This API's only retrieval
   path is the chat/message pipeline (``AIPipeline`` -> real OpenAI
   query-rewrite + generation calls), which is unsuitable for a
   deterministic authorization test. "Retrieval" here is therefore
   performed by deriving a real ``AccessContext`` via direct calls to
   the real, unmodified ``get_current_user`` / ``get_access_context``
   dependency functions (never a hand-built ``AccessContext``) using the
   JWT obtained from a real ``POST /auth/login`` call, then calling the
   real, unmodified ``DenseRepository.hybrid_search`` -- the exact
   method that builds and applies ``_authorization_filter`` against a
   real Qdrant server. No authorization logic is reimplemented anywhere
   in this file.

Both deviations are necessary substitutions for infrastructure this
repository does not have (a fast/deterministic extraction+embedding path,
a non-LLM retrieval endpoint) -- they never substitute for, bypass, or
reimplement any authorization decision itself.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import Depends
from qdrant_client.models import PointStruct, SparseVector
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Import every model module so Base.metadata is complete before create_all
# -- mirrors every existing tests/unit/test_rbac_*.py factory file.
import app.models  # noqa: F401

from app.chunking.models import ChunkMetadata, DocumentChunk
from app.config.settings import settings
from app.core.security import security
from app.database.base import Base
from app.database.session import get_db
from app.dependencies.access import get_access_context
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_ingestion_service
from app.embeddings.models import EmbeddedChunk, EmbeddingMetadata, EmbeddingVector
from app.enums.document import DocumentStatus
from app.enums.organisation import OrgRole
from app.enums.team import TeamRole
from app.main import app
from app.models.organisation import Organisation
from app.models.team import Team
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.retrieval.access import AccessContext
from app.search.dense.repository import DenseRepository
from app.search.hybrid.mapper import HybridMapper
from fastapi.testclient import TestClient
from tests.conftest import DEDICATED_TEST_COLLECTION, PRODUCTION_COLLECTION

# A single, fixed-length, non-semantic dense query/document vector --
# correct dimensionality for the real collection config, no embedding
# model involved (see module docstring, deviation 1).
_DENSE_VECTOR = [0.0] * settings.EMBEDDING_DIMENSIONS
_SPARSE_INDICES = [0]
_SPARSE_VALUES = [1.0]

_FIXTURE_PASSWORD = "Password@123"

# A minimal, syntactically-valid-enough PDF. Content is never parsed --
# the fake ingestion service (deviation 1) never touches file bytes --
# only the extension/content-type/non-empty checks in
# ``DocumentValidator`` need to pass.
_MINIMAL_PDF_BYTES = b"%PDF-1.4\n%%EOF\n"


# --------------------------------------------------------------------------- #
# Fake ingestion service (deviation 1 -- see module docstring)
# --------------------------------------------------------------------------- #


class _FakeIngestionService:
    """
    Test double for ``IngestionService``, wired in via
    ``app.dependency_overrides[get_ingestion_service]``.

    Loads the real ``Document`` row (real ``DocumentRepository``, the
    same isolated SQLite session as the request that created it),
    stamps one deterministic chunk with that row's real RBAC fields
    exactly as ``IngestionService.ingest_document`` does, builds its
    payload via the real ``HybridMapper.build_payload``, and upserts it
    via the real ``DenseRepository.upsert`` into ``astra_study_test``.
    Never reimplements RBAC stamping logic independently -- it reads the
    already-authorized ``Document`` row the real endpoint just created.
    """

    def __init__(self, db: Session) -> None:
        self.document_repository = DocumentRepository(db)

    def ingest_document(self, *, document_id: int) -> None:
        document = self.document_repository.get_by_id(document_id)

        if document is None:
            return

        metadata = ChunkMetadata(
            document_id=document.id,
            document_uuid=uuid4(),
            document_name=document.filename,
            user_id=document.user_id,
            organisation_id=document.organisation_id,
            team_id=document.team_id,
            access_scope=document.access_scope,
            chunk_uuid=uuid4(),
        )

        chunk = DocumentChunk(
            "RBAC-10A deterministic fixture chunk text.",
            0,
            metadata,
        )

        embedded = EmbeddedChunk(
            chunk,
            EmbeddingVector([0.1, 0.2]),
            EmbeddingMetadata("rbac-10a-fixture", 2),
        )

        payload = HybridMapper.build_payload(embedded)

        point = PointStruct(
            id=str(metadata.chunk_uuid),
            vector={
                settings.QDRANT_VECTOR_NAME: _DENSE_VECTOR,
                settings.QDRANT_SPARSE_VECTOR_NAME: SparseVector(
                    indices=_SPARSE_INDICES,
                    values=_SPARSE_VALUES,
                ),
            },
            payload=payload,
        )

        DenseRepository().upsert([point])

        self.document_repository.update_status(
            document_id=document.id,
            status=DocumentStatus.INDEXED,
        )


# --------------------------------------------------------------------------- #
# SQLite factories -- mirrors every existing tests/unit/test_rbac_*.py file
# --------------------------------------------------------------------------- #


def make_organisation(db: Session, *, slug: str = "rbac10a") -> Organisation:
    organisation = Organisation(name=slug.title(), slug=slug)
    db.add(organisation)
    db.commit()
    db.refresh(organisation)
    return organisation


def make_user(
    db: Session,
    organisation: Organisation,
    *,
    username: str,
    role: OrgRole = OrgRole.MEMBER,
) -> User:
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=security.hash_password(_FIXTURE_PASSWORD),
        organisation_id=organisation.id,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_team(db: Session, organisation: Organisation, *, name: str) -> Team:
    team = Team(organisation_id=organisation.id, name=name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def make_membership(
    db: Session, *, user: User, team: Team, role: TeamRole,
) -> TeamMembership:
    membership = TeamMembership(user_id=user.id, team_id=team.id, role=role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


# --------------------------------------------------------------------------- #
# The RBAC-10A environment fixture
# --------------------------------------------------------------------------- #


class _Env:
    """
    Everything one RBAC-10A test needs: an authenticated ``TestClient``,
    the isolated ``DenseRepository``, and the fixture users/team it was
    given. Deliberately a plain data holder, not a base-test-case class
    -- each test function owns its own instance via the ``env`` fixture
    below, so tests stay independent.
    """

    def __init__(
        self,
        *,
        client: TestClient,
        db_sessionmaker: sessionmaker,
        dense_repository: DenseRepository,
        organisation: Organisation,
        team: Team,
        users: dict[str, User],
    ) -> None:
        self.client = client
        self.db_sessionmaker = db_sessionmaker
        self.dense_repository = dense_repository
        self.organisation = organisation
        self.team = team
        self.users = users
        self.uploaded_document_ids: list[int] = []

    def login(self, username: str) -> str:
        """
        Real ``POST /auth/login`` call. Returns the raw JWT access
        token -- never a hand-built ``AccessContext``.
        """

        user = self.users[username]

        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": _FIXTURE_PASSWORD},
        )

        assert response.status_code == 200, response.text

        return response.json()["access_token"]

    def auth_headers(self, username: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.login(username)}"}

    def upload(
        self,
        username: str,
        *,
        filename: str,
        access_scope: str | None = None,
        team_id: int | None = None,
    ) -> int:
        """
        Real ``POST /documents/upload`` multipart call, authenticated as
        ``username``. Returns the created ``Document.id``. The real
        endpoint's ``BackgroundTasks`` scheduling (now backed by
        ``_FakeIngestionService`` -- see module docstring, deviation 1)
        runs synchronously within this call under ``TestClient``.
        """

        data: dict[str, str] = {}

        if access_scope is not None:
            data["access_scope"] = access_scope

        if team_id is not None:
            data["team_id"] = str(team_id)

        response = self.client.post(
            "/api/v1/documents/upload",
            headers=self.auth_headers(username),
            files=[("files", (filename, _MINIMAL_PDF_BYTES, "application/pdf"))],
            data=data,
        )

        assert response.status_code == 201, response.text

        documents = response.json()

        assert len(documents) == 1

        document = documents[0]
        document_id = document["id"]

        # The response body is serialized BEFORE BackgroundTasks run (this
        # is standard FastAPI/Starlette response ordering, not specific to
        # the fake ingestion service), so document["status"] here is still
        # "uploaded". By the time TestClient's .post() call returns to this
        # point, though, the background task has already executed
        # synchronously (TestClient drives the whole ASGI response cycle,
        # background tasks included, before control returns) -- so a fresh
        # DB read now reflects its result.
        db = self.db_sessionmaker()
        try:
            indexed_document = DocumentRepository(db).get_by_id(document_id)
            assert indexed_document is not None
            assert indexed_document.status == DocumentStatus.INDEXED, indexed_document.status
        finally:
            db.close()

        self.uploaded_document_ids.append(document_id)

        return document_id

    def retrieve_chunk_uuids(self, username: str) -> set[str]:
        """
        The "retrieval" leg (see module docstring, deviation 2): derive
        a real ``AccessContext`` via the real, unmodified
        ``get_current_user`` / ``get_access_context`` functions from a
        real JWT, then call the real, unmodified
        ``DenseRepository.hybrid_search`` -- the exact production method
        that builds and applies ``_authorization_filter`` against the
        real ``astra_study_test`` Qdrant server. Never a hand-built
        ``AccessContext``, never a reimplemented filter.
        """

        token = self.login(username)

        db = self.db_sessionmaker()

        try:
            current_user = get_current_user(token=token, db=db)
            access: AccessContext = get_access_context(
                current_user=current_user,
                db=db,
            )
        finally:
            db.close()

        results = self.dense_repository.hybrid_search(
            dense_vector=_DENSE_VECTOR,
            sparse_indices=_SPARSE_INDICES,
            sparse_values=_SPARSE_VALUES,
            access=access,
            limit=50,
        )

        return {str(r.chunk_uuid) for r in results}

    def grant_jurisdiction(self, *, admin: str, team_id: int, user_id: int):
        return self.client.post(
            f"/api/v1/teams/{team_id}/managers/{user_id}",
            headers=self.auth_headers(admin),
        )

    def revoke_jurisdiction(self, *, admin: str, team_id: int, user_id: int):
        return self.client.delete(
            f"/api/v1/teams/{team_id}/managers/{user_id}",
            headers=self.auth_headers(admin),
        )

    def add_member(self, *, manager: str, team_id: int, user_id: int):
        return self.client.post(
            f"/api/v1/teams/{team_id}/members",
            headers=self.auth_headers(manager),
            json={"user_id": user_id},
        )

    def remove_member(self, *, manager: str, team_id: int, user_id: int):
        return self.client.delete(
            f"/api/v1/teams/{team_id}/members/{user_id}",
            headers=self.auth_headers(manager),
        )

    def delete_document(self, username: str, document_id: int):
        """
        Real ``DELETE /documents/{document_id}`` call, authenticated as
        ``username``. Returns the raw response so individual tests can
        assert the expected status code (204 on success, 404 for an
        unauthorized/nonexistent document -- see
        ``DocumentService._can_delete``/``DocumentNotFoundError``).
        """

        return self.client.delete(
            f"/api/v1/documents/{document_id}",
            headers=self.auth_headers(username),
        )


@pytest.fixture()
def env():
    """
    Function-scoped: every test gets its own isolated SQLite database
    and its own freshly created/dropped ``astra_study_test`` Qdrant
    collection, so tests never depend on execution order or another
    test's leftover state (section 9's isolation requirement).

    Fixture population (org, 5 users, team, the two baseline
    memberships) uses direct SQLAlchemy factories -- this is setup, not
    a workflow under test (see the RBAC-10A prompt's own explicit
    carve-out: "For fixture setup that is not itself under test, direct
    database factories are acceptable"). The operations actually under
    test (upload, jurisdiction grant/revoke, membership add/remove) are
    exclusively performed through real HTTP calls in the test bodies /
    ``_Env`` helper methods above -- never bypassed.
    """

    # ---- Isolated SQLite -------------------------------------------------
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    # expire_on_commit=False: fixture objects (organisation/users/team) are
    # read (.id/.email/.role/...) by test bodies and the _Env helper after
    # their setup session has been closed, matching how a real caller would
    # hold onto already-known ids -- never re-triggering a lazy load against
    # a closed session.
    db_sessionmaker = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False,
    )

    def override_get_db():
        db = db_sessionmaker()
        try:
            yield db
        finally:
            db.close()

    def override_get_ingestion_service(db: Session = Depends(get_db)):
        return _FakeIngestionService(db)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ingestion_service] = override_get_ingestion_service

    client = TestClient(app)

    # ---- Isolated Qdrant collection ---------------------------------------
    dense_repository = DenseRepository()

    assert dense_repository.COLLECTION_NAME == DEDICATED_TEST_COLLECTION
    assert dense_repository.COLLECTION_NAME != PRODUCTION_COLLECTION

    if dense_repository.collection_exists():
        dense_repository.delete_collection()

    dense_repository.create_collection()

    # ---- Fixture data: Organisation A, 5 users, Team A, 2 memberships ----
    setup_db = db_sessionmaker()

    organisation = make_organisation(setup_db, slug=f"rbac10a-{uuid4().hex[:8]}")

    users = {
        "admin": make_user(setup_db, organisation, username=f"admin_{uuid4().hex[:6]}", role=OrgRole.ADMIN),
        "org_manager": make_user(setup_db, organisation, username=f"orgmgr_{uuid4().hex[:6]}", role=OrgRole.MANAGER),
        "team_manager": make_user(setup_db, organisation, username=f"teammgr_{uuid4().hex[:6]}", role=OrgRole.MEMBER),
        "team_member": make_user(setup_db, organisation, username=f"teammem_{uuid4().hex[:6]}", role=OrgRole.MEMBER),
        "other_member": make_user(setup_db, organisation, username=f"other_{uuid4().hex[:6]}", role=OrgRole.MEMBER),
    }

    team = make_team(setup_db, organisation, name=f"Team A {uuid4().hex[:6]}")

    make_membership(setup_db, user=users["team_manager"], team=team, role=TeamRole.MANAGER)
    make_membership(setup_db, user=users["team_member"], team=team, role=TeamRole.MEMBER)

    setup_db.close()

    environment = _Env(
        client=client,
        db_sessionmaker=db_sessionmaker,
        dense_repository=dense_repository,
        organisation=organisation,
        team=team,
        users=users,
    )

    try:
        yield environment
    finally:
        # Fail loudly (section 9): no try/except swallowing here -- a
        # cleanup failure must surface as a test error, not be silently
        # ignored.
        assert dense_repository.COLLECTION_NAME == DEDICATED_TEST_COLLECTION
        assert dense_repository.COLLECTION_NAME != PRODUCTION_COLLECTION
        if dense_repository.collection_exists():
            dense_repository.delete_collection()

        # Best-effort removal of exactly the small fixture files this test
        # wrote under the real (gitignored) storage/uploads/ directory --
        # not required for isolation (SQLite/Qdrant are already isolated
        # per-test), just hygiene. Looked up by the exact stored_filename
        # of each document this test created via env.upload() -- never a
        # directory sweep, so a real pre-existing dev upload is never at
        # risk even if this lookup or deletion fails.
        if environment.uploaded_document_ids:
            cleanup_db = db_sessionmaker()
            try:
                stored_filenames = [
                    doc.stored_filename
                    for doc_id in environment.uploaded_document_ids
                    if (doc := DocumentRepository(cleanup_db).get_by_id(doc_id)) is not None
                ]
            finally:
                cleanup_db.close()

            uploads_dir = Path("storage") / "uploads"
            for stored_filename in stored_filenames:
                (uploads_dir / stored_filename).unlink(missing_ok=True)

        app.dependency_overrides.clear()
        engine.dispose()


# --------------------------------------------------------------------------- #
# Workflow 1: document upload -> RBAC metadata -> retrieval
# --------------------------------------------------------------------------- #


def test_individual_document_upload_retrieve_authorization(env: _Env):
    """
    INDIVIDUAL: owner can retrieve; another same-org user cannot.

    Exercises: real upload (owner = team_member) -> real SQLite Document
    row -> real indexing (deviation 1) -> real retrieval (deviation 2)
    for both the owner and a different same-org user.
    """

    document_id = env.upload(
        "team_member",
        filename="individual.pdf",
        access_scope="individual",
    )

    assert document_id is not None

    owner_results = env.retrieve_chunk_uuids("team_member")
    other_results = env.retrieve_chunk_uuids("other_member")

    assert owner_results, "owner must retrieve their own INDIVIDUAL document"
    assert not (owner_results & other_results), (
        "a different same-org user must not retrieve another user's "
        "INDIVIDUAL document"
    )


def test_team_document_upload_retrieve_authorization(env: _Env):
    """
    TEAM: authorized team member can retrieve; same-org non-member
    cannot.
    """

    document_id = env.upload(
        "team_manager",
        filename="team.pdf",
        access_scope="team",
        team_id=env.team.id,
    )

    assert document_id is not None

    member_results = env.retrieve_chunk_uuids("team_member")
    non_member_results = env.retrieve_chunk_uuids("other_member")

    assert member_results, "an authorized team member must retrieve the TEAM document"
    assert not non_member_results, (
        "a same-org non-member must not retrieve the TEAM document"
    )


# --------------------------------------------------------------------------- #
# Workflows 2 & 3: jurisdiction grant -> retrieve, revoke -> retrieve removed
# --------------------------------------------------------------------------- #


def test_jurisdiction_grant_then_revoke_propagates_to_retrieval(env: _Env):
    """
    Full round trip: an Org Manager with no jurisdiction cannot retrieve
    a TEAM document; after a real ``POST .../managers/{user_id}`` grant
    (as ADMIN) they can; after a real ``DELETE .../managers/{user_id}``
    revoke, they cannot again.

    Proves: grant API -> SQLite -> AccessContext -> Qdrant authorization
    filter -> retrieval result, and the reverse for revoke -- with no
    step skipped or hand-constructed.
    """

    env.upload(
        "team_manager",
        filename="team-jurisdiction.pdf",
        access_scope="team",
        team_id=env.team.id,
    )

    org_manager_id = env.users["org_manager"].id
    team_id = env.team.id

    # 1. Before grant: DENY.
    before_grant = env.retrieve_chunk_uuids("org_manager")
    assert not before_grant, "Org Manager without jurisdiction must not retrieve"

    # 2. Real grant, as ADMIN.
    grant_response = env.grant_jurisdiction(
        admin="admin", team_id=team_id, user_id=org_manager_id,
    )
    assert grant_response.status_code == 201, grant_response.text

    # 3. After grant: ALLOW.
    after_grant = env.retrieve_chunk_uuids("org_manager")
    assert after_grant, "Org Manager with jurisdiction must retrieve"

    # 4. Real revoke, as ADMIN.
    revoke_response = env.revoke_jurisdiction(
        admin="admin", team_id=team_id, user_id=org_manager_id,
    )
    assert revoke_response.status_code == 204, revoke_response.text

    # 5. After revoke: DENY again.
    after_revoke = env.retrieve_chunk_uuids("org_manager")
    assert not after_revoke, "Org Manager must lose retrieval after revoke"


# --------------------------------------------------------------------------- #
# Workflows 4 & 5: membership add -> retrieve, remove -> retrieve removed
# --------------------------------------------------------------------------- #


def test_team_membership_add_then_remove_propagates_to_retrieval(env: _Env):
    """
    Full round trip: a non-member cannot retrieve a TEAM document;
    after a real ``POST .../members`` add (as that team's
    ``TeamRole.MANAGER``) they can; after a real
    ``DELETE .../members/{user_id}`` remove, they cannot again.
    """

    env.upload(
        "team_manager",
        filename="team-membership.pdf",
        access_scope="team",
        team_id=env.team.id,
    )

    other_member_id = env.users["other_member"].id
    team_id = env.team.id

    # 1. Before add: DENY.
    before_add = env.retrieve_chunk_uuids("other_member")
    assert not before_add, "non-member must not retrieve the TEAM document"

    # 2. Real add, as the team's TeamRole.MANAGER.
    add_response = env.add_member(
        manager="team_manager", team_id=team_id, user_id=other_member_id,
    )
    assert add_response.status_code == 201, add_response.text

    # 3. After add: ALLOW.
    after_add = env.retrieve_chunk_uuids("other_member")
    assert after_add, "newly added member must retrieve the TEAM document"

    # 4. Real remove, as the team's TeamRole.MANAGER.
    remove_response = env.remove_member(
        manager="team_manager", team_id=team_id, user_id=other_member_id,
    )
    assert remove_response.status_code == 204, remove_response.text

    # 5. After remove: DENY again.
    after_remove = env.retrieve_chunk_uuids("other_member")
    assert not after_remove, "removed member must lose retrieval"


# --------------------------------------------------------------------------- #
# RBAC-10B
# --------------------------------------------------------------------------- #
# Workflow 6: ORGANISATION upload -> retrieval ALLOW/DENY (incl. a real
# second organisation) -> deletion -> SQL + Qdrant cleanup.
# --------------------------------------------------------------------------- #


def test_organisation_document_upload_retrieve_cross_org_and_delete(env: _Env):
    """
    ORGANISATION: same-org ADMIN can retrieve; same-org MEMBER and
    same-org MANAGER (non-ADMIN) cannot; a *different organisation's*
    real ADMIN cannot either. The original ADMIN can then delete it,
    which removes both the SQL row and the Qdrant vector.

    Organisation B and its ADMIN exist only in the isolated in-memory
    SQLite database (``env.db_sessionmaker``), via the same module-level
    factories every other fixture actor in this file uses -- never the
    real dev database.
    """

    setup_db = env.db_sessionmaker()
    try:
        organisation_b = make_organisation(setup_db, slug=f"rbac10b-orgb-{uuid4().hex[:8]}")
        admin_b = make_user(
            setup_db, organisation_b, username=f"adminb_{uuid4().hex[:6]}", role=OrgRole.ADMIN,
        )
    finally:
        setup_db.close()

    env.users["admin_b"] = admin_b

    document_id = env.upload(
        "admin",
        filename="organisation.pdf",
        access_scope="organisation",
    )

    assert document_id is not None

    same_org_admin_results = env.retrieve_chunk_uuids("admin")
    same_org_member_results = env.retrieve_chunk_uuids("other_member")
    same_org_manager_results = env.retrieve_chunk_uuids("org_manager")
    other_org_admin_results = env.retrieve_chunk_uuids("admin_b")

    assert same_org_admin_results, "the same-org ADMIN must retrieve the ORGANISATION document"
    assert not same_org_member_results, "a same-org MEMBER must not retrieve the ORGANISATION document"
    assert not same_org_manager_results, "a same-org MANAGER (non-ADMIN) must not retrieve the ORGANISATION document"
    assert not other_org_admin_results, "a different organisation's ADMIN must not retrieve the ORGANISATION document"

    before_delete_count = env.dense_repository.count()
    assert before_delete_count > 0

    delete_response = env.delete_document("admin", document_id)
    assert delete_response.status_code == 204, delete_response.text

    db = env.db_sessionmaker()
    try:
        assert DocumentRepository(db).get_by_id(document_id) is None
    finally:
        db.close()

    assert env.dense_repository.count() == 0


# --------------------------------------------------------------------------- #
# Workflow 7: TEAM document deletion authorization (TeamRole.MANAGER vs
# MEMBER) -> SQL + Qdrant cleanup.
# --------------------------------------------------------------------------- #


def test_team_document_delete_authorization_and_cleanup(env: _Env):
    """
    A plain ``TeamRole.MEMBER`` (non-owner) cannot delete a TEAM
    document -- the real endpoint returns 404 (``DocumentNotFoundError``,
    enumeration-safe -- never 403). That team's own ``TeamRole.MANAGER``
    can, and doing so removes both the SQL row and the Qdrant vector.
    """

    document_id = env.upload(
        "team_manager",
        filename="team-delete.pdf",
        access_scope="team",
        team_id=env.team.id,
    )

    before_delete_count = env.dense_repository.count()
    assert before_delete_count > 0

    denied_response = env.delete_document("team_member", document_id)
    assert denied_response.status_code == 404, denied_response.text

    allowed_response = env.delete_document("team_manager", document_id)
    assert allowed_response.status_code == 204, allowed_response.text

    db = env.db_sessionmaker()
    try:
        assert DocumentRepository(db).get_by_id(document_id) is None
    finally:
        db.close()

    assert env.dense_repository.count() == 0


# --------------------------------------------------------------------------- #
# Workflow 8: INDIVIDUAL document deletion -> SQL + Qdrant cleanup ->
# retrieval removed.
# --------------------------------------------------------------------------- #


def test_individual_document_delete_removes_sql_and_qdrant(env: _Env):
    """
    The owner of an INDIVIDUAL document can delete it via the real
    ``DELETE`` endpoint; afterward the SQL row is gone, the Qdrant
    vector is gone, and the former owner's retrieval returns empty.
    """

    document_id = env.upload(
        "other_member",
        filename="individual-delete.pdf",
        access_scope="individual",
    )

    baseline_results = env.retrieve_chunk_uuids("other_member")
    assert baseline_results, "owner must retrieve their own document before deletion"

    delete_response = env.delete_document("other_member", document_id)
    assert delete_response.status_code == 204, delete_response.text

    db = env.db_sessionmaker()
    try:
        assert DocumentRepository(db).get_by_id(document_id) is None
    finally:
        db.close()

    assert env.dense_repository.count() == 0

    after_delete_results = env.retrieve_chunk_uuids("other_member")
    assert not after_delete_results, "retrieval must return empty after deletion"


# --------------------------------------------------------------------------- #
# Workflow 9: TEAM document uploader-leaves-team asymmetry -- retrieval
# is lost, delete authority is retained -> SQL + Qdrant cleanup.
# --------------------------------------------------------------------------- #


def test_team_document_uploader_retains_delete_after_leaving_team(env: _Env):
    """
    READ requires current team membership; DELETE does not, because the
    uploader remains the document's owner regardless of membership.

    This test proves the implemented asymmetry exactly as it exists --
    it is not "fixed" here, and production authorization logic is not
    touched.
    """

    document_id = env.upload(
        "team_member",
        filename="team-leave.pdf",
        access_scope="team",
        team_id=env.team.id,
    )

    # 1. Before leaving: READ allowed.
    before_leave_results = env.retrieve_chunk_uuids("team_member")
    assert before_leave_results, "uploader must retrieve their TEAM document while still a member"

    # 2. Real membership removal, performed by the team's own
    #    TeamRole.MANAGER (there is no self-service "leave" endpoint).
    team_member_id = env.users["team_member"].id
    remove_response = env.remove_member(
        manager="team_manager", team_id=env.team.id, user_id=team_member_id,
    )
    assert remove_response.status_code == 204, remove_response.text

    # 3. After leaving: READ denied.
    after_leave_results = env.retrieve_chunk_uuids("team_member")
    assert not after_leave_results, "ex-member must lose retrieval after leaving the team"

    # 4. After leaving: DELETE still allowed (owner authority retained).
    delete_response = env.delete_document("team_member", document_id)
    assert delete_response.status_code == 204, delete_response.text

    db = env.db_sessionmaker()
    try:
        assert DocumentRepository(db).get_by_id(document_id) is None
    finally:
        db.close()

    assert env.dense_repository.count() == 0
