from __future__ import annotations

from app.ai.pipeline import AIPipeline
from app.config.settings import settings
from app.database.session import SessionLocal
from app.dependencies.resources import (
    get_llm_resource,
    get_reranking_resource,
)
from app.generation.prompt_builder import PromptBuilder
from app.generation.service import GenerationService
from app.repositories.team_membership import TeamMembershipRepository
from app.repositories.user import UserRepository
from app.retrieval.access import AccessContext
from app.retrieval.service import RetrievalService
from app.reranking.service import RerankingService
from app.search.hybrid.service import HybridService
from app.services.llm import LLMService

from evaluation.fixtures.manager import FixtureManager
from evaluation.predictor import EvaluationPredictor
from evaluation.provider import LangSmithProvider


class EvaluationService:

    DATASET_NAME = "Astra Study Evaluation"

    def __init__(
        self,
        fixture_manager: FixtureManager,
        provider: LangSmithProvider,
    ) -> None:

        self._fixture_manager = fixture_manager
        self._provider = provider

        llm_service: LLMService = get_llm_resource()

        prompt_builder = PromptBuilder()

        hybrid_service = HybridService()

        reranking_service: RerankingService = (
            get_reranking_resource()
        )

        retrieval_service = RetrievalService(
            hybrid_service=hybrid_service,
            reranking_service=reranking_service,
        )

        generation_service = GenerationService(
            prompt_builder=prompt_builder,
            llm_service=llm_service,
        )

        self._pipeline = AIPipeline(
            retrieval_service=retrieval_service,
            generation_service=generation_service,
            llm_service=llm_service,
        )

    @staticmethod
    def _resolve_access(
        evaluation_user_id: int,
    ) -> AccessContext:
        """
        Build the real, database-backed AccessContext for the configured
        evaluation user.

        Opens a short-lived session (outside any request context, same
        pattern as ``run_summary_refresh``) purely to read the user's
        actual ``organisation_id``/``role`` and team memberships -- never
        fabricated. No write occurs.
        """

        db = SessionLocal()

        try:
            user = UserRepository(db).get_by_id(evaluation_user_id)

            if user is None:
                raise RuntimeError(
                    "Evaluation user "
                    f"(id={evaluation_user_id!r}) not found. "
                    "settings.EVALUATION_USER_ID must reference a real "
                    "users.id row."
                )

            team_ids = TeamMembershipRepository(db).get_team_ids_by_user_id(
                user.id,
            )

            return AccessContext(
                user_id=user.id,
                organisation_id=user.organisation_id,
                team_ids=tuple(team_ids),
                role=user.role,
            )

        finally:
            db.close()

    def sync_fixture(
        self,
        fixture_path: str,
    ) -> None:

        fixture = self._fixture_manager.load_fixture(
            fixture_path,
        )

        self._provider.sync_fixture(
            dataset_name=self.DATASET_NAME,
            fixture=fixture,
        )

    def run_experiment(
        self,
        *,
        evaluation_user_id: int,
        evaluators=None,
    ):

        access = self._resolve_access(evaluation_user_id)

        predictor = EvaluationPredictor(
            ai_pipeline=self._pipeline,
            access=access,
        )

        return self._provider.run_evaluation(
            predictor=predictor.predict,
            dataset_name=self.DATASET_NAME,
            experiment_prefix="astra-study",
            evaluators=evaluators,
            metadata={
                "chat_model": settings.OPENAI_CHAT_MODEL,
                "embedding_model": settings.EMBEDDING_MODEL,
            },
        )