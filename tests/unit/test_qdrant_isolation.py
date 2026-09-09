"""
Offline safety regression for Qdrant test isolation.

Guarantees the test session can only ever operate against the dedicated
``astra_study_test`` collection, never production ``astra_study``. Fully
offline: no Qdrant client is constructed, no network request is made, no
collection is created, deleted, or recreated.
"""

from __future__ import annotations

import pytest

from app.config.settings import settings
from app.search.dense.repository import DenseRepository
from tests import conftest
from tests.conftest import (
    DEDICATED_TEST_COLLECTION,
    PRODUCTION_COLLECTION,
    TEST_QDRANT_COLLECTION,
    _isolate_qdrant_collection,
)


def test_default_test_collection_is_dedicated() -> None:
    assert DEDICATED_TEST_COLLECTION == "astra_study_test"
    assert TEST_QDRANT_COLLECTION == DEDICATED_TEST_COLLECTION
    assert TEST_QDRANT_COLLECTION != PRODUCTION_COLLECTION


def test_settings_and_repository_binding_are_isolated() -> None:
    # The class attribute is what every destructive collection op uses; it is
    # bound at import time, so it must be patched, not just the env var.
    assert settings.QDRANT_COLLECTION_NAME == DEDICATED_TEST_COLLECTION
    assert DenseRepository.COLLECTION_NAME == DEDICATED_TEST_COLLECTION


def test_unset_env_resolves_to_dedicated_collection(monkeypatch) -> None:
    monkeypatch.delenv("QDRANT_COLLECTION_NAME", raising=False)
    assert _isolate_qdrant_collection() == DEDICATED_TEST_COLLECTION


def test_explicit_dedicated_collection_is_accepted(monkeypatch) -> None:
    monkeypatch.setenv("QDRANT_COLLECTION_NAME", "astra_study_test")
    assert _isolate_qdrant_collection() == DEDICATED_TEST_COLLECTION


def test_explicit_production_collection_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("QDRANT_COLLECTION_NAME", "astra_study")
    with pytest.raises(RuntimeError):
        _isolate_qdrant_collection()


def test_arbitrary_collection_name_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("QDRANT_COLLECTION_NAME", "some_real_collection")
    with pytest.raises(RuntimeError):
        _isolate_qdrant_collection()


def test_sessionfinish_builds_no_qdrant_client_without_integration_tests(
    monkeypatch,
) -> None:
    # With no tests/integration item collected the cleanup hook stays disarmed
    # and must return before ever constructing a Qdrant client.
    monkeypatch.setattr(conftest, "_cleanup_required", False)

    def _forbidden(*args, **kwargs):
        raise AssertionError(
            "unit-only run must not construct a Qdrant client",
        )

    monkeypatch.setattr(DenseRepository, "__init__", _forbidden)

    conftest.pytest_sessionfinish()
