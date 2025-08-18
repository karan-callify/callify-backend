from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import json
from pathlib import Path

from app.api.routes.v1.analysis.models import JobResponse, JobInvite
from app.api.routes.v1.analysis.schemas import AnalysisRead, CountryAnalysis



class AnalysisService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_job_response_info(self) -> JobResponse | None:
        result = await self.session.execute(select(JobResponse).limit(1))
        return result.scalars().first()
    
    async def get_job_invite_info(self) -> JobInvite | None:
        result = await self.session.execute(select(JobInvite).limit(1))
        return result.scalars().first()

    async def get_analysis_of_calls(self, country_code: str | None = None) -> AnalysisRead:
        file_path = Path("app/analysis_results/best_times.json")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = {}
        if country_code:
            country_data = data.get(country_code)
            if country_data:
                result[country_code] = CountryAnalysis(
                    days_90=country_data.get("90_days"),
                    days_7=country_data.get("7_days"),
                )
        else:
            for code, country_data in data.items():
                result[code] = CountryAnalysis(
                    days_90=country_data.get("90_days"),
                    days_7=country_data.get("7_days"),
                )
        return AnalysisRead(data=result)
