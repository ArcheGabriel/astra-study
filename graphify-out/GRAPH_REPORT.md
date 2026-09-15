# Graph Report - Astra-Study  (2026-09-15)

## Corpus Check
- 37 files · ~228,626 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2316 nodes · 5573 edges · 156 communities (90 shown, 31 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 569 edges (avg confidence: 0.94)
- Token cost: 64,440 input · 0 output

## Community Hubs (Navigation)
- Docling Block Handlers
- ConversationService & Memory Tests
- Offline Chunking Evaluator
- Chunk Pipeline Contract Tests
- Citation & Provenance Tests
- Recursive Split & Tokenizer Utils
- Merge/Quality Stage Tests
- Docling Ingestion Processor
- Chunk Pipeline & Stages
- Retrieval Formatter & Exceptions
- Document API & Ingestion Service
- Auth API & User Service
- Sparse Encoder & Hybrid Pipeline
- LangSmith Evaluation Harness
- AccessContext & Hybrid Search Tests
- RBAC Team Membership & Foundation Tests
- Chat API & Document Upload
- Evaluation Fixtures & Test Documents
- Citation Generation & Scoring
- Chat/Message Models & Repositories
- Dependency Injection Wiring
- Frontend Document Service & Sources
- Metadata & Merge Stage Tests
- Query Rewrite & Summary Generators
- Message API & ConversationService
- Auth Dependency & Base Repository
- Dense Qdrant Repository
- Exception Hierarchy & App Entrypoint
- Chat Repository & Service
- AccessContext Dependency & Tests
- Embedding & Hybrid Mappers
- CrossEncoder Reranker Base
- CrossEncoder Reranker Implementation
- BaseRetrievalService & Retrieval Tests
- AIPipeline Orchestration
- OpenAI Embedder Exceptions
- RBAC SQLAlchemy Models
- Dense Search Mapper & Pipeline
- Reranking Exceptions
- RBAC-5B Propagation Tests
- RetrievalService & Integration Tests
- Frontend Chat Service & Workspace
- Reranking Integration Test
- LLM Provider Base & Service
- Filter Stage & Noise Filters
- Embedding Batcher & Dense Pipeline
- Dense Search Exceptions
- Frontend API Client
- Semantic Merge Stage Tests
- Embedding Batcher & Validator
- Reranker Call & Hybrid Mapper
- Embedding Vector & Validator
- Reranking Result Models
- Qdrant Isolation Conftest & Tests
- Core Security (JWT/Password)
- Frontend Sidebar & State
- Message Schemas & Service
- Document Validation Models
- Generation Exceptions
- Frontend App Entry & Styles
- Sparse Search Exceptions
- LLMService Generation Methods
- CLAUDE.md Project Overview
- CLAUDE.md Chunking Contract Notes
- Frontend Message Service & Models
- FinalizeStage UUID Assignment
- PromptBuilder
- Frontend Auth & User Models
- Search Import Isolation Tests
- Storage Path Helpers
- CLAUDE.md Retrieval Components Notes
- Frontend API Client & Auth
- API Response Schemas
- ConversationSummaryService
- CLAUDE.md Conversation Memory Notes
- CLAUDE.md Ingestion & Citation Notes
- Health Check Endpoint
- Document Parser
- Embedding Chunk UUID Fields
- RBAC Test Fake Storage Service
- OpenAI Client Init
- Dense Search Response Model
- Legacy Document Validator
- Alembic Env Migration Runner
- OpenAI Model Enum
- Get Messages Endpoint
- HybridService Init & Retrieval Comparison
- README Feature List
- App Settings (pydantic-settings)
- Chunking Evaluator Artifacts (LLM)
- APJ Speech Fixture Upload
- AI Package Init
- Document Constants
- Constants Package Init
- Generation StreamEvent Model
- Generation TokenUsage Model
- Generation Prompts Module
- Hybrid Search Package Init
- Multi-Head Attention Fixture
- Message GET Route Marker
- Message POST Route Marker
- Retrieval Base ABC Marker
- Dense Repository PointStruct Marker
- Document Service Type Marker
- User Service Type Marker
- Docker Compose Config
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

## God Nodes (most connected - your core abstractions)
1. `DocumentChunk` - 136 edges
2. `BlockType` - 116 edges
3. `User` - 61 edges
4. `AccessContext` - 52 edges
5. `DocumentBlock` - 51 edges
6. `count_tokens()` - 45 edges
7. `BlockProvenance` - 40 edges
8. `AIPipeline` - 38 edges
9. `ChunkPipeline` - 37 edges
10. `ApiClient` - 37 edges

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
- **8-stage chunking pipeline contract** — claude_md_chunkpipeline, claude_md_paragraphstage, claude_md_metadatastage, claude_md_mergestage, claude_md_recursivestage, claude_md_semanticstage, claude_md_filterstage, claude_md_qualitystage, claude_md_finalizestage, claude_md_chunkingconfig [EXTRACTED 1.00]
- **Retrieval + generation request flow** — claude_md_aipipeline, claude_md_retrievalservice, claude_md_rerankingservice, claude_md_generationservice, claude_md_promptbuilder [EXTRACTED 1.00]
- **Conversation memory rolling-summary mechanism** — claude_md_conversationservice, claude_md_conversationsummaryservice, claude_md_summarygenerator, claude_md_aipipeline, claude_md_conversation_memory [EXTRACTED 1.00]

## Communities (156 total, 31 thin omitted)

### Community 0 - "Docling Block Handlers"
Cohesion: 0.07
Nodes (48): DocumentConverter, Token, Converts Markdown-It tokens into semantic DocumentBlocks. The converter itself…, Convert Markdown tokens into semantic DocumentBlocks., BaseHandler, HandlerResult, ABC, Token (+40 more)

### Community 1 - "ConversationService & Memory Tests"
Cohesion: 0.06
Nodes (57): MessageService, ChatRepository, ConversationSummaryService, GenerationResponse, MessageRepository, RetrievedContext, add_messages(), db() (+49 more)

### Community 2 - "Offline Chunking Evaluator"
Cohesion: 0.07
Nodes (68): analyze(), _block_from_dict(), _block_range_valid(), _block_to_dict(), _chunk_body(), compare(), _dig(), _expected_prefix() (+60 more)

### Community 3 - "Chunk Pipeline Contract Tests"
Cohesion: 0.10
Nodes (65): count_tokens(), Count the number of tokens in text., BlockType, Represents the semantic type of a document block. This enum is parser-…, StrEnum, _distinct(), _list_blocks(), _long() (+57 more)

### Community 4 - "Citation & Provenance Tests"
Cohesion: 0.06
Nodes (50): ChunkMetadata, EmbeddedChunk, _context(), _conversation(), _embedded(), _extract(), FakeBBox, FakeConverter (+42 more)

### Community 5 - "Recursive Split & Tokenizer Utils"
Cohesion: 0.06
Nodes (40): _is_markdown_separator(), _norm(), Compact heading context: the deepest heading normally, or the deepest two…, Recover the source segments (one per contributing block) from the merged chunk…, The text a pass-through chunk would carry with ``prefix`` present exactly once.…, A markdown table separator row, e.g. ``| --- | :--: |``., Text of each child (before the heading prefix), plus -- for the structural…, Pack whole list items into child bodies, never dividing one. A single item… (+32 more)

### Community 6 - "Merge/Quality Stage Tests"
Cohesion: 0.06
Nodes (47): ChunkMetadata, DocumentChunk, Represents one chunk that will eventually be embedded and stored in the vector…, Metadata associated with a document chunk. This metadata flows through the…, One ContentSegment for a source block as it enters MergeStage (each chunk is…, Emit ``builder`` -- unless it only ever held a heading (or nothing), in which…, Start a new section chunk. Every metadata field is preserved by deep-copying…, Decide whether ``incoming`` starts a new section chunk. (+39 more)

### Community 7 - "Docling Ingestion Processor"
Cohesion: 0.07
Nodes (35): BaseProcessor, ABC, Path, Extract structured information from a document., Base class for every document processor., ProcessorFactory, Path, Returns the correct processor for a document. (+27 more)

### Community 8 - "Chunk Pipeline & Stages"
Cohesion: 0.09
Nodes (27): ChunkingConfig, Single source of truth for the chunking pipeline's size limits. Every value is…, ContentSegment, One source ``DocumentBlock`` that ``MergeStage`` folded into a chunk. Internal…, ChunkPipeline, Executes the configured chunking stages., BaseChunkStage, ABC (+19 more)

### Community 9 - "Retrieval Formatter & Exceptions"
Cohesion: 0.07
Nodes (38): ContextFormattingError, EmptyQueryError, NoRetrievalResultsError, Exception, Raised when no relevant contexts could be retrieved., Base exception for retrieval failures., Raised when the retrieval pipeline is improperly configured., Raised when retrieved contexts cannot be formatted for downstream generation. (+30 more)

### Community 10 - "Document API & Ingestion Service"
Cohesion: 0.07
Nodes (37): delete_document(), download_document(), get_document(), get_documents(), BackgroundTasks, delete, get, post (+29 more)

### Community 11 - "Auth API & User Service"
Cohesion: 0.08
Nodes (36): login(), oauth2_login(), post, Authenticate a user using JSON. Used by the frontend., OAuth2-compatible login endpoint. Swagger sends: username password We interpret…, register(), get_current_user_profile(), get (+28 more)

### Community 12 - "Sparse Encoder & Hybrid Pipeline"
Cohesion: 0.06
Nodes (20): HybridPipeline, Production Hybrid Indexing Pipeline. Responsibilities ----------------…, Index document chunks using hybrid dense+sparse vectors., traceable, Generate sparse embedding for a user query., Generates sparse embeddings for document chunks using FastEmbed.…, Generate sparse embeddings for document chunks., SparseEncoder (+12 more)

### Community 13 - "LangSmith Evaluation Harness"
Cohesion: 0.08
Nodes (25): answer_length(), citation_count(), exact_match(), Any, Exact answer match. Useful as a fast deterministic baseline., Records answer length. Helpful for spotting prompt regressions., Counts returned citations., FixtureManager (+17 more)

### Community 14 - "AccessContext & Hybrid Search Tests"
Cohesion: 0.13
Nodes (22): AIResponse, Response returned by the AI orchestration layer. This model is intentionally…, OrgRole, Enum, str, A user's organisation-scoped role. Distinct from document access scope -- role…, AccessContext, Immutable, request-scoped authorization identity. Built exclusively from… (+14 more)

### Community 15 - "RBAC Team Membership & Foundation Tests"
Cohesion: 0.10
Nodes (36): Enum, str, A user's role within a single team membership. Independent of ``OrgRole``: a…, TeamRole, Base, TimestampMixin, SQLAlchemy model representing a user's membership in a team. A user may hold at…, TeamMembership (+28 more)

### Community 16 - "Chat API & Document Upload"
Cohesion: 0.08
Nodes (32): create_chat(), delete_chat(), get_chat(), list_chats(), delete, get, post, Response (+24 more)

### Community 17 - "Evaluation Fixtures & Test Documents"
Cohesion: 0.06
Nodes (38): baseline_apjspeech.txt (commit 888fc8c report), baseline_Attention.txt (commit 888fc8c report), baseline_LLM.txt (commit 888fc8c report), comparison.txt (baseline vs stage14 deltas), comparison_stage5_to_stage6.txt (Stage 6 primary comparison), apjspeech.pdf (eval corpus doc), Attention.pdf (eval corpus doc), LLM.pdf (eval corpus doc) (+30 more)

### Community 18 - "Citation Generation & Scoring"
Cohesion: 0.10
Nodes (30): BaseGenerationService, ABC, Abstract interface for the Generation layer. Implementations are responsible…, Generate a complete response., Stream the generated response. Each yielded string represents the next chunk of…, EmptyResponseError, Raised when the LLM returns an empty response., Citation (+22 more)

### Community 19 - "Chat/Message Models & Repositories"
Cohesion: 0.10
Nodes (20): Base, Base class for all SQLAlchemy ORM models., ChatSession, Represents a chat session belonging to a user., ChatMessage, Represents a single message within a chat session., Adds automatic timestamp fields to database models., TimestampMixin (+12 more)

### Community 20 - "Dependency Injection Wiring"
Cohesion: 0.14
Nodes (31): get_db(), Session, Creates a new database session for each request and ensures it is closed after…, get_llm_resource(), get_reranking_resource(), Return the shared LLM service., Return the shared reranking service. The underlying CrossEncoder model is…, build_conversation_summary_service() (+23 more)

### Community 21 - "Frontend Document Service & Sources"
Cohesion: 0.10
Nodes (21): Retrieve all uploaded documents., BinaryIO, DocumentService, Service responsible for all document-related operations., Download the original uploaded document., Retrieve metadata for a single document., Upload one or more documents., Document (+13 more)

### Community 22 - "Metadata & Merge Stage Tests"
Cohesion: 0.15
Nodes (31): True when ``inner`` names the same section as ``outer`` or a subsection nested…, section_contains(), _body(), _chunk(), _heading(), _merge(), _mk(), _prov() (+23 more)

### Community 23 - "Query Rewrite & Summary Generators"
Cohesion: 0.15
Nodes (18): QueryRewriter, Build the prompt used to rewrite the latest user message into a standalone…, Convert structured conversation messages into a readable prompt format., Responsible for rewriting conversational user queries into standalone search…, Build the prompt used to generate or update the rolling conversation summary., Responsible for building prompts used to generate and maintain a rolling…, SummaryGenerator, Build the prompt used to generate a chat title. (+10 more)

### Community 24 - "Message API & ConversationService"
Cohesion: 0.11
Nodes (24): create_message(), BackgroundTasks, ConversationResponse, MessageCreate, Send a message and receive the assistant response., Stream an assistant response using Server-Sent Events (SSE)., stream_message(), ConversationService (+16 more)

### Community 25 - "Auth Dependency & Base Repository"
Cohesion: 0.09
Nodes (17): get_current_user(), Session, Return the currently authenticated user., AuthenticationError, Raised when authentication fails because the access token is invalid, expired,…, BaseRepository, Session, Base repository providing common CRUD operations. (+9 more)

### Community 26 - "Dense Qdrant Repository"
Cohesion: 0.08
Nodes (17): DenseRepository, HybridSearchResult, traceable, Create the Astra Study collection., Delete the Astra Study collection., Drop and recreate the collection. Useful during development., Insert or update points in the collection., Return the number of vectors stored in the collection. (+9 more)

### Community 27 - "Exception Hierarchy & App Entrypoint"
Cohesion: 0.10
Nodes (23): AppException, Exception, Initialize the exception. If no message is supplied, use the class-level…, Base exception for all application-specific errors., DocumentNotFoundError, DocumentTooLargeError, EmptyDocumentError, InvalidDocumentTypeError (+15 more)

### Community 28 - "Chat Repository & Service"
Cohesion: 0.10
Nodes (17): Create a new chat session., Rename a chat session., get_chat_service(), ChatService, ChatNotFoundError, Raised when the requested chat session does not exist or is inaccessible., ChatRepository, datetime (+9 more)

### Community 29 - "AccessContext Dependency & Tests"
Cohesion: 0.16
Nodes (22): get_access_context(), Session, Build the request-scoped authorization identity. Every field is derived…, Session, Return the ids of every team the given user is a member of. Selects only the…, Repository for TeamMembership database operations., TeamMembershipRepository, db() (+14 more)

### Community 30 - "Embedding & Hybrid Mappers"
Cohesion: 0.11
Nodes (17): EmbeddedChunk, Returns the chunk text., Returns the embedding dimensions., Represents a chunk together with its embedding. This object is produced by the…, Execute the complete embedding pipeline., Convenience wrapper. Allows pipeline(chunks) instead of pipeline.run(chunks), PointStruct, Convert multiple EmbeddedChunks into PointStructs. (+9 more)

### Community 31 - "CrossEncoder Reranker Base"
Cohesion: 0.10
Nodes (16): BaseReranker, ABC, Abstract interface for all rerankers. Every reranker implementation…, Abstract base class for reranking implementations., Returns the underlying reranker model name., Returns the execution device. Example ------- cpu cuda cuda:0 mps, Batch size used for inference., Maximum sequence length accepted by the reranker. (+8 more)

### Community 32 - "CrossEncoder Reranker Implementation"
Cohesion: 0.09
Nodes (15): CrossEncoderReranker, Automatically determine the best available inference device. Priority --------…, Name of the underlying HuggingFace model., Device used for inference., Batch size used during inference., Maximum sequence length accepted by the model., Returns the loaded CrossEncoder instance. This property is primarily useful for…, Validate the user query before inference. (+7 more)

### Community 33 - "BaseRetrievalService & Retrieval Tests"
Cohesion: 0.14
Nodes (20): ABC, BaseRetrievalService, RetrievalResult, Base contract for all retrieval implementations., Execute the complete retrieval pipeline. Retrieval is keyword-only and always…, Allow the service to be invoked like a function., RerankingResult, make_hybrid_result() (+12 more)

### Community 34 - "AIPipeline Orchestration"
Cohesion: 0.14
Nodes (17): AIResponse, AIPipeline, ChatMessage, StreamEvent, traceable, Stream an assistant response using Retrieval-Augmented Generation., Generate a short AI title for a new conversation., Generate or update the conversation summary. (+9 more)

### Community 35 - "OpenAI Embedder Exceptions"
Cohesion: 0.12
Nodes (20): traceable, Execute one embedding request. Retries automatically for transient OpenAI…, Embed a single batch of document chunks. Parameters ---------- chunks A batch…, Generate an embedding for a user query., Estimate embedding cost in USD. Cost is calculated using the official OpenAI…, EmbeddingCacheError, EmbeddingConfigurationError, EmbeddingError (+12 more)

### Community 36 - "RBAC SQLAlchemy Models"
Cohesion: 0.17
Nodes (15): Document, Base, TimestampMixin, Represents an uploaded document., SQLAlchemy ORM Models, Organisation, Base, TimestampMixin (+7 more)

### Community 37 - "Dense Search Mapper & Pipeline"
Cohesion: 0.12
Nodes (10): DenseMapper, ScoredPoint, Converts between Astra Study domain models and Qdrant models. Responsibilities…, Convert a Qdrant ScoredPoint into a DenseSearchResult., Convert multiple ScoredPoints into DenseSearchResults., DenseSearchResult, Represents one result returned from the dense vector search., DensePipeline (+2 more)

### Community 38 - "Reranking Exceptions"
Cohesion: 0.14
Nodes (16): Cross Encoder based reranker implementation. This module implements the…, Validate retrieval candidates before reranking., CandidateFormatError, EmptyCandidateError, InvalidQueryError, InvalidTopKError, ModelLoadError, PredictionError (+8 more)

### Community 39 - "RBAC-5B Propagation Tests"
Cohesion: 0.12
Nodes (24): make_conversation_service(), make_dense_repository_with_fake_client(), _persisted(), parametrize, Executable specification for RBAC-5B: threading the trusted AccessContext…, Requirement 13: whichever path is taken, retrieval sees the identical…, Requirements 9-12: no organisation_id / team_id / access_scope / role condition…, The dense and sparse RRF branches must never diverge in filtering. (+16 more)

### Community 40 - "RetrievalService & Integration Tests"
Cohesion: 0.12
Nodes (18): RetrievalResult, traceable, Execute the complete retrieval pipeline. Steps ----- 1. Validate query 2.…, Production Retrieval Orchestrator. Pipeline -------- User Query │ ▼ Hybrid…, Callable wrapper. Allows RetrievalService to be invoked like a function while…, Convert reranked search results into RetrievedContext objects consumed by…, RetrievalService, GenerationService (+10 more)

### Community 41 - "Frontend Chat Service & Workspace"
Cohesion: 0.18
Nodes (13): ChatService, Chat, Citation, _active_chat(), _client(), Refresh the sidebar chat list., Return the selected chat., Render workspace heading. (+5 more)

### Community 42 - "Reranking Integration Test"
Cohesion: 0.16
Nodes (22): preview_text(), print_header(), print_hybrid_results(), print_performance(), print_quality_benchmark(), print_rank_movements(), print_reranked_results(), print_reranking_statistics() (+14 more)

### Community 43 - "LLM Provider Base & Service"
Cohesion: 0.14
Nodes (12): BaseLLMProvider, ABC, Generate a complete response from the language model., Stream a response from the language model., Base interface for all LLM providers., OpenAIProvider, OpenAI implementation of the LLM provider., Generate a complete response using OpenAI. (+4 more)

### Community 44 - "Filter Stage & Noise Filters"
Cohesion: 0.17
Nodes (19): FilterStage, Removes only truly useless chunks. Philosophy ---------- Never remove…, is_copyright(), is_doi(), is_empty(), is_isbn(), is_numeric_only(), is_page_number() (+11 more)

### Community 45 - "Embedding Batcher & Dense Pipeline"
Cohesion: 0.18
Nodes (14): EmbeddingBatcher, Splits document chunks into batches suitable for the embedding provider. The…, OpenAIEmbedder, Generates OpenAI embeddings for DocumentChunks. Responsibilities…, EmbeddingPipeline, Production embedding pipeline. Pipeline DocumentChunks │ ▼ EmbeddingBatcher │ ▼…, PDFProcessor, Backward-compatible PDF processor. PDF ingestion is now handled by… (+6 more)

### Community 46 - "Dense Search Exceptions"
Cohesion: 0.13
Nodes (21): CollectionAlreadyExistsError, CollectionCreationError, CollectionDeletionError, CollectionNotFoundError, DenseSearchConfigurationError, DenseSearchError, InvalidPayloadError, InvalidSearchQueryError (+13 more)

### Community 47 - "Frontend API Client"
Cohesion: 0.16
Nodes (7): ApiClient, Any, Response, Download binary data., Open a Server-Sent Events POST request., Base HTTP client used by all frontend services., Execute an HTTP request.

### Community 48 - "Semantic Merge Stage Tests"
Cohesion: 0.20
Nodes (16): Narrow post-split cleanup. Responsibilities ---------------- - concatenate a…, SemanticStage, BlockProvenance, A compact, parser-neutral reference to the source of one block., _sc(), _sem_chunk(), test_semantic_caption_owns_following_text_still_works(), test_semantic_merge_deduplicates_shared_provenance() (+8 more)

### Community 49 - "Embedding Batcher & Validator"
Cohesion: 0.15
Nodes (11): Split chunks into embedding batches., Convenience wrapper allowing the batcher to be called directly., Embed multiple batches. Parameters ---------- batches List of EmbeddingBatch…, Convenience wrapper. Allows embedder(batches) instead of embedder.embed(batches), EmbeddingBatchError, Raised when an embedding batch is invalid. Examples: - Empty batch - Batch…, EmbeddingBatch, Represents a batch of chunks sent in a single embedding request. (+3 more)

### Community 50 - "Reranker Call & Hybrid Mapper"
Cohesion: 0.14
Nodes (12): Allows the reranker instance to be invoked like a function. Example -------…, Rerank retrieved candidates. Parameters ---------- query: User query.…, traceable, Callable wrapper. Example ------- >>> result = service( ... query=query, ...…, ScoredPoint, Convert a Qdrant ScoredPoint into a HybridSearchResult., Convert multiple ScoredPoints into HybridSearchResult objects., HybridSearchResponse (+4 more)

### Community 51 - "Embedding Vector & Validator"
Cohesion: 0.17
Nodes (14): Convert raw vectors returned by OpenAI into EmbeddedChunk objects., EmbeddingValidationError, Raised when an embedding fails validation. Examples: - Empty embedding -…, EmbeddingMetadata, EmbeddingVector, Represents a dense embedding vector generated by an embedding model. The vector…, Returns the embedding dimension., Metadata describing how an embedding was generated. Document metadata is… (+6 more)

### Community 52 - "Reranking Result Models"
Cohesion: 0.14
Nodes (10): slice, SupportsIndex, Returns the top-k reranked chunks. Parameters ---------- k: Number of chunks to…, Represents a single reranked retrieval result. Attributes ---------- result:…, Represents the complete output of the reranking stage. Attributes ----------…, Returns the highest ranked chunk., Returns all reranker scores., Returns the original retrieval scores. (+2 more)

### Community 53 - "Qdrant Isolation Conftest & Tests"
Cohesion: 0.16
Nodes (13): _isolate_qdrant_collection(), pytest_collection_modifyitems(), pytest_sessionfinish(), Test-wide Qdrant collection isolation. The integration tests drive…, Record whether this session collected any ``tests/integration`` test., Best-effort drop the dedicated test collection -- and only that collection --…, Pin every test to the dedicated Qdrant collection and return its name. Executed…, Offline safety regression for Qdrant test isolation. Guarantees the test… (+5 more)

### Community 54 - "Core Security (JWT/Password)"
Cohesion: 0.16
Nodes (9): Any, Handles password hashing, password verification, and JWT token generation., Decode and validate a JWT., Hash a plain-text password., Verify a password against its hash., Create an access token., Create a refresh token., SecurityManager (+1 more)

### Community 55 - "Frontend Sidebar & State"
Cohesion: 0.23
Nodes (14): _client(), _create_chat(), _load_chat(), Refresh chats and documents., Load a chat and its messages., Upload selected documents., Left navigation panel., _refresh_workspace() (+6 more)

### Community 56 - "Message Schemas & Service"
Cohesion: 0.19
Nodes (11): ConversationResponse, BaseModel, Response returned after sending a message. Contains both the persisted user…, MessageCreate, MessageResponse, BaseModel, Response schema representing a chat message., Request schema for sending a user message. (+3 more)

### Community 57 - "Document Validation Models"
Cohesion: 0.20
Nodes (9): DocumentValidator, Validates document-level metadata., Any, One metric produced by a validator., Output returned by every validator. Every validator returns exactly one…, Represents a non-fatal validation issue., ValidationMetric, ValidationResult (+1 more)

### Community 58 - "Generation Exceptions"
Cohesion: 0.21
Nodes (12): EmptyPromptError, GenerationError, GenerationTimeoutError, InvalidGenerationResponseError, Exception, Exceptions raised by the Generation module., Raised when prompt generation results in no messages., Raised when the configured LLM times out. (+4 more)

### Community 59 - "Frontend App Entry & Styles"
Cohesion: 0.22
Nodes (11): main(), _load_workspace(), login_screen(), Load chats and documents immediately after login., Render the login / registration page., Render the right-side panel., sources_panel(), initialize_session_state() (+3 more)

### Community 60 - "Sparse Search Exceptions"
Cohesion: 0.23
Nodes (11): Exception, Raised when the sparse encoder configuration is invalid., Base exception for all sparse search errors., Raised when a sparse vector collection operation fails., Raised when sparse retrieval fails., Raised when sparse embeddings cannot be generated., SparseCollectionError, SparseConfigurationError (+3 more)

### Community 61 - "LLMService Generation Methods"
Cohesion: 0.17
Nodes (6): Convert provider-agnostic messages into the format expected by the LLM provider., Generate an assistant response., Generate a concise title., Generate or update a rolling conversation summary., Rewrite the latest user query into a standalone retrieval query., Stream an assistant response.

### Community 62 - "CLAUDE.md Project Overview"
Cohesion: 0.18
Nodes (12): alembic/ (DB migrations), app/ (FastAPI backend), Astra Study, ConversationService (app/services/conversation.py), evaluation/ (LangSmith + chunking report), frontend/ (Streamlit UI), LangSmith tracing, PostgreSQL (SQLAlchemy 2.0 + Alembic) (+4 more)

### Community 63 - "CLAUDE.md Chunking Contract Notes"
Cohesion: 0.29
Nodes (12): evaluation/chunking_report.py (offline structural evaluator), ChunkingConfig (app/chunking/config.py), ChunkPipeline (app/chunking/pipeline.py), FilterStage, FinalizeStage, MergeStage, MetadataStage, ParagraphStage (+4 more)

### Community 64 - "Frontend Message Service & Models"
Cohesion: 0.35
Nodes (4): MessageService, Yield assistant text chunks from the message SSE endpoint., Conversation, Message

### Community 65 - "FinalizeStage UUID Assignment"
Cohesion: 0.31
Nodes (5): FinalizeStage, UUID, Generate a deterministic UUID for every chunk. UUIDs must satisfy: • Stable…, Final stage executed before embeddings. Responsibilities ---------------- •…, Normalize page/block ranges. Pages should always be ascending. Block ranges are…

### Community 66 - "PromptBuilder"
Cohesion: 0.24
Nodes (7): PromptBuilder, traceable, Convert retrieved contexts into a formatted block., Build the optional long-term conversation summary., Convert conversation history into LLM messages. The latest user message is…, Builds provider-agnostic prompts for the Generation layer. Responsibilities…, Build the complete prompt sent to the LLM.

### Community 67 - "Frontend Auth & User Models"
Cohesion: 0.33
Nodes (4): TokenResponse, ApiResponse, Standard API response returned by Astra Study., User

### Community 68 - "Search Import Isolation Tests"
Cohesion: 0.24
Nodes (9): CompletedProcess, parametrize, Regression test for a circular import discovered during the RBAC-5B independent…, Reproduces the exact import order used by ``scripts/reingest_document.py``…, Run ``code`` in a brand-new Python process with no inherited ``sys.modules``…, Each of these must be importable as the very first thing a fresh process does…, _run_in_fresh_process(), test_reingest_document_script_import_sequence_succeeds_in_fresh_process() (+1 more)

### Community 69 - "Storage Path Helpers"
Cohesion: 0.22
Nodes (5): Path, Return the absolute path of a stored file., Path, UploadFile, Save an uploaded file.

### Community 70 - "CLAUDE.md Retrieval Components Notes"
Cohesion: 0.25
Nodes (9): DenseRepository (COLLECTION_NAME), get_current_user (app/dependencies/auth.py), HybridPipeline (app/search/hybrid/pipeline.py), LLMService (OpenAI-backed), Qdrant (vector store), Qdrant integration-test production-collection hazard, RerankingService (CrossEncoder), RetrievalService (+1 more)

### Community 71 - "Frontend API Client & Auth"
Cohesion: 0.39
Nodes (4): ApiException, Exception, Raised when the backend returns an error response., AuthService

### Community 72 - "API Response Schemas"
Cohesion: 0.36
Nodes (6): success_response(), ApiResponse, ErrorResponse, BaseModel, Standard error API response., Standard success API response.

### Community 73 - "ConversationSummaryService"
Cohesion: 0.29
Nodes (5): ConversationSummaryService, traceable, Maintains a rolling AI-generated summary for long conversations. Lifecycle…, How many conversational messages the stored summary already reflects., Generate or refresh the conversation summary if it is due. Safe to call after…

### Community 74 - "CLAUDE.md Conversation Memory Notes"
Cohesion: 0.29
Nodes (8): AIPipeline (app/ai/pipeline.py), Citation ordering score formula, GenerationService.citations_for, Conversation memory (rolling summary + recent window), ConversationSummaryService, GenerationService (app/generation/service.py), prompt_builder (app/generation/prompt_builder.py), SummaryGenerator

### Community 75 - "CLAUDE.md Ingestion & Citation Notes"
Cohesion: 0.25
Nodes (8): BlockProvenance (app/document/models.py), Citation (app/generation/models.py, frozen dataclass), Docling (ingestion library), DoclingProcessor (app/ingestion/processors/docling.py), DocumentBlock, ExtractionResult, IngestionService, ProcessorFactory (app/ingestion/factory.py)

### Community 76 - "Health Check Endpoint"
Cohesion: 0.38
Nodes (5): health_check(), get, HealthResponse, BaseModel, Response model for the health check endpoint.

### Community 77 - "Document Parser"
Cohesion: 0.29
Nodes (4): DocumentParser, Token, Parse Markdown into tokens., Parses Markdown into Markdown-It tokens. This class is intentionally…

### Community 78 - "Embedding Chunk UUID Fields"
Cohesion: 0.29
Nodes (4): UUID, Returns the UUIDs of all chunks contained in the batch., Returns the chunk UUID., Returns the document UUID.

### Community 79 - "RBAC Test Fake Storage Service"
Cohesion: 0.29
Nodes (4): FakeStorageService, BaseStorageService, Path, In-memory stand-in for LocalStorageService -- no filesystem access, so this…

### Community 80 - "OpenAI Client Init"
Cohesion: 0.40
Nodes (3): get_openai_client(), Create and return an OpenAI client. The client is configured using application…, OpenAI

### Community 81 - "Dense Search Response Model"
Cohesion: 0.33
Nodes (4): DenseSearchResponse, Represents the complete response returned from the dense search pipeline., Number of retrieved results., Highest similarity score.

### Community 82 - "Legacy Document Validator"
Cohesion: 0.33
Nodes (4): DocumentValidator, UploadFile, Validates uploaded documents before they are stored on disk., Validate an uploaded document. Raises ------ HTTPException If validation fails.

### Community 83 - "Alembic Env Migration Runner"
Cohesion: 0.40
Nodes (4): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online()

### Community 84 - "OpenAI Model Enum"
Cohesion: 0.50
Nodes (4): OpenAIModel, Enum, str, Supported OpenAI chat models.

### Community 85 - "Get Messages Endpoint"
Cohesion: 0.40
Nodes (5): get_messages(), MessageService, Retrieve all messages for a chat session., get, MessageResponse

### Community 86 - "HybridService Init & Retrieval Comparison"
Cohesion: 0.40
Nodes (4): OpenAIEmbedder, SparseEncoder, Compare Dense Retrieval vs Hybrid Retrieval using the same indexed document., test_retrieval_comparison()

### Community 87 - "README Feature List"
Cohesion: 0.40
Nodes (5): Astra Study (README overview), Guardrails, LangGraph, OCR / Vision-based Document Understanding, OpenAI GPT-5 / GPT-5 Vision

### Community 94 - "App Settings (pydantic-settings)"
Cohesion: 0.67
Nodes (3): Application settings loaded from environment variables., Settings, BaseSettings

### Community 96 - "APJ Speech Fixture Upload"
Cohesion: 1.00
Nodes (3): A P J Abdul Kalam Departing Speech (upload 510fce33), A P J Abdul Kalam Departing Speech, Developed India 2020

## Knowledge Gaps
- **47 isolated node(s):** `astra-study`, `Multi-head attention`, `Scaled dot-product attention`, `pre_apjspeech.txt (pre-refactor report)`, `pre_LLM.txt (pre-refactor report)` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 853 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DocumentChunk` connect `Merge/Quality Stage Tests` to `FinalizeStage UUID Assignment`, `Offline Chunking Evaluator`, `OpenAI Embedder Exceptions`, `Chunk Pipeline Contract Tests`, `Recursive Split & Tokenizer Utils`, `Dense Search Mapper & Pipeline`, `Chunk Pipeline & Stages`, `Filter Stage & Noise Filters`, `Embedding Batcher & Dense Pipeline`, `AccessContext & Hybrid Search Tests`, `Sparse Encoder & Hybrid Pipeline`, `Semantic Merge Stage Tests`, `Embedding Batcher & Validator`, `Embedding Vector & Validator`, `Metadata & Merge Stage Tests`, `Document Validation Models`, `Embedding & Hybrid Mappers`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `get_documents()` connect `Document API & Ingestion Service` to `Chat API & Document Upload`, `Frontend Document Service & Sources`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `Retrieve all uploaded documents.` connect `Frontend Document Service & Sources` to `Document API & Ingestion Service`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `DocumentChunk` (e.g. with `ChunkPipeline` and `BaseChunkStage`) actually correct?**
  _`DocumentChunk` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 90 inferred relationships involving `BlockType` (e.g. with `ChunkMetadata` and `ContentSegment`) actually correct?**
  _`BlockType` has 90 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `User` (e.g. with `create_chat()` and `delete_chat()`) actually correct?**
  _`User` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `AccessContext` (e.g. with `AIPipeline` and `create_message()`) actually correct?**
  _`AccessContext` has 11 INFERRED edges - model-reasoned connections that need verification._