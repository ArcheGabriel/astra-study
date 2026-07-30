from __future__ import annotations

from dataclasses import asdict

from app.ai.pipeline import AIPipeline
from app.ai.schemas import AIResponse
from app.enums.message import MessageRole
from app.models.message import ChatMessage


class EvaluationPredictor:
    """
    Executes Astra Study's production AI pipeline for LangSmith evaluation.

    This bypasses ConversationService and ChatService so that only the
    AI pipeline is evaluated.

    No database writes occur.
    """

    def __init__(
        self,
        *,
        ai_pipeline: AIPipeline,
        evaluation_user_id: int,
    ) -> None:

        self._pipeline = ai_pipeline
        self._user_id = evaluation_user_id

    def predict(
        self,
        inputs: dict,
    ) -> dict:
        """
        Executes the production AI pipeline for a single evaluation example.
        """

        question = inputs["question"]

        conversation = [
            ChatMessage(
                chat_session_id=0,
                role=MessageRole.USER,
                content=question,
            )
        ]

        response: AIResponse = self._pipeline.generate_response(
            conversation=conversation,
            user_id=self._user_id,
            summary=None,
        )

        return {
            "answer": response.answer,
            "citations": [
                asdict(citation)
                for citation in response.citations
            ],
        }