# Graph Report - Astra-Study  (2026-09-27)

## Corpus Check
- 6 files · ~259,401 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3279 nodes · 8237 edges · 221 communities (103 shown, 82 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 591 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Document Repository Visibility
- Qdrant Authorization Filter Tests
- RBAC-5J Test Fixtures
- Merge Stage Section Chunks
- Document Creation Test Fixtures
- Base Document Handler
- Team Exceptions
- Chunking Validation Helpers
- Qdrant Test Isolation & RBAC-6 Authorization Tests
- Chunk Metadata & Content Segments
- Embedded Chunk & Provenance Tests
- Document Exceptions
- Chat Message & Conversation Tests
- Chunking Config & Pipeline
- Recursive Stage Heading Logic
- Evaluation Metric Evaluators
- Auth Session Dependency
- Base Ingestion Processor
- Retrieval Exceptions
- Team API Routes
- Base Generation Service
- Query Rewriter
- Auth Login Endpoints
- Chunking Evaluation Baselines
- Reranking Pipeline Tests
- Settings & Access Dependencies
- Base LLM Provider
- Access Context Tests
- Hybrid Payload Mapper
- Sparse Embedding Encoder
- Chat API Routes
- OrgRole Enum & Base Model
- Dependency Service Wiring
- RBAC-5G Whoami Jurisdiction Tests
- Conversation Service Propagation Tests
- RBAC Foundation Tests
- Reingest Metadata Tests
- Section Matching & Chunking Tests
- Document Scope Exceptions
- OpenAI Embedder
- Document Service API
- RBAC Document Authorization Concepts
- User Profile Endpoint
- Conversation Service Message Flow
- Frontend Chat Service Client
- Frontend API Client
- Embedded Chunk Model
- AI Pipeline Response Building
- Reranking Candidate Validation
- Org Manager Jurisdiction Grant/Revoke API
- Dense Search Exceptions
- Base Storage Service
- Frontend Layout & Streaming
- Chat Not Found & Message API
- Embedding Request Execution
- Reranker Callable Interface
- Document Service Delete/Download UI
- Document API Routes
- Message API & Schemas
- Embedded Chunk Model
- Document Exceptions
- Document Not Found & Delete Service
- Base Reranker
- Cross-Encoder Reranker
- Retrieval Service Orchestrator
- Ingestion & Citation Provenance Flow
- Embedding Batcher
- AI Pipeline & Message Repository
- AccessContext Jurisdiction Concepts
- Cross-Encoder Reranker
- Filter Stage
- Password Hashing & JWT Security
- Conversation Memory Flow Concepts
- Reranking Service Tests
- Embedding Batcher
- Chunking Pipeline Contract Concepts
- Chat Not Found & Message API
- Document Access Scope Enum
- AI Pipeline & Message Repository
- Document Validator
- Chunk-Document Provenance Stamping
- Generation Exceptions
- Base Repository CRUD
- Sparse Search Exceptions
- Message Service Streaming
- Exception Handlers & Reranker Resource
- Repo Top-Level Areas
- RBAC-5J Migration & Repository Concepts
- Import Isolation Regression Test
- Embedding Request Execution
- Ingestion & Citation Provenance Flow
- API Response Schemas
- Evaluation AI Response Schemas
- Health Check Route
- Markdown Parser
- Reranking Service Public API
- Dense Search Response
- Document Validator Module
- Alembic Migration Env
- OpenAI Model Enum
- Document Not Found & Delete Service
- Grant Admin Session Wrapper
- Team API Routes
- Chunking Stage Comparison Reports
- Kalam Speech Fixture Doc
- AI Package Init
- Document Constants
- App Constants Init
- Hybrid Package Init
- Attention Mechanism Concepts
- Background Tasks Import
- Delete Route Import
- Get Route Import
- Post Route Import
- Response Import
- User Model Import
- Get Route Import
- Post Route Import
- AccessContext Reference
- Get Route Import
- AI Pipeline Reference
- Auth Service Reference
- Chat Service Reference
- Ingestion Service Reference
- Message Service Reference
- User Service Reference
- AppException Reference
- AccessContext Reference
- Org Manager Jurisdiction Exceptions
- TeamMembership Reference
- ABC Reference
- AccessContext Reference
- PointStruct Reference
- Traceable Decorator Reference
- ScoredPoint Reference
- User Model Reference
- Org Manager Jurisdiction Grant/Revoke API
- Org Manager Jurisdiction Grant/Revoke API
- AccessContext Reference
- BaseModel Reference
- Base Storage Service Reference
- Evaluation Runner Reference
- Observability Reference
- Chunking Test Spec Reference
- User Model Reference
- Docker Compose Placeholder
- Document Response Reference
- Suspected Chunks Metric
- Pre-Refactor Baseline Report
- Pre-Refactor Baseline Report
- Frozen Docling Block Snapshots
- Source Item ID Metric
- Stage 5 Frozen Tree Report
- Stage 5 Frozen Tree Report
- Stage 6 Content Segment Report
- Stage 7 Report
- Stage 7 Attention Report
- Structural Atomicity Metric
- AccessContext Reference
- Test Fixture Reference
- Frontend README
- Generation Request Reference
- Astra Study Project Name
- RetrievalService Reference
- ChatMessage Reference
- ChatSession Reference
- AccessContext Reference
- AccessContext Reference
- DenseRepository Reference
- AccessContext Reference
- UserService Reference
- AccessContext Reference
- AccessContext Reference
- RBAC-5J Parity Test Fixtures
- Qdrant Filter Evaluator (RBAC-5J Parity)
- RBAC-5J Test Fixtures
- RBAC-5J Parity Test Fixtures
- RBAC-5J Parity Test Fixtures
- RBAC-5J Parity Test Fixtures
- RBAC-5J Parity Test Fixtures
- RBAC-5J Parity Test Fixtures
- Path Reference
- UploadFile Reference
- UserCreate Schema Reference
- UserService Reference

## God Nodes (most connected - your core abstractions)
1. `DocumentChunk` - 140 edges
2. `BlockType` - 113 edges
3. `AccessContext` - 92 edges
4. `DocumentBlock` - 51 edges
5. `count_tokens()` - 43 edges
6. `make_document()` - 41 edges
7. `make_user()` - 41 edges
8. `make_user()` - 41 edges
9. `make_organisation()` - 40 edges
10. `build_access()` - 40 edges

## Surprising Connections (you probably didn't know these)
- `Transformer architecture` --semantically_similar_to--> `LangGraph`  [INFERRED] [semantically similar]
  tests/test_documents/Attention.pdf → README.md
- `A P J Abdul Kalam Departing Speech (upload 510fce33)` --semantically_similar_to--> `A P J Abdul Kalam Departing Speech`  [INFERRED] [semantically similar]
  storage/uploads/510fce33-b651-4584-ae7d-7b5677ce8472.pdf → tests/test_documents/apjspeech.pdf
- `Attention Is All You Need (upload 005042b4)` --semantically_similar_to--> `Attention Is All You Need`  [INFERRED] [semantically similar]
  storage/uploads/005042b4-01ed-4861-a6cb-18bd665703c5.pdf → tests/test_documents/Attention.pdf
- `A Comprehensive Overview of Large Language Models (upload 3c7e729d)` --semantically_similar_to--> `A Comprehensive Overview of Large Language Models`  [INFERRED] [semantically similar]
  storage/uploads/3c7e729d-ecfe-4ab9-848a-0e1812fa8460.pdf → tests/test_documents/LLM.pdf
- `Self-attention` --conceptually_related_to--> `Attention.pdf (eval corpus doc)`  [INFERRED]
  tests/test_documents/Attention.pdf → evaluation/artifacts/baseline_Attention.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **BERT deep bidirectional pre-training** — tests_test_documents_bert_masked_language_model, tests_test_documents_bert_next_sentence_prediction, tests_test_documents_bert_bidirectional_pretraining, tests_test_documents_bert_fine_tuning [EXTRACTED 0.75]
- **Offline chunking evaluation harness** — evaluation_artifacts_readme_frozen_blocks, evaluation_artifacts_comparison [EXTRACTED 0.75]
- **RAG paradigm progression** — tests_test_documents_rag_retrieval_augmented_generation, tests_test_documents_rag_naive_rag, tests_test_documents_rag_advanced_rag, tests_test_documents_rag_modular_rag [EXTRACTED 0.75]
- **Transformer built from attention components** — tests_test_documents_attention_transformer, tests_test_documents_attention_self_attention, tests_test_documents_attention_scaled_dot_product_attention, tests_test_documents_attention_multi_head_attention, tests_test_documents_attention_positional_encoding [EXTRACTED 0.75]
- **8-stage chunking pipeline contract** — claude_chunkpipeline, claude_paragraphstage, claude_metadatastage, claude_mergestage, claude_recursivestage, claude_semanticstage, claude_filterstage, claude_qualitystage, claude_finalizestage [EXTRACTED 1.00]
- **Rolling summary + recent-window conversation memory flow** — claude_aipipeline, claude_conversationsummaryservice_update_summary, claude_summarygenerator, claude_messagerepository, claude_run_summary_refresh [EXTRACTED 1.00]
- **RBAC authorization flow (AccessContext threading + retrieval + document authz)** — claude_accesscontext, claude_get_access_context, claude_denserepository, claude_documentservice, claude_documentrepository [EXTRACTED 1.00]
- **Conversation memory summarization flow** — claude_messagerepository, claude_summarygenerator, claude_conversationsummaryservice_update_summary, claude_conversation_summary_run_summary_refresh, claude_aipipeline [EXTRACTED 1.00]
- **Document authorization filter parity (Qdrant + SQL)** — claude_denserepository_authorization_filter, claude_documentrepository_get_visible, claude_accesscontext, claude_team_jurisdiction_branch, claude_team_admin_branch [EXTRACTED 1.00]
- **RBAC-5J jurisdiction grant/revoke authorization flow** — claude_orgmanagerteamservice, claude_orgmanagerteam_model, claude_orgmanagerteamrepository, claude_teamnotfounderror, claude_targetnotorgmanagererror [EXTRACTED 1.00]

## Communities (221 total, 82 thin omitted)

### Community 0 - "Document Repository Visibility"
Cohesion: 0.07
Nodes (94): DocumentRepository, Document, Session, Return one document only if ``access`` is authorized to see it -- same…, Repository for Document database operations., Update the processing status of a document., The SQL-level mirror of ``DenseRepository._authorization_filter``'s branch…, Return every document ``access`` is authorized to see: owned INDIVIDUAL… (+86 more)

### Community 1 - "Qdrant Authorization Filter Tests"
Cohesion: 0.06
Nodes (80): DenseRepository, Filter, HybridSearchResult, Create the Astra Study collection., Delete the Astra Study collection., Drop and recreate the collection. Useful during development., Delete every point belonging to one schema_version=3 document. Scoped…, Return the number of vectors stored in the collection. (+72 more)

### Community 2 - "RBAC-5J Test Fixtures"
Cohesion: 0.08
Nodes (87): Document, Filter, Organisation, parametrize, Team, TeamMembership, TeamRepository, TeamRole (+79 more)

### Community 3 - "Merge Stage Section Chunks"
Cohesion: 0.08
Nodes (82): Narrow post-split cleanup. Responsibilities ---------------- - concatenate a…, SemanticStage, count_tokens(), Count the number of tokens in text., BlockProvenance, A compact, parser-neutral reference to the source of one block., BlockType, Represents the semantic type of a document block. This enum is parser-… (+74 more)

### Community 4 - "Document Creation Test Fixtures"
Cohesion: 0.09
Nodes (77): IngestionService, Path, build_access(), db(), FakeStorageService, _ingest_and_capture_metadata(), make_document_service(), make_document_service_with_storage_spy() (+69 more)

### Community 5 - "Base Document Handler"
Cohesion: 0.07
Nodes (48): DocumentConverter, Token, Converts Markdown-It tokens into semantic DocumentBlocks. The converter itself…, Convert Markdown tokens into semantic DocumentBlocks., BaseHandler, HandlerResult, ABC, Token (+40 more)

### Community 6 - "Team Exceptions"
Cohesion: 0.07
Nodes (72): InvalidTeamNameError, Raised when a team name is already taken within the requester's organisation.…, Raised when a team name is blank/whitespace-only after trimming, or exceeds 255…, Raised when a non-ADMIN, non-MANAGER user attempts to create a team., TeamCreationForbiddenError, TeamNameAlreadyExistsError, Session, Team (+64 more)

### Community 7 - "Chunking Validation Helpers"
Cohesion: 0.07
Nodes (71): analyze(), _block_from_dict(), _block_range_valid(), _block_to_dict(), _chunk_body(), compare(), _dig(), _expected_prefix() (+63 more)

### Community 8 - "Qdrant Test Isolation & RBAC-6 Authorization Tests"
Cohesion: 0.05
Nodes (64): Insert or update points in the collection., ChunkMetadata, DenseRepository.COLLECTION_NAME, Persistence (SQLAlchemy + Qdrant + filesystem), Qdrant collection (astra_study / astra_study_test), tests/conftest.py (Qdrant test isolation guard), DenseRepository, EmbeddedChunk (+56 more)

### Community 9 - "Chunk Metadata & Content Segments"
Cohesion: 0.05
Nodes (53): ChunkMetadata, DocumentChunk, Represents one chunk that will eventually be embedded and stored in the vector…, Metadata associated with a document chunk. This metadata flows through the…, FinalizeStage, UUID, Generate a deterministic UUID for every chunk. UUIDs must satisfy: • Stable…, Final stage executed before embeddings. Responsibilities ---------------- •… (+45 more)

### Community 10 - "Embedded Chunk & Provenance Tests"
Cohesion: 0.05
Nodes (54): AIPipeline, GenerationResponse, _context(), _conversation(), _embedded(), _extract(), FakeBBox, FakeConverter (+46 more)

### Community 11 - "Document Exceptions"
Cohesion: 0.14
Nodes (63): Raised when the acting user is not the target team's own ``TeamRole.MANAGER``.…, Raised when the target user has no ``TeamMembership`` row for the given team --…, Raised when adding a user who is already a member of the team, or promoting a…, TeamMemberNotFoundError, TeamMembershipAlreadyExistsError, TeamMembershipOperationForbiddenError, Promote an existing ``TeamRole.MEMBER`` to ``TeamRole.MANAGER`` in place --…, all_memberships() (+55 more)

### Community 12 - "Chat Message & Conversation Tests"
Cohesion: 0.07
Nodes (51): ChatMessage, ChatSession, PromptBuilder, add_messages(), db(), _FakeLLM, _FakeRetrieval, FakeSummaryPipeline (+43 more)

### Community 13 - "Chunking Config & Pipeline"
Cohesion: 0.07
Nodes (37): ChunkingConfig, Single source of truth for the chunking pipeline's size limits. Every value is…, ContentSegment, One source ``DocumentBlock`` that ``MergeStage`` folded into a chunk. Internal…, True when ``inner`` names the same section as ``outer`` or a subsection nested…, section_contains(), ChunkPipeline, Executes the configured chunking stages. (+29 more)

### Community 14 - "Recursive Stage Heading Logic"
Cohesion: 0.06
Nodes (40): _is_markdown_separator(), _norm(), Compact heading context: the deepest heading normally, or the deepest two…, Recover the source segments (one per contributing block) from the merged chunk…, The text a pass-through chunk would carry with ``prefix`` present exactly once.…, A markdown table separator row, e.g. ``| --- | :--: |``., Text of each child (before the heading prefix), plus -- for the structural…, Pack whole list items into child bodies, never dividing one. A single item… (+32 more)

### Community 15 - "Evaluation Metric Evaluators"
Cohesion: 0.06
Nodes (44): answer_length(), citation_count(), exact_match(), Any, Exact answer match. Useful as a fast deterministic baseline., Records answer length. Helpful for spotting prompt regressions., Counts returned citations., FixtureManager (+36 more)

### Community 16 - "Auth Session Dependency"
Cohesion: 0.07
Nodes (41): login(), oauth2_login(), post, Authenticate a user using JSON. Used by the frontend., OAuth2-compatible login endpoint. Swagger sends: username password We interpret…, register(), get_db(), Session (+33 more)

### Community 17 - "Base Ingestion Processor"
Cohesion: 0.07
Nodes (33): BaseProcessor, ABC, Path, Extract structured information from a document., Base class for every document processor., ProcessorFactory, Path, Returns the correct processor for a document. (+25 more)

### Community 18 - "Retrieval Exceptions"
Cohesion: 0.07
Nodes (38): ContextFormattingError, EmptyQueryError, NoRetrievalResultsError, Exception, Raised when no relevant contexts could be retrieved., Base exception for retrieval failures., Raised when the retrieval pipeline is improperly configured., Raised when retrieved contexts cannot be formatted for downstream generation. (+30 more)

### Community 19 - "Team API Routes"
Cohesion: 0.08
Nodes (36): add_team_member(), create_team(), grant_org_manager_jurisdiction(), list_teams(), promote_team_member(), TeamService, Promote an existing ``TeamRole.MEMBER`` to ``TeamRole.MANAGER``. Only that…, Grant an Org Manager jurisdiction over a team. Only ``OrgRole.ADMIN`` may call… (+28 more)

### Community 20 - "Base Generation Service"
Cohesion: 0.08
Nodes (38): AIResponse, Response returned by the AI orchestration layer. This model is intentionally…, BaseGenerationService, ABC, Abstract interface for the Generation layer. Implementations are responsible…, Generate a complete response., Stream the generated response. Each yielded string represents the next chunk of…, EmptyResponseError (+30 more)

### Community 21 - "Query Rewriter"
Cohesion: 0.10
Nodes (24): QueryRewriter, Build the prompt used to rewrite the latest user message into a standalone…, Convert structured conversation messages into a readable prompt format., Responsible for rewriting conversational user queries into standalone search…, Build the prompt used to generate or update the rolling conversation summary., Responsible for building prompts used to generate and maintain a rolling…, SummaryGenerator, Build the prompt used to generate a chat title. (+16 more)

### Community 22 - "Auth Login Endpoints"
Cohesion: 0.07
Nodes (31): OrgManagerTeam, SQLAlchemy model representing an ``OrgRole.MANAGER``'s jurisdiction over a…, OrgManagerTeamRepository, Grant ``user_id`` jurisdiction over ``team_id``. Raises…, Repository for OrgManagerTeam (RBAC-5J jurisdiction) database operations.…, Revoke ``user_id``'s jurisdiction over ``team_id``. Raises…, Return the jurisdiction row for one (Org Manager, team) pair, if any -- the…, Return the ids of every team the given user holds jurisdiction over -- the… (+23 more)

### Community 23 - "Chunking Evaluation Baselines"
Cohesion: 0.05
Nodes (44): baseline_apjspeech.txt (commit 888fc8c report), baseline_Attention.txt (commit 888fc8c report), baseline_LLM.txt (commit 888fc8c report), comparison.txt (baseline vs stage14 deltas), comparison_stage5_to_stage6.txt (Stage 6 primary comparison), apjspeech.pdf (eval corpus doc), Attention.pdf (eval corpus doc), LLM.pdf (eval corpus doc) (+36 more)

### Community 24 - "Reranking Pipeline Tests"
Cohesion: 0.07
Nodes (41): get_hybrid_service(), get_reranking_service(), get_retrieval_service(), FixtureManager, HybridService, LangSmithProvider, RerankingService, print_results() (+33 more)

### Community 25 - "Settings & Access Dependencies"
Cohesion: 0.12
Nodes (18): ABC, Application settings loaded from environment variables., Settings, OrgRole, Enum, str, A user's organisation-scoped role. Distinct from document access scope -- role…, Domain models for the reranking subsystem. These models represent the output of… (+10 more)

### Community 26 - "Base LLM Provider"
Cohesion: 0.07
Nodes (23): BaseLLMProvider, ABC, Generate a complete response from the language model., Stream a response from the language model., Base interface for all LLM providers., get_openai_client(), Create and return an OpenAI client. The client is configured using application…, OpenAIProvider (+15 more)

### Community 27 - "Access Context Tests"
Cohesion: 0.11
Nodes (39): get_access_context(), Session, User, Build the request-scoped authorization identity. Every field is derived…, db(), make_jurisdiction(), make_membership(), make_organisation() (+31 more)

### Community 28 - "Hybrid Payload Mapper"
Cohesion: 0.09
Nodes (26): HybridMapper, EmbeddedChunk, HybridSearchResult, PointStruct, Combine dense and sparse representations into a single hybrid Qdrant point., Converts Astra Study domain models into hybrid Qdrant PointStruct objects.…, Convert dense and sparse chunk collections into hybrid PointStructs. Both lists…, Convert a Qdrant ScoredPoint into a HybridSearchResult. (+18 more)

### Community 29 - "Sparse Embedding Encoder"
Cohesion: 0.09
Nodes (17): traceable, Generate sparse embedding for a user query., Generates sparse embeddings for document chunks using FastEmbed.…, Generate sparse embeddings for document chunks., SparseEncoder, Represents a sparse vector generated by the sparse encoder. Unlike dense…, Number of non-zero dimensions., Represents a document chunk together with its sparse vector. (+9 more)

### Community 30 - "Chat API Routes"
Cohesion: 0.10
Nodes (26): create_chat(), delete_chat(), get_chat(), list_chats(), delete, get, post, Response (+18 more)

### Community 31 - "OrgRole Enum & Base Model"
Cohesion: 0.12
Nodes (21): Enum, str, A user's role within a single team membership. Independent of ``OrgRole``: a…, TeamRole, Document, Base, TimestampMixin, Represents an uploaded document. (+13 more)

### Community 32 - "Dependency Service Wiring"
Cohesion: 0.16
Nodes (31): build_conversation_summary_service(), get_ai_pipeline(), get_auth_service(), get_chat_service(), get_conversation_service(), get_conversation_summary_service(), get_document_service(), get_generation_service() (+23 more)

### Community 33 - "RBAC-5G Whoami Jurisdiction Tests"
Cohesion: 0.18
Nodes (30): db(), make_jurisdiction(), make_membership(), make_organisation(), make_team(), make_user(), make_user_service(), fixture (+22 more)

### Community 34 - "Conversation Service Propagation Tests"
Cohesion: 0.10
Nodes (27): ConversationService, _individual_branch_user_id(), make_conversation_service(), make_dense_repository_with_fake_client(), _persisted(), Filter, parametrize, Executable specification for RBAC-5B: threading the trusted AccessContext… (+19 more)

### Community 35 - "RBAC Foundation Tests"
Cohesion: 0.15
Nodes (25): db(), make_document(), make_organisation(), make_team(), make_upload_file(), make_user(), Document, fixture (+17 more)

### Community 36 - "Reingest Metadata Tests"
Cohesion: 0.16
Nodes (23): main(), SimpleNamespace, db(), _FakeChunkPipeline, _FakeProcessor, make_document(), make_organisation(), make_user() (+15 more)

### Community 37 - "Section Matching & Chunking Tests"
Cohesion: 0.17
Nodes (28): _body(), _chunk(), _heading(), _merge(), _mk(), _prov(), Run the first real stages that shape section chunks: Metadata -> Merge. Input…, _run_metadata() (+20 more)

### Community 38 - "Document Scope Exceptions"
Cohesion: 0.10
Nodes (25): DocumentTooLargeError, EmptyDocumentError, InvalidAccessScopeError, InvalidDocumentTypeError, OrganisationScopeForbiddenError, Raised when an empty document is uploaded., Raised when a document exceeds the allowed size., Raised for a malformed or self-contradictory scope/team_id combination on… (+17 more)

### Community 39 - "OpenAI Embedder"
Cohesion: 0.14
Nodes (14): EmbeddingBatcher, Splits document chunks into batches suitable for the embedding provider. The…, Convenience wrapper allowing the batcher to be called directly., EmbeddingPipeline, Production embedding pipeline. Pipeline DocumentChunks │ ▼ EmbeddingBatcher │ ▼…, Execute the complete embedding pipeline., Convenience wrapper. Allows pipeline(chunks) instead of pipeline.run(chunks), PDFProcessor (+6 more)

### Community 40 - "Document Service API"
Cohesion: 0.12
Nodes (19): BinaryIO, Retrieve metadata for a single document., Upload one or more documents., Document, Create an authenticated API client., _client(), _document_service(), _normalize_heading_path() (+11 more)

### Community 41 - "RBAC Document Authorization Concepts"
Cohesion: 0.11
Nodes (26): Authorization (RBAC), DocumentAccessScope enum (app/enums/document.py), DocumentService, DocumentService._can_create, DocumentService._can_delete, InvalidAccessScopeError, Last-manager invariant (DELETE-embedded correlated subquery), OrganisationScopeForbiddenError (+18 more)

### Community 42 - "User Profile Endpoint"
Cohesion: 0.12
Nodes (13): get_current_user_profile(), get, UserService, Return the currently authenticated user's profile, including their organisation…, AuthService, ApiClient, Fetch the richer RBAC profile (organisation_id, role, team memberships) for the…, TokenResponse (+5 more)

### Community 43 - "Conversation Service Message Flow"
Cohesion: 0.13
Nodes (18): ConversationService, BackgroundTasks, ChatMessage, ChatSession, ConversationResponse, MessageCreate, MessageService, StreamEvent (+10 more)

### Community 44 - "Frontend Chat Service Client"
Cohesion: 0.17
Nodes (13): ChatService, Chat, Citation, _active_chat(), _client(), Refresh the sidebar chat list., Return the selected chat., Render workspace heading. (+5 more)

### Community 45 - "Frontend API Client"
Cohesion: 0.14
Nodes (10): ApiClient, ApiException, Any, Exception, Response, Download binary data., Open a Server-Sent Events POST request., Base HTTP client used by all frontend services. (+2 more)

### Community 46 - "Embedded Chunk Model"
Cohesion: 0.13
Nodes (10): DenseMapper, ScoredPoint, Converts between Astra Study domain models and Qdrant models. Responsibilities…, Convert a Qdrant ScoredPoint into a DenseSearchResult., Convert multiple ScoredPoints into DenseSearchResults., DenseSearchResult, Represents one result returned from the dense vector search., DensePipeline (+2 more)

### Community 47 - "AI Pipeline Response Building"
Cohesion: 0.17
Nodes (15): AIResponse, AIPipeline, ChatMessage, StreamEvent, traceable, Stream an assistant response using Retrieval-Augmented Generation., Generate a short AI title for a new conversation., Generate or update the conversation summary. (+7 more)

### Community 48 - "Reranking Candidate Validation"
Cohesion: 0.15
Nodes (15): Cross Encoder based reranker implementation. This module implements the…, CandidateFormatError, EmptyCandidateError, InvalidQueryError, InvalidTopKError, ModelLoadError, PredictionError, Exception (+7 more)

### Community 49 - "Org Manager Jurisdiction Grant/Revoke API"
Cohesion: 0.15
Nodes (16): Remove a user's membership from a team entirely, regardless of its current…, Revoke an Org Manager's jurisdiction over a team. Only ``OrgRole.ADMIN`` may…, remove_team_member(), revoke_org_manager_jurisdiction(), OrgManagerTeamService, AccessContext, Confirm the acting user is ``OrgRole.ADMIN``. Runs first, before any database…, Confirm ``team_id`` exists in the ADMIN's own organisation. Nonexistent team… (+8 more)

### Community 50 - "Dense Search Exceptions"
Cohesion: 0.13
Nodes (21): CollectionAlreadyExistsError, CollectionCreationError, CollectionDeletionError, CollectionNotFoundError, DenseSearchConfigurationError, DenseSearchError, InvalidPayloadError, InvalidSearchQueryError (+13 more)

### Community 51 - "Base Storage Service"
Cohesion: 0.12
Nodes (13): BaseStorageService, ABC, Path, UploadFile, Save a file and return: ( stored_filename, file_size, ), Delete a stored file., Return the absolute path of a stored file., Base interface for all storage providers. (+5 more)

### Community 52 - "Frontend Layout & Streaming"
Cohesion: 0.13
Nodes (19): ChatService, AuthService.get_current_user_profile, frontend/app.py (3-column layout), frontend/models/user.py::User, frontend/models/user.py User dataclass, Streaming protocol (SSE), TeamMembershipResponse, UserProfileResponse (app/schemas/user.py) (+11 more)

### Community 53 - "Chat Not Found & Message API"
Cohesion: 0.16
Nodes (14): Base, Base class for all SQLAlchemy ORM models., ChatNotFoundError, Raised when the requested chat session does not exist or is inaccessible., ChatSession, Represents a chat session belonging to a user., ChatMessage, Represents a single message within a chat session. (+6 more)

### Community 54 - "Embedding Request Execution"
Cohesion: 0.14
Nodes (14): OpenAIEmbedder, traceable, Execute one embedding request. Retries automatically for transient OpenAI…, Embed a single batch of document chunks. Parameters ---------- chunks A batch…, Embed multiple batches. Parameters ---------- batches List of EmbeddingBatch…, Convenience wrapper. Allows embedder(batches) instead of embedder.embed(batches), Generate an embedding for a user query., Generates OpenAI embeddings for DocumentChunks. Responsibilities… (+6 more)

### Community 55 - "Reranker Callable Interface"
Cohesion: 0.11
Nodes (12): Allows the reranker instance to be invoked like a function. Example -------…, Rerank retrieved candidates. Parameters ---------- query: User query.…, slice, SupportsIndex, Returns the top-k reranked chunks. Parameters ---------- k: Number of chunks to…, Represents a single reranked retrieval result. Attributes ---------- result:…, Represents the complete output of the reranking stage. Attributes ----------…, Returns the highest ranked chunk. (+4 more)

### Community 56 - "Document Service Delete/Download UI"
Cohesion: 0.16
Nodes (17): DocumentService, Service responsible for all document-related operations., Download the original uploaded document., _client(), _create_chat(), _load_chat(), Refresh chats and documents., Load a chat and its messages. (+9 more)

### Community 57 - "Document API Routes"
Cohesion: 0.17
Nodes (19): delete_document(), download_document(), get_document(), get_documents(), AccessContext, DocumentResponse, IngestionService, UploadFile (+11 more)

### Community 58 - "Message API & Schemas"
Cohesion: 0.11
Nodes (18): create_message(), get_messages(), BackgroundTasks, ConversationResponse, MessageCreate, MessageService, Retrieve all messages for a chat session., Send a message and receive the assistant response. (+10 more)

### Community 59 - "Embedded Chunk Model"
Cohesion: 0.12
Nodes (12): EmbeddedChunk, UUID, Returns the chunk text., Returns the embedding dimensions., Returns the UUIDs of all chunks contained in the batch., Represents a chunk together with its embedding. This object is produced by the…, Returns the chunk UUID., Returns the document UUID. (+4 more)

### Community 60 - "Document Exceptions"
Cohesion: 0.13
Nodes (12): LastTeamManagerError, Raised when removing a ``TeamRole.MANAGER`` would leave the team with zero…, Session, Count a team's current ``TeamRole.MANAGER`` memberships. ``exclude_user_id``…, Add ``user_id`` to ``team_id`` as a plain ``TeamRole.MEMBER``. Raises…, Repository for TeamMembership database operations., Remove a ``(user_id, team_id)`` membership entirely, regardless of its current…, Return the ids of every team the given user is a member of. Selects only the… (+4 more)

### Community 61 - "Document Not Found & Delete Service"
Cohesion: 0.13
Nodes (13): DocumentNotFoundError, Raised when a requested document does not exist or does not belong to the…, AccessContext, Document, DocumentResponse, Path, UploadFile, Retrieve every document ``access`` is authorized to see: owned INDIVIDUAL… (+5 more)

### Community 62 - "Base Reranker"
Cohesion: 0.12
Nodes (11): BaseReranker, ABC, Abstract interface for all rerankers. Every reranker implementation…, Abstract base class for reranking implementations., Returns the underlying reranker model name., Returns the execution device. Example ------- cpu cuda cuda:0 mps, Batch size used for inference., Maximum sequence length accepted by the reranker. (+3 more)

### Community 63 - "Cross-Encoder Reranker"
Cohesion: 0.12
Nodes (11): CrossEncoderReranker, Automatically determine the best available inference device. Priority --------…, Name of the underlying HuggingFace model., Device used for inference., Batch size used during inference., Maximum sequence length accepted by the model., Returns the loaded CrossEncoder instance. This property is primarily useful for…, Cross Encoder implementation of the reranker. The model scores every (query,… (+3 more)

### Community 64 - "Retrieval Service Orchestrator"
Cohesion: 0.15
Nodes (13): RetrievalResult, traceable, Execute the complete retrieval pipeline. Steps ----- 1. Validate query 2.…, Production Retrieval Orchestrator. Pipeline -------- User Query │ ▼ Hybrid…, Callable wrapper. Allows RetrievalService to be invoked like a function while…, Convert reranked search results into RetrievedContext objects consumed by…, RetrievalService, HybridService (+5 more)

### Community 65 - "Ingestion & Citation Provenance Flow"
Cohesion: 0.12
Nodes (19): answer_support scoring term, app/ingestion/factory.py::ProcessorFactory, app/ingestion/processors/docling.py (DoclingProcessor), BlockProvenance, Citation model (app/generation/models.py), Citations (single source of truth), Deterministic citation ranking rationale (no LLM), DoclingProcessor (app/ingestion/processors/docling.py) (+11 more)

### Community 66 - "Embedding Batcher"
Cohesion: 0.16
Nodes (14): Convert raw vectors returned by OpenAI into EmbeddedChunk objects., EmbeddingValidationError, Raised when an embedding fails validation. Examples: - Empty embedding -…, EmbeddingMetadata, EmbeddingVector, Represents a dense embedding vector generated by an embedding model. The vector…, Returns the embedding dimension., Metadata describing how an embedding was generated. Document metadata is… (+6 more)

### Community 67 - "AI Pipeline & Message Repository"
Cohesion: 0.12
Nodes (11): MessageRepository, datetime, Session, Count the user + assistant messages created at or before ``timestamp``.…, Retrieve the most recent messages from a chat session. Returned in…, Repository for ChatMessage database operations., Retrieve all messages belonging to a chat session. Messages are returned in…, Retrieve the user + assistant messages of a chat session in order. This is the… (+3 more)

### Community 68 - "AccessContext Jurisdiction Concepts"
Cohesion: 0.16
Nodes (18): AccessContext (app/retrieval/access.py), AccessContext.jurisdiction_team_ids, app/dependencies/access.py::get_access_context, app/dependencies/auth.py::get_current_user, DenseRepository._authorization_filter, Request/DI layering (backend), DocumentRepository, DocumentRepository.get_visible / get_by_id_visible / _visibility_conditions (+10 more)

### Community 69 - "Cross-Encoder Reranker"
Cohesion: 0.14
Nodes (11): Validate the user query before inference., Validate the requested top_k value., Validate retrieval candidates before reranking., Convert retrieved candidates into CrossEncoder inputs. Each candidate becomes a…, Combine retrieval results with reranker scores and sort them in descending…, Rerank retrieved candidates using the Cross Encoder. Parameters ----------…, HybridSearchResponse, HybridSearchResult (+3 more)

### Community 70 - "Filter Stage"
Cohesion: 0.25
Nodes (13): is_copyright(), is_doi(), is_empty(), is_isbn(), is_numeric_only(), is_page_number(), is_punctuation_only(), is_short_noise() (+5 more)

### Community 71 - "Password Hashing & JWT Security"
Cohesion: 0.16
Nodes (9): Any, Handles password hashing, password verification, and JWT token generation., Decode and validate a JWT., Hash a plain-text password., Verify a password against its hash., Create an access token., Create a refresh token., SecurityManager (+1 more)

### Community 72 - "Conversation Memory Flow Concepts"
Cohesion: 0.17
Nodes (16): AIPipeline (app/ai/pipeline.py), tests/conftest.py (Qdrant isolation guard), Conversation memory (rolling summary + recent window), Conversation memory (rolling summary + recent window) design, conversation_summary.run_summary_refresh, ConversationService (app/services/conversation.py), ConversationSummaryService.update_summary, DenseRepository (+8 more)

### Community 73 - "Reranking Service Tests"
Cohesion: 0.23
Nodes (15): RerankingResult, make_hybrid_result(), make_reranking_result(), make_service(), HybridSearchResult, RetrievalService, Graceful empty retrieval (commit b5d8d4b): when every candidate is filtered out…, The other half of graceful empty retrieval: no hybrid candidates at all short-… (+7 more)

### Community 74 - "Embedding Batcher"
Cohesion: 0.22
Nodes (9): Split chunks into embedding batches., EmbeddingBatchError, Custom exceptions for the embeddings module., Raised when an embedding batch is invalid. Examples: - Empty batch - Batch…, EmbeddingBatch, Represents a batch of chunks sent in a single embedding request., Returns the number of chunks in the batch., Validate an embedding batch before sending it to the embedding provider. (+1 more)

### Community 75 - "Chunking Pipeline Contract Concepts"
Cohesion: 0.24
Nodes (15): Chunking pipeline contract, ChunkingConfig (app/chunking/config.py), ChunkPipeline (app/chunking/pipeline.py), ContentSegment, evaluation/chunking_report.py (offline structural evaluator), FilterStage, FinalizeStage, Chunking pipeline contract (frozen) (+7 more)

### Community 76 - "Chat Not Found & Message API"
Cohesion: 0.23
Nodes (9): ConversationResponse, BaseModel, Response returned after sending a message. Contains both the persisted user…, MessageCreate, MessageResponse, BaseModel, Response schema representing a chat message., Request schema for sending a user message. (+1 more)

### Community 77 - "Document Access Scope Enum"
Cohesion: 0.23
Nodes (9): DocumentAccessScope, DocumentStatus, Enum, str, Who can retrieve/query a document. Separate from ``OrgRole`` / ``TeamRole`` --…, Processing state of a document., DocumentResponse, BaseModel (+1 more)

### Community 78 - "AI Pipeline & Message Repository"
Cohesion: 0.16
Nodes (9): ChatRepository, Session, Repository for ChatSession database operations., Return all chat sessions belonging to a user., ConversationSummaryService, traceable, Maintains a rolling AI-generated summary for long conversations. Lifecycle…, How many conversational messages the stored summary already reflects. (+1 more)

### Community 79 - "Document Validator"
Cohesion: 0.20
Nodes (9): DocumentValidator, Validates document-level metadata., Any, One metric produced by a validator., Output returned by every validator. Every validator returns exactly one…, Represents a non-fatal validation issue., ValidationMetric, ValidationResult (+1 more)

### Community 80 - "Chunk-Document Provenance Stamping"
Cohesion: 0.31
Nodes (14): DocumentChunk, Document, Stamp every chunk's metadata from the one authoritative Document row.…, _stamp_rbac_fields(), _embedded(), make_document_like(), ChunkMetadata, DocumentAccessScope (+6 more)

### Community 81 - "Generation Exceptions"
Cohesion: 0.21
Nodes (12): EmptyPromptError, GenerationError, GenerationTimeoutError, InvalidGenerationResponseError, Exception, Exceptions raised by the Generation module., Raised when prompt generation results in no messages., Raised when the configured LLM times out. (+4 more)

### Community 82 - "Base Repository CRUD"
Cohesion: 0.23
Nodes (7): BaseRepository, Session, Base repository providing common CRUD operations., Persist a new entity., Retrieve an entity by its primary key., Persist changes made to an existing entity., ModelType

### Community 83 - "Sparse Search Exceptions"
Cohesion: 0.23
Nodes (11): Exception, Raised when the sparse encoder configuration is invalid., Base exception for all sparse search errors., Raised when a sparse vector collection operation fails., Raised when sparse retrieval fails., Raised when sparse embeddings cannot be generated., SparseCollectionError, SparseConfigurationError (+3 more)

### Community 84 - "Message Service Streaming"
Cohesion: 0.35
Nodes (4): MessageService, Yield assistant text chunks from the message SSE endpoint., Conversation, Message

### Community 85 - "Exception Handlers & Reranker Resource"
Cohesion: 0.25
Nodes (9): get_reranking_resource(), Return the shared reranking service. The underlying CrossEncoder model is…, FastAPI, Register all application exception handlers., register_exception_handlers(), lifespan(), FastAPI, get (+1 more)

### Community 86 - "Repo Top-Level Areas"
Cohesion: 0.22
Nodes (10): alembic/ migrations, app/ (FastAPI backend), Astra Study, evaluation/ harness, frontend/ (Streamlit UI), scripts/ (operational one-offs), grant_admin(), main() (+2 more)

### Community 87 - "RBAC-5J Migration & Repository Concepts"
Cohesion: 0.18
Nodes (11): Document model (app/models/document.py), ManagedTeamResponse (RBAC-5J), alembic migration 116ced32c143 (RBAC org/team foundation), Organisation model (app/models/organisation.py), OrgManagerTeamRepository, OrgManagerTeamRepository.grant, OrgManagerTeamRepository.revoke, alembic 116ced32c143_rbac_organisation_team_foundation (+3 more)

### Community 88 - "Import Isolation Regression Test"
Cohesion: 0.24
Nodes (9): CompletedProcess, parametrize, Regression test for a circular import discovered during the RBAC-5B independent…, Reproduces the exact import order used by ``scripts/reingest_document.py``…, Run ``code`` in a brand-new Python process with no inherited ``sys.modules``…, Each of these must be importable as the very first thing a fresh process does…, _run_in_fresh_process(), test_reingest_document_script_import_sequence_succeeds_in_fresh_process() (+1 more)

### Community 89 - "Embedding Request Execution"
Cohesion: 0.22
Nodes (9): EmbeddingCacheError, EmbeddingError, EmbeddingRateLimitError, EmbeddingTimeoutError, Exception, Raised when the embedding cache encounters an error., Raised when the embedding provider rate limits requests., Raised when an embedding request times out. (+1 more)

### Community 90 - "Ingestion & Citation Provenance Flow"
Cohesion: 0.25
Nodes (8): DenseRepository.delete_by_document_id, HybridMapper.build_payload (app/search/hybrid/mapper.py), HybridMapper.build_payload, HybridPipeline.index (app/search/hybrid/pipeline.py), Qdrant vector store, app/search/{dense,hybrid}/mapper.py, Re-run one document through the production ingestion path. Document.id (SQLite)…, _summarise()

### Community 91 - "API Response Schemas"
Cohesion: 0.36
Nodes (6): success_response(), ApiResponse, ErrorResponse, BaseModel, Standard error API response., Standard success API response.

### Community 92 - "Evaluation AI Response Schemas"
Cohesion: 0.25
Nodes (6): EvaluationPredictor, AccessContext, AIPipeline, Executes Astra Study's production AI pipeline for LangSmith evaluation. This…, ``access`` is resolved once from the real database-backed User/TeamMembership…, Executes the production AI pipeline for a single evaluation example.

### Community 93 - "Health Check Route"
Cohesion: 0.38
Nodes (5): health_check(), get, HealthResponse, BaseModel, Response model for the health check endpoint.

### Community 94 - "Markdown Parser"
Cohesion: 0.29
Nodes (4): DocumentParser, Token, Parse Markdown into tokens., Parses Markdown into Markdown-It tokens. This class is intentionally…

### Community 95 - "Reranking Service Public API"
Cohesion: 0.40
Nodes (4): traceable, Callable wrapper. Example ------- >>> result = service( ... query=query, ...…, Public service for document reranking. The service hides the concrete reranker…, RerankingService

### Community 96 - "Dense Search Response"
Cohesion: 0.33
Nodes (4): DenseSearchResponse, Represents the complete response returned from the dense search pipeline., Number of retrieved results., Highest similarity score.

### Community 97 - "Document Validator Module"
Cohesion: 0.33
Nodes (4): DocumentValidator, UploadFile, Validates uploaded documents before they are stored on disk., Validate an uploaded document. Raises ------ HTTPException If validation fails.

### Community 98 - "Alembic Migration Env"
Cohesion: 0.40
Nodes (4): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online()

### Community 99 - "OpenAI Model Enum"
Cohesion: 0.50
Nodes (4): OpenAIModel, Enum, str, Supported OpenAI chat models.

### Community 100 - "Document Not Found & Delete Service"
Cohesion: 0.40
Nodes (4): BaseStorageService, DenseRepository, DocumentRepository, TeamMembershipRepository

### Community 102 - "Team API Routes"
Cohesion: 0.50
Nodes (3): TeamMembershipRepository, TeamRepository, UserRepository

### Community 111 - "Kalam Speech Fixture Doc"
Cohesion: 1.00
Nodes (3): A P J Abdul Kalam Departing Speech (upload 510fce33), A P J Abdul Kalam Departing Speech, Developed India 2020

## Ambiguous Edges - Review These
- `tests/conftest.py (Qdrant isolation guard)` → `ConversationSummaryService.update_summary`  [AMBIGUOUS]
  CLAUDE.md · relation: semantically_similar_to

## Knowledge Gaps
- **62 isolated node(s):** `astra-study`, `prompt_builder (app/generation/prompt_builder.py)`, `stage6_LLM.txt (Stage 6 ContentSegment report)`, `stage7_LLM.txt (Stage 7 report)`, `Multi-head attention` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1191 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **82 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `tests/conftest.py (Qdrant isolation guard)` and `ConversationSummaryService.update_summary`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `AccessContext` connect `Settings & Access Dependencies` to `Document Repository Visibility`, `Qdrant Authorization Filter Tests`, `Document Creation Test Fixtures`, `Team Exceptions`, `Embedded Chunk & Provenance Tests`, `Document Exceptions`, `Chat Message & Conversation Tests`, `Evaluation Metric Evaluators`, `Auth Session Dependency`, `Team API Routes`, `Query Rewriter`, `Reranking Pipeline Tests`, `Access Context Tests`, `Conversation Service Propagation Tests`, `RBAC Foundation Tests`, `Conversation Service Message Flow`, `AI Pipeline Response Building`, `Org Manager Jurisdiction Grant/Revoke API`, `Message API & Schemas`, `Retrieval Service Orchestrator`, `Reranking Service Tests`, `Chat Not Found & Message API`, `Document Access Scope Enum`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `get_current_user_profile()` connect `User Profile Endpoint` to `Auth Login Endpoints`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `DocumentChunk` (e.g. with `ChunkPipeline` and `BaseChunkStage`) actually correct?**
  _`DocumentChunk` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 88 inferred relationships involving `BlockType` (e.g. with `FilterStage` and `MergeStage`) actually correct?**
  _`BlockType` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `AccessContext` (e.g. with `AIPipeline` and `create_message()`) actually correct?**
  _`AccessContext` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `DocumentBlock` (e.g. with `DocumentConverter` and `HandlerResult`) actually correct?**
  _`DocumentBlock` has 16 INFERRED edges - model-reasoned connections that need verification._