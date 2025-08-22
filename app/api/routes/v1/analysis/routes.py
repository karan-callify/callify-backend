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
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/analysis_of_calls", response_model=AnalysisRead)
async def get_analysis_of_calls(
    service: AnalysisServiceDep,
    country_code: Optional[str] = None,
):
    """
    Get analysis of calls with optional filters for country.
    """
    try:
        result = await service.get_analysis_of_calls(country_code)

        # Case 1: No results (service returned None or empty dict)
        if not result or not result.data:
            logger.warning(f"No analysis data found. country_code={country_code}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No analysis data found for the given filters."
            )

        return result

    except ValueError as ve:
        # Case 2: Bad input (e.g., invalid country code)
        logger.warning(f"Invalid input in analysis_of_calls: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except HTTPException:
        # Already a FastAPI HTTPException → just bubble up
        raise
    
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