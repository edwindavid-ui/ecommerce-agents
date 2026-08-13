from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_buyer_task():
    payload = {
        "buyer_id": "buyer_123",
        "requirement": "I need a laptop for coding and machine learning",
        "budget": 2000.0,
        "category": "electronics",
    }
    response = client.post("/buyer-agents/tasks", json=payload)
    assert response.status_code == 201
    task = response.json()
    assert task["buyer_id"] == "buyer_123"
    assert task["status"] == "task_created"
    assert "task_id" in task


def test_get_buyer_task_status():
    # Create a task
    create_payload = {
        "buyer_id": "buyer_456",
        "requirement": "Looking for a gaming laptop",
        "budget": 1500.0,
        "category": "electronics",
    }
    create_response = client.post("/buyer-agents/tasks", json=create_payload)
    task_id = create_response.json()["task_id"]

    # Get the task
    get_response = client.get(f"/buyer-agents/tasks/{task_id}")
    assert get_response.status_code == 200
    task = get_response.json()
    assert task["task_id"] == task_id
    assert task["buyer_id"] == "buyer_456"


def test_start_buyer_task():
    # Create a task
    create_payload = {
        "buyer_id": "buyer_789",
        "requirement": "Budget-friendly laptop for daily work",
        "budget": 800.0,
        "category": "electronics",
    }
    create_response = client.post("/buyer-agents/tasks", json=create_payload)
    task_id = create_response.json()["task_id"]

    # Start the task
    start_response = client.post(f"/buyer-agents/tasks/{task_id}/start")
    assert start_response.status_code == 200
    task = start_response.json()
    assert task["status"] in ["analyzing_requirements", "searching", "completed"]


def test_cancel_buyer_task():
    # Create a task
    create_payload = {
        "buyer_id": "buyer_000",
        "requirement": "Test cancellation",
        "budget": 500.0,
        "category": "electronics",
    }
    create_response = client.post("/buyer-agents/tasks", json=create_payload)
    task_id = create_response.json()["task_id"]

    # Cancel the task
    cancel_response = client.post(f"/buyer-agents/tasks/{task_id}/cancel")
    assert cancel_response.status_code == 200
    task = cancel_response.json()
    assert task["status"] == "cancelled"
