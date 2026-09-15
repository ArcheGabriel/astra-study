from app.retrieval.base import BaseRetrievalService
from app.retrieval.formatter import ContextFormatter
from app.retrieval.models import (
    RetrievedContext,
    RetrievalResult,
)

# ``RetrievalService`` is deliberately NOT eagerly imported/re-exported here.
# Nothing in the codebase imports it via ``app.retrieval`` (every caller uses
# the fully-qualified ``app.retrieval.service``) and eagerly importing it
# pulled the entire search stack (HybridService -> DenseRepository) into this
# package's __init__ -- which in turn imports back into this same package
# (``app.retrieval.access``), producing a circular import whenever a leaf
# module under ``app.search`` is the first thing a process imports (e.g.
# ``scripts/reingest_document.py``). Import ``RetrievalService`` from
# ``app.retrieval.service`` directly instead.

__all__ = [
    "BaseRetrievalService",
    "ContextFormatter",
    "RetrievedContext",
    "RetrievalResult",
]