"""
Executable specification for RBAC-5B: threading the trusted AccessContext
(RBAC-5A) through the retrieval contract.

RBAC-5B does not implement any organisation/team/role-based Qdrant
filtering -- that is RBAC-5C. These tests only prove that:

- the message API boundary obtains AccessContext exclusively through
  ``get_access_context`` (never from client-controllable request data);
- the *same* AccessContext instance travels, unmodified, through
  ConversationService -> AIPipeline -> RetrievalService -> HybridService ->
  DenseRepository, for both the normal and the streaming path;
- the existing Qdrant filter semantics (``user_id`` now sourced from
  ``access.user_id``, plus ``is_reference=False`` / ``is_appendix=False``)
  are unchanged, with no organisation/team/access_scope/role condition
  added;
- chat ownership continues to be enforced from ``current_user``, entirely
  independent of ``access``;
- there is no second, competing authorization-identity parameter anywhere
  in the new contract.
"""

from __future__ import annotations

import inspect
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.params import Depends as DependsMarker
from qdrant_client.models import Filter

from app.ai.pipeline import AIPipeline
from app.api.v1.message import create_message, stream_message
from app.dependencies.access import get_access_context
from app.enums.organisation import OrgRole
from app.exceptions.chat import ChatNotFoundError
from app.generation.models import GenerationResponse
from app.retrieval.access import AccessContext
from app.retrieval.service import RetrievalService
from app.search.dense.repository import DenseRepository
from app.search.hybrid.service import HybridService
from app.services.conversation import ConversationService

_ACCESS = AccessContext(
    user_id=7,
    organisation_id=3,
    team_ids=(10, 11),
    role=OrgRole.MEMBER,
)

_OTHER_ACCESS = AccessContext(
    user_id=999,
    organisation_id=999,
    team_ids=(),
    role=OrgRole.ADMIN,
)


# --------------------------------------------------------------------------- #
# 1. API boundary: AccessContext comes only from get_access_context
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("route", [create_message, stream_message])
def test_message_routes_obtain_access_only_through_get_access_context(route):
    parameters = inspect.signature(route).parameters

    assert "access" in parameters

    default = parameters["access"].default
    assert isinstance(default, DependsMarker)
    assert default.dependency is get_access_context


@pytest.mark.parametrize("route", [create_message, stream_message])
def test_message_routes_accept_no_client_controllable_rbac_parameter(route):
    """No Query/Body/Path/Header parameter can supply organisation_id, role,
    or team_ids -- the only way in is the AccessContext dependency."""

    parameters = inspect.signature(route).parameters

    for name in ("organisation_id", "team_ids", "role"):
        assert name not in parameters


# --------------------------------------------------------------------------- #
# 2-6, 13. AccessContext propagation: API -> ConversationService ->
# AIPipeline -> RetrievalService -> HybridService -> DenseRepository
# --------------------------------------------------------------------------- #


def _persisted(message):
    """Simulate MessageRepository.create() assigning DB-generated fields."""
    message.id = 1
    message.created_at = datetime(2026, 1, 1)
    return message


def make_conversation_service(ai_pipeline):
    chat_repository = MagicMock()
    chat_repository.get_by_id.return_value = SimpleNamespace(
        id=1, user_id=42, title="New Chat", summary=None,
    )

    message_repository = MagicMock()
    message_repository.get_conversational_messages.return_value = [
        SimpleNamespace(content="hello", role="user"),
    ]
    message_repository.create.side_effect = _persisted

    message_service = MagicMock()
    message_service.create_message.return_value = SimpleNamespace(
        id=1, role="user", content="hi", created_at=datetime(2026, 1, 1),
    )

    conversation_summary_service = MagicMock()

    return ConversationService(
        chat_repository=chat_repository,
        message_repository=message_repository,
        message_service=message_service,
        ai_pipeline=ai_pipeline,
        conversation_summary_service=conversation_summary_service,
    )


