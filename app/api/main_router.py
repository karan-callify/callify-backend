from fastapi import APIRouter
from app.api.routes.v1.analysis import routes as analysis_routes


api_router = APIRouter()
api_router.include_router(analysis_routes.router, prefix="/api/v1/analysis", tags=["analysis"])