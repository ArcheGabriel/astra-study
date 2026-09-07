"""
Executable specification for the rolling conversation-memory behaviour
(feat/conversation-memory-window).

Covers, with no live services:

- the summary cadence: first summary at ``INITIAL_SUMMARY_THRESHOLD`` total
  conversational messages, then a refresh every ``SUMMARY_UPDATE_INTERVAL``;
- the bounded summary input: previous summary + only the new delta, never the
  whole transcript;
- the bounded generation context: summary + a rolling
  ``RECENT_MESSAGE_WINDOW`` of recent messages once summarization is active,
  full history before that;
- retrieval-query rewriting keeping its own independent history window;
- failure / catch-up handling that never drops conversation context;
- deterministic id-based message ordering;
- the streaming path (exactly one assistant row, ``done`` never blocked by the
  summary call).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.database.base import Base
from app.enums.message import MessageRole
from app.generation.models import GenerationRequest, GenerationResponse
from app.generation.prompt_builder import PromptBuilder
from app.retrieval.models import RetrievalResult, RetrievedContext

# Import model modules so ``Base.metadata`` is complete before create_all.
import app.models.user  # noqa: F401
import app.models.chat  # noqa: F401
import app.models.message  # noqa: F401

from app.models.chat import ChatSession
from app.models.message import ChatMessage
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository
from app.services.conversation import ConversationService
from app.services.conversation_summary import ConversationSummaryService
from app.ai.pipeline import AIPipeline


BASE_TIME = datetime(2026, 1, 1, 12, 0, 0)


# --------------------------------------------------------------------------- #
# Fixtures / fakes
# --------------------------------------------------------------------------- #


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    try:
        yield session
    finally:
        session.close()


def make_chat(db, *, summary=None, summary_updated_at=None) -> ChatSession:
    chat = ChatSession(
        title="New Chat",
        user_id=1,
        summary=summary,
        summary_updated_at=summary_updated_at,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def add_messages(
    db,
    chat_id: int,
    count: int,
    *,
    start_index: int = 0,
    last_is_user: bool = False,
) -> None:
    """Append ``count`` conversational messages with controlled timestamps.

    Roles alternate USER/ASSISTANT starting from USER at ``start_index`` 0.
    ``last_is_user`` forces the final message to be a USER message so that
    window tests can model "the current user turn just persisted".
    """

    end = start_index + count
    for i in range(start_index, end):
        role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
        if last_is_user and i == end - 1:
            role = MessageRole.USER
        db.add(
            ChatMessage(
                chat_session_id=chat_id,
                role=role,
                content=f"m{i + 1}",
                created_at=BASE_TIME + timedelta(minutes=i),
            )
        )
    db.commit()


def set_cursor(db, chat: ChatSession, covered_count: int) -> None:
    """Pin ``summary_updated_at`` so exactly ``covered_count`` messages count
    as already summarized (between message N and message N+1)."""

    chat.summary_updated_at = BASE_TIME + timedelta(
        minutes=covered_count - 1,
        seconds=30,
    )
    db.commit()


class FakeSummaryPipeline:
    """Stands in for AIPipeline in the summary service (only generate_summary)."""

    def __init__(self) -> None:
        self.calls: list[SimpleNamespace] = []
        self.should_fail = False
        self.next_result = "ROLLING SUMMARY"

    def generate_summary(self, *, existing_summary, conversation):
        self.calls.append(
            SimpleNamespace(
                existing_summary=existing_summary,
                messages=[m.content for m in conversation],
            )
        )
        if self.should_fail:
            raise RuntimeError("summary backend down")
        return self.next_result


def make_summary_service(db, pipeline=None):
    pipeline = pipeline or FakeSummaryPipeline()
    service = ConversationSummaryService(
        chat_repository=ChatRepository(db),
        message_repository=MessageRepository(db),
        ai_pipeline=pipeline,
    )
    return service, pipeline


# --------------------------------------------------------------------------- #
# Repository ordering / counting
# --------------------------------------------------------------------------- #


def test_message_ordering_is_by_id_even_with_identical_timestamps(db):
    chat = make_chat(db)
    stamp = BASE_TIME
    for i in range(6):
        db.add(
            ChatMessage(
                chat_session_id=chat.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"m{i + 1}",
                created_at=stamp,  # deliberately identical
            )
        )
    db.commit()

    repo = MessageRepository(db)
    ordered = [m.content for m in repo.get_conversational_messages(chat.id)]
    assert ordered == ["m1", "m2", "m3", "m4", "m5", "m6"]


def test_counting_includes_user_and_assistant_only(db):
    chat = make_chat(db)
    add_messages(db, chat.id, 4)  # 2 user + 2 assistant
    db.add(
        ChatMessage(
            chat_session_id=chat.id,
            role=MessageRole.SYSTEM,
            content="system noise",
            created_at=BASE_TIME + timedelta(minutes=99),
        )
    )
    db.commit()

    repo = MessageRepository(db)
    assert repo.count_conversational_messages(chat.id) == 4
    assert len(repo.get_conversational_messages(chat.id)) == 4


# --------------------------------------------------------------------------- #
# Summary cadence
# --------------------------------------------------------------------------- #


def test_no_summary_before_threshold(db):
    chat = make_chat(db)
    add_messages(db, chat.id, settings.INITIAL_SUMMARY_THRESHOLD - 1)

    service, pipeline = make_summary_service(db)
    service.update_summary(chat_id=chat.id)

    assert pipeline.calls == []
    db.refresh(chat)
    assert chat.summary is None
    assert chat.summary_updated_at is None


def test_first_summary_at_exact_threshold(db):
    chat = make_chat(db)
    add_messages(db, chat.id, 20)

    service, pipeline = make_summary_service(db)
    service.update_summary(chat_id=chat.id)

    assert len(pipeline.calls) == 1
    assert pipeline.calls[0].existing_summary is None
    assert pipeline.calls[0].messages == [f"m{i}" for i in range(1, 21)]
    db.refresh(chat)
    assert chat.summary == "ROLLING SUMMARY"
    assert chat.summary_updated_at is not None


def test_no_regeneration_on_non_boundary_turns(db):
    chat = make_chat(db, summary="S1")
    add_messages(db, chat.id, 26)
    set_cursor(db, chat, 20)  # summary covers messages 1..20

    service, pipeline = make_summary_service(db)
    for _ in range(4):  # counts 26, 27, 28, 29 -> pending 6..9
        service.update_summary(chat_id=chat.id)

    assert pipeline.calls == []


def test_refresh_at_thirty_uses_previous_summary_plus_only_new_delta(db):
    chat = make_chat(db, summary="S1")
    add_messages(db, chat.id, 30)
    set_cursor(db, chat, 20)

    service, pipeline = make_summary_service(db)
    pipeline.next_result = "S2"
    service.update_summary(chat_id=chat.id)

    assert len(pipeline.calls) == 1
    assert pipeline.calls[0].existing_summary == "S1"
    assert pipeline.calls[0].messages == [f"m{i}" for i in range(21, 31)]
    db.refresh(chat)
    assert chat.summary == "S2"


def test_refresh_at_forty_uses_only_its_ten_message_delta(db):
    chat = make_chat(db, summary="S2")
    add_messages(db, chat.id, 40)
    set_cursor(db, chat, 30)

    service, pipeline = make_summary_service(db)
    service.update_summary(chat_id=chat.id)

    assert pipeline.calls[0].existing_summary == "S2"
    assert pipeline.calls[0].messages == [f"m{i}" for i in range(31, 41)]


def test_refresh_at_fifty_is_incremental(db):
    chat = make_chat(db, summary="S3")
    add_messages(db, chat.id, 50)
    set_cursor(db, chat, 40)

    service, pipeline = make_summary_service(db)
    service.update_summary(chat_id=chat.id)

    assert pipeline.calls[0].existing_summary == "S3"
    assert pipeline.calls[0].messages == [f"m{i}" for i in range(41, 51)]


def test_summary_delta_is_exactly_the_new_interval(db):
    chat = make_chat(db, summary="S1")
    add_messages(db, chat.id, 30)
    set_cursor(db, chat, 20)

    service, pipeline = make_summary_service(db)
    service.update_summary(chat_id=chat.id)

    assert len(pipeline.calls[0].messages) == settings.SUMMARY_UPDATE_INTERVAL


# --------------------------------------------------------------------------- #
# Pre-existing sessions
# --------------------------------------------------------------------------- #


def test_existing_long_session_without_summary_gets_full_history_catch_up(db):
    chat = make_chat(db)  # no summary at all
    add_messages(db, chat.id, 45)

    service, pipeline = make_summary_service(db)
    service.update_summary(chat_id=chat.id)

    assert len(pipeline.calls) == 1
    assert pipeline.calls[0].existing_summary is None
    assert pipeline.calls[0].messages == [f"m{i}" for i in range(1, 46)]


def test_existing_session_with_populated_summary_keeps_working(db):
    chat = make_chat(db, summary="OLD FULL-TRANSCRIPT SUMMARY")
    add_messages(db, chat.id, 34)
    set_cursor(db, chat, 30)

    service, pipeline = make_summary_service(db)
    service.update_summary(chat_id=chat.id)  # pending 4 -> not due yet
    assert pipeline.calls == []

    add_messages(db, chat.id, 6, start_index=34)  # now 40, pending 10
    service.update_summary(chat_id=chat.id)
    assert len(pipeline.calls) == 1
    assert pipeline.calls[0].existing_summary == "OLD FULL-TRANSCRIPT SUMMARY"
    assert pipeline.calls[0].messages == [f"m{i}" for i in range(31, 41)]


# --------------------------------------------------------------------------- #
# Failure / catch-up
# --------------------------------------------------------------------------- #


def test_summary_failure_preserves_existing_summary_and_does_not_raise(db):
    chat = make_chat(db, summary="S1")
    add_messages(db, chat.id, 30)
    set_cursor(db, chat, 20)

    service, pipeline = make_summary_service(db)
    pipeline.should_fail = True

    service.update_summary(chat_id=chat.id)  # must not raise

    db.refresh(chat)
    assert chat.summary == "S1"


def test_failed_boundary_is_recovered_by_a_later_catch_up(db):
    chat = make_chat(db, summary="S1")
    add_messages(db, chat.id, 30)
    set_cursor(db, chat, 20)

    service, pipeline = make_summary_service(db)

    # Boundary at 30 fails.
    pipeline.should_fail = True
    service.update_summary(chat_id=chat.id)
    db.refresh(chat)
    assert chat.summary == "S1"  # unchanged, cursor still at 20

    # Two turns later (count 32) the backend recovers: the delta must now
    # include the messages the failed boundary would have covered - nothing
    # is dropped.
    add_messages(db, chat.id, 2, start_index=30)
    pipeline.should_fail = False
    pipeline.next_result = "S2"
    service.update_summary(chat_id=chat.id)

    assert pipeline.calls[-1].existing_summary == "S1"
    assert pipeline.calls[-1].messages == [f"m{i}" for i in range(21, 33)]
    db.refresh(chat)
    assert chat.summary == "S2"


def test_f1_message_committed_during_generation_is_not_marked_covered(db):
    """F1: a turn that lands while the summary LLM call is running must not be
    counted as covered by the resulting summary -- it belongs in the next
    delta, not silently dropped."""

    chat = make_chat(db)
    add_messages(db, chat.id, 20)

    class _RacingPipeline(FakeSummaryPipeline):
        def generate_summary(self, *, existing_summary, conversation):
            # A new user turn is persisted mid-generation (strictly later
            # ``created_at`` than every message in the snapshot).
            db.add(
                ChatMessage(
                    chat_session_id=chat.id,
                    role=MessageRole.USER,
                    content="m21",
                    created_at=BASE_TIME + timedelta(minutes=20),
                )
            )
            db.commit()
            return super().generate_summary(
                existing_summary=existing_summary,
                conversation=conversation,
            )

    service, pipeline = make_summary_service(db, _RacingPipeline())
    service.update_summary(chat_id=chat.id)

    db.refresh(chat)
    assert chat.summary == "ROLLING SUMMARY"
    # The racing message was not part of the summarized delta ...
    assert pipeline.calls[0].messages == [f"m{i}" for i in range(1, 21)]

    # ... and the stored cursor does not mark it as covered.
    message_repo = MessageRepository(db)
    covered = message_repo.count_conversational_messages_before(
        chat_session_id=chat.id,
        timestamp=chat.summary_updated_at,
    )
    assert covered == 20

    # It is incorporated by the next delta rather than lost.
    add_messages(db, chat.id, 9, start_index=21)  # -> 30 conversational msgs
    pipeline.next_result = "S2"
    service.update_summary(chat_id=chat.id)
    assert pipeline.calls[-1].messages == [f"m{i}" for i in range(21, 31)]


def test_f2_stale_refresh_cannot_overwrite_newer_summary(db):
    """F2: an older/slower background refresh finishing after a newer one must
    not roll the summary or its cursor backwards."""

    chat = make_chat(db)
    add_messages(db, chat.id, 40)
    chat_repo = ChatRepository(db)

    newer_cursor = BASE_TIME + timedelta(minutes=39)  # created_at of m40
    older_cursor = BASE_TIME + timedelta(minutes=29)  # created_at of m30

    chat_repo.update_summary(
        chat_id=chat.id,
        summary="S-NEW",
        summarized_through=newer_cursor,
    )

    result = chat_repo.update_summary(
        chat_id=chat.id,
        summary="S-STALE",
        summarized_through=older_cursor,
    )

    assert result.summary == "S-NEW"
    db.refresh(chat)
    assert chat.summary == "S-NEW"
    assert chat.summary_updated_at == newer_cursor

    # A refresh landing exactly on the current cursor is also a no-op.
    chat_repo.update_summary(
        chat_id=chat.id,
        summary="S-EQUAL",
        summarized_through=newer_cursor,
    )
    db.refresh(chat)
    assert chat.summary == "S-NEW"


def test_empty_summary_result_is_ignored(db):
    chat = make_chat(db, summary="S1")
    add_messages(db, chat.id, 30)
    set_cursor(db, chat, 20)

    service, pipeline = make_summary_service(db)
    pipeline.next_result = "   "
    service.update_summary(chat_id=chat.id)

    db.refresh(chat)
    assert chat.summary == "S1"


# --------------------------------------------------------------------------- #
# Generation context window (AIPipeline)
# --------------------------------------------------------------------------- #


class _RecordingGeneration:
    def __init__(self) -> None:
        self.request: GenerationRequest | None = None

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        self.request = request
        return GenerationResponse(answer="ANSWER", citations=[])

    def stream(self, request: GenerationRequest):
        self.request = request
        yield "ANSWER"

    def citations_for(self, request, answer=None):
        return []


class _FakeLLM:
    def __init__(self) -> None:
        self.rewrite_messages = None

    def rewrite_query(self, *, messages):
        self.rewrite_messages = messages
        return "rewritten standalone query"


class _FakeRetrieval:
    def retrieve(self, *, query, user_id):
        return RetrievalResult(
            query=query,
            contexts=[
                RetrievedContext(
                    text="a retrieved chunk of context",
                    source="doc.pdf",
                    chunk_uuid=uuid4(),
                    retrieval_score=0.9,
                    reranker_score=0.9,
                )
            ],
            retrieval_latency=0.0,
        )


def make_pipeline():
    generation = _RecordingGeneration()
    llm = _FakeLLM()
    pipeline = AIPipeline(
        retrieval_service=_FakeRetrieval(),
        generation_service=generation,
        llm_service=llm,
    )
    return pipeline, generation, llm


def orm_conversation(count: int) -> list[ChatMessage]:
    messages: list[ChatMessage] = []
    for i in range(count):
        role = MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT
        if i == count - 1:
            role = MessageRole.USER  # current user turn
        messages.append(ChatMessage(role=role, content=f"m{i + 1}"))
    return messages


@pytest.mark.parametrize(
    "count, expected_history, expected_query",
    [
        (21, [f"m{i}" for i in range(11, 21)], "m21"),
        (22, [f"m{i}" for i in range(12, 22)], "m22"),
        (30, [f"m{i}" for i in range(20, 30)], "m30"),
        (31, [f"m{i}" for i in range(21, 31)], "m31"),
        (32, [f"m{i}" for i in range(22, 32)], "m32"),
        (41, [f"m{i}" for i in range(31, 41)], "m41"),
    ],
)
def test_generation_context_is_summary_plus_rolling_window(
    count, expected_history, expected_query
):
    pipeline, generation, _ = make_pipeline()

    pipeline.generate_response(
        conversation=orm_conversation(count),
        user_id=1,
        summary="ACTIVE SUMMARY",
    )

    request = generation.request
    assert request.summary == "ACTIVE SUMMARY"

    prompt = PromptBuilder().build(request)
    history = [m.content for m in prompt if m.content in expected_history]
    assert history == expected_history
    assert request.query == expected_query

    # The current user message is not duplicated inside the history window;
    # it appears only as the trailing user prompt.
    assert not any(m.content == expected_query for m in prompt[:-1])
    user_prompt = prompt[-1]
    assert user_prompt.role == MessageRole.USER
    assert expected_query in user_prompt.content


def test_full_history_used_before_first_summary():
    pipeline, generation, _ = make_pipeline()

    pipeline.generate_response(
        conversation=orm_conversation(12),
        user_id=1,
        summary=None,
    )

    contents = [m.content for m in generation.request.conversation]
    assert contents == [f"m{i}" for i in range(1, 13)]


def test_generation_history_bounded_for_very_long_conversation():
    pipeline, generation, _ = make_pipeline()

    pipeline.generate_response(
        conversation=orm_conversation(200),
        user_id=1,
        summary="ACTIVE SUMMARY",
    )

    prompt = PromptBuilder().build(generation.request)
    history_msgs = [
        m
        for m in prompt
        if m.role in (MessageRole.USER, MessageRole.ASSISTANT)
    ]
    # RECENT_MESSAGE_WINDOW history messages + the single trailing user prompt.
    assert len(history_msgs) <= settings.RECENT_MESSAGE_WINDOW + 1


def test_summary_text_not_duplicated_into_history():
    pipeline, generation, _ = make_pipeline()
    pipeline.generate_response(
        conversation=orm_conversation(40),
        user_id=1,
        summary="UNIQUE-SUMMARY-SENTINEL",
    )
    prompt = PromptBuilder().build(generation.request)
    hits = [m for m in prompt if "UNIQUE-SUMMARY-SENTINEL" in m.content]
    assert len(hits) == 1
    assert hits[0].role == MessageRole.SYSTEM


def test_retrieval_rewrite_keeps_its_own_independent_window():
    pipeline, generation, llm = make_pipeline()

    pipeline.generate_response(
        conversation=orm_conversation(40),
        user_id=1,
        summary="ACTIVE SUMMARY",
    )

    # Generation history is compressed to the recent window ...
    assert len(generation.request.conversation) <= settings.RECENT_MESSAGE_WINDOW + 1

    # ... but the retrieval-query rewrite still sees up to
    # QUERY_REWRITE_HISTORY_WINDOW messages.
    rewrite_user_prompt = llm.rewrite_messages[-1].content
    assert "m21" in rewrite_user_prompt  # 20 back from message 40
    assert "m20" not in rewrite_user_prompt
    assert "m1:" not in rewrite_user_prompt


def test_summary_not_injected_when_missing_even_past_threshold():
    """A pending/failed first summary must not trigger history truncation."""
    pipeline, generation, _ = make_pipeline()

    pipeline.generate_response(
        conversation=orm_conversation(40),
        user_id=1,
        summary=None,
    )

    assert generation.request.summary is None
    contents = [m.content for m in generation.request.conversation]
    assert contents == [f"m{i}" for i in range(1, 41)]  # full history preserved


# --------------------------------------------------------------------------- #
# ConversationService streaming / scheduling
# --------------------------------------------------------------------------- #


class _RecordingBackgroundTasks:
    def __init__(self) -> None:
        self.tasks: list[tuple] = []

    def add_task(self, func, *args, **kwargs):
        self.tasks.append((func, args, kwargs))


class _StreamingAIPipeline:
    def stream_response(self, *, conversation, user_id, summary=None):
        yield SimpleNamespace(text="hello ", citations=None)
        yield SimpleNamespace(text="world", citations=None)
        yield SimpleNamespace(text=None, citations=[])

    def generate_title(self, *, first_message):
        return "Title"


def make_conversation_service(db):
    chat_repo = ChatRepository(db)
    message_repo = MessageRepository(db)

    class _MsgSvc:
        def create_message(self, *, chat_id, current_user, message_data):
            msg = ChatMessage(
                chat_session_id=chat_id,
                role=MessageRole.USER,
                content=message_data.content,
                created_at=BASE_TIME + timedelta(minutes=999),
            )
            return message_repo.create(msg)

    summary_service, summary_pipeline = make_summary_service(db)

    service = ConversationService(
        chat_repository=chat_repo,
        message_repository=message_repo,
        message_service=_MsgSvc(),
        ai_pipeline=_StreamingAIPipeline(),
        conversation_summary_service=summary_service,
    )
    return service, summary_pipeline


def test_streaming_persists_exactly_one_assistant_message(db):
    chat = make_chat(db)
    add_messages(db, chat.id, 4)

    service, _ = make_conversation_service(db)
    background = _RecordingBackgroundTasks()

    events = list(
        service.stream_message(
            chat_id=chat.id,
            current_user=SimpleNamespace(id=1),
            message_data=SimpleNamespace(content="a new question"),
            background_tasks=background,
        )
    )

    assert any(e.citations is not None for e in events)
    repo = MessageRepository(db)
    assistant = [
        m
        for m in repo.get_conversational_messages(chat.id)
        if m.role == MessageRole.ASSISTANT
    ]
    # 2 original assistant messages + exactly 1 new one.
    assert assistant[-1].content == "hello world"
    assert len(assistant) == 3


def test_streaming_done_not_blocked_by_summary_generation(db):
    chat = make_chat(db)
    add_messages(db, chat.id, 40)

    service, summary_pipeline = make_conversation_service(db)
    background = _RecordingBackgroundTasks()

    list(
        service.stream_message(
            chat_id=chat.id,
            current_user=SimpleNamespace(id=1),
            message_data=SimpleNamespace(content="another question"),
            background_tasks=background,
        )
    )

    # The summary refresh was handed to background tasks, not run inline.
    assert summary_pipeline.calls == []
    assert len(background.tasks) == 1
    func, args, _ = background.tasks[0]
    assert func.__name__ == "run_summary_refresh"
    assert args == (chat.id,)
