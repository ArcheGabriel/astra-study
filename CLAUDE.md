# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Astra Study is an AI-powered multimodal study assistant: a Retrieval-Augmented Generation
(RAG) chat over user-uploaded documents. The repo contains three deployable pieces plus a
migration and evaluation harness:

- `app/` – FastAPI backend (API, RAG pipeline, auth, persistence)
- `frontend/` – Streamlit workspace UI that talks to the backend over HTTP/SSE
- `evaluation/` – LangSmith dataset sync + experiment runner; `chunking_report.py` offline
  structural evaluator + `artifacts/`
- `scripts/` – operational one-offs (`reingest_document.py`)
- `alembic/` – database migrations

Package/dependency manager is **uv**. Python 3.11–3.13.

The top-level `ingestion/`, `orchestration/`, `prompts/`, `docs/`, `docker/` directories are
empty placeholders — all real code lives under `app/`, `frontend/`, and `evaluation/`.

## Commands

```bash
uv sync                                             # install deps (incl. dev group)
cp .env.example .env                                # then fill in secrets

uv run uvicorn app.main:app --reload                # backend on :8000, prefix /api/v1
uv run python -m streamlit run frontend/app.py      # frontend (expects backend on 127.0.0.1:8000)

uv run alembic upgrade head                         # apply migrations
uv run alembic revision --autogenerate -m "msg"     # new migration

uv run pytest tests/unit -q                         # THE normal check (fast; ML deps are faked)
uv run pytest tests/unit/test_chunking.py -q        # one file
uv run pytest tests/unit/test_provenance.py::test_pdf_page_and_bbox_provenance -q   # one test

uv run python -m evaluation.runner                  # run LangSmith evaluation experiment
uv run python -m evaluation.chunking_report analyze --blocks <blocks.json> --out <report.json>   # offline chunk structural report
```

Frontend API base URL is overridable with `ASTRA_API_URL`.

pytest config lives in `pyproject.toml`: `pythonpath=["."]`, `testpaths=["tests"]`. Root-level
`test_*.py` files (`test_chunk_pipeline.py`, etc.) are legacy scratch scripts and are **not**
collected.

**Never run a bare `uv run pytest` / `pytest -q` in this repo.** `testpaths=["tests"]` collects
`tests/integration/` too, and `tests/integration/test_dense_pipeline.py::test_dense_pipeline`
calls `DensePipeline().recreate_collection()` — which **deletes and recreates the production
Qdrant collection** (`DenseRepository.COLLECTION_NAME` == `settings.QDRANT_COLLECTION_NAME`,
default `astra_study`, with no test-specific override). There is no test-collection isolation and
no snapshot/backup anywhere in the repo. Scope every run to `tests/unit` (or otherwise exclude
`tests/integration`). `tests/unit/` fakes Docling and all ML models and is the self-contained
suite; `tests/integration/` hits **live** Qdrant / OpenAI / downloaded models and a populated
vector store — run individual files deliberately, never as part of a normal check.

## Architecture

### Request/DI layering (backend)

`app/api/v1/*` routers → `app/services/*` (orchestration) → `app/repositories/*` (DB access) +
domain packages (`chunking`, `search`, `retrieval`, `reranking`, `generation`, `ingestion`, `ai`).

- `app/dependencies/services.py` – per-request wiring of services/repositories (FastAPI `Depends`).
- `app/dependencies/resources.py` – process-wide `@lru_cache(maxsize=1)` singletons for heavy ML
  models: the OpenAI-backed `LLMService` and the CrossEncoder `RerankingService`. The reranker is
  preloaded in `app/main.py`'s lifespan so the model is warm before the first request.
- `app/dependencies/auth.py::get_current_user` – OAuth2 password bearer + JWT; every chat and
  document route depends on it, and retrieval is always scoped to the authenticated `user_id`.

### Ingestion pipeline (upload → vectors)

1. `POST /api/v1/documents` stores the file and schedules ingestion via FastAPI `BackgroundTasks`
   (`IngestionService.ingest_document`).
2. `app/ingestion/factory.py::ProcessorFactory` selects a processor by extension. **Docling is the
   only processor** (`app/ingestion/processors/docling.py`) and handles `.pdf .docx .xlsx .csv
   .jpg .jpeg .png`, with RapidOCR for scanned/image input. It emits an `ExtractionResult` of
   `DocumentBlock`s, each carrying `BlockProvenance` (`app/document/models.py`).
3. `app/chunking/pipeline.py::ChunkPipeline` runs 8 ordered stages, one per file under
   `app/chunking/stages/`: `Paragraph → Metadata → Merge → Recursive → Semantic → Filter →
   Quality → Finalize`. See "Chunking pipeline contract" below.
4. `app/search/hybrid/pipeline.py::HybridPipeline.index` embeds each chunk as a **dense** vector
   (OpenAI embeddings) and a **sparse** vector, then upserts to Qdrant with a compact,
   JSON-serializable payload built by `app/search/{dense,hybrid}/mapper.py` (never whole Docling
   objects).

### Chunking pipeline contract (`app/chunking/`)

