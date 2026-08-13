from datetime import datetime, timezone
from typing import Any, Optional

from app.schemas.job import JobCreate


class JobRepository:
    def __init__(self, collection: Any):
        self.collection = collection
        self._jobs: dict[str, dict] = {}

    async def create_job(self, job_data: JobCreate) -> dict:
        """Create a new background job."""
        job_id = f"job_{len(self._jobs) + 1}"
        now = datetime.now(timezone.utc).isoformat()
        
        job = {
            "id": job_id,
            "task_type": job_data.task_type,
            "task_data": job_data.task_data,
            "status": "queued",
            "result": None,
            "error": None,
            "retry_count": 0,
            "max_retries": job_data.max_retries,
            "created_at": now,
            "updated_at": now,
        }
        self._jobs[job_id] = job
        return job

    async def get_job_by_id(self, job_id: str) -> Optional[dict]:
        return self._jobs.get(job_id)

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[dict] = None,
        error: Optional[str] = None,
    ) -> Optional[dict]:
        """Update job status and optionally set result or error."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        job["status"] = status
        job["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        if result is not None:
            job["result"] = result
        if error is not None:
            job["error"] = error
        
        return job

    async def increment_retry_count(self, job_id: str) -> Optional[dict]:
        """Increment retry count and reset status to queued."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        if job["retry_count"] < job["max_retries"]:
            job["retry_count"] += 1
            job["status"] = "queued"
            job["error"] = None
            job["updated_at"] = datetime.now(timezone.utc).isoformat()
            return job
        
        return None  # Max retries exceeded

    async def list_all_jobs(self) -> list[dict]:
        return list(self._jobs.values())

    async def list_jobs_by_status(self, status: str) -> list[dict]:
        return [j for j in self._jobs.values() if j["status"] == status]

    async def list_jobs_by_task_type(self, task_type: str) -> list[dict]:
        return [j for j in self._jobs.values() if j["task_type"] == task_type]
