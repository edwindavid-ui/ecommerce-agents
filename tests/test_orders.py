import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def setup_negotiation():
    """Setup a completed negotiation to create an order from."""
    # Create negotiation
    neg_response = client.post(
        "/negotiations",
        json={
            "buyer_id": "buyer1",
            "seller_id": "seller1",
            "product_id": "product1",
            "buyer_max_price": 500.0,
            "seller_min_price": 100.0,
            "seller_target_price": 300.0,
            "max_rounds": 5,
        },
    )
    assert neg_response.status_code == 201
    negotiation_id = neg_response.json()["negotiation_id"]

    # Make an offer that will be accepted
    offer_response = client.post(
        f"/negotiations/{negotiation_id}/offer",
        json={"actor": "buyer", "offer_price": 350.0},
    )
    assert offer_response.status_code == 200
    assert offer_response.json()["status"] == "accepted"

    return negotiation_id


def test_create_order_from_negotiation(setup_negotiation):
    """Test creating an order from an accepted negotiation."""
    negotiation_id = setup_negotiation

    response = client.post(
        "/orders",
        json={"negotiation_id": negotiation_id},
    )

    assert response.status_code == 201
    data = response.json()
    assert "order_id" in data
    assert data["negotiation_id"] == negotiation_id
    assert data["status"] == "pending"
    assert data["buyer_id"] == "buyer1"
    assert data["seller_id"] == "seller1"
    assert data["product_id"] == "product1"
    assert data["final_price"] == 350.0


def test_get_order(setup_negotiation):
    """Test retrieving an order by ID."""
    negotiation_id = setup_negotiation

    create_response = client.post(
        "/orders",
        json={"negotiation_id": negotiation_id},
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["order_id"]

    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == order_id
    assert data["status"] == "pending"
    assert data["negotiation_id"] == negotiation_id


def test_list_orders_by_buyer(setup_negotiation):
    """Test listing orders for a buyer."""
    negotiation_id = setup_negotiation

    create_response = client.post(
        "/orders",
        json={"negotiation_id": negotiation_id},
    )
    assert create_response.status_code == 201

    response = client.get("/orders?buyer_id=buyer1")

    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert len(data["orders"]) > 0
    assert data["orders"][0]["buyer_id"] == "buyer1"


def test_cannot_create_order_from_rejected_negotiation():
    """Test that orders cannot be created from rejected negotiations."""
    # Create a negotiation with an impossible constraint
    neg_response = client.post(
        "/negotiations",
        json={
            "buyer_id": "buyer2",
            "seller_id": "seller2",
            "product_id": "product2",
            "buyer_max_price": 100.0,
            "seller_min_price": 200.0,
            "seller_target_price": 250.0,
            "max_rounds": 1,
        },
    )
    # Should fail because seller minimum exceeds buyer maximum
    assert neg_response.status_code == 400

    # Create a valid negotiation but make a low offer that gets rejected
    neg_response = client.post(
        "/negotiations",
        json={
            "buyer_id": "buyer2",
            "seller_id": "seller2",
            "product_id": "product2",
            "buyer_max_price": 500.0,
            "seller_min_price": 300.0,
            "seller_target_price": 400.0,
            "max_rounds": 5,
        },
    )
    assert neg_response.status_code == 201
    negotiation_id = neg_response.json()["negotiation_id"]

    # Make a low offer (it will be accepted by API but rejected by seller logic)
    offer_response = client.post(
        f"/negotiations/{negotiation_id}/offer",
        json={"actor": "buyer", "offer_price": 100.0},
    )
    # API accepts the offer, but seller rejects it (status=rejected)
    assert offer_response.status_code == 200
    assert offer_response.json()["status"] == "rejected"

    # Try to create order from rejected negotiation - should fail
    response = client.post(
        "/orders",
        json={"negotiation_id": negotiation_id},
    )
    assert response.status_code == 400
