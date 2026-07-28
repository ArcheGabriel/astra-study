import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.config.settings import settings
from app.exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Astra Study is starting...")

    # ------------------------------------------------------------------
    # Export LangSmith settings to process environment
    # ------------------------------------------------------------------
    os.environ["LANGSMITH_TRACING"] = str(
        settings.LANGSMITH_TRACING
    ).lower()

    os.environ["LANGSMITH_API_KEY"] = (
        settings.LANGSMITH_API_KEY or ""
    )

    os.environ["LANGSMITH_ENDPOINT"] = (
        settings.LANGSMITH_ENDPOINT
    )

    os.environ["LANGSMITH_PROJECT"] = (
        settings.LANGSMITH_PROJECT
    )

    print("\n========== LangSmith Environment ==========")
    print(f"LANGSMITH_TRACING  : {os.getenv('LANGSMITH_TRACING')}")
    print(f"LANGSMITH_ENDPOINT : {os.getenv('LANGSMITH_ENDPOINT')}")
    print(f"LANGSMITH_PROJECT  : {os.getenv('LANGSMITH_PROJECT')}")
    print(
        f"LANGSMITH_API_KEY  : {'Loaded' if os.getenv('LANGSMITH_API_KEY') else 'NOT FOUND'}"
    )
    print("===========================================\n")

    yield

    print("🛑 Astra Study is shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)

register_exception_handlers(app)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Astra Study 🚀"
    }