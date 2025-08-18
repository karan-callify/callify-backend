from fastapi import FastAPI
from app.api.main_router import api_router
from contextlib import asynccontextmanager
from app.workers.worker import lifespan

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await connect_to_mongo()
#     yield
#     await close_mongo_connection()

app = FastAPI(lifespan=lifespan)
# app = FastAPI()

app.include_router(api_router)



