from pathlib import Path

import pymupdf4llm

from app.document.page import MarkdownPage


class MarkdownExtractor:
    """
    Extracts page-aware Markdown from PDF documents using
    PyMuPDF4LLM.

    Each page is returned as a strongly typed MarkdownPage
    object so that page metadata, layout information and
    Markdown remain together throughout the pipeline.
    """

    def extract(
        self,
        file_path: Path,
    ) -> list[MarkdownPage]:
        """
        Convert a PDF into page-wise Markdown.
        """

        pages = pymupdf4llm.to_markdown(
            str(file_path),
            page_chunks=True,
        )

        markdown_pages: list[MarkdownPage] = []

        for page in pages:

            metadata = page["metadata"]

            markdown_pages.append(
                MarkdownPage(
                    page_number=metadata["page_number"],
                    page_count=metadata["page_count"],
                    markdown=page["text"],
                    page_boxes=page.get(
                        "page_boxes",
                        [],
                    ),
                    toc_items=page.get(
                        "toc_items",
                        [],
                    ),
                    metadata=dict(
                        metadata,
                    ),
                )
            )

        return markdown_pages