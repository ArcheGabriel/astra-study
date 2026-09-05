"""Chunk-quality contract tests (Phase 2).

Built incrementally alongside the chunker rework. STAGE 1 covers the
config single-source-of-truth, the section-id regex, section-id
propagation, ``section_key`` and heading-path de-duplication.

No models are downloaded: fixtures are plain ``DocumentChunk`` objects fed
straight into the stage under test.
"""

from __future__ import annotations

from copy import deepcopy

import pytest

from app.chunking.config import DEFAULT_CHUNKING_CONFIG, ChunkingConfig
from app.chunking.models import ChunkMetadata, DocumentChunk, section_contains
from app.chunking.stages.filter import FilterStage
from app.chunking.stages.merge import MergeStage
from app.chunking.stages.metadata import MetadataStage
from app.chunking.stages.quality import QualityStage
from app.chunking.stages.recursive import RecursiveStage
from app.chunking.stages.semantic import SemanticStage
from app.chunking.utils.tokens import count_tokens
from app.document.models import BlockProvenance
from app.enums.block import BlockType


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _prov(page: int | None = None, item: str = "#/x", charspan: tuple[int, int] | None = None) -> BlockProvenance:
    return BlockProvenance(page_number=page, source_item_id=item, charspan=charspan)


def _mk(
    text: str,
    block_type: BlockType,
    *,
    level: int = 0,
    page: int | None = None,
    block_index: int = 0,
    prov: list[BlockProvenance] | None = None,
) -> DocumentChunk:
    return DocumentChunk(
        text=text,
        chunk_index=block_index,
        metadata=ChunkMetadata(
            block_type=block_type,
            heading_level=level,
            page_start=page,
            page_end=page,
            block_start=block_index,
            block_end=block_index,
            provenance=list(prov or []),
        ),
    )


def _chunk(text: str, block_type: BlockType, *, heading_level: int = 0) -> DocumentChunk:
    return _mk(text, block_type, level=heading_level)


def _heading(text: str, level: int = 1, *, page: int | None = None, prov: list[BlockProvenance] | None = None) -> DocumentChunk:
    return _mk(text, BlockType.HEADING, level=level, page=page, prov=prov)


def _body(
    text: str = "Body sentence with enough words to be a paragraph.",
    *,
    page: int | None = None,
    prov: list[BlockProvenance] | None = None,
) -> DocumentChunk:
    return _mk(text, BlockType.TEXT, page=page, prov=prov)


def _run_metadata(chunks: list[DocumentChunk]) -> list[DocumentChunk]:
    return MetadataStage().run(
        [DocumentChunk(c.text, i, deepcopy(c.metadata)) for i, c in enumerate(chunks)]
    )


def _merge(chunks: list[DocumentChunk], config: ChunkingConfig | None = None) -> list[DocumentChunk]:
    """Run the first real stages that shape section chunks: Metadata -> Merge.

    Input chunks are deep-copied so a test list can be reused."""
    prepared = _run_metadata(chunks)
    return MergeStage(config).run(prepared)


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------


def test_chunking_config_is_the_single_source_of_token_limits():
    cfg = DEFAULT_CHUNKING_CONFIG
    # The values the stages historically hard-coded, now centralised and
    # deliberately NOT tuned in this phase.
    assert (cfg.embed_max, cfg.overlap, cfg.merge_min) == (700, 100, 120)
    assert (cfg.section_soft, cfg.section_hard) == (1200, 1600)
    # Frozen so a stage cannot mutate the shared default.
    with pytest.raises(Exception):
        cfg.embed_max = 999  # type: ignore[misc]


def test_chunking_config_override_is_possible_for_tests():
    cfg = ChunkingConfig(embed_max=400)
    assert cfg.embed_max == 400
    assert cfg.overlap == 100  # untouched fields keep their default


# ---------------------------------------------------------------------------
# section-id regex  (RC-3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "heading, expected",
    [
        ("1 Introduction", "1"),
        ("1. Introduction", "1"),
        ("1.2 Problem Statement", "1.2"),
        ("1.2. Problem Statement", "1.2"),
        ("2.1.3 Deeply Nested", "2.1.3"),
        ("10. Limitations", "10"),
        ("Executive Summary", None),          # unnumbered
        ("A.1 Illustration of the Tasks", None),  # letter-prefixed appendix
        ("1.2.3", None),                      # a bare number is not a heading
    ],
)
def test_section_id_regex_handles_latex_and_word_numbering(heading, expected):
    assert MetadataStage()._extract_section_id(heading) == expected


# ---------------------------------------------------------------------------
# section-id propagation  (RC-1)
# ---------------------------------------------------------------------------


def test_section_id_propagates_to_content_chunks():
    chunks = _run_metadata([
        _heading("3 BERT"),
        _body("We introduce BERT and its implementation."),
        _heading("3.1 Pre-training BERT"),
        _body("Unlike prior work, BERT is pre-trained on two tasks."),
        _body("The next-sentence-prediction task jointly pretrains pairs."),
    ])

    assert [c.metadata.section_id for c in chunks] == ["3", "3", "3.1", "3.1", "3.1"]
    # content chunks now carry their section's number -- previously all None
    assert chunks[1].metadata.section_id == "3"
    assert chunks[-1].metadata.section_id == "3.1"


def test_content_before_any_heading_keeps_null_section_id():
    chunks = _run_metadata([_body("Title page text, no heading yet."), _heading("1 Intro")])
    assert chunks[0].metadata.section_id is None
    assert chunks[0].metadata.section_key == ()


# ---------------------------------------------------------------------------
# section_key nesting  (RC-2)
# ---------------------------------------------------------------------------


def test_section_key_encodes_hierarchy():
    chunks = _run_metadata([
        _heading("1 Business Problem"),
        _body("intro to the problem area"),
        _heading("1.1 Background"),
        _body("background paragraph"),
        _heading("1.2 Problem Statement"),
        _body("candidates lack realistic practice"),
    ])

    keys = [c.metadata.section_key for c in chunks]
    assert keys == [
        ("1",), ("1",),
        ("1", "1.1"), ("1", "1.1"),
        ("1", "1.2"), ("1", "1.2"),
    ]
    # 1.1 content and 1.2 content are siblings -> a hard boundary
    assert not section_contains(("1", "1.1"), ("1", "1.2"))
    # both are still inside section 1
    assert section_contains(("1",), ("1", "1.1"))
    assert section_contains(("1",), ("1", "1.2"))


def test_section_key_for_unnumbered_headings_uses_titles():
    chunks = _run_metadata([
        _heading("Executive Summary", level=1),
        _body("summary body"),
        _heading("Target Customers", level=1),
        _body("customer body"),
    ])
    assert chunks[1].metadata.section_key == ("Executive Summary",)
    assert chunks[3].metadata.section_key == ("Target Customers",)
    assert not section_contains(("Executive Summary",), ("Target Customers",))


def test_section_contains_relationships():
    assert section_contains((), ())                        # same (no section)
    assert not section_contains((), ("1",))                # entering first section = boundary
    assert section_contains(("1",), ("1",))                # same
    assert section_contains(("1",), ("1", "2"))            # descendant
    assert not section_contains(("1", "2"), ("1",))        # ancestor = boundary
    assert not section_contains(("1", "2"), ("1", "3"))    # sibling = boundary


# ---------------------------------------------------------------------------
# heading_path de-duplication  (RC-2 / P12)
# ---------------------------------------------------------------------------


def test_heading_path_collapses_consecutive_duplicate_titles():
    chunks = _run_metadata([
        _heading("Executive Summary", level=2),
        _heading("Executive Summary", level=3),   # Docling duplicate
        _body("the actual executive summary text"),
        _heading("Scope", level=3),               # genuine child of Executive Summary
        _body("scope text"),
    ])

    assert chunks[2].metadata.heading_path == ["Executive Summary"]
    assert chunks[2].metadata.section_title == "Executive Summary"
    # a genuine child still nests correctly under the (de-duplicated) parent
    assert chunks[4].metadata.heading_path == ["Executive Summary", "Scope"]


def test_non_consecutive_repeated_title_is_preserved():
    chunks = _run_metadata([
        _heading("Overview", level=1),
        _body("a"),
        _heading("Details", level=1),
        _body("b"),
        _heading("Overview", level=1),   # a real second "Overview" section
        _body("c"),
    ])
    assert chunks[5].metadata.heading_path == ["Overview"]
    assert chunks[1].metadata.section_key == ("Overview",)
    assert chunks[5].metadata.section_key == ("Overview",)


# ---------------------------------------------------------------------------
# determinism
# ---------------------------------------------------------------------------


def test_metadata_stage_is_deterministic():
    src = [
        _heading("1 Introduction"), _body("x"),
        _heading("1.1 Background"), _body("y"),
        _heading("2 Method"), _body("z"),
    ]
    first = [(c.metadata.section_id, c.metadata.section_key, tuple(c.metadata.heading_path))
             for c in _run_metadata(src)]
    second = [(c.metadata.section_id, c.metadata.section_key, tuple(c.metadata.heading_path))
              for c in _run_metadata(src)]
    assert first == second


# ===========================================================================
# STAGE 2 -- MergeStage: heading-anchored sections
# ===========================================================================


# --- A. heading + paragraph ------------------------------------------------


def test_heading_and_paragraph_fold_into_one_content_chunk():
    out = _merge([
        _heading("3 BERT"),
        _body("We introduce BERT and its detailed implementation in this section."),
    ])
    assert len(out) == 1
    c = out[0]
    assert c.text == (
        "3 BERT\n\nWe introduce BERT and its detailed implementation in this section."
    )
    assert c.metadata.block_type == BlockType.TEXT     # effective type, not HEADING
    assert c.metadata.section_title == "3 BERT"
    assert c.metadata.section_id == "3"
    assert c.metadata.heading_path == ["3 BERT"]
    assert c.metadata.section_key == ("3",)


# --- B. heading + multiple paragraphs -------------------------------------


def test_heading_and_multiple_paragraphs_form_one_section_with_unioned_provenance():
    out = _merge([
        _heading("2.1 Background", prov=[_prov(2, "#/h")]),
        _body("First background paragraph about representation learning.", page=2, prov=[_prov(2, "#/p1")]),
        _body("Second background paragraph continuing the discussion.", page=3, prov=[_prov(3, "#/p2")]),
    ])
    assert len(out) == 1
    c = out[0]
    assert "First background paragraph" in c.text and "Second background paragraph" in c.text
    assert [p.source_item_id for p in c.metadata.provenance] == ["#/h", "#/p1", "#/p2"]
    assert c.metadata.page_end == 3


def test_merge_keeps_provenance_from_every_contributing_block_in_order():
    out = _merge([
        _heading("1 S", prov=[_prov(1, "#/h1")]),
        _body("para a", page=1, prov=[_prov(1, "#/a")]),
        _body("para b", page=2, prov=[_prov(2, "#/b")]),
        _body("para c", page=2, prov=[_prov(2, "#/c")]),
    ])
    assert len(out) == 1
    assert [p.source_item_id for p in out[0].metadata.provenance] == ["#/h1", "#/a", "#/b", "#/c"]


