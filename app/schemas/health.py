from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """
    Response model for the health check endpoint.
    """

    status: str
    application: str

    model_config = ConfigDict(
        extra="forbid"
    )