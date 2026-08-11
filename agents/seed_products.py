import asyncio
from database import products_collection

PRODUCTS = [
    {"name": "Wireless Earbuds", "category": "electronics", "price": 45.0},
    {"name": "Bluetooth Speaker", "category": "electronics", "price": 60.0},
    {"name": "Running Shoes", "category": "fashion", "price": 80.0},
    {"name": "Backpack", "category": "fashion", "price": 35.0},
    {"name": "Desk Lamp", "category": "home", "price": 25.0},
]

async def seed():
    await products_collection.delete_many({})
    await products_collection.insert_many(PRODUCTS)
    print("Products inserted successfully.")

asyncio.run(seed())