def test_send_message_forwards_access_unmodified_to_ai_pipeline():
    ai_pipeline = MagicMock()
    ai_pipeline.generate_response.return_value = SimpleNamespace(
        answer="answer", citations=[],
    )

    service = make_conversation_service(ai_pipeline)

    service.send_message(
        chat_id=1,
        current_user=SimpleNamespace(id=42),
        access=_ACCESS,
        message_data=SimpleNamespace(content="hi"),
        background_tasks=None,
    )

    ai_pipeline.generate_response.assert_called_once()
    assert ai_pipeline.generate_response.call_args.kwargs["access"] is _ACCESS


def test_stream_message_forwards_access_unmodified_to_ai_pipeline():
    ai_pipeline = MagicMock()
    ai_pipeline.stream_response.return_value = iter(
        [SimpleNamespace(text="hi", citations=None)]
    )

    service = make_conversation_service(ai_pipeline)

    list(
        service.stream_message(
            chat_id=1,
            current_user=SimpleNamespace(id=42),
            access=_ACCESS,
            message_data=SimpleNamespace(content="hi"),
            background_tasks=None,
        )
    )

    ai_pipeline.stream_response.assert_called_once()
    assert ai_pipeline.stream_response.call_args.kwargs["access"] is _ACCESS


def test_streaming_and_non_streaming_paths_receive_the_same_access_instance():
    """Requirement 13: whichever path is taken, retrieval sees the identical
    AccessContext object the API boundary resolved -- no separate identity
    is derived for streaming."""

    normal_pipeline = MagicMock()
    normal_pipeline.generate_response.return_value = SimpleNamespace(
        answer="a", citations=[],
    )
    normal_service = make_conversation_service(normal_pipeline)
    normal_service.send_message(
        chat_id=1,
        current_user=SimpleNamespace(id=42),
        access=_ACCESS,
        message_data=SimpleNamespace(content="hi"),
        background_tasks=None,
    )

    streaming_pipeline = MagicMock()
    streaming_pipeline.stream_response.return_value = iter(
        [SimpleNamespace(text="a", citations=None)]
    )
    streaming_service = make_conversation_service(streaming_pipeline)
    list(
        streaming_service.stream_message(
            chat_id=1,
            current_user=SimpleNamespace(id=42),
            access=_ACCESS,
            message_data=SimpleNamespace(content="hi"),
            background_tasks=None,
        )
    )

    assert (
        normal_pipeline.generate_response.call_args.kwargs["access"]
        is streaming_pipeline.stream_response.call_args.kwargs["access"]
        is _ACCESS
    )


def test_ai_pipeline_generate_response_forwards_access_to_retrieval_service():
    retrieval_service = MagicMock()
    retrieval_service.retrieve.return_value = SimpleNamespace(
        query="q", contexts=[], retrieval_latency=0.0,
    )
    generation_service = MagicMock()
    generation_service.generate.return_value = GenerationResponse(
        answer="a", citations=[],
    )

    pipeline = AIPipeline(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        llm_service=MagicMock(),
    )

    pipeline.generate_response(
        conversation=[SimpleNamespace(role="user", content="hi")],
        access=_ACCESS,
    )

    retrieval_service.retrieve.assert_called_once()
    assert retrieval_service.retrieve.call_args.kwargs["access"] is _ACCESS


def test_ai_pipeline_stream_response_forwards_access_to_retrieval_service():
    retrieval_service = MagicMock()
    retrieval_service.retrieve.return_value = SimpleNamespace(
        query="q", contexts=[], retrieval_latency=0.0,
    )
    generation_service = MagicMock()
    generation_service.stream.return_value = iter(["a"])
    generation_service.citations_for.return_value = []

    pipeline = AIPipeline(
        retrieval_service=retrieval_service,
        generation_service=generation_service,
        llm_service=MagicMock(),
    )

    list(
        pipeline.stream_response(
            conversation=[SimpleNamespace(role="user", content="hi")],
            access=_ACCESS,
        )
    )

    retrieval_service.retrieve.assert_called_once()
    assert retrieval_service.retrieve.call_args.kwargs["access"] is _ACCESS


