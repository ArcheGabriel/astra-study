from __future__ import annotations

import logging
from pathlib import Path

import yaml

from evaluation.schemas import EvaluationFixture

logger = logging.getLogger(__name__)


class FixtureManager:
    """
    Loads evaluation fixtures from YAML files.

    Responsibilities
    ----------------
    - Read YAML fixtures.
    - Validate them using Pydantic.
    - Return strongly typed EvaluationFixture objects.

    This class has no knowledge of LangSmith.
    """

    def __init__(
        self,
        fixtures_directory: str | Path = "evaluation/fixtures",
    ) -> None:

        self._fixtures_directory = Path(
            fixtures_directory
        )

    def load_fixture(
        self,
        filename: str,
    ) -> EvaluationFixture:
        """
        Load a single evaluation fixture.

        Parameters
        ----------
        filename
            YAML filename.

        Returns
        -------
        EvaluationFixture
        """

        path = self._fixtures_directory / filename

        if not path.exists():

            raise FileNotFoundError(
                f"Fixture '{filename}' not found."
            )

        logger.info(
            "Loading fixture '%s'.",
            path,
        )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = yaml.safe_load(file)

        fixture = EvaluationFixture.model_validate(
            data
        )

        logger.info(
            (
                "Loaded fixture '%s' "
                "containing %d example(s)."
            ),
            fixture.name,
            len(fixture.examples),
        )

        return fixture

    def list_fixtures(
        self,
    ) -> list[Path]:
        """
        List all available fixture files.
        """

        return sorted(
            self._fixtures_directory.glob("*.yaml")
        )