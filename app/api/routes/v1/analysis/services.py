import json
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.routes.v1.analysis.models import JobResponse, JobInvite
from app.api.routes.v1.analysis.schemas import AnalysisRead


class AnalysisService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_job_response_info(self) -> JobResponse | None:
        result = await self.session.execute(select(JobResponse).limit(1))
        return result.scalars().first()

    async def get_job_invite_info(self) -> JobInvite | None:
        result = await self.session.execute(select(JobInvite).limit(1))
        return result.scalars().first()

    async def get_analysis_of_calls(self, country_code: Optional[str] = None) -> AnalysisRead:
        file_path = Path("app/analysis_results/best_times.json")

        if not file_path.exists():
            raise FileNotFoundError(f"Analysis results file not found at {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as je:
            raise ValueError(f"Invalid JSON format in {file_path}: {je}") from je
        except Exception as e:
            raise RuntimeError(f"Unexpected error while reading {file_path}: {e}") from e

        if country_code:
            if country_code not in data:
                raise ValueError(f"No analysis data found for country_code={country_code}")
            return AnalysisRead(data={country_code: data[country_code]})

        return AnalysisRead(data=data)
