import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_background_job():
    """Test creating a background job for a long-running task."""
    response = client.post(
        "/jobs",
        json={
            "task_type": "negotiate",
            "task_data": {
                "negotiation_id": "neg_1",
                "buyer_id": "buyer1",
                "seller_id": "seller1",
            },
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert data["task_type"] == "negotiate"


def test_get_job_status():
    """Test retrieving job status."""
    create_response = client.post(
        "/jobs",
        json={
            "task_type": "process_order",
            "task_data": {"order_id": "order_1"},
        },
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["job_id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["task_type"] == "process_order"
    assert data["status"] in ["queued", "running", "completed", "failed"]


def test_list_jobs():
    """Test listing all background jobs."""
    # Create a job
    create_response = client.post(
        "/jobs",
        json={
            "task_type": "analyze",
            "task_data": {"buyer_id": "buyer1"},
        },
    )
    assert create_response.status_code == 201

    response = client.get("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert isinstance(data["jobs"], list)


def test_job_status_transitions():
    """Test that jobs can transition through states."""
    # Create job
    create_response = client.post(
        "/jobs",
        json={
            "task_type": "test_task",
            "task_data": {"test": "data"},
        },
    )
    job_id = create_response.json()["job_id"]

    # Job starts in queued state
    response = client.get(f"/jobs/{job_id}")
    assert response.json()["status"] == "queued"

    # Simulate job processing
    update_response = client.patch(
        f"/jobs/{job_id}/status",
        json={"status": "running"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "running"

    # Mark job as completed
    complete_response = client.patch(
        f"/jobs/{job_id}/status",
        json={"status": "completed", "result": {"success": True}},
    )
    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"


def test_job_retry_on_failure():
    """Test that failed jobs can be retried."""
    create_response = client.post(
        "/jobs",
        json={
            "task_type": "retry_test",
            "task_data": {"test": "data"},
            "max_retries": 3,
        },
    )
    job_id = create_response.json()["job_id"]

    # Mark as failed
    fail_response = client.patch(
        f"/jobs/{job_id}/status",
        json={"status": "failed", "error": "Test error"},
    )
    assert fail_response.status_code == 200

    # Retry the job
    retry_response = client.post(f"/jobs/{job_id}/retry")
    assert retry_response.status_code == 200
    data = retry_response.json()
    assert data["status"] == "queued"