This pipeline went through a large staged refactor (`feat/chunking-improvements`, Stages 1–7)
and is now **frozen** — treat its behaviour as a contract, verified by `tests/unit/test_chunking.py`
(the executable spec) and the offline evaluator. Do not reopen it without an explicit reason and
a failing test.

- **Size limits live only in `app/chunking/config.py::ChunkingConfig`** (token counts:
  `embed_max=700`, `overlap=100`, `merge_min=120`, `section_soft=1200`, `section_hard=1600`).
  Every stage takes a `config` override for tests. No stage hard-codes a size.
- `MetadataStage` reconstructs `heading_path`/`section_title`/`section_id` (LaTeX `1.2` and
  Word `1.2.` numbering) and an **internal `section_key`** (tuple; numbered id or cleaned title
  per level) used with `section_contains()` for same/descendant/sibling section boundary
  decisions. `section_key` is **not** in the Qdrant payload.
- `MergeStage` folds a heading into its section's content (**a content-free heading is never
  emitted as a vector**), locks the chunk's **effective `block_type` to the first non-heading
  contributor**, and records one **`ContentSegment`** per contributing source block
  (`block_type` + text + provenance + `source_block_index`) on `ChunkMetadata.content_segments`
  — internal, **not** in the payload.
- `RecursiveStage` splits oversized sections and re-prefixes the deepest heading on every child
  exactly once. When `content_segments` is present (the normal MergeStage path) it uses the
  **authoritative path**: it routes each segment by its real Docling `block_type` —
  `TABLE` → row-atomic split (markdown header repeated, a data row is never divided),
  `LIST` → item-atomic packing (a list item is never divided), prose → sentence windows — and
  attributes provenance to each child **exactly** from its contributing segments (no fuzzy
  matching). A child that contains a `TABLE` segment is typed `TABLE`; else a `LIST` segment →
  `LIST`; else it keeps the effective type. Page/block ranges are recomputed **body-only** (the
  heading prefix's page never widens them). The legacy text-derived path (`_split_source` +
  `_align_provenance` + `_segment_overlaps`) is retained only for chunks with no
  `content_segments`.
- `SemanticStage` concatenates a tiny same-section neighbour and attaches a caption to the block
  after it; its structural guard means a `TABLE`/`LIST` chunk merges **only** with the same
  structural type in the same section.
- `QualityStage` scores the **effective `block_type`** (`TABLE`→`TABLE_SCORE`/`is_table`,
  `CAPTION`→`CAPTION_SCORE`/`is_caption`, `TEXT`/`LIST`→`DEFAULT_SCORE`); `References`/`Appendix`
  score from `section_title`. `METADATA_PATTERN` matches the chunk **body with the folded
  heading line stripped**, so a section merely *titled* `Authorization`/`DOI Routing` is not
  mis-scored as front-matter. Do not change the scoring constants or policy.
- `FinalizeStage` assigns deterministic `uuid5` chunk/document IDs (derived from the file
  checksum, so re-ingesting an identical file is idempotent) and hard-validates every chunk
  (non-empty text, valid page/block ranges, matching counts) — it raises rather than emit a bad
  chunk.
- **Determinism is required**: identical `ExtractionResult` in → byte-identical chunks out.
- **Accepted, frozen limitations** (do not "fix"): (1) content-free parent headings carry no
  `source_item_id` — `heading_path` preserves their context; (2) rare non-consecutive duplicate
  heading folding from Docling; (3) a single indivisible table row / list item may exceed
  `embed_max`; (4) identical prose sentences across different source segments can cause bounded
  provenance over-approximation.
- `evaluation/chunking_report.py` is the **offline structural evaluator** (no Qdrant, no OpenAI):
  `extract` a document's Docling blocks to JSON, `analyze` those blocks into a deterministic
  structural report (token distribution, over-limit / heading-only / structural-atomicity /
  provenance / range / determinism metrics), `compare` two reports. Frozen block snapshots and
  stage-to-stage comparisons live in `evaluation/artifacts/`.
- `scripts/reingest_document.py` re-runs one document through
  `DoclingProcessor → ChunkPipeline → HybridPipeline.index`; it is **dry-run by default** and
  refuses to write to Qdrant without `--commit --yes-write-to-qdrant --user-id`.

### Retrieval + generation (`app/ai/pipeline.py::AIPipeline`)

conversation history → LLM query rewrite → `RetrievalService`:
Qdrant hybrid query filtered by `user_id` (`QDRANT_HYBRID_CANDIDATE_LIMIT` = 50) →
CrossEncoder `RerankingService` → top `RETRIEVAL_TOP_K` (= 5) `RetrievedContext` objects →
`GenerationService` builds the prompt (`app/generation/prompt_builder.py`), streams the answer
from OpenAI, and derives citations.

`RetrievalService.retrieve` / `__call__` (and `BaseRetrievalService`) are **keyword-only and
tenant-scoped**: `retrieve(*, query: str, user_id: int)`. An empty result (no hybrid hits, or
everything filtered out in reranking) returns an empty `RetrievalResult` — it does **not** raise
(`NoRetrievalResultsError` exists but is unused).

