from pathlib import Path

from app.chunking.pipeline import ChunkPipeline
from app.embeddings.embedder import OpenAIEmbedder
from app.ingestion.processors.pdf import PDFProcessor
from app.search.dense.pipeline import DensePipeline
from app.search.hybrid.pipeline import HybridPipeline
from app.search.hybrid.service import HybridService


PDF_PATH = Path(
    "storage/uploads/e1767367-fdff-461a-86c1-579bb9fec1de.pdf"
)


def test_retrieval_comparison() -> None:
    """
    Compare Dense Retrieval vs Hybrid Retrieval
    using the same indexed document.
    """

    print("\nLoading PDF...")

    extraction = PDFProcessor().extract(
        PDF_PATH,
    )

    chunks = ChunkPipeline().run(
        extraction,
    )

    print(f"Chunks: {len(chunks)}")

    hybrid = HybridPipeline()

    print("\nRecreating collection...")

    hybrid.recreate_collection()

    print("\nIndexing...")

    hybrid.index(chunks)
    
    print("\nInspecting stored payload...")

    points = hybrid.repository.scroll(limit=1)

    print(points[0].payload)

    dense = DensePipeline()

    embedder = OpenAIEmbedder()

    hybrid_service = HybridService()

    queries = [

        "What is Retrieval Augmented Generation?",

        "Explain transformer architecture.",

        "What is RLHF?",

        "What is Chain of Thought?",

        "What are Large Language Models?",

    ]

    for query in queries:

        print("\n")
        print("=" * 100)
        print(query)
        print("=" * 100)

        dense_results = dense.search(
            query_vector=embedder.embed_query(query),
            limit=3,
        )

        hybrid_results = hybrid_service.search(
            query=query,
            limit=3,
        )

        print("\nDENSE RETRIEVAL")
        print("-" * 100)

        for rank, result in enumerate(
            dense_results,
            start=1,
        ):

            payload = result.payload or {}

            print(
                f"{rank}. "
                f"[{result.score:.4f}] "
                f"{payload.get('section_title')}"
            )

        print()

        print("HYBRID RETRIEVAL")
        print("-" * 100)

        for rank, result in enumerate(
            hybrid_results,
            start=1,
        ):

            payload = result.payload or {}

            print(
                f"{rank}. "
                f"[{result.score:.4f}] "
                f"{payload.get('section_title')}"
            )