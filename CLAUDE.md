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
- `scripts/` – operational one-offs (`reingest_document.py`, `grant_admin.py`)
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
uv run pytest tests/unit/test_conversation_memory.py -q   # rolling-summary / recent-window spec
uv run pytest tests/unit/test_qdrant_isolation.py -q      # offline regression for the test-collection guard
uv run pytest tests/unit/test_access_context.py tests/unit/test_rbac_5b_propagation.py -q   # AccessContext + retrieval-threading spec
uv run pytest tests/unit/test_rbac_5c_authorization_filter.py tests/unit/test_rbac_5c_payload.py tests/unit/test_rbac_5c_evaluation_access.py -q   # Qdrant retrieval authorization filter + payload spec
uv run pytest tests/unit/test_rbac_5d_document_authorization.py -q   # document list/get/download/delete authorization spec
uv run pytest tests/unit/test_rbac_5e_document_creation_authorization.py -q   # document upload (INDIVIDUAL/TEAM/ORGANISATION) creation authorization spec
uv run pytest tests/unit/test_rbac_5f_reingest_metadata.py -q   # scripts/reingest_document.py RBAC metadata sourcing spec
uv run pytest tests/unit/test_rbac_5g_whoami.py -q   # GET /users/me RBAC context (organisation role + team memberships) spec
uv run pytest tests/unit/test_rbac_5h_team_creation_and_listing.py -q   # team creation (ADMIN/MANAGER) + organisation-scoped listing spec
uv run pytest tests/unit/test_rbac_5i_team_membership_management.py -q   # direct team membership management (add/remove/promote, last-manager invariant) spec
uv run pytest tests/unit/test_rbac_5j_org_manager_jurisdiction.py -q   # Org Manager <-> Team jurisdiction (grant/revoke, SQL/Qdrant parity) spec

uv run pytest tests/integration/test_hybrid_pipeline.py -q   # one integration file: live Qdrant+OpenAI+Docling, minutes per file, isolated to astra_study_test
uv run pytest tests/integration/test_rbac_qdrant_authorization.py -q   # real Qdrant round-trip: full RBAC authorization matrix via DenseRepository.hybrid_search, isolated to astra_study_test, no OpenAI/Docling

uv run python -m evaluation.runner                  # run LangSmith evaluation experiment
uv run python -m evaluation.chunking_report analyze --blocks <blocks.json> --out <report.json>   # offline chunk structural report

