from __future__ import annotations

import logging
from pprint import pprint
from time import perf_counter

from app.generation.models import GenerationRequest
from app.generation.prompt_builder import PromptBuilder
from app.generation.service import GenerationService
from app.retrieval.service import RetrievalService
from app.reranking.service import RerankingService
from app.search.hybrid.service import HybridService
from app.services.llm import LLMService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ============================================================================
# Change this query while validating the generation module.
# ============================================================================
#QUERY = "What is Flash Attention?"
#QUERY = "Explain RLHF."
#QUERY = "What are LLM scaling laws?"
#QUERY = "Compare T5 and GPT-3."
QUERY = "Who won the FIFA World Cup 2022?"


def print_results(
    request: GenerationRequest,
    answer: str,
    latency: float,
) -> None:

    print("\n" + "=" * 100)
    print("GENERATION PIPELINE RESULTS")
    print("=" * 100)

    print("\nQuestion")
    print("-" * 100)
    print(request.query)

    print("\nRetrieval Summary")
    print("-" * 100)
    print(f"Contexts Returned : {len(request.retrieval)}")
    print(f"Sources           : {request.retrieval.sources}")
    print(f"Pages             : {request.retrieval.pages}")
    print(f"Sections          : {request.retrieval.sections}")

    print("\n" + "=" * 100)
    print("RETRIEVED CONTEXTS")
    print("=" * 100)

    for index, context in enumerate(request.retrieval, start=1):

        print(f"\nContext #{index}")

        print("-" * 100)

        print(f"Source            : {context.source}")
        print(f"Page              : {context.page}")
        print(f"Section           : {context.section}")

        print(
            f"Retrieval Score   : "
            f"{context.retrieval_score:.4f}"
        )

        print(
            f"Reranker Score    : "
            f"{context.reranker_score:.4f}"
        )

        preview = context.text.replace("\n", " ")

        if len(preview) > 1000:
            preview = preview[:1000] + "..."

        print("\nContext Preview")
        print("-" * 100)
        print(preview)

    print("\n" + "=" * 100)
    print("GENERATED ANSWER")
    print("=" * 100)

    print(answer)

    print("\n" + "=" * 100)

    print("GENERATION METRICS")
    print("=" * 100)

    print(f"Answer Length     : {len(answer)} characters")
    print(f"Generation Time   : {latency:.2f} seconds")

    print("=" * 100)


def test_generation_pipeline() -> None:
    """
    Integration Test

    Query
        ↓
    Hybrid Search
        ↓
    CrossEncoder Reranking
        ↓
    RetrievalService
        ↓
    PromptBuilder
        ↓
    LLMService
        ↓
    GenerationService
    """

    #
    # Retrieval
    #
    hybrid_service = HybridService()

    reranking_service = RerankingService()

    retrieval_service = RetrievalService(
        hybrid_service=hybrid_service,
        reranking_service=reranking_service,
    )

    retrieval_result = retrieval_service(
        query=QUERY,
    )

    #
    # Generation
    #
    generation_service = GenerationService(
        prompt_builder=PromptBuilder(),
        llm_service=LLMService(),
    )

    request = GenerationRequest(
        query=QUERY,
        retrieval=retrieval_result,
        conversation=[],
    )

    start = perf_counter()

    response = generation_service.generate(
        request=request,
    )

    latency = perf_counter() - start

    #
    # Assertions
    #

    #
    # Generation
    #
    assert response.answer

    assert response.answer.strip()

    assert response.answer != QUERY

    assert len(response.answer) > 100

    #
    # Retrieval
    #
    assert retrieval_result.best_context is not None

    assert len(retrieval_result.contexts) > 0

    for context in retrieval_result.contexts:

        assert context.text

        assert context.source

        assert context.chunk_uuid is not None

        assert isinstance(
            context.retrieval_score,
            float,
        )

        assert isinstance(
            context.reranker_score,
            float,
        )

    #
    # Grounding
    #
    best_context = retrieval_result.best_context

    assert best_context is not None

    assert (
        best_context.reranker_score
        >= retrieval_result.contexts[-1].reranker_score
    )

    #
    # Hallucination Guard
    #
    if "FIFA" in QUERY:

        answer = response.answer.lower()

        assert (
            "does not contain" in answer
            or "not contain" in answer
            or "don't have enough" in answer
            or "not available" in answer
        )

    #
    # Pretty Output
    #
    print_results(
        request=request,
        answer=response.answer,
        latency=latency,
    )