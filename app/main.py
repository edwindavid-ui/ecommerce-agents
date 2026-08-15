from fastapi import FastAPI, HTTPException

from app.db.mongodb import user_collection
from app.db.mongodb import ping_db

from app.api.auth import router as auth_router
from app.api.buyer_agents import router as buyer_agents_router
from app.api.jobs import router as jobs_router
from app.api.negotiations import router as negotiations_router
from app.api.orders import router as orders_router
from app.api.products import router as products_router
from app.api.seller_agents import router as seller_agents_router
from app.core.logging import get_logger

app = FastAPI(title="E-commerce Agent System")
logger = get_logger(__name__)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(buyer_agents_router)
app.include_router(seller_agents_router)
app.include_router(negotiations_router)
app.include_router(orders_router)
app.include_router(jobs_router)


@app.get("/")
def read_root():
    logger.info("Health endpoint accessed")
    return {"message": "E-commerce agent system running"}


@app.get("/health")
async def health_check():
    is_db_up = await ping_db()
    if is_db_up:
        logger.info("Health check requested")
        return {
            "status": "ok",
            "database_status": "up",
                }
    else:
        raise HTTPException(
            status_code=503,
            detail="Database is down"
        )