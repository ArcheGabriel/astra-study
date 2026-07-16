from pathlib import Path

from app.chunking.pipeline import ChunkPipeline
from app.embeddings.embedder import OpenAIEmbedder
from app.embeddings.pipeline import EmbeddingPipeline
from app.ingestion.processors.pdf import PDFProcessor
from app.search.dense.pipeline import DensePipeline


PDF_PATH = Path(
    "storage/uploads/e1767367-fdff-461a-86c1-579bb9fec1de.pdf"
)


def test_dense_pipeline() -> None:
    """
    End-to-end integration test for the complete Dense Retrieval pipeline.

    Pipeline:

    PDF
        ↓
    Extraction
        ↓
    Chunking
        ↓
    Embedding
        ↓
    Qdrant Indexing
        ↓
    Semantic Search
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

    print("\nEmbedding...")

    embedded_chunks = EmbeddingPipeline().run(
        chunks,
    )

    print(
        f"Embedded: {len(embedded_chunks)}"
    )

    assert len(embedded_chunks) == len(chunks)

    dense = DensePipeline()

    print("\nRecreating collection...")

    dense.recreate_collection()

    print("\nIndexing vectors...")

    dense.index(
        embedded_chunks,
    )

    vector_count = dense.count()

    print(
        f"Vectors stored: {vector_count}"
    )

    assert vector_count == len(
        embedded_chunks,
    )

    embedder = OpenAIEmbedder()

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

        query_vector = embedder.embed_query(
            query,
        )

        results = dense.search(
            query_vector=query_vector,
            limit=5,
        )

        assert len(results) > 0

        previous_score = None

        for rank, result in enumerate(results, start=1):

            if previous_score is not None:

                assert (
                    result.score <= previous_score
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
    print("Dense Retrieval Integration Test Passed")
    print("=" * 80)