from __future__ import annotations

from langsmith.schemas import Dataset

from evaluation.fixtures.manager import FixtureManager
from evaluation.provider import LangSmithProvider


class EvaluationService:
    """
    Evaluation application service.

    Responsibilities
    ----------------
    - Orchestrate evaluation workflows.
    - Coordinate FixtureManager and LangSmithProvider.
    - Contain business logic only.
    """

    DATASET_NAME = "Astra Study Evaluation"

    DATASET_DESCRIPTION = (
        "Regression dataset used to evaluate "
        "Astra Study RAG responses."
    )

    def __init__(self) -> None:

        self._provider = LangSmithProvider()
        self._fixture_manager = FixtureManager()

    # ---------------------------------------------------------
    # Dataset Operations
    # ---------------------------------------------------------

    def list_datasets(self):

        return self._provider.list_datasets()

    def ensure_dataset(self) -> Dataset:

        dataset = self._provider.get_dataset_by_name(
            self.DATASET_NAME,
        )

        if dataset:
            return dataset

        return self._provider.create_dataset(
            name=self.DATASET_NAME,
            description=self.DATASET_DESCRIPTION,
        )

    # ---------------------------------------------------------
    # Example Operations
    # ---------------------------------------------------------

    def list_examples(
        self,
        dataset_id: str,
    ):

        return self._provider.list_examples(
            dataset_id=dataset_id,
        )

    def create_example(
        self,
        *,
        dataset_id: str,
        example_id: str,
        question: str,
    ):

        return self._provider.create_example(
            dataset_id=dataset_id,
            example_id=example_id,
            question=question,
        )

    # ---------------------------------------------------------
    # Synchronization
    # ---------------------------------------------------------

    def sync_fixture(
        self,
        filename: str,
    ) -> dict:

        fixture = self._fixture_manager.load_fixture(
            filename,
        )

        dataset = self.ensure_dataset()

        remote_examples = self.list_examples(
            dataset.id,
        )

        remote_fixture_ids = {
            (
                example.metadata or {}
            ).get(
                "fixture_id"
            )
            for example in remote_examples
        }

        uploaded = 0
        skipped = 0

        for example in fixture.examples:

            if example.id in remote_fixture_ids:

                skipped += 1
                continue

            self.create_example(
                dataset_id=dataset.id,
                example_id=example.id,
                question=example.question,
            )

            uploaded += 1

        return {
            "dataset_name": dataset.name,
            "total_examples": len(
                fixture.examples
            ),
            "uploaded": uploaded,
            "skipped": skipped,
        }