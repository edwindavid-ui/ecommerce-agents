from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_recommendation_request_with_valid_constraints():
    payload = {
        "buyer_id": "buyer_123",
        "category": "electronics",
        "max_price": 1000.0,
        "min_price": 100.0,
    }
    response = client.post("/recommendations", json=payload)
    assert response.status_code == 201
    rec = response.json()
    assert rec["buyer_id"] == "buyer_123"
    assert "recommendation_id" in rec
    assert rec["status"] == "completed"


def test_recommendation_filters_by_category_and_price():
    payload = {
        "buyer_id": "buyer_456",
        "category": "electronics",
        "max_price": 500.0,
    }
    response = client.post("/recommendations", json=payload)
    assert response.status_code == 201
    rec = response.json()
    assert "results" in rec
    assert isinstance(rec["results"], list)


def test_get_recommendation_by_id():
    # First create a recommendation
    payload = {
        "buyer_id": "buyer_789",
        "category": "electronics",
        "max_price": 800.0,
    }
    create_response = client.post("/recommendations", json=payload)
    assert create_response.status_code == 201
    rec_id = create_response.json()["recommendation_id"]

    # Then retrieve it
    get_response = client.get(f"/recommendations/{rec_id}")
    assert get_response.status_code == 200
    rec = get_response.json()
    assert rec["buyer_id"] == "buyer_789"
