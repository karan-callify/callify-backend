from fastapi import FastAPI
from app.api.main_router import api_router
from app.workers.worker import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",  # points to app object in this file
        host="0.0.0.0",
        port=8000,
        reload=True
    )
