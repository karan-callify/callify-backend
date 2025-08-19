from typing import Optional
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    File,
    Form,
    UploadFile,
    Response
)
from fastapi.responses import JSONResponse
from pydantic import EmailStr

from app.api.dependencies import AnalysisServiceDep
from app.api.routes.v1.analysis.schemas import (
    AnalysisRead
)

router = APIRouter()


@router.get("/analysis_of_calls", response_model=AnalysisRead)
async def get_analysis_of_calls(
    service: AnalysisServiceDep,
    country_code: Optional[str] = None,
):
    """
    Get analysis of calls with optional filters for country and date range.
    """
    try:
        result = await service.get_analysis_of_calls(country_code)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "API is live"
        }
    )