# app/api/routes/v1/portfolio/dependencies.py

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.api.routes.v1.analysis.services import AnalysisService

# DB Dependencies
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Service Dependency
def get_analysis_service(
    session: SessionDep,
) -> AnalysisService:
    return AnalysisService(session=session)

AnalysisServiceDep = Annotated[AnalysisService, Depends(get_analysis_service)]