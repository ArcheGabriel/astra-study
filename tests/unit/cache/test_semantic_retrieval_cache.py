"""
Executable specification for ``app.cache.semantic.SemanticRetrievalCache``
(RBAC/C.3 -- the retrieval-level semantic cache).

Covers the cache component in isolation: no Qdrant, no OpenAI, no
RetrievalService. Behavioral, not implementation-detail tests -- each
test exercises lookup()/store()/invalidate_*() through their public
contract, matching this project's existing hand-rolled-fixture
convention (no mocking framework for the data itself).
"""

from __future__ import annotations

import time

import pytest

from app.cache.models import Namespace
from app.cache.semantic import SemanticRetrievalCache, build_namespace
from app.config.settings import settings
from app.enums.organisation import OrgRole
from app.retrieval.access import AccessContext
from app.retrieval.models import RetrievalResult, RetrievedContext
from uuid import uuid4


def _namespace(
    *,
    user_id: int = 1,
    organisation_id: int = 9,
    role: str = "member",
    team_ids: tuple[int, ...] = (),
    jurisdiction_team_ids: tuple[int, ...] = (),
) -> Namespace:
    return (user_id, organisation_id, role, team_ids, jurisdiction_team_ids)


def _result(query: str = "q") -> RetrievalResult:
    return RetrievalResult(
        query=query,
        contexts=[
            RetrievedContext(
                text="Some retrieved text.",
                source="doc.pdf",
                chunk_uuid=uuid4(),
                retrieval_score=0.9,
                reranker_score=0.95,
            ),
        ],
        retrieval_latency=0.01,
    )


def _vector(*values: float) -> list[float]:
    return list(values)


# --------------------------------------------------------------------------- #
# 1. empty cache -> miss
# --------------------------------------------------------------------------- #


def test_empty_cache_is_a_miss():
    cache = SemanticRetrievalCache()

    hit = cache.lookup(namespace=_namespace(), query_embedding=_vector(1.0, 0.0))

    assert hit is None


# --------------------------------------------------------------------------- #
# 2. exact semantic match -> hit
# --------------------------------------------------------------------------- #


def test_exact_embedding_match_is_a_hit():
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    result = _result()

    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 0.0, 0.0),
        retrieval_result=result,
    )

    hit = cache.lookup(namespace=_namespace(), query_embedding=_vector(1.0, 0.0, 0.0))

    assert hit is not None
    assert hit.retrieval_result is result
    assert hit.similarity_score == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# 3. near semantic match above threshold -> hit
# --------------------------------------------------------------------------- #


def test_near_match_above_threshold_is_a_hit():
    cache = SemanticRetrievalCache(similarity_threshold=0.90)
    result = _result()

    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=result,
    )

    # Slightly off-axis vector -- cosine similarity is high but not 1.0.
    hit = cache.lookup(namespace=_namespace(), query_embedding=_vector(0.99, 0.14))

    assert hit is not None
    assert hit.similarity_score >= 0.90


# --------------------------------------------------------------------------- #
# 4. similarity below threshold -> miss
# --------------------------------------------------------------------------- #


def test_similarity_below_threshold_is_a_miss():
    cache = SemanticRetrievalCache(similarity_threshold=0.97)

    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result(),
    )

    # Orthogonal vector -- similarity 0.0, well below threshold.
    hit = cache.lookup(namespace=_namespace(), query_embedding=_vector(0.0, 1.0))

    assert hit is None


# --------------------------------------------------------------------------- #
# 5. TTL expiration -> miss
# --------------------------------------------------------------------------- #


def test_ttl_expiry_is_a_miss():
    cache = SemanticRetrievalCache(similarity_threshold=0.97, ttl_seconds=0.01)

    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result(),
    )

    time.sleep(0.02)

    hit = cache.lookup(namespace=_namespace(), query_embedding=_vector(1.0, 0.0))

    assert hit is None


# --------------------------------------------------------------------------- #
# 6. maximum cache size / eviction
# --------------------------------------------------------------------------- #


