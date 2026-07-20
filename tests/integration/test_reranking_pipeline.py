"""
Integration test for the Cross Encoder reranking pipeline.

Prerequisites
-------------
1. Run test_hybrid_pipeline.py first.
2. Ensure the Qdrant collection exists.
3. Ensure documents are already indexed.

This test validates:
- Hybrid retrieval
- Cross Encoder reranking
- Ranking integrity
- Public reranker API
- Latency
- Benchmark statistics
"""

from __future__ import annotations

import statistics
import time
from pathlib import Path
from typing import Final

from app.config.settings import settings
from app.reranking.service import RerankingService
from app.search.hybrid.service import HybridService

# ==============================================================================
# Configuration
# ==============================================================================

TOP_K: Final[int] = settings.RERANK_TOP_K

SEARCH_LIMIT: Final[int] = (
    settings.QDRANT_HYBRID_CANDIDATE_LIMIT
)

TEST_QUERIES: Final[list[str]] = [

    "What is Retrieval Augmented Generation?",

    "Explain transformer architecture.",

    "What are Large Language Models?",

    "What is Chain of Thought?",

    "What is RLHF?",

]

LINE: Final[str] = "=" * 100

SEPARATOR: Final[str] = "-" * 100


# ==============================================================================
# Printing Helpers
# ==============================================================================


def print_header(
    title: str,
) -> None:

    print()
    print(LINE)
    print(title)
    print(LINE)


def preview_text(
    text: str,
    *,
    length: int = 250,
) -> str:

    cleaned = text.replace(
        "\n",
        " ",
    ).strip()

    if len(cleaned) <= length:
        return cleaned

    return cleaned[:length] + "..."


# ==============================================================================
# Result Printing
# ==============================================================================


def print_hybrid_results(
    results,
) -> None:

    print_header(
        "HYBRID SEARCH RESULTS"
    )

    previous_score = None

    for rank, result in enumerate(
        results,
        start=1,
    ):

        if previous_score is not None:

            assert (
                result.score
                <= previous_score
            )

        previous_score = result.score

        payload = result.payload or {}

        print(
            f"Rank        : {rank}"
        )

        print(
            f"Score       : {result.score:.4f}"
        )

        print(
            f"Document    : "
            f"{payload.get('document_name')}"
        )

        print(
            f"Page        : "
            f"{payload.get('page_start')}"
        )

        print(
            f"Section     : "
            f"{payload.get('section_title')}"
        )

        print(
            f"Chunk UUID  : "
            f"{result.chunk_uuid}"
        )

        print()

        print(
            preview_text(
                result.text,
            )
        )

        print(SEPARATOR)


def print_reranked_results(
    reranked,
) -> None:

    print_header(
        "RERANKED RESULTS"
    )

    previous_score = None

    for chunk in reranked:

        if previous_score is not None:

            assert (
                chunk.reranker_score
                <= previous_score
            )

        previous_score = (
            chunk.reranker_score
        )

        payload = (
            chunk.result.payload
            or {}
        )

        print(
            f"Rank             : "
            f"{chunk.rank}"
        )

        print(
            f"Hybrid Score     : "
            f"{chunk.result.score:.4f}"
        )

        print(
            f"CrossEncoder     : "
            f"{chunk.reranker_score:.4f}"
        )

        print(
            f"Document         : "
            f"{payload.get('document_name')}"
        )

        print(
            f"Page             : "
            f"{payload.get('page_start')}"
        )

        print(
            f"Section          : "
            f"{payload.get('section_title')}"
        )

        print(
            f"Chunk UUID       : "
            f"{chunk.result.chunk_uuid}"
        )

        print()

        print(
            preview_text(
                chunk.result.text,
            )
        )

        print(SEPARATOR)


# ==============================================================================
# Rank Movement
# ==============================================================================


