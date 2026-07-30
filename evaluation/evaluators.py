from __future__ import annotations

from typing import Any


def exact_match(
    outputs: dict,
    reference_outputs: dict,
) -> dict[str, Any]:
    """
    Exact answer match.

    Useful as a fast deterministic baseline.
    """

    predicted = (
        outputs.get("answer", "")
        .strip()
        .lower()
    )

    expected = (
        reference_outputs.get("answer", "")
        .strip()
        .lower()
    )

    return {
        "key": "exact_match",
        "score": float(predicted == expected),
    }


def answer_length(
    outputs: dict,
) -> dict[str, Any]:
    """
    Records answer length.

    Helpful for spotting prompt regressions.
    """

    answer = outputs.get("answer", "")

    return {
        "key": "answer_length",
        "score": len(answer),
    }


def citation_count(
    outputs: dict,
) -> dict[str, Any]:
    """
    Counts returned citations.
    """

    citations = outputs.get(
        "citations",
        [],
    )

    return {
        "key": "citation_count",
        "score": len(citations),
    }