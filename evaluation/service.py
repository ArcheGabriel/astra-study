from __future__ import annotations

from app.ai.pipeline import AIPipeline
from app.config.settings import settings
from app.dependencies.resources import (
    get_llm_resource,
    get_reranking_resource,
)
from app.generation.prompt_builder import PromptBuilder
from app.generation.service import GenerationService
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

        predictor = EvaluationPredictor(
            ai_pipeline=self._pipeline,
            evaluation_user_id=evaluation_user_id,
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