`app/ai/` is the orchestration layer (query rewriting, title/summary generation, the
conversation `AIPipeline`); `app/generation/` is the narrower "build prompt → call LLM →
produce `GenerationResponse` + citations" step that `AIPipeline` calls into. `ConversationService`
(`app/services/conversation.py`) sits above `AIPipeline` and owns message persistence + the SSE
event loop.

### Citations (single source of truth)

`GenerationService.citations_for(request, answer=None)` (`app/generation/service.py`) is the
**only** place citations are produced, and is used by both the streaming and non-streaming
endpoints so they never diverge. The `Citation` model (`app/generation/models.py`) is a frozen
dataclass; new fields must be optional/`None`-defaulted for backward compatibility.

Citation **ordering** is deterministic (no LLM, no thresholds), bounded, and never drops or
merges evidence — it only re-sorts the retrieved chunks:

```
score  =  reranker_score
        + _heading_match(term_weights, citation)  * 0.20   # section TITLE answers the question
        + answer_support                          * 0.15   # only when an answer is available
```

- `_query_term_weights` down-weights query terms that name the document topic (in the source
  filename, or in most retrieved chunks — e.g. "BERT" in a BERT paper) and up-weights terms that
  pin down one section (e.g. "Problem Statement"), so a heading merely repeating the entity gets
  ~no bonus.
- `answer_support` (populated when `answer` is passed) is deterministic lexical overlap between
  the generated answer and the chunk's own text; `None` when unmeasured (no answer / chunk too
  short) — never treated as "unsupported".
- Dedup key includes `chunk_uuid`; only exact-duplicate chunks collapse, distinct chunks in the
  same section stay individually traceable.

Provenance data flow, end to end:
`Docling item.prov` → `BlockProvenance` → `ChunkMetadata.provenance` → Qdrant payload
`provenance` → `RetrievedContext.provenance` → `Citation.provenance`.

Docling 2.124 only exposes `page_no`, `bbox` (`l/t/r/b` + `coord_origin`) and `charspan` per
item, and no per-item OCR flag. **Missing metadata must stay `null` — never fabricate pages,
sections, sheet names, bboxes or OCR status.** DOCX/XLSX/CSV legitimately have no page number;
lean on `heading_path`/`section` and `sheet_name` instead.

Treated as frozen unless a change is explicitly required and backed by a failing test: the
chunking pipeline (see its contract above), retrieval ranking, citation scoring, the Qdrant
payload schema / mappers, `BlockProvenance`, the `uuid5` ID strategy, `ChunkPipeline` stage
ordering, the SSE streaming protocol, and the Streamlit layout. Citation-precision work is
deterministic (no LLM in the citation path).

### Streaming protocol

`POST /api/v1/chats/{chat_id}/messages/stream` returns SSE:

```
data: {"text": "..."}          # repeated
event: citations
data: {"citations": [...]}      # exactly once, after all text
event: done
data: {}
```

`POST /api/v1/chats/{chat_id}/messages` is the non-streaming equivalent and returns the same
citation payload.

### Frontend

`frontend/app.py` renders a fixed 3-column Streamlit layout (sidebar / workspace / sources panel).
`frontend/api/*` are thin HTTP clients over the backend (`api_client.py` handles auth + SSE
parsing); `frontend/ui/*` are the view functions; `frontend/models/*` are response DTOs. All
cross-render state (JWT token, active chat, messages, citations, documents) lives in
`st.session_state`, initialised in `frontend/ui/state.py`. Auth is a JWT bearer token obtained
from `/api/v1/auth` and attached to every request.

### Persistence

- **PostgreSQL** via SQLAlchemy 2.0 + Alembic – users, chats, messages, documents
  (`DATABASE_URL`). A checked-in `astra_study.db` SQLite file exists for local dev.
- **Qdrant** – one collection (`QDRANT_COLLECTION_NAME`, default `astra_study`) with named
  vectors `dense` and `sparse`; payload includes a `schema_version` field. `docker-compose.yml`
  is empty — run Qdrant separately (default `:6333`).
- **Local filesystem** (`storage/`) – uploaded source files.

### Observability

LangSmith tracing is pervasive via `@traceable` decorators on service/pipeline methods;
`app/main.py`'s lifespan exports the `LANGSMITH_*` env vars. Langfuse is also configured.

## Environment / platform notes

- All required env vars are declared in `app/config/settings.py` (`pydantic-settings`); start
  from `.env.example`. Missing non-defaulted vars fail app startup.
- Windows: `DOCLING_DISABLE_HF_SYMLINKS=true` makes `app/ingestion/processors/docling.py` set
  `HF_HUB_DISABLE_SYMLINKS` before importing Docling, so first-run HuggingFace model downloads
  work without Developer Mode.
- Unit tests fake Docling and the ML models; do not add tests that require downloading models.
- `tests/unit` should be fully green. A single `langsmith` deprecation warning is expected.
  Anything under `tests/integration` needs live services (and one test recreates the production
  Qdrant collection — see Commands) and is not part of a normal check.
- The Docling models are downloaded to the HuggingFace cache; `evaluation.chunking_report extract`
  runs real Docling offline (no Qdrant/OpenAI). Re-extracting a document takes minutes.
