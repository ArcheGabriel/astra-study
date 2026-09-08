# Graph Report - Astra-Study  (2026-09-08)

## Corpus Check
- 287 files · ~220,790 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2113 nodes · 5402 edges · 135 communities (85 shown, 16 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 616 edges (avg confidence: 0.94)
- Token cost: 142,483 input · 25,144 output

## Community Hubs (Navigation)
- Document Block Handlers
- Offline Chunking Evaluator
- Recursive Split & Token Utils
- Chunk Pipeline & Stages
- Document API & Ingestion Service
- CrossEncoder Reranker
- Docling Ingestion Processor
- Finalize/Quality Stages & Metrics
- Dense Qdrant Repository
- Dense Search Pipeline & Mapper
- Reranking Base & Models
- Conversation Memory Tests
- Chunking Contract Tests
- Query/Summary/Title Generators
- Message API & Service
- Service DI Wiring & Local Storage
- Citation Ordering & Provenance Tests
- Chat API & Service
- OpenAI Embedder
- Sparse Encoder & Pipeline
- Hybrid Indexing Integration Tests
- LangSmith Evaluation Harness
- LLM Service & Prompt Builder
- Retrieval Base Contract & Tests
- SQLAlchemy Models & Migration Env
- Conversation Service & Message Repo
- Base Repository & Auth Dependency
- RetrievalResult Model & Tests
- Chunking Stage Tests
- Retrieval/Rerank Integration Tests
- Auth & User Schemas
- Embedding Models & Batcher
- Chunking Utils Tests
- Research Paper Corpus (PDFs)
- Chunking Provenance Audit Tests
- AIPipeline Orchestration
- Frontend Sidebar & State
- Integration Test Suite
- Frontend API Client
- OpenAI AI Client
- Domain Exception Hierarchy
- Hybrid Search Pipeline
- Unit Tests (misc)
- Generation Base & Tests
- Chunking Splitter Utils
- Conversation Service
- Frontend Sources Panel
- Evaluation Predictor
- Core Security (JWT/Password)
- Generation Exceptions
- Frontend Login Flow
- Input Validation Models
- Frontend Document API
- LLM Fundamentals Fixture & Artifacts
- Frontend Workspace View
- Chunking Semantic/Merge Stages
- Retrieval Context Formatter
- Frontend Response DTOs
- Unit Tests (misc 2)
- Sparse Search Models
- CLAUDE.md Chunking Notes
- Frontend Message API & DTOs
- App Main & Exception Handlers
- CLAUDE.md Conversation/Citation Notes
- Auth Service & Exceptions
- Reranking Result Model
- CLAUDE.md Project Overview
- Frontend Chat API
- Response Schemas
- Evaluation Artifacts README
- Unit Tests (misc 3)
- Health Check Endpoint
- Document Parser
- Embedding Models (aux)
- Retrieval Service
- Generation Service (aux)
- Dense Search (aux)
- Storage Base
- Document Validators
- CLAUDE.md Qdrant/Ingestion Notes
- AI Models
- Evaluation Comparison Artifacts
- Hybrid Search (aux)
- Document Service (aux)
- Attention Paper Duplicate Link
- Speech Paper Duplicate Link
- Chat API (aux)
- Evaluation Stage Artifacts
- Ai: Init
- Constants: Document
- Constants: Init
- Generation: Service
- Search: Hybrid
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
4. `DocumentBlock` - 51 edges
5. `User` - 50 edges
6. `GenerationRequest` - 49 edges
7. `GenerationService` - 46 edges
8. `ChunkPipeline` - 45 edges
9. `count_tokens()` - 45 edges
10. `AIPipeline` - 44 edges

## Surprising Connections (you probably didn't know these)
- `Transformer Architecture` --semantically_similar_to--> `LangGraph`  [INFERRED] [semantically similar]
  evaluation/fixtures/llm_fundamentals.yaml → README.md
- `Langfuse` --semantically_similar_to--> `LangSmith Tracing (@traceable)`  [INFERRED] [semantically similar]
  README.md → CLAUDE.md
- `Attention Is All You Need (upload 005042b4)` --semantically_similar_to--> `Attention Is All You Need`  [INFERRED] [semantically similar]
  storage/uploads/005042b4-01ed-4861-a6cb-18bd665703c5.pdf → tests/test_documents/Attention.pdf
- `Transformer architecture` --semantically_similar_to--> `Transformer architecture`  [INFERRED] [semantically similar]
  storage/uploads/005042b4-01ed-4861-a6cb-18bd665703c5.pdf → tests/test_documents/Attention.pdf
- `Self-attention` --semantically_similar_to--> `Self-attention`  [INFERRED] [semantically similar]
  storage/uploads/005042b4-01ed-4861-a6cb-18bd665703c5.pdf → tests/test_documents/Attention.pdf

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **ChunkPipeline ordered stage flow** — claude_chunk_pipeline, claude_metadata_stage, claude_merge_stage, claude_recursive_stage, claude_semantic_stage, claude_quality_stage, claude_finalize_stage [EXTRACTED 0.75]
- **Retrieval to generation to citation flow** — claude_ai_pipeline, claude_retrieval_service, claude_reranking_service, claude_generation_service, claude_citations [EXTRACTED 0.75]
- **Offline chunking evaluation harness** — evaluation_artifacts_readme_chunking_report, evaluation_artifacts_readme_frozen_blocks, evaluation_artifacts_comparison, evaluation_artifacts_readme_determinism [EXTRACTED 0.75]
- **Transformer built from attention components** — tests_test_documents_attention_transformer, tests_test_documents_attention_self_attention, tests_test_documents_attention_scaled_dot_product_attention, tests_test_documents_attention_multi_head_attention, tests_test_documents_attention_positional_encoding [EXTRACTED 0.75]
- **RAG paradigm progression** — tests_test_documents_rag_retrieval_augmented_generation, tests_test_documents_rag_naive_rag, tests_test_documents_rag_advanced_rag, tests_test_documents_rag_modular_rag [EXTRACTED 0.75]
- **BERT deep bidirectional pre-training** — tests_test_documents_bert_masked_language_model, tests_test_documents_bert_next_sentence_prediction, tests_test_documents_bert_bidirectional_pretraining, tests_test_documents_bert_fine_tuning [EXTRACTED 0.75]

## Communities (135 total, 16 thin omitted)

### Community 0 - "Document Block Handlers"
Cohesion: 0.06
Nodes (55): DocumentConverter, Token, Converts Markdown-It tokens into semantic DocumentBlocks. The converter itself…, Convert Markdown tokens into semantic DocumentBlocks., BaseHandler, HandlerResult, ABC, Token (+47 more)

### Community 1 - "Offline Chunking Evaluator"
Cohesion: 0.07
Nodes (68): analyze(), _block_from_dict(), _block_range_valid(), _block_to_dict(), _chunk_body(), compare(), _dig(), _expected_prefix() (+60 more)

### Community 2 - "Recursive Split & Token Utils"
Cohesion: 0.06
Nodes (40): _is_markdown_separator(), _norm(), Compact heading context: the deepest heading normally, or the deepest two…, Recover the source segments (one per contributing block) from the merged chunk…, The text a pass-through chunk would carry with ``prefix`` present exactly once.…, A markdown table separator row, e.g. ``| --- | :--: |``., Text of each child (before the heading prefix), plus -- for the structural…, Pack whole list items into child bodies, never dividing one. A single item… (+32 more)

### Community 3 - "Chunk Pipeline & Stages"
Cohesion: 0.08
Nodes (34): ChunkingConfig, Single source of truth for the chunking pipeline's size limits. Every value is…, True when ``inner`` names the same section as ``outer`` or a subsection nested…, section_contains(), ChunkPipeline, Executes the configured chunking stages., BaseChunkStage, ABC (+26 more)

### Community 4 - "Document API & Ingestion Service"
Cohesion: 0.06
Nodes (41): delete_document(), download_document(), get_document(), get_documents(), BackgroundTasks, delete, get, post (+33 more)

### Community 5 - "CrossEncoder Reranker"
Cohesion: 0.06
Nodes (32): CrossEncoderReranker, Cross Encoder based reranker implementation. This module implements the…, Automatically determine the best available inference device. Priority --------…, Name of the underlying HuggingFace model., Device used for inference., Batch size used during inference., Maximum sequence length accepted by the model., Returns the loaded CrossEncoder instance. This property is primarily useful for… (+24 more)

### Community 6 - "Docling Ingestion Processor"
Cohesion: 0.07
Nodes (30): BaseProcessor, ABC, Path, Extract structured information from a document., Base class for every document processor., ProcessorFactory, Path, Returns the correct processor for a document. (+22 more)

### Community 7 - "Finalize/Quality Stages & Metrics"
Cohesion: 0.07
Nodes (38): DocumentChunk, Represents one chunk that will eventually be embedded and stored in the vector…, FinalizeStage, UUID, Generate a deterministic UUID for every chunk. UUIDs must satisfy: • Stable…, Final stage executed before embeddings. Responsibilities ---------------- •…, Normalize page/block ranges. Pages should always be ascending. Block ranges are…, QualityStage (+30 more)

### Community 8 - "Dense Qdrant Repository"
Cohesion: 0.07
Nodes (33): CollectionAlreadyExistsError, CollectionCreationError, CollectionDeletionError, CollectionNotFoundError, DenseSearchConfigurationError, DenseSearchError, InvalidPayloadError, InvalidSearchQueryError (+25 more)

### Community 9 - "Dense Search Pipeline & Mapper"
Cohesion: 0.07
Nodes (21): EmbeddedChunk, Returns the chunk text., Returns the embedding dimensions., Represents a chunk together with its embedding. This object is produced by the…, Execute the complete embedding pipeline., Convenience wrapper. Allows pipeline(chunks) instead of pipeline.run(chunks), DenseMapper, PointStruct (+13 more)

### Community 10 - "Reranking Base & Models"
Cohesion: 0.07
Nodes (26): BaseReranker, ABC, Abstract interface for all rerankers. Every reranker implementation…, Allows the reranker instance to be invoked like a function. Example -------…, Abstract base class for reranking implementations., Rerank retrieved candidates. Parameters ---------- query: User query.…, Returns the underlying reranker model name., Returns the execution device. Example ------- cpu cuda cuda:0 mps (+18 more)

### Community 11 - "Conversation Memory Tests"
Cohesion: 0.13
Nodes (35): fixture, add_messages(), db(), FakeSummaryPipeline, make_chat(), make_conversation_service(), make_summary_service(), Executable specification for the rolling conversation-memory behaviour… (+27 more)

### Community 12 - "Chunking Contract Tests"
Cohesion: 0.13
Nodes (40): _distinct(), _fchunk(), _list_blocks(), _long(), _merged_section(), Chunk-quality contract tests (Phase 2). Built incrementally alongside the…, A MergeStage-style section chunk: ``blocks`` joined with blank lines…, Q2/Q3: 1 heading + 4 distinct body blocks, 2 pages, forced into several… (+32 more)

### Community 13 - "Query/Summary/Title Generators"
Cohesion: 0.11
Nodes (25): QueryRewriter, Build the prompt used to rewrite the latest user message into a standalone…, Convert structured conversation messages into a readable prompt format., Responsible for rewriting conversational user queries into standalone search…, Build the prompt used to generate or update the rolling conversation summary., Convert structured conversation messages into a readable prompt format., Responsible for building prompts used to generate and maintain a rolling…, SummaryGenerator (+17 more)

### Community 14 - "Message API & Service"
Cohesion: 0.12
Nodes (28): create_message(), get_messages(), BackgroundTasks, get, post, Retrieve all messages for a chat session., Send a message and receive the assistant response., Stream an assistant response using Server-Sent Events (SSE). (+20 more)

### Community 15 - "Service DI Wiring & Local Storage"
Cohesion: 0.11
Nodes (32): get_db(), Session, Creates a new database session for each request and ensures it is closed after…, get_ai_pipeline(), get_auth_service(), get_chat_service(), get_conversation_service(), get_conversation_summary_service() (+24 more)

### Community 16 - "Citation Ordering & Provenance Tests"
Cohesion: 0.16
Nodes (34): GenerationRequest, Input required by the Prompt Builder and Generation layer., GenerationService, Production implementation of the Generation layer. Responsibilities…, Generate a complete assistant response., Build clean, deduplicated citations from retrieved provenance, ordered by…, Stream the assistant response., Citation (+26 more)

### Community 17 - "Chat API & Service"
Cohesion: 0.08
Nodes (29): create_chat(), delete_chat(), get_chat(), list_chats(), delete, get, post, Response (+21 more)

### Community 18 - "OpenAI Embedder"
Cohesion: 0.08
Nodes (29): traceable, Execute one embedding request. Retries automatically for transient OpenAI…, Convert raw vectors returned by OpenAI into EmbeddedChunk objects., Embed a single batch of document chunks. Parameters ---------- chunks A batch…, Generate an embedding for a user query., Estimate embedding cost in USD. Cost is calculated using the official OpenAI…, EmbeddingCacheError, EmbeddingConfigurationError (+21 more)

### Community 19 - "Sparse Encoder & Pipeline"
Cohesion: 0.08
Nodes (17): traceable, Generate sparse embedding for a user query., Generates sparse embeddings for document chunks using FastEmbed.…, Generate sparse embeddings for document chunks., SparseEncoder, Represents a sparse vector generated by the sparse encoder. Unlike dense…, Number of non-zero dimensions., Represents a document chunk together with its sparse vector. (+9 more)

### Community 20 - "Hybrid Indexing Integration Tests"
Cohesion: 0.10
Nodes (17): OpenAIEmbedder, Generates OpenAI embeddings for DocumentChunks. Responsibilities…, EmbeddingPipeline, Production embedding pipeline. Pipeline DocumentChunks │ ▼ EmbeddingBatcher │ ▼…, PDFProcessor, Backward-compatible PDF processor. PDF ingestion is now handled by…, HybridPipeline, Production Hybrid Indexing Pipeline. Responsibilities ----------------… (+9 more)

### Community 21 - "LangSmith Evaluation Harness"
Cohesion: 0.10
Nodes (21): answer_length(), citation_count(), exact_match(), Any, Exact answer match. Useful as a fast deterministic baseline., Records answer length. Helpful for spotting prompt regressions., Counts returned citations., FixtureManager (+13 more)

### Community 22 - "LLM Service & Prompt Builder"
Cohesion: 0.09
Nodes (17): get_llm_resource(), Application-scoped AI resources. Heavy resources (models, vector clients, LLM…, Return the shared LLM service., PromptBuilder, traceable, Convert retrieved contexts into a formatted block., Build the optional long-term conversation summary., Builds provider-agnostic prompts for the Generation layer. Responsibilities… (+9 more)

### Community 23 - "Retrieval Base Contract & Tests"
Cohesion: 0.11
Nodes (26): BaseRetrievalService, ABC, Base contract for all retrieval implementations., ContextFormattingError, EmptyQueryError, NoRetrievalResultsError, Exception, Raised when no relevant contexts could be retrieved. (+18 more)

### Community 24 - "SQLAlchemy Models & Migration Env"
Cohesion: 0.12
Nodes (18): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Base, Base class for all SQLAlchemy ORM models., ChatSession, Represents a chat session belonging to a user. (+10 more)

### Community 25 - "Conversation Service & Message Repo"
Cohesion: 0.10
Nodes (20): AIPipeline, Production AI orchestration layer. Responsibilities ---------------- - Convert…, build_conversation_summary_service(), Construct a ConversationSummaryService without FastAPI's DI graph. Used by the…, ChatRepository, Session, Repository for ChatSession database operations., MessageRepository (+12 more)

### Community 26 - "Base Repository & Auth Dependency"
Cohesion: 0.09
Nodes (17): get_current_user(), Session, Return the currently authenticated user., BaseRepository, Session, Base repository providing common CRUD operations., Persist a new entity., Retrieve an entity by its primary key. (+9 more)

### Community 27 - "RetrievalResult Model & Tests"
Cohesion: 0.12
Nodes (20): Execute the complete retrieval pipeline. Retrieval is keyword-only and always…, Allow the service to be invoked like a function., slice, SupportsIndex, Return unique section names while preserving retrieval order., Represents a single document chunk after the complete retrieval pipeline…, Final output returned by the RetrievalService., Return unique document sources while preserving retrieval order. (+12 more)

### Community 28 - "Chunking Stage Tests"
Cohesion: 0.12
Nodes (27): ChunkMetadata, ContentSegment, One source ``DocumentBlock`` that ``MergeStage`` folded into a chunk. Internal…, Metadata associated with a document chunk. This metadata flows through the…, Narrow post-split cleanup. Responsibilities ---------------- - concatenate a…, SemanticStage, BlockProvenance, A compact, parser-neutral reference to the source of one block. (+19 more)

### Community 29 - "Retrieval/Rerank Integration Tests"
Cohesion: 0.13
Nodes (18): Application settings loaded from environment variables., Settings, Public service for document reranking. The service hides the concrete reranker…, Initialize the reranking service. Parameters ---------- reranker: Optional…, Returns the active reranker. The default CrossEncoderReranker is created only…, RerankingService, Production Retrieval Orchestrator. Pipeline -------- User Query │ ▼ Hybrid…, RetrievalService (+10 more)

### Community 30 - "Auth & User Schemas"
Cohesion: 0.15
Nodes (23): login(), oauth2_login(), post, Authenticate a user using JSON. Used by the frontend., OAuth2-compatible login endpoint. Swagger sends: username password We interpret…, register(), LoginRequest, BaseModel (+15 more)

### Community 31 - "Embedding Models & Batcher"
Cohesion: 0.11
Nodes (19): EmbeddingBatcher, Splits document chunks into batches suitable for the embedding provider. The…, Split chunks into embedding batches., Convenience wrapper allowing the batcher to be called directly., Embed multiple batches. Parameters ---------- batches List of EmbeddingBatch…, Convenience wrapper. Allows embedder(batches) instead of embedder.embed(batches), EmbeddingBatchError, Raised when an embedding batch is invalid. Examples: - Empty batch - Batch… (+11 more)

### Community 32 - "Chunking Utils Tests"
Cohesion: 0.18
Nodes (28): count_tokens(), Count the number of tokens in text., BlockType, Represents the semantic type of a document block. This enum is parser-…, StrEnum, _md_table(), _pipeline_from_blocks(), _row_lines() (+20 more)

### Community 33 - "Research Paper Corpus (PDFs)"
Cohesion: 0.10
Nodes (27): Attention Is All You Need (upload 005042b4), Positional encoding, Self-attention, Transformer architecture, A Comprehensive Overview of Large Language Models (upload 3c7e729d), LLM fine-tuning and training strategies, Large language models, Transformer foundation of LLMs (+19 more)

### Community 34 - "Chunking Provenance Audit Tests"
Cohesion: 0.19
Nodes (26): _body(), _heading(), _merge(), _prov(), Run the first real stages that shape section chunks: Metadata -> Merge. Input…, _run_metadata(), test_consecutive_headings_drop_the_content_free_one(), test_content_before_any_heading_keeps_null_section_id() (+18 more)

### Community 35 - "AIPipeline Orchestration"
Cohesion: 0.13
Nodes (14): traceable, Stream an assistant response using Retrieval-Augmented Generation., Generate a short AI title for a new conversation., Generate or update the conversation summary., Build the query used for document retrieval. Conversational follow-up questions…, Select the conversation messages sent verbatim to the answer LLM. Before…, Convert ORM ChatMessage models into generation domain models., Decide whether the conversation summary should be injected into the prompt. The… (+6 more)

### Community 36 - "Frontend Sidebar & State"
Cohesion: 0.15
Nodes (20): main(), _client(), _create_chat(), _load_chat(), Create an authenticated API client., Refresh chats and documents., Load a chat and its messages., Upload selected documents. (+12 more)

### Community 37 - "Integration Test Suite"
Cohesion: 0.16
Nodes (22): preview_text(), print_header(), print_hybrid_results(), print_performance(), print_quality_benchmark(), print_rank_movements(), print_reranked_results(), print_reranking_statistics() (+14 more)

### Community 38 - "Frontend API Client"
Cohesion: 0.16
Nodes (7): ApiClient, Any, Response, Download binary data., Open a Server-Sent Events POST request., Base HTTP client used by all frontend services., Execute an HTTP request.

### Community 39 - "OpenAI AI Client"
Cohesion: 0.12
Nodes (12): BaseLLMProvider, ABC, Generate a complete response from the language model., Stream a response from the language model., Base interface for all LLM providers., get_openai_client(), Create and return an OpenAI client. The client is configured using application…, OpenAIProvider (+4 more)

### Community 40 - "Domain Exception Hierarchy"
Cohesion: 0.14
Nodes (15): AppException, Exception, Initialize the exception. If no message is supplied, use the class-level…, Base exception for all application-specific errors., DocumentTooLargeError, EmptyDocumentError, InvalidDocumentTypeError, Raised when an empty document is uploaded. (+7 more)

### Community 41 - "Hybrid Search Pipeline"
Cohesion: 0.13
Nodes (12): traceable, Execute native Qdrant Hybrid Search using Reciprocal Rank Fusion (RRF).…, HybridMapper, PointStruct, ScoredPoint, Combine dense and sparse representations into a single hybrid Qdrant point., Converts Astra Study domain models into hybrid Qdrant PointStruct objects.…, Convert dense and sparse chunk collections into hybrid PointStructs. Both lists… (+4 more)

### Community 42 - "Unit Tests (misc)"
Cohesion: 0.15
Nodes (11): _extract(), FakeBBox, FakeConverter, FakeDocument, FakeItem, FakeProv, test_chunking_preserves_provenance(), test_docx_heading_section_without_page() (+3 more)

### Community 43 - "Generation Base & Tests"
Cohesion: 0.14
Nodes (9): BaseGenerationService, ABC, Abstract interface for the Generation layer. Implementations are responsible…, Generate a complete response., Stream the generated response. Each yielded string represents the next chunk of…, GenerationResponse, Structured response produced by the Generation layer., _RecordingGeneration (+1 more)

### Community 44 - "Chunking Splitter Utils"
Cohesion: 0.25
Nodes (13): is_copyright(), is_doi(), is_empty(), is_isbn(), is_numeric_only(), is_page_number(), is_punctuation_only(), is_short_noise() (+5 more)

### Community 45 - "Conversation Service"
Cohesion: 0.23
Nodes (10): ConversationService, BackgroundTasks, traceable, Stream an AI response while persisting the final assistant message., Validate that the chat exists and belongs to the current user., Generate an AI title for a newly created chat., Persist the assistant response., Trigger a rolling-summary refresh without blocking the response. In the normal… (+2 more)

### Community 46 - "Frontend Sources Panel"
Cohesion: 0.17
Nodes (15): _client(), _document_service(), _normalize_heading_path(), DocumentService, Presentation-only cleanup: collapse consecutive duplicate heading entries (e.g.…, Create an authenticated API client., Display retrieved citations., Create the document service. (+7 more)

### Community 47 - "Evaluation Predictor"
Cohesion: 0.17
Nodes (11): AIResponse, Response returned by the AI orchestration layer. This model is intentionally…, Citation, Represents a source citation supporting the generated answer., _citation_relevance(), _heading_match(), Weighted fraction of the question's *discriminative* terms carried by this…, Blends the three distinct notions of relevance, all bounded so this only re-… (+3 more)

### Community 48 - "Core Security (JWT/Password)"
Cohesion: 0.15
Nodes (8): Any, Handles password hashing, password verification, and JWT token generation., Decode and validate a JWT., Hash a plain-text password., Verify a password against its hash., Create an access token., Create a refresh token., SecurityManager

### Community 49 - "Generation Exceptions"
Cohesion: 0.18
Nodes (14): EmptyPromptError, EmptyResponseError, GenerationError, GenerationTimeoutError, InvalidGenerationResponseError, Exception, Exceptions raised by the Generation module., Raised when prompt generation results in no messages. (+6 more)

### Community 50 - "Frontend Login Flow"
Cohesion: 0.26
Nodes (8): ApiException, Exception, Raised when the backend returns an error response., AuthService, _load_workspace(), login_screen(), Load chats and documents immediately after login., Render the login / registration page.

### Community 51 - "Input Validation Models"
Cohesion: 0.20
Nodes (9): DocumentValidator, Validates document-level metadata., Any, One metric produced by a validator., Output returned by every validator. Every validator returns exactly one…, Represents a non-fatal validation issue., ValidationMetric, ValidationResult (+1 more)

### Community 52 - "Frontend Document API"
Cohesion: 0.21
Nodes (8): BinaryIO, DocumentService, Service responsible for all document-related operations., Download the original uploaded document., Retrieve all uploaded documents., Retrieve metadata for a single document., Upload one or more documents., Document

### Community 53 - "LLM Fundamentals Fixture & Artifacts"
Cohesion: 0.16
Nodes (14): baseline_apjspeech.txt (commit 888fc8c report), baseline_Attention.txt (commit 888fc8c report), baseline_LLM.txt (commit 888fc8c report), comparison.txt (baseline vs stage14 deltas), apjspeech.pdf (eval corpus doc), Attention.pdf (eval corpus doc), LLM.pdf (eval corpus doc), Chunking Evaluation Artifacts README (+6 more)

### Community 54 - "Frontend Workspace View"
Cohesion: 0.23
Nodes (12): Citation, _active_chat(), _client(), Create an authenticated API client., Refresh the sidebar chat list., Return the selected chat., Render workspace heading., Render conversation history. (+4 more)

### Community 55 - "Chunking Semantic/Merge Stages"
Cohesion: 0.19
Nodes (7): One ContentSegment for a source block as it enters MergeStage (each chunk is…, Emit ``builder`` -- unless it only ever held a heading (or nothing), in which…, Start a new section chunk. Every metadata field is preserved by deep-copying…, Decide whether ``incoming`` starts a new section chunk., Incrementally builds one heading-anchored section chunk. A heading may *seed* a…, _segment_of(), SemanticChunkBuilder

### Community 56 - "Retrieval Context Formatter"
Cohesion: 0.23
Nodes (9): ContextFormatter, Formats retrieved contexts into different representations suitable for…, Serialize contexts into JSON., Format contexts as plain text., Format contexts as Markdown., make_result(), test_to_json(), test_to_markdown() (+1 more)

### Community 57 - "Frontend Response DTOs"
Cohesion: 0.26
Nodes (4): TokenResponse, ApiResponse, Standard API response returned by Astra Study., User

### Community 58 - "Unit Tests (misc 2)"
Cohesion: 0.22
Nodes (11): _FakeLLM, make_pipeline(), orm_conversation(), parametrize, A pending/failed first summary must not trigger history truncation., test_full_history_used_before_first_summary(), test_generation_context_is_summary_plus_rolling_window(), test_generation_history_bounded_for_very_long_conversation() (+3 more)

### Community 59 - "Sparse Search Models"
Cohesion: 0.23
Nodes (11): Exception, Raised when the sparse encoder configuration is invalid., Base exception for all sparse search errors., Raised when a sparse vector collection operation fails., Raised when sparse retrieval fails., Raised when sparse embeddings cannot be generated., SparseCollectionError, SparseConfigurationError (+3 more)

### Community 60 - "CLAUDE.md Chunking Notes"
Cohesion: 0.20
Nodes (12): ChunkPipeline (8 ordered stages), ChunkingConfig (token size limits), Chunking Pipeline Contract (frozen), ContentSegment (structural atomicity), FinalizeStage, MergeStage, MetadataStage, QualityStage (+4 more)

### Community 61 - "Frontend Message API & DTOs"
Cohesion: 0.35
Nodes (4): MessageService, Yield assistant text chunks from the message SSE endpoint., Conversation, Message

### Community 62 - "App Main & Exception Handlers"
Cohesion: 0.25
Nodes (9): get_reranking_resource(), Return the shared reranking service. The underlying CrossEncoder model is…, FastAPI, Register all application exception handlers., register_exception_handlers(), lifespan(), FastAPI, get (+1 more)

### Community 63 - "CLAUDE.md Conversation/Citation Notes"
Cohesion: 0.20
Nodes (11): AIPipeline (retrieval + generation), Citation Ordering (deterministic), Conversation Memory (rolling summary + recent window), ConversationService (SSE event loop), GenerationService, PostgreSQL (SQLAlchemy + Alembic), CrossEncoder RerankingService, RetrievalService (tenant-scoped) (+3 more)

### Community 64 - "Auth Service & Exceptions"
Cohesion: 0.22
Nodes (8): AuthenticationError, InactiveUserError, InvalidCredentialsError, Raised when an inactive user attempts to log in., Raised when authentication fails because the access token is invalid, expired,…, Raised when the provided email or password is incorrect., TokenResponse, Authenticate a user and return JWT tokens.

### Community 65 - "Reranking Result Model"
Cohesion: 0.20
Nodes (6): slice, SupportsIndex, Returns the top-k reranked chunks. Parameters ---------- k: Number of chunks to…, Represents a single reranked retrieval result. Attributes ---------- result:…, Returns the highest ranked chunk., RerankedChunk

### Community 66 - "CLAUDE.md Project Overview"
Cohesion: 0.31
Nodes (9): Astra Study, FastAPI Backend (app/), LangSmith Tracing (@traceable), RAG Chat over Uploaded Documents, Streamlit Workspace UI (frontend/), Astra Study Frontend README, Astra Study (README overview), Langfuse (+1 more)

### Community 68 - "Response Schemas"
Cohesion: 0.36
Nodes (6): success_response(), ApiResponse, ErrorResponse, BaseModel, Standard error API response., Standard success API response.

### Community 69 - "Evaluation Artifacts README"
Cohesion: 0.29
Nodes (8): BlockProvenance data flow, Docling Processor, Full-list-fallback Suspected Chunks Metric, chunking_report.py offline structural evaluator, Chunking Determinism Requirement, Frozen Docling Block Snapshots (blocks_<doc>.json), Source Item ID Coverage Metric, OCR / Vision-based Document Understanding

### Community 70 - "Unit Tests (misc 3)"
Cohesion: 0.29
Nodes (6): _conversation(), _FakeStreamGen, _pipeline(), test_normal_pipeline_returns_citations(), test_streaming_citations_reflect_the_streamed_answer(), test_streaming_pipeline_emits_citations_after_text()

### Community 71 - "Health Check Endpoint"
Cohesion: 0.38
Nodes (5): health_check(), get, HealthResponse, BaseModel, Response model for the health check endpoint.

### Community 72 - "Document Parser"
Cohesion: 0.29
Nodes (4): DocumentParser, Token, Parse Markdown into tokens., Parses Markdown into Markdown-It tokens. This class is intentionally…

### Community 73 - "Embedding Models (aux)"
Cohesion: 0.29
Nodes (4): UUID, Returns the UUIDs of all chunks contained in the batch., Returns the chunk UUID., Returns the document UUID.

### Community 74 - "Retrieval Service"
Cohesion: 0.33
Nodes (4): traceable, Execute the complete retrieval pipeline. Steps ----- 1. Validate query 2.…, Callable wrapper. Allows RetrievalService to be invoked like a function while…, Convert reranked search results into RetrievedContext objects consumed by…

### Community 75 - "Generation Service (aux)"
Cohesion: 0.33
Nodes (6): _answer_support(), _query_term_weights(), Deterministic answer/evidence alignment signal: the fraction of the chunk's own…, Weight each distinctive query term by how well it *discriminates* between the…, _tokenize(), test_query_term_weights_discount_topic_terms_and_reward_distinctive_ones()

### Community 76 - "Dense Search (aux)"
Cohesion: 0.33
Nodes (4): DenseSearchResponse, Represents the complete response returned from the dense search pipeline., Number of retrieved results., Highest similarity score.

### Community 77 - "Storage Base"
Cohesion: 0.27
Nodes (4): Path, UploadFile, Save a file and return: ( stored_filename, file_size, ), Return the absolute path of a stored file.

### Community 78 - "Document Validators"
Cohesion: 0.33
Nodes (4): DocumentValidator, UploadFile, Validates uploaded documents before they are stored on disk., Validate an uploaded document. Raises ------ HTTPException If validation fails.

### Community 79 - "CLAUDE.md Qdrant/Ingestion Notes"
Cohesion: 0.33
Nodes (6): HybridPipeline (dense + sparse indexing), Ingestion Pipeline (upload to vectors), Qdrant Vector Store, Qdrant Integration Test Hazard, docker-compose.yml (empty placeholder), OpenAI GPT-5 / GPT-5 Vision

### Community 80 - "AI Models"
Cohesion: 0.50
Nodes (4): OpenAIModel, Enum, str, Supported OpenAI chat models.

### Community 81 - "Evaluation Comparison Artifacts"
Cohesion: 0.40
Nodes (4): comparison_stage5_to_stage6.txt (Stage 6 primary comparison), pre_Attention.txt (pre-refactor report), stage14_Attention.txt (Stage 5 frozen tree report), stage6_Attention.txt (Stage 6 ContentSegment report)

### Community 83 - "Document Service (aux)"
Cohesion: 0.50
Nodes (3): Document, UploadFile, Upload one or more documents. Returns the created Document models.

### Community 84 - "Attention Paper Duplicate Link"
Cohesion: 0.67
Nodes (4): Multi-head attention, Scaled dot-product attention, Multi-head attention, Scaled dot-product attention

### Community 85 - "Speech Paper Duplicate Link"
Cohesion: 0.67
Nodes (4): A P J Abdul Kalam Departing Speech (upload 510fce33), Developed India 2020, A P J Abdul Kalam Departing Speech, Developed India 2020

### Community 91 - "Chat API (aux)"
Cohesion: 0.67
Nodes (3): get_current_user_profile(), get, Return the currently authenticated user's profile.

## Knowledge Gaps
- **31 isolated node(s):** `astra-study`, `RAG Chat over Uploaded Documents`, `MetadataStage`, `SemanticStage`, `QualityStage` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 781 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DocumentChunk` connect `Finalize/Quality Stages & Metrics` to `Offline Chunking Evaluator`, `Recursive Split & Token Utils`, `Chunk Pipeline & Stages`, `Chunking Provenance Audit Tests`, `Dense Search Pipeline & Mapper`, `Hybrid Search Pipeline`, `Chunking Splitter Utils`, `Chunking Contract Tests`, `Citation Ordering & Provenance Tests`, `OpenAI Embedder`, `Sparse Encoder & Pipeline`, `Hybrid Indexing Integration Tests`, `Input Validation Models`, `Chunking Semantic/Merge Stages`, `Chunking Stage Tests`, `Embedding Models & Batcher`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `BlockType` connect `Chunking Utils Tests` to `Document Block Handlers`, `Offline Chunking Evaluator`, `Recursive Split & Token Utils`, `Chunk Pipeline & Stages`, `Chunking Provenance Audit Tests`, `Docling Ingestion Processor`, `Finalize/Quality Stages & Metrics`, `Unit Tests (misc)`, `Chunking Splitter Utils`, `Chunking Contract Tests`, `Citation Ordering & Provenance Tests`, `Chunking Semantic/Merge Stages`, `Chunking Stage Tests`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `HybridSearchResult` connect `Reranking Base & Models` to `Reranking Result Model`, `CrossEncoder Reranker`, `Dense Qdrant Repository`, `Dense Search Pipeline & Mapper`, `Hybrid Search Pipeline`, `Hybrid Search (aux)`, `Sparse Encoder & Pipeline`, `Retrieval Base Contract & Tests`, `Retrieval/Rerank Integration Tests`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `DocumentChunk` (e.g. with `ChunkPipeline` and `BaseChunkStage`) actually correct?**
  _`DocumentChunk` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 92 inferred relationships involving `BlockType` (e.g. with `ChunkMetadata` and `ContentSegment`) actually correct?**
  _`BlockType` has 92 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `RetrievalResult` (e.g. with `GenerationRequest` and `BaseRetrievalService`) actually correct?**
  _`RetrievalResult` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `DocumentBlock` (e.g. with `DocumentConverter` and `HandlerResult`) actually correct?**
  _`DocumentBlock` has 16 INFERRED edges - model-reasoned connections that need verification._