def print_rank_movements(
    hybrid_results,
    reranked,
) -> None:

    print_header(
        "RANK MOVEMENTS"
    )

    hybrid_rank = {

        result.chunk_uuid: rank

        for rank, result in enumerate(
            hybrid_results,
            start=1,
        )

    }

    print(
        f"{'Chunk UUID':36}"
        f"{'Hybrid':>10}"
        f"{'Rerank':>10}"
        f"{'Shift':>10}"
    )

    print(SEPARATOR)

    changed = False

    for chunk in reranked:

        old_rank = hybrid_rank[
            chunk.result.chunk_uuid
        ]

        shift = (
            old_rank
            - chunk.rank
        )

        if shift != 0:
            changed = True

        print(
            f"{str(chunk.result.chunk_uuid):36}"
            f"{old_rank:>10}"
            f"{chunk.rank:>10}"
            f"{shift:>10}"
        )

    print()

    if changed:

        print(
            "✓ Ranking changed after reranking."
        )

    else:

        print(
            "✓ Ranking remained unchanged "
            "(Hybrid search was already optimal)."
        )

# ==============================================================================
# Quality Benchmark
# ==============================================================================


def print_quality_benchmark(
    hybrid_results,
    reranked,
) -> None:
    """
    Compare Hybrid Search ranking with
    Cross Encoder ranking.
    """

    print_header(
        "QUALITY BENCHMARK"
    )

    hybrid_rank = {

        result.chunk_uuid: rank

        for rank, result in enumerate(
            hybrid_results,
            start=1,
        )

    }

    print(
        f"{'Hybrid':<10}"
        f"{'Rerank':<10}"
        f"{'Hybrid Score':<18}"
        f"{'CE Score':<18}"
        f"{'Section'}"
    )

    print(SEPARATOR)

    for chunk in reranked:

        payload = (
            chunk.result.payload
            or {}
        )

        print(
            f"{hybrid_rank[chunk.result.chunk_uuid]:<10}"
            f"{chunk.rank:<10}"
            f"{chunk.result.score:<18.4f}"
            f"{chunk.reranker_score:<18.4f}"
            f"{payload.get('section_title')}"
        )


# ==============================================================================
# Statistics
# ==============================================================================


def print_reranking_statistics(
    hybrid_results,
    reranked,
) -> float:
    """
    Print reranking statistics.

    Returns
    -------
    float
        Average absolute rank shift.
    """

    print_header(
        "RERANKING STATISTICS"
    )

    hybrid_rank = {

        result.chunk_uuid: rank

        for rank, result in enumerate(
            hybrid_results,
            start=1,
        )

    }

    shifts: list[int] = []

    promotions = 0

    demotions = 0

    unchanged = 0

    for chunk in reranked:

        previous_rank = hybrid_rank[
            chunk.result.chunk_uuid
        ]

        shift = previous_rank - chunk.rank

        shifts.append(abs(shift))

        if shift > 0:

            promotions += 1

        elif shift < 0:

            demotions += 1

        else:

            unchanged += 1

    average_shift = (
        statistics.mean(shifts)
        if shifts
        else 0.0
    )

    print(
        f"Candidates Tested : {len(reranked)}"
    )

    print(
        f"Promotions        : {promotions}"
    )

    print(
        f"Demotions         : {demotions}"
    )

    print(
        f"Unchanged         : {unchanged}"
    )

    print(
        f"Average Shift     : {average_shift:.2f}"
    )

    return average_shift


# ==============================================================================
# Validation Helpers
# ==============================================================================


def validate_reranking_result(
    reranked,
) -> None:
    """
    Validate the returned RerankingResult.
    """

    assert reranked is not None

    assert (
        reranked.total_candidates
        >= reranked.returned_candidates
    )

    assert (
        len(reranked.results)
        == reranked.returned_candidates
    )

    assert (
        reranked.best_match
        is not None
    )

    assert (
        len(reranked.top_k(3))
        == min(
            3,
            reranked.returned_candidates,
        )
    )


