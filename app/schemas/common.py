from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard application error payload returned by exception handlers."""

    detail: str = Field(..., description="Human-readable error message")


class HealthResponse(BaseModel):
    """Liveness probe response."""

    status: str = Field(..., description="Service health status", examples=["ok"])
