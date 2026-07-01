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

    # ------------------------------------------------------------------
    # Qdrant
    # ------------------------------------------------------------------
    QDRANT_URL: str

    # ------------------------------------------------------------------
    # LangSmith
    # ------------------------------------------------------------------
    LANGCHAIN_API_KEY: str

    # ------------------------------------------------------------------
    # Langfuse
    # ------------------------------------------------------------------
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()