def test_bounded_size_evicts_oldest_entry_first():
    cache = SemanticRetrievalCache(similarity_threshold=0.97, max_size=2)

    cache.store(
        namespace=_namespace(user_id=1),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result("first"),
    )
    cache.store(
        namespace=_namespace(user_id=2),
        query_embedding=_vector(0.0, 1.0),
        retrieval_result=_result("second"),
    )

    assert len(cache) == 2

    # A third store exceeds max_size=2 -- the oldest (user_id=1) entry
    # must be evicted first (FIFO).
    cache.store(
        namespace=_namespace(user_id=3),
        query_embedding=_vector(1.0, 1.0),
        retrieval_result=_result("third"),
    )

    assert len(cache) == 2
    assert cache.lookup(namespace=_namespace(user_id=1), query_embedding=_vector(1.0, 0.0)) is None
    assert cache.lookup(namespace=_namespace(user_id=2), query_embedding=_vector(0.0, 1.0)) is not None


# --------------------------------------------------------------------------- #
# 7. malformed cache entry does not break retrieval
# --------------------------------------------------------------------------- #


def test_malformed_entry_is_skipped_not_raised():
    cache = SemanticRetrievalCache(similarity_threshold=0.5)

    # A well-formed entry.
    cache.store(
        namespace=_namespace(user_id=1),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result("good"),
    )

    # Directly corrupt internal state to simulate a malformed entry
    # (mismatched embedding dimensionality) -- lookup must skip it, not
    # raise, and still find the well-formed entry.
    from dataclasses import replace

    bad_key = next(iter(cache._entries))
    cache._entries[bad_key] = replace(
        cache._entries[bad_key],
        query_embedding=(1.0,),  # wrong dimensionality vs. the 2D query below
    )
    cache.store(
        namespace=_namespace(user_id=2),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result("also-good"),
    )

    hit = cache.lookup(namespace=_namespace(user_id=2), query_embedding=_vector(1.0, 0.0))

    assert hit is not None
    assert hit.retrieval_result.query == "also-good"


# --------------------------------------------------------------------------- #
# 8 / 9. cache lookup/insertion failure fails open (exercised at the
# RetrievalService integration layer -- see
# tests/unit/retrieval/test_semantic_cache_integration.py)
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# 10. explicit invalidation removes affected entries
# --------------------------------------------------------------------------- #


def test_invalidate_user_removes_only_that_users_entries():
    cache = SemanticRetrievalCache(similarity_threshold=0.5)

    cache.store(
        namespace=_namespace(user_id=1),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result("user-1"),
    )
    cache.store(
        namespace=_namespace(user_id=2),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result("user-2"),
    )

    removed = cache.invalidate_user(1)

    assert removed == 1
    assert cache.lookup(namespace=_namespace(user_id=1), query_embedding=_vector(1.0, 0.0)) is None
    assert cache.lookup(namespace=_namespace(user_id=2), query_embedding=_vector(1.0, 0.0)) is not None


def test_invalidate_organisation_removes_only_that_organisations_entries():
    cache = SemanticRetrievalCache(similarity_threshold=0.5)

    cache.store(
        namespace=_namespace(user_id=1, organisation_id=9),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result("org-9"),
    )
    cache.store(
        namespace=_namespace(user_id=2, organisation_id=10),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result("org-10"),
    )

    removed = cache.invalidate_organisation(9)

    assert removed == 1
    assert cache.lookup(namespace=_namespace(user_id=1, organisation_id=9), query_embedding=_vector(1.0, 0.0)) is None
    assert cache.lookup(namespace=_namespace(user_id=2, organisation_id=10), query_embedding=_vector(1.0, 0.0)) is not None


# --------------------------------------------------------------------------- #
# 11. clear-all invalidation
# --------------------------------------------------------------------------- #


def test_clear_removes_every_entry():
    cache = SemanticRetrievalCache(similarity_threshold=0.5)

    cache.store(
        namespace=_namespace(user_id=1),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result(),
    )
    cache.store(
        namespace=_namespace(user_id=2),
        query_embedding=_vector(0.0, 1.0),
        retrieval_result=_result(),
    )

    cache.clear()

    assert len(cache) == 0


# --------------------------------------------------------------------------- #
# build_namespace -- mirrors AccessContext fields exactly
# --------------------------------------------------------------------------- #


def test_build_namespace_reflects_every_access_context_field():
    access = AccessContext(
        user_id=7,
        organisation_id=3,
        team_ids=(1, 2),
        jurisdiction_team_ids=(5,),
        role=OrgRole.MANAGER,
    )

    namespace = build_namespace(access)

    assert namespace == (7, 3, "manager", (1, 2), (5,))


