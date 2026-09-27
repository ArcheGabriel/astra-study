"""
RBAC-6: real Qdrant round-trip validation for the complete RBAC-5C..5J
authorization chain.

Exercises the actual production authorization path end to end:

    AccessContext
        -> DenseRepository.hybrid_search(...)
        -> DenseRepository._authorization_filter(access)   [real method]
        -> self.client.query_points(...)                   [real Qdrant server]
        -> actual stored payloads, built via HybridMapper.build_payload
           (the real production payload constructor)

No shadow authorization logic is introduced anywhere in this file: every
ALLOW/DENY assertion below is the direct, unmodified result of a real
Qdrant query executed by real production code.

Isolation: this file lives under ``tests/integration/``, so
``tests/conftest.py`` forces ``DenseRepository.COLLECTION_NAME`` (and
``settings.QDRANT_COLLECTION_NAME``) to the dedicated ``astra_study_test``
collection *before* this module is even imported, and raises immediately
if anything else is requested. The production ``astra_study`` collection
is never named, referenced, or constructed anywhere in this file. The
fixture below additionally performs its own create/drop of the isolated
collection (on top of the session-level cleanup already provided by
``tests/conftest.py``), asserting the collection name at every step, so
cleanup does not depend solely on the session-level safety net.

Vector *content* is irrelevant to authorization correctness -- only
payload fields participate in ``_authorization_filter``. Dense/sparse
query and stored vectors are therefore small, deterministic, non-semantic
values (no OpenAI/FastEmbed calls), keeping this test fast and free of
external API dependencies while still performing a genuine Qdrant
``query_points`` round-trip.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from qdrant_client.models import PointStruct, SparseVector

from app.chunking.models import ChunkMetadata, DocumentChunk
from app.config.settings import settings
from app.embeddings.models import EmbeddedChunk, EmbeddingMetadata, EmbeddingVector
from app.enums.document import DocumentAccessScope
from app.enums.organisation import OrgRole
from app.retrieval.access import AccessContext
from app.search.dense.repository import DenseRepository
from app.search.hybrid.mapper import HybridMapper
from tests.conftest import DEDICATED_TEST_COLLECTION, PRODUCTION_COLLECTION

# A single, fixed-length, non-semantic dense vector -- correct dimensionality
# for the real collection config, no embedding model involved.
_DENSE_VECTOR = [0.0] * settings.EMBEDDING_DIMENSIONS
_SPARSE_INDICES = [0]
_SPARSE_VALUES = [1.0]

# Arbitrary, mutually-distinct organisation/team/user ids. Qdrant has no FK
# relationship to SQLite, so these need only be internally consistent --
# they never touch the real SQLite database.
ORG_A = 9001
ORG_B = 9002
TEAM_X = 9101  # in ORG_A
TEAM_Y = 9102  # in ORG_A
TEAM_X_NUMERIC_COLLISION_ORG_B = 9101  # same numeric id as TEAM_X, but in ORG_B

OWNER_A = 9201
OTHER_USER_A = 9202


def _embedded(metadata: ChunkMetadata) -> EmbeddedChunk:
    """Minimal real EmbeddedChunk -- same construction pattern already
    established in tests/unit/test_rbac_5c_payload.py::_embedded."""

    return EmbeddedChunk(
        DocumentChunk("chunk text", 0, metadata),
        EmbeddingVector([0.1, 0.2]),
        EmbeddingMetadata("test-model", 2),
    )


def _make_point(
    *,
    organisation_id: int,
    access_scope: DocumentAccessScope,
    user_id: int = OWNER_A,
    team_id: int | None = None,
    is_reference: bool = False,
    is_appendix: bool = False,
) -> PointStruct:
    """
    Build one real Qdrant point via the actual production payload
    constructor (``HybridMapper.build_payload``) -- never a hand-rolled
    payload shadowing the real schema.
    """

    chunk_uuid = uuid4()
    document_uuid = uuid4()

    metadata = ChunkMetadata(
        document_id=None,
        document_uuid=document_uuid,
        chunk_uuid=chunk_uuid,
        user_id=user_id,
        organisation_id=organisation_id,
        team_id=team_id,
        access_scope=access_scope,
        is_reference=is_reference,
        is_appendix=is_appendix,
    )

    payload = HybridMapper.build_payload(_embedded(metadata))

    return PointStruct(
        id=str(chunk_uuid),
        vector={
            settings.QDRANT_VECTOR_NAME: _DENSE_VECTOR,
            settings.QDRANT_SPARSE_VECTOR_NAME: SparseVector(
                indices=_SPARSE_INDICES,
                values=_SPARSE_VALUES,
            ),
        },
        payload=payload,
    )


def _access(
    *,
    user_id: int,
    organisation_id: int,
    team_ids: tuple[int, ...] = (),
    jurisdiction_team_ids: tuple[int, ...] = (),
    role: OrgRole = OrgRole.MEMBER,
) -> AccessContext:
    return AccessContext(
        user_id=user_id,
        organisation_id=organisation_id,
        team_ids=team_ids,
        jurisdiction_team_ids=jurisdiction_team_ids,
        role=role,
    )


@pytest.fixture()
def qdrant_repo():
    """
    Create the isolated test collection fresh, yield a real
    ``DenseRepository``, and guarantee cleanup afterward -- even if the
    test body raises.

    Every step re-asserts the collection name is the dedicated test
    collection, never production, as an additional guard on top of
    ``tests/conftest.py``'s session-level enforcement.
    """

    repository = DenseRepository()

    assert repository.COLLECTION_NAME == DEDICATED_TEST_COLLECTION
    assert repository.COLLECTION_NAME != PRODUCTION_COLLECTION

    if repository.collection_exists():
        repository.delete_collection()

    repository.create_collection()

    try:
        yield repository
    finally:
        assert repository.COLLECTION_NAME == DEDICATED_TEST_COLLECTION
        assert repository.COLLECTION_NAME != PRODUCTION_COLLECTION
        if repository.collection_exists():
            repository.delete_collection()


def _search_chunk_uuids(repository: DenseRepository, access: AccessContext) -> set[str]:
    """
    Perform a REAL Qdrant hybrid_search call -- the exact production
    method that builds and applies ``_authorization_filter`` -- and
    return the set of chunk_uuids Qdrant actually returned.

    limit=50 comfortably exceeds the total number of points seeded by
    this test module, so a missing chunk_uuid means the authorization
    filter genuinely excluded it, not that it was pushed out by ranking.
    """

    results = repository.hybrid_search(
        dense_vector=_DENSE_VECTOR,
        sparse_indices=_SPARSE_INDICES,
        sparse_values=_SPARSE_VALUES,
        access=access,
        limit=50,
    )
    return {str(r.chunk_uuid) for r in results}


@pytest.fixture()
def seeded_points(qdrant_repo: DenseRepository):
    """
    Seed every fixture document needed by the full RBAC-6 matrix into the
    isolated collection, via the real ``HybridMapper.build_payload`` path,
    and return their chunk_uuids (as strings) keyed by scenario name.
    """

    points = {
        "team_x": _make_point(
            organisation_id=ORG_A, access_scope=DocumentAccessScope.TEAM, team_id=TEAM_X,
        ),
        "team_y": _make_point(
            organisation_id=ORG_A, access_scope=DocumentAccessScope.TEAM, team_id=TEAM_Y,
        ),
        "team_x_org_b": _make_point(
            organisation_id=ORG_B,
            access_scope=DocumentAccessScope.TEAM,
            team_id=TEAM_X_NUMERIC_COLLISION_ORG_B,
        ),
        "individual_owner_a": _make_point(
            organisation_id=ORG_A, access_scope=DocumentAccessScope.INDIVIDUAL, user_id=OWNER_A,
        ),
        "individual_other_a": _make_point(
            organisation_id=ORG_A, access_scope=DocumentAccessScope.INDIVIDUAL, user_id=OTHER_USER_A,
        ),
        "organisation_a": _make_point(
            organisation_id=ORG_A, access_scope=DocumentAccessScope.ORGANISATION,
        ),
        "organisation_b": _make_point(
            organisation_id=ORG_B, access_scope=DocumentAccessScope.ORGANISATION,
        ),
        "team_x_is_reference": _make_point(
            organisation_id=ORG_A,
            access_scope=DocumentAccessScope.TEAM,
            team_id=TEAM_X,
            is_reference=True,
        ),
        "team_x_is_appendix": _make_point(
            organisation_id=ORG_A,
            access_scope=DocumentAccessScope.TEAM,
            team_id=TEAM_X,
            is_appendix=True,
        ),
    }

    qdrant_repo.upsert(list(points.values()))

    ids = {name: point.id for name, point in points.items()}

    verified_count = qdrant_repo.count()
    assert verified_count == len(points), (
        f"expected {len(points)} points in the isolated collection, found {verified_count}"
    )

    return ids


# --------------------------------------------------------------------------- #
# 1-2: Team membership (MEMBER / MANAGER read visibility is identical --
# TeamRole never affects Qdrant read filtering, only TeamMembership.role
# matters for SQL delete authorization elsewhere)
# --------------------------------------------------------------------------- #


def test_team_member_sees_own_team_document(qdrant_repo, seeded_points):
    access = _access(user_id=1, organisation_id=ORG_A, team_ids=(TEAM_X,))
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] in found


def test_team_member_does_not_see_another_teams_document(qdrant_repo, seeded_points):
    access = _access(user_id=1, organisation_id=ORG_A, team_ids=(TEAM_X,))
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_y"] not in found


def test_team_manager_sees_own_team_document(qdrant_repo, seeded_points):
    """TeamRole.MANAGER read visibility for Qdrant is identical to plain
    membership -- team_ids alone drives this branch."""

    access = _access(user_id=2, organisation_id=ORG_A, team_ids=(TEAM_X,))
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] in found


# --------------------------------------------------------------------------- #
# 4-7, 21: Org Manager jurisdiction
# --------------------------------------------------------------------------- #


def test_org_manager_with_jurisdiction_sees_team_document(qdrant_repo, seeded_points):
    access = _access(
        user_id=3, organisation_id=ORG_A, role=OrgRole.MANAGER, jurisdiction_team_ids=(TEAM_X,),
    )
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] in found


def test_org_manager_without_jurisdiction_denied(qdrant_repo, seeded_points):
    access = _access(user_id=3, organisation_id=ORG_A, role=OrgRole.MANAGER)
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] not in found


def test_org_manager_with_unrelated_jurisdiction_denied(qdrant_repo, seeded_points):
    """Jurisdiction over TEAM_Y must not grant visibility into TEAM_X."""

    access = _access(
        user_id=3, organisation_id=ORG_A, role=OrgRole.MANAGER, jurisdiction_team_ids=(TEAM_Y,),
    )
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] not in found
    # 21. Different team ids: same actor correctly sees the team they DO
    # hold jurisdiction over.
    assert seeded_points["team_y"] in found


def test_org_manager_jurisdiction_without_team_membership_still_allowed(qdrant_repo, seeded_points):
    """Jurisdiction is intentionally independent of TeamMembership --
    team_ids is empty here, only jurisdiction_team_ids grants access."""

    access = _access(
        user_id=3,
        organisation_id=ORG_A,
        role=OrgRole.MANAGER,
        team_ids=(),
        jurisdiction_team_ids=(TEAM_X,),
    )
    assert access.team_ids == ()
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] in found


# --------------------------------------------------------------------------- #
# 8-9: ADMIN
# --------------------------------------------------------------------------- #


def test_admin_same_organisation_sees_team_document(qdrant_repo, seeded_points):
    access = _access(user_id=4, organisation_id=ORG_A, role=OrgRole.ADMIN)
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] in found


def test_admin_different_organisation_denied(qdrant_repo, seeded_points):
    access = _access(user_id=4, organisation_id=ORG_A, role=OrgRole.ADMIN)
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x_org_b"] not in found


# --------------------------------------------------------------------------- #
# 10-11: unrelated / cross-org
# --------------------------------------------------------------------------- #


def test_same_org_unrelated_member_denied(qdrant_repo, seeded_points):
    access = _access(user_id=5, organisation_id=ORG_A, role=OrgRole.MEMBER)
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] not in found


def test_cross_org_team_member_denied(qdrant_repo, seeded_points):
    """A numerically colliding team_id in a different organisation must
    never match -- team_x_org_b shares TEAM_X's numeric id but belongs to
    ORG_B; a member of TEAM_X in ORG_A must not see it."""

    access = _access(user_id=1, organisation_id=ORG_A, team_ids=(TEAM_X,))
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x_org_b"] not in found


# --------------------------------------------------------------------------- #
# 12-13: INDIVIDUAL
# --------------------------------------------------------------------------- #


def test_individual_owner_sees_own_document(qdrant_repo, seeded_points):
    access = _access(user_id=OWNER_A, organisation_id=ORG_A)
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["individual_owner_a"] in found


def test_individual_non_owner_denied(qdrant_repo, seeded_points):
    access = _access(user_id=OWNER_A, organisation_id=ORG_A)
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["individual_other_a"] not in found


# --------------------------------------------------------------------------- #
# 14-16: ORGANISATION
# --------------------------------------------------------------------------- #


def test_organisation_admin_same_org_sees_document(qdrant_repo, seeded_points):
    access = _access(user_id=4, organisation_id=ORG_A, role=OrgRole.ADMIN)
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["organisation_a"] in found


def test_organisation_member_denied(qdrant_repo, seeded_points):
    access = _access(user_id=5, organisation_id=ORG_A, role=OrgRole.MEMBER)
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["organisation_a"] not in found


def test_organisation_cross_org_admin_denied(qdrant_repo, seeded_points):
    access = _access(user_id=4, organisation_id=ORG_A, role=OrgRole.ADMIN)
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["organisation_b"] not in found


# --------------------------------------------------------------------------- #
# 17-18: structural exclusions
# --------------------------------------------------------------------------- #


def test_is_reference_excluded_even_for_authorized_team(qdrant_repo, seeded_points):
    access = _access(user_id=1, organisation_id=ORG_A, team_ids=(TEAM_X,))
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x_is_reference"] not in found
    # Sanity: the same actor DOES see the non-reference TEAM_X document.
    assert seeded_points["team_x"] in found


def test_is_appendix_excluded_even_for_authorized_team(qdrant_repo, seeded_points):
    access = _access(user_id=1, organisation_id=ORG_A, team_ids=(TEAM_X,))
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x_is_appendix"] not in found


# --------------------------------------------------------------------------- #
# 19-20: empty tuples
# --------------------------------------------------------------------------- #


def test_empty_team_ids_denies_team_document(qdrant_repo, seeded_points):
    access = _access(user_id=6, organisation_id=ORG_A, role=OrgRole.MEMBER, team_ids=())
    assert access.team_ids == ()
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] not in found


def test_empty_jurisdiction_team_ids_denies_team_document(qdrant_repo, seeded_points):
    access = _access(
        user_id=3, organisation_id=ORG_A, role=OrgRole.MANAGER, jurisdiction_team_ids=(),
    )
    assert access.jurisdiction_team_ids == ()
    found = _search_chunk_uuids(qdrant_repo, access)
    assert seeded_points["team_x"] not in found


# --------------------------------------------------------------------------- #
# Multi-document filtering proof: one query, one actor, several documents in
# the SAME collection -- proves actual filtering, not merely a query that
# happens to succeed.
# --------------------------------------------------------------------------- #


def test_single_query_returns_exactly_the_authorized_subset(qdrant_repo, seeded_points):
    """A Team MEMBER of TEAM_X, querying the full 9-document isolated
    collection in one call, must receive exactly {own INDIVIDUAL doc,
    TEAM_X doc} and nothing else -- proving real Qdrant-side filtering
    across multiple stored points, not an artifact of a single-document
    collection."""

    access = _access(user_id=OWNER_A, organisation_id=ORG_A, team_ids=(TEAM_X,))
    found = _search_chunk_uuids(qdrant_repo, access)

    expected = {seeded_points["team_x"], seeded_points["individual_owner_a"]}
    assert found == expected, f"expected exactly {expected}, got {found}"