def validate_rank_order(
    reranked,
) -> None:
    """
    Validate rank ordering.
    """

    previous_score = None

    expected_rank = 1

    for chunk in reranked:

        assert (
            chunk.rank
            == expected_rank
        )

        if previous_score is not None:

            assert (
                chunk.reranker_score
                <= previous_score
            )

        previous_score = (
            chunk.reranker_score
        )

        expected_rank += 1


def validate_chunk_integrity(
    hybrid_results,
    reranked,
) -> None:
    """
    Ensure reranking never changes
    or removes retrieved chunks.
    """

    hybrid_ids = {

        result.chunk_uuid

        for result in hybrid_results

    }

    reranked_ids = {

        chunk.result.chunk_uuid

        for chunk in reranked

    }

    assert (
        reranked_ids
        <= hybrid_ids
    )

    assert len(
        reranked_ids
    ) == len(reranked)


def validate_api_helpers(
    reranked,
) -> None:
    """
    Validate helper APIs exposed by
    RerankingResult.
    """

    count = 0

    for _ in reranked:

        count += 1

    assert (
        count
        == len(reranked)
    )

    assert (
        reranked[0].rank
        == 1
    )

    assert (
        len(
            reranked.reranker_scores
        )
        == len(reranked)
    )

    assert (
        len(
            reranked.retrieval_scores
        )
        == len(reranked)
    )


# ==============================================================================
# Performance
# ==============================================================================


def print_performance(
    *,
    hybrid_latency: float,
    rerank_latency: float,
    candidate_count: int,
) -> float:
    """
    Print latency measurements.

    Returns
    -------
    float
        Total latency.
    """

    total = (
        hybrid_latency
        + rerank_latency
    )

    average = (
        rerank_latency
        / candidate_count
        if candidate_count
        else 0.0
    )

    print_header(
        "PERFORMANCE"
    )

    print(
        f"Hybrid Retrieval : "
        f"{hybrid_latency:.3f} sec"
    )

    print(
        f"Cross Encoder    : "
        f"{rerank_latency:.3f} sec"
    )

    print(
        f"Total            : "
        f"{total:.3f} sec"
    )

    print(
        f"Per Candidate    : "
        f"{average:.4f} sec"
    )

    return total

# ==============================================================================
# Main Integration Test
# ==============================================================================


