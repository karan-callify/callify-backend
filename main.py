# main.py
from fastapi import FastAPI
from app.api.main_router import api_router
from app.core.logger import setup_logger
from app.workers.worker import lifespan

logger = setup_logger("main")

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
