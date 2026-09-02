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

# Bounded contribution a genuine section-title match can add on top of the
# reranker score when ordering citations. Large enough to let a section
# whose title actually answers the question (e.g. "Problem Statement" for a
# question about the problem statement) outrank a broader section (e.g.
# "Executive Summary") that scored a little higher semantically; small
# enough that it can never outweigh a genuinely large reranker-score gap.
# The match itself is *intent-weighted* (see `_query_term_weights`) so a
# heading that merely repeats the question's topic/entity earns almost none
# of it.
_HEADING_MATCH_WEIGHT = 0.2

# Bounded contribution for answer/evidence alignment: how much the generated
# answer actually draws on a chunk. Slightly smaller than the heading weight
# (structural match to the question is a stronger citation signal than
# lexical echo in the answer), still bounded so it only re-orders retrieved
# evidence and never fabricates or drops any.
_ANSWER_SUPPORT_WEIGHT = 0.15

# A chunk needs at least this many distinctive tokens for answer-overlap to
# be a meaningful signal; shorter chunks (e.g. a bare heading) score `None`.
_MIN_SUPPORT_TOKENS = 4

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


def _query_term_weights(request: GenerationRequest) -> dict[str, float]:
    """Weight each distinctive query term by how well it *discriminates*
    between the retrieved sections.

    The heading match must reward a genuine section-title hit ("Problem
    Statement" for a question about the problem statement) far more than a
    heading that merely repeats the question's topic/entity ("3 BERT" in a
    paper about BERT). So a term that names the source document, or that
    turns up across most of the retrieved chunks, is topical background and
    earns ~no weight; a term that pins down a single retrieved section earns
    full weight.

    Pure function of the already-retrieved contexts: deterministic, bounded
    to [0, 1] per term, no model or LLM call.
    """
    query_tokens = _tokenize(request.query)
    if not query_tokens:
        return {}

    contexts = list(request.retrieval)
    n = len(contexts)
    if n == 0:
        return {term: 1.0 for term in query_tokens}

    source_tokens: set[str] = set()
    per_context_tokens: list[set[str]] = []
    for context in contexts:
        source_tokens |= _tokenize(context.source)
        per_context_tokens.append(
            _tokenize(context.text)
            | _tokenize(" ".join(context.heading_path or []))
            | _tokenize(context.section)
        )

    weights: dict[str, float] = {}
    for term in query_tokens:
        if term in source_tokens:
            # Names the document's subject, not a particular section.
            weights[term] = 0.0
            continue
        df = sum(1 for tokens in per_context_tokens if term in tokens)
        if df == 0:
            weights[term] = 0.0
            continue
        # 1.0 when the term is unique to one retrieved chunk, → 0.0 when it
        # appears in every retrieved chunk.
        weights[term] = max(0.0, min(1.0, 1.0 - (df - 1) / max(n - 1, 1)))
    return weights


def _heading_match(term_weights: dict[str, float], citation: Citation) -> float:
    """Weighted fraction of the question's *discriminative* terms carried by
    this chunk's own heading/section (see `_query_term_weights`).

    A section whose heading only repeats the topic entity scores ~0; a
    section whose title genuinely names what the question asks for scores
    near 1. Zero when there is nothing to compare -- never negative, never
    fabricated, it only reads structural metadata produced by chunking.
    """
    total = sum(term_weights.values())
    if total <= 0.0:
        return 0.0
    heading_tokens = _tokenize(" ".join(citation.heading_path or []))
    heading_tokens |= _tokenize(citation.section)
    if not heading_tokens:
        return 0.0
    matched = sum(
        weight
        for term, weight in term_weights.items()
        if term in heading_tokens
    )
    return matched / total


def _answer_support(answer_tokens: set[str], chunk_text: str | None) -> float | None:
    """Deterministic answer/evidence alignment signal: the fraction of the
    chunk's own distinctive vocabulary that reappears in the generated
    answer. High when the answer clearly drew on this chunk, ~0 when the
    chunk was retrieved but unused.

    Returns `None` (not `0.0`) when it cannot be measured -- no answer, or a
    chunk too short to score reliably -- so callers never treat an
    unmeasured chunk as "unsupported".
    """
    if not answer_tokens:
        return None
    chunk_tokens = _tokenize(chunk_text)
    if len(chunk_tokens) < _MIN_SUPPORT_TOKENS:
        return None
    return len(chunk_tokens & answer_tokens) / len(chunk_tokens)


def _citation_relevance(
    term_weights: dict[str, float],
    citation: Citation,
) -> float:
    """Blends the three distinct notions of relevance, all bounded so this
    only re-orders already-retrieved evidence:

    - retrieval relevance   -> `citation.score` (the reranker score, base)
    - citation relevance    -> `_heading_match`: the chunk's section *title*
                               names what the question asks for (a heading
                               that merely repeats the topic/entity is
                               discounted via `_query_term_weights`)
    - claim/evidence align. -> `citation.answer_support` (answer draws on it)

    It never changes what was retrieved or what generation consumed.
    """

    base = citation.score if citation.score is not None else 0.0
    base += _heading_match(term_weights, citation) * _HEADING_MATCH_WEIGHT
    if citation.answer_support is not None:
        base += citation.answer_support * _ANSWER_SUPPORT_WEIGHT
    return base


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

        citations = self.citations_for(request, response)

        return GenerationResponse(
            answer=response,
            citations=citations,
        )

    @staticmethod
    def citations_for(
        request: GenerationRequest,
        answer: str | None = None,
    ) -> list[Citation]:
        """Build clean, deduplicated citations from retrieved provenance,
        ordered by citation relevance rather than raw reranker order.

        Retrieval/reranker order answers "what is semantically close to the
        query"; citation order answers "which retrieved chunk is the
        question's own dedicated evidence, and which did the answer actually
        use". Citations are re-sorted using `_citation_relevance` (reranker
        score + bounded heading-match + bounded answer-grounding bonuses).

        `answer` is optional and additive: when omitted, behaviour is
        identical to the query-only ordering (backward compatible for any
        caller that has no answer yet). Generation itself is never affected
        -- it consumes `request.retrieval` directly in its reranked order.
        No chunk is dropped, merged, or given another chunk's metadata.
        """
        answer_tokens = _tokenize(answer)

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
                answer_support=_answer_support(answer_tokens, context.text),
            ))

        term_weights = _query_term_weights(request)
        # `sort` is stable: citations with equal relevance keep their
        # original (reranked) relative order.
        citations.sort(
            key=lambda citation: _citation_relevance(term_weights, citation),
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
