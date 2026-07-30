from __future__ import annotations

from app.config.settings import settings

from evaluation.evaluators import (
    answer_length,
    citation_count,
    exact_match,
)
from evaluation.fixtures.manager import FixtureManager
from evaluation.provider import LangSmithProvider
from evaluation.service import EvaluationService


FIXTURE = "llm_fundamentals.yaml"


def main() -> None:

    print("=" * 70)
    print("Astra Study Evaluation")
    print("=" * 70)

    fixture_manager = FixtureManager()

    provider = LangSmithProvider()

    service = EvaluationService(
        fixture_manager=fixture_manager,
        provider=provider,
    )

    print("\nSynchronizing LangSmith dataset...\n")

    service.sync_fixture(
        fixture_path=FIXTURE,
    )

    print("✓ Dataset synchronized.\n")

    print("Running evaluation...\n")

    experiment = service.run_experiment(
        evaluation_user_id=settings.EVALUATION_USER_ID,
        evaluators=[
            exact_match,
            answer_length,
            citation_count,
        ],
    )

    print("\n✓ Evaluation completed.\n")

    print(experiment)


if __name__ == "__main__":
    main()