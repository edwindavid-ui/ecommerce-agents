from fastapi import APIRouter, HTTPException, status

from app.db.repositories import job_repo
from app.schemas.job import JobCreate, JobStatusUpdate
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Initialize service with shared repository
job_service = JobService(job_repo)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_job(payload: JobCreate):
    """Create a new background job."""
    try:
        result = await job_service.create_job(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.get("/{job_id}")
async def get_job(job_id: str):
    """Retrieve a job by ID."""
    try:
        result = await job_service.get_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result


@router.get("")
async def list_jobs():
    """List all background jobs."""
    jobs = await job_service.list_jobs()
    return {"jobs": jobs}


@router.patch("/{job_id}/status")
async def update_job_status(job_id: str, payload: JobStatusUpdate):
    """Update the status of a job."""
    try:
        result = await job_service.update_job_status(
            job_id, payload.status, payload.result, payload.error
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.post("/{job_id}/retry")
async def retry_job(job_id: str):
    """Retry a failed job."""
    try:
        result = await job_service.retry_job(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result
