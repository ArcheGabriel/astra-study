from __future__ import annotations

import logging
import math
import time
from collections import OrderedDict
from collections.abc import Sequence

from app.cache.models import CacheEntry, CacheLookupResult, Namespace
from app.config.settings import settings
from app.retrieval.access import AccessContext
from app.retrieval.models import RetrievalResult

logger = logging.getLogger(__name__)

# The only miss reasons this class can determine reliably from its own
# state, without restructuring lookup() itself -- see
# SemanticRetrievalCache.diagnose_miss. "disabled"/lookup-exception cases
# are deliberately not covered here: the caller (RetrievalService) knows
# those directly and never calls diagnose_miss for them.
_MISS_REASON_EMPTY = "empty"
_MISS_REASON_NAMESPACE_MISMATCH = "namespace_mismatch"
_MISS_REASON_EXPIRED = "expired"
_MISS_REASON_BELOW_THRESHOLD = "below_threshold"


def build_namespace(access: AccessContext) -> Namespace:
    """
    Build the authorization-equivalence key a cache entry is isolated to.

    Mirrors exactly the fields ``AccessContext`` carries -- never a
    reduced subset. Two different users only ever share a namespace (and
    therefore a cache entry) if every one of these fields is identical,
    which is deliberately conservative: it is always a safe
    over-approximation of who ``DenseRepository._authorization_filter``
    would actually treat as retrieval-equivalent, never an
    under-approximation (see the C.3 investigation report's RBAC
    analysis for why a coarser key, e.g. organisation-only, would risk
    cross-team/cross-jurisdiction sharing it cannot prove safe).
    """

    return (
        access.user_id,
        access.organisation_id,
        access.role.value,
        access.team_ids,
        access.jurisdiction_team_ids,
    )


def _cosine_similarity(
    a: Sequence[float],
    b: Sequence[float],
) -> float:
    """
    Deterministic cosine similarity in [-1.0, 1.0]. Returns 0.0 (never
    raises) for mismatched dimensionality or a zero vector, both of
    which are treated as "no match" rather than an error -- a malformed
    cached embedding must never crash a lookup (fail-open).
    """

    if len(a) != len(b) or not a or not b:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


