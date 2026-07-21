from __future__ import annotations

import logging
from pprint import pprint

from app.config.settings import settings
from app.retrieval.service import RetrievalService
from app.reranking.service import RerankingService
from app.search.hybrid.service import HybridService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


QUERY = "Explain semantic chunking and why it improves RAG."


def print_results(result) -> None:
    print("\n" + "=" * 80)
    print("RETRIEVAL PIPELINE RESULTS")
    print("=" * 80)

    print(f"\nQuery:\n{result.query}")

    print(
        f"\nRetrieval Latency : "
        f"{result.retrieval_latency:.2f} seconds"
    )

    print(f"Contexts Returned : {len(result.contexts)}")

    print("\n" + "-" * 80)

    for idx, context in enumerate(result.contexts, start=1):

        print(f"\nRank #{idx}")

        print(f"Source           : {context.source}")
        print(f"Page             : {context.page}")
        print(f"Section          : {context.section}")

        print(
            f"Retrieval Score  : "
            f"{context.retrieval_score:.4f}"
        )

        print(
            f"Reranker Score   : "
            f"{context.reranker_score:.4f}"
        )

        preview = context.text.replace("\n", " ")

        if len(preview) > 300:
            preview = preview[:300] + "..."

        print("\nPreview")
        print(preview)

        print("-" * 80)

    print("\nSources")

    pprint(result.sources)

    print("=" * 80)


def test_retrieval_pipeline() -> None:
    """
    Integration test for the complete retrieval pipeline.

    Pipeline:

    Query
        ↓
    Hybrid Search
        ↓
    CrossEncoder Reranking
        ↓
    RetrievalService
    """

    hybrid_service = HybridService()

    reranking_service = RerankingService()

    retrieval_service = RetrievalService(
        hybrid_service=hybrid_service,
        reranking_service=reranking_service,
    )

    result = retrieval_service(
        query=QUERY,
    )

    assert result.query == QUERY

    assert len(result.contexts) > 0

    assert result.best_context is not None

    assert len(result.sources) > 0

    assert result.retrieval_latency > 0

    for context in result.contexts:

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

    print_results(result)