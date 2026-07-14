from __future__ import annotations

from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

from app.chunking.pipeline import ChunkPipeline
from app.embeddings.batcher import EmbeddingBatcher
from app.embeddings.pipeline import EmbeddingPipeline
from app.ingestion.processors.pdf import PDFProcessor
from app.config.settings import settings


PDF_PATH = Path(
    "storage/uploads/e1767367-fdff-461a-86c1-579bb9fec1de.pdf"
)


class EmbeddingPipelineTester:
    """
    End-to-end tester for

        PDF
            ↓
        Chunk Pipeline
            ↓
        Embedding Pipeline

    This script is intended to verify that every stage
    works correctly before introducing the vector
    database.
    """

    def __init__(
        self,
    ) -> None:

        self.processor = PDFProcessor()

        self.chunk_pipeline = ChunkPipeline()

        self.embedding_pipeline = EmbeddingPipeline()

        self.batcher = EmbeddingBatcher()

    def header(
        self,
        title: str,
    ) -> None:

        print()

        print("=" * 100)

        print(title)

        print("=" * 100)

    def subheader(
        self,
        title: str,
    ) -> None:

        print()

        print("-" * 100)

        print(title)

        print("-" * 100)

    def run(
        self,
    ):

        #
        # ----------------------------------------------------
        # Extract document
        # ----------------------------------------------------
        #

        extraction = self.processor.extract(
            PDF_PATH,
        )

        self.header(
            "DOCUMENT INFORMATION",
        )

        print(
            f"Document : {PDF_PATH.name}"
        )

        print(
            f"Pages    : {extraction.metadata.page_count}"
        )

        print(
            f"Blocks   : {len(extraction.blocks)}"
        )

        #
        # ----------------------------------------------------
        # Chunk Pipeline
        # ----------------------------------------------------
        #

        self.header(
            "CHUNK PIPELINE",
        )

        chunks = self.chunk_pipeline.run(
            extraction,
        )

        print(
            f"Chunks Produced : {len(chunks)}"
        )

        #
        # ----------------------------------------------------
        # Embedding Batches
        # ----------------------------------------------------
        #

        batches = self.batcher.create_batches(
            chunks,
        )

        self.header(
            "EMBEDDING BATCHES",
        )

        print(
            f"Batch Count : {len(batches)}"
        )

        for index, batch in enumerate(
            batches,
            start=1,
        ):

            print(
                f"Batch {index:<3} : {batch.size} chunks"
            )

        #
        # ----------------------------------------------------
        # Embedding Pipeline
        # ----------------------------------------------------
        #

        self.header(
            "EMBEDDING PIPELINE",
        )

        embedded_chunks = self.embedding_pipeline.run(
            chunks,
        )

        print(
            f"Embedded Chunks : {len(embedded_chunks)}"
        )

        return (
            extraction,
            chunks,
            batches,
            embedded_chunks,
        )


