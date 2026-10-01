from __future__ import annotations

from dataclasses import dataclass

from app.retrieval.models import RetrievalResult

# The authorization-equivalence key a cached entry is isolated to.
# (user_id, organisation_id, role_value, team_ids, jurisdiction_team_ids)
# -- the exact fields AccessContext carries (app/retrieval/access.py).
# Deliberately includes user_id (not just organisation/team/role) per the
# approved C.3 design: "prefer correctness over maximizing cache sharing".
# A tuple, not a dataclass, so it hashes/compares by value with no extra
# machinery and can be used directly as an equality check.
Namespace = tuple[int, int, str, tuple[int, ...], tuple[int, ...]]


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """
    One stored semantic-retrieval-cache entry.

    ``query_embedding`` is the exact dense query vector produced by
    ``RetrievalService``'s own embedding call -- never a second,
    cache-specific embedding request (see the C.3 investigation report).
    ``retrieval_result`` is the real, already-reranked ``RetrievalResult``
    that would otherwise have required a full Qdrant + CrossEncoder round
    trip to reproduce. ``created_at`` is a ``time.monotonic()`` timestamp,
    immune to wall-clock adjustments, used for TTL expiry math only.
    """

    namespace: Namespace
    query_embedding: tuple[float, ...]
    retrieval_result: RetrievalResult
    created_at: float


@dataclass(frozen=True, slots=True)
class CacheLookupResult:
    """
    The result of a cache HIT -- the matched entry's ``RetrievalResult``
    plus the observability fields ``RetrievalService`` attaches to its
    existing LangSmith ``run.metadata``.
    """

    retrieval_result: RetrievalResult
    similarity_score: float
    cache_age_seconds: float
