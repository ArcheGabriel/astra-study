from __future__ import annotations

import re
from collections.abc import Iterator

from app.generation.base import BaseGenerationService
from app.generation.exceptions import EmptyResponseError
from app.generation.models import (
    Citation,
    GenerationRequest,
    GenerationResponse,
)
from app.generation.prompt_builder import PromptBuilder
from app.services.llm import LLMService

# Deterministic citation-relevance tuning. See `_citation_relevance` for why
# this exists: retrieval/reranker order answers "what is semantically close
# to the query", not "which chunk is the question's own dedicated section".
_STOPWORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "what", "who", "whom",
    "which", "that", "of", "in", "on", "for", "to", "and", "or", "do",
    "does", "did", "this", "these", "those", "with", "by", "as", "at",
    "be", "been", "being", "it", "its", "their", "they", "he", "she",
    "you", "your", "i", "we", "our", "us", "about", "from", "into",
    "how", "why", "when", "where", "will", "can", "please",
})

# Bounded contribution a structural heading match can add on top of the
# reranker score when ordering citations. Large enough to let an exact,
# on-topic section heading (e.g. "Problem Statement" for a question about
# the problem statement) outrank a broader section (e.g. "Executive
# Summary") that scored a little higher semantically; small enough that it
# can never outweigh a genuinely large reranker-score gap.
_HEADING_MATCH_WEIGHT = 0.2

_EXCERPT_LIMIT = 500

_WORD_PATTERN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str | None) -> set[str]:
    if not text:
        return set()
    return {
        token
        for token in _WORD_PATTERN.findall(text.lower())
        if len(token) > 2 and token not in _STOPWORDS
    }


def _heading_overlap(query_tokens: set[str], citation: Citation) -> float:
    """Fraction of the question's own words that appear in the chunk's
    heading/section. Zero when there is nothing to compare, never negative,
    never fabricated -- it only reads structural metadata already produced
    by chunking.
    """
    if not query_tokens:
        return 0.0
    heading_tokens = _tokenize(" ".join(citation.heading_path or []))
    heading_tokens |= _tokenize(citation.section)
    if not heading_tokens:
        return 0.0
    return len(query_tokens & heading_tokens) / len(query_tokens)


def _citation_relevance(query_tokens: set[str], citation: Citation) -> float:
    """Citation relevance = retrieval/reranker confidence + a bounded
    structural bonus for a heading that directly echoes the question.

    This never changes what was retrieved or what generation used -- it only
    orders the citations already built from that evidence, so the most
    directly relevant section is surfaced first while every retrieved chunk
    remains cited.
    """

    base = citation.score if citation.score is not None else 0.0
    return base + _heading_overlap(query_tokens, citation) * _HEADING_MATCH_WEIGHT


def _excerpt(text: str | None) -> str | None:
    """Deterministic excerpt from the cited chunk's own text -- never text
    from another chunk, never LLM-rewritten. Truncates on a word boundary so
    the excerpt never ends mid-word.
    """

    if not text:
        return None
    excerpt = text.strip()
    if len(excerpt) <= _EXCERPT_LIMIT:
        return excerpt
    truncated = excerpt[:_EXCERPT_LIMIT]
    boundary = truncated.rfind(" ")
    if boundary > 0:
        truncated = truncated[:boundary]
    return truncated.rstrip() + "…"


class GenerationService(BaseGenerationService):
    """
    Production implementation of the Generation layer.

    Responsibilities
    ----------------
    - Build prompts using the PromptBuilder.
    - Delegate response generation to the LLMService.
    - Convert provider responses into GenerationResponse.
    - Produce deterministic source citations from retrieved contexts.

    This service intentionally contains no provider-specific logic.
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        llm_service: LLMService,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._llm_service = llm_service

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """
        Generate a complete assistant response.
        """
        
        if not request.retrieval:
            return GenerationResponse(
                answer=("I couldn't find any relevant information in your uploaded "
                        "documents that answers this question."),
                citations=[],
            )

        messages = self._prompt_builder.build(
            request=request,
        )

        response = self._llm_service.generate_response(
            messages=messages,
        )

        response = response.strip()

        if not response:
            raise EmptyResponseError(
                "The language model returned an empty response."
            )

        citations = self.citations_for(request)

        return GenerationResponse(
            answer=response,
            citations=citations,
        )

    @staticmethod
    def citations_for(request: GenerationRequest) -> list[Citation]:
        """Build clean, deduplicated citations from retrieved provenance,
        ordered by citation relevance rather than raw reranker order.

        Retrieval/reranker order answers "what is semantically close to the
        query"; citation order answers "which of the retrieved chunks is the
        question's own dedicated evidence". Both are legitimate but distinct,
        so citations are re-sorted using `_citation_relevance` (reranker
        score plus a bounded heading-match bonus) -- generation itself is
        unaffected, since it still consumes `request.retrieval` directly in
        its original reranked order.
        """
        seen: set[tuple[str | None, ...]] = set()
        citations: list[Citation] = []
        for context in request.retrieval:
            # chunk_uuid keeps distinct chunks from the same document/section
            # individually traceable; only exact duplicate chunks collapse.
            key = (
                context.source, context.page, context.section,
                context.sheet_name, str(context.chunk_uuid),
            )
            if key in seen:
                continue
            seen.add(key)
            citations.append(Citation(
                source=context.source, page=context.page, section=context.section,
                source_type=context.source_type, sheet_name=context.sheet_name,
                heading_path=context.heading_path, block_type=context.block_type,
                chunk_id=str(context.chunk_uuid), provenance=context.provenance,
                page_end=context.page_end, parser=context.parser,
                score=context.reranker_score, excerpt=_excerpt(context.text),
            ))

        query_tokens = _tokenize(request.query)
        # `sort` is stable: citations with equal relevance keep their
        # original (reranked) relative order.
        citations.sort(
            key=lambda citation: _citation_relevance(query_tokens, citation),
            reverse=True,
        )
        return citations

    def stream(
        self,
        request: GenerationRequest,
    ) -> Iterator[str]:
        """
        Stream the assistant response.
        """
        
        if not request.retrieval:
            yield (
                "I couldn't find any relevant information in your uploaded "
                "documents that answers this question."
            )
            return

        messages = self._prompt_builder.build(
            request=request,
        )

        yield from self._llm_service.stream_response(
            messages=messages,
        )
