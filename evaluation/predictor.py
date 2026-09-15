from __future__ import annotations

from dataclasses import asdict

from app.ai.pipeline import AIPipeline
from app.ai.schemas import AIResponse
from app.enums.message import MessageRole
from app.models.message import ChatMessage
from app.retrieval.access import AccessContext

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
        access: AccessContext,
    ) -> None:
        """
        ``access`` is resolved once from the real database-backed
        User/TeamMembership rows by ``EvaluationService`` -- see
        ``EvaluationService._resolve_access`` -- never fabricated here.
        """

        self._pipeline = ai_pipeline
        self._access = access

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
            access=self._access,
            summary=None,
        )

        return {
            "answer": response.answer,
            "citations": [
                asdict(citation)
                for citation in response.citations
            ],
        }