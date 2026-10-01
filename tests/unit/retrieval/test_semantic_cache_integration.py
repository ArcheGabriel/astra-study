"""
Executable specification for the semantic retrieval cache's integration
into ``RetrievalService`` (RBAC/C.3): RBAC isolation, cache-hit/-miss
retrieval behavior, embedding reuse, and fail-open behavior. Mirrors
``tests/unit/retrieval/test_service.py``'s hand-rolled ``MagicMock``
convention for ``HybridService``/``RerankingService``.
"""

from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.cache.semantic import SemanticRetrievalCache
from app.config.settings import settings
from app.enums.organisation import OrgRole
from app.retrieval.access import AccessContext
from app.retrieval.service import RetrievalService
from app.reranking.models import RerankedChunk, RerankingResult
from app.search.hybrid.models import HybridSearchResult


def _access(
    *,
    user_id: int = 1,
    organisation_id: int = 9,
    role: OrgRole = OrgRole.MEMBER,
    team_ids: tuple[int, ...] = (),
    jurisdiction_team_ids: tuple[int, ...] = (),
) -> AccessContext:
    return AccessContext(
        user_id=user_id,
        organisation_id=organisation_id,
        team_ids=team_ids,
        jurisdiction_team_ids=jurisdiction_team_ids,
        role=role,
    )


def _hybrid_result() -> HybridSearchResult:
    return HybridSearchResult(
        chunk_uuid=uuid4(),
        document_uuid=uuid4(),
        score=0.9,
        text="Retrieved chunk text.",
        payload={"document_name": "doc.pdf", "page_start": 1, "section_title": "Intro"},
    )


def _reranking_result(hybrid: HybridSearchResult) -> RerankingResult:
    return RerankingResult(
        query="q",
        total_candidates=1,
        returned_candidates=1,
        results=[RerankedChunk(result=hybrid, reranker_score=0.95, rank=1)],
    )


def make_service(
    *,
    semantic_cache: SemanticRetrievalCache | None = None,
    embedding: list[float] | None = None,
):
    hybrid_service = MagicMock()
    reranking_service = MagicMock()

    embedder = MagicMock()
    embedder.embed_query.return_value = embedding or [1.0, 0.0, 0.0]

    hybrid = _hybrid_result()
    hybrid_service.return_value = [hybrid]
    reranking_service.return_value = _reranking_result(hybrid)

    service = RetrievalService(
        hybrid_service=hybrid_service,
        reranking_service=reranking_service,
        embedder=embedder,
        semantic_cache=semantic_cache if semantic_cache is not None else SemanticRetrievalCache(),
    )

    return service, hybrid_service, reranking_service, embedder


# --------------------------------------------------------------------------- #
# 23/24/25. cache miss executes normal retrieval; cache hit skips it;
# cache hit returns an equivalent RetrievalResult.
# --------------------------------------------------------------------------- #


def test_cache_miss_executes_normal_retrieval():
    service, hybrid_service, reranking_service, _ = make_service()

    result = service.retrieve(query="q", access=_access())

    hybrid_service.assert_called_once()
    reranking_service.assert_called_once()
    assert len(result.contexts) == 1


def test_cache_hit_skips_hybrid_and_reranking():
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    service, hybrid_service, reranking_service, embedder = make_service(semantic_cache=cache)

    first = service.retrieve(query="q", access=_access())
    assert hybrid_service.call_count == 1
    assert reranking_service.call_count == 1

    second = service.retrieve(query="q", access=_access())

    # Identical embedding (same mocked value) -> guaranteed cache hit.
    # Hybrid/reranking must NOT have been called a second time.
    assert hybrid_service.call_count == 1
    assert reranking_service.call_count == 1
    assert second.contexts == first.contexts


# --------------------------------------------------------------------------- #
# "existing embedding is reused" / "no second embedding call occurs"
# --------------------------------------------------------------------------- #


def test_embedding_is_computed_exactly_once_per_retrieve_call():
    service, _, _, embedder = make_service()

    service.retrieve(query="q", access=_access())

    embedder.embed_query.assert_called_once_with("q")


def test_hybrid_service_receives_the_already_computed_dense_vector():
    service, hybrid_service, _, embedder = make_service(embedding=[0.3, 0.4, 0.5])

    service.retrieve(query="q", access=_access())

    assert hybrid_service.call_args.kwargs["dense_vector"] == [0.3, 0.4, 0.5]
    # Only the one embed_query call from RetrievalService itself -- never
    # a second one inside HybridService (which is mocked here, so this
    # also proves HybridService.search's own embed_query was never
    # reached for real).
    embedder.embed_query.assert_called_once()


