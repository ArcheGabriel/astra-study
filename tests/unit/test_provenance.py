"""Provenance propagation: Docling → block → chunk → vector payload →
retrieval context → citation → normal & streaming API responses.

Docling is faked so these tests never download ML models.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.ai.pipeline import AIPipeline
from app.chunking.models import ChunkMetadata, DocumentChunk
from app.chunking.pipeline import ChunkPipeline
from app.document.models import BlockProvenance
from app.embeddings.models import (
    EmbeddedChunk,
    EmbeddingMetadata,
    EmbeddingVector,
)
from app.enums.block import BlockType
from app.enums.message import MessageRole
from app.generation.models import GenerationRequest
from app.generation.service import GenerationService
from app.ingestion.processors.docling import DoclingProcessor
from app.retrieval.models import RetrievedContext, RetrievalResult
from app.retrieval.service import RetrievalService
from app.search.dense.mapper import DenseMapper
from app.search.hybrid.mapper import HybridMapper


# ---------------------------------------------------------------------------
# Docling fakes
# ---------------------------------------------------------------------------


class FakeBBox:
    def __init__(self, l, t, r, b, coord_origin="TOPLEFT"):
        self.l, self.t, self.r, self.b = l, t, r, b
        self.coord_origin = SimpleNamespace(value=coord_origin)


class FakeProv:
    def __init__(self, page_no=None, bbox=None, charspan=None):
        self.page_no = page_no
        self.bbox = bbox
        self.charspan = charspan


class FakeItem:
    def __init__(self, label, text="", prov=None, parent=None, self_ref="#/texts/0"):
        self.label = SimpleNamespace(value=label)
        self.text = text
        self.prov = prov or []
        self.parent = parent
        self.self_ref = self_ref

    def export_to_markdown(self, doc):
        return self.text


class FakeDocument:
    def __init__(self, items):
        self.name = "fixture"
        self.pages = {1: object()}
        self._items = items

    def iterate_items(self):
        return iter(self._items)


class FakeConverter:
    def __init__(self, document):
        self.document = document

    def convert(self, path):
        return SimpleNamespace(document=self.document)


def _extract(tmp_path, name, items):
    path = tmp_path / name
    path.write_bytes(b"fixture")
    return DoclingProcessor(FakeConverter(FakeDocument(items))).extract(path)


# ---------------------------------------------------------------------------
# 1. PDF → page + bbox provenance
# ---------------------------------------------------------------------------


def test_pdf_page_and_bbox_provenance(tmp_path):
    bbox = FakeBBox(10, 20, 30, 40)
    result = _extract(
        tmp_path,
        "paper.pdf",
        [
            (FakeItem("section_header", "1 Introduction",
                      prov=[FakeProv(page_no=2)], self_ref="#/texts/0"), 1),
            (FakeItem("paragraph", "Grounded content.",
                      prov=[FakeProv(page_no=2, bbox=bbox, charspan=(0, 17))],
                      self_ref="#/texts/1"), 2),
        ],
    )

    para = result.blocks[1]
    assert para.page_number == 2
    ref = para.provenance[0]
    assert ref.page_number == 2
    assert ref.bbox == {
        "left": 10.0, "top": 20.0, "right": 30.0, "bottom": 40.0,
        "coord_origin": "TOPLEFT",
    }
    assert ref.charspan == (0, 17)
    assert ref.source_item_id == "#/texts/1"


# ---------------------------------------------------------------------------
# 2. DOCX → heading / section, no invented page
# ---------------------------------------------------------------------------


def test_docx_heading_section_without_page(tmp_path):
    result = _extract(
        tmp_path,
        "report.docx",
        [
            (FakeItem("section_header", "Executive Summary", self_ref="#/texts/0"), 1),
            (FakeItem("paragraph", "Key findings for the quarter.", self_ref="#/texts/1"), 2),
        ],
    )

    chunks = ChunkPipeline().run(result)
    body = chunks[-1].metadata
    assert body.page_start is None
    assert body.section_title == "Executive Summary"
    assert body.heading_path == ["Executive Summary"]
    assert body.source_type == ".docx"
    assert body.parser == "docling"


# ---------------------------------------------------------------------------
# 3. XLSX → sheet provenance, no page
# ---------------------------------------------------------------------------


def test_xlsx_sheet_provenance(tmp_path):
    sheet = SimpleNamespace(label=SimpleNamespace(value="sheet"), name="Segments")
    parent = SimpleNamespace(resolve=lambda document: sheet)
    result = _extract(
        tmp_path,
        "metrics.xlsx",
        [(FakeItem("table", "| Segment | Revenue |", parent=parent, self_ref="#/tables/0"), 1)],
    )

    block = result.blocks[0]
    assert block.block_type is BlockType.TABLE
    assert block.metadata["sheet_name"] == "Segments"
    assert block.provenance[0].sheet_name == "Segments"
    assert block.provenance[0].table_index == 0
    assert block.page_number is None

    chunk = ChunkPipeline().run(result)[0]
    assert chunk.metadata.sheet_name == "Segments"
    assert chunk.metadata.page_start is None


# ---------------------------------------------------------------------------
# 4. Image / OCR → bbox provenance survives
# ---------------------------------------------------------------------------


def test_image_ocr_bbox_provenance(tmp_path):
    bbox = FakeBBox(1, 2, 3, 4, coord_origin="BOTTOMLEFT")
    result = _extract(
        tmp_path,
        "scan.png",
        [(FakeItem("paragraph", "Text recovered by OCR.",
                   prov=[FakeProv(page_no=1, bbox=bbox)], self_ref="#/texts/0"), 1)],
    )

    # Images are not paginated in this architecture, but the raw bbox / item id
    # from the OCR pipeline is still preserved on the provenance record.
    ref = result.blocks[0].provenance[0]
    assert ref.bbox["coord_origin"] == "BOTTOMLEFT"
    assert ref.source_item_id == "#/texts/0"
    assert result.blocks[0].page_number is None


# ---------------------------------------------------------------------------
# 5. Chunking does not lose provenance
# ---------------------------------------------------------------------------


def test_chunking_preserves_provenance(tmp_path):
    paragraph = (
        "Detailed methodology text that is long enough to remain its own "
        "chunk throughout the pipeline without being merged away. " * 3
    )
    result = _extract(
        tmp_path,
        "notes.pdf",
        [
            (FakeItem("paragraph", paragraph,
                      prov=[FakeProv(page_no=3, bbox=FakeBBox(5, 6, 7, 8), charspan=(0, 40))],
                      self_ref="#/texts/1"), 1),
        ],
    )

    chunk = ChunkPipeline().run(result)[0]
    pages = {ref.page_number for ref in chunk.metadata.provenance}
    assert pages == {3}
    assert chunk.metadata.page_start == 3
    ref = chunk.metadata.provenance[0]
    assert ref.bbox["left"] == 5.0
    assert ref.source_item_id == "#/texts/1"


# ---------------------------------------------------------------------------
# 6. Vector payload preserves citation metadata (dense + hybrid)
# ---------------------------------------------------------------------------


def _embedded(metadata: ChunkMetadata) -> EmbeddedChunk:
    return EmbeddedChunk(
        DocumentChunk("chunk text", 0, metadata),
        EmbeddingVector([0.1, 0.2]),
        EmbeddingMetadata("test-model", 2),
    )


@pytest.mark.parametrize("build", [
    lambda e: DenseMapper.to_point(e).payload,
    lambda e: HybridMapper.build_payload(e),
])
def test_vector_payload_preserves_provenance(build):
    metadata = ChunkMetadata(
        document_uuid=uuid4(), chunk_uuid=uuid4(), document_name="metrics.xlsx",
        source="metrics.xlsx", source_type=".xlsx", parser="docling",
        sheet_name="Segments", section_title="Customers", heading_path=["Customers"],
        block_type=BlockType.TABLE, page_start=None, page_end=None,
        provenance=[BlockProvenance(page_number=None, sheet_name="Segments", table_index=0)],
    )
    payload = build(_embedded(metadata))
    assert payload["source"] == "metrics.xlsx"
    assert payload["parser"] == "docling"
    assert payload["sheet_name"] == "Segments"
    assert payload["heading_path"] == ["Customers"]
    assert payload["provenance"][0]["table_index"] == 0


# ---------------------------------------------------------------------------
# 7. Retrieval forwards citation metadata (incl. page_end + parser)
# ---------------------------------------------------------------------------


def _reranked(*payloads):
    results = []
    for payload in payloads:
        result = SimpleNamespace(
            text=payload["text"], chunk_uuid=uuid4(), score=0.9, payload=payload,
        )
        results.append(SimpleNamespace(result=result, reranker_score=0.77))
    return SimpleNamespace(results=results)


def test_retrieval_forwards_provenance_fields():
    service = RetrievalService(MagicMock(), MagicMock())
    contexts = service._build_contexts(reranked=_reranked({
        "text": "Body text.", "source": "paper.pdf", "page_start": 4, "page_end": 5,
        "section_title": "Results", "source_type": ".pdf", "parser": "docling",
        "heading_path": ["Results"], "block_type": "text",
        "provenance": [{"page_number": 4}],
    }))
    ctx = contexts[0]
    assert (ctx.page, ctx.page_end, ctx.parser) == (4, 5, "docling")
    assert ctx.section == "Results"
    assert ctx.provenance == [{"page_number": 4}]


# ---------------------------------------------------------------------------
# 8/10. citations_for: fields populated, distinct chunks stay traceable
# ---------------------------------------------------------------------------


def _context(**kw):
    base = dict(
        text="excerpt body", source="doc.pdf", chunk_uuid=uuid4(),
        retrieval_score=0.5, reranker_score=0.8,
    )
    base.update(kw)
    return RetrievedContext(**base)


def test_citations_for_populates_new_fields():
    ctx = _context(page=2, page_end=3, section="Intro", parser="docling",
                   source_type=".pdf", provenance=[{"page_number": 2}])
    citation = GenerationService.citations_for(
        GenerationRequest("q", RetrievalResult("q", [ctx], 0.1))
    )[0]
    assert (citation.page, citation.page_end, citation.parser) == (2, 3, "docling")
    assert citation.score == 0.8
    assert citation.excerpt == "excerpt body"
    assert citation.provenance == [{"page_number": 2}]


def test_distinct_chunks_same_section_stay_individually_traceable():
    a = _context(page=1, section="Overview", provenance=[{"page_number": 1}])
    b = _context(page=2, section="Overview", provenance=[{"page_number": 2}])
    citations = GenerationService.citations_for(
        GenerationRequest("q", RetrievalResult("q", [a, b], 0.1))
    )
    assert len(citations) == 2
    assert citations[0].chunk_id != citations[1].chunk_id
    assert citations[0].page == 1 and citations[1].page == 2
    # No cross-inheritance of page / provenance.
    assert citations[0].provenance == [{"page_number": 1}]
    assert citations[1].provenance == [{"page_number": 2}]


def test_exact_duplicate_context_is_collapsed():
    shared = uuid4()
    a = _context(chunk_uuid=shared, page=1, section="Overview")
    b = _context(chunk_uuid=shared, page=1, section="Overview")
    citations = GenerationService.citations_for(
        GenerationRequest("q", RetrievalResult("q", [a, b], 0.1))
    )
    assert len(citations) == 1


# ---------------------------------------------------------------------------
# 9. Normal and streaming pipeline both emit the same citations
# ---------------------------------------------------------------------------


class _FakeGeneration:
    citations_for = staticmethod(GenerationService.citations_for)

    def generate(self, request):
        from app.generation.models import GenerationResponse
        return GenerationResponse(answer="answer", citations=self.citations_for(request))

    def stream(self, request):
        yield "ans"
        yield "wer"


def _pipeline(retrieval_result):
    retrieval = MagicMock()
    retrieval.retrieve.return_value = retrieval_result
    return AIPipeline(retrieval, _FakeGeneration(), MagicMock())


def _conversation():
    return [SimpleNamespace(role=MessageRole.USER, content="What are the results?")]


def test_normal_pipeline_returns_citations():
    ctx = _context(page=7, section="Results", parser="docling")
    pipeline = _pipeline(RetrievalResult("q", [ctx], 0.1))
    response = pipeline.generate_response(conversation=_conversation(), user_id=1)
    assert response.citations[0].page == 7
    assert response.citations[0].section == "Results"


def test_streaming_pipeline_emits_citations_after_text():
    ctx = _context(page=7, section="Results", parser="docling")
    pipeline = _pipeline(RetrievalResult("q", [ctx], 0.1))
    events = list(pipeline.stream_response(conversation=_conversation(), user_id=1))

    text_events = [e for e in events if e.text is not None]
    citation_events = [e for e in events if e.citations is not None]
    assert "".join(e.text for e in text_events) == "answer"
    assert len(citation_events) == 1
    assert events[-1] is citation_events[0]
    assert citation_events[0].citations[0].page == 7


# ---------------------------------------------------------------------------
# Citation relevance: structural heading match vs raw reranker score
#
# Regression coverage for the real-world failure case: a broad section
# (e.g. "Executive Summary") can score marginally higher with the
# reranker than the question's own dedicated subsection, purely because it
# restates the topic in general terms. citations_for() must not simply
# mirror reranker order -- it should prefer the chunk whose own heading
# directly echoes the question, without dropping, merging or fabricating
# any evidence.
# ---------------------------------------------------------------------------


def test_citation_prefers_dedicated_section_over_higher_scored_summary():
    executive_summary = _context(
        text=(
            "InterviewAce AI helps candidates prepare for interviews by "
            "addressing common preparation challenges end to end."
        ),
        source="INTERVIEWACE AI Report.docx",
        section="Executive Summary",
        heading_path=["Executive Summary"],
        source_type=".docx", parser="docling",
        reranker_score=0.98,
    )
    problem_statement = _context(
        text=(
            "Candidates preparing for technical interviews struggle to get "
            "realistic, structured practice, which is the core problem this "
            "product addresses."
        ),
        source="INTERVIEWACE AI Report.docx",
        section="1.2 Problem Statement",
        heading_path=["1. Business Problem Statement", "1.2 Problem Statement"],
        source_type=".docx", parser="docling",
        reranker_score=0.94,
    )
    request = GenerationRequest(
        "What is the Business Problem Statement of InterviewAce AI?",
        RetrievalResult("q", [executive_summary, problem_statement], 0.1),
    )

    citations = GenerationService.citations_for(request)

    # Both chunks remain cited (no evidence dropped) ...
    assert {c.section for c in citations} == {"Executive Summary", "1.2 Problem Statement"}
    # ... but the dedicated section is preferred as the primary citation,
    # even though it had the lower reranker score.
    assert citations[0].section == "1.2 Problem Statement"
    assert citations[0].heading_path == [
        "1. Business Problem Statement", "1.2 Problem Statement",
    ]


def test_citation_prefers_dedicated_subsection_generalized_case():
    """Analogous case with different headings, proving the mechanism is not
    hardcoded to any particular phrase or document."""

    executive_summary = _context(
        text="The product serves a broad range of job seekers across industries.",
        source="report.docx", section="Executive Summary",
        heading_path=["Executive Summary"], reranker_score=0.97,
    )
    primary_segment = _context(
        text="The primary customer segment is early-career software engineers.",
        source="report.docx", section="2.1 Primary Customer Segment",
        heading_path=["2. Target Customer Segment", "2.1 Primary Customer Segment"],
        reranker_score=0.93,
    )
    request = GenerationRequest(
        "What is the Primary Customer Segment?",
        RetrievalResult("q", [executive_summary, primary_segment], 0.1),
    )

    citations = GenerationService.citations_for(request)

    assert citations[0].section == "2.1 Primary Customer Segment"
    assert len(citations) == 2


def test_citation_order_unchanged_when_no_heading_signal():
    """Without any structural overlap with the query, citation order must
    fall back to (and preserve) the original reranker order."""

    a = _context(text="alpha", source="doc.pdf", page=1,
                 section="Alpha", heading_path=["Alpha"], reranker_score=0.9)
    b = _context(text="beta", source="doc.pdf", page=2,
                 section="Beta", heading_path=["Beta"], reranker_score=0.7)
    c = _context(text="gamma", source="doc.pdf", page=3,
                 section="Gamma", heading_path=["Gamma"], reranker_score=0.5)
    request = GenerationRequest(
        "Summarize the document for me please",
        RetrievalResult("q", [a, b, c], 0.1),
    )

    citations = GenerationService.citations_for(request)
    assert [c.page for c in citations] == [1, 2, 3]


def test_citation_order_is_deterministic_across_runs():
    ctx_a = _context(section="Executive Summary", heading_path=["Executive Summary"],
                      reranker_score=0.9)
    ctx_b = _context(section="1.2 Problem Statement",
                      heading_path=["1. Business Problem Statement", "1.2 Problem Statement"],
                      reranker_score=0.85)
    request = GenerationRequest(
        "What is the business problem statement?",
        RetrievalResult("q", [ctx_a, ctx_b], 0.1),
    )

    first = [c.chunk_id for c in GenerationService.citations_for(request)]
    second = [c.chunk_id for c in GenerationService.citations_for(request)]
    assert first == second


def test_excerpt_truncates_on_word_boundary_and_never_mixes_chunks():
    long_text = "word " * 200  # far beyond the excerpt limit
    ctx = _context(text=long_text)
    citation = GenerationService.citations_for(
        GenerationRequest("q", RetrievalResult("q", [ctx], 0.1))
    )[0]

    assert citation.excerpt is not None
    assert citation.excerpt.endswith("…")
    body = citation.excerpt[:-1].rstrip()
    # The excerpt must be an exact prefix of the source chunk's own text --
    # never a splice of another chunk's text -- and must not end mid-word.
    assert long_text.startswith(body)
    assert not body or long_text[len(body)] in (" ", "")


def test_missing_metadata_is_never_fabricated_in_citations():
    ctx = _context(page=None, page_end=None, section=None, sheet_name=None,
                    heading_path=None, parser=None, provenance=None)
    citation = GenerationService.citations_for(
        GenerationRequest("q", RetrievalResult("q", [ctx], 0.1))
    )[0]
    assert citation.page is None
    assert citation.page_end is None
    assert citation.section is None
    assert citation.sheet_name is None
    assert citation.heading_path is None
    assert citation.parser is None
    assert citation.provenance is None


# ---------------------------------------------------------------------------
# Answer/evidence alignment: deterministic answer-grounding of citations
#
# `citations_for` can optionally receive the generated answer. When it does,
# citations that the answer actually draws on are surfaced first, without
# dropping, merging, or fabricating any evidence. When it does not, ordering
# is byte-identical to the query-only behaviour (backward compatible).
# ---------------------------------------------------------------------------


def test_answer_grounding_reorders_toward_evidence_the_answer_used():
    unused = _context(
        text="Alpha section covers deployment pipelines and infrastructure automation tooling.",
        source="doc.pdf", page=1, section="Alpha", heading_path=["Alpha"],
        reranker_score=0.9,
    )
    used = _context(
        text="Beta section states the mitochondrion is the powerhouse of the cell producing ATP.",
        source="doc.pdf", page=2, section="Beta", heading_path=["Beta"],
        reranker_score=0.9,
    )
    request = GenerationRequest(
        "Tell me about cell biology",  # no overlap with either heading
        RetrievalResult("q", [unused, used], 0.1),
    )
    answer = "The mitochondrion is the powerhouse of the cell and produces ATP for the cell."

    citations = GenerationService.citations_for(request, answer)

    assert {c.page for c in citations} == {1, 2}          # nothing dropped
    assert citations[0].page == 2                          # answer-grounded chunk first
    assert citations[0].answer_support > citations[1].answer_support


def test_answer_support_is_measured_only_when_an_answer_is_supplied():
    ctx = _context(
        text="The primary customer segment is early-career software engineers worldwide.",
    )
    with_answer = GenerationService.citations_for(
        GenerationRequest("q", RetrievalResult("q", [ctx], 0.1)),
        "Early-career software engineers are the primary customer segment.",
    )[0]
    without_answer = GenerationService.citations_for(
        GenerationRequest("q", RetrievalResult("q", [ctx], 0.1)),
    )[0]

    assert isinstance(with_answer.answer_support, float)
    assert 0.0 <= with_answer.answer_support <= 1.0
    assert without_answer.answer_support is None


def test_citation_order_unchanged_without_answer_and_for_unrelated_answer():
    a = _context(text="alpha body text that is reasonably long for scoring", page=1,
                 section="Alpha", heading_path=["Alpha"], reranker_score=0.9)
    b = _context(text="beta body text that is reasonably long for scoring", page=2,
                 section="Beta", heading_path=["Beta"], reranker_score=0.7)
    request = GenerationRequest(
        "an unrelated question about zebra migration",
        RetrievalResult("q", [a, b], 0.1),
    )

    assert [c.page for c in GenerationService.citations_for(request)] == [1, 2]
    # An answer that overlaps neither chunk must not perturb the order.
    assert [
        c.page for c in GenerationService.citations_for(request, "zebras are striped animals")
    ] == [1, 2]


def test_answer_grounding_scores_short_chunks_as_none_not_zero():
    """A bare heading chunk is too short to score -- it must come back `None`
    (unmeasured), never a fabricated 0.0 that labels it 'unsupported'."""

    ctx = _context(text="Abstract", section="Abstract", heading_path=["Abstract"])
    citation = GenerationService.citations_for(
        GenerationRequest("q", RetrievalResult("q", [ctx], 0.1)),
        "Abstract discussion of BERT and its bidirectional transformer pretraining.",
    )[0]
    assert citation.answer_support is None


def test_answer_grounding_keeps_chunks_distinct_and_provenance_intact():
    a = _context(
        text="Bidirectional encoder representations from transformers pretrained with a masked language model.",
        page=1, section="3 BERT", heading_path=["3 BERT"],
        provenance=[{"page_number": 1}], reranker_score=0.9,
    )
    b = _context(
        text="Comparison of BERT, ELMo and OpenAI GPT across downstream benchmark tasks and datasets.",
        page=14, section="A.4 Comparison", heading_path=["A.4 Comparison"],
        provenance=[{"page_number": 14}], reranker_score=0.9,
    )
    answer = (
        "The model uses bidirectional encoder representations from transformers, "
        "pretrained with a masked language model objective."
    )
    citations = GenerationService.citations_for(
        GenerationRequest("explain the pretraining approach", RetrievalResult("q", [a, b], 0.1)),
        answer,
    )

    assert len(citations) == 2
    by_page = {c.page: c for c in citations}
    assert by_page[1].provenance == [{"page_number": 1}]     # not merged / swapped
    assert by_page[14].provenance == [{"page_number": 14}]
    assert citations[0].page == 1                             # the chunk the answer used


class _FakeStreamGen:
    citations_for = staticmethod(GenerationService.citations_for)

    def __init__(self, chunks: list[str]) -> None:
        self._chunks = chunks

    def stream(self, request):
        yield from self._chunks


def test_streaming_citations_reflect_the_streamed_answer():
    off_topic = _context(
        text="Alpha section about deployment pipelines and infrastructure automation tooling.",
        page=1, section="Alpha", heading_path=["Alpha"], reranker_score=0.9,
    )
    on_topic = _context(
        text="Beta section states the mitochondrion is the powerhouse of the cell producing ATP.",
        page=2, section="Beta", heading_path=["Beta"], reranker_score=0.9,
    )
    retrieval = MagicMock()
    retrieval.retrieve.return_value = RetrievalResult("q", [off_topic, on_topic], 0.1)
    pipeline = AIPipeline(
        retrieval,
        _FakeStreamGen(["The mitochondrion ", "is the powerhouse ", "of the cell."]),
        MagicMock(),
    )

    events = list(pipeline.stream_response(conversation=_conversation(), user_id=1))
    citation_events = [e for e in events if e.citations is not None]

    assert len(citation_events) == 1
    assert events[-1] is citation_events[0]            # SSE order unchanged
    assert citation_events[0].citations[0].page == 2   # grounded in the streamed text


# ---------------------------------------------------------------------------
# Intent-weighted heading match: a heading that merely repeats the question's
# topic/entity must not score like a heading that genuinely names the answer.
#
#   "What is BERT?"   -> "BERT" is the topic. A section titled "3 BERT" is
#                        not automatically the best citation; the Abstract is.
#   "What is the Primary Customer Segment?" -> "Primary Customer Segment" is
#                        a real section title and must still win.
# ---------------------------------------------------------------------------


def test_query_term_weights_discount_topic_terms_and_reward_distinctive_ones():
    from app.generation.service import _query_term_weights

    contexts = [
        _context(text="BERT is a transformer model for language understanding.",
                 source="BERT.pdf", section="Abstract", heading_path=["Abstract"]),
        _context(text="BERT uses a masked language model objective during pretraining.",
                 source="BERT.pdf", section="1 Introduction", heading_path=["1 Introduction"]),
        _context(text="We evaluate BERT on the SQuAD question answering benchmark.",
                 source="BERT.pdf", section="4.2 SQuAD",
                 heading_path=["4 Experiments", "4.2 SQuAD"]),
    ]
    weights = _query_term_weights(
        GenerationRequest(
            "What is BERT's performance on SQuAD?",
            RetrievalResult("q", contexts, 0.1),
        )
    )

    assert weights.get("bert", 0.0) == 0.0        # in the file name + every chunk -> topic
    assert weights.get("performance", 0.0) == 0.0  # appears in no retrieved chunk
    assert weights["squad"] == 1.0                # pins down exactly one section


def test_topic_entity_in_a_heading_does_not_outrank_the_definitional_section():
    architecture = _context(
        text=(
            "BERT's model architecture is a multi-layer bidirectional Transformer "
            "encoder. We denote the number of layers as L and the hidden size as H."
        ),
        source="BERT.pdf", page=3, page_end=4,
        section="3 BERT", heading_path=["3 BERT"],
        source_type=".pdf", parser="docling", reranker_score=0.8884,
    )
    abstract = _context(
        text=(
            "We introduce a new language representation model called BERT. BERT is "
            "designed to pre-train deep bidirectional representations from unlabeled "
            "text by jointly conditioning on both left and right context."
        ),
        source="BERT.pdf", page=1,
        section="Abstract", heading_path=["Abstract"],
        source_type=".pdf", parser="docling", reranker_score=0.9946,
    )
    introduction = _context(
        text=(
            "Language model pre-training has been effective. BERT alleviates the "
            "unidirectionality constraint using a masked language model objective."
        ),
        source="BERT.pdf", page=1, page_end=2,
        section="1 Introduction", heading_path=["1 Introduction"],
        source_type=".pdf", parser="docling", reranker_score=0.9744,
    )
    request = GenerationRequest(
        "What is BERT?",
        RetrievalResult("q", [architecture, abstract, introduction], 0.1),
    )

    citations = GenerationService.citations_for(request)

    # Nothing dropped.
    assert {c.section for c in citations} == {"3 BERT", "Abstract", "1 Introduction"}
    # "3 BERT" no longer gets a heading bonus just for repeating the entity,
    # so the definitional sources (ordered by their own reranker score) win.
    assert citations[0].section == "Abstract"
    assert citations[-1].section == "3 BERT"


def test_distinctive_heading_term_still_earns_the_bonus():
    """Proves the heading signal is discounted, not disabled: a title that
    carries a term unique to one retrieved section still outranks a
    higher-reranked generic section."""

    generic = _context(
        text="This report covers the whole product end to end for every reader.",
        source="report.docx", section="Executive Summary",
        heading_path=["Executive Summary"], reranker_score=0.97,
    )
    dedicated = _context(
        text=(
            "The onboarding flow walks a new user through account setup, resume "
            "upload and their first mock interview."
        ),
        source="report.docx", section="4.3 Onboarding Flow",
        heading_path=["4. User Experience", "4.3 Onboarding Flow"],
        reranker_score=0.90,
    )
    request = GenerationRequest(
        "What does the onboarding flow look like?",
        RetrievalResult("q", [generic, dedicated], 0.1),
    )

    citations = GenerationService.citations_for(request)
    assert citations[0].section == "4.3 Onboarding Flow"
    assert len(citations) == 2


def test_enumeration_query_prefers_the_section_that_names_the_set():
    executive = _context(
        text="InterviewAce AI provides end-to-end interview preparation for job seekers.",
        source="INTERVIEWACE AI Report.docx", section="Executive Summary",
        heading_path=["Executive Summary"], reranker_score=0.95,
    )
    agents = _context(
        text=(
            "InterviewAce AI includes four agents: the Resume Agent, the Interview "
            "Agent, the Feedback Agent and the Scheduling Agent, each with a "
            "distinct responsibility."
        ),
        source="INTERVIEWACE AI Report.docx", section="3. The Four AI Agents",
        heading_path=["3. The Four AI Agents"], reranker_score=0.90,
    )
    one_agent = _context(
        text="The Interview Agent conducts adaptive mock interviews and scores answers.",
        source="INTERVIEWACE AI Report.docx", section="3.2 Interview Agent",
        heading_path=["3. The Four AI Agents", "3.2 Interview Agent"],
        reranker_score=0.88,
    )
    request = GenerationRequest(
        "What are the four AI agents in InterviewAce AI?",
        RetrievalResult("q", [executive, agents, one_agent], 0.1),
    )

    citations = GenerationService.citations_for(request)
    assert citations[0].section == "3. The Four AI Agents"
    assert {c.section for c in citations} == {
        "Executive Summary", "3. The Four AI Agents", "3.2 Interview Agent",
    }


def test_intent_weighting_preserves_provenance_and_determinism():
    a = _context(
        text="Executive overview of the whole product for all stakeholders.",
        source="report.docx", page=2, section="Executive Summary",
        heading_path=["Executive Summary"], provenance=[{"page_number": 2}],
        reranker_score=0.96,
    )
    b = _context(
        text="Candidates lack realistic structured interview practice; that is the gap.",
        source="report.docx", page=5, section="1.2 Problem Statement",
        heading_path=["1. Business Problem Statement", "1.2 Problem Statement"],
        provenance=[{"page_number": 5}], reranker_score=0.92,
    )
    request = GenerationRequest(
        "What is the Business Problem Statement?",
        RetrievalResult("q", [a, b], 0.1),
    )

    first = GenerationService.citations_for(request)
    second = GenerationService.citations_for(request)

    assert [c.chunk_id for c in first] == [c.chunk_id for c in second]  # deterministic
    assert first[0].section == "1.2 Problem Statement"
    by_page = {c.page: c for c in first}
    assert by_page[2].provenance == [{"page_number": 2}]   # not merged / swapped
    assert by_page[5].provenance == [{"page_number": 5}]