# --- C. numbered heading never a standalone vector -----------------------


def test_numbered_heading_never_produces_a_standalone_heading_vector():
    out = _merge([
        _heading("3. BERT"),
        _body("BERT is designed to pre-train deep bidirectional representations."),
    ])
    assert len(out) == 1
    assert all(c.metadata.block_type != BlockType.HEADING for c in out)
    assert not any(c.text.strip() in ("3. BERT", "3 BERT") for c in out)


# --- D. sibling sections -------------------------------------------------


def test_sibling_sections_do_not_share_content():
    out = _merge([
        _heading("1 Section A"),
        _body("Alpha content about topic A that stands on its own."),
        _heading("2 Section B"),
        _body("Beta content about topic B that stands on its own."),
    ])
    assert len(out) == 2
    a, b = out
    assert a.metadata.section_key == ("1",)
    assert b.metadata.section_key == ("2",)
    assert "Alpha content" in a.text and "Beta content" not in a.text
    assert "Beta content" in b.text and "Alpha content" not in b.text


# --- E. nested sections ------------------------------------------------


def test_nested_sections_keep_parent_and_children_separate():
    out = _merge([
        _heading("1 Parent"),
        _body("Parent-level overview paragraph before any subsection."),
        _heading("1.1 Child"),
        _body("Child one paragraph with its own distinct content."),
        _heading("1.2 Child Two"),
        _body("Child two paragraph with different distinct content."),
    ])
    assert len(out) == 3
    parent, c1, c2 = out
    assert parent.metadata.section_key == ("1",)
    assert c1.metadata.section_key == ("1", "1.1")
    assert c2.metadata.section_key == ("1", "1.2")
    assert "Parent-level overview" in parent.text
    assert "Parent-level overview" not in c1.text and "Parent-level overview" not in c2.text
    assert "Child one paragraph" in c1.text and "Child one paragraph" not in c2.text
    assert "Child two paragraph" in c2.text and "Child two paragraph" not in c1.text
    assert c1.metadata.heading_path == ["1 Parent", "1.1 Child"]
    assert c2.metadata.heading_path == ["1 Parent", "1.2 Child Two"]
    assert all(c.metadata.block_type != BlockType.HEADING for c in out)


# --- F. consecutive headings ------------------------------------------


def test_consecutive_headings_drop_the_content_free_one():
    out = _merge([
        _heading("Overview", level=1),   # no content -> must vanish
        _heading("Details", level=1),
        _body("The details section body with real content here."),
    ])
    assert len(out) == 1
    assert out[0].metadata.section_title == "Details"
    assert out[0].text.startswith("Details\n\n")
    assert "Overview" not in out[0].text


# --- G. heading at EOF -----------------------------------------------


def test_trailing_heading_without_content_is_not_emitted():
    out = _merge([
        _heading("1 Intro"),
        _body("Intro body text with enough words to be a paragraph."),
        _heading("2 Appendix"),   # nothing after it
    ])
    assert len(out) == 1
    assert out[0].metadata.section_key == ("1",)


def test_document_of_only_headings_yields_no_chunks():
    out = _merge([_heading("A", level=1), _heading("B", level=1), _heading("C", level=1)])
    assert out == []


# --- H. effective block types ---------------------------------------


@pytest.mark.parametrize(
    "content_type",
    [BlockType.TEXT, BlockType.TABLE, BlockType.LIST, BlockType.CAPTION],
)
def test_effective_block_type_comes_from_first_non_heading_block(content_type):
    out = _merge([
        _heading("Section", level=1),
        _mk("the section's actual content body here", content_type, block_index=1),
    ])
    assert len(out) == 1
    assert out[0].metadata.block_type == content_type


# --- I. configuration ----------------------------------------------


def test_mergestage_reads_limits_from_chunking_config_not_local_constants():
    assert not hasattr(MergeStage, "SOFT_LIMIT")
    assert not hasattr(MergeStage, "HARD_LIMIT")
    assert MergeStage()._config.section_soft == 1200
    assert MergeStage()._config.section_hard == 1600


def test_mergestage_honours_a_custom_section_hard_limit():
    body = "word " * 80
    src = [
        _heading("1 Intro"),
        _body(body), _body(body), _body(body),
    ]
    default_out = _merge(src)
    tiny_out = _merge(src, ChunkingConfig(section_hard=30, section_soft=20))
    assert len(default_out) == 1               # merges under the real 1600 ceiling
    assert len(tiny_out) >= 2                  # force-split at the tiny ceiling


# --- J. determinism ----------------------------------------------


def test_merge_stage_is_deterministic():
    src = [
        _heading("1 A"), _body("alpha one"), _body("alpha two"),
        _heading("1.1 B"), _body("bravo one"),
        _heading("2 C"), _body("charlie one"),
    ]
    a = [(c.text, c.metadata.section_key, c.metadata.block_type) for c in _merge(src)]
    b = [(c.text, c.metadata.section_key, c.metadata.block_type) for c in _merge(src)]
    assert a == b


# --- InterviewAce-shaped regression (merge level) -----------------


def test_interviewace_shaped_numbered_sections_are_not_orphaned():
    out = _merge([
        _heading("Executive Summary", level=1),
        _body("A broad summary mentioning the business problem loosely."),
        _heading("1. Business Problem Statement", level=1),
        _body("Framing the problem area for candidates."),
        _heading("1.2 Problem Statement", level=1),
        _body("Candidates preparing for technical interviews lack realistic structured practice."),
    ])
    assert {c.metadata.section_title for c in out} == {
        "Executive Summary", "1. Business Problem Statement", "1.2 Problem Statement",
    }
    ps = next(c for c in out if c.metadata.section_title == "1.2 Problem Statement")
    assert "lack realistic structured practice" in ps.text
    assert "Framing the problem area" not in ps.text        # no parent-content leak
    assert ps.metadata.block_type == BlockType.TEXT
    assert ps.metadata.heading_path == ["1. Business Problem Statement", "1.2 Problem Statement"]
    assert all(c.metadata.block_type != BlockType.HEADING for c in out)


# ===========================================================================
# STAGE 3 -- RecursiveStage (provenance partition + heading prefix) & SemanticStage
# ===========================================================================


def _long(marker: str, n: int = 80) -> str:
    # marker-dense pseudo-sentences: every 6-word window contains the marker,
    # so no two different markers share a 6-gram (keeps the provenance
    # substring matcher honest in tests without relying on real prose).
    return " ".join(
        f"{marker}a{k} {marker}b {marker}c {marker}d{k} {marker}e {marker}f." for k in range(n)
    )


def _merged_section(
    blocks: list[tuple[str, int | None, str]],
    *,
    heading_path: list[str],
    section_key: tuple[str, ...],
    section_id: str | None = None,
    block_type: BlockType = BlockType.TEXT,
) -> DocumentChunk:
    """A MergeStage-style section chunk: ``blocks`` joined with blank lines
    (``blocks[0]`` is normally the folded heading), one provenance entry per
    block. ``block_type`` is the *effective* type MergeStage would have
    locked from the first non-heading contributor."""
    pages = [p for _, p, _ in blocks if p is not None]
    md = ChunkMetadata(
        block_type=block_type,
        heading_level=len(section_key) or 1,
        heading_path=list(heading_path),
        section_title=(heading_path[-1] if heading_path else None),
        section_id=section_id,
        section_key=tuple(section_key),
        block_start=0,
        block_end=len(blocks) - 1,
        page_start=(min(pages) if pages else None),
        page_end=(max(pages) if pages else None),
        provenance=[BlockProvenance(page_number=p, source_item_id=i) for _, p, i in blocks],
    )
    return DocumentChunk("\n\n".join(t for t, _, _ in blocks), 0, md)


def _md_table(header: list[str], n_rows: int) -> str:
    head = "| " + " | ".join(header) + " |"
    sep = "| " + " | ".join("---" for _ in header) + " |"
    rows = [
        "| " + " | ".join(f"cell{r}col{c}xyz" for c in range(len(header))) + " |"
        for r in range(n_rows)
    ]
    return "\n".join([head, sep, *rows])


def _recursive(chunk: DocumentChunk, config: ChunkingConfig | None = None) -> list[DocumentChunk]:
    return RecursiveStage(config).run([deepcopy(chunk)])


# --- C1. long section: heading prefix on every child --------------------


def test_oversized_section_prefixes_every_child_exactly_once():
    chunk = _merged_section(
        [
            ("2.1 Feature-based Approaches", 3, "#/h"),
            (_long("Alpha"), 3, "#/a"),
            (_long("Bravo"), 4, "#/b"),
            (_long("Charlie"), 4, "#/c"),
        ],
        heading_path=["2 Related Work", "2.1 Feature-based Approaches"],
        section_key=("2", "2.1"),
        section_id="2.1",
    )
    out = _recursive(chunk)

    assert len(out) >= 2
    for child in out:
        assert child.text.startswith("2.1 Feature-based Approaches\n\n")
        assert child.text.count("2.1 Feature-based Approaches") == 1
        assert count_tokens(child.text) <= DEFAULT_CHUNKING_CONFIG.embed_max
        assert child.metadata.heading_path == ["2 Related Work", "2.1 Feature-based Approaches"]
        assert child.metadata.section_key == ("2", "2.1")
        assert child.metadata.block_type == BlockType.TEXT
        assert child.parent_chunk == out[0].parent_chunk        # shared parent link
    # no heading-only vector
    assert not any("\n\n" not in c.text for c in out)


def test_content_only_continuation_gets_the_heading_prefix():
    # a MergeStage size-split continuation: heading_path is set but the text
    # does not begin with the heading.
    chunk = _merged_section(
        [
            (_long("Delta"), 5, "#/d"),
            (_long("Echo"), 5, "#/e"),
        ],
        heading_path=["3 BERT", "3.1 Pre-training BERT"],
        section_key=("3", "3.1"),
        section_id="3.1",
    )
    out = _recursive(chunk)
    for child in out:
        assert child.text.startswith("3.1 Pre-training BERT\n\n")
        assert child.text.count("3.1 Pre-training BERT") == 1


def test_deep_nesting_uses_the_deepest_two_headings_in_the_prefix():
    chunk = _merged_section(
        [
            ("1.1.2 Deep Topic", 1, "#/h"),
            (_long("Foxtrot"), 1, "#/f"),
            (_long("Golf"), 1, "#/g"),
        ],
        heading_path=["1 Parent", "1.1 Child", "1.1.2 Deep Topic"],
        section_key=("1", "1.1", "1.1.2"),
        section_id="1.1.2",
    )
    out = _recursive(chunk)
    assert len(out) >= 2
    for child in out:
        assert child.text.startswith("1.1 Child › 1.1.2 Deep Topic\n\n")
        assert child.text.count("Deep Topic") == 1
    # stored structural heading_path is untouched
    assert out[0].metadata.heading_path == ["1 Parent", "1.1 Child", "1.1.2 Deep Topic"]


