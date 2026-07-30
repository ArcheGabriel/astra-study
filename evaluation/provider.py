from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from langsmith import Client
from langsmith.evaluation import evaluate

from app.config.settings import settings

from evaluation.schemas.fixture import EvaluationFixture


class LangSmithProvider:
    """
    Handles all LangSmith interactions.
    """

    def __init__(self) -> None:
        self._client = Client(
            api_key=settings.LANGSMITH_API_KEY,
            api_url=settings.LANGSMITH_ENDPOINT,
        )

    # ------------------------------------------------------------------
    # Dataset
    # ------------------------------------------------------------------

    def _get_dataset(
        self,
        dataset_name: str,
    ):
        for dataset in self._client.list_datasets():
            if dataset.name == dataset_name:
                return dataset

        return self._client.create_dataset(
            dataset_name=dataset_name,
        )

    # ------------------------------------------------------------------
    # Synchronization
    # ------------------------------------------------------------------

    def sync_fixture(
        self,
        *,
        dataset_name: str,
        fixture: EvaluationFixture,
    ) -> None:

        dataset = self._get_dataset(
            dataset_name,
        )

        existing_examples = list(
            self._client.list_examples(
                dataset_id=dataset.id,
            )
        )

        existing_fixture_ids = {
            (example.metadata or {}).get("fixture_id")
            for example in existing_examples
        }

        for example in fixture.examples:

            if example.id in existing_fixture_ids:
                continue

            self._client.create_example(
                dataset_id=dataset.id,
                inputs={
                    "question": example.question,
                },
                outputs={
                    "answer": example.answer,
                },
                metadata={
                    "fixture_id": example.id,
                    "category": example.category,
                    "difficulty": example.difficulty,
                },
            )

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def run_evaluation(
        self,
        *,
        predictor,
        dataset_name: str,
        experiment_prefix: str,
        evaluators=None,
        metadata=None,
        max_concurrency: int = 5,
    ):
        """
        Execute a LangSmith evaluation experiment.
        """

        return evaluate(
            predictor,  # <-- positional argument
            data=dataset_name,
            evaluators=evaluators or [],
            experiment_prefix=experiment_prefix,
            metadata=metadata or {},
            max_concurrency=max_concurrency,
            client=self._client,
        )