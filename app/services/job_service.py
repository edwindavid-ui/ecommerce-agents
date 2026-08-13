from app.db.repositories.jobs import JobRepository
from app.schemas.job import JobCreate
from typing import Optional, Any


class JobService:
    def __init__(self, job_repo: JobRepository):
        self.job_repo = job_repo

    async def create_job(self, job_data: JobCreate) -> dict:
        """Create a new background job."""
        job = await self.job_repo.create_job(job_data)
        
        return {
            "job_id": job["id"],
            "task_type": job["task_type"],
            "task_data": job["task_data"],
            "status": job["status"],
            "result": job["result"],
            "error": job["error"],
            "retry_count": job["retry_count"],
            "max_retries": job["max_retries"],
            "created_at": job["created_at"],
            "updated_at": job["updated_at"],
        }

    async def get_job(self, job_id: str) -> dict:
        """Retrieve a job by ID."""
        job = await self.job_repo.get_job_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        
        return {
            "job_id": job["id"],
            "task_type": job["task_type"],
            "task_data": job["task_data"],
            "status": job["status"],
            "result": job["result"],
            "error": job["error"],
            "retry_count": job["retry_count"],
            "max_retries": job["max_retries"],
            "created_at": job["created_at"],
            "updated_at": job["updated_at"],
        }

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[dict] = None,
        error: Optional[str] = None,
    ) -> dict:
        """Update job status."""
        # Validate status
        valid_statuses = ["queued", "running", "completed", "failed"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        
        job = await self.job_repo.update_job_status(job_id, status, result, error)
        if not job:
            raise ValueError("Job not found")
        
        return {
            "job_id": job["id"],
            "task_type": job["task_type"],
            "task_data": job["task_data"],
            "status": job["status"],
            "result": job["result"],
            "error": job["error"],
            "retry_count": job["retry_count"],
            "max_retries": job["max_retries"],
            "created_at": job["created_at"],
            "updated_at": job["updated_at"],
        }

    async def retry_job(self, job_id: str) -> dict:
        """Retry a failed job."""
        job = await self.job_repo.get_job_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        
        if job["status"] != "failed":
            raise ValueError(f"Cannot retry job with status: {job['status']}")
        
        updated_job = await self.job_repo.increment_retry_count(job_id)
        if not updated_job:
            raise ValueError("Maximum retries exceeded")
        
        return {
            "job_id": updated_job["id"],
            "task_type": updated_job["task_type"],
            "task_data": updated_job["task_data"],
            "status": updated_job["status"],
            "result": updated_job["result"],
            "error": updated_job["error"],
            "retry_count": updated_job["retry_count"],
            "max_retries": updated_job["max_retries"],
            "created_at": updated_job["created_at"],
            "updated_at": updated_job["updated_at"],
        }

    async def list_jobs(self) -> list[dict]:
        """List all jobs."""
        jobs = await self.job_repo.list_all_jobs()
        return [
            {
                "job_id": job["id"],
                "task_type": job["task_type"],
                "task_data": job["task_data"],
                "status": job["status"],
                "result": job["result"],
                "error": job["error"],
                "retry_count": job["retry_count"],
                "max_retries": job["max_retries"],
                "created_at": job["created_at"],
                "updated_at": job["updated_at"],
            }
            for job in jobs
        ]
