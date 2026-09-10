# Graph Report - Astra-Study  (2026-09-10)

## Corpus Check
- 8 files · ~222,040 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2142 nodes · 5442 edges · 138 communities (87 shown, 17 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 607 edges (avg confidence: 0.94)
- Token cost: 55,894 input · 9,863 output

## Community Hubs (Navigation)
- Offline Chunking Evaluator
- Document Block Handlers
- Chunking Contract Tests
- Chunk Pipeline & Stages
- Recursive Split & Token Utils
- Docling Ingestion Processor
- Conversation Service & Message API
- Dense Qdrant Repository
- Sparse Encoder & Hybrid Models
- Citation & Provenance Tests
- CrossEncoder Reranker
- Query/Summary/Title Generators
- Finalize/Quality Stages & Metrics
- Conversation Memory Tests
- Embedding Batcher & Pipeline Tests
- AIPipeline Orchestration
- Embedding Models & Validator
- Retrieval Formatter & Exceptions
- LLM Service & AI Client
- OpenAI Embedder & Exceptions
- User Repo & Auth Exceptions
- Reranking Base & Hybrid Search
- Frontend Sources & Document API
- Chunking Stage Tests
- Metadata/Merge Stage Tests
- Message & Base Repositories
- Storage Base & Document Repo
- Service DI Wiring
- Chat Repository & Service
- RetrievalResult Model & Tests
- LangSmith Evaluation Harness
- SQLAlchemy Models & Migrations
- Chat API & Schemas
- Reranking Result Model
- Generation Exceptions
- Frontend Workspace & Chat API
- Integration Test Suite
- Retrieval/Rerank Integration Tests
- Dense Search & Settings
- Frontend API Client
- Chunking Stage Tests (2)
- Document Service
- Dense Search Repository (aux)
- Unit Tests (misc)
- Generation Base & Tests
- Document Exception Hierarchy
- Qdrant Isolation Conftest & Tests
- User Service & Exceptions
- Document API & Schemas
- Document Validators & Enums
- CLAUDE.md Project Overview
- Evaluation Artifacts
- Frontend Sidebar & State
- Core Security (JWT/Password)
- CLAUDE.md Citation/Provenance Notes
- Auth API & Schemas
- Input Validation Models
- CLAUDE.md Chunking/Memory Notes
- Test Documents & LLM Fixture
- Health Check Endpoint
- Retrieval Service Unit Tests
- Hybrid Search Pipeline
- Frontend Login & Styles
- Unit Tests (misc 2)
- Sparse Search Models
- Frontend Message API & DTOs
- CLAUDE.md DI Layering Notes
- Frontend Response DTOs
- Prompt Builder
- Evaluation Fixture Schemas
- Local Storage Service
- Frontend Auth API
- Response Schemas
- Hybrid/Dense Search (aux)
- Unit Tests (misc 3)
- User API & Schemas
- Document Parser
- CrossEncoder Reranker (aux)
- Retrieval Service
- CLAUDE.md ContentSegment/Merge Notes
- Dense Search (aux)
- CLAUDE.md Dense Pipeline/Integration Notes
- Test Documents (aux)
- OpenAI AI Client
- AI Models
- Test Documents (aux 2)
- Hybrid Search (aux)
- Evaluation Artifacts
- Test Fixtures
- Ai: Init
- Constants: Document
- Constants: Init
- Generation: Service
- Reranking: Service
- Search: Hybrid
- Test Fixtures
- Evaluation Artifacts
- Evaluation Artifacts
- Evaluation Artifacts
- Evaluation Artifacts
- Evaluation Artifacts
- Evaluation Artifacts
- Evaluation Artifacts
- Pkg

## God Nodes (most connected - your core abstractions)
1. `DocumentChunk` - 138 edges
2. `BlockType` - 119 edges
3. `RetrievalResult` - 65 edges
4. `ChunkPipeline` - 56 edges
5. `DocumentBlock` - 51 edges
6. `User` - 50 edges
7. `AIPipeline` - 48 edges
8. `GenerationService` - 47 edges
9. `GenerationRequest` - 46 edges
10. `count_tokens()` - 45 edges

## Surprising Connections (you probably didn't know these)
- `Transformer architecture` --semantically_similar_to--> `LangGraph`  [INFERRED] [semantically similar]
  tests/test_documents/Attention.pdf → README.md
- `GenerationService` --references--> `LLMService (OpenAI-backed)`  [INFERRED]
  app/generation/service.py → CLAUDE.md
- `HybridPipeline` --implements--> `Qdrant Payload Schema / Mappers`  [EXTRACTED]
  app/search/hybrid/pipeline.py → CLAUDE.md
- `AIPipeline` --references--> `LLM Query Rewriting`  [EXTRACTED]
  app/ai/pipeline.py → CLAUDE.md
- `AIPipeline` --shares_data_with--> `RetrievedContext`  [EXTRACTED]
  app/ai/pipeline.py → CLAUDE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **BERT deep bidirectional pre-training** — tests_test_documents_bert_masked_language_model, tests_test_documents_bert_next_sentence_prediction, tests_test_documents_bert_bidirectional_pretraining, tests_test_documents_bert_fine_tuning [EXTRACTED 0.75]
- **Offline chunking evaluation harness** — claude_chunking_report, evaluation_artifacts_readme_frozen_blocks, evaluation_artifacts_comparison, claude_chunking_determinism [EXTRACTED 0.75]
- **RAG paradigm progression** — tests_test_documents_rag_retrieval_augmented_generation, tests_test_documents_rag_naive_rag, tests_test_documents_rag_advanced_rag, tests_test_documents_rag_modular_rag [EXTRACTED 0.75]
- **Transformer built from attention components** — tests_test_documents_attention_transformer, tests_test_documents_attention_self_attention, tests_test_documents_attention_scaled_dot_product_attention, tests_test_documents_attention_multi_head_attention, tests_test_documents_attention_positional_encoding [EXTRACTED 0.75]
- **ChunkPipeline 8-stage ordered flow** — claude_paragraph_stage, claude_metadata_stage, claude_merge_stage, claude_recursive_stage, claude_semantic_stage, claude_filter_stage, claude_quality_stage, claude_finalize_stage [EXTRACTED 1.00]
- **Ingestion flow: upload to Qdrant vectors** — claude_ingestion_service, claude_docling_processor, app_chunking_pipeline_chunkpipeline, app_search_hybrid_pipeline_hybridpipeline, claude_qdrant [EXTRACTED 1.00]
- **Retrieval + generation pipeline** — app_ai_pipeline_aipipeline, claude_query_rewrite, app_retrieval_service_retrievalservice, claude_reranking_service, app_generation_service_generationservice, claude_citations_for [EXTRACTED 1.00]

## Communities (138 total, 17 thin omitted)

### Community 0 - "Offline Chunking Evaluator"
Cohesion: 0.06
Nodes (81): is_copyright(), is_doi(), is_empty(), is_isbn(), is_numeric_only(), is_page_number(), is_punctuation_only(), is_short_noise() (+73 more)

### Community 1 - "Document Block Handlers"
Cohesion: 0.07
Nodes (48): DocumentConverter, Token, Converts Markdown-It tokens into semantic DocumentBlocks. The converter itself…, Convert Markdown tokens into semantic DocumentBlocks., BaseHandler, HandlerResult, ABC, Token (+40 more)

### Community 2 - "Chunking Contract Tests"
Cohesion: 0.10
Nodes (66): count_tokens(), Count the number of tokens in text., BlockType, Represents the semantic type of a document block. This enum is parser-…, StrEnum, _distinct(), _list_blocks(), _long() (+58 more)

### Community 3 - "Chunk Pipeline & Stages"
Cohesion: 0.07
Nodes (40): ChunkingConfig, Single source of truth for the chunking pipeline's size limits. Every value is…, ChunkPipeline, Executes the configured chunking stages., BaseChunkStage, ABC, Process the incoming data and return chunks., Base interface for every chunking stage. (+32 more)

### Community 4 - "Recursive Split & Token Utils"
Cohesion: 0.06
Nodes (40): _is_markdown_separator(), _norm(), Compact heading context: the deepest heading normally, or the deepest two…, Recover the source segments (one per contributing block) from the merged chunk…, The text a pass-through chunk would carry with ``prefix`` present exactly once.…, A markdown table separator row, e.g. ``| --- | :--: |``., Text of each child (before the heading prefix), plus -- for the structural…, Pack whole list items into child bodies, never dividing one. A single item… (+32 more)

### Community 5 - "Docling Ingestion Processor"
Cohesion: 0.06
Nodes (35): BaseProcessor, ABC, Path, Extract structured information from a document., Base class for every document processor., ProcessorFactory, Path, Returns the correct processor for a document. (+27 more)

### Community 6 - "Conversation Service & Message API"
Cohesion: 0.10
Nodes (33): create_message(), get_messages(), BackgroundTasks, get, post, Retrieve all messages for a chat session., Send a message and receive the assistant response., Stream an assistant response using Server-Sent Events (SSE). (+25 more)

### Community 7 - "Dense Qdrant Repository"
Cohesion: 0.07
Nodes (33): CollectionAlreadyExistsError, CollectionCreationError, CollectionDeletionError, CollectionNotFoundError, DenseSearchConfigurationError, DenseSearchError, InvalidPayloadError, InvalidSearchQueryError (+25 more)

### Community 8 - "Sparse Encoder & Hybrid Models"
Cohesion: 0.07
Nodes (23): HybridMapper, PointStruct, Combine dense and sparse representations into a single hybrid Qdrant point., Converts Astra Study domain models into hybrid Qdrant PointStruct objects.…, Convert dense and sparse chunk collections into hybrid PointStructs. Both lists…, Build the payload stored alongside every vector inside Qdrant. Payload…, traceable, Generate sparse embedding for a user query. (+15 more)

### Community 9 - "Citation & Provenance Tests"
Cohesion: 0.14
Nodes (40): GenerationRequest, Input required by the Prompt Builder and Generation layer., _answer_support(), GenerationService, _query_term_weights(), Deterministic answer/evidence alignment signal: the fraction of the chunk's own…, Production implementation of the Generation layer. Responsibilities…, Generate a complete assistant response. (+32 more)

### Community 10 - "CrossEncoder Reranker"
Cohesion: 0.08
Nodes (26): CrossEncoderReranker, Cross Encoder based reranker implementation. This module implements the…, Name of the underlying HuggingFace model., Device used for inference., Batch size used during inference., Maximum sequence length accepted by the model., Validate the user query before inference., Validate the requested top_k value. (+18 more)

### Community 11 - "Query/Summary/Title Generators"
Cohesion: 0.12
Nodes (25): QueryRewriter, Build the prompt used to rewrite the latest user message into a standalone…, Convert structured conversation messages into a readable prompt format., Responsible for rewriting conversational user queries into standalone search…, AIResponse, Response returned by the AI orchestration layer. This model is intentionally…, Build the prompt used to generate or update the rolling conversation summary., Responsible for building prompts used to generate and maintain a rolling… (+17 more)

### Community 12 - "Finalize/Quality Stages & Metrics"
Cohesion: 0.08
Nodes (34): ContentSegment, DocumentChunk, One source ``DocumentBlock`` that ``MergeStage`` folded into a chunk. Internal…, Represents one chunk that will eventually be embedded and stored in the vector…, One ContentSegment for a source block as it enters MergeStage (each chunk is…, Emit ``builder`` -- unless it only ever held a heading (or nothing), in which…, Start a new section chunk. Every metadata field is preserved by deep-copying…, Decide whether ``incoming`` starts a new section chunk. (+26 more)

### Community 13 - "Conversation Memory Tests"
Cohesion: 0.14
Nodes (33): add_messages(), FakeSummaryPipeline, make_chat(), make_conversation_service(), make_summary_service(), Executable specification for the rolling conversation-memory behaviour…, Pin ``summary_updated_at`` so exactly ``covered_count`` messages count as…, Stands in for AIPipeline in the summary service (only generate_summary). (+25 more)

### Community 14 - "Embedding Batcher & Pipeline Tests"
Cohesion: 0.10
Nodes (22): EmbeddingBatcher, Splits document chunks into batches suitable for the embedding provider. The…, Split chunks into embedding batches., Convenience wrapper allowing the batcher to be called directly., EmbeddingBatchError, Raised when an embedding batch is invalid. Examples: - Empty batch - Batch…, EmbeddingBatch, Represents a batch of chunks sent in a single embedding request. (+14 more)

### Community 15 - "AIPipeline Orchestration"
Cohesion: 0.10
Nodes (23): AIPipeline, traceable, Stream an assistant response using Retrieval-Augmented Generation., Generate a short AI title for a new conversation., Generate or update the conversation summary., Build the query used for document retrieval. Conversational follow-up questions…, Production AI orchestration layer. Responsibilities ---------------- - Convert…, Select the conversation messages sent verbatim to the answer LLM. Before… (+15 more)

### Community 16 - "Embedding Models & Validator"
Cohesion: 0.09
Nodes (25): Convert raw vectors returned by OpenAI into EmbeddedChunk objects., EmbeddingValidationError, Raised when an embedding fails validation. Examples: - Empty embedding -…, EmbeddedChunk, EmbeddingMetadata, EmbeddingVector, UUID, Returns the chunk text. (+17 more)

### Community 17 - "Retrieval Formatter & Exceptions"
Cohesion: 0.09
Nodes (25): BaseRetrievalService, ABC, Execute the complete retrieval pipeline. Retrieval is keyword-only and always…, Allow the service to be invoked like a function., Base contract for all retrieval implementations., ContextFormattingError, NoRetrievalResultsError, Exception (+17 more)

### Community 18 - "LLM Service & AI Client"
Cohesion: 0.09
Nodes (18): BaseLLMProvider, ABC, Generate a complete response from the language model., Stream a response from the language model., Base interface for all LLM providers., OpenAIProvider, OpenAI implementation of the LLM provider., Generate a complete response using OpenAI. (+10 more)

### Community 19 - "OpenAI Embedder & Exceptions"
Cohesion: 0.10
Nodes (24): OpenAIEmbedder, traceable, Execute one embedding request. Retries automatically for transient OpenAI…, Embed a single batch of document chunks. Parameters ---------- chunks A batch…, Embed multiple batches. Parameters ---------- batches List of EmbeddingBatch…, Convenience wrapper. Allows embedder(batches) instead of embedder.embed(batches), Generate an embedding for a user query., Generates OpenAI embeddings for DocumentChunks. Responsibilities… (+16 more)

### Community 20 - "User Repo & Auth Exceptions"
Cohesion: 0.10
Nodes (22): get_current_user(), Session, Return the currently authenticated user., get_auth_service(), AuthService, AuthenticationError, InactiveUserError, InvalidCredentialsError (+14 more)

### Community 21 - "Reranking Base & Hybrid Search"
Cohesion: 0.09
Nodes (19): BaseReranker, ABC, Abstract interface for all rerankers. Every reranker implementation…, Allows the reranker instance to be invoked like a function. Example -------…, Abstract base class for reranking implementations., Returns the underlying reranker model name., Returns the execution device. Example ------- cpu cuda cuda:0 mps, Batch size used for inference. (+11 more)

### Community 22 - "Frontend Sources & Document API"
Cohesion: 0.10
Nodes (21): Retrieve all uploaded documents., BinaryIO, DocumentService, Service responsible for all document-related operations., Download the original uploaded document., Retrieve metadata for a single document., Upload one or more documents., Document (+13 more)

### Community 23 - "Chunking Stage Tests"
Cohesion: 0.15
Nodes (31): True when ``inner`` names the same section as ``outer`` or a subsection nested…, section_contains(), _body(), _chunk(), _heading(), _merge(), _mk(), _prov() (+23 more)

### Community 24 - "Metadata/Merge Stage Tests"
Cohesion: 0.11
Nodes (21): ChunkMetadata, Metadata associated with a document chunk. This metadata flows through the…, FinalizeStage, UUID, Generate a deterministic UUID for every chunk. UUIDs must satisfy: • Stable…, Final stage executed before embeddings. Responsibilities ---------------- •…, Normalize page/block ranges. Pages should always be ascending. Block ranges are…, QualityStage (+13 more)

### Community 25 - "Message & Base Repositories"
Cohesion: 0.08
Nodes (16): BaseRepository, Session, Base repository providing common CRUD operations., Persist a new entity., Retrieve an entity by its primary key., Persist changes made to an existing entity., MessageRepository, datetime (+8 more)

### Community 26 - "Storage Base & Document Repo"
Cohesion: 0.11
Nodes (18): get_document_service(), get_ingestion_service(), DocumentService, DocumentRepository, Session, Repository for Document database operations., Return all documents belonging to a user., Return a document only if it belongs to the specified user. (+10 more)

### Community 27 - "Service DI Wiring"
Cohesion: 0.16
Nodes (26): get_db(), Session, Creates a new database session for each request and ensures it is closed after…, get_llm_resource(), get_reranking_resource(), Return the shared LLM service., Return the shared reranking service. The underlying CrossEncoder model is…, build_conversation_summary_service() (+18 more)

### Community 28 - "Chat Repository & Service"
Cohesion: 0.13
Nodes (15): ChatNotFoundError, Raised when the requested chat session does not exist or is inaccessible., ChatSession, Represents a chat session belonging to a user., ChatRepository, datetime, Session, Repository for ChatSession database operations. (+7 more)

### Community 29 - "RetrievalResult Model & Tests"
Cohesion: 0.14
Nodes (18): slice, SupportsIndex, Return unique section names while preserving retrieval order., Represents a single document chunk after the complete retrieval pipeline…, Final output returned by the RetrievalService., Return unique document sources while preserving retrieval order., RetrievalResult, RetrievedContext (+10 more)

### Community 30 - "LangSmith Evaluation Harness"
Cohesion: 0.12
Nodes (16): answer_length(), citation_count(), exact_match(), Any, Exact answer match. Useful as a fast deterministic baseline., Records answer length. Helpful for spotting prompt regressions., Counts returned citations., FixtureManager (+8 more)

### Community 31 - "SQLAlchemy Models & Migrations"
Cohesion: 0.17
Nodes (16): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Base, Base class for all SQLAlchemy ORM models., Document, Represents an uploaded document. (+8 more)

### Community 32 - "Chat API & Schemas"
Cohesion: 0.13
Nodes (22): create_chat(), delete_chat(), get_chat(), list_chats(), delete, get, post, Response (+14 more)

### Community 33 - "Reranking Result Model"
Cohesion: 0.10
Nodes (14): Rerank retrieved candidates. Parameters ---------- query: User query.…, Combine retrieval results with reranker scores and sort them in descending…, slice, SupportsIndex, Returns the top-k reranked chunks. Parameters ---------- k: Number of chunks to…, Represents a single reranked retrieval result. Attributes ---------- result:…, Represents the complete output of the reranking stage. Attributes ----------…, Returns the highest ranked chunk. (+6 more)

### Community 34 - "Generation Exceptions"
Cohesion: 0.12
Nodes (19): EmptyPromptError, EmptyResponseError, GenerationError, GenerationTimeoutError, InvalidGenerationResponseError, Exception, Exceptions raised by the Generation module., Raised when prompt generation results in no messages. (+11 more)

### Community 35 - "Frontend Workspace & Chat API"
Cohesion: 0.18
Nodes (13): ChatService, Chat, Citation, _active_chat(), _client(), Refresh the sidebar chat list., Return the selected chat., Render workspace heading. (+5 more)

### Community 36 - "Integration Test Suite"
Cohesion: 0.16
Nodes (22): preview_text(), print_header(), print_hybrid_results(), print_performance(), print_quality_benchmark(), print_rank_movements(), print_reranked_results(), print_reranking_statistics() (+14 more)

### Community 37 - "Retrieval/Rerank Integration Tests"
Cohesion: 0.16
Nodes (13): Public service for document reranking. The service hides the concrete reranker…, RerankingService, Production Retrieval Orchestrator. Pipeline -------- User Query │ ▼ Hybrid…, RetrievalService, HybridService, Production Hybrid Retriever. Responsibilities ---------------- • Generate dense…, GenerationRequest, print_results() (+5 more)

### Community 38 - "Dense Search & Settings"
Cohesion: 0.16
Nodes (13): Application settings loaded from environment variables., Settings, DenseMapper, ScoredPoint, Converts between Astra Study domain models and Qdrant models. Responsibilities…, Convert a Qdrant ScoredPoint into a DenseSearchResult., Convert multiple ScoredPoints into DenseSearchResults., DenseSearchResult (+5 more)

### Community 39 - "Frontend API Client"
Cohesion: 0.16
Nodes (7): ApiClient, Any, Response, Download binary data., Open a Server-Sent Events POST request., Base HTTP client used by all frontend services., Execute an HTTP request.

### Community 40 - "Chunking Stage Tests (2)"
Cohesion: 0.19
Nodes (16): Narrow post-split cleanup. Responsibilities ---------------- - concatenate a…, SemanticStage, BlockProvenance, A compact, parser-neutral reference to the source of one block., _sc(), _sem_chunk(), test_semantic_caption_owns_following_text_still_works(), test_semantic_merge_deduplicates_shared_provenance() (+8 more)

### Community 41 - "Document Service"
Cohesion: 0.12
Nodes (14): delete_document(), delete, Response, DocumentNotFoundError, Raised when a requested document does not exist or does not belong to the…, DocumentService, Document, Path (+6 more)

### Community 42 - "Dense Search Repository (aux)"
Cohesion: 0.11
Nodes (7): PointStruct, Convert multiple EmbeddedChunks into PointStructs., Convert one EmbeddedChunk into a Qdrant PointStruct., DensePipeline, Production dense search pipeline. Responsibilities ----------------…, Execute dense vector similarity search., Index embedded chunks into Qdrant.

### Community 43 - "Unit Tests (misc)"
Cohesion: 0.15
Nodes (11): _extract(), FakeBBox, FakeConverter, FakeDocument, FakeItem, FakeProv, test_chunking_preserves_provenance(), test_docx_heading_section_without_page() (+3 more)

### Community 44 - "Generation Base & Tests"
Cohesion: 0.14
Nodes (9): BaseGenerationService, ABC, Abstract interface for the Generation layer. Implementations are responsible…, Generate a complete response., Stream the generated response. Each yielded string represents the next chunk of…, GenerationResponse, Structured response produced by the Generation layer., _RecordingGeneration (+1 more)

### Community 45 - "Document Exception Hierarchy"
Cohesion: 0.17
Nodes (13): AppException, Exception, Initialize the exception. If no message is supplied, use the class-level…, Base exception for all application-specific errors., DocumentTooLargeError, EmptyDocumentError, InvalidDocumentTypeError, Raised when an empty document is uploaded. (+5 more)

### Community 46 - "Qdrant Isolation Conftest & Tests"
Cohesion: 0.16
Nodes (13): _isolate_qdrant_collection(), pytest_collection_modifyitems(), pytest_sessionfinish(), Test-wide Qdrant collection isolation. The integration tests drive…, Record whether this session collected any ``tests/integration`` test., Best-effort drop the dedicated test collection -- and only that collection --…, Pin every test to the dedicated Qdrant collection and return its name. Executed…, Offline safety regression for Qdrant test isolation. Guarantees the test… (+5 more)

### Community 47 - "User Service & Exceptions"
Cohesion: 0.24
Nodes (10): register(), EmailAlreadyExistsError, Raised when a username is already taken., Raised when an email is already registered., UsernameAlreadyExistsError, Schema used when a new user registers., UserCreate, User (+2 more)

### Community 48 - "Document API & Schemas"
Cohesion: 0.13
Nodes (15): download_document(), get_document(), get_documents(), BackgroundTasks, get, post, UploadFile, Retrieve a single document. (+7 more)

### Community 49 - "Document Validators & Enums"
Cohesion: 0.18
Nodes (9): DocumentStatus, Enum, str, Processing state of a document., Update the processing status of a document., DocumentValidator, UploadFile, Validates uploaded documents before they are stored on disk. (+1 more)

### Community 50 - "CLAUDE.md Project Overview"
Cohesion: 0.15
Nodes (16): Astra Study, Evaluation Harness (evaluation/), evaluation.runner (LangSmith experiment runner), FastAPI Backend (app/), LangSmith Tracing, Observability, Retrieval-Augmented Generation (RAG), Streamlit Frontend (frontend/) (+8 more)

### Community 51 - "Evaluation Artifacts"
Cohesion: 0.14
Nodes (15): Chunking Determinism Requirement, chunking_report.py (offline structural evaluator), baseline_apjspeech.txt (commit 888fc8c report), baseline_Attention.txt (commit 888fc8c report), baseline_LLM.txt (commit 888fc8c report), comparison.txt (baseline vs stage14 deltas), comparison_stage5_to_stage6.txt (Stage 6 primary comparison), apjspeech.pdf (eval corpus doc) (+7 more)

### Community 52 - "Frontend Sidebar & State"
Cohesion: 0.23
Nodes (14): _client(), _create_chat(), _load_chat(), Refresh chats and documents., Load a chat and its messages., Upload selected documents., Left navigation panel., _refresh_workspace() (+6 more)

### Community 53 - "Core Security (JWT/Password)"
Cohesion: 0.15
Nodes (8): Any, Handles password hashing, password verification, and JWT token generation., Decode and validate a JWT., Hash a plain-text password., Verify a password against its hash., Create an access token., Create a refresh token., SecurityManager

### Community 54 - "CLAUDE.md Citation/Provenance Notes"
Cohesion: 0.14
Nodes (15): BlockProvenance, Citation Model (frozen dataclass), Deterministic Citation Ordering, GenerationService.citations_for (single source of truth), Process-wide ML Singletons (dependencies/resources.py), LLMService (OpenAI-backed), Missing Metadata Stays Null, Provenance Data Flow (end to end) (+7 more)

### Community 55 - "Auth API & Schemas"
Cohesion: 0.18
Nodes (13): login(), oauth2_login(), post, Authenticate a user using JSON. Used by the frontend., OAuth2-compatible login endpoint. Swagger sends: username password We interpret…, BaseModel, Response returned after successful authentication., Request schema for refreshing an access token. (+5 more)

### Community 56 - "Input Validation Models"
Cohesion: 0.20
Nodes (9): DocumentValidator, Validates document-level metadata., Any, One metric produced by a validator., Output returned by every validator. Every validator returns exactly one…, Represents a non-fatal validation issue., ValidationMetric, ValidationResult (+1 more)

### Community 57 - "CLAUDE.md Chunking/Memory Notes"
Cohesion: 0.14
Nodes (14): Chunking Pipeline Contract (frozen), Conversation Memory (rolling summary + recent window), DoclingProcessor, DocumentBlock / ExtractionResult, Ingestion Pipeline (upload to vectors), IngestionService, Memory Tuning Constants (settings.py), MessageRepository (conversational message counting) (+6 more)

### Community 58 - "Test Documents & LLM Fixture"
Cohesion: 0.21
Nodes (14): Astra Study Evaluation Dataset (LLM fundamentals), Emergent Abilities in LLMs, In-Context Learning, LangSmith Evaluation Runner (evaluation.runner), Attention Is All You Need (upload 005042b4), A Comprehensive Overview of Large Language Models (upload 3c7e729d), LLM fine-tuning and training strategies, Attention Is All You Need (+6 more)

### Community 59 - "Health Check Endpoint"
Cohesion: 0.19
Nodes (9): health_check(), get, lifespan(), FastAPI, get, root(), HealthResponse, BaseModel (+1 more)

### Community 60 - "Retrieval Service Unit Tests"
Cohesion: 0.29
Nodes (12): EmptyQueryError, Raised when the supplied query is empty., make_hybrid_result(), make_reranking_result(), make_service(), Graceful empty retrieval (commit b5d8d4b): when every candidate is filtered out…, The other half of graceful empty retrieval: no hybrid candidates at all short-…, test_callable_wrapper() (+4 more)

### Community 61 - "Hybrid Search Pipeline"
Cohesion: 0.17
Nodes (5): HybridPipeline, Production Hybrid Indexing Pipeline. Responsibilities ----------------…, Index document chunks using hybrid dense+sparse vectors., Dense Vector (OpenAI embeddings), Sparse Vector

### Community 62 - "Frontend Login & Styles"
Cohesion: 0.22
Nodes (11): main(), _load_workspace(), login_screen(), Load chats and documents immediately after login., Render the login / registration page., Render the right-side panel., sources_panel(), initialize_session_state() (+3 more)

### Community 63 - "Unit Tests (misc 2)"
Cohesion: 0.22
Nodes (11): _FakeLLM, make_pipeline(), orm_conversation(), parametrize, A pending/failed first summary must not trigger history truncation., test_full_history_used_before_first_summary(), test_generation_context_is_summary_plus_rolling_window(), test_generation_history_bounded_for_very_long_conversation() (+3 more)

### Community 64 - "Sparse Search Models"
Cohesion: 0.23
Nodes (11): Exception, Raised when the sparse encoder configuration is invalid., Base exception for all sparse search errors., Raised when a sparse vector collection operation fails., Raised when sparse retrieval fails., Raised when sparse embeddings cannot be generated., SparseCollectionError, SparseConfigurationError (+3 more)

### Community 65 - "Frontend Message API & DTOs"
Cohesion: 0.35
Nodes (4): MessageService, Yield assistant text chunks from the message SSE endpoint., Conversation, Message

### Community 66 - "CLAUDE.md DI Layering Notes"
Cohesion: 0.20
Nodes (11): API Routers (app/api/v1), get_current_user (OAuth2 + JWT auth), ConversationService, Request/DI Layering, Local Filesystem Storage (storage/), Persistence Layer, PostgreSQL (SQLAlchemy 2.0 + Alembic), Repositories Layer (app/repositories) (+3 more)

### Community 67 - "Frontend Response DTOs"
Cohesion: 0.33
Nodes (4): TokenResponse, ApiResponse, Standard API response returned by Astra Study., User

### Community 68 - "Prompt Builder"
Cohesion: 0.24
Nodes (6): PromptBuilder, traceable, Convert retrieved contexts into a formatted block., Build the optional long-term conversation summary., Builds provider-agnostic prompts for the Generation layer. Responsibilities…, Build the complete prompt sent to the LLM.

### Community 69 - "Evaluation Fixture Schemas"
Cohesion: 0.29
Nodes (6): Load a single evaluation fixture. Parameters ---------- filename YAML filename.…, EvaluationExample, EvaluationFixture, BaseModel, Represents an evaluation fixture., Represents a single evaluation example stored inside a fixture.

### Community 70 - "Local Storage Service"
Cohesion: 0.22
Nodes (5): Path, Return the absolute path of a stored file., Path, UploadFile, Save an uploaded file.

### Community 71 - "Frontend Auth API"
Cohesion: 0.39
Nodes (4): ApiException, Exception, Raised when the backend returns an error response., AuthService

### Community 72 - "Response Schemas"
Cohesion: 0.36
Nodes (6): success_response(), ApiResponse, ErrorResponse, BaseModel, Standard error API response., Standard success API response.

### Community 73 - "Hybrid/Dense Search (aux)"
Cohesion: 0.29
Nodes (5): traceable, Execute native Qdrant Hybrid Search using Reciprocal Rank Fusion (RRF).…, ScoredPoint, Convert a Qdrant ScoredPoint into a HybridSearchResult., Convert multiple ScoredPoints into HybridSearchResult objects.

### Community 74 - "Unit Tests (misc 3)"
Cohesion: 0.29
Nodes (6): _conversation(), _FakeStreamGen, _pipeline(), test_normal_pipeline_returns_citations(), test_streaming_citations_reflect_the_streamed_answer(), test_streaming_pipeline_emits_citations_after_text()

### Community 75 - "User API & Schemas"
Cohesion: 0.33
Nodes (6): get_current_user_profile(), get, Return the currently authenticated user's profile., BaseModel, Schema returned after a successful registration., UserResponse

### Community 76 - "Document Parser"
Cohesion: 0.29
Nodes (4): DocumentParser, Token, Parse Markdown into tokens., Parses Markdown into Markdown-It tokens. This class is intentionally…

### Community 77 - "CrossEncoder Reranker (aux)"
Cohesion: 0.29
Nodes (4): Automatically determine the best available inference device. Priority --------…, Returns the loaded CrossEncoder instance. This property is primarily useful for…, Initialize the reranker. Parameters ---------- model_name: HuggingFace model…, CrossEncoder

### Community 78 - "Retrieval Service"
Cohesion: 0.33
Nodes (4): traceable, Execute the complete retrieval pipeline. Steps ----- 1. Validate query 2.…, Callable wrapper. Allows RetrievalService to be invoked like a function while…, Convert reranked search results into RetrievedContext objects consumed by…

### Community 79 - "CLAUDE.md ContentSegment/Merge Notes"
Cohesion: 0.38
Nodes (7): ContentSegment, MergeStage, MetadataStage, ParagraphStage, RecursiveStage, Internal section_key, Structural Atomicity Metrics (table rows / list items split across chunks)

### Community 80 - "Dense Search (aux)"
Cohesion: 0.33
Nodes (4): DenseSearchResponse, Represents the complete response returned from the dense search pipeline., Number of retrieved results., Highest similarity score.

### Community 81 - "CLAUDE.md Dense Pipeline/Integration Notes"
Cohesion: 0.47
Nodes (6): DensePipeline / DenseRepository, tests/integration (live services), Qdrant Vector Store, Qdrant Integration Test Hazard (recreate_collection), Qdrant Test Isolation Mechanism, docker-compose.yml (empty placeholder)

### Community 82 - "Test Documents (aux)"
Cohesion: 0.40
Nodes (6): Retrieval-Augmented Generation for LLMs: A Survey, Advanced RAG, LLM hallucination, Modular RAG, Naive RAG, Retrieval-Augmented Generation

### Community 83 - "OpenAI AI Client"
Cohesion: 0.50
Nodes (3): get_openai_client(), Create and return an OpenAI client. The client is configured using application…, OpenAI

### Community 84 - "AI Models"
Cohesion: 0.50
Nodes (4): OpenAIModel, Enum, str, Supported OpenAI chat models.

### Community 85 - "Test Documents (aux 2)"
Cohesion: 0.50
Nodes (5): BERT: Pre-training of Deep Bidirectional Transformers, Deep bidirectional pre-training, Fine-tuning for downstream tasks, Masked language model (MLM), Next sentence prediction (NSP)

### Community 93 - "Test Fixtures"
Cohesion: 1.00
Nodes (3): A P J Abdul Kalam Departing Speech (upload 510fce33), A P J Abdul Kalam Departing Speech, Developed India 2020

## Knowledge Gaps
- **37 isolated node(s):** `astra-study`, `pre_apjspeech.txt (pre-refactor report)`, `pre_LLM.txt (pre-refactor report)`, `stage14_apjspeech.txt (Stage 5 frozen tree report)`, `stage14_LLM.txt (Stage 5 frozen tree report)` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 770 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DocumentChunk` connect `Finalize/Quality Stages & Metrics` to `Offline Chunking Evaluator`, `Chunking Contract Tests`, `Chunk Pipeline & Stages`, `Recursive Split & Token Utils`, `Chunking Stage Tests (2)`, `Sparse Encoder & Hybrid Models`, `Citation & Provenance Tests`, `Embedding Batcher & Pipeline Tests`, `Embedding Models & Validator`, `OpenAI Embedder & Exceptions`, `Chunking Stage Tests`, `Metadata/Merge Stage Tests`, `Input Validation Models`, `Hybrid Search Pipeline`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Why does `ChunkPipeline` connect `Chunk Pipeline & Stages` to `Offline Chunking Evaluator`, `Chunking Contract Tests`, `Recursive Split & Token Utils`, `Docling Ingestion Processor`, `Chunking Stage Tests (2)`, `Citation & Provenance Tests`, `Unit Tests (misc)`, `Finalize/Quality Stages & Metrics`, `Embedding Batcher & Pipeline Tests`, `CLAUDE.md ContentSegment/Merge Notes`, `Evaluation Artifacts`, `Metadata/Merge Stage Tests`, `CLAUDE.md Chunking/Memory Notes`, `Storage Base & Document Repo`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `get_documents()` connect `Document API & Schemas` to `Document Service`, `Storage Base & Document Repo`, `Frontend Sources & Document API`, `SQLAlchemy Models & Migrations`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `DocumentChunk` (e.g. with `ChunkPipeline` and `BaseChunkStage`) actually correct?**
  _`DocumentChunk` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 92 inferred relationships involving `BlockType` (e.g. with `ChunkMetadata` and `ContentSegment`) actually correct?**
  _`BlockType` has 92 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `RetrievalResult` (e.g. with `GenerationRequest` and `BaseRetrievalService`) actually correct?**
  _`RetrievalResult` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ChunkPipeline` (e.g. with `DocumentChunk` and `BaseChunkStage`) actually correct?**
  _`ChunkPipeline` has 14 INFERRED edges - model-reasoned connections that need verification._