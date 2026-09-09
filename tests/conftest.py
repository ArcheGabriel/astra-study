"""
Test-wide Qdrant collection isolation.

The integration tests drive ``DensePipeline`` / ``HybridPipeline`` with default
repositories, whose collection name resolves to
``settings.QDRANT_COLLECTION_NAME`` (production default: ``astra_study``).
Three of them -- ``test_dense_pipeline``, ``test_hybrid_pipeline`` and
``test_retrieval_comparison`` -- then call ``recreate_collection()``, which
deletes and recreates that collection.  Without isolation a bare ``pytest`` run
therefore destroys the production vector store.

This module forces every test onto a single dedicated, allowlisted collection
(``astra_study_test``) and fails the session loudly, before any test collection
completes, if a different name is requested.  It is strictly test-only:
production never imports ``tests/conftest.py`` and the production
``QDRANT_COLLECTION_NAME`` semantics are left completely unchanged.

``DenseRepository.COLLECTION_NAME`` is a class attribute bound at import time
from ``settings.QDRANT_COLLECTION_NAME``.  Setting ``os.environ`` alone is not
sufficient if the settings or repository module has already been imported
(another conftest, a pytest plugin, an earlier in-process run), so the override
is also applied defensively to the already-materialised values.

Cleanup of the dedicated collection runs only when the session actually
collected integration tests; a ``tests/unit``-only run never constructs a
Qdrant client and never contacts Qdrant.
"""

from __future__ import annotations

import os

#: The production collection tests must never touch.
PRODUCTION_COLLECTION = "astra_study"

#: The one collection name the test suite is allowed to use.
DEDICATED_TEST_COLLECTION = "astra_study_test"


def _isolate_qdrant_collection() -> str:
    """
    Pin every test to the dedicated Qdrant collection and return its name.

    Executed at import time -- before pytest collects any test module -- so the
    override is in place before ``app.config.settings`` is first imported and
    before ``DenseRepository`` binds its ``COLLECTION_NAME`` class attribute.

    Allowlist: ``QDRANT_COLLECTION_NAME`` may be unset or exactly
    ``astra_study_test``.  Any other value (the production ``astra_study``
    included) raises ``RuntimeError``.
    """

    requested = os.environ.get("QDRANT_COLLECTION_NAME")

    if requested is not None and requested != DEDICATED_TEST_COLLECTION:
        raise RuntimeError(
            "Refusing to run the test suite with "
            f"QDRANT_COLLECTION_NAME={requested!r}. Integration tests may only "
            f"use the dedicated collection {DEDICATED_TEST_COLLECTION!r}; unset "
            "QDRANT_COLLECTION_NAME or set it to exactly that value "
            f"(the production collection {PRODUCTION_COLLECTION!r} is never "
            "allowed)."
        )

    collection = DEDICATED_TEST_COLLECTION
    os.environ["QDRANT_COLLECTION_NAME"] = collection

    # Defensively update anything that already read the value. Importing these
    # now is harmless: it only materialises the settings singleton / the class
    # object -- no Qdrant client is constructed and no network call is made.
    try:
        from app.config.settings import settings
    except Exception:  # pragma: no cover - settings misconfigured in this env
        settings = None
    else:
        settings.QDRANT_COLLECTION_NAME = collection

    try:
        from app.search.dense.repository import DenseRepository
    except Exception:  # pragma: no cover - repository import unavailable
        DenseRepository = None
    else:
        DenseRepository.COLLECTION_NAME = collection

    # Final guard: every effective value tests could reach must be exactly the
    # dedicated test collection.
    effective = {collection}
    if settings is not None:
        effective.add(settings.QDRANT_COLLECTION_NAME)
    if DenseRepository is not None:
        effective.add(DenseRepository.COLLECTION_NAME)

    if effective != {DEDICATED_TEST_COLLECTION}:
        raise RuntimeError(
            "Qdrant test isolation failed: effective collection names are "
            f"{sorted(effective)!r}, expected only "
            f"[{DEDICATED_TEST_COLLECTION!r}]."
        )

    return collection


#: Effective, isolated Qdrant collection name for the whole test session.
TEST_QDRANT_COLLECTION = _isolate_qdrant_collection()


#: Set during collection when the session includes integration tests. Only then
#: may the dedicated test collection be cleaned up on session finish.
_cleanup_required = False


def pytest_collection_modifyitems(items) -> None:
    """Record whether this session collected any ``tests/integration`` test."""

    global _cleanup_required

    for item in items:
        nodeid = item.nodeid.replace("\\", "/")
        if nodeid.startswith("tests/integration/") or "/tests/integration/" in nodeid:
            _cleanup_required = True
            return


def pytest_sessionfinish() -> None:
    """
    Best-effort drop the dedicated test collection -- and only that collection --
    after a session that ran integration tests.

    A ``tests/unit``-only run never reaches the Qdrant client here.
    """

    if not _cleanup_required:
        return

    # Cleanup is only ever allowed against the dedicated test collection.
    if TEST_QDRANT_COLLECTION != DEDICATED_TEST_COLLECTION:  # pragma: no cover
        return

    try:
        from app.search.dense.repository import DenseRepository

        repository = DenseRepository()

        if (
            repository.COLLECTION_NAME == DEDICATED_TEST_COLLECTION
            and repository.COLLECTION_NAME != PRODUCTION_COLLECTION
            and repository.collection_exists()
        ):
            repository.client.delete_collection(
                collection_name=DEDICATED_TEST_COLLECTION,
            )
    except Exception:
        # Integration tests own the pass/fail signal; a cleanup miss (e.g.
        # Qdrant already gone) must not be reported as a failure here.
        pass
