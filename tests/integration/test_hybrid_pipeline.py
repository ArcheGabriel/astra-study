from pathlib import Path

from app.chunking.pipeline import ChunkPipeline
from app.ingestion.processors.pdf import PDFProcessor
from app.search.hybrid.pipeline import HybridPipeline
from app.search.hybrid.service import HybridService


PDF_PATH = Path(
    "storage/uploads/e1767367-fdff-461a-86c1-579bb9fec1de.pdf"
)


def test_hybrid_pipeline() -> None:
    """
    End-to-end integration test for the complete
    Hybrid Retrieval pipeline.

    Pipeline

    PDF
        ↓
    Extraction
        ↓
    Chunking
        ↓
    Dense Embedding
        ↓
    Sparse Embedding
        ↓
    Hybrid Indexing
        ↓
    Native Qdrant Hybrid Search (RRF)
    """

    print("\nLoading PDF...")

    extraction = PDFProcessor().extract(
        PDF_PATH,
    )

    print(
        f"Pages: {extraction.metadata.page_count}"
    )

    print("\nChunking...")

    chunks = ChunkPipeline().run(
        extraction,
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    assert len(chunks) > 0

    hybrid = HybridPipeline()

    print("\nRecreating collection...")

    hybrid.recreate_collection()

    print("\nHybrid Indexing...")

    hybrid.index(
        chunks,
    )

    vector_count = hybrid.count()

    print(
        f"Vectors stored: {vector_count}"
    )

    assert vector_count == len(chunks)

    assert hybrid.is_empty() is False

    print()

    print("=" * 80)
    print("Collection Information")
    print("=" * 80)

    print(
        hybrid.collection_info()
    )

    service = HybridService()

    queries = [

        "What is Retrieval Augmented Generation?",

        "Explain transformer architecture.",

        "What are Large Language Models?",

        "What is Chain of Thought?",

        "What is RLHF?",

    ]

    for query in queries:

        print()
        print("=" * 80)
        print(query)
        print("=" * 80)

        results = service.search(
            query=query,
            limit=5,
        )

        assert len(results) > 0

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

            print()

            print(
                f"Rank      : {rank}"
            )

            print(
                f"Score     : {result.score:.4f}"
            )

            print(
                f"Document  : {payload.get('document_name')}"
            )

            print(
                f"Page      : {payload.get('page_start')}"
            )

            print(
                f"Section   : {payload.get('section_title')}"
            )

            print(
                f"Chunk UUID: {result.chunk_uuid}"
            )

            print()

            snippet = result.text.replace(
                "\n",
                " ",
            )

            print(
                snippet[:350]
            )

            print("-" * 80)

    print()
    print("=" * 80)
    print("Hybrid Retrieval Integration Test Passed")
    print("=" * 80)