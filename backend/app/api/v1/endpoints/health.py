from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str


router = APIRouter()


@router.get("/readiness", response_model=HealthResponse)
def readiness_check() -> HealthResponse:
    """Readiness probe for infrastructure and service health."""
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        version=settings.api_version,
    )
