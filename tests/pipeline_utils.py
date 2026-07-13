from __future__ import annotations

from collections import Counter
from statistics import mean

from app.chunking.models import DocumentChunk


def print_header(
    title: str,
) -> None:
    """
    Print a formatted section header.
    """

    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def print_subheader(
    title: str,
) -> None:
    """
    Print a formatted subsection header.
    """

    print()
    print("-" * 100)
    print(title)
    print("-" * 100)


def separator() -> None:
    """
    Print a separator line.
    """

    print("-" * 100)


def block_type_distribution(
    chunks: list[DocumentChunk],
) -> Counter:
    """
    Count chunks by block type.
    """

    return Counter(

        chunk.metadata.block_type.value

        for chunk in chunks

    )


def token_statistics(
    chunks: list[DocumentChunk],
) -> dict:

    if not chunks:

        return {
            "min": 0,
            "max": 0,
            "avg": 0,
        }

    values = [

        chunk.metadata.token_count

        for chunk in chunks

    ]

    return {

        "min": min(values),

        "max": max(values),

        "avg": round(
            mean(values),
            2,
        ),

    }


def character_statistics(
    chunks: list[DocumentChunk],
) -> dict:

    if not chunks:

        return {
            "min": 0,
            "max": 0,
            "avg": 0,
        }

    values = [

        chunk.metadata.character_count

        for chunk in chunks

    ]

    return {

        "min": min(values),

        "max": max(values),

        "avg": round(
            mean(values),
            2,
        ),

    }


def recursive_chunk_count(
    chunks: list[DocumentChunk],
) -> int:

    return sum(

        chunk.parent_chunk is not None

        for chunk in chunks

    )


def oversized_chunks(
    chunks: list[DocumentChunk],
    limit: int = 700,
) -> list[DocumentChunk]:

    return [

        chunk

        for chunk in chunks

        if chunk.metadata.token_count > limit

    ]


def duplicate_uuid_count(
    chunks: list[DocumentChunk],
) -> int:

    uuids = [

        chunk.metadata.chunk_uuid

        for chunk in chunks

    ]

    return len(uuids) - len(set(uuids))


def empty_chunk_count(
    chunks: list[DocumentChunk],
) -> int:

    return sum(

        not chunk.text.strip()

        for chunk in chunks

    )


def missing_uuid_count(
    chunks: list[DocumentChunk],
) -> int:

    return sum(

        chunk.metadata.chunk_uuid is None

        for chunk in chunks

    )


def invalid_page_ranges(
    chunks: list[DocumentChunk],
) -> list[DocumentChunk]:

    invalid = []

    for chunk in chunks:

        metadata = chunk.metadata

        if (

            metadata.page_start is not None

            and metadata.page_end is not None

            and metadata.page_start > metadata.page_end

        ):

            invalid.append(
                chunk,
            )

    return invalid


def invalid_block_ranges(
    chunks: list[DocumentChunk],
) -> list[DocumentChunk]:

    invalid = []

    for chunk in chunks:

        metadata = chunk.metadata

        if (

            metadata.block_start is not None

            and metadata.block_end is not None

            and metadata.block_start > metadata.block_end

        ):

            invalid.append(
                chunk,
            )

    return invalid


def heading_path_errors(
    chunks: list[DocumentChunk],
) -> list[DocumentChunk]:

    return [

        chunk

        for chunk in chunks

        if (
            chunk.metadata.section_title
            and not chunk.metadata.heading_path
        )

    ]


def quality_distribution(
    chunks: list[DocumentChunk],
) -> dict:

    return {

        "references": sum(

            chunk.metadata.is_reference

            for chunk in chunks

        ),

        "appendix": sum(

            chunk.metadata.is_appendix

            for chunk in chunks

        ),

        "captions": sum(

            chunk.metadata.is_caption

            for chunk in chunks

        ),

        "tables": sum(

            chunk.metadata.is_table

            for chunk in chunks

        ),

        "formulae": sum(

            chunk.metadata.is_formula

            for chunk in chunks

        ),

        "metadata": sum(

            chunk.metadata.is_metadata

            for chunk in chunks

        ),

    }


def largest_chunks(
    chunks: list[DocumentChunk],
    limit: int = 10,
) -> list[DocumentChunk]:

    return sorted(

        chunks,

        key=lambda chunk: chunk.metadata.token_count,

        reverse=True,

    )[:limit]