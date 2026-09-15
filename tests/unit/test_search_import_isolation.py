"""
Regression test for a circular import discovered during the RBAC-5B
independent audit.

``app/search/dense/repository.py`` gained a top-level
``from app.retrieval.access import AccessContext`` (RBAC-5B). Importing any
submodule forces Python to first execute the parent package's
``__init__.py``. If ``app/retrieval/__init__.py`` eagerly imports something
that itself imports back down into ``app.search`` (as it used to, via
``RetrievalService`` -> ``HybridService`` -> ``DenseRepository``), then
whichever of these leaf modules is the *first* thing a process imports ends
up re-entering itself while only partially initialized, raising
``ImportError``.

This is entirely masked by import *order* within a single interpreter
process: once any part of ``app.retrieval`` has been imported once (which
routinely happens first in the full unit-test session or in
``app.main``), everything is cached and the bug never surfaces again in
that process. That is exactly why the original RBAC-5B implementation's own
``pytest`` run (and even ``import app.main``) did not catch it, while the
real, documented ``scripts/reingest_document.py`` -- whose first relevant
import is ``app.search.hybrid.pipeline`` -- failed immediately.

These tests therefore deliberately spawn a *fresh* subprocess per import
target rather than relying on anything already cached in this test
session's own ``sys.modules``. Each must fail against the pre-fix
implementation (where ``app/retrieval/__init__.py`` eagerly imported
``RetrievalService``) and pass once that eager import is removed/lazy.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

_TARGETS = [
    ("import app.search.dense.repository", "app.search.dense.repository"),
    (
        "from app.search.dense.pipeline import DensePipeline",
        "app.search.dense.pipeline.DensePipeline",
    ),
    (
        "from app.search.hybrid.pipeline import HybridPipeline",
        "app.search.hybrid.pipeline.HybridPipeline",
    ),
    ("import app.search.hybrid.service", "app.search.hybrid.service"),
]

# The exact import order scripts/reingest_document.py uses before it ever
# touches app.search.hybrid.pipeline -- the real production path the audit
# found broken.
_REINGEST_SCRIPT_IMPORT_SEQUENCE = "\n".join(
    [
        "from app.chunking.pipeline import ChunkPipeline",
        "from app.ingestion.factory import ProcessorFactory",
        "from app.chunking.utils.tokens import count_tokens",
        "from app.search.hybrid.pipeline import HybridPipeline",
    ]
)


def _run_in_fresh_process(code: str) -> subprocess.CompletedProcess:
    """Run ``code`` in a brand-new Python process with no inherited
    ``sys.modules`` cache, so import order is genuinely isolated from
    whatever this test session has already imported."""

    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
    )


@pytest.mark.parametrize(
    "import_statement,label",
    _TARGETS,
    ids=[label for _, label in _TARGETS],
)
def test_search_module_importable_as_first_touch_in_fresh_process(
    import_statement, label,
):
    """Each of these must be importable as the very first thing a fresh
    process does -- reproducing the exact failure mode found in
    ``scripts/reingest_document.py`` (whose first relevant import is
    ``app.search.hybrid.pipeline``, not anything under ``app.retrieval``)."""

    result = _run_in_fresh_process(import_statement)

    assert result.returncode == 0, (
        f"Fresh-process import of {label!r} failed:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "circular import" not in result.stderr.lower()


def test_reingest_document_script_import_sequence_succeeds_in_fresh_process():
    """Reproduces the exact import order used by
    ``scripts/reingest_document.py`` (chunking -> ingestion -> chunking
    utils -> hybrid pipeline) without running any ingestion/indexing -- this
    is the real broken production path the independent audit found."""

    result = _run_in_fresh_process(_REINGEST_SCRIPT_IMPORT_SEQUENCE)

    assert result.returncode == 0, (
        "Fresh-process import sequence matching scripts/reingest_document.py "
        f"failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "circular import" not in result.stderr.lower()
