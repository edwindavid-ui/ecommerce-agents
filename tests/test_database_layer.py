import pytest

from app.db.repositories.products import ProductRepository
from app.schemas.product import ProductCreate


class FakeCollection:
    def __init__(self):
        self.calls = []

    def find(self, query):
        self.calls.append(("find", query))
        return []


def test_product_schema_validates_core_fields():
    product = ProductCreate(
        name="Laptop",
        category="electronics",
        price=999.99,
        seller_id="seller_123",
        description="Portable workstation",
    )

    assert product.name == "Laptop"
    assert product.category == "electronics"
    assert product.price == 999.99
    assert product.status == "active"


def test_product_repository_build_filters_limits_price_and_category():
    repo = ProductRepository(collection=FakeCollection())
    filters = repo.build_filters(category="electronics", max_price=500)

    assert filters == {"category": "electronics", "price": {"$lte": 500}}
