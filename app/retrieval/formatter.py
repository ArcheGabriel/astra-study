from __future__ import annotations

import json

from app.retrieval.exceptions import ContextFormattingError
from app.retrieval.models import RetrievalResult


class ContextFormatter:
    """
    Formats retrieved contexts into different representations
    suitable for downstream LLMs.
    """

    def to_plain_text(
        self,
        result: RetrievalResult,
    ) -> str:
        """
        Format contexts as plain text.
        """

        if not result.contexts:
            raise ContextFormattingError(
                "No contexts available to format."
            )

        sections: list[str] = []

        for index, context in enumerate(
            result.contexts,
            start=1,
        ):
            metadata = (
                f"[Context {index}] "
                f"Source: {context.source}"
            )

            if context.page is not None:
                metadata += (
                    f" | Page: {context.page}"
                )

            if context.section:
                metadata += (
                    f" | Section: {context.section}"
                )

            sections.append(
                "\n".join(
                    (
                        metadata,
                        context.text.strip(),
                    )
                )
            )

        return "\n\n".join(sections)

    def to_markdown(
        self,
        result: RetrievalResult,
    ) -> str:
        """
        Format contexts as Markdown.
        """

        if not result.contexts:
            raise ContextFormattingError(
                "No contexts available to format."
            )

        blocks: list[str] = []

        for index, context in enumerate(
            result.contexts,
            start=1,
        ):
            header = (
                f"## Context {index}\n"
                f"- **Source:** {context.source}"
            )

            if context.page is not None:
                header += (
                    f"\n- **Page:** {context.page}"
                )

            if context.section:
                header += (
                    f"\n- **Section:** {context.section}"
                )

            blocks.append(
                (
                    f"{header}\n\n"
                    f"{context.text.strip()}"
                )
            )

        return "\n\n---\n\n".join(blocks)

    def to_json(
        self,
        result: RetrievalResult,
    ) -> str:
        """
        Serialize contexts into JSON.
        """

        payload = [
            {
                "source": context.source,
                "page": context.page,
                "section": context.section,
                "text": context.text,
                "retrieval_score": context.retrieval_score,
                "reranker_score": context.reranker_score,
                "chunk_uuid": str(
                    context.chunk_uuid,
                ),
            }
            for context in result.contexts
        ]

        return json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )