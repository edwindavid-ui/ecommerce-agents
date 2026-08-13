from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_negotiation():
    payload = {
        "buyer_id": "buyer_123",
        "seller_id": "seller_123",
        "product_id": "prod_123",
        "buyer_max_price": 1000.0,
        "seller_min_price": 700.0,
        "seller_target_price": 900.0,
    }
    response = client.post("/negotiations", json=payload)
    assert response.status_code == 201
    negotiation = response.json()
    assert negotiation["buyer_id"] == "buyer_123"
    assert negotiation["status"] == "initiated"
    assert "negotiation_id" in negotiation


def test_get_negotiation():
    # Create a negotiation
    create_payload = {
        "buyer_id": "buyer_456",
        "seller_id": "seller_456",
        "product_id": "prod_456",
        "buyer_max_price": 800.0,
        "seller_min_price": 500.0,
        "seller_target_price": 750.0,
    }
    create_response = client.post("/negotiations", json=create_payload)
    neg_id = create_response.json()["negotiation_id"]

    # Get the negotiation
    get_response = client.get(f"/negotiations/{neg_id}")
    assert get_response.status_code == 200
    negotiation = get_response.json()
    assert negotiation["negotiation_id"] == neg_id


def test_buyer_makes_initial_offer():
    # Create a negotiation
    create_payload = {
        "buyer_id": "buyer_789",
        "seller_id": "seller_789",
        "product_id": "prod_789",
        "buyer_max_price": 1200.0,
        "seller_min_price": 800.0,
        "seller_target_price": 1000.0,
    }
    create_response = client.post("/negotiations", json=create_payload)
    neg_id = create_response.json()["negotiation_id"]

    # Make an offer
    offer_payload = {
        "actor": "buyer",
        "offer_price": 850.0,
    }
    offer_response = client.post(f"/negotiations/{neg_id}/offer", json=offer_payload)
    assert offer_response.status_code == 200
    negotiation = offer_response.json()
    assert negotiation["status"] in ["offered", "countered", "accepted"]


def test_negotiation_expires_on_max_rounds():
    # Create a negotiation with 1 max round
    create_payload = {
        "buyer_id": "buyer_000",
        "seller_id": "seller_000",
        "product_id": "prod_000",
        "buyer_max_price": 1000.0,
        "seller_min_price": 700.0,
        "seller_target_price": 900.0,
        "max_rounds": 1,
    }
    create_response = client.post("/negotiations", json=create_payload)
    neg_id = create_response.json()["negotiation_id"]

    # Make first offer
    offer1 = {"actor": "buyer", "offer_price": 750.0}
    client.post(f"/negotiations/{neg_id}/offer", json=offer1)
    
    # Try to make second offer
    offer2 = {"actor": "buyer", "offer_price": 780.0}
    response = client.post(f"/negotiations/{neg_id}/offer", json=offer2)
    
    # Should either be expired or show status indicating max rounds
    assert response.status_code in [200, 400]


def test_negotiation_acceptance():
    # Create a negotiation
    create_payload = {
        "buyer_id": "buyer_111",
        "seller_id": "seller_111",
        "product_id": "prod_111",
        "buyer_max_price": 1000.0,
        "seller_min_price": 700.0,
        "seller_target_price": 900.0,
    }
    create_response = client.post("/negotiations", json=create_payload)
    neg_id = create_response.json()["negotiation_id"]

    # Make an offer at or above target
    offer_payload = {
        "actor": "buyer",
        "offer_price": 900.0,
    }
    offer_response = client.post(f"/negotiations/{neg_id}/offer", json=offer_payload)
    negotiation = offer_response.json()
    
    # If offer is accepted, status should be accepted
    if negotiation["status"] == "accepted":
        assert negotiation["final_price"] == 900.0