def main():

    tester = EmbeddingPipelineTester()

    (
        extraction,
        chunks,
        batches,
        embedded_chunks,
    ) = tester.run()

    tester.header(
        "EMBEDDING SUMMARY",
    )

    print(
        f"Document Chunks : {len(chunks)}"
    )

    print(
        f"Embedded Chunks : {len(embedded_chunks)}"
    )

    print(
        f"Batches         : {len(batches)}"
    )

    #
    # ----------------------------------------------------
    # Vector Dimensions
    # ----------------------------------------------------
    #

    dimensions = [

        chunk.vector.dimensions

        for chunk in embedded_chunks

    ]

    print()

    print(
        f"Minimum Dimensions : {min(dimensions)}"
    )

    print(
        f"Maximum Dimensions : {max(dimensions)}"
    )

    print(
        f"Average Dimensions : {mean(dimensions):.2f}"
    )
    
    tester.header(
        "FIRST 20 EMBEDDED CHUNKS",
    )

    for embedded in embedded_chunks[:20]:

        chunk = embedded.chunk

        metadata = chunk.metadata

        embedding = embedded.metadata

        print()

        print("-" * 100)

        print(
            f"Chunk Index      : {chunk.chunk_index}"
        )

        print(
            f"Chunk UUID       : {metadata.chunk_uuid}"
        )

        print(
            f"Document UUID    : {metadata.document_uuid}"
        )

        print(
            f"Parent UUID      : {metadata.parent_chunk_uuid}"
        )

        print(
            f"Pages            : "
            f"{metadata.page_start} -> "
            f"{metadata.page_end}"
        )

        print(
            f"Blocks           : "
            f"{metadata.block_start} -> "
            f"{metadata.block_end}"
        )

        print(
            f"Tokens           : "
            f"{metadata.token_count}"
        )

        print(
            f"Characters       : "
            f"{metadata.character_count}"
        )

        print(
            f"Section          : "
            f"{metadata.section_title}"
        )

        print(
            f"Heading Path     : "
            f"{metadata.heading_path}"
        )

        print(
            f"Block Type       : "
            f"{metadata.block_type.value}"
        )

        print(
            f"Embedding Model  : "
            f"{embedding.model}"
        )

        print(
            f"Dimensions       : "
            f"{embedded.dimensions}"
        )

        print(
            f"Latency (ms)     : "
            f"{embedding.processing_time_ms:.3f}"
        )

        print(
            f"Cost (USD)       : "
            f"{embedding.cost_usd:.8f}"
        )

        print(
            f"Validated        : "
            f"{embedding.validated}"
        )

        print()

        print(
            chunk.text[:350]
        )

    #
    # ----------------------------------------------------
    # UUID VALIDATION
    # ----------------------------------------------------
    #

    tester.header(
        "UUID VALIDATION",
    )

    duplicate_chunk_uuid = (
        len(embedded_chunks)
        -
        len(
            {
                chunk.chunk_uuid
                for chunk in embedded_chunks
            }
        )
    )

    duplicate_document_uuid = (
        len(embedded_chunks)
        -
        len(
            {
                chunk.document_uuid
                for chunk in embedded_chunks
            }
        )
    )

    missing_chunk_uuid = sum(

        chunk.chunk_uuid is None

        for chunk in embedded_chunks

    )

    missing_document_uuid = sum(

        chunk.document_uuid is None

        for chunk in embedded_chunks

    )

    missing_parent_uuid = sum(

        (
            chunk.chunk.parent_chunk
            is not None
        )

        and

        (
            chunk.chunk.metadata.parent_chunk_uuid
            is None
        )

        for chunk in embedded_chunks

    )

    print()

    print(
        f"Duplicate Chunk UUIDs    : "
        f"{duplicate_chunk_uuid}"
    )

    print(
        f"Duplicate Document UUIDs : "
        f"{duplicate_document_uuid}"
    )

    print(
        f"Missing Chunk UUIDs      : "
        f"{missing_chunk_uuid}"
    )

    print(
        f"Missing Document UUIDs   : "
        f"{missing_document_uuid}"
    )

    print(
        f"Missing Parent UUIDs     : "
        f"{missing_parent_uuid}"
    )

    #
    # ----------------------------------------------------
    # BATCH SUMMARY
    # ----------------------------------------------------
    #

    tester.header(
        "BATCH SUMMARY",
    )

    batch_sizes = [

        batch.size

        for batch in batches

    ]

    print()

    print(
        f"Smallest Batch : "
        f"{min(batch_sizes)}"
    )

    print(
        f"Largest Batch  : "
        f"{max(batch_sizes)}"
    )

    print(
        f"Average Batch  : "
        f"{mean(batch_sizes):.2f}"
    )

    print()

    empty_batches = sum(

        batch.size == 0

        for batch in batches

    )

    print(
        f"Empty Batches  : "
        f"{empty_batches}"
    )
    
    #
    # ----------------------------------------------------
    # VECTOR VALIDATION
    # ----------------------------------------------------
    #

    tester.header(
        "VECTOR VALIDATION",
    )

    vector_dimensions = []

    empty_vectors = 0

    nan_vectors = 0

    infinite_vectors = 0

    for embedded in embedded_chunks:

        vector = embedded.vector.values

        if not vector:

            empty_vectors += 1

            continue

        vector_dimensions.append(
            len(vector),
        )

        for value in vector:

            if value != value:

                nan_vectors += 1

                break

            if value in (
                float("inf"),
                float("-inf"),
            ):

                infinite_vectors += 1

                break

    print()

    print(
        f"Empty Vectors        : {empty_vectors}"
    )

    print(
        f"NaN Vectors          : {nan_vectors}"
    )

    print(
        f"Infinite Vectors     : {infinite_vectors}"
    )

    print()

    print(
        f"Minimum Dimensions   : {min(vector_dimensions)}"
    )

    print(
        f"Maximum Dimensions   : {max(vector_dimensions)}"
    )

    print(
        f"Average Dimensions   : {mean(vector_dimensions):.2f}"
    )

    print()

    print(
        f"Dimension Frequency"
    )

    dimension_counter = Counter(
        vector_dimensions,
    )

    for dimension, count in sorted(
        dimension_counter.items(),
    ):

        print(
            f"{dimension:<8}{count}"
        )

    #
    # ----------------------------------------------------
    # COST STATISTICS
    # ----------------------------------------------------
    #

    tester.header(
        "COST STATISTICS",
    )

    costs = [

        embedded.metadata.cost_usd

        for embedded in embedded_chunks

    ]

    print()

    print(
        f"Total Cost (USD)     : {sum(costs):.8f}"
    )

    print(
        f"Average Cost (USD)   : {mean(costs):.8f}"
    )

    print(
        f"Lowest Cost (USD)    : {min(costs):.8f}"
    )

    print(
        f"Highest Cost (USD)   : {max(costs):.8f}"
    )

    #
    # ----------------------------------------------------
    # LATENCY STATISTICS
    # ----------------------------------------------------
    #

    tester.header(
        "LATENCY STATISTICS",
    )

    latencies = [

        embedded.metadata.processing_time_ms

        for embedded in embedded_chunks

    ]

    print()

    print(
        f"Total Latency (ms)   : {sum(latencies):.2f}"
    )

    print(
        f"Average Latency (ms) : {mean(latencies):.2f}"
    )

    print(
        f"Fastest Chunk (ms)   : {min(latencies):.2f}"
    )

    print(
        f"Slowest Chunk (ms)   : {max(latencies):.2f}"
    )

    #
    # ----------------------------------------------------
    # EMBEDDING METADATA
    # ----------------------------------------------------
    #

    tester.header(
        "EMBEDDING METADATA",
    )

    model_counter = Counter(

        embedded.metadata.model

        for embedded in embedded_chunks

    )

    print()

    for model, count in sorted(
        model_counter.items(),
    ):

        print(
            f"{model:<35}{count}"
        )

    print()

    validated_chunks = sum(

        embedded.metadata.validated

        for embedded in embedded_chunks

    )

    print(
        f"Validated Chunks     : {validated_chunks}"
    )

    print(
        f"Unvalidated Chunks   : "
        f"{len(embedded_chunks) - validated_chunks}"
    )
    
    #
    # ----------------------------------------------------
    # PRODUCTION READINESS
    # ----------------------------------------------------
    #

    tester.header(
        "PRODUCTION READINESS",
    )

    checks = {

        "Embedded Chunks Created":
            len(embedded_chunks) == len(chunks),

        "No Empty Vectors":
            empty_vectors == 0,

        "No NaN Values":
            nan_vectors == 0,

        "No Infinite Values":
            infinite_vectors == 0,

        "Correct Embedding Dimensions":
            (
                len(dimension_counter) == 1
            ),

        "Chunk UUIDs Preserved":
            missing_chunk_uuid == 0,

        "Document UUIDs Preserved":
            missing_document_uuid == 0,

        "Parent UUIDs Preserved":
            missing_parent_uuid == 0,

        "Validated Metadata":
            validated_chunks == len(
                embedded_chunks
            ),

        "No Empty Batches":
            empty_batches == 0,

        "Batch Sizes Within Limit":
            max(batch_sizes) <= settings.EMBEDDING_MAX_BATCH_SIZE,

        "Costs Populated":
            all(
                embedded.metadata.cost_usd >= 0
                for embedded in embedded_chunks
            ),

        "Latency Populated":
            all(
                embedded.metadata.processing_time_ms > 0
                for embedded in embedded_chunks
            ),

    }

    passed = 0

    failed = 0

    print()

    for name, status in checks.items():

        if status:

            print(
                f"[PASS] {name}"
            )

            passed += 1

        else:

            print(
                f"[FAIL] {name}"
            )

            failed += 1

    tester.header(
        "FINAL RESULT",
    )

    score = round(

        passed
        / len(checks)
        * 100,

        2,

    )

    print()

    print(
        f"Passed Checks : {passed}"
    )

    print(
        f"Failed Checks : {failed}"
    )

    print(
        f"Pipeline Score: {score}%"
    )

    print()

    if failed == 0:

        print(
            "STATUS : PASS"
        )

    else:

        print(
            "STATUS : FAIL"
        )


if __name__ == "__main__":

    main()