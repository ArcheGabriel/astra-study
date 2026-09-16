# Graph Report - Astra-Study  (2026-09-16)

## Corpus Check
- 18 files · ~235,297 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2532 nodes · 6054 edges · 177 communities (102 shown, 40 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 522 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Docling Block Handlers
- Chunk Pipeline Contract Tests
- Service Dependency Wiring & AI Pipeline Init
- ConversationService & Memory Tests
- Offline Chunking Evaluator
- Recursive Split & Tokenizer Utils
- Storage Service Base
- Chunk Pipeline & Stages
- Merge/Quality Stage Tests
- Embedding Batcher & OpenAI Embedder
- Dense Repository Authorization & Delete
- Sparse Encoder & Hybrid Pipeline
- RBAC-5D Document Authorization Test Fixtures
- Evaluation Fixtures & Test Documents
- Message API & Service
- Citation Generation & Scoring
- Evaluation Predictor
- AccessContext & Hybrid Search Tests
- Hybrid Search Mapper
- LangSmith Evaluation Harness
- Chat Repository & Service
- AccessContext Dependency & Tests
- CrossEncoder Reranker Base
- Dense Search Mapper & Pipeline
- Metadata & Merge Stage Tests
- RBAC SQLAlchemy Models
- Document Repository & Access Dependency
- Auth API & User Service
- Auth Dependency & Base Repository
- OpenAI Embedder Exceptions
- Embedding Batcher & Dense Pipeline
- Grant Admin Script & RBAC-5D Tests
- Citation & Provenance Tests
- Document API Routes
- Chat/Message Models & Repositories
- Dense Qdrant Repository
- Reranking Result Models
- Retrieval Formatter & Exceptions
- Reranking Exceptions
- AIPipeline Orchestration
- LLM Provider Base & Service
- Reranking Integration Test
- Query Rewrite & Summary Generators
- Merge/Quality Stage Tests
- CrossEncoder Reranker Implementation
- Dense Search Exceptions
- Frontend API Client
- Frontend Document Service & Sources
- Chat API & Document Upload
- Exception Hierarchy & App Entrypoint
- Message API & ConversationService
- Docling Ingestion Processor
- Citation & Provenance Tests
- LLMService Generation Methods
- DocumentService Authorization Logic
- CLAUDE.md Architecture Concepts
- Frontend API Client & Auth
- Qdrant Isolation Conftest & Tests
- BaseRetrievalService & Retrieval Tests
- Filter Stage & Noise Filters
- Core Security (JWT/Password)
- Docling Ingestion Processor
- Retrieval Formatter & Exceptions
- CLAUDE.md Project Overview
- Frontend Sidebar & State
- Semantic Merge Stage Tests
- Document Validation Models
- Query Rewrite & Summary Generators
- Generation Exceptions
- Docling Ingestion Processor
- Frontend App Entry & Styles
- Frontend Chat Service & Workspace
- BaseRetrievalService & Retrieval Tests
- PromptBuilder
- Auth Dependency & Base Repository
- Sparse Search Exceptions
- CLAUDE.md Chunking Contract Notes
- Frontend Auth & User Models
- Frontend Message Service & Models
- Exception Hierarchy & App Entrypoint
- Document API & Ingestion Service
- Document Repository Visibility Queries
- Retrieval Formatter & Exceptions
- Search Import Isolation Tests
- Frontend Chat Service & Workspace
- Citation & Provenance Tests
- Docling Ingestion Processor
- Auth API & User Service
- CLAUDE.md Retrieval Components Notes
- API Response Schemas
- RetrievalService & Integration Tests
- ConversationSummaryService
- Health Check Endpoint
- Document Parser
- CrossEncoder Reranker Implementation
- Dense Search Response Model
- Legacy Document Validator
- Alembic Env Migration Runner
- OpenAI Model Enum
- Citation & Provenance Tests
- Dependency Injection Wiring
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
- Message GET Route Marker
- Message POST Route Marker
- Dependency Injection Wiring
- Chat Repository & Service
- Dependency Injection Wiring
- Dependency Injection Wiring
- Retrieval Base ABC Marker
- Dense Qdrant Repository
- Reranker Call & Hybrid Mapper
- User Service Type Marker
- Docker Compose Config
- RBAC Team Membership & Foundation Tests
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

## God Nodes (most connected - your core abstractions)
1. `DocumentChunk` - 140 edges
2. `BlockType` - 113 edges
3. `DocumentBlock` - 51 edges
4. `AccessContext` - 45 edges
5. `User` - 45 edges
6. `count_tokens()` - 45 edges
7. `DenseRepository` - 40 edges
8. `ApiClient` - 37 edges
9. `BlockProvenance` - 37 edges
10. `ChunkPipeline` - 34 edges

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
- **Conversation memory rolling-summary mechanism** — claude_md_conversationservice, claude_md_conversationsummaryservice, claude_md_summarygenerator, claude_md_aipipeline, claude_md_conversation_memory [EXTRACTED 1.00]
- **Retrieval + generation request flow** — claude_md_aipipeline, claude_md_retrievalservice, claude_md_rerankingservice, claude_md_generationservice, claude_md_promptbuilder [EXTRACTED 1.00]

## Communities (177 total, 40 thin omitted)

### Community 0 - "Docling Block Handlers"
Cohesion: 0.07
Nodes (48): DocumentConverter, Token, Converts Markdown-It tokens into semantic DocumentBlocks. The converter itself…, Convert Markdown tokens into semantic DocumentBlocks., BaseHandler, HandlerResult, ABC, Token (+40 more)

### Community 1 - "Chunk Pipeline Contract Tests"
Cohesion: 0.08
Nodes (72): BlockType, Represents the semantic type of a document block. This enum is parser-…, DocumentMetadata, Metadata extracted from a document., StrEnum, _chunk(), _distinct(), _list_blocks() (+64 more)

### Community 2 - "Service Dependency Wiring & AI Pipeline Init"
Cohesion: 0.06
Nodes (65): build_conversation_summary_service(), get_ai_pipeline(), get_auth_service(), get_chat_service(), get_conversation_service(), get_conversation_summary_service(), get_document_service(), get_generation_service() (+57 more)

### Community 3 - "ConversationService & Memory Tests"
Cohesion: 0.07
Nodes (55): MessageService, ChatRepository, GenerationResponse, MessageRepository, RetrievedContext, add_messages(), db(), _FakeLLM (+47 more)

### Community 4 - "Offline Chunking Evaluator"
Cohesion: 0.07
Nodes (68): analyze(), _block_from_dict(), _block_range_valid(), _block_to_dict(), _chunk_body(), compare(), _dig(), _expected_prefix() (+60 more)

### Community 5 - "Recursive Split & Tokenizer Utils"
Cohesion: 0.06
Nodes (42): _is_markdown_separator(), _norm(), Compact heading context: the deepest heading normally, or the deepest two…, Recover the source segments (one per contributing block) from the merged chunk…, The text a pass-through chunk would carry with ``prefix`` present exactly once.…, A markdown table separator row, e.g. ``| --- | :--: |``., Text of each child (before the heading prefix), plus -- for the structural…, Pack whole list items into child bodies, never dividing one. A single item… (+34 more)

### Community 6 - "Storage Service Base"
Cohesion: 0.06
Nodes (44): BaseStorageService, ABC, Path, UploadFile, Save a file and return: ( stored_filename, file_size, ), Delete a stored file., Return the absolute path of a stored file., Base interface for all storage providers. (+36 more)

### Community 7 - "Chunk Pipeline & Stages"
Cohesion: 0.09
Nodes (30): ContentSegment, One source ``DocumentBlock`` that ``MergeStage`` folded into a chunk. Internal…, ChunkPipeline, Executes the configured chunking stages., BaseChunkStage, ABC, Process the incoming data and return chunks., Base interface for every chunking stage. (+22 more)

### Community 8 - "Merge/Quality Stage Tests"
Cohesion: 0.07
Nodes (42): ChunkMetadata, DocumentChunk, Represents one chunk that will eventually be embedded and stored in the vector…, Metadata associated with a document chunk. This metadata flows through the…, FinalizeStage, UUID, Generate a deterministic UUID for every chunk. UUIDs must satisfy: • Stable…, Final stage executed before embeddings. Responsibilities ---------------- •… (+34 more)

### Community 9 - "Embedding Batcher & OpenAI Embedder"
Cohesion: 0.06
Nodes (35): Split chunks into embedding batches., Convenience wrapper allowing the batcher to be called directly., Convert raw vectors returned by OpenAI into EmbeddedChunk objects., Embed a single batch of document chunks. Parameters ---------- chunks A batch…, Embed multiple batches. Parameters ---------- batches List of EmbeddingBatch…, Convenience wrapper. Allows embedder(batches) instead of embedder.embed(batches), EmbeddingBatchError, EmbeddingValidationError (+27 more)

### Community 10 - "Dense Repository Authorization & Delete"
Cohesion: 0.12
Nodes (47): AccessContext, Filter, HybridSearchResult, Delete every point belonging to one schema_version=3 document. Scoped…, Build the document-visibility filter for ``access``. Structural constraints…, Execute native Qdrant Hybrid Search using Reciprocal Rank Fusion (RRF).…, MatchAny, _branch_count() (+39 more)

### Community 11 - "Sparse Encoder & Hybrid Pipeline"
Cohesion: 0.06
Nodes (20): HybridPipeline, Production Hybrid Indexing Pipeline. Responsibilities ----------------…, Index document chunks using hybrid dense+sparse vectors., traceable, Generate sparse embedding for a user query., Generates sparse embeddings for document chunks using FastEmbed.…, Generate sparse embeddings for document chunks., SparseEncoder (+12 more)

### Community 12 - "RBAC-5D Document Authorization Test Fixtures"
Cohesion: 0.17
Nodes (43): TeamRole, build_access(), make_document(), make_document_service(), make_membership(), make_organisation(), make_team(), make_user() (+35 more)

### Community 13 - "Evaluation Fixtures & Test Documents"
Cohesion: 0.06
Nodes (38): baseline_apjspeech.txt (commit 888fc8c report), baseline_Attention.txt (commit 888fc8c report), baseline_LLM.txt (commit 888fc8c report), comparison.txt (baseline vs stage14 deltas), comparison_stage5_to_stage6.txt (Stage 6 primary comparison), apjspeech.pdf (eval corpus doc), Attention.pdf (eval corpus doc), LLM.pdf (eval corpus doc) (+30 more)

### Community 14 - "Message API & Service"
Cohesion: 0.10
Nodes (30): create_message(), get_messages(), BackgroundTasks, ConversationResponse, MessageCreate, MessageService, Retrieve all messages for a chat session., Send a message and receive the assistant response. (+22 more)

### Community 15 - "Citation Generation & Scoring"
Cohesion: 0.10
Nodes (30): BaseGenerationService, ABC, Abstract interface for the Generation layer. Implementations are responsible…, Generate a complete response., Stream the generated response. Each yielded string represents the next chunk of…, EmptyResponseError, Raised when the LLM returns an empty response., Citation (+22 more)

### Community 16 - "Evaluation Predictor"
Cohesion: 0.11
Nodes (30): EvaluationPredictor, AccessContext, AIPipeline, Executes Astra Study's production AI pipeline for LangSmith evaluation. This…, ``access`` is resolved once from the real database-backed User/TeamMembership…, Executes the production AI pipeline for a single evaluation example., EvaluationService, AccessContext (+22 more)

### Community 17 - "AccessContext & Hybrid Search Tests"
Cohesion: 0.10
Nodes (21): Application settings loaded from environment variables., Settings, HybridService, HybridSearchResult, traceable, Production Hybrid Retriever. Responsibilities ---------------- • Generate dense…, Execute Hybrid Retrieval., BaseSettings (+13 more)

### Community 18 - "Hybrid Search Mapper"
Cohesion: 0.12
Nodes (28): HybridMapper, EmbeddedChunk, HybridSearchResult, PointStruct, Combine dense and sparse representations into a single hybrid Qdrant point., Converts Astra Study domain models into hybrid Qdrant PointStruct objects.…, Convert dense and sparse chunk collections into hybrid PointStructs. Both lists…, Convert a Qdrant ScoredPoint into a HybridSearchResult. (+20 more)

### Community 19 - "LangSmith Evaluation Harness"
Cohesion: 0.10
Nodes (21): answer_length(), citation_count(), exact_match(), Any, Exact answer match. Useful as a fast deterministic baseline., Records answer length. Helpful for spotting prompt regressions., Counts returned citations., FixtureManager (+13 more)

### Community 20 - "Chat Repository & Service"
Cohesion: 0.11
Nodes (19): delete_chat(), delete, Response, Delete a chat session., ChatNotFoundError, Raised when the requested chat session does not exist or is inaccessible., ChatSession, Represents a chat session belonging to a user. (+11 more)

### Community 21 - "AccessContext Dependency & Tests"
Cohesion: 0.14
Nodes (31): get_access_context(), Session, Build the request-scoped authorization identity. Every field is derived…, OrgRole, Enum, str, A user's organisation-scoped role. Distinct from document access scope -- role…, AccessContext (+23 more)

### Community 22 - "CrossEncoder Reranker Base"
Cohesion: 0.09
Nodes (21): BaseReranker, ABC, Abstract interface for all rerankers. Every reranker implementation…, Abstract base class for reranking implementations., Returns the underlying reranker model name., Returns the execution device. Example ------- cpu cuda cuda:0 mps, Batch size used for inference., Maximum sequence length accepted by the reranker. (+13 more)

### Community 23 - "Dense Search Mapper & Pipeline"
Cohesion: 0.10
Nodes (14): DenseMapper, PointStruct, ScoredPoint, Convert multiple EmbeddedChunks into PointStructs., Converts between Astra Study domain models and Qdrant models. Responsibilities…, Convert a Qdrant ScoredPoint into a DenseSearchResult., Convert multiple ScoredPoints into DenseSearchResults., Convert one EmbeddedChunk into a Qdrant PointStruct. (+6 more)

### Community 24 - "Metadata & Merge Stage Tests"
Cohesion: 0.16
Nodes (30): True when ``inner`` names the same section as ``outer`` or a subsection nested…, section_contains(), _body(), _heading(), _merge(), _mk(), _prov(), Run the first real stages that shape section chunks: Metadata -> Merge. Input… (+22 more)

### Community 25 - "RBAC SQLAlchemy Models"
Cohesion: 0.14
Nodes (21): Enum, str, A user's role within a single team membership. Independent of ``OrgRole``: a…, TeamRole, Document, Base, TimestampMixin, Represents an uploaded document. (+13 more)

### Community 26 - "Document Repository & Access Dependency"
Cohesion: 0.11
Nodes (17): DocumentRepository, Session, Repository for Document database operations., Session, TeamMembership, Return the ids of every team the given user is a member of. Selects only the…, Return the membership row for one (user, team) pair, if any. Used to resolve…, Repository for TeamMembership database operations. (+9 more)

### Community 27 - "Auth API & User Service"
Cohesion: 0.12
Nodes (24): login(), oauth2_login(), post, Authenticate a user using JSON. Used by the frontend., OAuth2-compatible login endpoint. Swagger sends: username password We interpret…, register(), get_current_user_profile(), get (+16 more)

### Community 28 - "Auth Dependency & Base Repository"
Cohesion: 0.11
Nodes (18): get_current_user(), Session, Return the currently authenticated user., AuthenticationError, InactiveUserError, InvalidCredentialsError, Raised when an inactive user attempts to log in., Raised when authentication fails because the access token is invalid, expired,… (+10 more)

### Community 29 - "OpenAI Embedder Exceptions"
Cohesion: 0.11
Nodes (21): get_openai_client(), Create and return an OpenAI client. The client is configured using application…, traceable, Execute one embedding request. Retries automatically for transient OpenAI…, Generate an embedding for a user query., EmbeddingCacheError, EmbeddingConfigurationError, EmbeddingError (+13 more)

### Community 30 - "Embedding Batcher & Dense Pipeline"
Cohesion: 0.13
Nodes (16): EmbeddingBatcher, Splits document chunks into batches suitable for the embedding provider. The…, OpenAIEmbedder, Generates OpenAI embeddings for DocumentChunks. Responsibilities…, Estimate embedding cost in USD. Cost is calculated using the official OpenAI…, EmbeddingPipeline, Production embedding pipeline. Pipeline DocumentChunks │ ▼ EmbeddingBatcher │ ▼…, Execute the complete embedding pipeline. (+8 more)

### Community 31 - "Grant Admin Script & RBAC-5D Tests"
Cohesion: 0.12
Nodes (25): grant_admin(), main(), Promote an existing user to OrgRole.ADMIN, by email. uv run python -m…, Promote the user with ``email`` to ADMIN. Returns a process exit code., db(), make_dense_repository_with_fake_client(), _patched_session_local(), fixture (+17 more)

### Community 32 - "Citation & Provenance Tests"
Cohesion: 0.12
Nodes (27): _context(), Provenance propagation: Docling → block → chunk → vector payload → retrieval…, Analogous case with different headings, proving the mechanism is not hardcoded…, Without any structural overlap with the query, citation order must fall back to…, A bare heading chunk is too short to score -- it must come back `None`…, Proves the heading signal is discounted, not disabled: a title that carries a…, _reranked(), test_answer_grounding_keeps_chunks_distinct_and_provenance_intact() (+19 more)

### Community 33 - "Document API Routes"
Cohesion: 0.10
Nodes (23): delete_document(), download_document(), get_document(), get_documents(), AccessContext, DocumentResponse, UploadFile, User (+15 more)

### Community 34 - "Chat/Message Models & Repositories"
Cohesion: 0.11
Nodes (16): Base, Base class for all SQLAlchemy ORM models., ChatMessage, Represents a single message within a chat session., Adds automatic timestamp fields to database models., TimestampMixin, MessageRepository, datetime (+8 more)

### Community 35 - "Dense Qdrant Repository"
Cohesion: 0.10
Nodes (14): DenseRepository, PointStruct, Create the Astra Study collection., Delete the Astra Study collection., Drop and recreate the collection. Useful during development., Insert or update points in the collection., Return the number of vectors stored in the collection., Scroll through stored points. Useful for debugging. (+6 more)

### Community 36 - "Reranking Result Models"
Cohesion: 0.10
Nodes (14): Allows the reranker instance to be invoked like a function. Example -------…, Rerank retrieved candidates. Parameters ---------- query: User query.…, slice, SupportsIndex, Returns the top-k reranked chunks. Parameters ---------- k: Number of chunks to…, Represents a single reranked retrieval result. Attributes ---------- result:…, Represents the complete output of the reranking stage. Attributes ----------…, Returns the highest ranked chunk. (+6 more)

### Community 37 - "Retrieval Formatter & Exceptions"
Cohesion: 0.15
Nodes (17): slice, SupportsIndex, Return unique section names while preserving retrieval order., Represents a single document chunk after the complete retrieval pipeline…, Final output returned by the RetrievalService., Return unique document sources while preserving retrieval order., RetrievalResult, RetrievedContext (+9 more)

### Community 38 - "Reranking Exceptions"
Cohesion: 0.14
Nodes (15): Cross Encoder based reranker implementation. This module implements the…, CandidateFormatError, EmptyCandidateError, InvalidQueryError, InvalidTopKError, ModelLoadError, PredictionError, Exception (+7 more)

### Community 39 - "AIPipeline Orchestration"
Cohesion: 0.17
Nodes (15): AIResponse, AIPipeline, ChatMessage, StreamEvent, traceable, Stream an assistant response using Retrieval-Augmented Generation., Generate a short AI title for a new conversation., Generate or update the conversation summary. (+7 more)

### Community 40 - "LLM Provider Base & Service"
Cohesion: 0.13
Nodes (14): BaseLLMProvider, ABC, Generate a complete response from the language model., Stream a response from the language model., Base interface for all LLM providers., OpenAIProvider, OpenAI implementation of the LLM provider., Generate a complete response using OpenAI. (+6 more)

### Community 41 - "Reranking Integration Test"
Cohesion: 0.16
Nodes (22): preview_text(), print_header(), print_hybrid_results(), print_performance(), print_quality_benchmark(), print_rank_movements(), print_reranked_results(), print_reranking_statistics() (+14 more)

### Community 42 - "Query Rewrite & Summary Generators"
Cohesion: 0.17
Nodes (11): AIResponse, Response returned by the AI orchestration layer. This model is intentionally…, MessageRole, Enum, str, Represents the sender of a chat message., Internal streaming event; text and citations never share a payload., Token usage statistics returned by the LLM provider. (+3 more)

### Community 43 - "Merge/Quality Stage Tests"
Cohesion: 0.12
Nodes (13): ChunkingConfig, Single source of truth for the chunking pipeline's size limits. Every value is…, MergeStage, Group neighbouring blocks into heading-anchored *section* chunks. Boundaries…, One ContentSegment for a source block as it enters MergeStage (each chunk is…, Emit ``builder`` -- unless it only ever held a heading (or nothing), in which…, Start a new section chunk. Every metadata field is preserved by deep-copying…, Decide whether ``incoming`` starts a new section chunk. (+5 more)

### Community 44 - "CrossEncoder Reranker Implementation"
Cohesion: 0.11
Nodes (12): CrossEncoderReranker, Name of the underlying HuggingFace model., Device used for inference., Batch size used during inference., Maximum sequence length accepted by the model., Validate the user query before inference., Validate the requested top_k value., Validate retrieval candidates before reranking. (+4 more)

### Community 45 - "Dense Search Exceptions"
Cohesion: 0.13
Nodes (21): CollectionAlreadyExistsError, CollectionCreationError, CollectionDeletionError, CollectionNotFoundError, DenseSearchConfigurationError, DenseSearchError, InvalidPayloadError, InvalidSearchQueryError (+13 more)

### Community 46 - "Frontend API Client"
Cohesion: 0.16
Nodes (7): ApiClient, Any, Response, Download binary data., Open a Server-Sent Events POST request., Base HTTP client used by all frontend services., Execute an HTTP request.

### Community 47 - "Frontend Document Service & Sources"
Cohesion: 0.13
Nodes (14): BinaryIO, DocumentService, Service responsible for all document-related operations., Download the original uploaded document., Retrieve metadata for a single document., Upload one or more documents., Document, Create an authenticated API client. (+6 more)

### Community 48 - "Chat API & Document Upload"
Cohesion: 0.16
Nodes (18): create_chat(), get_chat(), list_chats(), get, post, Create a new chat session., Return all chat sessions belonging to the current user., Return a chat session. (+10 more)

### Community 49 - "Exception Hierarchy & App Entrypoint"
Cohesion: 0.14
Nodes (16): AppException, Exception, Initialize the exception. If no message is supplied, use the class-level…, Base exception for all application-specific errors., DocumentNotFoundError, DocumentTooLargeError, EmptyDocumentError, InvalidDocumentTypeError (+8 more)

### Community 50 - "Message API & ConversationService"
Cohesion: 0.17
Nodes (13): BackgroundTasks, ChatMessage, ChatSession, ConversationResponse, MessageCreate, StreamEvent, traceable, Stream an AI response while persisting the final assistant message.… (+5 more)

### Community 51 - "Docling Ingestion Processor"
Cohesion: 0.19
Nodes (11): FailingConverter, FakeConverter, FakeDocument, FakeItem, parametrize, test_corrupt_or_empty_docling_output_fails_cleanly(), test_docling_bbox_and_table_provenance_survive_chunking(), test_docling_conversion_failure_is_sanitized() (+3 more)

### Community 52 - "Citation & Provenance Tests"
Cohesion: 0.15
Nodes (11): _extract(), FakeBBox, FakeConverter, FakeDocument, FakeItem, FakeProv, test_chunking_preserves_provenance(), test_docx_heading_section_without_page() (+3 more)

### Community 53 - "LLMService Generation Methods"
Cohesion: 0.15
Nodes (11): Build the prompt used to generate a chat title., Responsible for generating prompts used to create chat titles., TitleGenerator, LLMMessage, Provider-agnostic message exchanged between the Prompt Builder and the LLM…, Convert provider-agnostic messages into the format expected by the LLM provider., Generate an assistant response., Generate a concise title. (+3 more)

### Community 54 - "DocumentService Authorization Logic"
Cohesion: 0.12
Nodes (12): AccessContext, Document, DocumentResponse, Path, UploadFile, User, Retrieve a single document, if ``access`` is authorized to see it. Unauthorized…, Delete a document, its Qdrant vectors, and its stored file -- only if… (+4 more)

### Community 55 - "CLAUDE.md Architecture Concepts"
Cohesion: 0.12
Nodes (17): AIPipeline (app/ai/pipeline.py), BlockProvenance (app/document/models.py), Citation (app/generation/models.py, frozen dataclass), Citation ordering score formula, GenerationService.citations_for, Conversation memory (rolling summary + recent window), ConversationService (app/services/conversation.py), ConversationSummaryService (+9 more)

### Community 56 - "Frontend API Client & Auth"
Cohesion: 0.22
Nodes (8): ApiException, Exception, Raised when the backend returns an error response., AuthService, _normalize_heading_path(), Presentation-only cleanup: collapse consecutive duplicate heading entries (e.g.…, Display retrieved citations., _render_citations()

### Community 57 - "Qdrant Isolation Conftest & Tests"
Cohesion: 0.16
Nodes (13): _isolate_qdrant_collection(), pytest_collection_modifyitems(), pytest_sessionfinish(), Test-wide Qdrant collection isolation. The integration tests drive…, Record whether this session collected any ``tests/integration`` test., Best-effort drop the dedicated test collection -- and only that collection --…, Pin every test to the dedicated Qdrant collection and return its name. Executed…, Offline safety regression for Qdrant test isolation. Guarantees the test… (+5 more)

### Community 58 - "BaseRetrievalService & Retrieval Tests"
Cohesion: 0.19
Nodes (10): ABC, BaseRetrievalService, RetrievalResult, Base contract for all retrieval implementations., Execute the complete retrieval pipeline. Retrieval is keyword-only and always…, Allow the service to be invoked like a function., Production Retrieval Orchestrator. Pipeline -------- User Query │ ▼ Hybrid…, RetrievalService (+2 more)

### Community 59 - "Filter Stage & Noise Filters"
Cohesion: 0.25
Nodes (13): is_copyright(), is_doi(), is_empty(), is_isbn(), is_numeric_only(), is_page_number(), is_punctuation_only(), is_short_noise() (+5 more)

### Community 60 - "Core Security (JWT/Password)"
Cohesion: 0.16
Nodes (9): Any, Handles password hashing, password verification, and JWT token generation., Decode and validate a JWT., Hash a plain-text password., Verify a password against its hash., Create an access token., Create a refresh token., SecurityManager (+1 more)

### Community 61 - "Docling Ingestion Processor"
Cohesion: 0.21
Nodes (8): ExtractedTable, Represents one extracted table. Future parsers (Docling etc.) will populate…, DoclingProcessor, Any, Path, Map Docling's public ``item.prov`` records without assuming all converters…, Convert every supported upload into Astra Study's existing block contract., Return unique page numbers while preserving retrieval order.

### Community 62 - "Retrieval Formatter & Exceptions"
Cohesion: 0.21
Nodes (11): ContextFormattingError, Raised when retrieved contexts cannot be formatted for downstream generation., ContextFormatter, Formats retrieved contexts into different representations suitable for…, Serialize contexts into JSON., Format contexts as plain text., Format contexts as Markdown., make_result() (+3 more)

### Community 63 - "CLAUDE.md Project Overview"
Cohesion: 0.13
Nodes (16): alembic/ (DB migrations), app/ (FastAPI backend), Astra Study, evaluation/ (LangSmith + chunking report), frontend/ (Streamlit UI), LangSmith tracing, PostgreSQL (SQLAlchemy 2.0 + Alembic), scripts/ (operational one-offs) (+8 more)

### Community 64 - "Frontend Sidebar & State"
Cohesion: 0.23
Nodes (14): _client(), _create_chat(), _load_chat(), Refresh chats and documents., Load a chat and its messages., Upload selected documents., Left navigation panel., _refresh_workspace() (+6 more)

### Community 65 - "Semantic Merge Stage Tests"
Cohesion: 0.29
Nodes (11): Narrow post-split cleanup. Responsibilities ---------------- - concatenate a…, SemanticStage, BlockProvenance, A compact, parser-neutral reference to the source of one block., _sem_chunk(), test_semantic_caption_owns_following_text_still_works(), test_semantic_merge_deduplicates_shared_provenance(), test_semantic_merge_unions_provenance_and_recomputes_ranges() (+3 more)

### Community 66 - "Document Validation Models"
Cohesion: 0.20
Nodes (9): DocumentValidator, Validates document-level metadata., Any, One metric produced by a validator., Output returned by every validator. Every validator returns exactly one…, Represents a non-fatal validation issue., ValidationMetric, ValidationResult (+1 more)

### Community 67 - "Query Rewrite & Summary Generators"
Cohesion: 0.24
Nodes (9): QueryRewriter, Build the prompt used to rewrite the latest user message into a standalone…, Convert structured conversation messages into a readable prompt format., Responsible for rewriting conversational user queries into standalone search…, Build the prompt used to generate or update the rolling conversation summary., Responsible for building prompts used to generate and maintain a rolling…, SummaryGenerator, ConversationMessage (+1 more)

### Community 68 - "Generation Exceptions"
Cohesion: 0.21
Nodes (12): EmptyPromptError, GenerationError, GenerationTimeoutError, InvalidGenerationResponseError, Exception, Exceptions raised by the Generation module., Raised when prompt generation results in no messages., Raised when the configured LLM times out. (+4 more)

### Community 69 - "Docling Ingestion Processor"
Cohesion: 0.22
Nodes (8): BaseProcessor, ABC, Path, Extract structured information from a document., Base class for every document processor., calculate_sha256(), Path, Calculate the SHA-256 checksum of a file.

### Community 70 - "Frontend App Entry & Styles"
Cohesion: 0.22
Nodes (11): main(), login_screen(), Render the login / registration page., Display uploaded documents., Render the right-side panel., _render_uploaded_documents(), sources_panel(), initialize_session_state() (+3 more)

### Community 71 - "Frontend Chat Service & Workspace"
Cohesion: 0.26
Nodes (11): Citation, _active_chat(), _client(), Refresh the sidebar chat list., Return the selected chat., Render workspace heading., Render conversation history., _refresh_chat_list() (+3 more)

### Community 72 - "BaseRetrievalService & Retrieval Tests"
Cohesion: 0.31
Nodes (12): RerankingResult, make_hybrid_result(), make_reranking_result(), make_service(), HybridSearchResult, Graceful empty retrieval (commit b5d8d4b): when every candidate is filtered out…, The other half of graceful empty retrieval: no hybrid candidates at all short-…, test_callable_wrapper() (+4 more)

### Community 73 - "PromptBuilder"
Cohesion: 0.21
Nodes (7): PromptBuilder, traceable, Convert retrieved contexts into a formatted block., Build the optional long-term conversation summary., Convert conversation history into LLM messages. The latest user message is…, Builds provider-agnostic prompts for the Generation layer. Responsibilities…, Build the complete prompt sent to the LLM.

### Community 74 - "Auth Dependency & Base Repository"
Cohesion: 0.23
Nodes (7): BaseRepository, Session, Base repository providing common CRUD operations., Persist a new entity., Retrieve an entity by its primary key., Persist changes made to an existing entity., ModelType

### Community 75 - "Sparse Search Exceptions"
Cohesion: 0.23
Nodes (11): Exception, Raised when the sparse encoder configuration is invalid., Base exception for all sparse search errors., Raised when a sparse vector collection operation fails., Raised when sparse retrieval fails., Raised when sparse embeddings cannot be generated., SparseCollectionError, SparseConfigurationError (+3 more)

### Community 76 - "CLAUDE.md Chunking Contract Notes"
Cohesion: 0.29
Nodes (12): evaluation/chunking_report.py (offline structural evaluator), ChunkingConfig (app/chunking/config.py), ChunkPipeline (app/chunking/pipeline.py), FilterStage, FinalizeStage, MergeStage, MetadataStage, ParagraphStage (+4 more)

### Community 77 - "Frontend Auth & User Models"
Cohesion: 0.29
Nodes (4): TokenResponse, ApiResponse, Standard API response returned by Astra Study., User

### Community 78 - "Frontend Message Service & Models"
Cohesion: 0.35
Nodes (4): MessageService, Yield assistant text chunks from the message SSE endpoint., Conversation, Message

### Community 79 - "Exception Hierarchy & App Entrypoint"
Cohesion: 0.25
Nodes (9): get_reranking_resource(), Return the shared reranking service. The underlying CrossEncoder model is…, FastAPI, Register all application exception handlers., register_exception_handlers(), lifespan(), FastAPI, get (+1 more)

### Community 80 - "Document API & Ingestion Service"
Cohesion: 0.27
Nodes (9): DocumentAccessScope, DocumentStatus, Enum, str, Who can retrieve/query a document. Separate from ``OrgRole`` / ``TeamRole`` --…, Processing state of a document., DocumentResponse, BaseModel (+1 more)

### Community 81 - "Document Repository Visibility Queries"
Cohesion: 0.24
Nodes (7): AccessContext, Document, Update the processing status of a document., The SQL-level mirror of ``DenseRepository._authorization_filter``'s branch…, Return every document ``access`` is authorized to see: owned INDIVIDUAL…, Return one document only if ``access`` is authorized to see it -- same…, DocumentStatus

### Community 82 - "Retrieval Formatter & Exceptions"
Cohesion: 0.27
Nodes (9): EmptyQueryError, NoRetrievalResultsError, Exception, Raised when no relevant contexts could be retrieved., Base exception for retrieval failures., Raised when the retrieval pipeline is improperly configured., Raised when the supplied query is empty., RetrievalConfigurationError (+1 more)

### Community 83 - "Search Import Isolation Tests"
Cohesion: 0.24
Nodes (9): CompletedProcess, parametrize, Regression test for a circular import discovered during the RBAC-5B independent…, Reproduces the exact import order used by ``scripts/reingest_document.py``…, Run ``code`` in a brand-new Python process with no inherited ``sys.modules``…, Each of these must be importable as the very first thing a fresh process does…, _run_in_fresh_process(), test_reingest_document_script_import_sequence_succeeds_in_fresh_process() (+1 more)

### Community 84 - "Frontend Chat Service & Workspace"
Cohesion: 0.38
Nodes (4): ChatService, Chat, _load_workspace(), Load chats and documents immediately after login.

### Community 85 - "Citation & Provenance Tests"
Cohesion: 0.22
Nodes (7): _conversation(), _FakeGeneration, _FakeStreamGen, _pipeline(), test_normal_pipeline_returns_citations(), test_streaming_citations_reflect_the_streamed_answer(), test_streaming_pipeline_emits_citations_after_text()

### Community 86 - "Docling Ingestion Processor"
Cohesion: 0.33
Nodes (7): ProcessorFactory, Path, Returns the correct processor for a document., main(), Re-run one document through the production ingestion path. document path ->…, _summarise(), test_unsupported_extension_is_rejected_by_factory()

### Community 87 - "Auth API & User Service"
Cohesion: 0.25
Nodes (6): Service responsible for user-related business logic., Register a new user. Every new user is attached to the seeded default…, Resolve the seeded default organisation by its stable slug. Looked up by slug…, UserService, UserCreate, UserRepository

### Community 88 - "CLAUDE.md Retrieval Components Notes"
Cohesion: 0.25
Nodes (9): DenseRepository (COLLECTION_NAME), get_current_user (app/dependencies/auth.py), HybridPipeline (app/search/hybrid/pipeline.py), LLMService (OpenAI-backed), Qdrant (vector store), Qdrant integration-test production-collection hazard, RerankingService (CrossEncoder), RetrievalService (+1 more)

### Community 89 - "API Response Schemas"
Cohesion: 0.36
Nodes (6): success_response(), ApiResponse, ErrorResponse, BaseModel, Standard error API response., Standard success API response.

### Community 90 - "RetrievalService & Integration Tests"
Cohesion: 0.32
Nodes (5): RetrievalResult, traceable, Execute the complete retrieval pipeline. Steps ----- 1. Validate query 2.…, Callable wrapper. Allows RetrievalService to be invoked like a function while…, Convert reranked search results into RetrievedContext objects consumed by…

### Community 91 - "ConversationSummaryService"
Cohesion: 0.29
Nodes (5): ConversationSummaryService, traceable, Maintains a rolling AI-generated summary for long conversations. Lifecycle…, How many conversational messages the stored summary already reflects., Generate or refresh the conversation summary if it is due. Safe to call after…

### Community 92 - "Health Check Endpoint"
Cohesion: 0.38
Nodes (5): health_check(), get, HealthResponse, BaseModel, Response model for the health check endpoint.

### Community 93 - "Document Parser"
Cohesion: 0.29
Nodes (4): DocumentParser, Token, Parse Markdown into tokens., Parses Markdown into Markdown-It tokens. This class is intentionally…

### Community 94 - "CrossEncoder Reranker Implementation"
Cohesion: 0.29
Nodes (4): Automatically determine the best available inference device. Priority --------…, Returns the loaded CrossEncoder instance. This property is primarily useful for…, Initialize the reranker. Parameters ---------- model_name: HuggingFace model…, CrossEncoder

### Community 95 - "Dense Search Response Model"
Cohesion: 0.33
Nodes (4): DenseSearchResponse, Represents the complete response returned from the dense search pipeline., Number of retrieved results., Highest similarity score.

### Community 96 - "Legacy Document Validator"
Cohesion: 0.33
Nodes (4): DocumentValidator, UploadFile, Validates uploaded documents before they are stored on disk., Validate an uploaded document. Raises ------ HTTPException If validation fails.

### Community 97 - "Alembic Env Migration Runner"
Cohesion: 0.40
Nodes (4): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online()

### Community 98 - "OpenAI Model Enum"
Cohesion: 0.50
Nodes (4): OpenAIModel, Enum, str, Supported OpenAI chat models.

### Community 99 - "Citation & Provenance Tests"
Cohesion: 0.50
Nodes (5): ChunkMetadata, EmbeddedChunk, _embedded(), parametrize, test_vector_payload_preserves_provenance()

### Community 106 - "Dependency Injection Wiring"
Cohesion: 0.67
Nodes (3): get_db(), Session, Creates a new database session for each request and ensures it is closed after…

### Community 108 - "APJ Speech Fixture Upload"
Cohesion: 1.00
Nodes (3): A P J Abdul Kalam Departing Speech (upload 510fce33), A P J Abdul Kalam Departing Speech, Developed India 2020

## Knowledge Gaps
- **47 isolated node(s):** `astra-study`, `Multi-head attention`, `Scaled dot-product attention`, `docker-compose.yml (empty placeholder)`, `Full-list-fallback Suspected Chunks Metric` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 933 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DocumentChunk` connect `Merge/Quality Stage Tests` to `Semantic Merge Stage Tests`, `Document Validation Models`, `Chunk Pipeline Contract Tests`, `Offline Chunking Evaluator`, `Recursive Split & Tokenizer Utils`, `Chunk Pipeline & Stages`, `Embedding Batcher & OpenAI Embedder`, `Merge/Quality Stage Tests`, `Sparse Encoder & Hybrid Pipeline`, `AccessContext & Hybrid Search Tests`, `Hybrid Search Mapper`, `Metadata & Merge Stage Tests`, `Filter Stage & Noise Filters`, `OpenAI Embedder Exceptions`, `Embedding Batcher & Dense Pipeline`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `DenseRepository` connect `Dense Qdrant Repository` to `Service Dependency Wiring & AI Pipeline Init`, `Dense Repository Authorization & Delete`, `Sparse Encoder & Hybrid Pipeline`, `AccessContext & Hybrid Search Tests`, `Hybrid Search Mapper`, `Dense Search Mapper & Pipeline`, `Document Repository & Access Dependency`, `Grant Admin Script & RBAC-5D Tests`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `BlockType` connect `Chunk Pipeline Contract Tests` to `Docling Block Handlers`, `Semantic Merge Stage Tests`, `Offline Chunking Evaluator`, `Recursive Split & Tokenizer Utils`, `Docling Ingestion Processor`, `Chunk Pipeline & Stages`, `Merge/Quality Stage Tests`, `Embedding Batcher & OpenAI Embedder`, `Merge/Quality Stage Tests`, `Docling Ingestion Processor`, `Metadata & Merge Stage Tests`, `Filter Stage & Noise Filters`, `Docling Ingestion Processor`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `DocumentChunk` (e.g. with `ChunkPipeline` and `BaseChunkStage`) actually correct?**
  _`DocumentChunk` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 88 inferred relationships involving `BlockType` (e.g. with `FilterStage` and `MergeStage`) actually correct?**
  _`BlockType` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `DocumentBlock` (e.g. with `DocumentConverter` and `HandlerResult`) actually correct?**
  _`DocumentBlock` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `AccessContext` (e.g. with `AIPipeline` and `create_message()`) actually correct?**
  _`AccessContext` has 9 INFERRED edges - model-reasoned connections that need verification._