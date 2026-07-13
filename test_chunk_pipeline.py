from __future__ import annotations

from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

from app.chunking.pipeline import ChunkPipeline
from app.chunking.stages.filter import FilterStage
from app.chunking.stages.finalize import FinalizeStage
from app.chunking.stages.merge import MergeStage
from app.chunking.stages.metadata import MetadataStage
from app.chunking.stages.paragraph import ParagraphStage
from app.chunking.stages.quality import QualityStage
from app.chunking.stages.recursive import RecursiveStage
from app.chunking.stages.semantic import SemanticStage
from app.ingestion.processors.pdf import PDFProcessor


PDF_PATH = Path(
    "storage/uploads/e1767367-fdff-461a-86c1-579bb9fec1de.pdf"
)


class PipelineTester:

    def __init__(self):

        self.processor = PDFProcessor()

        self.pipeline = ChunkPipeline()

        self.stages = [

            ParagraphStage(),

            MetadataStage(),

            MergeStage(),

            RecursiveStage(),

            SemanticStage(),

            FilterStage(),

            QualityStage(),

            FinalizeStage(),

        ]

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

    def run(self):

        extraction = self.processor.extract(
            PDF_PATH,
        )

        self.header(
            "DOCUMENT INFORMATION"
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

        data: Any = extraction

        self.header(
            "PIPELINE EXECUTION"
        )

        for stage in self.stages:

            print()

            print(
                f"Running {stage.__class__.__name__}"
            )

            before = (
                len(data.blocks)
                if hasattr(
                    data,
                    "blocks",
                )
                else len(data)
            )

            data = stage.run(
                data,
            )

            after = len(data)

            print(
                f"Input  : {before}"
            )

            print(
                f"Output : {after}"
            )

        chunks = data

        self.header(
            "PIPELINE SUMMARY"
        )

        print(
            f"Final Chunks : {len(chunks)}"
        )

        return extraction, chunks


def main():

    tester = PipelineTester()

    extraction, chunks = tester.run()

    print()

    print("=" * 100)

    print("BLOCK TYPE DISTRIBUTION")

    print("=" * 100)

    counter = Counter(

        chunk.metadata.block_type.value

        for chunk in chunks

    )

    for block_type, count in sorted(
        counter.items(),
    ):

        print(
            f"{block_type:<20}{count}"
        )

    print()

    print("=" * 100)

    print("FIRST 20 CHUNKS")

    print("=" * 100)

    for chunk in chunks[:20]:

        print()

        print("-" * 100)

        print(
            f"Chunk Index      : {chunk.chunk_index}"
        )

        print(
            f"Chunk UUID       : {chunk.metadata.chunk_uuid}"
        )

        print(
            f"Document UUID    : {chunk.metadata.document_uuid}"
        )

        print(
            f"Parent Chunk     : {chunk.parent_chunk}"
        )

        print(
            f"Parent UUID      : {chunk.metadata.parent_chunk_uuid}"
        )

        print(
            f"Pages            : {chunk.metadata.page_start} -> {chunk.metadata.page_end}"
        )

        print(
            f"Blocks           : {chunk.metadata.block_start} -> {chunk.metadata.block_end}"
        )

        print(
            f"Tokens           : {chunk.metadata.token_count}"
        )

        print(
            f"Characters       : {chunk.metadata.character_count}"
        )

        print(
            f"Heading Level    : {chunk.metadata.heading_level}"
        )

        print(
            f"Heading Path     : {chunk.metadata.heading_path}"
        )

        print(
            f"Section ID       : {chunk.metadata.section_id}"
        )

        print(
            f"Section Title    : {chunk.metadata.section_title}"
        )

        print(
            f"Block Type       : {chunk.metadata.block_type.value}"
        )

        print(
            f"Quality Score    : {chunk.metadata.quality_score:.2f}"
        )

        print(
            f"Priority         : {chunk.metadata.retrieval_priority}"
        )

        print()

        print(
            chunk.text[:350]
        )

        print()

    print("=" * 100)

    print("QUALITY CHECK")

    print("=" * 100)

    empty_chunks = sum(

        not chunk.text.strip()

        for chunk in chunks

    )

    duplicate_uuid_count = len(chunks) - len({

        chunk.metadata.chunk_uuid

        for chunk in chunks

    })

    missing_chunk_uuid = sum(

        chunk.metadata.chunk_uuid is None

        for chunk in chunks

    )

    missing_document_uuid = sum(

        chunk.metadata.document_uuid is None

        for chunk in chunks

    )

    missing_parent_uuid = sum(

        chunk.parent_chunk is not None

        and chunk.metadata.parent_chunk_uuid is None

        for chunk in chunks

    )

    token_counts = [

        chunk.metadata.token_count

        for chunk in chunks

    ]

    character_counts = [

        chunk.metadata.character_count

        for chunk in chunks

    ]

    print()

    print(f"Empty Chunks           : {empty_chunks}")

    print(f"Duplicate UUIDs        : {duplicate_uuid_count}")

    print(f"Missing Chunk UUIDs    : {missing_chunk_uuid}")

    print(f"Missing Document UUIDs : {missing_document_uuid}")

    print(f"Missing Parent UUIDs   : {missing_parent_uuid}")

    print()

    print(f"Minimum Tokens         : {min(token_counts)}")

    print(f"Maximum Tokens         : {max(token_counts)}")

    print(f"Average Tokens         : {mean(token_counts):.2f}")

    print()

    print(f"Minimum Characters     : {min(character_counts)}")

    print(f"Maximum Characters     : {max(character_counts)}")

    print(f"Average Characters     : {mean(character_counts):.2f}")

    print()

    print("=" * 100)

    print("OVERSIZED CHUNKS")

    print("=" * 100)
    

    oversized = [

        chunk

        for chunk in chunks

        if chunk.metadata.token_count > 700

    ]

    print()

    print(

        f"Chunks >700 Tokens : {len(oversized)}"

    )

    for chunk in oversized:

        print()

        print("-" * 80)

        print(

            f"Chunk        : {chunk.chunk_index}"

        )

        print(

            f"Tokens       : {chunk.metadata.token_count}"

        )

        print(

            f"Characters   : {chunk.metadata.character_count}"

        )

        print(

            f"Pages        : {chunk.metadata.page_start}->{chunk.metadata.page_end}"

        )

        print(

            f"Section      : {chunk.metadata.section_title}"

        )

        print(

            f"Heading Path : {chunk.metadata.heading_path}"

        )

    print()

    print("=" * 100)

    print("RECURSIVE SPLIT CHECK")

    print("=" * 100)

    recursive_chunks = [

        chunk

        for chunk in chunks

        if chunk.parent_chunk is not None

    ]

    print()

    print(

        f"Recursive Chunks : {len(recursive_chunks)}"

    )

    for chunk in recursive_chunks[:20]:

        print()

        print(

            f"Chunk       : {chunk.chunk_index}"

        )

        print(

            f"Parent      : {chunk.parent_chunk}"

        )

        print(

            f"Chunk UUID  : {chunk.metadata.chunk_uuid}"

        )

        print(

            f"Parent UUID : {chunk.metadata.parent_chunk_uuid}"

        )

        print(

            f"Tokens      : {chunk.metadata.token_count}"

        )

        print(

            f"Characters  : {chunk.metadata.character_count}"

        )

        print(

            f"Section     : {chunk.metadata.section_title}"

        )

    print()

    print("=" * 100)

    print("REFERENCE / CAPTION / TABLE SUMMARY")

    print("=" * 100)

    print()

    print(

        f"Reference Chunks : {sum(chunk.metadata.is_reference for chunk in chunks)}"

    )

    print(

        f"Appendix Chunks  : {sum(chunk.metadata.is_appendix for chunk in chunks)}"

    )

    print(

        f"Metadata Chunks  : {sum(chunk.metadata.is_metadata for chunk in chunks)}"

    )

    print(

        f"Caption Chunks   : {sum(chunk.metadata.is_caption for chunk in chunks)}"

    )

    print(

        f"Table Chunks     : {sum(chunk.metadata.is_table for chunk in chunks)}"

    )

    print(

        f"Formula Chunks   : {sum(chunk.metadata.is_formula for chunk in chunks)}"

    )

    print()

    print("=" * 100)

    print("TOP 10 LARGEST CHUNKS")

    print("=" * 100)

    largest_chunks = sorted(

        chunks,

        key=lambda chunk: chunk.metadata.token_count,

        reverse=True,

    )[:10]

    for chunk in largest_chunks:

        print()

        print("-" * 100)

        print(
            f"Chunk Index      : {chunk.chunk_index}"
        )

        print(
            f"Chunk UUID       : {chunk.metadata.chunk_uuid}"
        )

        print(
            f"Parent Chunk     : {chunk.parent_chunk}"
        )

        print(
            f"Parent UUID      : {chunk.metadata.parent_chunk_uuid}"
        )

        print(
            f"Tokens           : {chunk.metadata.token_count}"
        )

        print(
            f"Characters       : {chunk.metadata.character_count}"
        )

        print(
            f"Pages            : {chunk.metadata.page_start} -> {chunk.metadata.page_end}"
        )

        print(
            f"Blocks           : {chunk.metadata.block_start} -> {chunk.metadata.block_end}"
        )

        print(
            f"Section          : {chunk.metadata.section_title}"
        )

        print(
            f"Heading Path     : {chunk.metadata.heading_path}"
        )

        print(
            f"Quality Score    : {chunk.metadata.quality_score:.2f}"
        )

        print(
            f"Priority         : {chunk.metadata.retrieval_priority}"
        )

    print()

    print("=" * 100)

    print("PRODUCTION READINESS CHECK")

    print("=" * 100)

    checks = {

        "No Empty Chunks":
            empty_chunks == 0,

        "Chunk UUIDs Generated":
            missing_chunk_uuid == 0,

        "Document UUIDs Generated":
            missing_document_uuid == 0,

        "Parent UUIDs Generated":
            missing_parent_uuid == 0,

        "Unique Chunk UUIDs":
            duplicate_uuid_count == 0,

        "Token Counts Populated":
            min(token_counts) > 0,

        "Character Counts Populated":
            min(character_counts) > 0,

        "No Oversized Chunks":
            len(oversized) == 0,

        "Section Titles Present":
            all(
                chunk.metadata.section_title is not None
                for chunk in chunks
            ),

        "Heading Paths Present":
            all(
                len(chunk.metadata.heading_path) > 0
                for chunk in chunks
            ),

        "Valid Page Ranges":
            all(
                (
                    chunk.metadata.page_start is None
                    or chunk.metadata.page_end is None
                    or chunk.metadata.page_start <= chunk.metadata.page_end
                )
                for chunk in chunks
            ),

        "Valid Block Ranges":
            all(
                (
                    #
                    # Missing block information is valid.
                    #
                    chunk.metadata.block_start is None
                    or chunk.metadata.block_end is None

                    #
                    # Different pages.
                    #
                    # Block numbering restarts on every page,
                    # so ordering cannot be compared.
                    #
                    or (
                        chunk.metadata.page_start is not None
                        and chunk.metadata.page_end is not None
                        and chunk.metadata.page_start != chunk.metadata.page_end
                    )

                    #
                    # Same page.
                    #
                    # Block numbers must be increasing.
                    #
                    or (
                        chunk.metadata.page_start == chunk.metadata.page_end
                        and chunk.metadata.block_start
                        <= chunk.metadata.block_end
                    )
                )
                for chunk in chunks
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

    print()

    print("=" * 100)

    print("FINAL RESULT")

    print("=" * 100)

    score = round(

        passed / len(checks) * 100,

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