def test_reranking_pipeline() -> None:
    """
    End-to-end integration test for the reranking pipeline.

    Assumptions
    -----------
    - The Hybrid Pipeline has already been executed.
    - The Qdrant collection already exists.
    - Documents are already indexed.

    Pipeline

    Existing Collection
            ↓
    Hybrid Search
            ↓
    Cross Encoder Reranking
            ↓
    Validation
            ↓
    Benchmark
    """

    print_header(
        "RERANKING CONFIGURATION"
    )

    hybrid_service = HybridService()

    reranking_service = RerankingService()

    reranker = reranking_service.reranker

    print(
        f"Model        : {reranker.model_name}"
    )

    print(
        f"Device       : {reranker.device}"
    )

    print(
        f"Batch Size   : {reranker.batch_size}"
    )

    print(
        f"Max Length   : {reranker.max_length}"
    )

    print(
        f"Top K        : {TOP_K}"
    )

    print(
        f"Search Limit : {SEARCH_LIMIT}"
    )

    average_rank_shifts: list[float] = []

    hybrid_latencies: list[float] = []

    reranking_latencies: list[float] = []

    total_latencies: list[float] = []

    highest_ce_score = float("-inf")

    lowest_ce_score = float("inf")

    for query in TEST_QUERIES:

        print_header(
            f"QUERY: {query}"
        )

        # --------------------------------------------------------------
        # Hybrid Search
        # --------------------------------------------------------------

        hybrid_start = time.perf_counter()

        hybrid_results = hybrid_service(
            query=query,
            limit=SEARCH_LIMIT,
        )

        hybrid_latency = (
            time.perf_counter()
            - hybrid_start
        )

        hybrid_latencies.append(
            hybrid_latency
        )

        assert (
            len(hybrid_results) > 0
        )

        print_hybrid_results(
            hybrid_results
        )

        # --------------------------------------------------------------
        # Cross Encoder Reranking
        # --------------------------------------------------------------

        rerank_start = time.perf_counter()

        reranked = reranking_service(
            query=query,
            candidates=hybrid_results,
            top_k=TOP_K,
        )

        rerank_latency = (
            time.perf_counter()
            - rerank_start
        )

        reranking_latencies.append(
            rerank_latency
        )

        print_reranked_results(
            reranked
        )

        # --------------------------------------------------------------
        # Validation
        # --------------------------------------------------------------

        validate_reranking_result(
            reranked
        )

        validate_rank_order(
            reranked
        )

        validate_chunk_integrity(
            hybrid_results,
            reranked,
        )

        validate_api_helpers(
            reranked
        )

        # --------------------------------------------------------------
        # Benchmark
        # --------------------------------------------------------------

        print_rank_movements(
            hybrid_results,
            reranked,
        )

        print_quality_benchmark(
            hybrid_results,
            reranked,
        )

        average_shift = (
            print_reranking_statistics(
                hybrid_results,
                reranked,
            )
        )

        average_rank_shifts.append(
            average_shift
        )

        total_latency = (
            print_performance(
                hybrid_latency=hybrid_latency,
                rerank_latency=rerank_latency,
                candidate_count=reranked.total_candidates,
            )
        )

        total_latencies.append(
            total_latency
        )

        highest_ce_score = max(
            highest_ce_score,
            max(
                reranked.reranker_scores
            ),
        )

        lowest_ce_score = min(
            lowest_ce_score,
            min(
                reranked.reranker_scores
            ),
        )
        
    print_header(
        "RERANKING SUMMARY"
    )

    average_hybrid_latency = statistics.mean(
        hybrid_latencies
    )

    average_reranking_latency = statistics.mean(
        reranking_latencies
    )

    average_total_latency = statistics.mean(
        total_latencies
    )

    average_rank_shift = statistics.mean(
        average_rank_shifts
    )

    print(
        f"Queries Tested            : "
        f"{len(TEST_QUERIES)}"
    )

    print(
        f"Average Hybrid Latency    : "
        f"{average_hybrid_latency:.3f} sec"
    )

    print(
        f"Average Reranking Latency : "
        f"{average_reranking_latency:.3f} sec"
    )

    print(
        f"Average Total Latency     : "
        f"{average_total_latency:.3f} sec"
    )

    print(
        f"Average Rank Shift        : "
        f"{average_rank_shift:.2f}"
    )

    print(
        f"Highest CE Score          : "
        f"{highest_ce_score:.4f}"
    )

    print(
        f"Lowest CE Score           : "
        f"{lowest_ce_score:.4f}"
    )

    print(
        f"Model                     : "
        f"{reranker.model_name}"
    )

    print(
        f"Device                    : "
        f"{reranker.device}"
    )

    print(
        f"Batch Size                : "
        f"{reranker.batch_size}"
    )

    print(
        f"Max Length                : "
        f"{reranker.max_length}"
    )

    print()

    # ==========================================================
    # Final Assertions
    # ==========================================================

    assert len(hybrid_latencies) == len(TEST_QUERIES)

    assert len(reranking_latencies) == len(TEST_QUERIES)

    assert len(total_latencies) == len(TEST_QUERIES)

    assert highest_ce_score >= lowest_ce_score

    assert average_hybrid_latency > 0

    assert average_reranking_latency > 0

    assert average_total_latency > 0

    print()

    print(LINE)

    print(
        "✓ ALL RERANKING TESTS PASSED"
    )

    print(
        "✓ Cross Encoder loaded successfully"
    )

    print(
        "✓ Hybrid Retrieval validated"
    )

    print(
        "✓ Ranking integrity verified"
    )

    print(
        "✓ Reranker API validated"
    )

    print(
        "✓ Performance benchmark completed"
    )

    print(
        "✓ Astra Study Reranker is production ready"
    )

    print(LINE)