# --- C2/C3/C4. provenance partition + page/block ranges ---------------


def test_oversized_section_partitions_provenance_and_ranges_per_child():
    chunk = _merged_section(
        [
            ("3.1 Pre-training BERT", 4, "#/h"),
            (_long("Alpha"), 4, "#/a"),
            (_long("Bravo"), 4, "#/b"),
            (_long("Charlie"), 5, "#/c"),
        ],
        heading_path=["3 BERT", "3.1 Pre-training BERT"],
        section_key=("3", "3.1"),
        section_id="3.1",
    )
    out = _recursive(chunk)
    assert len(out) >= 2

    first, last = out[0], out[-1]

    # not copied wholesale
    assert len(first.metadata.provenance) < 4
    assert len(last.metadata.provenance) < 4

    first_ids = [p.source_item_id for p in first.metadata.provenance]
    last_ids = [p.source_item_id for p in last.metadata.provenance]

    assert "#/h" in first_ids and "#/h" in last_ids           # heading prefix -> heading prov everywhere
    assert "#/a" in first_ids and "#/a" not in last_ids        # Alpha only near the start
    assert "#/c" in last_ids and "#/c" not in first_ids        # Charlie only near the end
    # order preserved (document order, no fabricated ids)
    assert first_ids == sorted(first_ids, key=["#/h", "#/a", "#/b", "#/c"].index)
    assert all(pid in {"#/h", "#/a", "#/b", "#/c"} for c in out for pid in [p.source_item_id for p in c.metadata.provenance])

    # page range from THIS child's provenance -- not the parent's 4-5
    assert (first.metadata.page_start, first.metadata.page_end) == (4, 4)
    assert last.metadata.page_end == 5

    # block range tight to contributing blocks (base = block_start 0 + 1 for the heading)
    assert first.metadata.block_start == 1                     # Alpha is block index 1
    assert last.metadata.block_end == 3                        # Charlie is block index 3
    assert first.metadata.block_start >= chunk.metadata.block_start
    assert last.metadata.block_end <= chunk.metadata.block_end


def test_child_provenance_matches_child_content_including_straddling_blocks():
    chunk = _merged_section(
        [
            ("S", 1, "#/h"),
            (_long("Alpha", 40), 1, "#/a"),
            (_long("Bravo", 40), 2, "#/b"),
        ],
        heading_path=["S"],
        section_key=("S",),
    )
    out = _recursive(chunk)
    assert len(out) >= 2
    for c in out:
        ids = {p.source_item_id for p in c.metadata.provenance}
        assert ids <= {"#/h", "#/a", "#/b"}                    # nothing fabricated
        assert "#/h" in ids                                    # heading prefix everywhere
        # a source block's provenance is present iff its text is in this child
        assert ("#/a" in ids) == ("alpha" in c.text.lower())
        assert ("#/b" in ids) == ("bravo" in c.text.lower())


def test_docx_oversized_section_keeps_page_ranges_null():
    chunk = _merged_section(
        [
            ("Executive Summary", None, "#/h"),
            (_long("Alpha"), None, "#/a"),
            (_long("Bravo"), None, "#/b"),
        ],
        heading_path=["Executive Summary"],
        section_key=("Executive Summary",),
    )
    out = _recursive(chunk)
    assert len(out) >= 2
    for c in out:
        assert c.metadata.page_start is None
        assert c.metadata.page_end is None            # never fabricated


def test_unpartitionable_provenance_falls_back_to_full_list():
    # a block that produced two provenance records with the SAME source id is
    # still partitionable; a record with NO source id forces the documented
    # last-resort full-list fallback.
    chunk = _merged_section(
        [
            ("S", 1, "#/h"),
            (_long("Alpha"), 1, "#/a"),
            (_long("Bravo"), 2, "#/b"),
        ],
        heading_path=["S"],
        section_key=("S",),
    )
    chunk.metadata.provenance.append(BlockProvenance(page_number=2, source_item_id=None))
    out = _recursive(chunk)
    assert len(out) >= 2
    for c in out:
        assert len(c.metadata.provenance) == 4        # full list retained, nothing dropped/fabricated


# --- C5. determinism -------------------------------------------------


def test_recursive_stage_is_deterministic():
    chunk = _merged_section(
        [
            ("3.1 Pre-training BERT", 4, "#/h"),
            (_long("Alpha"), 4, "#/a"),
            (_long("Bravo"), 4, "#/b"),
            (_long("Charlie"), 5, "#/c"),
        ],
        heading_path=["3 BERT", "3.1 Pre-training BERT"],
        section_key=("3", "3.1"),
        section_id="3.1",
    )

    def snap(chunks):
        return [
            (
                c.text,
                tuple(p.source_item_id for p in c.metadata.provenance),
                (c.metadata.page_start, c.metadata.page_end),
                (c.metadata.block_start, c.metadata.block_end),
                c.parent_chunk,
                c.chunk_index,
            )
            for c in chunks
        ]

    assert snap(_recursive(chunk)) == snap(_recursive(chunk))


# --- C9. no heading duplication ------------------------------------


def test_recursive_never_produces_heading_heading_content_or_heading_content_heading():
    chunk = _merged_section(
        [
            ("2.1 Approaches", 3, "#/h"),
            (_long("Alpha"), 3, "#/a"),
            (_long("Bravo"), 4, "#/b"),
        ],
        heading_path=["2 Related Work", "2.1 Approaches"],
        section_key=("2", "2.1"),
        section_id="2.1",
    )
    for child in _recursive(chunk):
        # heading appears once, and only at the very start
        assert child.text.count("2.1 Approaches") == 1
        assert child.text.index("2.1 Approaches") == 0
        assert not child.text.rstrip().endswith("2.1 Approaches")


# ===========================================================================
# SemanticStage
# ===========================================================================


def _sem_chunk(
    text: str,
    *,
    section_key: tuple[str, ...],
    prov: list[BlockProvenance],
    block_start: int,
    block_end: int,
    parent_chunk: int | None = None,
    block_type: BlockType = BlockType.TEXT,
) -> DocumentChunk:
    md = ChunkMetadata(
        block_type=block_type,
        section_key=tuple(section_key),
        heading_path=list(section_key),
        provenance=list(prov),
        block_start=block_start,
        block_end=block_end,
    )
    pgs = [p.page_number for p in prov if p.page_number is not None]
    md.page_start = min(pgs) if pgs else None
    md.page_end = max(pgs) if pgs else None
    return DocumentChunk(text, 0, md, parent_chunk=parent_chunk)


# --- C6. provenance union on merge --------------------------------


def test_semantic_merge_unions_provenance_and_recomputes_ranges():
    a = _sem_chunk(
        "tiny lead-in sentence",
        section_key=("4",), prov=[BlockProvenance(page_number=6, source_item_id="#/a")],
        block_start=10, block_end=10,
    )
    b = _sem_chunk(
        "the rest of the very short section body follows here",
        section_key=("4",), prov=[BlockProvenance(page_number=7, source_item_id="#/b")],
        block_start=11, block_end=11,
    )
    out = SemanticStage().run([a, b])
    assert len(out) == 1
    merged = out[0]
    assert [p.source_item_id for p in merged.metadata.provenance] == ["#/a", "#/b"]   # both, in order
    assert (merged.metadata.page_start, merged.metadata.page_end) == (6, 7)           # union
    assert (merged.metadata.block_start, merged.metadata.block_end) == (10, 11)       # union
    assert "tiny lead-in" in merged.text and "rest of the very short section" in merged.text


def test_semantic_merge_deduplicates_shared_provenance():
    shared = BlockProvenance(page_number=6, source_item_id="#/shared")
    a = _sem_chunk("tiny one", section_key=("4",), prov=[shared], block_start=1, block_end=1)
    b = _sem_chunk(
        "tiny two", section_key=("4",),
        prov=[BlockProvenance(page_number=6, source_item_id="#/shared"),
              BlockProvenance(page_number=6, source_item_id="#/extra")],
        block_start=1, block_end=2,
    )
    out = SemanticStage().run([a, b])
    assert len(out) == 1
    ids = [p.source_item_id for p in out[0].metadata.provenance]
    assert ids == ["#/shared", "#/extra"]     # shared not duplicated


# --- C7. section safety --------------------------------------------


def test_semantic_never_merges_across_section_boundaries():
    same_a = _sem_chunk("tiny a", section_key=("1",), prov=[BlockProvenance(1, None, "#/a")], block_start=0, block_end=0)
    same_b = _sem_chunk("tiny b", section_key=("1",), prov=[BlockProvenance(1, None, "#/b")], block_start=1, block_end=1)
    descendant = _sem_chunk("tiny c", section_key=("1", "1.1"), prov=[BlockProvenance(1, None, "#/c")], block_start=2, block_end=2)
    sibling = _sem_chunk("tiny d", section_key=("2",), prov=[BlockProvenance(1, None, "#/d")], block_start=3, block_end=3)
    unrelated = _sem_chunk("tiny e", section_key=("X", "Y"), prov=[BlockProvenance(1, None, "#/e")], block_start=4, block_end=4)

    out = SemanticStage().run([same_a, same_b, descendant, sibling, unrelated])
    # same_a + same_b merge; nothing else does
    assert len(out) == 4
    assert "tiny a" in out[0].text and "tiny b" in out[0].text
    assert out[1].metadata.section_key == ("1", "1.1")      # descendant untouched
    assert out[2].metadata.section_key == ("2",)            # sibling untouched
    assert out[3].metadata.section_key == ("X", "Y")        # unrelated untouched


# --- C8. parent-chunk difference must not block a same-section merge -----


def test_semantic_merges_same_section_despite_different_parent_chunk():
    a = _sem_chunk(
        "tiny tail of split three",
        section_key=("5",), prov=[BlockProvenance(8, None, "#/a")],
        block_start=20, block_end=20, parent_chunk=3,
    )
    b = _sem_chunk(
        "tiny head of split four",
        section_key=("5",), prov=[BlockProvenance(8, None, "#/b")],
        block_start=21, block_end=21, parent_chunk=4,
    )
    out = SemanticStage().run([a, b])
    assert len(out) == 1
    assert [p.source_item_id for p in out[0].metadata.provenance] == ["#/a", "#/b"]


def test_semantic_stage_is_deterministic():
    src = [
        _sem_chunk("tiny one", section_key=("1",), prov=[BlockProvenance(1, None, "#/a")], block_start=0, block_end=0),
        _sem_chunk("tiny two", section_key=("1",), prov=[BlockProvenance(2, None, "#/b")], block_start=1, block_end=1),
        _sem_chunk("a bigger sibling section body " * 8, section_key=("2",), prov=[BlockProvenance(3, None, "#/c")], block_start=2, block_end=2),
    ]

    def snap(chunks):
        return [
            (c.text, tuple(p.source_item_id for p in c.metadata.provenance),
             (c.metadata.page_start, c.metadata.page_end))
            for c in chunks
        ]

    assert snap(SemanticStage().run([deepcopy(c) for c in src])) == snap(SemanticStage().run([deepcopy(c) for c in src]))


