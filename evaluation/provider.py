from __future__ import annotations

import logging

from langsmith import Client
from langsmith.schemas import Dataset

from app.config.settings import settings

logger = logging.getLogger(__name__)


class LangSmithProvider:
    """
    Thin wrapper around the LangSmith SDK.

    Responsibilities
    ----------------
    - Initialize LangSmith client.
    - Perform SDK operations.
    - No business logic.
    """

    def __init__(self) -> None:

        self._client = Client(
            api_key=settings.LANGSMITH_API_KEY,
            api_url=settings.LANGSMITH_ENDPOINT,
        )

    @property
    def client(self) -> Client:
        return self._client

    # ---------------------------------------------------------
    # Dataset Operations
    # ---------------------------------------------------------

    def list_datasets(self) -> list[Dataset]:

        datasets = list(
            self._client.list_datasets()
        )

        logger.info(
            "Retrieved %d dataset(s).",
            len(datasets),
        )

        return datasets

    def get_dataset_by_name(
        self,
        name: str,
    ) -> Dataset | None:

        for dataset in self._client.list_datasets():

            if dataset.name == name:
                return dataset

        return None

    def create_dataset(
        self,
        *,
        name: str,
        description: str,
    ) -> Dataset:

        logger.info(
            "Creating LangSmith dataset '%s'.",
            name,
        )

        return self._client.create_dataset(
            dataset_name=name,
            description=description,
        )

    # ---------------------------------------------------------
    # Example Operations
    # ---------------------------------------------------------

    def list_examples(
        self,
        *,
        dataset_id: str,
    ) -> list:

        examples = list(
            self._client.list_examples(
                dataset_id=dataset_id,
            )
        )

        logger.info(
            "Retrieved %d example(s) from dataset '%s'.",
            len(examples),
            dataset_id,
        )

        return examples

    def create_example(
        self,
        *,
        dataset_id: str,
        example_id: str,
        question: str,
    ):

        logger.info(
            "Creating example '%s'.",
            example_id,
        )

        return self._client.create_example(
            dataset_id=dataset_id,
            inputs={
                "question": question,
            },
            metadata={
                "fixture_id": example_id,
            },
        )