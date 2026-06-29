from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
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
    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str

    # Qdrant
    QDRANT_URL: str

    # LangSmith
    LANGCHAIN_API_KEY: str

    # Langfuse
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()