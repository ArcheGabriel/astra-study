# Graph Report - Astra-Study  (2026-09-27)

## Corpus Check
- 37 files · ~257,946 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3224 nodes · 8180 edges · 238 communities (120 shown, 82 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 614 edges (avg confidence: 0.94)
- Token cost: 0 input · 107,123 output

## Community Hubs (Navigation)
- Document Repository Visibility
- Document Exceptions
- Team Exceptions
- Document Creation Test Fixtures
- Chunk Metadata & Content Segments
- Chunking Config & Pipeline
- Embedded Chunk & Provenance Tests
- Recursive Stage Heading Logic
- Evaluation Metric Evaluators
- Qdrant Authorization Filter Tests
- Retrieval Exceptions
- Team API Routes
- Base Document Handler
- Auth Login Endpoints
- Chunking Evaluation Baselines
- Base Ingestion Processor
- Query Rewriter
- Chunking Validation Helpers
- RBAC-5J Test Fixtures
- Org Manager Jurisdiction Exceptions
- Dense Repository Collection Ops
- Base LLM Provider
- Auth Session Dependency
- Section Matching & Chunking Tests
- OrgRole Enum & Base Model
- Chat Message & Conversation Tests
- Merge Stage Section Chunks
- Chat Not Found & Message API
- Chunking Report Analyzer
- Chat API Routes
- Access Context Tests
- Block Type & Token Counting
- RBAC-5G Whoami Jurisdiction Tests
- RBAC-5J Parity Test Fixtures
- Base Generation Service
- Base Reranker
- Conversation Service Propagation Tests
- Org Manager Jurisdiction Grant/Revoke API
- Reingest Metadata Tests
- RBAC Foundation Tests
- AI Pipeline & Message Repository
- Cross-Encoder Reranker
- Embedded Chunk Model
- Document Not Found & Delete Service
- Document Service API
- RBAC Document Authorization Concepts
- User Profile Endpoint
- Dependency Service Wiring
- Embedding Batcher
- Sparse Embedding Encoder
- Conversation Service Message Flow
- Frontend Chat Service Client
- Frontend API Client
- OpenAI Embedder
- Reranking Candidate Validation
- Reranking Pipeline Tests
- Filter Stage
- Retrieval Service Orchestrator
- Dense Search Exceptions
- Base Storage Service
- Frontend Layout & Streaming
- AI Pipeline Response Building
- Embedding Request Execution
- Reranker Callable Interface
- Qdrant Test Isolation Conftest
- Document Service Delete/Download UI
- Alembic Migration Env
- Document API Routes
- Settings & Access Dependencies
- Ingestion & Citation Provenance Flow
- Semantic Stage Merge
- Retrieval/Hybrid/Reranking DI Wiring
- AccessContext Jurisdiction Concepts
- Caption Handler
- Citation Model & Scoring
- Password Hashing & JWT Security
- Hybrid Payload Mapper
- Conversation Memory Flow Concepts
- Prompt Builder & Fakes
- Reranking Service Tests
- Generation Exceptions
- Chunking Pipeline Contract Concepts
- AI Pipeline DI Wiring
- Markdown Token Converter
- Document Access Scope Enum
- Base Repository CRUD
- Document Validator
- Chunk-Document Provenance Stamping
- Evaluation AI Response Schemas
- Dense Pipeline Collection Ops
- Sparse Search Exceptions
- Message Service Streaming
- Base Retrieval Service
- Exception Handlers & Reranker Resource
- Document Scope Exceptions
- Hybrid Pipeline Ops
- Repo Top-Level Areas
- RBAC-5J Migration & Repository Concepts
- Base App Exceptions
- Reranking Service Public API
- Sparse Pipeline Ops
- Import Isolation Regression Test
- OpenAI Client Factory
- Message API & Schemas
- API Response Schemas
- Citation Ranking Rationale
- Health Check Route
- Markdown Parser
- Chunk UUID Helpers
- Hybrid Point Conversion
- Embedding Vector Model
- Dense Search Response
- Hybrid Search Result Conversion
- Document Validator Module
- Fake Generation Test Double
- OpenAI Model Enum
- Document Block Handler Interface
- TeamRole Enum
- Grant Admin Session Wrapper
- Qdrant Filter Evaluator (RBAC-5J Parity)
- Message Service Retrieval
- Embedder Callable Interface
- Embedding Pipeline Callable
- Fake Summary Pipeline
- Team/User Repository Init
- Chunking Stage Comparison Reports
- Kalam Speech Fixture Doc
- Streaming AI Pipeline Test Double
- AI Package Init
- Document Constants
- App Constants Init
- Hybrid Package Init
- Attention Mechanism Concepts
- DB Fixture
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
- TeamMembership Reference
- ABC Reference
- AccessContext Reference
- PointStruct Reference
- Traceable Decorator Reference
- ScoredPoint Reference
- User Model Reference
- AccessContext Reference
- BaseModel Reference
- Base Storage Service Reference
- Chunk Metadata Reference
- Evaluation Runner Reference
- Observability Reference
- Chunking Test Spec Reference
- User Model Reference
- Docker Compose Placeholder
- Document Model Reference
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
- TeamRole Reference
- ChatMessage Reference
- ChatSession Reference
- AccessContext Reference
- AccessContext Reference
- DenseRepository Reference
- AccessContext Reference
- UserService Reference
- AccessContext Reference
- AccessContext Reference
- Path Reference
- UploadFile Reference
- UserCreate Schema Reference
- UserRepository Reference
- UserService Reference

## God Nodes (most connected - your core abstractions)
1. `DocumentChunk` - 140 edges
2. `BlockType` - 113 edges
3. `AccessContext` - 103 edges
4. `DocumentBlock` - 51 edges
5. `count_tokens()` - 43 edges
6. `OrgManagerTeamRepository` - 42 edges
7. `make_user()` - 41 edges
8. `make_document()` - 41 edges
9. `make_user()` - 41 edges
10. `make_organisation()` - 40 edges

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
- **Document authorization filter parity (Qdrant + SQL)** — claude_denserepository_authorization_filter, claude_documentrepository_get_visible, claude_accesscontext, claude_team_jurisdiction_branch, claude_team_admin_branch [EXTRACTED 1.00]
- **RBAC-5J jurisdiction grant/revoke authorization flow** — claude_orgmanagerteamservice, claude_orgmanagerteam_model, claude_orgmanagerteamrepository, claude_teamnotfounderror, claude_targetnotorgmanagererror [EXTRACTED 1.00]
- **Conversation memory summarization flow** — claude_messagerepository, claude_summarygenerator, claude_conversationsummaryservice_update_summary, claude_conversation_summary_run_summary_refresh, claude_aipipeline [EXTRACTED 1.00]

## Communities (238 total, 82 thin omitted)

### Community 0 - "Document Repository Visibility"
Cohesion: 0.07
Nodes (94): DocumentRepository, Document, Session, Return one document only if ``access`` is authorized to see it -- same…, Repository for Document database operations., Update the processing status of a document., The SQL-level mirror of ``DenseRepository._authorization_filter``'s branch…, Return every document ``access`` is authorized to see: owned INDIVIDUAL… (+86 more)

### Community 1 - "Document Exceptions"
Cohesion: 0.08
Nodes (82): DocumentTooLargeError, EmptyDocumentError, InvalidDocumentTypeError, Raised when an empty document is uploaded., Raised when a document exceeds the allowed size., Raised when an unsupported file type is uploaded., LastTeamManagerError, Raised when the acting user is not the target team's own ``TeamRole.MANAGER``.… (+74 more)

### Community 2 - "Team Exceptions"
Cohesion: 0.06
Nodes (74): InvalidTeamNameError, Raised when a team name is already taken within the requester's organisation.…, Raised when a team name is blank/whitespace-only after trimming, or exceeds 255…, Raised when a non-ADMIN, non-MANAGER user attempts to create a team., TeamCreationForbiddenError, TeamNameAlreadyExistsError, Session, Team (+66 more)

### Community 3 - "Document Creation Test Fixtures"
Cohesion: 0.09
Nodes (76): Path, build_access(), db(), FakeStorageService, _ingest_and_capture_metadata(), make_document_service(), make_document_service_with_storage_spy(), make_membership() (+68 more)

### Community 4 - "Chunk Metadata & Content Segments"
Cohesion: 0.05
Nodes (58): ChunkMetadata, ContentSegment, DocumentChunk, One source ``DocumentBlock`` that ``MergeStage`` folded into a chunk. Internal…, Represents one chunk that will eventually be embedded and stored in the vector…, Metadata associated with a document chunk. This metadata flows through the…, FinalizeStage, UUID (+50 more)

### Community 5 - "Chunking Config & Pipeline"
Cohesion: 0.07
Nodes (35): ChunkingConfig, Single source of truth for the chunking pipeline's size limits. Every value is…, ChunkPipeline, Executes the configured chunking stages., BaseChunkStage, ABC, Process the incoming data and return chunks., Base interface for every chunking stage. (+27 more)

### Community 6 - "Embedded Chunk & Provenance Tests"
Cohesion: 0.05
Nodes (52): EmbeddedChunk, GenerationResponse, _context(), _conversation(), _embedded(), _extract(), FakeBBox, FakeConverter (+44 more)

### Community 7 - "Recursive Stage Heading Logic"
Cohesion: 0.06
Nodes (40): _is_markdown_separator(), _norm(), Compact heading context: the deepest heading normally, or the deepest two…, Recover the source segments (one per contributing block) from the merged chunk…, The text a pass-through chunk would carry with ``prefix`` present exactly once.…, A markdown table separator row, e.g. ``| --- | :--: |``., Text of each child (before the heading prefix), plus -- for the structural…, Pack whole list items into child bodies, never dividing one. A single item… (+32 more)

### Community 8 - "Evaluation Metric Evaluators"
Cohesion: 0.06
Nodes (44): answer_length(), citation_count(), exact_match(), Any, Exact answer match. Useful as a fast deterministic baseline., Records answer length. Helpful for spotting prompt regressions., Counts returned citations., FixtureManager (+36 more)

### Community 9 - "Qdrant Authorization Filter Tests"
Cohesion: 0.12
Nodes (59): _admin_team_branches(), _branch_count(), branch_filter(), call_hybrid_search(), find_matchany(), _jurisdiction_team_branches(), make_access(), make_dense_repository_with_fake_client() (+51 more)

### Community 10 - "Retrieval Exceptions"
Cohesion: 0.07
Nodes (38): ContextFormattingError, EmptyQueryError, NoRetrievalResultsError, Exception, Raised when no relevant contexts could be retrieved., Base exception for retrieval failures., Raised when the retrieval pipeline is improperly configured., Raised when retrieved contexts cannot be formatted for downstream generation. (+30 more)

### Community 11 - "Team API Routes"
Cohesion: 0.07
Nodes (39): add_team_member(), create_team(), list_teams(), promote_team_member(), TeamService, Remove a user's membership from a team entirely, regardless of its current…, Promote an existing ``TeamRole.MEMBER`` to ``TeamRole.MANAGER``. Only that…, Create a team in the requester's own organisation. Requires ``OrgRole.ADMIN``… (+31 more)

### Community 12 - "Base Document Handler"
Cohesion: 0.13
Nodes (24): BaseHandler, HandlerResult, ABC, Result returned by every document handler., Base class for all document handlers., CodeHandler, Token, Handles fenced code blocks. (+16 more)

### Community 13 - "Auth Login Endpoints"
Cohesion: 0.09
Nodes (36): login(), oauth2_login(), post, Authenticate a user using JSON. Used by the frontend., OAuth2-compatible login endpoint. Swagger sends: username password We interpret…, register(), LoginRequest, BaseModel (+28 more)

### Community 14 - "Chunking Evaluation Baselines"
Cohesion: 0.05
Nodes (44): baseline_apjspeech.txt (commit 888fc8c report), baseline_Attention.txt (commit 888fc8c report), baseline_LLM.txt (commit 888fc8c report), comparison.txt (baseline vs stage14 deltas), comparison_stage5_to_stage6.txt (Stage 6 primary comparison), apjspeech.pdf (eval corpus doc), Attention.pdf (eval corpus doc), LLM.pdf (eval corpus doc) (+36 more)

### Community 15 - "Base Ingestion Processor"
Cohesion: 0.09
Nodes (24): BaseProcessor, ABC, Path, Extract structured information from a document., Base class for every document processor., ProcessorFactory, Path, Returns the correct processor for a document. (+16 more)

### Community 16 - "Query Rewriter"
Cohesion: 0.12
Nodes (23): QueryRewriter, Build the prompt used to rewrite the latest user message into a standalone…, Convert structured conversation messages into a readable prompt format., Responsible for rewriting conversational user queries into standalone search…, Build the prompt used to generate or update the rolling conversation summary., Responsible for building prompts used to generate and maintain a rolling…, SummaryGenerator, Build the prompt used to generate a chat title. (+15 more)

### Community 17 - "Chunking Validation Helpers"
Cohesion: 0.10
Nodes (36): _block_range_valid(), _chunk_body(), _expected_prefix(), _heading_candidates(), _is_content_free(), _looks_like_md_table_row(), _num_stats(), _page_range_valid() (+28 more)

### Community 18 - "RBAC-5J Test Fixtures"
Cohesion: 0.18
Nodes (37): build_access(), make_organisation(), make_service(), make_team(), make_user(), Organisation, OrgRole, Mirrors get_access_context's real logic -- genuine team-membership and… (+29 more)

### Community 19 - "Org Manager Jurisdiction Exceptions"
Cohesion: 0.10
Nodes (27): OrgManagerJurisdictionAlreadyExistsError, OrgManagerJurisdictionNotFoundError, Raised when granting jurisdiction for a ``(user_id, team_id)`` pair that…, Raised when revoking a jurisdiction relationship that does not exist for the…, OrgManagerTeam, SQLAlchemy model representing an ``OrgRole.MANAGER``'s jurisdiction over a…, OrgManagerTeamRepository, Session (+19 more)

### Community 20 - "Dense Repository Collection Ops"
Cohesion: 0.07
Nodes (21): DenseRepository, Filter, HybridSearchResult, Create the Astra Study collection., Delete the Astra Study collection., Drop and recreate the collection. Useful during development., Insert or update points in the collection., Delete every point belonging to one schema_version=3 document. Scoped… (+13 more)

### Community 21 - "Base LLM Provider"
Cohesion: 0.09
Nodes (20): BaseLLMProvider, ABC, Generate a complete response from the language model., Stream a response from the language model., Base interface for all LLM providers., OpenAIProvider, OpenAI implementation of the LLM provider., Generate a complete response using OpenAI. (+12 more)

### Community 22 - "Auth Session Dependency"
Cohesion: 0.08
Nodes (25): get_db(), Session, Creates a new database session for each request and ensures it is closed after…, get_current_user(), Session, Return the currently authenticated user., AuthenticationError, InactiveUserError (+17 more)

### Community 23 - "Section Matching & Chunking Tests"
Cohesion: 0.18
Nodes (32): True when ``inner`` names the same section as ``outer`` or a subsection nested…, section_contains(), _body(), _chunk(), _heading(), _merge(), _mk(), _prov() (+24 more)

### Community 24 - "OrgRole Enum & Base Model"
Cohesion: 0.12
Nodes (25): OrgRole, Enum, str, A user's organisation-scoped role. Distinct from document access scope -- role…, Document, Base, TimestampMixin, Represents an uploaded document. (+17 more)

### Community 25 - "Chat Message & Conversation Tests"
Cohesion: 0.17
Nodes (31): ChatMessage, ChatSession, add_messages(), make_chat(), make_conversation_service(), make_summary_service(), Executable specification for the rolling conversation-memory behaviour…, Append ``count`` conversational messages with controlled timestamps. Roles… (+23 more)

### Community 26 - "Merge Stage Section Chunks"
Cohesion: 0.13
Nodes (34): _distinct(), _list_blocks(), _long(), _merged_section(), A MergeStage-style section chunk: ``blocks`` joined with blank lines…, Q2/Q3: 1 heading + 4 distinct body blocks, 2 pages, forced into several…, A single body block longer than several windows: a middle child holds only its…, Two adjacent blocks that share a verbatim 6-word run at their start. The… (+26 more)

### Community 27 - "Chat Not Found & Message API"
Cohesion: 0.12
Nodes (19): ChatNotFoundError, Raised when the requested chat session does not exist or is inaccessible., ChatRepository, datetime, Session, Repository for ChatSession database operations., Update the title of a chat session., Update the rolling summary of a chat session. ``summarized_through`` is the… (+11 more)

### Community 28 - "Chunking Report Analyzer"
Cohesion: 0.14
Nodes (32): analyze(), _block_from_dict(), _block_to_dict(), compare(), _dig(), extract(), _extraction_from_payload(), _list_content_audit() (+24 more)

### Community 29 - "Chat API Routes"
Cohesion: 0.11
Nodes (25): create_chat(), delete_chat(), get_chat(), list_chats(), delete, get, post, Response (+17 more)

### Community 30 - "Access Context Tests"
Cohesion: 0.16
Nodes (31): get_access_context(), Session, User, Build the request-scoped authorization identity. Every field is derived…, db(), make_jurisdiction(), make_membership(), make_organisation() (+23 more)

### Community 31 - "Block Type & Token Counting"
Cohesion: 0.16
Nodes (31): count_tokens(), Count the number of tokens in text., BlockType, Represents the semantic type of a document block. This enum is parser-…, StrEnum, _md_table(), _pipeline_from_blocks(), _row_lines() (+23 more)

### Community 32 - "RBAC-5G Whoami Jurisdiction Tests"
Cohesion: 0.18
Nodes (30): db(), make_jurisdiction(), make_membership(), make_organisation(), make_team(), make_user(), make_user_service(), fixture (+22 more)

### Community 33 - "RBAC-5J Parity Test Fixtures"
Cohesion: 0.11
Nodes (31): _document_payload(), get_jurisdiction(), make_document(), make_jurisdiction(), make_membership(), Document, DocumentAccessScope, parametrize (+23 more)

### Community 34 - "Base Generation Service"
Cohesion: 0.11
Nodes (20): BaseGenerationService, ABC, Abstract interface for the Generation layer. Implementations are responsible…, Generate a complete response., Stream the generated response. Each yielded string represents the next chunk of…, GenerationRequest, GenerationResponse, Structured response produced by the Generation layer. (+12 more)

### Community 35 - "Base Reranker"
Cohesion: 0.12
Nodes (18): BaseReranker, ABC, Abstract interface for all rerankers. Every reranker implementation…, Abstract base class for reranking implementations., Returns the underlying reranker model name., Returns the execution device. Example ------- cpu cuda cuda:0 mps, Batch size used for inference., Maximum sequence length accepted by the reranker. (+10 more)

### Community 36 - "Conversation Service Propagation Tests"
Cohesion: 0.10
Nodes (27): ConversationService, _individual_branch_user_id(), make_conversation_service(), make_dense_repository_with_fake_client(), _persisted(), Filter, parametrize, Executable specification for RBAC-5B: threading the trusted AccessContext… (+19 more)

### Community 37 - "Org Manager Jurisdiction Grant/Revoke API"
Cohesion: 0.11
Nodes (20): grant_org_manager_jurisdiction(), Grant an Org Manager jurisdiction over a team. Only ``OrgRole.ADMIN`` may call…, Revoke an Org Manager's jurisdiction over a team. Only ``OrgRole.ADMIN`` may…, revoke_org_manager_jurisdiction(), OrgManagerJurisdictionForbiddenError, Raised when a non-``OrgRole.ADMIN`` attempts to grant or revoke Org Manager…, Raised when the target user does not currently hold ``OrgRole.MANAGER``.…, TargetNotOrgManagerError (+12 more)

### Community 38 - "Reingest Metadata Tests"
Cohesion: 0.16
Nodes (23): main(), SimpleNamespace, db(), _FakeChunkPipeline, _FakeProcessor, make_document(), make_organisation(), make_user() (+15 more)

### Community 39 - "RBAC Foundation Tests"
Cohesion: 0.15
Nodes (24): db(), make_document(), make_organisation(), make_team(), make_upload_file(), make_user(), Document, fixture (+16 more)

### Community 40 - "AI Pipeline & Message Repository"
Cohesion: 0.09
Nodes (16): AIPipeline, Production AI orchestration layer. Responsibilities ---------------- - Convert…, MessageRepository, datetime, Session, Count the user + assistant messages created at or before ``timestamp``.…, Retrieve the most recent messages from a chat session. Returned in…, Repository for ChatMessage database operations. (+8 more)

### Community 41 - "Cross-Encoder Reranker"
Cohesion: 0.09
Nodes (15): CrossEncoderReranker, Automatically determine the best available inference device. Priority --------…, Name of the underlying HuggingFace model., Device used for inference., Batch size used during inference., Maximum sequence length accepted by the model., Returns the loaded CrossEncoder instance. This property is primarily useful for…, Validate the user query before inference. (+7 more)

### Community 42 - "Embedded Chunk Model"
Cohesion: 0.13
Nodes (15): EmbeddedChunk, Returns the chunk text., Returns the embedding dimensions., Represents a chunk together with its embedding. This object is produced by the…, DenseMapper, PointStruct, ScoredPoint, Convert multiple EmbeddedChunks into PointStructs. (+7 more)

### Community 43 - "Document Not Found & Delete Service"
Cohesion: 0.11
Nodes (19): DocumentNotFoundError, Raised when a requested document does not exist or does not belong to the…, DocumentService, AccessContext, BaseStorageService, DenseRepository, Document, DocumentResponse (+11 more)

### Community 44 - "Document Service API"
Cohesion: 0.12
Nodes (19): BinaryIO, Retrieve metadata for a single document., Upload one or more documents., Document, Create an authenticated API client., _client(), _document_service(), _normalize_heading_path() (+11 more)

### Community 45 - "RBAC Document Authorization Concepts"
Cohesion: 0.11
Nodes (26): Authorization (RBAC), DocumentAccessScope enum (app/enums/document.py), DocumentService, DocumentService._can_create, DocumentService._can_delete, InvalidAccessScopeError, Last-manager invariant (DELETE-embedded correlated subquery), OrganisationScopeForbiddenError (+18 more)

### Community 46 - "User Profile Endpoint"
Cohesion: 0.12
Nodes (13): get_current_user_profile(), get, UserService, Return the currently authenticated user's profile, including their organisation…, AuthService, ApiClient, Fetch the richer RBAC profile (organisation_id, role, team memberships) for the…, TokenResponse (+5 more)

### Community 47 - "Dependency Service Wiring"
Cohesion: 0.20
Nodes (24): build_conversation_summary_service(), get_auth_service(), get_chat_service(), get_conversation_service(), get_conversation_summary_service(), get_document_service(), get_ingestion_service(), get_message_service() (+16 more)

### Community 48 - "Embedding Batcher"
Cohesion: 0.13
Nodes (18): Split chunks into embedding batches., Convenience wrapper allowing the batcher to be called directly., EmbeddingBatchError, EmbeddingValidationError, Custom exceptions for the embeddings module., Raised when an embedding fails validation. Examples: - Empty embedding -…, Raised when an embedding batch is invalid. Examples: - Empty batch - Batch…, EmbeddingBatch (+10 more)

### Community 49 - "Sparse Embedding Encoder"
Cohesion: 0.12
Nodes (12): traceable, Generate sparse embedding for a user query., Generates sparse embeddings for document chunks using FastEmbed.…, Generate sparse embeddings for document chunks., SparseEncoder, Represents a sparse vector generated by the sparse encoder. Unlike dense…, Number of non-zero dimensions., Represents a document chunk together with its sparse vector. (+4 more)

### Community 50 - "Conversation Service Message Flow"
Cohesion: 0.13
Nodes (18): ConversationService, BackgroundTasks, ChatMessage, ChatSession, ConversationResponse, MessageCreate, MessageService, StreamEvent (+10 more)

### Community 51 - "Frontend Chat Service Client"
Cohesion: 0.17
Nodes (13): ChatService, Chat, Citation, _active_chat(), _client(), Refresh the sidebar chat list., Return the selected chat., Render workspace heading. (+5 more)

### Community 52 - "Frontend API Client"
Cohesion: 0.14
Nodes (10): ApiClient, ApiException, Any, Exception, Response, Download binary data., Open a Server-Sent Events POST request., Base HTTP client used by all frontend services. (+2 more)

### Community 53 - "OpenAI Embedder"
Cohesion: 0.17
Nodes (15): EmbeddingBatcher, Splits document chunks into batches suitable for the embedding provider. The…, OpenAIEmbedder, Generates OpenAI embeddings for DocumentChunks. Responsibilities…, EmbeddingMetadata, Metadata describing how an embedding was generated. Document metadata is…, EmbeddingPipeline, Production embedding pipeline. Pipeline DocumentChunks │ ▼ EmbeddingBatcher │ ▼… (+7 more)

### Community 54 - "Reranking Candidate Validation"
Cohesion: 0.13
Nodes (15): Validate retrieval candidates before reranking., CandidateFormatError, EmptyCandidateError, InvalidQueryError, InvalidTopKError, ModelLoadError, PredictionError, Exception (+7 more)

### Community 55 - "Reranking Pipeline Tests"
Cohesion: 0.16
Nodes (22): preview_text(), print_header(), print_hybrid_results(), print_performance(), print_quality_benchmark(), print_rank_movements(), print_reranked_results(), print_reranking_statistics() (+14 more)

### Community 56 - "Filter Stage"
Cohesion: 0.17
Nodes (19): FilterStage, Removes only truly useless chunks. Philosophy ---------- Never remove…, is_copyright(), is_doi(), is_empty(), is_isbn(), is_numeric_only(), is_page_number() (+11 more)

### Community 57 - "Retrieval Service Orchestrator"
Cohesion: 0.12
Nodes (15): RetrievalResult, traceable, Execute the complete retrieval pipeline. Steps ----- 1. Validate query 2.…, Production Retrieval Orchestrator. Pipeline -------- User Query │ ▼ Hybrid…, Callable wrapper. Allows RetrievalService to be invoked like a function while…, Convert reranked search results into RetrievedContext objects consumed by…, RetrievalService, HybridService (+7 more)

### Community 58 - "Dense Search Exceptions"
Cohesion: 0.13
Nodes (21): CollectionAlreadyExistsError, CollectionCreationError, CollectionDeletionError, CollectionNotFoundError, DenseSearchConfigurationError, DenseSearchError, InvalidPayloadError, InvalidSearchQueryError (+13 more)

### Community 59 - "Base Storage Service"
Cohesion: 0.12
Nodes (13): BaseStorageService, ABC, Path, UploadFile, Save a file and return: ( stored_filename, file_size, ), Delete a stored file., Return the absolute path of a stored file., Base interface for all storage providers. (+5 more)

### Community 60 - "Frontend Layout & Streaming"
Cohesion: 0.13
Nodes (19): ChatService, AuthService.get_current_user_profile, frontend/app.py (3-column layout), frontend/models/user.py::User, frontend/models/user.py User dataclass, Streaming protocol (SSE), TeamMembershipResponse, UserProfileResponse (app/schemas/user.py) (+11 more)

### Community 61 - "AI Pipeline Response Building"
Cohesion: 0.16
Nodes (13): AIResponse, ChatMessage, StreamEvent, traceable, Stream an assistant response using Retrieval-Augmented Generation., Generate a short AI title for a new conversation., Generate or update the conversation summary., Build the query used for document retrieval. Conversational follow-up questions… (+5 more)

### Community 62 - "Embedding Request Execution"
Cohesion: 0.11
Nodes (17): traceable, Execute one embedding request. Retries automatically for transient OpenAI…, Embed a single batch of document chunks. Parameters ---------- chunks A batch…, Generate an embedding for a user query., Estimate embedding cost in USD. Cost is calculated using the official OpenAI…, EmbeddingCacheError, EmbeddingError, EmbeddingGenerationError (+9 more)

### Community 63 - "Reranker Callable Interface"
Cohesion: 0.11
Nodes (12): Allows the reranker instance to be invoked like a function. Example -------…, Rerank retrieved candidates. Parameters ---------- query: User query.…, slice, SupportsIndex, Returns the top-k reranked chunks. Parameters ---------- k: Number of chunks to…, Represents a single reranked retrieval result. Attributes ---------- result:…, Represents the complete output of the reranking stage. Attributes ----------…, Returns the highest ranked chunk. (+4 more)

### Community 64 - "Qdrant Test Isolation Conftest"
Cohesion: 0.12
Nodes (17): DenseRepository.COLLECTION_NAME, Persistence (SQLAlchemy + Qdrant + filesystem), Qdrant collection (astra_study / astra_study_test), tests/conftest.py (Qdrant test isolation guard), _isolate_qdrant_collection(), pytest_collection_modifyitems(), pytest_sessionfinish(), Test-wide Qdrant collection isolation. The integration tests drive… (+9 more)

### Community 65 - "Document Service Delete/Download UI"
Cohesion: 0.16
Nodes (17): DocumentService, Service responsible for all document-related operations., Download the original uploaded document., _client(), _create_chat(), _load_chat(), Refresh chats and documents., Load a chat and its messages. (+9 more)

### Community 66 - "Alembic Migration Env"
Cohesion: 0.14
Nodes (15): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Base, Base class for all SQLAlchemy ORM models., ChatSession, Represents a chat session belonging to a user. (+7 more)

### Community 67 - "Document API Routes"
Cohesion: 0.14
Nodes (19): delete_document(), download_document(), get_document(), get_documents(), AccessContext, DocumentResponse, IngestionService, UploadFile (+11 more)

### Community 68 - "Settings & Access Dependencies"
Cohesion: 0.28
Nodes (3): Application settings loaded from environment variables., Settings, BaseSettings

### Community 69 - "Ingestion & Citation Provenance Flow"
Cohesion: 0.12
Nodes (19): app/ingestion/factory.py::ProcessorFactory, app/ingestion/processors/docling.py (DoclingProcessor), BlockProvenance, Citation model (app/generation/models.py), DenseRepository.delete_by_document_id, DoclingProcessor (app/ingestion/processors/docling.py), DocumentBlock, POST /api/v1/documents (upload route) (+11 more)

### Community 70 - "Semantic Stage Merge"
Cohesion: 0.20
Nodes (16): Narrow post-split cleanup. Responsibilities ---------------- - concatenate a…, SemanticStage, BlockProvenance, A compact, parser-neutral reference to the source of one block., _sc(), _sem_chunk(), test_semantic_caption_owns_following_text_still_works(), test_semantic_merge_deduplicates_shared_provenance() (+8 more)

### Community 71 - "Retrieval/Hybrid/Reranking DI Wiring"
Cohesion: 0.14
Nodes (18): get_hybrid_service(), get_reranking_service(), get_retrieval_service(), RetrievalService, HybridService, RerankingService, print_results(), GenerationRequest (+10 more)

### Community 72 - "AccessContext Jurisdiction Concepts"
Cohesion: 0.16
Nodes (18): AccessContext (app/retrieval/access.py), AccessContext.jurisdiction_team_ids, app/dependencies/access.py::get_access_context, app/dependencies/auth.py::get_current_user, DenseRepository._authorization_filter, Request/DI layering (backend), DocumentRepository, DocumentRepository.get_visible / get_by_id_visible / _visibility_conditions (+10 more)

### Community 73 - "Caption Handler"
Cohesion: 0.16
Nodes (12): CaptionHandler, Token, Detects figure/table captions., Token, clean_text(), is_caption(), is_image_text(), is_page_number() (+4 more)

### Community 74 - "Citation Model & Scoring"
Cohesion: 0.20
Nodes (15): Citation, Represents a source citation supporting the generated answer., _answer_support(), _citation_relevance(), _excerpt(), _heading_match(), _query_term_weights(), Weighted fraction of the question's *discriminative* terms carried by this… (+7 more)

### Community 75 - "Password Hashing & JWT Security"
Cohesion: 0.16
Nodes (9): Any, Handles password hashing, password verification, and JWT token generation., Decode and validate a JWT., Hash a plain-text password., Verify a password against its hash., Create an access token., Create a refresh token., SecurityManager (+1 more)

### Community 76 - "Hybrid Payload Mapper"
Cohesion: 0.31
Nodes (14): HybridMapper, Converts Astra Study domain models into hybrid Qdrant PointStruct objects.…, Build the payload stored alongside every vector inside Qdrant. Payload…, _embedded(), EmbeddedChunk, Executable specification for RBAC-5C: RBAC-aware Qdrant payloads for newly…, DenseMapper is not part of the production indexing path (only…, _rbac_metadata() (+6 more)

### Community 77 - "Conversation Memory Flow Concepts"
Cohesion: 0.17
Nodes (16): AIPipeline (app/ai/pipeline.py), tests/conftest.py (Qdrant isolation guard), Conversation memory (rolling summary + recent window), Conversation memory (rolling summary + recent window) design, conversation_summary.run_summary_refresh, ConversationService (app/services/conversation.py), ConversationSummaryService.update_summary, DenseRepository (+8 more)

### Community 78 - "Prompt Builder & Fakes"
Cohesion: 0.18
Nodes (13): PromptBuilder, _FakeLLM, _FakeRetrieval, make_pipeline(), orm_conversation(), parametrize, A pending/failed first summary must not trigger history truncation., test_full_history_used_before_first_summary() (+5 more)

### Community 79 - "Reranking Service Tests"
Cohesion: 0.23
Nodes (15): RerankingResult, make_hybrid_result(), make_reranking_result(), make_service(), HybridSearchResult, RetrievalService, Graceful empty retrieval (commit b5d8d4b): when every candidate is filtered out…, The other half of graceful empty retrieval: no hybrid candidates at all short-… (+7 more)

### Community 80 - "Generation Exceptions"
Cohesion: 0.18
Nodes (14): EmptyPromptError, EmptyResponseError, GenerationError, GenerationTimeoutError, InvalidGenerationResponseError, Exception, Exceptions raised by the Generation module., Raised when prompt generation results in no messages. (+6 more)

### Community 81 - "Chunking Pipeline Contract Concepts"
Cohesion: 0.24
Nodes (15): Chunking pipeline contract, ChunkingConfig (app/chunking/config.py), ChunkPipeline (app/chunking/pipeline.py), ContentSegment, evaluation/chunking_report.py (offline structural evaluator), FilterStage, FinalizeStage, Chunking pipeline contract (frozen) (+7 more)

### Community 82 - "AI Pipeline DI Wiring"
Cohesion: 0.21
Nodes (12): AIPipeline, get_ai_pipeline(), get_generation_service(), get_llm_service(), get_prompt_builder(), Dependency for AIPipeline., FixtureManager, GenerationService (+4 more)

### Community 83 - "Markdown Token Converter"
Cohesion: 0.19
Nodes (9): DocumentConverter, Token, Converts Markdown-It tokens into semantic DocumentBlocks. The converter itself…, Convert Markdown tokens into semantic DocumentBlocks., ImageHandler, Token, Handles OCR text extracted from figures/images. Markdown-based parsers may emit…, MarkdownPage (+1 more)

### Community 84 - "Document Access Scope Enum"
Cohesion: 0.23
Nodes (9): DocumentAccessScope, DocumentStatus, Enum, str, Who can retrieve/query a document. Separate from ``OrgRole`` / ``TeamRole`` --…, Processing state of a document., DocumentResponse, BaseModel (+1 more)

### Community 85 - "Base Repository CRUD"
Cohesion: 0.20
Nodes (7): BaseRepository, Session, Base repository providing common CRUD operations., Persist a new entity., Retrieve an entity by its primary key., Persist changes made to an existing entity., ModelType

### Community 86 - "Document Validator"
Cohesion: 0.20
Nodes (9): DocumentValidator, Validates document-level metadata., Any, One metric produced by a validator., Output returned by every validator. Every validator returns exactly one…, Represents a non-fatal validation issue., ValidationMetric, ValidationResult (+1 more)

### Community 87 - "Chunk-Document Provenance Stamping"
Cohesion: 0.31
Nodes (14): DocumentChunk, Document, Stamp every chunk's metadata from the one authoritative Document row.…, _stamp_rbac_fields(), _embedded(), make_document_like(), ChunkMetadata, DocumentAccessScope (+6 more)

### Community 88 - "Evaluation AI Response Schemas"
Cohesion: 0.17
Nodes (8): AIResponse, Response returned by the AI orchestration layer. This model is intentionally…, EvaluationPredictor, AccessContext, AIPipeline, Executes Astra Study's production AI pipeline for LangSmith evaluation. This…, ``access`` is resolved once from the real database-backed User/TeamMembership…, Executes the production AI pipeline for a single evaluation example.

### Community 89 - "Dense Pipeline Collection Ops"
Cohesion: 0.17
Nodes (3): DensePipeline, Production dense search pipeline. Responsibilities ----------------…, Execute dense vector similarity search.

### Community 90 - "Sparse Search Exceptions"
Cohesion: 0.23
Nodes (11): Exception, Raised when the sparse encoder configuration is invalid., Base exception for all sparse search errors., Raised when a sparse vector collection operation fails., Raised when sparse retrieval fails., Raised when sparse embeddings cannot be generated., SparseCollectionError, SparseConfigurationError (+3 more)

### Community 91 - "Message Service Streaming"
Cohesion: 0.35
Nodes (4): MessageService, Yield assistant text chunks from the message SSE endpoint., Conversation, Message

### Community 92 - "Base Retrieval Service"
Cohesion: 0.27
Nodes (6): ABC, BaseRetrievalService, RetrievalResult, Base contract for all retrieval implementations., Execute the complete retrieval pipeline. Retrieval is keyword-only and always…, Allow the service to be invoked like a function.

### Community 93 - "Exception Handlers & Reranker Resource"
Cohesion: 0.25
Nodes (9): get_reranking_resource(), Return the shared reranking service. The underlying CrossEncoder model is…, FastAPI, Register all application exception handlers., register_exception_handlers(), lifespan(), FastAPI, get (+1 more)

### Community 94 - "Document Scope Exceptions"
Cohesion: 0.18
Nodes (10): InvalidAccessScopeError, OrganisationScopeForbiddenError, Raised for a malformed or self-contradictory scope/team_id combination on…, Raised when the requested ``team_id`` does not exist, or exists in a different…, Raised when the requester is authenticated and the team exists in their own…, Raised when a non-ADMIN requests ORGANISATION-scoped document creation., TeamMembershipRequiredError, TeamNotFoundError (+2 more)

### Community 95 - "Hybrid Pipeline Ops"
Cohesion: 0.18
Nodes (3): HybridPipeline, Production Hybrid Indexing Pipeline. Responsibilities ----------------…, Index document chunks using hybrid dense+sparse vectors.

### Community 96 - "Repo Top-Level Areas"
Cohesion: 0.22
Nodes (10): alembic/ migrations, app/ (FastAPI backend), Astra Study, evaluation/ harness, frontend/ (Streamlit UI), scripts/ (operational one-offs), grant_admin(), main() (+2 more)

### Community 97 - "RBAC-5J Migration & Repository Concepts"
Cohesion: 0.18
Nodes (11): Document model (app/models/document.py), ManagedTeamResponse (RBAC-5J), alembic migration 116ced32c143 (RBAC org/team foundation), Organisation model (app/models/organisation.py), OrgManagerTeamRepository, OrgManagerTeamRepository.grant, OrgManagerTeamRepository.revoke, alembic 116ced32c143_rbac_organisation_team_foundation (+3 more)

### Community 98 - "Base App Exceptions"
Cohesion: 0.24
Nodes (7): EmailAlreadyExistsError, AppException, Raised when a username is already taken., Raised when a target user id does not exist, or belongs to a different…, Raised when an email is already registered., UsernameAlreadyExistsError, UserNotFoundError

### Community 99 - "Reranking Service Public API"
Cohesion: 0.22
Nodes (6): traceable, Callable wrapper. Example ------- >>> result = service( ... query=query, ...…, Public service for document reranking. The service hides the concrete reranker…, Initialize the reranking service. Parameters ---------- reranker: Optional…, Returns the active reranker. The default CrossEncoderReranker is created only…, RerankingService

### Community 100 - "Sparse Pipeline Ops"
Cohesion: 0.22
Nodes (5): Generate sparse vectors for multiple chunks., Generate a sparse vector for a search query., Convenience wrapper around encode()., Generates sparse embeddings for document chunks. Responsibilities…, SparsePipeline

### Community 101 - "Import Isolation Regression Test"
Cohesion: 0.24
Nodes (9): CompletedProcess, parametrize, Regression test for a circular import discovered during the RBAC-5B independent…, Reproduces the exact import order used by ``scripts/reingest_document.py``…, Run ``code`` in a brand-new Python process with no inherited ``sys.modules``…, Each of these must be importable as the very first thing a fresh process does…, _run_in_fresh_process(), test_reingest_document_script_import_sequence_succeeds_in_fresh_process() (+1 more)

### Community 102 - "OpenAI Client Factory"
Cohesion: 0.29
Nodes (5): get_openai_client(), Create and return an OpenAI client. The client is configured using application…, EmbeddingConfigurationError, Raised when the embedding configuration is invalid. Examples: - Missing API key…, OpenAI

### Community 103 - "Message API & Schemas"
Cohesion: 0.29
Nodes (8): create_message(), BackgroundTasks, ConversationResponse, MessageCreate, Send a message and receive the assistant response., Stream an assistant response using Server-Sent Events (SSE)., stream_message(), StreamingResponse

### Community 104 - "API Response Schemas"
Cohesion: 0.36
Nodes (6): success_response(), ApiResponse, ErrorResponse, BaseModel, Standard error API response., Standard success API response.

### Community 105 - "Citation Ranking Rationale"
Cohesion: 0.32
Nodes (8): answer_support scoring term, Citations (single source of truth), Deterministic citation ranking rationale (no LLM), GenerationService (app/generation/service.py), GenerationService.citations_for, LLMService (OpenAI-backed), prompt_builder (app/generation/prompt_builder.py), _query_term_weights

### Community 106 - "Health Check Route"
Cohesion: 0.38
Nodes (5): health_check(), get, HealthResponse, BaseModel, Response model for the health check endpoint.

### Community 107 - "Markdown Parser"
Cohesion: 0.29
Nodes (4): DocumentParser, Token, Parse Markdown into tokens., Parses Markdown into Markdown-It tokens. This class is intentionally…

### Community 108 - "Chunk UUID Helpers"
Cohesion: 0.29
Nodes (4): UUID, Returns the UUIDs of all chunks contained in the batch., Returns the chunk UUID., Returns the document UUID.

### Community 109 - "Hybrid Point Conversion"
Cohesion: 0.43
Nodes (5): EmbeddedChunk, PointStruct, Combine dense and sparse representations into a single hybrid Qdrant point., Convert dense and sparse chunk collections into hybrid PointStructs. Both lists…, SparseEmbeddedChunk

### Community 110 - "Embedding Vector Model"
Cohesion: 0.33
Nodes (4): Convert raw vectors returned by OpenAI into EmbeddedChunk objects., EmbeddingVector, Represents a dense embedding vector generated by an embedding model. The vector…, Returns the embedding dimension.

### Community 111 - "Dense Search Response"
Cohesion: 0.33
Nodes (4): DenseSearchResponse, Represents the complete response returned from the dense search pipeline., Number of retrieved results., Highest similarity score.

### Community 112 - "Hybrid Search Result Conversion"
Cohesion: 0.47
Nodes (4): HybridSearchResult, Convert a Qdrant ScoredPoint into a HybridSearchResult., Convert multiple ScoredPoints into HybridSearchResult objects., ScoredPoint

### Community 113 - "Document Validator Module"
Cohesion: 0.33
Nodes (4): DocumentValidator, UploadFile, Validates uploaded documents before they are stored on disk., Validate an uploaded document. Raises ------ HTTPException If validation fails.

### Community 115 - "OpenAI Model Enum"
Cohesion: 0.50
Nodes (4): OpenAIModel, Enum, str, Supported OpenAI chat models.

### Community 116 - "Document Block Handler Interface"
Cohesion: 0.40
Nodes (3): Token, Returns True if this handler can process the current token., Converts one logical markdown block into a DocumentBlock.

### Community 117 - "TeamRole Enum"
Cohesion: 0.50
Nodes (4): Enum, str, A user's role within a single team membership. Independent of ``OrgRole``: a…, TeamRole

### Community 119 - "Qdrant Filter Evaluator (RBAC-5J Parity)"
Cohesion: 0.40
Nodes (5): _evaluate_qdrant_condition(), _evaluate_qdrant_filter(), Filter, Evaluate one condition node (a nested Filter, a FieldCondition, or an…, Evaluate a real qdrant_client ``Filter`` object against a payload dict,…

### Community 120 - "Message Service Retrieval"
Cohesion: 0.50
Nodes (4): get_messages(), MessageService, Retrieve all messages for a chat session., MessageResponse

### Community 133 - "Kalam Speech Fixture Doc"
Cohesion: 1.00
Nodes (3): A P J Abdul Kalam Departing Speech (upload 510fce33), A P J Abdul Kalam Departing Speech, Developed India 2020

## Ambiguous Edges - Review These
- `tests/conftest.py (Qdrant isolation guard)` → `ConversationSummaryService.update_summary`  [AMBIGUOUS]
  CLAUDE.md · relation: semantically_similar_to

## Knowledge Gaps
- **62 isolated node(s):** `astra-study`, `stage6_LLM.txt (Stage 6 ContentSegment report)`, `stage7_LLM.txt (Stage 7 report)`, `Multi-head attention`, `Scaled dot-product attention` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1173 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **82 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `tests/conftest.py (Qdrant isolation guard)` and `ConversationSummaryService.update_summary`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `AccessContext` connect `Team API Routes` to `Document Repository Visibility`, `Document Exceptions`, `Team Exceptions`, `Document Creation Test Fixtures`, `Embedded Chunk & Provenance Tests`, `Evaluation Metric Evaluators`, `Qdrant Authorization Filter Tests`, `Query Rewriter`, `RBAC-5J Test Fixtures`, `Org Manager Jurisdiction Exceptions`, `Dense Repository Collection Ops`, `Chat Message & Conversation Tests`, `Chat Not Found & Message API`, `Access Context Tests`, `RBAC-5J Parity Test Fixtures`, `Conversation Service Propagation Tests`, `Org Manager Jurisdiction Grant/Revoke API`, `RBAC Foundation Tests`, `AI Pipeline & Message Repository`, `Conversation Service Message Flow`, `Reranking Pipeline Tests`, `Retrieval Service Orchestrator`, `AI Pipeline Response Building`, `Settings & Access Dependencies`, `Reranking Service Tests`, `Document Access Scope Enum`, `Base Retrieval Service`, `Message API & Schemas`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `DocumentChunk` connect `Chunk Metadata & Content Segments` to `Chunking Config & Pipeline`, `Recursive Stage Heading Logic`, `Chunking Validation Helpers`, `Section Matching & Chunking Tests`, `Merge Stage Section Chunks`, `Chunking Report Analyzer`, `Block Type & Token Counting`, `Embedded Chunk Model`, `Embedding Batcher`, `Sparse Embedding Encoder`, `OpenAI Embedder`, `Filter Stage`, `Embedding Request Execution`, `Settings & Access Dependencies`, `Semantic Stage Merge`, `Hybrid Payload Mapper`, `Document Validator`, `Hybrid Pipeline Ops`, `Sparse Pipeline Ops`, `Embedding Vector Model`, `Embedding Pipeline Callable`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `get_current_user_profile()` connect `User Profile Endpoint` to `Auth Login Endpoints`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `DocumentChunk` (e.g. with `ChunkPipeline` and `BaseChunkStage`) actually correct?**
  _`DocumentChunk` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 88 inferred relationships involving `BlockType` (e.g. with `FilterStage` and `MergeStage`) actually correct?**
  _`BlockType` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `AccessContext` (e.g. with `AIPipeline` and `create_message()`) actually correct?**
  _`AccessContext` has 25 INFERRED edges - model-reasoned connections that need verification._