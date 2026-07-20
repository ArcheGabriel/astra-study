from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    APP_NAME: str = "Astra Study"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = """
    🚀 Astra Study is an AI-powered multimodal study assistant.

    Features:
    - Chat with documents
    - Multimodal document understanding
    - Retrieval-Augmented Generation (RAG)
    - GPT-5 powered responses
    - Semantic Chunking
    - Hybrid Search
    """

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    API_V1_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str

    # ------------------------------------------------------------------
    # OpenAI
    # ------------------------------------------------------------------
    OPENAI_API_KEY: str
    OPENAI_CHAT_MODEL: str = "gpt-5"

    # ------------------------------------------------------------------
    # Qdrant
    # ------------------------------------------------------------------
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str = "astra_study"
    # Dense vector name
    QDRANT_VECTOR_NAME: str = "dense"
    # Sparse vector name
    QDRANT_SPARSE_VECTOR_NAME: str = "sparse"
    # settings.py
    QDRANT_HYBRID_CANDIDATE_LIMIT: int = 50

    # ------------------------------------------------------------------
    # LangSmith
    # ------------------------------------------------------------------
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_TRACING: bool = True
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_PROJECT: str = "Astra-Study"

    # ------------------------------------------------------------------
    # Langfuse
    # ------------------------------------------------------------------
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_HOST: str | None = None

    # ------------------------------------------------------------------
    # Document Upload
    # ------------------------------------------------------------------
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_DOCUMENT_EXTENSIONS: tuple[str, ...] = (
        ".pdf",
        ".docx",
        ".txt",
        ".md",
    )

    ALLOWED_CONTENT_TYPES: tuple[str, ...] = (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
    )
    
    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS: int = 3072
    EMBEDDING_MAX_BATCH_SIZE: int = 100
    EMBEDDING_MAX_RETRIES: int = 3
    EMBEDDING_TIMEOUT_SECONDS: int = 60
    EMBEDDING_PRICE_PER_MILLION_INPUT_TOKENS: float = 0.13
    
    # ------------------------------------------------------------------
    # Sparse Embeddings
    # ------------------------------------------------------------------
    SPARSE_EMBEDDING_MODEL: str = (
        "Qdrant/bm42-all-minilm-l6-v2-attentions"
    )
    
    # ------------------------------------------------------------------
    # Cross Encoder Reranker
    # ------------------------------------------------------------------
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANKER_BATCH_SIZE: int = 32
    RERANKER_MAX_LENGTH: int = 512
    RERANK_TOP_K: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()