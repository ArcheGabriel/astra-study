import logging

from langsmith import traceable

from app.ai.pipeline import AIPipeline
from app.config.settings import settings
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository

logger = logging.getLogger(__name__)


class ConversationSummaryService:
    """
    Maintains a rolling AI-generated summary for long conversations.

    Lifecycle
    ---------
    - Nothing happens until a conversation reaches
      ``settings.INITIAL_SUMMARY_THRESHOLD`` conversational (user + assistant)
      messages. The first summary then covers messages 1..threshold.
    - After that the summary is refreshed every
      ``settings.SUMMARY_UPDATE_INTERVAL`` further messages. Each refresh feeds
      the *previous* summary plus only the newly-accumulated messages to the
      LLM -- the whole transcript is never re-summarized.
    - "How far the current summary has got" is derived from
      ``chat_sessions.summary_updated_at`` versus message ``created_at`` (no
      extra schema). If a refresh fails or is skipped, the pending-message
      count simply keeps growing and the next turn catches up, so a failed
      boundary cannot silently drop conversation context.
    """

    def __init__(
        self,
        *,
        chat_repository: ChatRepository,
        message_repository: MessageRepository,
        ai_pipeline: AIPipeline,
    ) -> None:
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.ai_pipeline = ai_pipeline

    @traceable(
        name="Update Conversation Summary",
        run_type="chain",
    )
    def update_summary(
        self,
        *,
        chat_id: int,
    ) -> None:
        """
        Generate or refresh the conversation summary if it is due.

        Safe to call after every turn: it is a no-op unless the conversation
        has crossed the initial threshold and at least one update interval of
        messages is not yet reflected in the stored summary.
        """

        chat = self.chat_repository.get_by_id(chat_id)

        if chat is None:
            return

        conversation = self.message_repository.get_conversational_messages(
            chat_id,
        )

        message_count = len(conversation)

        if message_count < settings.INITIAL_SUMMARY_THRESHOLD:
            return

        covered = self._covered_message_count(chat)
        pending = message_count - covered

        # ``covered == 0`` means either the first summary has never been
        # generated or an existing (pre-feature) conversation has no summary
        # yet -- in both cases summarize everything so earlier context is not
        # lost. Otherwise wait until a full interval of new messages exists.
        is_due = (
            covered == 0
            or pending >= settings.SUMMARY_UPDATE_INTERVAL
        )

        if not is_due:
            return

        existing_summary = chat.summary or None

        if covered == 0:
            delta = conversation
        else:
            delta = conversation[covered:]

        # The cursor must reflect the content actually summarized, not the
        # wall-clock time the LLM call happens to finish. Pin it to the
        # ``created_at`` of the last message fed to the summary: any message
        # committed *after* this snapshot (e.g. while the LLM call is running,
        # or by a concurrent turn) then has a strictly later ``created_at`` and
        # is correctly left for the next delta rather than silently marked as
        # covered. ``delta`` is non-empty here (message_count >= threshold).
        summarized_through = delta[-1].created_at

        try:
            summary = self.ai_pipeline.generate_summary(
                existing_summary=existing_summary,
                conversation=delta,
            )
        except Exception:
            logger.exception(
                "Conversation summary generation failed "
                "(chat_id=%s, message_count=%s, covered=%s). "
                "Existing summary preserved; a later turn will retry.",
                chat_id,
                message_count,
                covered,
            )
            return

        if not summary or not summary.strip():
            logger.warning(
                "Conversation summary generation returned an empty result "
                "(chat_id=%s); existing summary preserved.",
                chat_id,
            )
            return

        # Re-fetch immediately before writing so a concurrent turn's update is
        # not clobbered with stale data. ``update_summary`` also refuses to
        # move the cursor backwards, so an older/slower refresh cannot
        # overwrite a newer summary.
        self.chat_repository.update_summary(
            chat_id=chat_id,
            summary=summary.strip(),
            summarized_through=summarized_through,
        )

    def _covered_message_count(
        self,
        chat,
    ) -> int:
        """
        How many conversational messages the stored summary already reflects.
        """

        if not chat.summary or chat.summary_updated_at is None:
            return 0

        return self.message_repository.count_conversational_messages_before(
            chat_session_id=chat.id,
            timestamp=chat.summary_updated_at,
        )


def run_summary_refresh(chat_id: int) -> None:
    """
    Background entry point for refreshing a conversation summary.

    Runs outside the request/response cycle (FastAPI ``BackgroundTasks``) with
    its own database session so it never touches the request-scoped session and
    never delays the user-facing response or the SSE ``done`` event.
    """

    from app.database.session import SessionLocal
    from app.dependencies.services import build_conversation_summary_service

    db = SessionLocal()

    try:
        service = build_conversation_summary_service(db)
        service.update_summary(chat_id=chat_id)
    except Exception:
        logger.exception(
            "Background conversation summary refresh failed (chat_id=%s).",
            chat_id,
        )
    finally:
        db.close()
