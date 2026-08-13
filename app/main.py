from fastapi import FastAPI

from app.core.logging import get_logger

app = FastAPI(title="E-commerce Agent System")
logger = get_logger(__name__)


@app.get("/")
def read_root():
    logger.info("Health endpoint accessed")
    return {"message": "E-commerce agent system running"}


@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}
