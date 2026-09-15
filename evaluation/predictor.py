from __future__ import annotations

from dataclasses import asdict

from app.ai.pipeline import AIPipeline
from app.ai.schemas import AIResponse
from app.enums.message import MessageRole
from app.enums.organisation import OrgRole
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

        # The evaluation harness is Qdrant/LangSmith/fixture-based only: it
        # has no database session and no real Organisation/User row to look
        # up (settings.EVALUATION_USER_ID is itself just a Qdrant payload
        # user_id stamped onto fixture chunks, not a guaranteed users.id).
        #
        # organisation_id below is therefore a PLACEHOLDER, not real data --
        # it reuses the evaluation user id purely so AccessContext.__post_init__
        # accepts an int. It is harmless today only because RBAC-5B's Qdrant
        # filter never reads organisation_id (see DenseRepository.hybrid_search).
        # It MUST be replaced with a real, database-backed organisation id --
        # or the evaluation harness must gain a documented evaluation-tenant
        # concept -- before RBAC-5C adds organisation-scoped Qdrant filtering;
        # otherwise evaluation retrieval will silently filter against a
        # non-existent organisation and return zero candidates.
        access = AccessContext(
            user_id=self._user_id,
            organisation_id=self._user_id,  # PLACEHOLDER -- see comment above
            team_ids=(),
            role=OrgRole.MEMBER,
        )

        response: AIResponse = self._pipeline.generate_response(
            conversation=conversation,
            access=access,
            summary=None,
        )

        return {
            "answer": response.answer,
            "citations": [
                asdict(citation)
                for citation in response.citations
            ],
        }