# ===========================================================================
# STAGE 3 AUDIT -- recursive provenance partitioning
# ===========================================================================


def _distinct(marker: str, n: int = 40) -> str:
    # marker-dense pseudo-sentences: no two markers share a 6-gram anywhere.
    return " ".join(
        f"{marker}{k} {marker}alpha {marker}beta {marker}gamma{k} {marker}delta {marker}epsilon."
        for k in range(n)
    )


def test_audit_body_provenance_exact_sets_per_child():
    """Q2/Q3: 1 heading + 4 distinct body blocks, 2 pages, forced into
    several children. Assert the exact source_item_id set and page range of
    every child -- not just lengths."""
    a, b, c, d = (_distinct(m) for m in ("aa", "bb", "cc", "dd"))
    chunk = _merged_section(
        [
            ("3.1 Pre-training BERT", 4, "#/h"),
            (a, 4, "#/a"),
            (b, 4, "#/b"),
            (c, 5, "#/c"),
            (d, 6, "#/d"),
        ],
        heading_path=["3 BERT", "3.1 Pre-training BERT"],
        section_key=("3", "3.1"),
        section_id="3.1",
    )
    out = _recursive(chunk)
    assert len(out) >= 3

    for child in out:
        ids = {p.source_item_id for p in child.metadata.provenance}
        markers = {m for m in ("aa", "bb", "cc", "dd") if f"{m}alpha" in child.text.lower()}

        # nothing fabricated
        assert ids <= {"#/h", "#/a", "#/b", "#/c", "#/d"}
        # the heading prefix is in every child -> so is the heading's provenance
        assert "#/h" in ids
        # a body block's provenance is present IFF its text is in this child
        body_ids = ids - {"#/h"}
        assert body_ids == {f"#/{m[0]}" for m in markers}
        # page range is body-only: exactly the pages of the markers present
        marker_pages = {"aa": 4, "bb": 4, "cc": 5, "dd": 6}
        expected = {marker_pages[m] for m in markers}
        assert (child.metadata.page_start, child.metadata.page_end) == (min(expected), max(expected))
        # a child of purely page-4 content is 4-4, never 4-6
        if markers == {"aa"} or markers == {"aa", "bb"}:
            assert child.metadata.page_end == 4

    # nothing silently lost: union across children == every source block
    all_ids = {p.source_item_id for child in out for p in child.metadata.provenance}
    assert all_ids == {"#/h", "#/a", "#/b", "#/c", "#/d"}
    # order preserved inside each child (document order of the parent list)
    for child in out:
        ids_in_order = [p.source_item_id for p in child.metadata.provenance]
        canonical = ["#/h", "#/a", "#/b", "#/c", "#/d"]
        assert ids_in_order == sorted(ids_in_order, key=canonical.index)


def test_audit_A_block_spanning_many_windows_uses_safety_net_not_heading_only():
    """A single body block longer than several windows: a middle child holds
    only its deep interior. It must NOT end up heading-only, and must not
    fabricate."""
    huge = _distinct("zz", 220)   # one very long block -> spans 4-5 windows
    chunk = _merged_section(
        [
            ("S", 3, "#/h"),
            (huge, 3, "#/z"),
        ],
        heading_path=["S"],
        section_key=("S",),
    )
    out = _recursive(chunk)
    assert len(out) >= 3
    for child in out:
        ids = {p.source_item_id for p in child.metadata.provenance}
        assert ids <= {"#/h", "#/z"}                 # nothing fabricated
        assert "#/z" in ids                          # never heading-only
        assert child.metadata.page_start == 3 and child.metadata.page_end == 3


def test_audit_B_adjacent_blocks_sharing_a_phrase_over_attribute_but_never_lose_or_fabricate():
    """Two adjacent blocks that share a verbatim 6-word run at their start.
    The heuristic may attribute one to the other (mild over-attribution to an
    adjacent block) but must never fabricate an id or lose a block."""
    shared = "identical opening phrase repeated verbatim across both blocks here"
    a = shared + " " + _distinct("aa", 45)
    b = shared + " " + _distinct("bb", 45)
    chunk = _merged_section(
        [
            ("S", 7, "#/h"),
            (a, 7, "#/a"),
            (b, 8, "#/b"),
        ],
        heading_path=["S"],
        section_key=("S",),
    )
    out = _recursive(chunk)
    assert len(out) >= 2
    for child in out:
        ids = {p.source_item_id for p in child.metadata.provenance}
        assert ids <= {"#/h", "#/a", "#/b"}          # never fabricated
    # both real blocks still reachable somewhere
    all_ids = {p.source_item_id for child in out for p in child.metadata.provenance}
    assert {"#/a", "#/b"} <= all_ids


def test_audit_D_multiple_records_same_source_id_align_precisely_not_fallback():
    """A body block with two provenance records (same source_item_id, two
    pages) is still partitioned precisely -- both records follow the block's
    text, and it does NOT trigger the full-list fallback."""
    a, b, c = (_distinct(m) for m in ("aa", "bb", "cc"))
    chunk = _merged_section(
        [
            ("3.1 Topic", 4, "#/h"),
            (a, 4, "#/a"),
            (b, 4, "#/b"),
            (c, 6, "#/c"),
        ],
        heading_path=["3 X", "3.1 Topic"],
        section_key=("3", "3.1"),
        section_id="3.1",
    )
    # give block "b" a second provenance record on page 5, same id
    b_pos = next(i for i, p in enumerate(chunk.metadata.provenance) if p.source_item_id == "#/b")
    chunk.metadata.provenance.insert(b_pos + 1, BlockProvenance(page_number=5, source_item_id="#/b"))

    out = _recursive(chunk)
    assert len(out) >= 3

    marker_pages = {"aa": {4}, "bb": {4, 5}, "cc": {6}}
    for child in out:
        markers = {m for m in marker_pages if f"{m}alpha" in child.text.lower()}
        b_records = [p for p in child.metadata.provenance if p.source_item_id == "#/b"]
        # both of b's records travel with b's text -- exactly where b's text is
        assert ({p.page_number for p in b_records} == {4, 5}) == ("bb" in markers)
        # body-only page range == union of the pages of the markers present
        if markers:
            pages = set().union(*(marker_pages[m] for m in markers))
            assert (child.metadata.page_start, child.metadata.page_end) == (min(pages), max(pages))

    # not the broad fallback: a child of purely 'aa' content has only h + a
    aa_child = next(
        c for c in out if "aaalpha" in c.text.lower() and "bbalpha" not in c.text.lower()
    )
    assert [p.source_item_id for p in aa_child.metadata.provenance] == ["#/h", "#/a"]


def test_audit_E_heading_provenance_in_every_child_body_provenance_only_where_text_is():
    a, b = (_distinct(m) for m in ("aa", "bb"))
    chunk = _merged_section(
        [
            ("2.1 Section", 3, "#/head"),
            (a, 3, "#/a"),
            (b, 4, "#/b"),
        ],
        heading_path=["2 Parent", "2.1 Section"],
        section_key=("2", "2.1"),
        section_id="2.1",
    )
    out = _recursive(chunk)
    assert len(out) >= 2
    for child in out:
        ids = [p.source_item_id for p in child.metadata.provenance]
        assert ids.count("#/head") == 1                        # heading prov once, every child
        assert ids[0] == "#/head"                              # and first (document order)
        has_a, has_b = "#/a" in ids, "#/b" in ids
        assert has_a == ("aaalpha" in child.text.lower())
        assert has_b == ("bbalpha" in child.text.lower())
    # first child: page 3 body only (heading also page 3 here)
    assert out[0].metadata.page_start == 3


def test_audit_docx_no_page_provenance_stays_null_through_split():
    a, b = (_distinct(m) for m in ("aa", "bb"))
    chunk = _merged_section(
        [
            ("Executive Summary", None, "#/h"),
            (a, None, "#/a"),
            (b, None, "#/b"),
        ],
        heading_path=["Executive Summary"],
        section_key=("Executive Summary",),
    )
    out = _recursive(chunk)
    assert len(out) >= 2
    for child in out:
        assert child.metadata.page_start is None
        assert child.metadata.page_end is None


# ===========================================================================
# STAGE 4 -- Table / List / Caption atomicity + Filter / Quality
# ===========================================================================


# --- TABLE -----------------------------------------------------------


def test_table_that_fits_is_one_atomic_chunk():
    table = _md_table(["Name", "Score"], 4)
    chunk = _merged_section(
        [("4.1 Scores", 7, "#/h"), (table, 7, "#/tbl")],
        heading_path=["4 Results", "4.1 Scores"], section_key=("4", "4.1"),
        section_id="4.1", block_type=BlockType.TABLE,
    )
    out = _recursive(chunk)
    assert len(out) == 1
    assert out[0].metadata.block_type == BlockType.TABLE
    assert table in out[0].text
    assert out[0].text.count("4.1 Scores") == 1


def test_oversized_table_splits_only_at_row_boundaries():
    table = _md_table(["Name", "Score", "Notes"], 130)
    chunk = _merged_section(
        [("4.1 Scores", 7, "#/h"), (table, 7, "#/tbl")],
        heading_path=["4 Results", "4.1 Scores"], section_key=("4", "4.1"),
        section_id="4.1", block_type=BlockType.TABLE,
    )
    out = _recursive(chunk)
    assert len(out) >= 2

    header_line = "| Name | Score | Notes |"
    sep_line = "| --- | --- | --- |"
    seen_rows: list[str] = []
    for child in out:
        assert child.metadata.block_type == BlockType.TABLE
        assert count_tokens(child.text) <= DEFAULT_CHUNKING_CONFIG.embed_max
        assert child.text.count("4.1 Scores") == 1
        lines = [ln for ln in child.text.split("\n") if ln.strip()]
        assert lines[1] == header_line and lines[2] == sep_line   # header repeated once
        data = lines[3:]
        assert data, "table child with no data rows"
        for row in data:
            assert row.startswith("| ") and row.rstrip().endswith(" |")
            assert row.count("|") == 4
        seen_rows += data

    original_rows = [ln for ln in table.split("\n") if ln.startswith("| cell")]
    assert seen_rows == original_rows        # every row once, none split, none duplicated


def test_oversized_table_provenance_and_ranges():
    table = _md_table(["A", "B"], 130)
    chunk = _merged_section(
        [("T", 5, "#/h"), (table, 5, "#/tbl")],
        heading_path=["Section", "T"], section_key=("s", "t"), block_type=BlockType.TABLE,
    )
    chunk.metadata.provenance.append(BlockProvenance(page_number=6, source_item_id="#/tbl"))
    out = _recursive(chunk)
    assert len(out) >= 2
    for child in out:
        ids = [p.source_item_id for p in child.metadata.provenance]
        assert ids == ["#/h", "#/tbl", "#/tbl"]
        assert (child.metadata.page_start, child.metadata.page_end) == (5, 6)   # body-only
        assert child.parent_chunk == out[0].parent_chunk


