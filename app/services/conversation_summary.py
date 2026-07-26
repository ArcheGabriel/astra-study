from app.ai.pipeline import AIPipeline
from app.models.chat import ChatSession
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository


class ConversationSummaryService:
    """
    Maintains an AI-generated summary for long conversations.

    A summary is generated only after a configurable number of
    conversation messages have been exchanged.
    """

    SUMMARY_TRIGGER_MESSAGE_COUNT = 20

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

    def update_summary(
        self,
        *,
        chat: ChatSession,
    ) -> None:
        """
        Generate or refresh the conversation summary.

        The entire conversation is summarized. This keeps the
        implementation simple and accurate. We can optimize to
        rolling summaries later if conversations become extremely
        large.
        """

        conversation = self.message_repository.get_by_chat_session(
            chat.id,
        )

        if len(conversation) < self.SUMMARY_TRIGGER_MESSAGE_COUNT:
            return

        summary = self.ai_pipeline.generate_summary(
            existing_summary=chat.summary,
            conversation=conversation,
        )

        self.chat_repository.update_summary(
            chat_id=chat.id,
            summary=summary,
        )