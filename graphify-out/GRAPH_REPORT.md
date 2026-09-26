# Graph Report - Astra-Study  (2026-09-27)

## Corpus Check
- 16 files · ~250,207 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2959 nodes · 7470 edges · 196 communities (102 shown, 59 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 646 edges (avg confidence: 0.93)
- Token cost: 0 input · 85,702 output

## Community Hubs (Navigation)
- Document Access Scope Enum
- Document Not Found & Delete Auth
- Markdown Token Converter
- Chat Message & Generation Models
- Chunk Metadata & Content Segments
- Chunking Report Analyzer
- Evaluation Metric Evaluators
- Team Listing API
- Recursive Stage Heading Logic
- Chunking Config & Section Matching
- Document Repository Visibility
- Team Membership Forbidden & Tests
- Team Creation Schema & Trim
- Retrieval Exceptions
- Base Ingestion Processor
- Reingest Document Script
- AI Pipeline & DI Wiring
- Chunking Evaluation Baselines
- Chat Not Found & Message API
- Qdrant Authorization Filter Tests
- Base LLM Provider
- Query Rewriter
- Base Generation Service
- Embedded Chunk Model
- Sparse Embedding Encoder
- Merge Stage Section Chunks
- Block Type & Token Counting
- Embedding Batcher
- OpenAI Embedder
- Chat API Routes
- Document API Routes
- Document Service Delete/Download
- Conversation Service Propagation Tests
- Chunking Pipeline Tests
- User Profile Endpoint
- Base Reranker
- Settings & Access Enums
- Citation Provenance Tests
- Cross-Encoder Reranker
- Dense Repository Collection Ops
- RBAC Foundation Tests
- Document Model
- User Exceptions
- Auth Login Endpoints
- Embedding Pipeline & Batching
- Frontend API Client
- AI Pipeline Response Building
- Access Context & Team Role
- Reranking Candidate Validation
- Streamlit App & Sidebar
- Reranking Pipeline Tests
- Filter Stage
- Base Repository CRUD
- Dense Search Exceptions
- Base Storage Service
- User Registration & Profile Schemas
- SQLAlchemy Base & Chat Models
- Reranker Callable Interface
- Conversation Service Message Flow
- Chat Service CRUD
- Message API & Schemas
- RBAC Retrieval Authorization Concepts
- Semantic Stage Merge
- OrgRole Enum & AccessContext
- Frontend Services & Auth
- Fake Docling Test Doubles
- RBAC Authorization Core Concepts
- Qdrant Test Isolation Conftest
- Password Hashing & JWT Security
- Auth Exceptions
- Retrieval Service Orchestrator
- Citation Ranking Rationale
- Reranking Service Tests
- Database Session Dependency
- Document Validator
- Chunking Evaluator Concepts
- Frontend Auth Profile Fetch
- Generation Exceptions
- Prompt Builder
- Hybrid Pipeline Ops
- Sparse Search Exceptions
- RBAC Access Dependency Concepts
- Message Service Streaming
- Base Retrieval Service
- Exception Handlers & Reranker Resource
- Reranking Service Public API
- Dense Repository Auth & Search
- Import Isolation Regression Test
- Fake Generation Test Double
- Health Check & User Router
- API Response Schemas
- Conversation Summary Service
- Markdown Parser
- Chunk UUID Helpers
- Fake Storage Service
- Dense Search Response
- Repo Top-Level Areas
- Alembic Migration Env
- OpenAI Model Enum
- Vector Payload Provenance Test
- Application Settings
- Chunking Stage Comparison Reports
- Kalam Speech Fixture Doc
- AI Package Init
- AI Response Model
- Document Constants
- App Constants Init
- Hybrid Package Init
- Attention Mechanism Concepts
- DB Fixture
- RBAC-5I Scope Assertion Test
- Background Tasks Import
- Delete Route Import
- Get Route Import
- Post Route Import
- Response Import
- User Model Import
- Get Route Import
- Post Route Import
- AI Pipeline Reference
- Auth Service Reference
- Chat Service Reference
- Document Service Reference
- Ingestion Service Reference
- Message Service Reference
- TeamMembership Model Node
- ABC Reference
- BaseModel Reference
- Traceable Decorator Reference
- ScoredPoint Reference
- User Model Reference
- User Model Reference
- Validators Package Init
- Evaluation Runner Reference
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
- Evaluation Package Init
- Frontend Package Init
- UI Package Init
- Generation Request Reference
- Astra Study Project Name
- Scripts Package Init
- Integration Tests Init
- Storage Service Reference
- Document Model Reference
- Path Reference
- UploadFile Reference
- User Model Reference
- User Create Schema Reference

## God Nodes (most connected - your core abstractions)
1. `DocumentChunk` - 140 edges
2. `BlockType` - 113 edges
3. `DocumentBlock` - 51 edges
4. `AccessContext` - 45 edges
5. `count_tokens()` - 43 edges
6. `TeamMembershipRepository` - 43 edges
7. `build_access()` - 41 edges
8. `User` - 40 edges
9. `make_user()` - 40 edges
10. `make_document_service()` - 39 edges

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
- **RBAC authorization flow (AccessContext threading + retrieval + document authz)** — claude_accesscontext, claude_get_access_context, claude_denserepository, claude_documentservice, claude_documentrepository [EXTRACTED 1.00]
- **8-stage chunking pipeline contract** — claude_chunkpipeline, claude_paragraphstage, claude_metadatastage, claude_mergestage, claude_recursivestage, claude_semanticstage, claude_filterstage, claude_qualitystage, claude_finalizestage [EXTRACTED 1.00]
- **Rolling summary + recent-window conversation memory flow** — claude_aipipeline, claude_conversationsummaryservice, claude_summarygenerator, claude_messagerepository, claude_run_summary_refresh [EXTRACTED 1.00]

## Communities (196 total, 59 thin omitted)

### Community 0 - "Document Access Scope Enum"
Cohesion: 0.06
Nodes (99): DocumentAccessScope, DocumentStatus, Enum, str, Who can retrieve/query a document. Separate from ``OrgRole`` / ``TeamRole`` --…, Processing state of a document., DocumentTooLargeError, EmptyDocumentError (+91 more)

### Community 1 - "Document Not Found & Delete Auth"
Cohesion: 0.06
Nodes (90): DocumentNotFoundError, Raised when a requested document does not exist or does not belong to the…, DocumentService, AccessContext, BaseStorageService, DenseRepository, Document, DocumentResponse (+82 more)

### Community 2 - "Markdown Token Converter"
Cohesion: 0.07
Nodes (48): DocumentConverter, Token, Converts Markdown-It tokens into semantic DocumentBlocks. The converter itself…, Convert Markdown tokens into semantic DocumentBlocks., BaseHandler, HandlerResult, ABC, Token (+40 more)

### Community 3 - "Chat Message & Generation Models"
Cohesion: 0.07
Nodes (55): MessageService, ChatRepository, GenerationResponse, MessageRepository, RetrievedContext, add_messages(), db(), _FakeLLM (+47 more)

### Community 4 - "Chunk Metadata & Content Segments"
Cohesion: 0.05
Nodes (53): ChunkMetadata, ContentSegment, DocumentChunk, One source ``DocumentBlock`` that ``MergeStage`` folded into a chunk. Internal…, Represents one chunk that will eventually be embedded and stored in the vector…, Metadata associated with a document chunk. This metadata flows through the…, FinalizeStage, UUID (+45 more)

### Community 5 - "Chunking Report Analyzer"
Cohesion: 0.07
Nodes (68): analyze(), _block_from_dict(), _block_range_valid(), _block_to_dict(), _chunk_body(), compare(), _dig(), _expected_prefix() (+60 more)

### Community 6 - "Evaluation Metric Evaluators"
Cohesion: 0.05
Nodes (51): answer_length(), citation_count(), exact_match(), Any, Exact answer match. Useful as a fast deterministic baseline., Records answer length. Helpful for spotting prompt regressions., Counts returned citations., FixtureManager (+43 more)

### Community 7 - "Team Listing API"
Cohesion: 0.06
Nodes (41): list_teams(), get, Return every team in the requester's own organisation. Membership is never…, InvalidTeamNameError, LastTeamManagerError, AppException, Raised when a team name is already taken within the requester's organisation.…, Raised when a team name is blank/whitespace-only after trimming, or exceeds 255… (+33 more)

### Community 8 - "Recursive Stage Heading Logic"
Cohesion: 0.06
Nodes (40): _is_markdown_separator(), _norm(), Compact heading context: the deepest heading normally, or the deepest two…, Recover the source segments (one per contributing block) from the merged chunk…, The text a pass-through chunk would carry with ``prefix`` present exactly once.…, A markdown table separator row, e.g. ``| --- | :--: |``., Text of each child (before the heading prefix), plus -- for the structural…, Pack whole list items into child bodies, never dividing one. A single item… (+32 more)

### Community 9 - "Chunking Config & Section Matching"
Cohesion: 0.08
Nodes (32): ChunkingConfig, Single source of truth for the chunking pipeline's size limits. Every value is…, True when ``inner`` names the same section as ``outer`` or a subsection nested…, section_contains(), ChunkPipeline, Executes the configured chunking stages., BaseChunkStage, ABC (+24 more)

### Community 10 - "Document Repository Visibility"
Cohesion: 0.06
Nodes (42): DocumentRepository, AccessContext, Document, Session, Repository for Document database operations., Update the processing status of a document., The SQL-level mirror of ``DenseRepository._authorization_filter``'s branch…, Return every document ``access`` is authorized to see: owned INDIVIDUAL… (+34 more)

### Community 11 - "Team Membership Forbidden & Tests"
Cohesion: 0.19
Nodes (53): Raised when the acting user is not the target team's own ``TeamRole.MANAGER``.…, TeamMembershipOperationForbiddenError, all_memberships(), build_access(), get_membership(), _make_file_backed_session_factory(), make_membership(), make_organisation() (+45 more)

### Community 12 - "Team Creation Schema & Trim"
Cohesion: 0.12
Nodes (52): Trim before length constraints are applied (mode="before" runs ahead of Field's…, Schema used when creating a team. Deliberately has no ``organisation_id`` field…, TeamCreate, field_validator, all_memberships(), all_teams(), build_access(), db() (+44 more)

### Community 13 - "Retrieval Exceptions"
Cohesion: 0.07
Nodes (38): ContextFormattingError, EmptyQueryError, NoRetrievalResultsError, Exception, Raised when no relevant contexts could be retrieved., Base exception for retrieval failures., Raised when the retrieval pipeline is improperly configured., Raised when retrieved contexts cannot be formatted for downstream generation. (+30 more)

### Community 14 - "Base Ingestion Processor"
Cohesion: 0.08
Nodes (30): BaseProcessor, ABC, Path, Extract structured information from a document., Base class for every document processor., ProcessorFactory, Path, Returns the correct processor for a document. (+22 more)

### Community 15 - "Reingest Document Script"
Cohesion: 0.09
Nodes (41): DocumentChunk, main(), Document, Re-run one document through the production ingestion path. Document.id (SQLite)…, Stamp every chunk's metadata from the one authoritative Document row.…, _stamp_rbac_fields(), _summarise(), SimpleNamespace (+33 more)

### Community 16 - "AI Pipeline & DI Wiring"
Cohesion: 0.11
Nodes (40): AIPipeline, build_conversation_summary_service(), get_ai_pipeline(), get_auth_service(), get_chat_service(), get_conversation_service(), get_conversation_summary_service(), get_document_service() (+32 more)

### Community 17 - "Chunking Evaluation Baselines"
Cohesion: 0.05
Nodes (44): baseline_apjspeech.txt (commit 888fc8c report), baseline_Attention.txt (commit 888fc8c report), baseline_LLM.txt (commit 888fc8c report), comparison.txt (baseline vs stage14 deltas), comparison_stage5_to_stage6.txt (Stage 6 primary comparison), apjspeech.pdf (eval corpus doc), Attention.pdf (eval corpus doc), LLM.pdf (eval corpus doc) (+36 more)

### Community 18 - "Chat Not Found & Message API"
Cohesion: 0.09
Nodes (25): ChatNotFoundError, Raised when the requested chat session does not exist or is inaccessible., ChatRepository, datetime, Session, Repository for ChatSession database operations., Update the title of a chat session., Update the rolling summary of a chat session. ``summarized_through`` is the… (+17 more)

### Community 19 - "Qdrant Authorization Filter Tests"
Cohesion: 0.17
Nodes (40): MatchAny, _branch_count(), branch_filter(), call_hybrid_search(), find_matchany(), make_access(), make_dense_repository_with_fake_client(), _organisation_branches() (+32 more)

### Community 20 - "Base LLM Provider"
Cohesion: 0.07
Nodes (23): BaseLLMProvider, ABC, Generate a complete response from the language model., Stream a response from the language model., Base interface for all LLM providers., get_openai_client(), Create and return an OpenAI client. The client is configured using application…, OpenAIProvider (+15 more)

### Community 21 - "Query Rewriter"
Cohesion: 0.11
Nodes (23): QueryRewriter, Build the prompt used to rewrite the latest user message into a standalone…, Convert structured conversation messages into a readable prompt format., Responsible for rewriting conversational user queries into standalone search…, Build the prompt used to generate or update the rolling conversation summary., Responsible for building prompts used to generate and maintain a rolling…, SummaryGenerator, Build the prompt used to generate a chat title. (+15 more)

### Community 22 - "Base Generation Service"
Cohesion: 0.10
Nodes (30): BaseGenerationService, ABC, Abstract interface for the Generation layer. Implementations are responsible…, Generate a complete response., Stream the generated response. Each yielded string represents the next chunk of…, EmptyResponseError, Raised when the LLM returns an empty response., Citation (+22 more)

### Community 23 - "Embedded Chunk Model"
Cohesion: 0.09
Nodes (18): EmbeddedChunk, Returns the chunk text., Returns the embedding dimensions., Represents a chunk together with its embedding. This object is produced by the…, DenseMapper, PointStruct, ScoredPoint, Convert multiple EmbeddedChunks into PointStructs. (+10 more)

### Community 24 - "Sparse Embedding Encoder"
Cohesion: 0.09
Nodes (17): traceable, Generate sparse embedding for a user query., Generates sparse embeddings for document chunks using FastEmbed.…, Generate sparse embeddings for document chunks., SparseEncoder, Represents a sparse vector generated by the sparse encoder. Unlike dense…, Number of non-zero dimensions., Represents a document chunk together with its sparse vector. (+9 more)

### Community 25 - "Merge Stage Section Chunks"
Cohesion: 0.13
Nodes (34): _distinct(), _list_blocks(), _long(), _merged_section(), A MergeStage-style section chunk: ``blocks`` joined with blank lines…, Q2/Q3: 1 heading + 4 distinct body blocks, 2 pages, forced into several…, A single body block longer than several windows: a middle child holds only its…, Two adjacent blocks that share a verbatim 6-word run at their start. The… (+26 more)

### Community 26 - "Block Type & Token Counting"
Cohesion: 0.15
Nodes (31): count_tokens(), Count the number of tokens in text., BlockType, Represents the semantic type of a document block. This enum is parser-…, StrEnum, _md_table(), _pipeline_from_blocks(), _row_lines() (+23 more)

### Community 27 - "Embedding Batcher"
Cohesion: 0.11
Nodes (23): Split chunks into embedding batches., Convenience wrapper allowing the batcher to be called directly., EmbeddingBatchError, EmbeddingValidationError, Custom exceptions for the embeddings module., Raised when an embedding fails validation. Examples: - Empty embedding -…, Raised when an embedding batch is invalid. Examples: - Empty batch - Batch…, EmbeddingBatch (+15 more)

### Community 28 - "OpenAI Embedder"
Cohesion: 0.09
Nodes (24): OpenAIEmbedder, traceable, Execute one embedding request. Retries automatically for transient OpenAI…, Convert raw vectors returned by OpenAI into EmbeddedChunk objects., Embed a single batch of document chunks. Parameters ---------- chunks A batch…, Embed multiple batches. Parameters ---------- batches List of EmbeddingBatch…, Convenience wrapper. Allows embedder(batches) instead of embedder.embed(batches), Generate an embedding for a user query. (+16 more)

### Community 29 - "Chat API Routes"
Cohesion: 0.11
Nodes (25): create_chat(), delete_chat(), get_chat(), list_chats(), delete, get, post, Response (+17 more)

### Community 30 - "Document API Routes"
Cohesion: 0.08
Nodes (31): delete_document(), download_document(), get_document(), get_documents(), AccessContext, DocumentResponse, IngestionService, UploadFile (+23 more)

### Community 31 - "Document Service Delete/Download"
Cohesion: 0.10
Nodes (22): BinaryIO, DocumentService, Service responsible for all document-related operations., Download the original uploaded document., Retrieve metadata for a single document., Upload one or more documents., Document, Create an authenticated API client. (+14 more)

### Community 32 - "Conversation Service Propagation Tests"
Cohesion: 0.09
Nodes (27): ConversationService, _individual_branch_user_id(), make_conversation_service(), make_dense_repository_with_fake_client(), _persisted(), Filter, parametrize, Executable specification for RBAC-5B: threading the trusted AccessContext… (+19 more)

### Community 33 - "Chunking Pipeline Tests"
Cohesion: 0.20
Nodes (29): _body(), _chunk(), _heading(), _merge(), _mk(), _prov(), Chunk-quality contract tests (Phase 2). Built incrementally alongside the…, Run the first real stages that shape section chunks: Metadata -> Merge. Input… (+21 more)

### Community 34 - "User Profile Endpoint"
Cohesion: 0.15
Nodes (29): get_current_user_profile(), get, UserService, Return the currently authenticated user's profile, including their organisation…, db(), make_membership(), make_organisation(), make_team() (+21 more)

### Community 35 - "Base Reranker"
Cohesion: 0.12
Nodes (18): BaseReranker, ABC, Abstract interface for all rerankers. Every reranker implementation…, Abstract base class for reranking implementations., Returns the underlying reranker model name., Returns the execution device. Example ------- cpu cuda cuda:0 mps, Batch size used for inference., Maximum sequence length accepted by the reranker. (+10 more)

### Community 36 - "Settings & Access Enums"
Cohesion: 0.19
Nodes (11): HybridService, Production Hybrid Retriever. Responsibilities ---------------- • Generate dense…, OpenAIEmbedder, SparseEncoder, End-to-end integration test for the complete Hybrid Retrieval pipeline.…, test_hybrid_pipeline(), Compare Dense Retrieval vs Hybrid Retrieval using the same indexed document., test_retrieval_comparison() (+3 more)

### Community 37 - "Citation Provenance Tests"
Cohesion: 0.12
Nodes (27): _context(), Provenance propagation: Docling → block → chunk → vector payload → retrieval…, Analogous case with different headings, proving the mechanism is not hardcoded…, Without any structural overlap with the query, citation order must fall back to…, A bare heading chunk is too short to score -- it must come back `None`…, Proves the heading signal is discounted, not disabled: a title that carries a…, _reranked(), test_answer_grounding_keeps_chunks_distinct_and_provenance_intact() (+19 more)

### Community 38 - "Cross-Encoder Reranker"
Cohesion: 0.09
Nodes (15): CrossEncoderReranker, Automatically determine the best available inference device. Priority --------…, Name of the underlying HuggingFace model., Device used for inference., Batch size used during inference., Maximum sequence length accepted by the model., Returns the loaded CrossEncoder instance. This property is primarily useful for…, Validate the user query before inference. (+7 more)

### Community 39 - "Dense Repository Collection Ops"
Cohesion: 0.09
Nodes (14): DenseRepository, PointStruct, Create the Astra Study collection., Delete the Astra Study collection., Drop and recreate the collection. Useful during development., Insert or update points in the collection., Return the number of vectors stored in the collection., Scroll through stored points. Useful for debugging. (+6 more)

### Community 40 - "RBAC Foundation Tests"
Cohesion: 0.16
Nodes (23): Document, db(), make_document(), make_organisation(), make_team(), make_upload_file(), make_user(), fixture (+15 more)

### Community 41 - "Document Model"
Cohesion: 0.18
Nodes (17): Document, Base, TimestampMixin, Represents an uploaded document., SQLAlchemy ORM Models, Organisation, Base, TimestampMixin (+9 more)

### Community 42 - "User Exceptions"
Cohesion: 0.14
Nodes (18): EmailAlreadyExistsError, AppException, Raised when a username is already taken., Raised when a target user id does not exist, or belongs to a different…, Raised when an email is already registered., UsernameAlreadyExistsError, UserNotFoundError, Schema returned for one team membership after a direct membership-management… (+10 more)

### Community 43 - "Auth Login Endpoints"
Cohesion: 0.17
Nodes (19): login(), oauth2_login(), post, Authenticate a user using JSON. Used by the frontend., OAuth2-compatible login endpoint. Swagger sends: username password We interpret…, LoginRequest, BaseModel, Response returned after successful authentication. (+11 more)

### Community 44 - "Embedding Pipeline & Batching"
Cohesion: 0.14
Nodes (13): EmbeddingBatcher, Splits document chunks into batches suitable for the embedding provider. The…, EmbeddingPipeline, Production embedding pipeline. Pipeline DocumentChunks │ ▼ EmbeddingBatcher │ ▼…, Execute the complete embedding pipeline., Convenience wrapper. Allows pipeline(chunks) instead of pipeline.run(chunks), PDFProcessor, Backward-compatible PDF processor. PDF ingestion is now handled by… (+5 more)

### Community 45 - "Frontend API Client"
Cohesion: 0.15
Nodes (10): ApiClient, ApiException, Any, Exception, Response, Download binary data., Open a Server-Sent Events POST request., Base HTTP client used by all frontend services. (+2 more)

### Community 46 - "AI Pipeline Response Building"
Cohesion: 0.17
Nodes (15): AIResponse, AIPipeline, ChatMessage, StreamEvent, traceable, Stream an assistant response using Retrieval-Augmented Generation., Generate a short AI title for a new conversation., Generate or update the conversation summary. (+7 more)

### Community 47 - "Access Context & Team Role"
Cohesion: 0.19
Nodes (22): get_access_context(), Session, Build the request-scoped authorization identity. Every field is derived…, Enum, str, A user's role within a single team membership. Independent of ``OrgRole``: a…, TeamRole, db() (+14 more)

### Community 48 - "Reranking Candidate Validation"
Cohesion: 0.13
Nodes (15): Validate retrieval candidates before reranking., CandidateFormatError, EmptyCandidateError, InvalidQueryError, InvalidTopKError, ModelLoadError, PredictionError, Exception (+7 more)

### Community 49 - "Streamlit App & Sidebar"
Cohesion: 0.16
Nodes (19): main(), _client(), _create_chat(), _load_chat(), Refresh chats and documents., Load a chat and its messages., Upload selected documents., Left navigation panel. (+11 more)

### Community 50 - "Reranking Pipeline Tests"
Cohesion: 0.16
Nodes (22): preview_text(), print_header(), print_hybrid_results(), print_performance(), print_quality_benchmark(), print_rank_movements(), print_reranked_results(), print_reranking_statistics() (+14 more)

### Community 51 - "Filter Stage"
Cohesion: 0.17
Nodes (19): FilterStage, Removes only truly useless chunks. Philosophy ---------- Never remove…, is_copyright(), is_doi(), is_empty(), is_isbn(), is_numeric_only(), is_page_number() (+11 more)

### Community 52 - "Base Repository CRUD"
Cohesion: 0.12
Nodes (12): BaseRepository, Session, Base repository providing common CRUD operations., Persist a new entity., Retrieve an entity by its primary key., Persist changes made to an existing entity., datetime, Count the user + assistant messages created at or before ``timestamp``.… (+4 more)

### Community 53 - "Dense Search Exceptions"
Cohesion: 0.13
Nodes (21): CollectionAlreadyExistsError, CollectionCreationError, CollectionDeletionError, CollectionNotFoundError, DenseSearchConfigurationError, DenseSearchError, InvalidPayloadError, InvalidSearchQueryError (+13 more)

### Community 54 - "Base Storage Service"
Cohesion: 0.12
Nodes (13): BaseStorageService, ABC, Path, UploadFile, Save a file and return: ( stored_filename, file_size, ), Delete a stored file., Return the absolute path of a stored file., Base interface for all storage providers. (+5 more)

### Community 55 - "User Registration & Profile Schemas"
Cohesion: 0.15
Nodes (16): register(), One of the requester's team memberships, as returned by ``GET /users/me``., ``GET /users/me`` response only -- extends ``UserResponse`` with RBAC context…, Schema used when a new user registers., TeamMembershipResponse, UserCreate, UserProfileResponse, Organisation (+8 more)

### Community 56 - "SQLAlchemy Base & Chat Models"
Cohesion: 0.13
Nodes (14): Base, Base class for all SQLAlchemy ORM models., ChatSession, Represents a chat session belonging to a user., ChatMessage, Represents a single message within a chat session., Adds automatic timestamp fields to database models., TimestampMixin (+6 more)

### Community 57 - "Reranker Callable Interface"
Cohesion: 0.11
Nodes (12): Allows the reranker instance to be invoked like a function. Example -------…, Rerank retrieved candidates. Parameters ---------- query: User query.…, slice, SupportsIndex, Returns the top-k reranked chunks. Parameters ---------- k: Number of chunks to…, Represents a single reranked retrieval result. Attributes ---------- result:…, Represents the complete output of the reranking stage. Attributes ----------…, Returns the highest ranked chunk. (+4 more)

### Community 58 - "Conversation Service Message Flow"
Cohesion: 0.17
Nodes (15): ConversationService, BackgroundTasks, ChatMessage, ChatSession, ConversationResponse, MessageCreate, StreamEvent, traceable (+7 more)

### Community 59 - "Chat Service CRUD"
Cohesion: 0.19
Nodes (13): ChatService, Chat, Citation, _active_chat(), _client(), Refresh the sidebar chat list., Return the selected chat., Render workspace heading. (+5 more)

### Community 60 - "Message API & Schemas"
Cohesion: 0.11
Nodes (18): create_message(), get_messages(), BackgroundTasks, ConversationResponse, MessageCreate, MessageService, Retrieve all messages for a chat session., Send a message and receive the assistant response. (+10 more)

### Community 61 - "RBAC Retrieval Authorization Concepts"
Cohesion: 0.13
Nodes (20): AccessContext (app/retrieval/access.py), AIPipeline (app/ai/pipeline.py), DenseRepository._authorization_filter, tests/conftest.py (Qdrant isolation guard), Conversation memory (rolling summary + recent window) design, ConversationService (app/services/conversation.py), ConversationSummaryService.update_summary, DenseRepository (+12 more)

### Community 62 - "Semantic Stage Merge"
Cohesion: 0.20
Nodes (16): Narrow post-split cleanup. Responsibilities ---------------- - concatenate a…, SemanticStage, BlockProvenance, A compact, parser-neutral reference to the source of one block., _sc(), _sem_chunk(), test_semantic_caption_owns_following_text_still_works(), test_semantic_merge_deduplicates_shared_provenance() (+8 more)

### Community 63 - "OrgRole Enum & AccessContext"
Cohesion: 0.15
Nodes (16): OrgRole, Enum, str, A user's organisation-scoped role. Distinct from document access scope -- role…, AccessContext, Immutable, request-scoped authorization identity. Built exclusively from…, Fail clearly rather than silently accepting an incomplete identity. Required…, HybridSearchResult (+8 more)

### Community 64 - "Frontend Services & Auth"
Cohesion: 0.17
Nodes (10): ChatService, DocumentService, AuthService, ApiClient, _load_workspace(), login_screen(), ApiClient, Load chats and documents immediately after login. (+2 more)

### Community 65 - "Fake Docling Test Doubles"
Cohesion: 0.15
Nodes (11): _extract(), FakeBBox, FakeConverter, FakeDocument, FakeItem, FakeProv, test_chunking_preserves_provenance(), test_docx_heading_section_without_page() (+3 more)

### Community 66 - "RBAC Authorization Core Concepts"
Cohesion: 0.15
Nodes (17): DocumentService._can_create, DocumentService._can_delete, TeamRepository.create_with_initial_manager, DenseRepository.delete_by_document_id, DocumentAccessScope enum (app/enums/document.py), DocumentService, HybridMapper.build_payload (app/search/hybrid/mapper.py), HybridPipeline.index (app/search/hybrid/pipeline.py) (+9 more)

### Community 67 - "Qdrant Test Isolation Conftest"
Cohesion: 0.16
Nodes (13): _isolate_qdrant_collection(), pytest_collection_modifyitems(), pytest_sessionfinish(), Test-wide Qdrant collection isolation. The integration tests drive…, Record whether this session collected any ``tests/integration`` test., Best-effort drop the dedicated test collection -- and only that collection --…, Pin every test to the dedicated Qdrant collection and return its name. Executed…, Offline safety regression for Qdrant test isolation. Guarantees the test… (+5 more)

### Community 68 - "Password Hashing & JWT Security"
Cohesion: 0.16
Nodes (9): Any, Handles password hashing, password verification, and JWT token generation., Decode and validate a JWT., Hash a plain-text password., Verify a password against its hash., Create an access token., Create a refresh token., SecurityManager (+1 more)

### Community 69 - "Auth Exceptions"
Cohesion: 0.17
Nodes (12): AuthenticationError, InactiveUserError, InvalidCredentialsError, Raised when an inactive user attempts to log in., Raised when authentication fails because the access token is invalid, expired,…, Raised when the provided email or password is incorrect., AppException, Exception (+4 more)

### Community 70 - "Retrieval Service Orchestrator"
Cohesion: 0.18
Nodes (11): RetrievalResult, traceable, Execute the complete retrieval pipeline. Steps ----- 1. Validate query 2.…, Production Retrieval Orchestrator. Pipeline -------- User Query │ ▼ Hybrid…, Callable wrapper. Allows RetrievalService to be invoked like a function while…, Convert reranked search results into RetrievedContext objects consumed by…, RetrievalService, print_results() (+3 more)

### Community 71 - "Citation Ranking Rationale"
Cohesion: 0.13
Nodes (15): answer_support (lexical overlap score), BlockProvenance, Citation model (app/generation/models.py), GenerationService.citations_for, Deterministic citation ranking rationale (no LLM), DoclingProcessor (app/ingestion/processors/docling.py), DocumentBlock (app/document/models.py), POST /api/v1/documents (upload route) (+7 more)

### Community 72 - "Reranking Service Tests"
Cohesion: 0.25
Nodes (14): RerankingResult, make_hybrid_result(), make_reranking_result(), make_service(), HybridSearchResult, Graceful empty retrieval (commit b5d8d4b): when every candidate is filtered out…, The other half of graceful empty retrieval: no hybrid candidates at all short-…, The abstract base's ``__call__`` fallback must forward the keyword-only,… (+6 more)

### Community 73 - "Database Session Dependency"
Cohesion: 0.18
Nodes (10): get_db(), Session, Creates a new database session for each request and ensures it is closed after…, get_current_user(), Session, Return the currently authenticated user., grant_admin(), main() (+2 more)

### Community 74 - "Document Validator"
Cohesion: 0.20
Nodes (9): DocumentValidator, Validates document-level metadata., Any, One metric produced by a validator., Output returned by every validator. Every validator returns exactly one…, Represents a non-fatal validation issue., ValidationMetric, ValidationResult (+1 more)

### Community 75 - "Chunking Evaluator Concepts"
Cohesion: 0.24
Nodes (14): evaluation/chunking_report.py (offline structural evaluator), ChunkingConfig (app/chunking/config.py), ChunkPipeline (app/chunking/pipeline.py), ContentSegment, FilterStage, FinalizeStage, Chunking pipeline contract (frozen), MergeStage (+6 more)

### Community 76 - "Frontend Auth Profile Fetch"
Cohesion: 0.23
Nodes (5): Fetch the richer RBAC profile (organisation_id, role, team memberships) for the…, TokenResponse, ApiResponse, Standard API response returned by Astra Study., User

### Community 77 - "Generation Exceptions"
Cohesion: 0.21
Nodes (12): EmptyPromptError, GenerationError, GenerationTimeoutError, InvalidGenerationResponseError, Exception, Exceptions raised by the Generation module., Raised when prompt generation results in no messages., Raised when the configured LLM times out. (+4 more)

### Community 78 - "Prompt Builder"
Cohesion: 0.21
Nodes (7): PromptBuilder, traceable, Convert retrieved contexts into a formatted block., Build the optional long-term conversation summary., Convert conversation history into LLM messages. The latest user message is…, Builds provider-agnostic prompts for the Generation layer. Responsibilities…, Build the complete prompt sent to the LLM.

### Community 79 - "Hybrid Pipeline Ops"
Cohesion: 0.17
Nodes (3): HybridPipeline, Production Hybrid Indexing Pipeline. Responsibilities ----------------…, Index document chunks using hybrid dense+sparse vectors.

### Community 80 - "Sparse Search Exceptions"
Cohesion: 0.23
Nodes (11): Exception, Raised when the sparse encoder configuration is invalid., Base exception for all sparse search errors., Raised when a sparse vector collection operation fails., Raised when sparse retrieval fails., Raised when sparse embeddings cannot be generated., SparseCollectionError, SparseConfigurationError (+3 more)

### Community 81 - "RBAC Access Dependency Concepts"
Cohesion: 0.17
Nodes (12): AuthService.get_current_user_profile, Document model (app/models/document.py), frontend/models/user.py User dataclass, get_access_context (app/dependencies/access.py), get_current_user (app/dependencies/auth.py), UserService._get_default_organisation, alembic migration 116ced32c143 (RBAC org/team foundation), Organisation model (app/models/organisation.py) (+4 more)

### Community 82 - "Message Service Streaming"
Cohesion: 0.35
Nodes (4): MessageService, Yield assistant text chunks from the message SSE endpoint., Conversation, Message

### Community 83 - "Base Retrieval Service"
Cohesion: 0.27
Nodes (6): ABC, BaseRetrievalService, RetrievalResult, Base contract for all retrieval implementations., Execute the complete retrieval pipeline. Retrieval is keyword-only and always…, Allow the service to be invoked like a function.

### Community 84 - "Exception Handlers & Reranker Resource"
Cohesion: 0.25
Nodes (9): get_reranking_resource(), Return the shared reranking service. The underlying CrossEncoder model is…, FastAPI, Register all application exception handlers., register_exception_handlers(), lifespan(), FastAPI, get (+1 more)

### Community 85 - "Reranking Service Public API"
Cohesion: 0.22
Nodes (6): traceable, Callable wrapper. Example ------- >>> result = service( ... query=query, ...…, Public service for document reranking. The service hides the concrete reranker…, Initialize the reranking service. Parameters ---------- reranker: Optional…, Returns the active reranker. The default CrossEncoderReranker is created only…, RerankingService

### Community 86 - "Dense Repository Auth & Search"
Cohesion: 0.22
Nodes (7): AccessContext, Filter, HybridSearchResult, Delete every point belonging to one schema_version=3 document. Scoped…, Build the document-visibility filter for ``access``. Structural constraints…, Execute native Qdrant Hybrid Search using Reciprocal Rank Fusion (RRF).…, traceable

### Community 87 - "Import Isolation Regression Test"
Cohesion: 0.24
Nodes (9): CompletedProcess, parametrize, Regression test for a circular import discovered during the RBAC-5B independent…, Reproduces the exact import order used by ``scripts/reingest_document.py``…, Run ``code`` in a brand-new Python process with no inherited ``sys.modules``…, Each of these must be importable as the very first thing a fresh process does…, _run_in_fresh_process(), test_reingest_document_script_import_sequence_succeeds_in_fresh_process() (+1 more)

### Community 88 - "Fake Generation Test Double"
Cohesion: 0.22
Nodes (7): _conversation(), _FakeGeneration, _FakeStreamGen, _pipeline(), test_normal_pipeline_returns_citations(), test_streaming_citations_reflect_the_streamed_answer(), test_streaming_pipeline_emits_citations_after_text()

### Community 89 - "Health Check & User Router"
Cohesion: 0.28
Nodes (5): health_check(), get, HealthResponse, BaseModel, Response model for the health check endpoint.

### Community 90 - "API Response Schemas"
Cohesion: 0.36
Nodes (6): success_response(), ApiResponse, ErrorResponse, BaseModel, Standard error API response., Standard success API response.

### Community 91 - "Conversation Summary Service"
Cohesion: 0.29
Nodes (5): ConversationSummaryService, traceable, Maintains a rolling AI-generated summary for long conversations. Lifecycle…, How many conversational messages the stored summary already reflects., Generate or refresh the conversation summary if it is due. Safe to call after…

### Community 92 - "Markdown Parser"
Cohesion: 0.29
Nodes (4): DocumentParser, Token, Parse Markdown into tokens., Parses Markdown into Markdown-It tokens. This class is intentionally…

### Community 93 - "Chunk UUID Helpers"
Cohesion: 0.29
Nodes (4): UUID, Returns the UUIDs of all chunks contained in the batch., Returns the chunk UUID., Returns the document UUID.

### Community 94 - "Fake Storage Service"
Cohesion: 0.29
Nodes (4): BaseStorageService, Path, FakeStorageService, In-memory stand-in for LocalStorageService -- no filesystem access, so this…

### Community 95 - "Dense Search Response"
Cohesion: 0.33
Nodes (4): DenseSearchResponse, Represents the complete response returned from the dense search pipeline., Number of retrieved results., Highest similarity score.

### Community 96 - "Repo Top-Level Areas"
Cohesion: 0.40
Nodes (6): alembic/ migrations, app/ (FastAPI backend), Astra Study, evaluation/ harness, frontend/ (Streamlit UI), scripts/ (operational one-offs)

### Community 97 - "Alembic Migration Env"
Cohesion: 0.40
Nodes (4): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online()

### Community 98 - "OpenAI Model Enum"
Cohesion: 0.50
Nodes (4): OpenAIModel, Enum, str, Supported OpenAI chat models.

### Community 99 - "Vector Payload Provenance Test"
Cohesion: 0.50
Nodes (5): ChunkMetadata, EmbeddedChunk, _embedded(), parametrize, test_vector_payload_preserves_provenance()

### Community 106 - "Application Settings"
Cohesion: 0.67
Nodes (3): Application settings loaded from environment variables., Settings, BaseSettings

### Community 108 - "Kalam Speech Fixture Doc"
Cohesion: 1.00
Nodes (3): A P J Abdul Kalam Departing Speech (upload 510fce33), A P J Abdul Kalam Departing Speech, Developed India 2020

## Ambiguous Edges - Review These
- `ConversationSummaryService.update_summary` → `tests/conftest.py (Qdrant isolation guard)`  [AMBIGUOUS]
  CLAUDE.md · relation: semantically_similar_to

## Knowledge Gaps
- **57 isolated node(s):** `astra-study`, `In-Context Learning`, `LangSmith Evaluation Runner (evaluation.runner)`, `Guardrails`, `Langfuse` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1074 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **59 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `ConversationSummaryService.update_summary` and `tests/conftest.py (Qdrant isolation guard)`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **Why does `User` connect `Frontend Auth Profile Fetch` to `Frontend Services & Auth`, `User Profile Endpoint`, `RBAC Foundation Tests`, `Team Membership Forbidden & Tests`, `Team Creation Schema & Trim`, `User Registration & Profile Schemas`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `DocumentChunk` connect `Chunk Metadata & Content Segments` to `Chunking Pipeline Tests`, `Settings & Access Enums`, `Chunking Report Analyzer`, `Recursive Stage Heading Logic`, `Chunking Config & Section Matching`, `Document Validator`, `Document Repository Visibility`, `Embedding Pipeline & Batching`, `Hybrid Pipeline Ops`, `Filter Stage`, `Embedded Chunk Model`, `Sparse Embedding Encoder`, `Merge Stage Section Chunks`, `Block Type & Token Counting`, `Embedding Batcher`, `OpenAI Embedder`, `Semantic Stage Merge`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `DocumentBlock` connect `Markdown Token Converter` to `Chunking Pipeline Tests`, `Chunking Report Analyzer`, `Chunking Config & Section Matching`, `Base Ingestion Processor`, `Block Type & Token Counting`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `DocumentChunk` (e.g. with `ChunkPipeline` and `BaseChunkStage`) actually correct?**
  _`DocumentChunk` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 88 inferred relationships involving `BlockType` (e.g. with `FilterStage` and `MergeStage`) actually correct?**
  _`BlockType` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `DocumentBlock` (e.g. with `DocumentConverter` and `HandlerResult`) actually correct?**
  _`DocumentBlock` has 16 INFERRED edges - model-reasoned connections that need verification._