def test_oversized_table_is_deterministic():
    table = _md_table(["A", "B", "C"], 140)
    chunk = _merged_section(
        [("T", 1, "#/h"), (table, 1, "#/tbl")],
        heading_path=["T"], section_key=("t",), block_type=BlockType.TABLE,
    )
    a = [c.text for c in _recursive(chunk)]
    b = [c.text for c in _recursive(chunk)]
    assert a == b and len(a) >= 2


# --- LIST ------------------------------------------------------------


def _list_blocks(marker: str, n: int, page: int | None = 9):
    return [
        (f"- {marker} item {i}: uniqueword{marker}{i} describing a distinct point in detail here.",
         page, f"#/{marker}{i}")
        for i in range(n)
    ]


def test_list_that_fits_is_one_chunk():
    chunk = _merged_section(
        [("Options", 9, "#/h"), *_list_blocks("opt", 4)],
        heading_path=["Options"], section_key=("options",), block_type=BlockType.LIST,
    )
    out = _recursive(chunk)
    assert len(out) == 1
    assert out[0].metadata.block_type == BlockType.LIST


def test_oversized_list_splits_between_whole_items():
    blocks = _list_blocks("lim", 90)
    chunk = _merged_section(
        [("5 Limitations", 9, "#/h"), *blocks],
        heading_path=["5 Limitations"], section_key=("5",), section_id="5",
        block_type=BlockType.LIST,
    )
    out = _recursive(chunk)
    assert len(out) >= 2

    all_items = [b[0] for b in blocks]
    seen: list[str] = []
    for child in out:
        assert child.metadata.block_type == BlockType.LIST
        assert count_tokens(child.text) <= DEFAULT_CHUNKING_CONFIG.embed_max
        assert child.text.count("5 Limitations") == 1
        body = child.text.split("\n\n", 1)[1]
        for item in body.split("\n\n"):
            assert item in all_items, "a list item was split or altered"
        seen += body.split("\n\n")
    assert seen == all_items


def test_oversized_list_provenance_is_exact_per_item():
    blocks = _list_blocks("x", 90)
    chunk = _merged_section(
        [("L", 9, "#/h"), *blocks],
        heading_path=["L"], section_key=("l",), block_type=BlockType.LIST,
    )
    out = _recursive(chunk)
    for child in out:
        ids = [p.source_item_id for p in child.metadata.provenance]
        assert ids[0] == "#/h"
        item_ids = set(ids[1:])
        text_ids = {b[2] for b in blocks if b[0] in child.text}
        assert item_ids == text_ids
        assert child.metadata.page_start == 9 and child.metadata.page_end == 9


def test_oversized_list_is_deterministic():
    chunk = _merged_section(
        [("L", 2, "#/h"), *_list_blocks("d", 80)],
        heading_path=["L"], section_key=("l",), block_type=BlockType.LIST,
    )
    a = [(c.text, tuple(p.source_item_id for p in c.metadata.provenance)) for c in _recursive(chunk)]
    b = [(c.text, tuple(p.source_item_id for p in c.metadata.provenance)) for c in _recursive(chunk)]
    assert a == b and len(a) >= 2


# --- CAPTION --------------------------------------------------------


def test_caption_folded_chunk_keeps_caption_type_and_prefix():
    chunk = _merged_section(
        [("Figure 2", 4, "#/h"), ("Figure 2 shows the architecture of the multi-agent system.", 4, "#/cap")],
        heading_path=["Figure 2"], section_key=("figure 2",), block_type=BlockType.CAPTION,
    )
    out = _recursive(chunk)
    assert len(out) == 1
    assert out[0].metadata.block_type == BlockType.CAPTION
    assert out[0].text.startswith("Figure 2\n\n")


def test_semantic_caption_owns_following_text_still_works():
    caption = _sem_chunk(
        "Figure 1 overview.", section_key=("s",),
        prov=[BlockProvenance(3, None, "#/cap")], block_start=5, block_end=5,
        block_type=BlockType.CAPTION,
    )
    body = _sem_chunk(
        "The figure shows the pipeline stages and their ordering across the whole system.",
        section_key=("s",), prov=[BlockProvenance(3, None, "#/txt")], block_start=6, block_end=6,
    )
    out = SemanticStage().run([caption, body])
    assert len(out) == 1
    assert out[0].metadata.block_type == BlockType.CAPTION
    assert [p.source_item_id for p in out[0].metadata.provenance] == ["#/cap", "#/txt"]


# --- FILTERSTAGE ---------------------------------------------------


def _fchunk(text: str, *, block_type=BlockType.TEXT, parent_chunk=None):
    return DocumentChunk(text, 0, ChunkMetadata(block_type=block_type), parent_chunk=parent_chunk)


def test_filter_retains_content_bearing_structural_and_continuation_chunks():
    kept = [
        _fchunk("| A | B |\n| --- | --- |\n| 1 | 2 |", block_type=BlockType.TABLE),
        _fchunk("- yes\n- no", block_type=BlockType.LIST),
        _fchunk("Figure 3 shows the workflow.", block_type=BlockType.CAPTION),
        _fchunk("3.1 Topic\n\nshort continuation body", parent_chunk=4),
        _fchunk("Scope\n\nThis section is short but real."),
    ]
    out = FilterStage().run([deepcopy(c) for c in kept])
    assert len(out) == len(kept)


def test_filter_still_removes_content_free_noise():
    noise = [
        _fchunk(""),
        _fchunk("   "),
        _fchunk("42"),
        _fchunk("doi: 10.1/xyz"),
        _fchunk("(C) 2024 Someone"),
        _fchunk("...."),
    ]
    out = FilterStage().run([deepcopy(c) for c in noise])
    # empty / blank / page-number / doi / punctuation are dropped
    assert all(c.text.strip() not in ("", "42", "doi: 10.1/xyz", "....") for c in out)
    assert len(out) < len(noise)


def test_filter_still_deduplicates_exact_duplicates():
    dup = [_fchunk("Header repeated on every page") for _ in range(3)]
    out = FilterStage().run([deepcopy(c) for c in dup])
    assert len(out) == 1


# --- QUALITYSTAGE (effective block_type) -------------------------


@pytest.mark.parametrize(
    "block_type, expect_is_table, expect_is_caption, expect_score",
    [
        (BlockType.TEXT, False, False, QualityStage.DEFAULT_SCORE),
        (BlockType.TABLE, True, False, QualityStage.TABLE_SCORE),
        (BlockType.LIST, False, False, QualityStage.DEFAULT_SCORE),
        (BlockType.CAPTION, False, True, QualityStage.CAPTION_SCORE),
    ],
)
def test_quality_scores_folded_chunk_by_effective_block_type(
    block_type, expect_is_table, expect_is_caption, expect_score
):
    chunk = DocumentChunk(
        "3.1 Section\n\nthe section body content goes here and is reasonably sized",
        0,
        ChunkMetadata(block_type=block_type, section_title="3.1 Section", section_key=("3", "3.1")),
    )
    QualityStage().run([chunk])
    assert chunk.metadata.is_table is expect_is_table
    assert chunk.metadata.is_caption is expect_is_caption
    assert chunk.metadata.quality_score == expect_score
    assert chunk.metadata.quality_score != QualityStage.HEADING_SCORE


def test_quality_genuine_reference_and_appendix_scoring_unchanged():
    ref = DocumentChunk("body", 0, ChunkMetadata(block_type=BlockType.TEXT, section_title="References"))
    apx = DocumentChunk("body", 0, ChunkMetadata(block_type=BlockType.TEXT, section_title="Appendix A"))
    QualityStage().run([ref, apx])
    assert ref.metadata.is_reference and ref.metadata.quality_score == QualityStage.REFERENCE_SCORE
    assert apx.metadata.is_appendix and apx.metadata.quality_score == QualityStage.APPENDIX_SCORE


# --- full pipeline end-to-end ---------------------------------


def _pipeline_from_blocks(blocks, checksum="stage4"):
    from app.chunking.pipeline import ChunkPipeline
    from app.document.models import DocumentBlock
    from app.ingestion.models import DocumentMetadata, ExtractionResult

    doc_blocks = []
    for i, (text, bt, level, page, item) in enumerate(blocks):
        doc_blocks.append(DocumentBlock(
            text=text, block_type=bt, level=level, page_number=page, block_index=i,
            metadata={"source_type": ".pdf", "parser": "docling"},
            provenance=[BlockProvenance(page_number=page, source_item_id=item)],
        ))
    res = ExtractionResult(
        metadata=DocumentMetadata(
            title="x", file_name="d.pdf", file_extension=".pdf",
            file_size=1, page_count=20, checksum=checksum,
        ),
        blocks=doc_blocks, tables=[],
    )
    return ChunkPipeline().run(res)


def test_end_to_end_heading_plus_table_scores_and_types_as_table():
    table = _md_table(["Metric", "Value"], 3)
    chunks = _pipeline_from_blocks([
        ("2 Results", BlockType.HEADING, 1, 3, "#/h"),
        (table, BlockType.TABLE, 0, 3, "#/tbl"),
    ])
    assert len(chunks) == 1
    c = chunks[0]
    assert c.metadata.block_type == BlockType.TABLE
    assert c.metadata.is_table is True
    assert c.metadata.quality_score == QualityStage.TABLE_SCORE
    assert c.text.startswith("2 Results\n\n") and table in c.text


def test_end_to_end_oversized_table_row_atomic_and_scored_as_table():
    table = _md_table(["Metric", "Value", "Delta"], 140)
    blocks = [
        ("2 Results", BlockType.HEADING, 1, 3, "#/h"),
        (table, BlockType.TABLE, 0, 3, "#/tbl"),
    ]
    chunks = _pipeline_from_blocks(blocks)
    assert len(chunks) >= 2
    original_rows = [ln for ln in table.split("\n") if ln.startswith("| cell")]
    seen: list[str] = []
    for c in chunks:
        assert c.metadata.block_type == BlockType.TABLE
        assert c.metadata.is_table is True
        assert count_tokens(c.text) <= DEFAULT_CHUNKING_CONFIG.embed_max
        assert c.text.count("2 Results") == 1
        lines = [ln for ln in c.text.split("\n") if ln.strip()]
        assert lines[1] == "| Metric | Value | Delta |"
        seen += [ln for ln in lines if ln.startswith("| cell")]
    assert seen == original_rows
    assert [c.text for c in chunks] == [c.text for c in _pipeline_from_blocks(blocks)]


def test_end_to_end_oversized_list_item_atomic_and_scored_as_list():
    items = [
        (f"- Item {i}: distinct{i} covers a specific facet of the discussion in some detail here.",
         BlockType.LIST, 0, 5, f"#/i{i}")
        for i in range(90)
    ]
    chunks = _pipeline_from_blocks([("6 Future Work", BlockType.HEADING, 1, 5, "#/h"), *items])
    assert len(chunks) >= 2
    all_items = [t for t, *_ in items]
    seen: list[str] = []
    for c in chunks:
        assert c.metadata.block_type == BlockType.LIST
        assert count_tokens(c.text) <= DEFAULT_CHUNKING_CONFIG.embed_max
        assert c.text.count("6 Future Work") == 1
        body = c.text.split("\n\n", 1)[1]
        for item in body.split("\n\n"):
            assert item in all_items
        seen += body.split("\n\n")
    assert seen == all_items