class SemanticRetrievalCache:
    """
    Bounded, in-process, namespace-isolated semantic cache for retrieval
    results (RBAC/C.3 -- "Semantic Retrieval Cache").

    Retrieval-level only: caches the already-reranked ``RetrievalResult``
    a full ``HybridService`` + Qdrant + ``RerankingService`` round trip
    would otherwise have to reproduce. Never caches a generated answer,
    a rewritten query, or anything LLM-produced -- see the C.3
    investigation report for why those layers were excluded.

    Every entry is isolated to the exact ``Namespace`` (user/org/role/
    team/jurisdiction tuple) it was stored under (``build_namespace``);
    a lookup never considers entries from a different namespace, so
    cross-tenant reuse is structurally impossible regardless of how
    similar two queries' embeddings are. This is a single in-process
    store -- no Redis, no external infrastructure -- matching the
    current single-process deployment profile this project's own C.3
    investigation confirmed.

    Every public method is designed to be called from a fail-open
    context: internal errors are caught and logged by the methods
    themselves wherever an error must not block a lookup/store, but
    callers (``RetrievalService``) additionally wrap every call in their
    own try/except, so even a bug in this class can never break
    retrieval -- the uncached path remains authoritative.
    """

    def __init__(
        self,
        *,
        similarity_threshold: float | None = None,
        ttl_seconds: float | None = None,
        max_size: int | None = None,
    ) -> None:

        self.similarity_threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else settings.SEMANTIC_CACHE_SIMILARITY_THRESHOLD
        )

        self.ttl_seconds = (
            ttl_seconds
            if ttl_seconds is not None
            else settings.SEMANTIC_CACHE_TTL_SECONDS
        )

        self.max_size = (
            max_size
            if max_size is not None
            else settings.SEMANTIC_CACHE_MAX_SIZE
        )

        # Insertion-ordered: eviction (store()) and expiry sweep (lookup())
        # both rely on iteration order == insertion order for a simple,
        # deterministic FIFO eviction strategy -- no LRU bookkeeping, no
        # external cache framework, matching "do not over-engineer".
        self._entries: OrderedDict[int, CacheEntry] = OrderedDict()
        self._next_id = 0

    def __len__(self) -> int:
        return len(self._entries)

    def lookup(
        self,
        *,
        namespace: Namespace,
        query_embedding: Sequence[float],
    ) -> CacheLookupResult | None:
        """
        Return the best same-namespace entry whose similarity to
        ``query_embedding`` meets ``similarity_threshold``, or ``None``.

        Expired entries (age > ``ttl_seconds``) are swept as they are
        encountered and never considered a match. A malformed individual
        entry (e.g. a corrupted/mismatched-dimension embedding) is
        skipped, not raised -- one bad entry must never fail the whole
        lookup for every other, valid entry.
        """

        now = time.monotonic()

        best_score = -1.0
        best_entry: CacheEntry | None = None
        expired_keys: list[int] = []

        for key, entry in self._entries.items():

            if entry.namespace != namespace:
                continue

            age = now - entry.created_at

            if age > self.ttl_seconds:
                expired_keys.append(key)
                continue

            try:
                score = _cosine_similarity(query_embedding, entry.query_embedding)
            except Exception:
                logger.exception(
                    "Semantic retrieval cache: malformed entry during "
                    "similarity comparison -- skipping entry.",
                )
                continue

            if score > best_score:
                best_score = score
                best_entry = entry

        for key in expired_keys:
            self._entries.pop(key, None)

        if best_entry is None or best_score < self.similarity_threshold:
            return None

        return CacheLookupResult(
            retrieval_result=best_entry.retrieval_result,
            similarity_score=best_score,
            cache_age_seconds=now - best_entry.created_at,
        )

    def diagnose_miss(
        self,
        *,
        namespace: Namespace,
        query_embedding: Sequence[float],
    ) -> tuple[str | None, float | None]:
        """
        Best-effort explanation for why a just-completed ``lookup()`` call
        for this exact ``(namespace, query_embedding)`` returned ``None``.
        Observability only -- never called on the hot path itself, never
        raises (returns ``(None, None)``, "undeterminable", rather than
        fabricate a reason or a score), and callers must still treat its
        result as advisory.

        A second, read-only pass over the same entries ``lookup()`` just
        scanned -- deliberately kept separate from ``lookup()`` rather
        than folded into it, so the hot path's return type and behavior
        are completely unchanged by this feature. Computing the best
        score here costs nothing extra: it is the same per-entry cosine
        comparison ``lookup()`` already performs, just not discarded.

        Returns a ``(reason, best_similarity_score)`` pair:

        - ``("empty", None)`` -- the cache has no entries at all.
        - ``("namespace_mismatch", None)`` -- entries exist, but none for
          this exact namespace, so no similarity comparison is
          meaningful.
        - ``("expired", None)`` -- same-namespace entries exist but all
          are past TTL, so none were eligible for a similarity
          comparison either.
        - ``("below_threshold", score)`` -- at least one non-expired
          same-namespace entry existed and was compared; ``score`` is
          the actual best cosine similarity found among them (always a
          real, non-fabricated value in this case -- never returned as
          ``None`` here).
        """

        if not self._entries:
            return _MISS_REASON_EMPTY, None

        now = time.monotonic()

        found_same_namespace = False
        best_score: float | None = None

        for entry in self._entries.values():

            if entry.namespace != namespace:
                continue

            found_same_namespace = True

            if now - entry.created_at > self.ttl_seconds:
                continue

            try:
                score = _cosine_similarity(query_embedding, entry.query_embedding)
            except Exception:
                logger.exception(
                    "Semantic retrieval cache: malformed entry during "
                    "miss-reason diagnosis -- skipping entry.",
                )
                continue

            if best_score is None or score > best_score:
                best_score = score

        if not found_same_namespace:
            return _MISS_REASON_NAMESPACE_MISMATCH, None

        if best_score is None:
            return _MISS_REASON_EXPIRED, None

        # At least one non-expired, same-namespace entry was compared,
        # and lookup() still returned None -- by lookup()'s own logic,
        # the only remaining cause is that even the best score fell
        # short of similarity_threshold.
        return _MISS_REASON_BELOW_THRESHOLD, best_score

    def store(
        self,
        *,
        namespace: Namespace,
        query_embedding: Sequence[float],
        retrieval_result: RetrievalResult,
    ) -> None:
        """
        Store one entry, evicting the oldest entry(ies) if this exceeds
        ``max_size``. FIFO eviction -- the simplest deterministic
        strategy appropriate for a bounded, single-process cache.
        """

        entry = CacheEntry(
            namespace=namespace,
            query_embedding=tuple(query_embedding),
            retrieval_result=retrieval_result,
            created_at=time.monotonic(),
        )

        self._entries[self._next_id] = entry
        self._next_id += 1

        while len(self._entries) > self.max_size:
            self._entries.popitem(last=False)

    def invalidate_user(self, user_id: int) -> int:
        """
        Remove every entry namespaced to ``user_id``, regardless of its
        other namespace fields. Used after a role/team-membership/
        jurisdiction mutation (RBAC C.2/5I/5J), each of which changes
        exactly one user's future ``AccessContext``.

        Returns the number of entries removed.
        """

        keys = [
            key
            for key, entry in self._entries.items()
            if entry.namespace[0] == user_id
        ]

        for key in keys:
            self._entries.pop(key, None)

        return len(keys)

    def invalidate_organisation(self, organisation_id: int) -> int:
        """
        Remove every entry namespaced to ``organisation_id``. Used after
        a document upload/delete, since every visibility branch
        ``DenseRepository._authorization_filter`` implements is at
        minimum organisation-scoped -- this is deliberately the
        coarsest, always-safe invalidation granularity for a document
        change, per the C.3 design's explicit instruction not to build a
        finer-grained (per-team/per-document) invalidation system.

        Returns the number of entries removed.
        """

        keys = [
            key
            for key, entry in self._entries.items()
            if entry.namespace[1] == organisation_id
        ]

        for key in keys:
            self._entries.pop(key, None)

        return len(keys)

    def clear(self) -> None:
        """Remove every entry. Not wired to any production call site --
        available for tests and an eventual operator tool."""

        self._entries.clear()