def test_different_namespace_is_never_matched_regardless_of_similarity():
    cache = SemanticRetrievalCache(similarity_threshold=0.0)

    cache.store(
        namespace=_namespace(user_id=1),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result(),
    )

    # Identical vector, different namespace -- must never hit, even with
    # a threshold of 0.0 (which would otherwise match anything).
    hit = cache.lookup(namespace=_namespace(user_id=2), query_embedding=_vector(1.0, 0.0))

    assert hit is None


# --------------------------------------------------------------------------- #
# Default TTL (RBAC/C.3 follow-up): the configured application default,
# not an arbitrary test value -- tests the actual setting, not a
# subjective product preference about what it "should" be.
# --------------------------------------------------------------------------- #


def test_default_ttl_matches_the_configured_application_setting():
    cache = SemanticRetrievalCache()

    assert cache.ttl_seconds == settings.SEMANTIC_CACHE_TTL_SECONDS


def test_entry_younger_than_ttl_remains_eligible():
    cache = SemanticRetrievalCache(similarity_threshold=0.97, ttl_seconds=3600.0)

    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result(),
    )

    hit = cache.lookup(namespace=_namespace(), query_embedding=_vector(1.0, 0.0))

    assert hit is not None


# --------------------------------------------------------------------------- #
# diagnose_miss (RBAC/C.3 follow-up: cache-miss-reason observability).
# A second, read-only pass used only for LangSmith metadata -- never on
# the hot lookup() path itself.
# --------------------------------------------------------------------------- #


def test_diagnose_miss_reports_empty_for_a_completely_empty_cache():
    cache = SemanticRetrievalCache()

    reason, score = cache.diagnose_miss(namespace=_namespace(), query_embedding=_vector(1.0, 0.0))

    assert reason == "empty"
    assert score is None


def test_diagnose_miss_reports_namespace_mismatch():
    cache = SemanticRetrievalCache(similarity_threshold=0.0)

    cache.store(
        namespace=_namespace(user_id=1),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result(),
    )

    reason, score = cache.diagnose_miss(
        namespace=_namespace(user_id=2),
        query_embedding=_vector(1.0, 0.0),
    )

    assert reason == "namespace_mismatch"
    assert score is None


def test_diagnose_miss_reports_expired():
    cache = SemanticRetrievalCache(similarity_threshold=0.0, ttl_seconds=0.01)

    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result(),
    )

    time.sleep(0.02)

    reason, score = cache.diagnose_miss(namespace=_namespace(), query_embedding=_vector(1.0, 0.0))

    assert reason == "expired"
    assert score is None


def test_diagnose_miss_reports_below_threshold():
    cache = SemanticRetrievalCache(similarity_threshold=0.97, ttl_seconds=3600.0)

    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result(),
    )

    # Orthogonal vector -- a real, non-expired, same-namespace entry
    # exists, but its similarity (0.0) is below the 0.97 threshold.
    reason, score = cache.diagnose_miss(namespace=_namespace(), query_embedding=_vector(0.0, 1.0))

    assert reason == "below_threshold"
    assert score == pytest.approx(0.0)


def test_diagnose_miss_below_threshold_reports_the_best_of_several_entries():
    cache = SemanticRetrievalCache(similarity_threshold=0.97, ttl_seconds=3600.0)

    # Three same-namespace entries at increasing similarity to the query
    # vector (1.0, 1.0) -- none meets the 0.97 threshold, but the best
    # (not an arbitrary one) must be the reported score.
    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result("low"),
    )
    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(0.0, 1.0),
        retrieval_result=_result("also-low"),
    )
    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(0.9, 1.0),
        retrieval_result=_result("closest"),
    )

    reason, score = cache.diagnose_miss(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 1.0),
    )

    assert reason == "below_threshold"
    # cosine((1,1), (0.9,1)) is the largest of the three candidate scores.
    import math

    expected_best = (1.0 * 0.9 + 1.0 * 1.0) / (math.sqrt(2) * math.sqrt(0.9**2 + 1.0**2))
    assert score == pytest.approx(expected_best)


def test_diagnose_miss_expired_entry_never_contributes_a_score():
    cache = SemanticRetrievalCache(similarity_threshold=0.97, ttl_seconds=0.01)

    # Exact-match entry, but it will be expired by the time we diagnose.
    cache.store(
        namespace=_namespace(),
        query_embedding=_vector(1.0, 0.0),
        retrieval_result=_result(),
    )

    time.sleep(0.02)

    reason, score = cache.diagnose_miss(namespace=_namespace(), query_embedding=_vector(1.0, 0.0))

    assert reason == "expired"
    assert score is None