def test_end_to_end_heading_plus_caption_scores_and_types_as_caption():
    chunks = _pipeline_from_blocks([
        ("Figure 4", BlockType.HEADING, 1, 8, "#/h"),
        ("Figure 4 illustrates the end-to-end request flow through the system.", BlockType.CAPTION, 0, 8, "#/cap"),
    ])
    assert len(chunks) == 1
    c = chunks[0]
    assert c.metadata.block_type == BlockType.CAPTION
    assert c.metadata.is_caption is True
    assert c.metadata.quality_score == QualityStage.CAPTION_SCORE


def test_end_to_end_short_structural_chunks_survive_filter_no_heading_only():
    chunks = _pipeline_from_blocks([
        ("1 Overview", BlockType.HEADING, 1, 1, "#/h1"),
        ("A short but genuine overview paragraph of the system.", BlockType.TEXT, 0, 1, "#/t1"),
        ("Config", BlockType.HEADING, 1, 2, "#/h2"),
        ("- enabled is set to true", BlockType.LIST, 0, 2, "#/l1"),
        ("- retries is set to three", BlockType.LIST, 0, 2, "#/l2"),
        ("Table 1", BlockType.HEADING, 1, 3, "#/h3"),
        (_md_table(["k", "v"], 2), BlockType.TABLE, 0, 3, "#/tbl"),
    ])
    assert all("\n\n" in c.text for c in chunks)   # no heading-only / content-free vector
    by_title = {c.metadata.section_title: c.metadata.block_type for c in chunks}
    assert by_title["Config"] == BlockType.LIST
    assert by_title["Table 1"] == BlockType.TABLE
    assert by_title["1 Overview"] == BlockType.TEXT


# --- REVIEW-GATE FIX 1: METADATA_PATTERN vs folded heading prefix -------


@pytest.mark.parametrize(
    "title",
    ["Authorization", "Authentication", "Author Contributions", "DOI Routing", "Publisher API"],
)
def test_quality_normal_section_titled_like_metadata_keeps_default_score(title):
    # MergeStage folds the heading in as the first line; the body is ordinary
    # content. Must NOT be scored as front-matter just because the title
    # starts with "author" / "doi" / "publisher".
    chunk = DocumentChunk(
        f"{title}\n\nThis section explains how the subsystem behaves in normal operation "
        f"and what callers should expect from it in practice.",
        0,
        ChunkMetadata(block_type=BlockType.TEXT, section_title=title, section_key=("3", "3.1")),
    )
    QualityStage().run([chunk])
    assert chunk.metadata.is_metadata is False
    assert chunk.metadata.quality_score == QualityStage.DEFAULT_SCORE


def test_quality_genuine_metadata_block_still_detected():
    # A standalone front-matter block (no folded heading line) is unchanged.
    chunk = DocumentChunk(
        "Authors: Jane Doe, John Smith. Affiliation: Institute of Technology.",
        0,
        ChunkMetadata(block_type=BlockType.TEXT),
    )
    QualityStage().run([chunk])
    assert chunk.metadata.is_metadata is True
    assert chunk.metadata.quality_score == QualityStage.METADATA_SCORE


def test_quality_genuine_metadata_under_matching_heading_still_detected():
    # Heading "Authors" + body that itself starts with author front-matter:
    # stripping the folded heading still leaves a metadata body.
    chunk = DocumentChunk(
        "Authors\n\nAuthors: Jane Doe and John Smith, Institute of Technology.",
        0,
        ChunkMetadata(block_type=BlockType.TEXT, section_title="Authors"),
    )
    QualityStage().run([chunk])
    assert chunk.metadata.is_metadata is True


# --- REVIEW-GATE FIX 2: pass-through prefix must not overflow embed_max --


def test_recursive_pass_through_prefix_never_exceeds_embed_max():
    long_heading = "3.2 Authorization And Token Exchange Protocol Implementation Details And Notes"
    body = (
        "The quick brown fox jumps over the lazy dog again and again. " * 52
    ).strip() + " One extra trailing sentence to push the body close to the limit now."
    chunk = DocumentChunk(
        body,
        0,
        ChunkMetadata(
            block_type=BlockType.TEXT,
            heading_path=["3 Security", long_heading],
            section_title=long_heading,
            section_key=("3", "3.2"),
            provenance=[BlockProvenance(page_number=5, source_item_id="#/t")],
            block_start=10,
            block_end=10,
            page_start=5,
            page_end=5,
        ),
    )
    assert count_tokens(chunk.text) <= DEFAULT_CHUNKING_CONFIG.embed_max          # fits before prefix
    out = _recursive(chunk)
    assert len(out) >= 2                                                          # routed through the splitter
    for child in out:
        assert child.text.startswith(long_heading + "\n\n")
        assert child.text.count(long_heading) == 1
        assert count_tokens(child.text) <= DEFAULT_CHUNKING_CONFIG.embed_max


def test_recursive_pass_through_short_chunk_still_single():
    # A genuinely small chunk + prefix that comfortably fits stays one chunk.
    chunk = DocumentChunk(
        "A compact paragraph that easily fits within the embedding budget.",
        0,
        ChunkMetadata(
            block_type=BlockType.TEXT,
            heading_path=["1 Intro", "1.1 Scope"],
            section_title="1.1 Scope",
            section_key=("1", "1.1"),
            provenance=[BlockProvenance(page_number=1, source_item_id="#/t")],
            block_start=2,
            block_end=2,
        ),
    )
    out = _recursive(chunk)
    assert len(out) == 1
    assert out[0].parent_chunk is None
    assert out[0].text.startswith("1.1 Scope\n\n")
    assert count_tokens(out[0].text) <= DEFAULT_CHUNKING_CONFIG.embed_max


# ==================================================================
# STAGE 6 -- structural element atomicity via ContentSegments
# ==================================================================
#
# MergeStage records one ContentSegment per source block (type + text +
# provenance + source_block_index). When a section is oversized, RecursiveStage
# routes each segment by its real Docling block_type: TABLE -> row-atomic,
# LIST -> item-atomic, prose -> sentence windows -- even when a prose lead-in
# precedes the structural element. Stage 5 measured 46/367 real table rows
# split mid-cell; Stage 6 target is 0.


def _row_lines(text):
    return [ln for ln in text.split("\n") if ln.count("|") >= 2]


def test_stage6_merge_records_content_segments():
    blocks = [
        ("2 Data", BlockType.HEADING, 1, 1, "#/h"),
        ("A short prose lead-in sentence.", BlockType.TEXT, 0, 1, "#/lead"),
        (_md_table(["a", "b", "c"], 3), BlockType.TABLE, 0, 1, "#/tbl"),
    ]
    from app.chunking.stages.paragraph import ParagraphStage
    from app.chunking.stages.metadata import MetadataStage
    from app.ingestion.models import DocumentMetadata, ExtractionResult
    from app.document.models import DocumentBlock
    docblocks = [
        DocumentBlock(text=t, block_type=bt, level=lvl, page_number=pg, block_index=i,
                      metadata={"source_type": ".pdf", "parser": "docling"},
                      provenance=[BlockProvenance(page_number=pg, source_item_id=it)])
        for i, (t, bt, lvl, pg, it) in enumerate(blocks)
    ]
    res = ExtractionResult(
        metadata=DocumentMetadata(title="x", file_name="d.pdf", file_extension=".pdf",
                                  file_size=1, page_count=1, checksum="seg"),
        blocks=docblocks, tables=[])
    chunks = MergeStage().run(MetadataStage().run(ParagraphStage().run(res)))
    assert len(chunks) == 1
    segs = chunks[0].metadata.content_segments
    assert [s.block_type for s in segs] == [BlockType.HEADING, BlockType.TEXT, BlockType.TABLE]
    assert segs[0].is_heading and not segs[1].is_heading
    assert segs[2].provenance[0].source_item_id == "#/tbl"
    assert segs[2].source_block_index == 2