uv run python -m scripts.grant_admin --email user@example.com   # promote an existing user to OrgRole.ADMIN
```

Frontend API base URL is overridable with `ASTRA_API_URL`.

pytest config lives in `pyproject.toml`: `pythonpath=["."]`, `testpaths=["tests"]`. Root-level
`test_*.py` files (`test_chunk_pipeline.py`, etc.) are legacy scratch scripts and are **not**
collected.

`tests/unit/` fakes Docling and all ML models and is the self-contained suite — this is THE
normal check. `tests/integration/` hits **live** Qdrant / OpenAI / downloaded models and takes
minutes per file (real Docling extraction + embeddings); run individual files deliberately, not
as part of a routine check. `testpaths=["tests"]` means a bare `pytest` collects
`tests/integration/` too — still scope routine runs to `tests/unit`.

**Qdrant test isolation (`tests/conftest.py`).** Several integration tests call
`recreate_collection()`, which deletes and recreates whatever `DenseRepository.COLLECTION_NAME`
resolves to. `DenseRepository.COLLECTION_NAME` is a **class attribute bound at import time** from
`settings.QDRANT_COLLECTION_NAME` (default `astra_study` — the production collection). The root
`tests/conftest.py` is imported before any test module and defends against this:

- forces `QDRANT_COLLECTION_NAME` to `astra_study_test` and defensively overwrites both the
  `settings` value and the already-bound `DenseRepository.COLLECTION_NAME`;
- **allowlist**: raises `RuntimeError` at collection time if `QDRANT_COLLECTION_NAME` is set to
  anything other than unset or exactly `astra_study_test` (production `astra_study` can never be
  reached from tests);
- a `pytest_sessionfinish` hook drops `astra_study_test` afterward, but only when the session
  actually collected a `tests/integration/` test — a `tests/unit`-only run never constructs a
  Qdrant client or touches the network.

`tests/unit/test_qdrant_isolation.py` is the offline regression. Do not weaken this guard or edit
`tests/conftest.py` casually. To run integration tests against real Qdrant, leave
`QDRANT_COLLECTION_NAME` unset so isolation applies.

`tests/integration/test_rbac_qdrant_authorization.py` is the real-Qdrant round-trip regression for
the full RBAC authorization chain (RBAC-6): it seeds points via the real `HybridMapper.build_payload`
into `astra_study_test` and asserts ALLOW/DENY for every branch of `DenseRepository._authorization_filter`
(team membership, Org Manager jurisdiction, ADMIN, INDIVIDUAL, ORGANISATION, `is_reference`/`is_appendix`
exclusion) by calling `DenseRepository.hybrid_search` itself — never a reimplemented shadow filter. It
needs no OpenAI/Docling (dense/sparse vectors are small deterministic non-semantic values, since only
payload fields participate in authorization filtering), so it is far cheaper than
`test_hybrid_pipeline.py` despite also being a live-Qdrant integration test. Its fixture creates and
drops `astra_study_test` itself, independently re-asserting the collection name at every step on top of
`tests/conftest.py`'s guard.

Each integration test is **self-contained**: it extracts + chunks a fixture PDF (tracked ones
live in `tests/test_documents/`; `storage/uploads/*` is gitignored), `recreate_collection()`s the
isolated collection, and indexes before exercising retrieval/rerank/generation. The
hybrid/retrieval/generation paths are **tenant-scoped** — those tests stamp
`chunk.metadata.user_id = settings.EVALUATION_USER_ID` on every chunk (production does this in
`IngestionService`, not `ChunkPipeline`) and pass an `AccessContext(user_id=settings.EVALUATION_USER_ID, ...)`
to `HybridService` / `RetrievalService` (see "Authorization (RBAC)" — `organisation_id` there is
an explicitly-documented placeholder, not real data). The dense-only path (`test_dense_pipeline`)
is not filtered by `user_id`.

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
- `app/dependencies/access.py::get_access_context` – builds the request-scoped `AccessContext`
  (see "Authorization (RBAC)" below) from `current_user` + a fresh team-membership lookup; never
  from JWT claims or client-supplied request data.

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
- `scripts/reingest_document.py` re-runs one document (identified by `--document-id`, not a raw
  file path) through `LocalStorageService.get_file_path → DoclingProcessor → ChunkPipeline →
  HybridPipeline.index`; it is **dry-run by default** and refuses to write to Qdrant without
  `--commit --yes-write-to-qdrant`. It reads the `documents` table (to resolve the authoritative
  `document_id`/`user_id`/`organisation_id`/`team_id`/`access_scope` RBAC fields and the stored
  file path from the one `Document` row identified by `--document-id`, exactly mirroring
  `IngestionService.ingest_document`'s own stamping) but never writes to it — no row is created,
  updated, or deleted, and no status transition occurs.

### Retrieval + generation (`app/ai/pipeline.py::AIPipeline`)

conversation history → LLM query rewrite → `RetrievalService`:
Qdrant hybrid query filtered by `user_id` (`QDRANT_HYBRID_CANDIDATE_LIMIT` = 50) →
CrossEncoder `RerankingService` → top `RETRIEVAL_TOP_K` (= 5) `RetrievedContext` objects →
`GenerationService` builds the prompt (`app/generation/prompt_builder.py`), streams the answer
from OpenAI, and derives citations.

`RetrievalService.retrieve` / `__call__` (and `BaseRetrievalService`) are **keyword-only and
tenant-scoped**: `retrieve(*, query: str, access: AccessContext)`. `AccessContext` (see
"Authorization (RBAC)" below) is threaded unmodified through `AIPipeline → RetrievalService →
HybridService → DenseRepository.hybrid_search`, which builds its Qdrant filter from the full
`AccessContext` (own INDIVIDUAL documents, TEAM documents for teams the requester belongs to, and
— ADMIN only — ORGANISATION documents in their organisation; see
`DenseRepository._authorization_filter` under "Authorization (RBAC)"), combined via AND with the
existing `is_reference=False` / `is_appendix=False` structural filter. An empty result (no hybrid
hits, or everything filtered out in reranking) returns an empty `RetrievalResult` — it does **not**
raise (`NoRetrievalResultsError` exists but is unused).

`app/ai/` is the orchestration layer (query rewriting, title/summary generation, the
conversation `AIPipeline`); `app/generation/` is the narrower "build prompt → call LLM →
produce `GenerationResponse` + citations" step that `AIPipeline` calls into. `ConversationService`
(`app/services/conversation.py`) sits above `AIPipeline` and owns message persistence + the SSE
event loop.

### Conversation memory (rolling summary + recent window)

Long conversations do **not** send the whole transcript to the answer LLM. Message counting is
over **conversational messages only** (`MessageRole.USER` + `ASSISTANT`, one each;
`MessageRepository.get_conversational_messages` / `count_conversational_messages`, ordered by
`id` — not `created_at`, which is only second-precision on SQLite).

- First summary is generated once the conversation reaches
  `settings.INITIAL_SUMMARY_THRESHOLD` (= 20) messages (covers messages 1–20).
- The summary is then refreshed every `settings.SUMMARY_UPDATE_INTERVAL` (= 10) further
  messages (boundaries 30, 40, 50, …). Each refresh feeds the LLM the **previous summary + only
  the newly-accumulated messages** (`SummaryGenerator`'s merge prompt) — the transcript is never
  re-summarized from scratch.
- Once a summary exists, `AIPipeline` sends the answer LLM the **summary + the last
  `settings.RECENT_MESSAGE_WINDOW` (= 10) messages** (`_generation_history`), so answer-prompt
  size stays flat as the conversation grows. Before the first summary, full history is used.
- Retrieval-query rewriting keeps its **own** independent `QUERY_REWRITE_HISTORY_WINDOW` (= 20)
  slice of the full history — it is not reduced to the generation window.
- `ConversationSummaryService.update_summary(*, chat_id)` derives "how far the stored summary
  got" from `chat_sessions.summary_updated_at` vs message `created_at` (no extra schema). If a
  refresh fails it logs and preserves the existing summary; the pending-message count keeps
  growing so a later turn catches up (the delta then spans all un-summarized messages) — a
  failed boundary never silently drops context. An existing conversation already past the
  threshold with no summary gets a one-time full-history catch-up summary.
- The refresh runs **out of band** via FastAPI `BackgroundTasks`
  (`conversation_summary.run_summary_refresh`, its own DB session) — it never blocks the HTTP
  response or the SSE `done` event. The assistant message is persisted before the task is
  scheduled so it counts toward the next boundary.
- Storage is the existing `chat_sessions.summary` / `summary_updated_at` columns only — **no
  schema change**.
- The four tuning constants (`INITIAL_SUMMARY_THRESHOLD`, `SUMMARY_UPDATE_INTERVAL`,
  `RECENT_MESSAGE_WINDOW`, `QUERY_REWRITE_HISTORY_WINDOW`) all live in
  `app/config/settings.py`; every stage/service takes them as injected values (no hard-coded
  counts). `tests/unit/test_conversation_memory.py` is the executable spec for the boundary and
  windowing behaviour.

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
payload schema / mappers, `DenseRepository._authorization_filter`, `AccessContext`'s structure,
`BlockProvenance`, the `uuid5` ID strategy, `ChunkPipeline` stage ordering, the SSE streaming
protocol, and the Streamlit layout. Citation-precision work is deterministic (no LLM in the
citation path).

### Authorization (RBAC)

The relational schema, `AccessContext` identity threading, Qdrant retrieval-visibility filtering,
and the document-management API's create/read/delete authorization are all in place and enforced.

- **Org/team model** (`app/models/organisation.py`, `team.py`, `team_membership.py`): every
  `User` belongs to exactly one `Organisation` (`User.organisation_id`, NOT NULL) with an
  org-scoped `OrgRole` (`app/enums/organisation.py`: `MEMBER` / `MANAGER` / `ADMIN`). A `Team`
  belongs to one `Organisation`; `TeamMembership` (unique on `(user_id, team_id)`) carries its
  own per-membership `TeamRole` (`app/enums/team.py`: `MEMBER` / `MANAGER`) — a user can be a
  `MANAGER` of one team and a plain `MEMBER` of another. `OrgRole`/`TeamRole` govern *capabilities*
  (document creation/deletion, below), never document visibility directly. Team creation/listing
  (RBAC-5H) and direct team-membership management (RBAC-5I, below) exist; there is still no
  broader organisation-*management* API (creating an organisation, changing a user's `OrgRole`) —
  `app/repositories/team.py::TeamRepository` remains deliberately minimal beyond what team
  creation/listing needs (`get_by_id` inherited from `BaseRepository`, plus its own
  name-lookup/atomic-create methods below).
- **Document access scope** (`app/models/document.py`): `organisation_id`, optional `team_id`,
  and `access_scope` (`DocumentAccessScope` in `app/enums/document.py`: `INDIVIDUAL` / `TEAM` /
  `ORGANISATION`) are separate, deliberately-orthogonal concepts from role — access scope is a
  property of the document, never derived from the requester's role. `POST /documents/upload`
  accepts optional `access_scope`/`team_id` multipart form fields alongside `files`; omitted
  entirely (every pre-RBAC-5E client), they default to `INDIVIDUAL`/`None`, identical to legacy
  behavior. `DocumentService._can_create` authorizes the requested scope *before* any file is
  validated or stored — INDIVIDUAL: any authenticated user; TEAM: the requester must be an actual
  `TeamMembership` member of a `team_id` that belongs to their own organisation (**any** `OrgRole`
  or `TeamRole` qualifies — TEAM creation is a membership check, not a role check, and
  `TeamRole.MANAGER` is *not* required, unlike TEAM deletion below); ORGANISATION:
  `OrgRole.ADMIN` only. `organisation_id` is never accepted from the client in any branch — always
  `access.organisation_id`. A nonexistent `team_id` and a `team_id` belonging to a different
  organisation are deliberately indistinguishable (both raise `TeamNotFoundError`, 404) so a
  requester can never enumerate another organisation's teams; being an authenticated non-member of
  a team that *does* exist in their own org raises `TeamMembershipRequiredError` (403); a non-ADMIN
  requesting ORGANISATION raises `OrganisationScopeForbiddenError` (403); a malformed scope/team_id
  combination (e.g. `TEAM` with no `team_id`, `INDIVIDUAL`/`ORGANISATION` with one supplied) raises
  `InvalidAccessScopeError` (400) — all four in `app/exceptions/document.py`.
- **Migration**: `alembic/versions/116ced32c143_rbac_organisation_team_foundation.py` seeds one
  `Organisation` (slug `"default"`, looked up by slug — never a hardcoded id — in
  `UserService._get_default_organisation`) and adds the columns above via the SQLite-safe
  add-nullable → backfill → tighten-to-NOT-NULL `batch_alter_table` pattern (this project's dev
  DB is SQLite — see "Persistence"). `scripts/grant_admin.py --email <email>` promotes an
  *existing* user to `OrgRole.ADMIN` (never creates a user, never touches org membership, no
  hardcoded email) — the only bootstrap path to a first ADMIN.
- **`AccessContext`** (`app/retrieval/access.py`) is the single trusted, request-scoped
  authorization identity: a frozen/slotted dataclass of `user_id`, `organisation_id`,
  `team_ids: tuple[int, ...]` (canonical sorted/deduped, never a wildcard-empty list),
  `jurisdiction_team_ids: tuple[int, ...]` (RBAC-5J, identical canonicalization, a structurally
  independent relationship — see the jurisdiction bullet below), and `role`. It has no methods (no
  `can_read`, no `is_admin`) — it is a value object, not a policy; it also deliberately carries no
  per-team `TeamRole` (a flat set of team ids, not a role map) — anything that needs to know
  *which* role a user holds on a specific team (e.g. delete authorization, below) does a targeted
  `TeamMembershipRepository.get_membership(user_id=, team_id=)` lookup instead.
  `app/dependencies/access.py::get_access_context` builds it from `current_user` (itself resolved
  from the JWT by `get_current_user`) plus a fresh `TeamMembershipRepository` lookup and a fresh
  `OrgManagerTeamRepository` lookup — never from JWT claims or any client-supplied field.
  `evaluation/service.py::EvaluationService._resolve_access` builds the same complete
  `AccessContext` (including `jurisdiction_team_ids`) for the configured evaluation user.
- **Retrieval visibility (chat/RAG path)**: `AccessContext` is threaded through the full chat path
  (`app/api/v1/message.py` → `ConversationService` → `AIPipeline` → `RetrievalService` →
  `HybridService` → `DenseRepository.hybrid_search`), and `DenseRepository._authorization_filter`
  builds the actual Qdrant filter: AND of the structural conditions
  (`is_reference=False`/`is_appendix=False`) with the OR of every scope branch the requester
  qualifies for — INDIVIDUAL (own, plus legacy `schema_version=2` points grandfathered in to their
  owner only via `IsEmptyCondition` on the missing `access_scope` field, never relaxed further),
  TEAM-membership (only built when `access.team_ids` is non-empty; same organisation *and* team
  membership), TEAM-jurisdiction (RBAC-5J; only built when `access.role == OrgRole.MANAGER` *and*
  `access.jurisdiction_team_ids` is non-empty; same organisation *and* jurisdiction over that
  specific team — structurally independent of the membership branch, a jurisdiction team id never
  needs to also be a membership team id), TEAM-ADMIN (RBAC-5J; only built when
  `access.role == OrgRole.ADMIN`; unconditional over every TEAM document in the requester's own
  organisation, regardless of membership or jurisdiction), ORGANISATION (only built when
  `access.role == OrgRole.ADMIN`; `role` is a Python-level decision about which branches exist,
  never a condition evaluated inside Qdrant itself). This filter and the Qdrant payload schema it
  depends on (`schema_version`, `access_scope`, `organisation_id`, `team_id`, `document_id`,
  written by `HybridMapper.build_payload`) are treated as frozen — see "Treated as frozen" below;
  the RBAC-5J branches are additive OR-terms only and do not change this schema.
- **Document-management API (upload/list/get/download/delete)**: every route in
  `app/api/v1/document.py`, including `POST /documents/upload`, takes `access: AccessContext`
  (not `current_user`) and delegates to `DocumentService`. `GET /documents`,
  `GET /documents/{id}`, `GET /documents/{id}/download` delegate read visibility to
  `DocumentRepository.get_visible` / `get_by_id_visible` — the SQL-level mirror of
  `DenseRepository._authorization_filter`'s branch logic (`_visibility_conditions`, including the
  RBAC-5J TEAM-jurisdiction and TEAM-ADMIN branches), kept in one place so list/get/download can
  never authorize inconsistently with each other. An unauthorized
  or nonexistent document is indistinguishable (`DocumentNotFoundError`/404 either way — no
  enumeration signal). Delete authorization (`DocumentService._can_delete`) is *stricter* than
  read visibility: owner always; a TEAM document additionally by a `TeamRole.MANAGER` of that
  specific team (never a plain member, resolved via the targeted membership lookup above, never
  from `AccessContext.team_ids` alone); an ORGANISATION document additionally by an `OrgRole.ADMIN`
  of the same organisation; cross-organisation access is always denied first. Deletion order is
  deliberate and not a distributed transaction: `DenseRepository.delete_by_document_id` (Qdrant)
  → `storage_service.delete_file` → SQL row delete — if the Qdrant step fails the exception
  propagates and nothing else is touched, so a failed delete never reproduces the pre-RBAC-5D bug
  (SQL/file gone, Qdrant vectors orphaned forever). `delete_by_document_id` filters on the real SQL
  `Document.id` (written into the payload only by `HybridMapper.build_payload`, always paired with
  `schema_version=3`), which makes it structurally incapable of matching a legacy
  `schema_version=2` point — no separate schema-version heuristic needed.
  `scripts/reingest_document.py` (see its bullet above) uses the same `document_id`-sourcing
  discipline for manual re-indexing, so a reingested document remains deletable the same way.
- `evaluation/service.py::EvaluationService._resolve_access` builds a real, database-backed
  `AccessContext` for `settings.EVALUATION_USER_ID` (actual `organisation_id`/`role`/team
  memberships, via a short-lived `SessionLocal()` session) — distinct from `tests/integration/*`'s
  own hardcoded `_ACCESS` fixtures (see "Qdrant test isolation" above), which still use
  `organisation_id=settings.EVALUATION_USER_ID` as an explicit placeholder, not real data.
- `current_user` (not `access`) remains the sole input to chat-ownership checks
  (`ConversationService._validate_chat`) and document/message authorship — do not conflate the two
  identities.
- **Who-am-I / RBAC context exposure (`GET /users/me`)**: returns `UserProfileResponse`
  (`app/schemas/user.py`) — `id`/`username`/`email` plus `organisation_id`, `role` (`OrgRole`),
  `teams: list[TeamMembershipResponse]` (`team_id`/`team_name`/`role` per membership, ordered by
  `team_id` ascending via `TeamMembershipRepository.get_memberships_with_team_by_user_id`'s
  `joinedload`), and `managed_teams: list[ManagedTeamResponse]` (RBAC-5J; `team_id`/`team_name`
  only, **no `role` field** — jurisdiction is a single binary state, not a `TeamRole`, sourced from
  `OrgManagerTeamRepository.get_jurisdictions_with_team_by_user_id`). `teams` and `managed_teams`
  are populated by two independent repository calls and stay structurally separate — a user may
  appear in either, both, or neither; `managed_teams` is never derived from or merged into `teams`.
  `UserService.get_profile` builds this from `current_user` directly (`organisation_id`/`role`
  need no extra query) plus those two repository calls — it deliberately does **not** use
  `AccessContext`, which carries no team name or per-team `TeamRole` and would add a second,
  heavier identity path for values already in hand. `UserProfileResponse` is a separate
  schema from `UserResponse`/`TokenResponse`, which remain completely unchanged (still returned
  as-is by `POST /auth/register`/`POST /auth/login`/`POST /auth/token`) — extending `UserResponse`
  directly would have leaked this profile into those three responses and broken their existing
  `UserResponse.model_validate(user)` calls, since `User` has no `teams` attribute (only the lazy,
  name-less `team_memberships` relationship). The frontend mirrors this: `frontend/models/user.py`'s
  `User` dataclass carries the same optional `organisation_id`/`role`/`teams` fields (defaulted, so
  the slim login-response shape still parses). `frontend/ui/login.py` fetches
  `AuthService.get_current_user_profile()` **before** writing anything to session state: only if
  that call succeeds are `st.session_state.token` and `st.session_state.current_user` set together
  (replacing `token.user` with the richer profile) — if it raises, neither is set, so a login that
  succeeds but whose follow-up `/users/me` call fails can never leave the session authenticated
  (`frontend/app.py` gates the workspace on `token`) with `current_user` still `None`.
- **Team creation & organisation-scoped listing (`POST /teams`, `GET /teams`)**: `TeamService.create_team`
  requires `access.role` to be `OrgRole.ADMIN` or `OrgRole.MANAGER` (`OrgRole.MEMBER` rejected before
  any database read, matching `_can_create`'s ordering); `organisation_id` always comes from
  `AccessContext` (`TeamCreate` has no `organisation_id` field at all — structurally, not just
  validation-wise, unsupplyable). `TeamRepository.create_with_initial_manager` persists the `Team`
  and its creator's initial `TeamMembership` (`role=TeamRole.MANAGER`) in **one transaction**
  (`add` → `flush` → `add` → `commit`, all inside one `try`/`except IntegrityError`) so a team can
  never exist with zero managers, even under failure — this is the first place `OrgRole.MANAGER`
  gains any defined behavior anywhere in this codebase. A duplicate `(organisation_id, name)` is
  rejected pre-emptively (`get_by_organisation_and_name`) and, for the TOCTOU race between that
  check and the commit, the commit-time `IntegrityError` is narrowly matched against the exact
  SQLite message for this constraint (`"teams.organisation_id"` and `"teams.name"` both present)
  and translated to `TeamNameAlreadyExistsError` — any other `IntegrityError` cause re-raises
  unchanged. `TeamService.list_teams` returns every team in `access.organisation_id` ordered by
  `id` ascending; membership is never a filter (listing does not imply membership). Member/role
  management, team rename/delete, and organisation management are all explicitly deferred to later
  milestones — see this stage's investigation and implementation-plan reports.
- **Direct team membership management (`POST/DELETE /teams/{team_id}/members`,
  `POST /teams/{team_id}/members/{user_id}/promote`)**: `TeamMembershipService` (a class distinct
  from `TeamService` — different authorization model, per-team `TeamRole` rather than org-wide
  `OrgRole`) implements exactly four operations: add a `TeamRole.MEMBER`, remove a member of either
  role, promote `MEMBER → MANAGER`, and remove a `MANAGER` subject to the last-manager invariant.
  **Only that specific team's own `TeamRole.MANAGER` may call any of the four** — resolved via a
  targeted `TeamMembershipRepository.get_membership(user_id=access.user_id, team_id=team_id)`
  lookup, never `AccessContext.team_ids` (which carries no per-team role). `OrgRole.ADMIN` and
  `OrgRole.MANAGER` (without independently holding that team's `TeamRole.MANAGER`) both have **no**
  direct membership-mutation authority — an ADMIN-initiated add is deferred to a future
  membership-request/approval-workflow milestone, not built here. There is **no
  `MANAGER → MEMBER` demotion operation anywhere** — a `TeamRole.MANAGER` only ever stops being one
  by being removed from the team entirely (`TeamMembershipRepository.remove_membership`), never by
  having its `role` rewritten; a team must always retain at least one manager. This last-manager
  invariant is enforced by the **DELETE statement itself**, not by a prior `SELECT count(...)`: the
  remaining-manager count is a correlated subquery embedded in the DELETE's own `WHERE` clause, so
  SQLite evaluates "does another manager exist" and "remove this row" as one indivisible write —
  closing a genuine race where two concurrent removals of two *different* managers on the same
  two-manager team could otherwise both observe "one other manager remains" and both succeed,
  leaving zero. `add_membership` similarly wraps its insert in the same `IntegrityError`-translation
  pattern as `TeamRepository.create_with_initial_manager` (pre-check, then guard the commit itself
  against the TOCTOU race). Both concurrency properties have permanent, repository-tracked
  regression tests using a real file-backed SQLite database, independent sessions, real OS threads,
  and a `threading.Barrier` (`tests/unit/test_rbac_5i_team_membership_management.py`) — not just
  sequential test calls. Team/target-user organisation checks (`TeamNotFoundError` /
  `UserNotFoundError`, both collapsing "doesn't exist" and "wrong organisation" for
  enumeration-safety, mirroring `TeamNotFoundError`'s existing precedent) run before authorization
  is even reached for the team, and target-user resolution runs only *after* authorization succeeds
  — an unauthorized actor never learns whether a given target user id exists. This stage introduces
  no jurisdiction concept, model, or field — see the RBAC-5J bullet below for that separate,
  supervisory relationship.
- **Org Manager jurisdiction (`POST/DELETE /teams/{team_id}/managers/{user_id}`)**: `OrgManagerTeam`
  (`app/models/org_manager_team.py`) is a many-to-many relationship — unique on `(user_id, team_id)`,
  no `role` column — recording which `OrgRole.MANAGER` supervises which team. **Structurally
  independent of `TeamMembership`**: a user can hold jurisdiction over a team without ever having a
  `TeamMembership` row for it, and vice versa; `OrgManagerTeamService`/`Repository` never read or
  write `TeamMembership`, and granting/revoking jurisdiction never creates, deletes, or touches a
  `TeamMembership` row. `TeamRole.MANAGER` (operational, per-team) and `OrgRole.MANAGER`-with-
  jurisdiction (supervisory, org-level) remain distinct concepts — jurisdiction never grants
  `TeamRole.MANAGER`, and being a team's `TeamRole.MANAGER` grants no jurisdiction-mutation
  authority. **Only `OrgRole.ADMIN` may grant or revoke jurisdiction** (`OrgManagerTeamService`):
  authorization runs first (`access.role != OrgRole.ADMIN` rejected before any database read tied
  to the request), then team/target-user are resolved in the ADMIN's own organisation
  (`TeamNotFoundError`/`UserNotFoundError`, both collapsing "doesn't exist" and "wrong
  organisation" for enumeration safety, mirroring existing precedent), then the target user's
  *current* `OrgRole` is verified to be `MANAGER` (`TargetNotOrgManagerError` otherwise) — the
  target's own role is checked for eligibility only, never consulted for authority. Creating a team
  does **not** automatically grant the creator jurisdiction over it (`TeamService.create_team` is
  untouched) — jurisdiction only ever exists after an explicit ADMIN grant. `OrgManagerTeamRepository.grant`
  uses the same pre-check + `IntegrityError`-translation pattern as `TeamMembershipRepository.add_membership`
  for the concurrent-duplicate-grant race; `revoke` has **no** minimum-jurisdiction-holder invariant
  (unlike the last-manager invariant for `TeamMembership` — a team may validly have zero Org
  Managers overseeing it, since its operational management continues via `TeamRole.MANAGER`
  regardless), so a plain fetch-then-delete is safe. Jurisdiction is **read-only**: it adds a TEAM
  branch to `DenseRepository._authorization_filter` / `DocumentRepository._visibility_conditions`
  (see above) but is never consulted by `DocumentService._can_create` (TEAM creation still requires
  actual `TeamMembership`) or `_can_delete` (unchanged — owner, that team's `TeamRole.MANAGER`, or
  ADMIN-for-ORGANISATION-scope only). As part of this same milestone, `OrgRole.ADMIN` additionally
  gained **unconditional** TEAM-document read visibility across their own organisation (the
  TEAM-ADMIN branch above) — a deliberate behavior change from ADMIN's previous membership-only
  TEAM visibility. Migration: `alembic/versions/d18a69b8ede3_rbac_org_manager_team_jurisdiction.py`
  (purely additive — one new table, no backfill, no existing table altered).
  `tests/unit/test_rbac_5j_org_manager_jurisdiction.py` includes a permanent SQL/Qdrant-parity
  test suite that evaluates the actual `Filter` object `_authorization_filter` returns (via a
  generic Qdrant boolean-semantics walker, never a second reimplementation of the authorization
  logic) against a real document's payload, so a future regression in either authorization path is
  caught by direct comparison, not by two independently-written expectations. Membership-request
  workflows and any Org-Manager-management UI remain out of scope for this stage.

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

- SQLAlchemy 2.0 + Alembic via `DATABASE_URL` – users, organisations, teams, team memberships,
  chats, messages, documents. **Local dev uses SQLite** (`.env`'s `DATABASE_URL=sqlite:///./astra_study.db`,
  a checked-in file) — `DATABASE_URL` is a generic connection string so Postgres works too, but
  SQLite is the actual configured/tested setup here; new migrations must stay SQLite-compatible
  (see the RBAC migration's `batch_alter_table` pattern above) rather than assuming Postgres-only
  DDL.
- **Qdrant** – one collection (`QDRANT_COLLECTION_NAME`, default `astra_study`) with named
  vectors `dense` and `sparse`; payload includes a `schema_version` field. `docker-compose.yml`
  is empty — run Qdrant separately (default `:6333`). The test suite uses a separate
  `astra_study_test` collection (see "Qdrant test isolation").
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
- `tests/unit` should be fully green. Two deprecation warnings are expected (`langsmith`'s
  `_openai_agents` module move, and stdlib `ast.Str` from a LangSmith dependency).
  Anything under `tests/integration` needs live services (Qdrant, OpenAI, downloaded models),
  takes minutes per file, and is not part of a normal check; it is isolated from the production
  Qdrant collection by `tests/conftest.py` (see "Qdrant test isolation"). Integration runs also
  emit two Docling `DeprecationWarning`s.
- The Docling models are downloaded to the HuggingFace cache; `evaluation.chunking_report extract`
  runs real Docling offline (no Qdrant/OpenAI). Re-extracting a document takes minutes.
