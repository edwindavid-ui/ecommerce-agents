from typing import Any, Optional

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    task_type: str = Field(..., min_length=1)
    task_data: dict[str, Any]
    max_retries: int = Field(default=3, ge=0)


class JobResponse(BaseModel):
    job_id: str
    task_type: str
    task_data: dict[str, Any]
    status: str  # queued, running, completed, failed
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int
    created_at: str
    updated_at: str


class JobStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(queued|running|completed|failed)$")
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