def test_stage6_prose_lead_in_plus_oversized_table_rows_atomic():
    blocks = [
        ("6 Results", BlockType.HEADING, 1, 8, "#/h"),
        ("To evaluate the importance of different components of the model we varied "
         "the base configuration in several ways and measured the change in "
         "performance on the development set.", BlockType.TEXT, 0, 8, "#/lead"),
        (_md_table(["variant", "bleu", "params", "steps", "notes"], 70),
         BlockType.TABLE, 0, 9, "#/tbl"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="s6-tbl-lead")

    table_children = [c for c in chunks if c.metadata.block_type == BlockType.TABLE]
    assert table_children, "the table must survive as TABLE-typed children"
    assert all(c.metadata.is_table for c in table_children)

    # every markdown row is a whole 5-column row, appears exactly once
    seen = []
    for c in table_children:
        for ln in _row_lines(c.text):
            if "---" in ln:
                continue
            assert ln.count("|") >= 5
            if "cell" in ln:
                seen.append(ln.strip())
    assert len(seen) == len(set(seen)) == 70

    for c in chunks:
        assert count_tokens(c.text) <= DEFAULT_CHUNKING_CONFIG.embed_max
        assert "\n\n" in c.text  # never a heading-only vector


def test_stage6_table_caption_stays_with_first_fragment():
    caption = "Table 3: variations on the architecture; unlisted values match the base model."
    table_seg = caption + "\n\n" + _md_table(["variant", "bleu", "params", "extra", "more"], 80)
    blocks = [
        ("6 Results", BlockType.HEADING, 1, 8, "#/h"),
        ("A prose lead-in that precedes the table and sets it up for the reader.",
         BlockType.TEXT, 0, 8, "#/lead"),
        (table_seg, BlockType.TABLE, 0, 9, "#/tbl"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="s6-caption")
    table_children = [c for c in chunks if c.metadata.block_type == BlockType.TABLE]
    assert sum(caption in c.text for c in table_children) == 1
    # the caption is on the FIRST table fragment
    assert caption in table_children[0].text
    for c in chunks:
        assert count_tokens(c.text) <= DEFAULT_CHUNKING_CONFIG.embed_max


def test_stage6_table_header_repeats_on_every_fragment():
    blocks = [
        ("T", BlockType.HEADING, 1, 1, "#/h"),
        ("prose lead in here for the table below", BlockType.TEXT, 0, 1, "#/l"),
        (_md_table(["colone", "coltwo", "colthree", "colfour", "colfive"], 90),
         BlockType.TABLE, 0, 2, "#/tbl"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="s6-hdr")
    frags = [c for c in chunks if c.metadata.block_type == BlockType.TABLE]
    assert len(frags) >= 2
    for c in frags:
        assert "| colone | coltwo | coltarget" not in c.text  # sanity
        assert c.text.count("colone") >= 1  # header present in each fragment


def test_stage6_oversized_table_deterministic():
    blocks = [
        ("T", BlockType.HEADING, 1, 1, "#/h"),
        ("lead prose", BlockType.TEXT, 0, 1, "#/l"),
        (_md_table(["a", "b", "c", "d", "e"], 120), BlockType.TABLE, 0, 2, "#/tbl"),
    ]
    a = _pipeline_from_blocks(blocks, checksum="s6-det")
    b = _pipeline_from_blocks(blocks, checksum="s6-det")
    assert [c.text for c in a] == [c.text for c in b]
    assert [str(c.metadata.chunk_uuid) for c in a] == [str(c.metadata.chunk_uuid) for c in b]


def test_stage6_prose_lead_in_plus_oversized_list_items_atomic():
    items = [(f"- list item number {i} explains configuration option {i} in enough "
              f"detail to be a real sentence with substance", BlockType.LIST, 0, 3, f"#/l{i}")
             for i in range(90)]
    blocks = [
        ("3 Config", BlockType.HEADING, 1, 3, "#/h"),
        ("The following options control the behaviour of the subsystem in production.",
         BlockType.TEXT, 0, 3, "#/lead"),
    ] + items
    chunks = _pipeline_from_blocks(blocks, checksum="s6-list-lead")

    list_children = [c for c in chunks if c.metadata.block_type == BlockType.LIST]
    assert list_children
    seen = []
    for c in list_children:
        for ln in c.text.split("\n"):
            if ln.startswith("- list item number"):
                seen.append(ln.strip())
    assert len(seen) == len(set(seen)) == 90
    for c in chunks:
        assert count_tokens(c.text) <= DEFAULT_CHUNKING_CONFIG.embed_max


def test_stage6_oversized_single_table_row_kept_intact_over_budget():
    big_cell = "word " * 900
    row = f"| {big_cell}| b |"
    grid = f"| h1 | h2 |\n| --- | --- |\n{row}\n| c | d |"
    blocks = [
        ("T", BlockType.HEADING, 1, 1, "#/h"),
        ("lead prose sentence here", BlockType.TEXT, 0, 1, "#/l"),
        (grid, BlockType.TABLE, 0, 2, "#/tbl"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="s6-bigrow")
    frags = [c for c in chunks if c.metadata.block_type == BlockType.TABLE]
    # the huge row survives intact in exactly one fragment
    assert sum(big_cell.strip() in c.text for c in frags) == 1
    over = [c for c in frags if count_tokens(c.text) > DEFAULT_CHUNKING_CONFIG.embed_max]
    assert len(over) == 1  # the indivisible row, accepted exception


def test_stage6_oversized_single_list_item_kept_intact_over_budget():
    big = "- " + ("sentence here. " * 400)
    blocks = [
        ("L", BlockType.HEADING, 1, 1, "#/h"),
        ("lead", BlockType.TEXT, 0, 1, "#/le"),
        (big, BlockType.LIST, 0, 2, "#/l0"),
        ("- small item", BlockType.LIST, 0, 2, "#/l1"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="s6-bigitem")
    lists = [c for c in chunks if c.metadata.block_type == BlockType.LIST]
    assert sum(big.strip() in c.text for c in lists) == 1
    over = [c for c in lists if count_tokens(c.text) > DEFAULT_CHUNKING_CONFIG.embed_max]
    assert len(over) == 1


def test_stage6_mixed_prose_table_child_is_table_typed():
    # small prose lead-in + small table -> one child, TABLE-dominant
    blocks = [
        ("2 D", BlockType.HEADING, 1, 1, "#/h"),
        ("Short lead-in.", BlockType.TEXT, 0, 1, "#/lead"),
        (_md_table(["a", "b"], 4), BlockType.TABLE, 0, 1, "#/tbl"),
        # padding prose to force the section oversized so it goes through _split_chunk
        ("padding sentence. " * 260, BlockType.TEXT, 0, 1, "#/pad"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="s6-mixed")
    table_children = [c for c in chunks if any(
        r.source_item_id == "#/tbl" for r in c.metadata.provenance)]
    assert table_children
    for c in table_children:
        assert c.metadata.block_type == BlockType.TABLE
        assert c.metadata.is_table is True


def test_stage6_exact_provenance_for_table_and_prose_segments():
    blocks = [
        ("6 R", BlockType.HEADING, 1, 8, "#/h"),
        ("Prose lead-in sentence number one with enough words to matter here.",
         BlockType.TEXT, 0, 8, "#/lead"),
        (_md_table(["a", "b", "c", "d", "e"], 90), BlockType.TABLE, 0, 9, "#/tbl"),
        ("Prose after the table wrapping up the discussion of the results shown.",
         BlockType.TEXT, 0, 10, "#/after"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="s6-prov")
    for c in chunks:
        ids = {r.source_item_id for r in c.metadata.provenance}
        assert ids <= {"#/h", "#/lead", "#/tbl", "#/after"}   # never fabricated
        if c.metadata.block_type == BlockType.TABLE:
            assert "#/tbl" in ids                              # table always present
            # a table fragment carries the table's own provenance; an adjacent
            # prose block may be co-packed, but the two prose blocks are in
            # different runs and cannot both land in one table child
            assert not {"#/lead", "#/after"} <= ids
    # every surviving source id appears somewhere, none dropped
    all_ids = {r.source_item_id for c in chunks for r in c.metadata.provenance}
    assert {"#/lead", "#/tbl", "#/after"} <= all_ids


def test_stage6_multipage_table_page_range_body_only():
    grid = "| h1 | h2 |\n| --- | --- |\n" + "\n".join(
        f"| r{i}a longer cell content here | r{i}b |" for i in range(80))
    from app.document.models import DocumentBlock
    from app.ingestion.models import DocumentMetadata, ExtractionResult
    from app.chunking.pipeline import ChunkPipeline
    docblocks = [
        DocumentBlock(text="9 Tables", block_type=BlockType.HEADING, level=1, page_number=4,
                      block_index=0, metadata={"source_type": ".pdf", "parser": "docling"},
                      provenance=[BlockProvenance(page_number=4, source_item_id="#/h")]),
        DocumentBlock(text="Prose lead-in on page four introducing the table.",
                      block_type=BlockType.TEXT, level=0, page_number=4, block_index=1,
                      metadata={"source_type": ".pdf", "parser": "docling"},
                      provenance=[BlockProvenance(page_number=4, source_item_id="#/lead")]),
        DocumentBlock(text=grid, block_type=BlockType.TABLE, level=0, page_number=5,
                      block_index=2, metadata={"source_type": ".pdf", "parser": "docling"},
                      provenance=[BlockProvenance(page_number=5, source_item_id="#/tbl"),
                                  BlockProvenance(page_number=6, source_item_id="#/tbl")]),
    ]
    res = ExtractionResult(
        metadata=DocumentMetadata(title="x", file_name="d.pdf", file_extension=".pdf",
                                  file_size=1, page_count=6, checksum="s6-mp"),
        blocks=docblocks, tables=[])
    chunks = ChunkPipeline().run(res)
    for c in chunks:
        if c.metadata.block_type == BlockType.TABLE:
            # table body is on pages 5-6; the heading/lead page 4 must NOT widen it
            assert c.metadata.page_start == 5 and c.metadata.page_end == 6
            assert c.metadata.block_start == 2 and c.metadata.block_end == 2


def test_stage6_heading_prefix_once_per_structural_child():
    blocks = [
        ("4 Results", BlockType.HEADING, 1, 1, "#/h"),
        ("prose lead in", BlockType.TEXT, 0, 1, "#/l"),
        (_md_table(["a", "b", "c", "d"], 100), BlockType.TABLE, 0, 2, "#/tbl"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="s6-prefix")
    for c in chunks:
        assert c.text.startswith("4 Results\n\n")
        assert c.text.count("4 Results") == 1


def test_stage6_standalone_table_and_list_unchanged():
    # standalone table (no prose lead-in) still TABLE, row atomic
    t = _pipeline_from_blocks([
        ("Table 3", BlockType.HEADING, 1, 9, "#/h"),
        (_md_table(["a", "b", "c", "d", "e"], 60), BlockType.TABLE, 0, 9, "#/tbl"),
    ], checksum="s6-std-t")
    assert {c.metadata.block_type for c in t} == {BlockType.TABLE}
    assert all(c.metadata.is_table for c in t)
    for c in t:
        assert count_tokens(c.text) <= DEFAULT_CHUNKING_CONFIG.embed_max

    # standalone list still LIST, item atomic
    li = _pipeline_from_blocks([
        ("Config", BlockType.HEADING, 1, 2, "#/h"),
    ] + [(f"- option {i} does something useful and specific here", BlockType.LIST, 0, 2, f"#/l{i}")
         for i in range(80)], checksum="s6-std-l")
    assert {c.metadata.block_type for c in li} == {BlockType.LIST}


def test_stage6_fallback_path_when_no_content_segments():
    # a chunk constructed directly (no MergeStage) has content_segments == ()
    chunk = _merged_section(
        [
            ("2.1 Approach", 3, "#/hh"),
            (_long("Alpha"), 3, "#/a"),
            (_long("Bravo"), 4, "#/b"),
        ],
        heading_path=["2 Work", "2.1 Approach"],
        section_key=("2", "2.1"),
        section_id="2.1",
    )
    assert chunk.metadata.content_segments == ()
    out = RecursiveStage().run([deepcopy(chunk)])
    assert len(out) >= 2
    for c in out:
        assert c.text.startswith("2.1 Approach\n\n")
        assert count_tokens(c.text) <= DEFAULT_CHUNKING_CONFIG.embed_max
        assert c.metadata.block_type == BlockType.TEXT


# --- SemanticStage structural-atomicity guard ---------------------


def _sc(text, section_key, block_type):
    return DocumentChunk(text, 0, ChunkMetadata(
        block_type=block_type, section_key=section_key,
        section_title=section_key[-1] if section_key else None,
        heading_path=list(section_key),
        provenance=[BlockProvenance(page_number=1, source_item_id="#/x")]))


def test_stage6_semantic_table_does_not_merge_with_prose():
    tbl = _sc("T\n\n| a | b |\n| 1 | 2 |", ("1",), BlockType.TABLE)
    prose = _sc("some short trailing prose", ("1",), BlockType.TEXT)
    out = SemanticStage().run([deepcopy(tbl), deepcopy(prose)])
    assert len(out) == 2
    assert out[0].metadata.block_type == BlockType.TABLE


def test_stage6_semantic_list_does_not_merge_with_prose():
    lst = _sc("L\n\n- one\n- two", ("1",), BlockType.LIST)
    prose = _sc("trailing prose", ("1",), BlockType.TEXT)
    out = SemanticStage().run([deepcopy(lst), deepcopy(prose)])
    assert len(out) == 2


def test_stage6_semantic_table_does_not_merge_with_list():
    tbl = _sc("T\n\n| a | b |", ("1",), BlockType.TABLE)
    lst = _sc("L\n\n- one", ("1",), BlockType.LIST)
    out = SemanticStage().run([deepcopy(tbl), deepcopy(lst)])
    assert len(out) == 2


def test_stage6_semantic_still_merges_tiny_prose_into_prose():
    a = _sc("tiny", ("1",), BlockType.TEXT)
    b = _sc("the following paragraph is the rest of the same section body", ("1",), BlockType.TEXT)
    out = SemanticStage().run([deepcopy(a), deepcopy(b)])
    assert len(out) == 1


# --- payload safety: content_segments is internal-only -----------


def test_stage6_content_segments_excluded_from_qdrant_payload():
    from dataclasses import fields
    from app.chunking.models import ContentSegment
    from app.document.models import BlockProvenance as BP
    from app.embeddings.models import EmbeddedChunk, EmbeddingMetadata, EmbeddingVector
    from app.search.hybrid.mapper import HybridMapper
    from app.search.dense.mapper import DenseMapper

    md = ChunkMetadata(
        block_type=BlockType.TABLE,
        section_title="2 Results",
        heading_path=["2 Results"],
        content_segments=(
            ContentSegment(BlockType.TEXT, "lead", (BP(page_number=1, source_item_id="#/l"),)),
            ContentSegment(BlockType.TABLE, "| a | b |", (BP(page_number=1, source_item_id="#/t"),)),
        ),
        provenance=[BP(page_number=1, source_item_id="#/t")],
    )
    chunk = DocumentChunk("2 Results\n\n| a | b |", 0, md)
    # score it exactly as the pipeline would, so payload values are realistic
    QualityStage().run([chunk])
    assert md.is_table is True and md.quality_score == QualityStage.TABLE_SCORE
    emb = EmbeddedChunk(
        chunk=chunk,
        vector=EmbeddingVector(values=[0.0, 0.0]),
        metadata=EmbeddingMetadata(model="x", dimensions=2),
    )

    for payload in (HybridMapper.build_payload(emb), DenseMapper.to_point(emb).payload):
        keys = set(payload)
        assert "content_segments" not in keys
        assert not any("segment" in k for k in keys)
        # provenance is still the compact BlockProvenance dict, unchanged shape
        assert set(payload["provenance"][0]) == {
            "page_number", "bbox", "source_item_id", "charspan", "sheet_name", "table_index"
        }
        # the whitelisted quality / effective-type fields still reach Qdrant,
        # carrying the values QualityStage produced
        assert payload["block_type"] == "table"
        assert payload["quality_score"] == QualityStage.TABLE_SCORE
        assert payload["retrieval_priority"] == QualityStage.TABLE_PRIORITY
        assert payload["is_table"] is True
        assert payload["is_caption"] is False
        for field_name in ("is_reference", "is_appendix", "is_metadata", "is_formula"):
            assert field_name in payload

    # BlockProvenance itself was not given new fields
    assert {f.name for f in fields(BP)} == {
        "page_number", "bbox", "source_item_id", "charspan", "sheet_name", "table_index"
    }


def test_standalone_table_without_prose_lead_in_stays_row_atomic():
    # contrast case: no prose lead-in -> effective TABLE -> row atomic
    blocks = [
        ("Table 3", BlockType.HEADING, 1, 9, "#/h"),
        (_md_table(["variant", "bleu", "params", "steps", "notes"], 60),
         BlockType.TABLE, 0, 9, "#/tbl"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="limitation-table-2")
    assert {c.metadata.block_type for c in chunks} == {BlockType.TABLE}
    assert all(c.metadata.is_table for c in chunks)
    for c in chunks:
        assert count_tokens(c.text) <= DEFAULT_CHUNKING_CONFIG.embed_max
        body_lines = [ln for ln in c.text.split("\n") if "|" in ln]
        assert all(ln.count("|") >= 5 for ln in body_lines)  # whole 5-col rows


# ==================================================================
# STAGE 7 -- effective-type quality validation (VALIDATION ONLY)
# ==================================================================
#
# QualityStage scores the EFFECTIVE block_type set by MergeStage / RecursiveStage,
# never the original source block type, and heading context never leaks a
# HEADING score into a content chunk. These are regression guards on the frozen
# Stage 1-6 behavior -- no production code changed in Stage 7.


def test_stage7_end_to_end_heading_plus_list_quality_is_default():
    # heading + prose lead-in + list -> LIST-typed child; heading context must
    # NOT give it HEADING_SCORE.
    items = [(f"- option {i} controls a specific behaviour of the subsystem in detail",
              BlockType.LIST, 0, 3, f"#/l{i}") for i in range(80)]
    chunks = _pipeline_from_blocks(
        [("3 Configuration", BlockType.HEADING, 1, 3, "#/h"),
         ("The options below control the subsystem in production deployments.",
          BlockType.TEXT, 0, 3, "#/lead")] + items,
        checksum="s7-list-quality")

    list_children = [c for c in chunks if c.metadata.block_type == BlockType.LIST]
    assert list_children
    for c in list_children:
        assert c.metadata.quality_score == QualityStage.DEFAULT_SCORE
        assert c.metadata.retrieval_priority == QualityStage.DEFAULT_PRIORITY
        assert c.metadata.is_table is False
        assert c.metadata.is_caption is False
        assert c.metadata.quality_score != QualityStage.HEADING_SCORE
    assert all(c.metadata.block_type != BlockType.HEADING for c in chunks)


def test_stage7_end_to_end_oversized_table_every_child_scored_as_table():
    table = _md_table(["Metric", "Value", "Delta"], 140)
    blocks = [
        ("2 Results", BlockType.HEADING, 1, 3, "#/h"),
        ("We evaluated the model on the development set and summarise results below.",
         BlockType.TEXT, 0, 3, "#/lead"),
        (table, BlockType.TABLE, 0, 3, "#/tbl"),
    ]
    chunks = _pipeline_from_blocks(blocks, checksum="s7-oversized-table")

    table_children = [c for c in chunks if c.metadata.block_type == BlockType.TABLE]
    assert len(table_children) >= 2
    for c in table_children:
        assert c.metadata.is_table is True
        assert c.metadata.quality_score == QualityStage.TABLE_SCORE
        assert c.metadata.retrieval_priority == QualityStage.TABLE_PRIORITY
    # no child is heading-typed / heading-scored
    for c in chunks:
        assert c.metadata.block_type != BlockType.HEADING
        assert c.metadata.quality_score != QualityStage.HEADING_SCORE

    # atomicity unchanged: every data row survives whole, exactly once
    original_rows = [ln for ln in table.split("\n") if ln.startswith("| cell")]
    seen: list[str] = []
    for c in table_children:
        assert count_tokens(c.text) <= DEFAULT_CHUNKING_CONFIG.embed_max
        assert c.text.count("2 Results") == 1
        lines = [ln for ln in c.text.split("\n") if ln.strip()]
        seen += [ln for ln in lines if ln.startswith("| cell")]
    assert seen == original_rows


def test_stage7_type_flag_invariants_full_pipeline():
    chunks = _pipeline_from_blocks([
        ("1 Overview", BlockType.HEADING, 1, 1, "#/h1"),
        ("A genuine overview paragraph describing the system at a high level.",
         BlockType.TEXT, 0, 1, "#/t1"),
        ("2 Data", BlockType.HEADING, 1, 2, "#/h2"),
        (_md_table(["k", "v", "note"], 3), BlockType.TABLE, 0, 2, "#/tbl"),
        ("Figure 1", BlockType.HEADING, 1, 3, "#/h3"),
        ("Figure 1: the overall architecture of the ingestion pipeline.",
         BlockType.CAPTION, 0, 3, "#/cap"),
        ("Config", BlockType.HEADING, 1, 4, "#/h4"),
        ("- flag one is enabled", BlockType.LIST, 0, 4, "#/l1"),
        ("- flag two is disabled", BlockType.LIST, 0, 4, "#/l2"),
    ], checksum="s7-invariants")

    for c in chunks:
        bt = c.metadata.block_type
        assert c.metadata.is_table is (bt == BlockType.TABLE)
        assert c.metadata.is_caption is (bt == BlockType.CAPTION)
        assert c.metadata.is_formula is (bt == BlockType.FORMULA)
        assert bt != BlockType.HEADING
        if bt == BlockType.TABLE:
            assert c.metadata.quality_score == QualityStage.TABLE_SCORE
        elif bt == BlockType.CAPTION:
            assert c.metadata.quality_score == QualityStage.CAPTION_SCORE
        elif bt in (BlockType.TEXT, BlockType.LIST):
            # default unless a section-title rule (References/Appendix/metadata)
            # applies -- none do in this fixture
            assert c.metadata.quality_score == QualityStage.DEFAULT_SCORE
        # the model intentionally has no is_list field
        assert not hasattr(c.metadata, "is_list")


def test_stage7_qualitystage_output_is_deterministic():
    def make():
        return [
            DocumentChunk("2 Results\n\n| a | b |\n| 1 | 2 |", 0, ChunkMetadata(
                block_type=BlockType.TABLE, section_title="2 Results")),
            DocumentChunk("Figure 3\n\nFigure 3: the request flow.", 1, ChunkMetadata(
                block_type=BlockType.CAPTION, section_title="Figure 3")),
            DocumentChunk("References\n\nDoe, J. Something. 2020.", 2, ChunkMetadata(
                block_type=BlockType.LIST, section_title="References")),
            DocumentChunk("Appendix A\n\nExtra derivations follow.", 3, ChunkMetadata(
                block_type=BlockType.TEXT, section_title="Appendix A")),
            DocumentChunk("3 Method\n\nOrdinary prose body of the section.", 4, ChunkMetadata(
                block_type=BlockType.TEXT, section_title="3 Method")),
            DocumentChunk("Authors\n\nAuthors: Jane Doe, Institute.", 5, ChunkMetadata(
                block_type=BlockType.TEXT, section_title="Authors")),
        ]

    fields = ("quality_score", "retrieval_priority", "is_reference", "is_appendix",
              "is_metadata", "is_caption", "is_table", "is_formula")

    def snapshot(chunks):
        return [tuple(getattr(c.metadata, f) for f in fields) for c in chunks]

    a = make(); QualityStage().run(a)
    b = make(); QualityStage().run(b)
    assert snapshot(a) == snapshot(b)
    # establish concrete expected values, not just equality
    assert snapshot(a) == [
        (QualityStage.TABLE_SCORE, QualityStage.TABLE_PRIORITY, False, False, False, False, True, False),
        (QualityStage.CAPTION_SCORE, QualityStage.CAPTION_PRIORITY, False, False, False, True, False, False),
        (QualityStage.REFERENCE_SCORE, QualityStage.REFERENCE_PRIORITY, True, False, False, False, False, False),
        (QualityStage.APPENDIX_SCORE, QualityStage.APPENDIX_PRIORITY, False, True, False, False, False, False),
        (QualityStage.DEFAULT_SCORE, QualityStage.DEFAULT_PRIORITY, False, False, False, False, False, False),
        (QualityStage.METADATA_SCORE, QualityStage.METADATA_PRIORITY, False, False, True, False, False, False),
    ]
    # re-running on already-scored chunks is idempotent
    QualityStage().run(a)
    assert snapshot(a) == snapshot(b)
