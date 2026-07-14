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
    
    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS: int = 3072
    EMBEDDING_MAX_BATCH_SIZE: int = 100
    EMBEDDING_MAX_RETRIES: int = 3
    EMBEDDING_TIMEOUT_SECONDS: int = 60
    EMBEDDING_PRICE_PER_MILLION_INPUT_TOKENS: float = 0.13

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()