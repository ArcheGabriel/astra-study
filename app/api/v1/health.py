from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the health status of the Astra Study API.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        application="Astra Study",
    )