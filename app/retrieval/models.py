from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import SupportsIndex
from uuid import UUID
from typing import Any


@dataclass(frozen=True, slots=True)
class RetrievedContext:
    """
    Represents a single document chunk after the complete
    retrieval pipeline (Hybrid Search + CrossEncoder Reranking).
    """

    text: str

    source: str

    chunk_uuid: UUID

    retrieval_score: float

    reranker_score: float

    page: int | None = None

    section: str | None = None

    source_type: str | None = None
    sheet_name: str | None = None
    heading_path: list[str] | None = None
    block_type: str | None = None
    provenance: list[dict[str, Any]] | None = None
    page_end: int | None = None
    parser: str | None = None


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    """
    Final output returned by the RetrievalService.
    """

    query: str

    contexts: list[RetrievedContext]

    retrieval_latency: float

    @property
    def best_context(
        self,
    ) -> RetrievedContext | None:

        if not self.contexts:
            return None

        return self.contexts[0]

    @property
    def sources(
        self,
    ) -> list[str]:
        """
        Return unique document sources while preserving
        retrieval order.
        """

        seen: set[str] = set()
        sources: list[str] = []

        for context in self.contexts:

            if context.source in seen:
                continue

            seen.add(context.source)
            sources.append(context.source)

        return sources

    @property
    def pages(
        self,
    ) -> list[int]:
        """
        Return unique page numbers while preserving
        retrieval order.
        """

        seen: set[int] = set()
        pages: list[int] = []

        for context in self.contexts:

            if context.page is None:
                continue

            if context.page in seen:
                continue

            seen.add(context.page)
            pages.append(context.page)

        return pages

    @property
    def sections(
        self,
    ) -> list[str]:
        """
        Return unique section names while preserving
        retrieval order.
        """

        seen: set[str] = set()
        sections: list[str] = []

        for context in self.contexts:

            if context.section is None:
                continue

            if context.section in seen:
                continue

            seen.add(context.section)
            sections.append(context.section)

        return sections

    def top_k(
        self,
        k: int,
    ) -> list[RetrievedContext]:

        return self.contexts[:k]

    def __len__(
        self,
    ) -> int:

        return len(
            self.contexts
        )

    def __iter__(
        self,
    ) -> Iterator[RetrievedContext]:

        return iter(
            self.contexts
        )

    def __getitem__(
        self,
        item: SupportsIndex | slice,
    ) -> RetrievedContext | Sequence[RetrievedContext]:

        return self.contexts[item]