# --------------------------------------------------------------------------- #
# 12-19. RBAC isolation
# --------------------------------------------------------------------------- #


def test_same_authorization_context_reuses_cache():
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    service, hybrid_service, _, _ = make_service(semantic_cache=cache)

    access = _access(user_id=1, organisation_id=9)
    service.retrieve(query="q", access=access)
    service.retrieve(query="q", access=access)

    assert hybrid_service.call_count == 1


def test_different_user_cannot_reuse_another_users_cached_result():
    cache = SemanticRetrievalCache(similarity_threshold=0.0)  # maximally permissive on similarity
    service, hybrid_service, _, _ = make_service(semantic_cache=cache)

    service.retrieve(query="q", access=_access(user_id=1))
    service.retrieve(query="q", access=_access(user_id=2))

    # Even with similarity_threshold=0.0 (anything "matches"), a
    # different user_id must never reuse user 1's cached result.
    assert hybrid_service.call_count == 2


def test_different_organisation_cannot_reuse_cached_result():
    cache = SemanticRetrievalCache(similarity_threshold=0.0)
    service, hybrid_service, _, _ = make_service(semantic_cache=cache)

    service.retrieve(query="q", access=_access(user_id=1, organisation_id=9))
    service.retrieve(query="q", access=_access(user_id=1, organisation_id=10))

    assert hybrid_service.call_count == 2


def test_different_team_membership_cannot_reuse_cached_result():
    cache = SemanticRetrievalCache(similarity_threshold=0.0)
    service, hybrid_service, _, _ = make_service(semantic_cache=cache)

    service.retrieve(query="q", access=_access(user_id=1, team_ids=(1,)))
    service.retrieve(query="q", access=_access(user_id=1, team_ids=(2,)))

    assert hybrid_service.call_count == 2


def test_different_jurisdiction_cannot_reuse_cached_result():
    cache = SemanticRetrievalCache(similarity_threshold=0.0)
    service, hybrid_service, _, _ = make_service(semantic_cache=cache)

    service.retrieve(
        query="q",
        access=_access(user_id=1, role=OrgRole.MANAGER, jurisdiction_team_ids=(1,)),
    )
    service.retrieve(
        query="q",
        access=_access(user_id=1, role=OrgRole.MANAGER, jurisdiction_team_ids=(2,)),
    )

    assert hybrid_service.call_count == 2


def test_role_change_is_a_different_namespace_and_therefore_a_miss():
    """
    A role promotion changes AccessContext.role on the very next request
    (get_access_context rebuilds it fresh) -- this proves the cache
    namespace reflects that immediately: the "old role" cached entry is
    simply never matched by the "new role" lookup, with no explicit
    invalidation required for correctness here (invalidation is still
    performed for cache-size/staleness hygiene -- see
    tests/unit/test_semantic_cache_service_invalidation.py).
    """
    cache = SemanticRetrievalCache(similarity_threshold=0.0)
    service, hybrid_service, _, _ = make_service(semantic_cache=cache)

    service.retrieve(query="q", access=_access(user_id=1, role=OrgRole.MEMBER))
    service.retrieve(query="q", access=_access(user_id=1, role=OrgRole.MANAGER))

    assert hybrid_service.call_count == 2


# --------------------------------------------------------------------------- #
# 8/9/26. fail-open behavior
# --------------------------------------------------------------------------- #


def test_cache_lookup_failure_falls_back_to_normal_retrieval():
    cache = MagicMock()
    cache.lookup.side_effect = RuntimeError("boom")

    service, hybrid_service, reranking_service, _ = make_service(semantic_cache=cache)

    result = service.retrieve(query="q", access=_access())

    hybrid_service.assert_called_once()
    reranking_service.assert_called_once()
    assert len(result.contexts) == 1


def test_cache_store_failure_does_not_break_retrieval():
    cache = MagicMock()
    cache.lookup.return_value = None
    cache.store.side_effect = RuntimeError("boom")

    service, hybrid_service, reranking_service, _ = make_service(semantic_cache=cache)

    result = service.retrieve(query="q", access=_access())

    assert len(result.contexts) == 1


def test_disabling_cache_via_settings_bypasses_it_entirely(monkeypatch):
    monkeypatch.setattr(settings, "SEMANTIC_CACHE_ENABLED", False)

    cache = MagicMock()
    service, hybrid_service, reranking_service, _ = make_service(semantic_cache=cache)

    service.retrieve(query="q", access=_access())

    cache.lookup.assert_not_called()
    cache.store.assert_not_called()
    hybrid_service.assert_called_once()


