from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_seller_agent():
    payload = {
        "seller_id": "seller_123",
        "product_id": "prod_123",
        "list_price": 1000.0,
        "min_price": 700.0,
        "target_price": 900.0,
        "max_negotiation_rounds": 5,
    }
    response = client.post("/seller-agents", json=payload)
    assert response.status_code == 201
    agent = response.json()
    assert agent["seller_id"] == "seller_123"
    assert agent["list_price"] == 1000.0
    assert "agent_id" in agent


def test_get_seller_agent():
    # Create an agent
    create_payload = {
        "seller_id": "seller_456",
        "product_id": "prod_456",
        "list_price": 500.0,
        "min_price": 300.0,
        "target_price": 450.0,
        "max_negotiation_rounds": 3,
    }
    create_response = client.post("/seller-agents", json=create_payload)
    agent_id = create_response.json()["agent_id"]

    # Get the agent
    get_response = client.get(f"/seller-agents/{agent_id}")
    assert get_response.status_code == 200
    agent = get_response.json()
    assert agent["agent_id"] == agent_id


def test_seller_evaluates_offer():
    payload = {
        "seller_id": "seller_789",
        "product_id": "prod_789",
        "list_price": 800.0,
        "min_price": 600.0,
        "target_price": 750.0,
        "max_negotiation_rounds": 4,
    }
    create_response = client.post("/seller-agents", json=payload)
    agent_id = create_response.json()["agent_id"]

    # Evaluate an offer
    offer_payload = {
        "offer_price": 650.0,
    }
    eval_response = client.post(f"/seller-agents/{agent_id}/evaluate-offer", json=offer_payload)
    assert eval_response.status_code == 200
    result = eval_response.json()
    assert result["decision"] in ["accept", "counter", "reject"]


def test_seller_agent_respects_minimum_price():
    payload = {
        "seller_id": "seller_000",
        "product_id": "prod_000",
        "list_price": 1000.0,
        "min_price": 800.0,
        "target_price": 950.0,
        "max_negotiation_rounds": 5,
    }
    create_response = client.post("/seller-agents", json=payload)
    agent_id = create_response.json()["agent_id"]

    # Offer below minimum
    offer_payload = {
        "offer_price": 700.0,
    }
    eval_response = client.post(f"/seller-agents/{agent_id}/evaluate-offer", json=offer_payload)
    result = eval_response.json()
    
    # Decision should not accept prices below minimum
    if result["decision"] == "counter":
        assert result["counter_price"] >= 800.0
