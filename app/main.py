from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.settings import settings
from app.api.v1.api import api_router

from app.exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Astra Study is starting...")

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