def test_retrieval_service_forwards_access_to_hybrid_service():
    hybrid_service = MagicMock()
    hybrid_service.return_value = []
    reranking_service = MagicMock()

    service = RetrievalService(
        hybrid_service=hybrid_service,
        reranking_service=reranking_service,
    )

    service.retrieve(query="q", access=_ACCESS)

    hybrid_service.assert_called_once()
    assert hybrid_service.call_args.kwargs["access"] is _ACCESS


def test_hybrid_service_forwards_access_to_dense_repository():
    repository = MagicMock()
    repository.hybrid_search.return_value = []

    embedder = MagicMock()
    embedder.embed_query.return_value = [0.1, 0.2]

    sparse_encoder = MagicMock()
    sparse_encoder.encode_query.return_value = SimpleNamespace(
        indices=[1], values=[0.5],
    )

    service = HybridService(
        embedder=embedder,
        sparse_encoder=sparse_encoder,
        repository=repository,
    )

    service.search(access=_ACCESS, query="q", limit=10)

    repository.hybrid_search.assert_called_once()
    assert repository.hybrid_search.call_args.kwargs["access"] is _ACCESS


# --------------------------------------------------------------------------- #
# 7-12. Qdrant filter audit: user_id from access.user_id, structural filters
# unchanged.
#
# NOTE: as of RBAC-5C, the filter also carries organisation/team/access_scope
# authorization branches (approved scope change -- see
# tests/unit/test_rbac_5c_authorization_filter.py for the full spec of that
# behaviour). These two tests were originally written to prove RBAC-5B's
# narrower boundary ("no RBAC scope conditions yet") and are updated here
# only to navigate the new nested filter shape -- they still prove exactly
# what RBAC-5B always required: user_id sourced from access.user_id, and
# is_reference/is_appendix preserved. `role` remains, as always, never a raw
# Qdrant filter key (RBAC-5C encodes it only as a Python-side branch
# inclusion decision).
# --------------------------------------------------------------------------- #


def make_dense_repository_with_fake_client():
    repository = DenseRepository.__new__(DenseRepository)
    repository.client = MagicMock()
    repository.client.query_points.return_value = SimpleNamespace(points=[])
    return repository


def _individual_branch_user_id(retrieval_filter: Filter) -> int:
    nested = next(c for c in retrieval_filter.must if isinstance(c, Filter))
    individual_branch = nested.should[0]
    return next(
        c.match.value for c in individual_branch.must if c.key == "user_id"
    )


def test_dense_repository_hybrid_search_filters_by_access_user_id():
    repository = make_dense_repository_with_fake_client()

    repository.hybrid_search(
        dense_vector=[0.1],
        sparse_indices=[1],
        sparse_values=[0.5],
        access=_ACCESS,
        limit=5,
    )

    call = repository.client.query_points.call_args
    retrieval_filter: Filter = call.kwargs["prefetch"][0].filter

    structural = {c.key: c.match.value for c in retrieval_filter.must if hasattr(c, "key")}

    assert _individual_branch_user_id(retrieval_filter) == _ACCESS.user_id
    assert structural["is_reference"] is False
    assert structural["is_appendix"] is False