# --------------------------------------------------------------------------- #
# G/H. LangSmith cache-hit/miss-reason metadata (RBAC/C.3 follow-up).
#
# get_current_run_tree() returns None outside an active LangSmith trace
# (the normal case in these unit tests), so run.metadata.update(...) is
# never reached unless a fake run is injected -- monkeypatch the name as
# imported into app.retrieval.service, matching how that module calls it.
# --------------------------------------------------------------------------- #


class _FakeRun:
    def __init__(self):
        self.metadata: dict = {}


def test_cache_hit_metadata_is_correct(monkeypatch):
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    service, hybrid_service, reranking_service, _ = make_service(semantic_cache=cache)

    fake_run = _FakeRun()
    monkeypatch.setattr(
        "app.retrieval.service.get_current_run_tree",
        lambda: fake_run,
    )

    service.retrieve(query="q", access=_access())  # miss -> stores
    fake_run.metadata.clear()  # isolate the second (hit) call's metadata only
    service.retrieve(query="q", access=_access())  # hit

    assert fake_run.metadata["cache_hit"] is True
    assert "cache_similarity_score" in fake_run.metadata
    assert "cache_age_seconds" in fake_run.metadata
    assert "cache_miss_reason" not in fake_run.metadata
    assert "cache_best_similarity_score" not in fake_run.metadata


def test_cache_miss_metadata_reports_empty_reason(monkeypatch):
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    service, hybrid_service, reranking_service, _ = make_service(semantic_cache=cache)

    fake_run = _FakeRun()
    monkeypatch.setattr(
        "app.retrieval.service.get_current_run_tree",
        lambda: fake_run,
    )

    service.retrieve(query="q", access=_access())

    assert fake_run.metadata["cache_hit"] is False
    assert fake_run.metadata["cache_miss_reason"] == "empty"
    assert "cache_best_similarity_score" not in fake_run.metadata


def test_cache_miss_metadata_reports_namespace_mismatch_reason(monkeypatch):
    cache = SemanticRetrievalCache(similarity_threshold=0.0)
    service, hybrid_service, reranking_service, _ = make_service(semantic_cache=cache)

    fake_run = _FakeRun()
    monkeypatch.setattr(
        "app.retrieval.service.get_current_run_tree",
        lambda: fake_run,
    )

    service.retrieve(query="q", access=_access(user_id=1))
    fake_run.metadata.clear()
    service.retrieve(query="q", access=_access(user_id=2))

    assert fake_run.metadata["cache_hit"] is False
    assert fake_run.metadata["cache_miss_reason"] == "namespace_mismatch"
    assert "cache_best_similarity_score" not in fake_run.metadata


def test_cache_miss_metadata_reports_below_threshold_reason(monkeypatch):
    # First embedding orthogonal to the second -> same namespace, non-expired,
    # but similarity is below the configured threshold.
    cache = SemanticRetrievalCache(similarity_threshold=0.97)
    service, hybrid_service, reranking_service, embedder = make_service(
        semantic_cache=cache, embedding=[1.0, 0.0, 0.0],
    )

    fake_run = _FakeRun()
    monkeypatch.setattr(
        "app.retrieval.service.get_current_run_tree",
        lambda: fake_run,
    )

    service.retrieve(query="q", access=_access())

    embedder.embed_query.return_value = [0.0, 1.0, 0.0]
    fake_run.metadata.clear()
    service.retrieve(query="q2", access=_access())

    assert fake_run.metadata["cache_hit"] is False
    assert fake_run.metadata["cache_miss_reason"] == "below_threshold"
    # [1,0,0] vs [0,1,0] are orthogonal -> cosine similarity 0.0, the
    # actual best (and only) candidate score, never fabricated.
    assert fake_run.metadata["cache_best_similarity_score"] == pytest.approx(0.0)


def test_cache_disabled_miss_metadata_has_no_fabricated_reason(monkeypatch):
    monkeypatch.setattr(settings, "SEMANTIC_CACHE_ENABLED", False)

    cache = MagicMock()
    service, hybrid_service, reranking_service, _ = make_service(semantic_cache=cache)

    fake_run = _FakeRun()
    monkeypatch.setattr(
        "app.retrieval.service.get_current_run_tree",
        lambda: fake_run,
    )

    service.retrieve(query="q", access=_access())

    assert fake_run.metadata["cache_hit"] is False
    assert "cache_miss_reason" not in fake_run.metadata
    assert "cache_best_similarity_score" not in fake_run.metadata
