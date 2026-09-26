# Graph Report - Astra-Study  (2026-09-26)

## Corpus Check
- 11 files · ~242,315 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2746 nodes · 6722 edges · 199 communities (108 shown, 56 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 591 edges (avg confidence: 0.93)
- Token cost: 0 input · 77,474 output

## Community Hubs (Navigation)
- Document Exceptions (RBAC Errors)
- DocumentService CRUD & Exceptions
- Dense Repository Authorization & Delete
- Evaluation Predictor
- Merge/Quality Stage Tests
- Recursive Split & Tokenizer Utils
- Chunking Tests & Section Utilities
- Docling Block Handlers
- AI Pipeline & Message Models
- Chunk Pipeline & Stages
- Docling Ingestion Processor
- Evaluation Fixtures & Test Documents
- Document Repository Visibility
- Offline Chunking Evaluator
- Whoami API & Team Membership Repository
- LLM Provider Base & Service
- Service Dependency Wiring & AI Pipeline Init
- Citation Generation & Scoring
- Retrieval Formatter & Exceptions
- Query Rewrite & Summary Generators
- Chat Repository & Service
- Chunk Pipeline Contract Tests
- AccessContext & Hybrid Search Tests
- Auth API & User Service
- Storage Service Base
- Service Dependency Wiring & AI Pipeline Init
- Message API & Conversation Service
- Frontend Document Service & Sources
- Embedding Batcher & OpenAI Embedder
- Offline Chunking Evaluator
- RBAC SQLAlchemy Models
- CrossEncoder Reranker Base
- Auth Dependency & Base Repository
- Citation & Provenance Tests
- CrossEncoder Reranker Implementation
- AccessContext Dependency & Tests
- Exception Hierarchy & App Entrypoint
- Semantic Merge Stage Tests
- Sparse Encoder & Hybrid Pipeline
- Dense Search Mapper & Pipeline
- Dense Search Mapper & Pipeline
- Frontend API Client
- AIPipeline Orchestration
- Reranking Exceptions
- Frontend Auth Service & Chat Service
- Frontend Sidebar & State
- Reranking Integration Test
- Dense Search Exceptions
- Frontend Chat Service & Workspace
- OpenAI Embedder Exceptions
- Reranking Result Models
- Message API & ConversationService
- ConversationService & Memory Tests
- Chat API & Document Upload
- Embedding Batcher & Dense Pipeline
- AccessContext Dependency & Tests
- ConversationService & Memory Tests
- Service Dependency Wiring & AI Pipeline Init
- Citation & Provenance Tests
- ConversationService & Memory Tests
- CLAUDE.md Document Authorization Concepts
- Reingest Script RBAC Stamping
- Frontend Message Service & Models
- CLAUDE.md Architecture Concepts
- Qdrant Isolation Conftest & Tests
- Filter Stage & Noise Filters
- Core Security (JWT/Password)
- Retrieval Formatter & Exceptions
- Hybrid Search Mapper
- CLAUDE.md Chunking Contract Notes
- CLAUDE.md Ingestion & RBAC Data Model Concepts
- Docling Block Handlers
- Document Validation Models
- RBAC-5F Reingest Metadata Test Fixtures
- Embedding Batcher & OpenAI Embedder
- Generation Exceptions
- BaseRetrievalService & Retrieval Tests
- Sparse Search Exceptions
- Merge/Quality Stage Tests
- Document API & Ingestion Service
- UserService Registration & Default Organisation
- Sparse Encoder & Hybrid Pipeline
- PromptBuilder
- CrossEncoder Reranker Base
- Sparse Encoder & Hybrid Pipeline
- Search Import Isolation Tests
- Citation & Provenance Tests
- Reingest Test Fake Pipeline Fixtures
- Alembic Env Migration Runner
- API Response Schemas
- RetrievalService & Integration Tests
- Chat/Message Models & Repositories
- ConversationService & Memory Tests
- Health Check Endpoint
- Document Parser
- Hybrid Search Mapper
- Storage Service Base
- Dense Search Response Model
- Hybrid Search Mapper
- OpenAI Model Enum
- Docling Block Handlers
- Docling Block Handlers
- Docling Ingestion Processor
- AccessContext & Hybrid Search Tests
- Citation & Provenance Tests
- CLAUDE.md Project Overview
- Reingest Test Non-Closing Session Helper
- ConversationService & Memory Tests
- AccessContext & Hybrid Search Tests
- Chunking Evaluator Artifacts (LLM)
- APJ Speech Fixture Upload
- AI Package Init
- Document Constants
- Constants Package Init
- Hybrid Search Package Init
- Multi-Head Attention Fixture
- Document API & Ingestion Service
- Document API & Ingestion Service
- Document API & Ingestion Service
- Document API & Ingestion Service
- Document API & Ingestion Service
- Document API Routes
- Message GET Route Marker
- Message POST Route Marker
- Auth API & User Service
- Service Dependency Wiring & AI Pipeline Init
- Dependency Injection Wiring
- Chat Repository & Service
- Dependency Injection Wiring
- Service Dependency Wiring & AI Pipeline Init
- Dependency Injection Wiring
- Document Repository & Access Dependency
- Retrieval Base ABC Marker
- Auth API & User Service
- Dense Qdrant Repository
- Reranker Call & Hybrid Mapper
- DocumentService Authorization Logic
- User Service Type Marker
- Service Dependency Wiring & AI Pipeline Init
- Docker Compose Config
- Chat API & Document Upload
- Chunking Fallback Artifact
- APJ Speech Pre-Chunking Artifact
- LLM Pre-Chunking Artifact
- Frozen Blocks Artifact Readme
- Source Item ID Coverage Metric
- APJ Speech Stage-14 Artifact
- LLM Stage-14 Artifact
- APJ Speech Stage-6 Artifact
- APJ Speech Stage-7 Artifact
- Attention Stage-7 Artifact
- Structural Atomicity Metric
- Fixture Type Marker
- Frontend README
- Generation Request Type Marker
- Package Metadata Marker
- Dense Qdrant Repository
- Storage Service Base
- Storage Service Base
- Storage Service Base
- Storage Service Base
- Storage Service Base
- Auth API & User Service
- Storage Service Base

## God Nodes (most connected - your core abstractions)
1. `DocumentChunk` - 140 edges
2. `BlockType` - 113 edges
3. `DocumentBlock` - 51 edges
4. `AccessContext` - 45 edges
5. `count_tokens()` - 43 edges
6. `build_access()` - 41 edges
7. `User` - 40 edges
8. `make_user()` - 40 edges
9. `make_document_service()` - 39 edges
10. `make_organisation()` - 38 edges

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
- **Ingestion pipeline flow (upload to vectors)** — claude_md_ingestionservice, claude_md_processorfactory, claude_md_docling_processor, claude_md_chunkpipeline, claude_md_hybridpipeline [EXTRACTED 1.00]
- **Retrieval and generation flow with RBAC threading** — claude_md_aipipeline, claude_md_retrievalservice, claude_md_hybridservice, claude_md_denserepository, claude_md_accesscontext, claude_md_rerankingservice, claude_md_generationservice [EXTRACTED 1.00]
- **Document authorization group (create/read/delete)** — claude_md_documentservice, claude_md_documentservice_can_create, claude_md_documentservice_can_delete, claude_md_documentrepository, claude_md_document_exceptions, claude_md_teammembershiprepository [EXTRACTED 1.00]

## Communities (199 total, 56 thin omitted)

### Community 0 - "Document Exceptions (RBAC Errors)"
Cohesion: 0.05
Nodes (109): DocumentTooLargeError, EmptyDocumentError, InvalidAccessScopeError, InvalidDocumentTypeError, OrganisationScopeForbiddenError, Raised when an empty document is uploaded., Raised when a document exceeds the allowed size., Raised for a malformed or self-contradictory scope/team_id combination on… (+101 more)

### Community 1 - "DocumentService CRUD & Exceptions"
Cohesion: 0.09
Nodes (75): DocumentNotFoundError, Raised when a requested document does not exist or does not belong to the…, BaseStorageService, DenseRepository, DocumentRepository, TeamMembershipRepository, build_access(), db() (+67 more)

### Community 2 - "Dense Repository Authorization & Delete"
Cohesion: 0.06
Nodes (61): DenseRepository, AccessContext, Filter, HybridSearchResult, PointStruct, Create the Astra Study collection., Delete the Astra Study collection., Drop and recreate the collection. Useful during development. (+53 more)

### Community 3 - "Evaluation Predictor"
Cohesion: 0.05
Nodes (48): answer_length(), citation_count(), exact_match(), Any, Exact answer match. Useful as a fast deterministic baseline., Records answer length. Helpful for spotting prompt regressions., Counts returned citations., FixtureManager (+40 more)

### Community 4 - "Merge/Quality Stage Tests"
Cohesion: 0.06
Nodes (53): ChunkMetadata, ContentSegment, DocumentChunk, One source ``DocumentBlock`` that ``MergeStage`` folded into a chunk. Internal…, Represents one chunk that will eventually be embedded and stored in the vector…, Metadata associated with a document chunk. This metadata flows through the…, One ContentSegment for a source block as it enters MergeStage (each chunk is…, Emit ``builder`` -- unless it only ever held a heading (or nothing), in which… (+45 more)

### Community 5 - "Recursive Split & Tokenizer Utils"
Cohesion: 0.06
Nodes (42): _is_markdown_separator(), _norm(), Compact heading context: the deepest heading normally, or the deepest two…, Recover the source segments (one per contributing block) from the merged chunk…, The text a pass-through chunk would carry with ``prefix`` present exactly once.…, A markdown table separator row, e.g. ``| --- | :--: |``., Text of each child (before the heading prefix), plus -- for the structural…, Pack whole list items into child bodies, never dividing one. A single item… (+34 more)

### Community 6 - "Chunking Tests & Section Utilities"
Cohesion: 0.09
Nodes (60): True when ``inner`` names the same section as ``outer`` or a subsection nested…, section_contains(), _body(), _chunk(), _fchunk(), _heading(), _md_table(), _merge() (+52 more)

### Community 7 - "Docling Block Handlers"
Cohesion: 0.11
Nodes (36): BaseHandler, HandlerResult, ABC, Result returned by every document handler., Base class for all document handlers., CaptionHandler, Token, Detects figure/table captions. (+28 more)

### Community 8 - "AI Pipeline & Message Models"
Cohesion: 0.08
Nodes (27): AIResponse, Response returned by the AI orchestration layer. This model is intentionally…, Enum, ChatMessage, Represents a single message within a chat session., MessageRepository, datetime, Session (+19 more)

### Community 9 - "Chunk Pipeline & Stages"
Cohesion: 0.11
Nodes (24): ChunkPipeline, Executes the configured chunking stages., BaseChunkStage, ABC, Process the incoming data and return chunks., Base interface for every chunking stage., FilterStage, Removes only truly useless chunks. Philosophy ---------- Never remove… (+16 more)

### Community 10 - "Docling Ingestion Processor"
Cohesion: 0.08
Nodes (28): BaseProcessor, ABC, Path, Extract structured information from a document., Base class for every document processor., ProcessorFactory, Path, Returns the correct processor for a document. (+20 more)

### Community 11 - "Evaluation Fixtures & Test Documents"
Cohesion: 0.05
Nodes (47): app/ (FastAPI backend), LangSmith tracing, SQLite (astra_study.db) via SQLAlchemy/Alembic, baseline_apjspeech.txt (commit 888fc8c report), baseline_Attention.txt (commit 888fc8c report), baseline_LLM.txt (commit 888fc8c report), comparison.txt (baseline vs stage14 deltas), comparison_stage5_to_stage6.txt (Stage 6 primary comparison) (+39 more)

### Community 12 - "Document Repository Visibility"
Cohesion: 0.06
Nodes (27): DocumentRepository, AccessContext, Document, Session, Repository for Document database operations., Update the processing status of a document., The SQL-level mirror of ``DenseRepository._authorization_filter``'s branch…, Return every document ``access`` is authorized to see: owned INDIVIDUAL… (+19 more)

### Community 13 - "Offline Chunking Evaluator"
Cohesion: 0.09
Nodes (44): analyze(), _block_range_valid(), _chunk_body(), _expected_prefix(), _heading_candidates(), _is_content_free(), _list_content_audit(), _looks_like_md_table_row() (+36 more)

### Community 14 - "Whoami API & Team Membership Repository"
Cohesion: 0.11
Nodes (36): get_current_user_profile(), Return the currently authenticated user's profile, including their organisation…, Session, Return the ids of every team the given user is a member of. Selects only the…, Repository for TeamMembership database operations., TeamMembershipRepository, One of the requester's team memberships, as returned by ``GET /users/me``., ``GET /users/me`` response only -- extends ``UserResponse`` with RBAC context… (+28 more)

### Community 15 - "LLM Provider Base & Service"
Cohesion: 0.07
Nodes (23): BaseLLMProvider, ABC, Generate a complete response from the language model., Stream a response from the language model., Base interface for all LLM providers., get_openai_client(), Create and return an OpenAI client. The client is configured using application…, OpenAIProvider (+15 more)

### Community 16 - "Service Dependency Wiring & AI Pipeline Init"
Cohesion: 0.14
Nodes (33): AIPipeline, build_conversation_summary_service(), get_ai_pipeline(), get_auth_service(), get_chat_service(), get_conversation_service(), get_conversation_summary_service(), get_document_service() (+25 more)

### Community 17 - "Citation Generation & Scoring"
Cohesion: 0.10
Nodes (30): BaseGenerationService, ABC, Abstract interface for the Generation layer. Implementations are responsible…, Generate a complete response., Stream the generated response. Each yielded string represents the next chunk of…, EmptyResponseError, Raised when the LLM returns an empty response., Citation (+22 more)

### Community 18 - "Retrieval Formatter & Exceptions"
Cohesion: 0.11
Nodes (24): ContextFormatter, Formats retrieved contexts into different representations suitable for…, Serialize contexts into JSON., slice, SupportsIndex, Return unique section names while preserving retrieval order., Represents a single document chunk after the complete retrieval pipeline…, Final output returned by the RetrievalService. (+16 more)

### Community 19 - "Query Rewrite & Summary Generators"
Cohesion: 0.11
Nodes (23): QueryRewriter, Build the prompt used to rewrite the latest user message into a standalone…, Convert structured conversation messages into a readable prompt format., Responsible for rewriting conversational user queries into standalone search…, Build the prompt used to generate or update the rolling conversation summary., Responsible for building prompts used to generate and maintain a rolling…, SummaryGenerator, Build the prompt used to generate a chat title. (+15 more)

### Community 20 - "Chat Repository & Service"
Cohesion: 0.10
Nodes (21): delete_chat(), delete, Response, Delete a chat session., ChatNotFoundError, Raised when the requested chat session does not exist or is inaccessible., ChatSession, Represents a chat session belonging to a user. (+13 more)

### Community 21 - "Chunk Pipeline Contract Tests"
Cohesion: 0.12
Nodes (35): _distinct(), _list_blocks(), _long(), _merged_section(), A MergeStage-style section chunk: ``blocks`` joined with blank lines…, Q2/Q3: 1 heading + 4 distinct body blocks, 2 pages, forced into several…, A single body block longer than several windows: a middle child holds only its…, Two adjacent blocks that share a verbatim 6-word run at their start. The… (+27 more)

### Community 22 - "AccessContext & Hybrid Search Tests"
Cohesion: 0.15
Nodes (17): Production Retrieval Orchestrator. Pipeline -------- User Query │ ▼ Hybrid…, RetrievalService, HybridService, Production Hybrid Retriever. Responsibilities ---------------- • Generate dense…, OpenAIEmbedder, SparseEncoder, print_results(), GenerationRequest (+9 more)

### Community 23 - "Auth API & User Service"
Cohesion: 0.13
Nodes (26): login(), oauth2_login(), post, Authenticate a user using JSON. Used by the frontend., OAuth2-compatible login endpoint. Swagger sends: username password We interpret…, register(), InactiveUserError, InvalidCredentialsError (+18 more)

### Community 24 - "Storage Service Base"
Cohesion: 0.12
Nodes (27): Return the membership row for one (user, team) pair, if any. Used to resolve…, Return every TeamMembership row for a user, with its Team eagerly loaded in the…, Document, DocumentService, TeamMembership, db(), make_document(), make_organisation() (+19 more)

### Community 25 - "Service Dependency Wiring & AI Pipeline Init"
Cohesion: 0.09
Nodes (29): ConversationService, _individual_branch_user_id(), make_conversation_service(), make_dense_repository_with_fake_client(), _persisted(), Filter, parametrize, Executable specification for RBAC-5B: threading the trusted AccessContext… (+21 more)

### Community 26 - "Message API & Conversation Service"
Cohesion: 0.09
Nodes (28): create_message(), get_messages(), BackgroundTasks, ConversationResponse, MessageCreate, MessageService, Retrieve all messages for a chat session., Send a message and receive the assistant response. (+20 more)

### Community 27 - "Frontend Document Service & Sources"
Cohesion: 0.10
Nodes (22): BinaryIO, DocumentService, Service responsible for all document-related operations., Download the original uploaded document., Retrieve metadata for a single document., Upload one or more documents., Document, Create an authenticated API client. (+14 more)

### Community 28 - "Embedding Batcher & OpenAI Embedder"
Cohesion: 0.11
Nodes (24): Convert raw vectors returned by OpenAI into EmbeddedChunk objects., EmbeddingCacheError, EmbeddingError, EmbeddingRateLimitError, EmbeddingTimeoutError, EmbeddingValidationError, Exception, Custom exceptions for the embeddings module. (+16 more)

### Community 29 - "Offline Chunking Evaluator"
Cohesion: 0.13
Nodes (29): DocumentMetadata, Metadata extracted from a document., _block_from_dict(), _block_to_dict(), compare(), _dig(), extract(), _extraction_from_payload() (+21 more)

### Community 30 - "RBAC SQLAlchemy Models"
Cohesion: 0.15
Nodes (20): Document, Base, TimestampMixin, Represents an uploaded document., SQLAlchemy ORM Models, Organisation, Base, TimestampMixin (+12 more)

### Community 31 - "CrossEncoder Reranker Base"
Cohesion: 0.12
Nodes (18): BaseReranker, ABC, Abstract interface for all rerankers. Every reranker implementation…, Abstract base class for reranking implementations., Returns the underlying reranker model name., Returns the execution device. Example ------- cpu cuda cuda:0 mps, Batch size used for inference., Maximum sequence length accepted by the reranker. (+10 more)

### Community 32 - "Auth Dependency & Base Repository"
Cohesion: 0.09
Nodes (16): BaseRepository, Session, Base repository providing common CRUD operations., Persist a new entity., Retrieve an entity by its primary key., Persist changes made to an existing entity., Session, Retrieve a user by email. (+8 more)

### Community 33 - "Citation & Provenance Tests"
Cohesion: 0.12
Nodes (27): _context(), Provenance propagation: Docling → block → chunk → vector payload → retrieval…, Analogous case with different headings, proving the mechanism is not hardcoded…, Without any structural overlap with the query, citation order must fall back to…, A bare heading chunk is too short to score -- it must come back `None`…, Proves the heading signal is discounted, not disabled: a title that carries a…, _reranked(), test_answer_grounding_keeps_chunks_distinct_and_provenance_intact() (+19 more)

### Community 34 - "CrossEncoder Reranker Implementation"
Cohesion: 0.09
Nodes (15): CrossEncoderReranker, Automatically determine the best available inference device. Priority --------…, Name of the underlying HuggingFace model., Device used for inference., Batch size used during inference., Maximum sequence length accepted by the model., Returns the loaded CrossEncoder instance. This property is primarily useful for…, Validate the user query before inference. (+7 more)

### Community 35 - "AccessContext Dependency & Tests"
Cohesion: 0.12
Nodes (21): ABC, OrgRole, Enum, str, A user's organisation-scoped role. Distinct from document access scope -- role…, AccessContext, Immutable, request-scoped authorization identity. Built exclusively from…, Fail clearly rather than silently accepting an incomplete identity. Required… (+13 more)

### Community 36 - "Exception Hierarchy & App Entrypoint"
Cohesion: 0.11
Nodes (19): get_reranking_resource(), Return the shared reranking service. The underlying CrossEncoder model is…, AuthenticationError, Raised when authentication fails because the access token is invalid, expired,…, AppException, Exception, Initialize the exception. If no message is supplied, use the class-level…, Base exception for all application-specific errors. (+11 more)

### Community 37 - "Semantic Merge Stage Tests"
Cohesion: 0.14
Nodes (19): ChunkingConfig, Single source of truth for the chunking pipeline's size limits. Every value is…, Narrow post-split cleanup. Responsibilities ---------------- - concatenate a…, SemanticStage, BlockProvenance, A compact, parser-neutral reference to the source of one block., _sc(), _sem_chunk() (+11 more)

### Community 38 - "Sparse Encoder & Hybrid Pipeline"
Cohesion: 0.12
Nodes (12): traceable, Generate sparse embedding for a user query., Generates sparse embeddings for document chunks using FastEmbed.…, Generate sparse embeddings for document chunks., SparseEncoder, Represents a sparse vector generated by the sparse encoder. Unlike dense…, Number of non-zero dimensions., Represents a document chunk together with its sparse vector. (+4 more)

### Community 39 - "Dense Search Mapper & Pipeline"
Cohesion: 0.10
Nodes (14): EmbeddedChunk, UUID, Returns the chunk text., Returns the embedding dimensions., Returns the UUIDs of all chunks contained in the batch., Represents a chunk together with its embedding. This object is produced by the…, Returns the chunk UUID., Returns the document UUID. (+6 more)

### Community 40 - "Dense Search Mapper & Pipeline"
Cohesion: 0.13
Nodes (10): DenseMapper, ScoredPoint, Converts between Astra Study domain models and Qdrant models. Responsibilities…, Convert a Qdrant ScoredPoint into a DenseSearchResult., Convert multiple ScoredPoints into DenseSearchResults., DenseSearchResult, Represents one result returned from the dense vector search., DensePipeline (+2 more)

### Community 41 - "Frontend API Client"
Cohesion: 0.15
Nodes (10): ApiClient, ApiException, Any, Exception, Response, Download binary data., Open a Server-Sent Events POST request., Base HTTP client used by all frontend services. (+2 more)

### Community 42 - "AIPipeline Orchestration"
Cohesion: 0.17
Nodes (15): AIResponse, AIPipeline, ChatMessage, StreamEvent, traceable, Stream an assistant response using Retrieval-Augmented Generation., Generate a short AI title for a new conversation., Generate or update the conversation summary. (+7 more)

### Community 43 - "Reranking Exceptions"
Cohesion: 0.13
Nodes (15): Validate retrieval candidates before reranking., CandidateFormatError, EmptyCandidateError, InvalidQueryError, InvalidTopKError, ModelLoadError, PredictionError, Exception (+7 more)

### Community 44 - "Frontend Auth Service & Chat Service"
Cohesion: 0.13
Nodes (12): ChatService, AuthService, ApiClient, Fetch the richer RBAC profile (organisation_id, role, team memberships) for the…, TokenResponse, User, _load_workspace(), login_screen() (+4 more)

### Community 45 - "Frontend Sidebar & State"
Cohesion: 0.16
Nodes (19): main(), _client(), _create_chat(), _load_chat(), Refresh chats and documents., Load a chat and its messages., Upload selected documents., Left navigation panel. (+11 more)

### Community 46 - "Reranking Integration Test"
Cohesion: 0.16
Nodes (22): preview_text(), print_header(), print_hybrid_results(), print_performance(), print_quality_benchmark(), print_rank_movements(), print_reranked_results(), print_reranking_statistics() (+14 more)

### Community 47 - "Dense Search Exceptions"
Cohesion: 0.13
Nodes (21): CollectionAlreadyExistsError, CollectionCreationError, CollectionDeletionError, CollectionNotFoundError, DenseSearchConfigurationError, DenseSearchError, InvalidPayloadError, InvalidSearchQueryError (+13 more)

### Community 48 - "Frontend Chat Service & Workspace"
Cohesion: 0.19
Nodes (12): ChatService, Chat, _active_chat(), _client(), Refresh the sidebar chat list., Return the selected chat., Render workspace heading., Render conversation history. (+4 more)

### Community 49 - "OpenAI Embedder Exceptions"
Cohesion: 0.14
Nodes (14): OpenAIEmbedder, traceable, Execute one embedding request. Retries automatically for transient OpenAI…, Embed a single batch of document chunks. Parameters ---------- chunks A batch…, Embed multiple batches. Parameters ---------- batches List of EmbeddingBatch…, Convenience wrapper. Allows embedder(batches) instead of embedder.embed(batches), Generate an embedding for a user query., Generates OpenAI embeddings for DocumentChunks. Responsibilities… (+6 more)

### Community 50 - "Reranking Result Models"
Cohesion: 0.11
Nodes (12): Allows the reranker instance to be invoked like a function. Example -------…, Rerank retrieved candidates. Parameters ---------- query: User query.…, slice, SupportsIndex, Returns the top-k reranked chunks. Parameters ---------- k: Number of chunks to…, Represents a single reranked retrieval result. Attributes ---------- result:…, Represents the complete output of the reranking stage. Attributes ----------…, Returns the highest ranked chunk. (+4 more)

### Community 51 - "Message API & ConversationService"
Cohesion: 0.17
Nodes (15): ConversationService, BackgroundTasks, ChatMessage, ChatSession, ConversationResponse, MessageCreate, StreamEvent, traceable (+7 more)

### Community 52 - "ConversationService & Memory Tests"
Cohesion: 0.25
Nodes (21): add_messages(), make_chat(), make_summary_service(), ChatSession, Append ``count`` conversational messages with controlled timestamps. Roles…, Pin ``summary_updated_at`` so exactly ``covered_count`` messages count as…, F1: a turn that lands while the summary LLM call is running must not be counted…, set_cursor() (+13 more)

### Community 53 - "Chat API & Document Upload"
Cohesion: 0.16
Nodes (18): create_chat(), get_chat(), list_chats(), get, post, Create a new chat session., Return all chat sessions belonging to the current user., Return a chat session. (+10 more)

### Community 54 - "Embedding Batcher & Dense Pipeline"
Cohesion: 0.19
Nodes (11): EmbeddingBatcher, Splits document chunks into batches suitable for the embedding provider. The…, EmbeddingPipeline, Production embedding pipeline. Pipeline DocumentChunks │ ▼ EmbeddingBatcher │ ▼…, PDFProcessor, Backward-compatible PDF processor. PDF ingestion is now handled by…, EmbeddingPipelineTester, main() (+3 more)

### Community 55 - "AccessContext Dependency & Tests"
Cohesion: 0.22
Nodes (18): Enum, str, A user's role within a single team membership. Independent of ``OrgRole``: a…, TeamRole, db(), make_membership(), make_organisation(), make_team() (+10 more)

### Community 56 - "ConversationService & Memory Tests"
Cohesion: 0.17
Nodes (16): RetrievedContext, db(), _FakeLLM, _FakeRetrieval, make_pipeline(), orm_conversation(), fixture, parametrize (+8 more)

### Community 57 - "Service Dependency Wiring & AI Pipeline Init"
Cohesion: 0.13
Nodes (19): delete_document(), download_document(), get_document(), get_documents(), AccessContext, DocumentResponse, IngestionService, UploadFile (+11 more)

### Community 58 - "Citation & Provenance Tests"
Cohesion: 0.15
Nodes (11): _extract(), FakeBBox, FakeConverter, FakeDocument, FakeItem, FakeProv, test_chunking_preserves_provenance(), test_docx_heading_section_without_page() (+3 more)

### Community 59 - "ConversationService & Memory Tests"
Cohesion: 0.14
Nodes (13): MessageService, ChatRepository, MessageRepository, make_conversation_service(), ChatMessage, F2: an older/slower background refresh finishing after a newer one must not…, _RecordingBackgroundTasks, _StreamingAIPipeline (+5 more)

### Community 60 - "CLAUDE.md Document Authorization Concepts"
Cohesion: 0.16
Nodes (18): AccessContext (app/retrieval/access.py), tests/conftest.py (Qdrant test isolation), Deletion order rationale (Qdrant -> storage -> SQL, non-transactional), DenseRepository (app/repositories), DenseRepository._authorization_filter, app/api/v1/document.py routes, app/exceptions/document.py (TeamNotFoundError, TeamMembershipRequiredError, OrganisationScopeForbiddenError, InvalidAccessScopeError), DocumentRepository (get_visible/get_by_id_visible) (+10 more)

### Community 61 - "Reingest Script RBAC Stamping"
Cohesion: 0.27
Nodes (17): DocumentChunk, Document, Stamp every chunk's metadata from the one authoritative Document row.…, _stamp_rbac_fields(), db(), _embedded(), make_document_like(), _one_chunk() (+9 more)

### Community 62 - "Frontend Message Service & Models"
Cohesion: 0.23
Nodes (7): MessageService, Yield assistant text chunks from the message SSE endpoint., Citation, Conversation, Message, ApiResponse, Standard API response returned by Astra Study.

### Community 63 - "CLAUDE.md Architecture Concepts"
Cohesion: 0.12
Nodes (17): AIPipeline (app/ai/pipeline.py), answer_support scoring, BaseRetrievalService, BlockProvenance (app/document/models.py), Citation model (app/generation/models.py), GenerationService.citations_for, ConversationService (app/services/conversation.py), ConversationSummaryService (update_summary) (+9 more)

### Community 64 - "Qdrant Isolation Conftest & Tests"
Cohesion: 0.16
Nodes (13): _isolate_qdrant_collection(), pytest_collection_modifyitems(), pytest_sessionfinish(), Test-wide Qdrant collection isolation. The integration tests drive…, Record whether this session collected any ``tests/integration`` test., Best-effort drop the dedicated test collection -- and only that collection --…, Pin every test to the dedicated Qdrant collection and return its name. Executed…, Offline safety regression for Qdrant test isolation. Guarantees the test… (+5 more)

### Community 65 - "Filter Stage & Noise Filters"
Cohesion: 0.25
Nodes (13): is_copyright(), is_doi(), is_empty(), is_isbn(), is_numeric_only(), is_page_number(), is_punctuation_only(), is_short_noise() (+5 more)

### Community 66 - "Core Security (JWT/Password)"
Cohesion: 0.16
Nodes (9): Any, Handles password hashing, password verification, and JWT token generation., Decode and validate a JWT., Hash a plain-text password., Verify a password against its hash., Create an access token., Create a refresh token., SecurityManager (+1 more)

### Community 67 - "Retrieval Formatter & Exceptions"
Cohesion: 0.16
Nodes (13): ContextFormattingError, EmptyQueryError, NoRetrievalResultsError, Exception, Raised when no relevant contexts could be retrieved., Base exception for retrieval failures., Raised when the retrieval pipeline is improperly configured., Raised when retrieved contexts cannot be formatted for downstream generation. (+5 more)

### Community 68 - "Hybrid Search Mapper"
Cohesion: 0.31
Nodes (14): HybridMapper, Converts Astra Study domain models into hybrid Qdrant PointStruct objects.…, Build the payload stored alongside every vector inside Qdrant. Payload…, _embedded(), EmbeddedChunk, Executable specification for RBAC-5C: RBAC-aware Qdrant payloads for newly…, DenseMapper is not part of the production indexing path (only…, _rbac_metadata() (+6 more)

### Community 69 - "CLAUDE.md Chunking Contract Notes"
Cohesion: 0.17
Nodes (16): evaluation/chunking_report.py (offline structural evaluator), ChunkingConfig (app/chunking/config.py), ChunkPipeline (app/chunking/pipeline.py), ContentSegment, Determinism requirement (identical ExtractionResult -> byte-identical chunks), evaluation/ (LangSmith harness), EvaluationService._resolve_access, FilterStage (+8 more)

### Community 70 - "CLAUDE.md Ingestion & RBAC Data Model Concepts"
Cohesion: 0.17
Nodes (14): DoclingProcessor (app/ingestion/processors/docling.py), Document model (app/models/document.py), DocumentAccessScope enum (app/enums/document.py), HybridMapper (app/search/hybrid/mapper.py), HybridPipeline (app/search/hybrid/pipeline.py), IngestionService, Organisation model (app/models/organisation.py), ProcessorFactory (app/ingestion/factory.py) (+6 more)

### Community 71 - "Docling Block Handlers"
Cohesion: 0.19
Nodes (9): DocumentConverter, Token, Converts Markdown-It tokens into semantic DocumentBlocks. The converter itself…, Convert Markdown tokens into semantic DocumentBlocks., CodeHandler, Token, Handles fenced code blocks., MarkdownPage (+1 more)

### Community 72 - "Document Validation Models"
Cohesion: 0.20
Nodes (9): DocumentValidator, Validates document-level metadata., Any, One metric produced by a validator., Output returned by every validator. Every validator returns exactly one…, Represents a non-fatal validation issue., ValidationMetric, ValidationResult (+1 more)

### Community 73 - "RBAC-5F Reingest Metadata Test Fixtures"
Cohesion: 0.26
Nodes (14): make_document(), make_organisation(), make_user(), _patch_storage(), _patched_session_local(), Document, DocumentAccessScope, Organisation (+6 more)

### Community 74 - "Embedding Batcher & OpenAI Embedder"
Cohesion: 0.19
Nodes (9): Split chunks into embedding batches., Convenience wrapper allowing the batcher to be called directly., EmbeddingBatchError, Raised when an embedding batch is invalid. Examples: - Empty batch - Batch…, EmbeddingBatch, Represents a batch of chunks sent in a single embedding request., Returns the number of chunks in the batch., Validate an embedding batch before sending it to the embedding provider. (+1 more)

### Community 75 - "Generation Exceptions"
Cohesion: 0.21
Nodes (12): EmptyPromptError, GenerationError, GenerationTimeoutError, InvalidGenerationResponseError, Exception, Exceptions raised by the Generation module., Raised when prompt generation results in no messages., Raised when the configured LLM times out. (+4 more)

### Community 76 - "BaseRetrievalService & Retrieval Tests"
Cohesion: 0.31
Nodes (12): RerankingResult, make_hybrid_result(), make_reranking_result(), make_service(), HybridSearchResult, Graceful empty retrieval (commit b5d8d4b): when every candidate is filtered out…, The other half of graceful empty retrieval: no hybrid candidates at all short-…, test_callable_wrapper() (+4 more)

### Community 77 - "Sparse Search Exceptions"
Cohesion: 0.23
Nodes (11): Exception, Raised when the sparse encoder configuration is invalid., Base exception for all sparse search errors., Raised when a sparse vector collection operation fails., Raised when sparse retrieval fails., Raised when sparse embeddings cannot be generated., SparseCollectionError, SparseConfigurationError (+3 more)

### Community 78 - "Merge/Quality Stage Tests"
Cohesion: 0.31
Nodes (5): FinalizeStage, UUID, Generate a deterministic UUID for every chunk. UUIDs must satisfy: • Stable…, Final stage executed before embeddings. Responsibilities ---------------- •…, Normalize page/block ranges. Pages should always be ascending. Block ranges are…

### Community 79 - "Document API & Ingestion Service"
Cohesion: 0.27
Nodes (9): DocumentAccessScope, DocumentStatus, Enum, str, Who can retrieve/query a document. Separate from ``OrgRole`` / ``TeamRole`` --…, Processing state of a document., DocumentResponse, BaseModel (+1 more)

### Community 80 - "UserService Registration & Default Organisation"
Cohesion: 0.20
Nodes (9): Schema used when a new user registers., UserCreate, Organisation, Register a new user. Every new user is attached to the seeded default…, Resolve the seeded default organisation by its stable slug. Looked up by slug…, BaseModel, test_registration_attaches_default_organisation_and_member_role(), test_registration_fails_clearly_when_default_organisation_is_missing() (+1 more)

### Community 81 - "Sparse Encoder & Hybrid Pipeline"
Cohesion: 0.18
Nodes (3): HybridPipeline, Production Hybrid Indexing Pipeline. Responsibilities ----------------…, Index document chunks using hybrid dense+sparse vectors.

### Community 82 - "PromptBuilder"
Cohesion: 0.24
Nodes (6): PromptBuilder, traceable, Convert retrieved contexts into a formatted block., Build the optional long-term conversation summary., Builds provider-agnostic prompts for the Generation layer. Responsibilities…, Build the complete prompt sent to the LLM.

### Community 83 - "CrossEncoder Reranker Base"
Cohesion: 0.22
Nodes (6): traceable, Callable wrapper. Example ------- >>> result = service( ... query=query, ...…, Public service for document reranking. The service hides the concrete reranker…, Initialize the reranking service. Parameters ---------- reranker: Optional…, Returns the active reranker. The default CrossEncoderReranker is created only…, RerankingService

### Community 84 - "Sparse Encoder & Hybrid Pipeline"
Cohesion: 0.22
Nodes (5): Generate sparse vectors for multiple chunks., Generate a sparse vector for a search query., Convenience wrapper around encode()., Generates sparse embeddings for document chunks. Responsibilities…, SparsePipeline

### Community 85 - "Search Import Isolation Tests"
Cohesion: 0.24
Nodes (9): CompletedProcess, parametrize, Regression test for a circular import discovered during the RBAC-5B independent…, Reproduces the exact import order used by ``scripts/reingest_document.py``…, Run ``code`` in a brand-new Python process with no inherited ``sys.modules``…, Each of these must be importable as the very first thing a fresh process does…, _run_in_fresh_process(), test_reingest_document_script_import_sequence_succeeds_in_fresh_process() (+1 more)

### Community 86 - "Citation & Provenance Tests"
Cohesion: 0.22
Nodes (7): _conversation(), _FakeGeneration, _FakeStreamGen, _pipeline(), test_normal_pipeline_returns_citations(), test_streaming_citations_reflect_the_streamed_answer(), test_streaming_pipeline_emits_citations_after_text()

### Community 87 - "Reingest Test Fake Pipeline Fixtures"
Cohesion: 0.25
Nodes (5): SimpleNamespace, _FakeChunkPipeline, _FakeProcessor, _patch_extraction_and_chunking(), Stand-in for the real (frozen) ChunkPipeline -- these tests exercise RBAC-field…

### Community 88 - "Alembic Env Migration Runner"
Cohesion: 0.25
Nodes (7): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Base, Base class for all SQLAlchemy ORM models., DeclarativeBase

### Community 89 - "API Response Schemas"
Cohesion: 0.36
Nodes (6): success_response(), ApiResponse, ErrorResponse, BaseModel, Standard error API response., Standard success API response.

### Community 90 - "RetrievalService & Integration Tests"
Cohesion: 0.32
Nodes (5): RetrievalResult, traceable, Execute the complete retrieval pipeline. Steps ----- 1. Validate query 2.…, Callable wrapper. Allows RetrievalService to be invoked like a function while…, Convert reranked search results into RetrievedContext objects consumed by…

### Community 91 - "Chat/Message Models & Repositories"
Cohesion: 0.29
Nodes (5): ConversationSummaryService, traceable, Maintains a rolling AI-generated summary for long conversations. Lifecycle…, How many conversational messages the stored summary already reflects., Generate or refresh the conversation summary if it is due. Safe to call after…

### Community 92 - "ConversationService & Memory Tests"
Cohesion: 0.29
Nodes (3): GenerationResponse, GenerationRequest, _RecordingGeneration

### Community 93 - "Health Check Endpoint"
Cohesion: 0.38
Nodes (5): health_check(), get, HealthResponse, BaseModel, Response model for the health check endpoint.

### Community 94 - "Document Parser"
Cohesion: 0.29
Nodes (4): DocumentParser, Token, Parse Markdown into tokens., Parses Markdown into Markdown-It tokens. This class is intentionally…

### Community 95 - "Hybrid Search Mapper"
Cohesion: 0.43
Nodes (5): EmbeddedChunk, PointStruct, Combine dense and sparse representations into a single hybrid Qdrant point., Convert dense and sparse chunk collections into hybrid PointStructs. Both lists…, SparseEmbeddedChunk

### Community 96 - "Storage Service Base"
Cohesion: 0.29
Nodes (4): BaseStorageService, Path, FakeStorageService, In-memory stand-in for LocalStorageService -- no filesystem access, so this…

### Community 97 - "Dense Search Response Model"
Cohesion: 0.33
Nodes (4): DenseSearchResponse, Represents the complete response returned from the dense search pipeline., Number of retrieved results., Highest similarity score.

### Community 98 - "Hybrid Search Mapper"
Cohesion: 0.47
Nodes (4): HybridSearchResult, Convert a Qdrant ScoredPoint into a HybridSearchResult., Convert multiple ScoredPoints into HybridSearchResult objects., ScoredPoint

### Community 99 - "OpenAI Model Enum"
Cohesion: 0.50
Nodes (4): OpenAIModel, Enum, str, Supported OpenAI chat models.

### Community 100 - "Docling Block Handlers"
Cohesion: 0.40
Nodes (3): Token, Returns True if this handler can process the current token., Converts one logical markdown block into a DocumentBlock.

### Community 101 - "Docling Block Handlers"
Cohesion: 0.50
Nodes (3): FormulaHandler, Token, Placeholder for mathematical expressions. Markdown-based parsers commonly emit…

### Community 102 - "Docling Ingestion Processor"
Cohesion: 0.50
Nodes (3): calculate_sha256(), Path, Calculate the SHA-256 checksum of a file.

### Community 103 - "AccessContext & Hybrid Search Tests"
Cohesion: 0.50
Nodes (3): HybridSearchResult, traceable, Execute Hybrid Retrieval.

### Community 104 - "Citation & Provenance Tests"
Cohesion: 0.50
Nodes (5): ChunkMetadata, EmbeddedChunk, _embedded(), parametrize, test_vector_payload_preserves_provenance()

### Community 105 - "CLAUDE.md Project Overview"
Cohesion: 0.40
Nodes (4): alembic/ (migrations), Astra Study, frontend/ (Streamlit UI), scripts/ (operational one-offs)

### Community 114 - "AccessContext & Hybrid Search Tests"
Cohesion: 0.67
Nodes (3): Application settings loaded from environment variables., Settings, BaseSettings

### Community 116 - "APJ Speech Fixture Upload"
Cohesion: 1.00
Nodes (3): A P J Abdul Kalam Departing Speech (upload 510fce33), A P J Abdul Kalam Departing Speech, Developed India 2020

## Knowledge Gaps
- **46 isolated node(s):** `astra-study`, `stage6_LLM.txt (Stage 6 ContentSegment report)`, `stage7_LLM.txt (Stage 7 report)`, `Multi-head attention`, `Scaled dot-product attention` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1003 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DocumentChunk` connect `Merge/Quality Stage Tests` to `Recursive Split & Tokenizer Utils`, `Chunking Tests & Section Utilities`, `Chunk Pipeline & Stages`, `Offline Chunking Evaluator`, `Chunk Pipeline Contract Tests`, `AccessContext & Hybrid Search Tests`, `Embedding Batcher & OpenAI Embedder`, `Offline Chunking Evaluator`, `Semantic Merge Stage Tests`, `Sparse Encoder & Hybrid Pipeline`, `Dense Search Mapper & Pipeline`, `OpenAI Embedder Exceptions`, `Embedding Batcher & Dense Pipeline`, `Filter Stage & Noise Filters`, `Hybrid Search Mapper`, `Document Validation Models`, `Embedding Batcher & OpenAI Embedder`, `Merge/Quality Stage Tests`, `Sparse Encoder & Hybrid Pipeline`, `Sparse Encoder & Hybrid Pipeline`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `SSE streaming protocol` connect `Message API & Conversation Service` to `CLAUDE.md Project Overview`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `AccessContext` connect `AccessContext Dependency & Tests` to `Citation & Provenance Tests`, `RetrievalService & Integration Tests`, `AccessContext & Hybrid Search Tests`, `AI Pipeline & Message Models`, `AIPipeline Orchestration`, `BaseRetrievalService & Retrieval Tests`, `Reranking Integration Test`, `Message API & ConversationService`, `AccessContext & Hybrid Search Tests`, `AccessContext Dependency & Tests`, `ConversationService & Memory Tests`, `Message API & Conversation Service`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `DocumentChunk` (e.g. with `ChunkPipeline` and `BaseChunkStage`) actually correct?**
  _`DocumentChunk` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 88 inferred relationships involving `BlockType` (e.g. with `FilterStage` and `MergeStage`) actually correct?**
  _`BlockType` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `DocumentBlock` (e.g. with `DocumentConverter` and `HandlerResult`) actually correct?**
  _`DocumentBlock` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `AccessContext` (e.g. with `AIPipeline` and `create_message()`) actually correct?**
  _`AccessContext` has 9 INFERRED edges - model-reasoned connections that need verification._