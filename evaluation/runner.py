from __future__ import annotations

from evaluation.service import EvaluationService


def main() -> None:

    service = EvaluationService()

    result = service.sync_fixture(
        "llm_fundamentals.yaml",
    )

    print()

    print("Evaluation Synchronization")
    print("--------------------------")

    print(
        f"Dataset          : {result['dataset_name']}"
    )

    print(
        f"Fixture Examples : {result['total_examples']}"
    )

    print(
        f"Uploaded         : {result['uploaded']}"
    )

    print(
        f"Skipped          : {result['skipped']}"
    )

    print()


if __name__ == "__main__":
    main()