def test_dense_repository_hybrid_search_filter_role_is_never_a_raw_filter_key():
    """`role` must never appear as a Qdrant FieldCondition key -- RBAC-5C
    only ever uses it to decide whether the organisation branch exists."""

    repository = make_dense_repository_with_fake_client()

    repository.hybrid_search(
        dense_vector=[0.1],
        sparse_indices=[1],
        sparse_values=[0.5],
        access=_ACCESS,
        limit=5,
    )

    call = repository.client.query_points.call_args
    retrieval_filter: Filter = call.kwargs["prefetch"][0].filter

    def all_keys(node) -> set[str]:
        keys: set[str] = set()

        def walk(value):
            if isinstance(value, Filter):
                for group in (value.must, value.should, value.must_not):
                    if group is None:
                        continue
                    items = group if isinstance(group, list) else [group]
                    for item in items:
                        walk(item)
            elif hasattr(value, "key"):
                keys.add(value.key)

        walk(node)
        return keys

    assert "role" not in all_keys(retrieval_filter)


def test_dense_repository_hybrid_search_applies_the_same_filter_to_dense_and_sparse_prefetch():
    """The dense and sparse RRF branches must never diverge in filtering."""

    repository = make_dense_repository_with_fake_client()

    repository.hybrid_search(
        dense_vector=[0.1],
        sparse_indices=[1],
        sparse_values=[0.5],
        access=_ACCESS,
        limit=5,
    )

    call = repository.client.query_points.call_args
    dense_prefetch, sparse_prefetch = call.kwargs["prefetch"]

    assert dense_prefetch.filter == sparse_prefetch.filter


def test_different_access_contexts_produce_different_user_id_filters():
    """Sanity check that the filter genuinely tracks access.user_id rather
    than a hardcoded/stale value."""

    repository = make_dense_repository_with_fake_client()

    repository.hybrid_search(
        dense_vector=[0.1], sparse_indices=[1], sparse_values=[0.5],
        access=_OTHER_ACCESS, limit=5,
    )

    call = repository.client.query_points.call_args
    retrieval_filter: Filter = call.kwargs["prefetch"][0].filter

    assert _individual_branch_user_id(retrieval_filter) == _OTHER_ACCESS.user_id
    assert _individual_branch_user_id(retrieval_filter) != _ACCESS.user_id


# --------------------------------------------------------------------------- #
# 14. Chat ownership continues to use current_user, independent of access
# --------------------------------------------------------------------------- #


def test_chat_ownership_is_enforced_from_current_user_not_access():
    """A valid AccessContext for a *different* identity must not bypass the
    chat-ownership check, which is keyed on current_user.id only."""

    ai_pipeline = MagicMock()
    service = make_conversation_service(ai_pipeline)
    # chat_repository fixture above returns a chat owned by user_id=42.

    with pytest.raises(ChatNotFoundError):
        service.send_message(
            chat_id=1,
            current_user=SimpleNamespace(id=999),  # not the owner
            access=_ACCESS,  # a validly-constructed AccessContext regardless
            message_data=SimpleNamespace(content="hi"),
            background_tasks=None,
        )

    ai_pipeline.generate_response.assert_not_called()


# --------------------------------------------------------------------------- #
# 15-16. AccessContext cannot be omitted/defaulted; no competing identity
# parameter exists anywhere in the new contract
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "func",
    [
        AIPipeline.generate_response,
        AIPipeline.stream_response,
        RetrievalService.retrieve,
        HybridService.search,
        DenseRepository.hybrid_search,
        ConversationService.send_message,
        ConversationService.stream_message,
    ],
)
def test_access_parameter_has_no_default_and_no_competing_identity_parameter(func):
    parameters = inspect.signature(func).parameters

    assert "access" in parameters
    assert parameters["access"].default is inspect.Parameter.empty

    # No second, competing authorization-identity parameter survives
    # alongside the trusted AccessContext.
    for forbidden in ("user_id", "organisation_id", "team_ids", "role"):
        assert forbidden not in parameters


def test_ai_pipeline_generate_response_rejects_call_without_access():
    pipeline = AIPipeline(
        retrieval_service=MagicMock(),
        generation_service=MagicMock(),
        llm_service=MagicMock(),
    )

    with pytest.raises(TypeError):
        pipeline.generate_response(
            conversation=[SimpleNamespace(role="user", content="hi")],
        )
