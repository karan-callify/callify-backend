from pydantic import BaseModel
from typing import Optional, Dict, List, Any


class BestHours(BaseModel):
    mon: Optional[List[str]] = []
    tue: Optional[List[str]] = []
    wed: Optional[List[str]] = []
    thu: Optional[List[str]] = []
    fri: Optional[List[str]] = []
    sat: Optional[List[str]] = []
    sun: Optional[List[str]] = []


class AnalysisPeriod(BaseModel):
    best_hours: BestHours
    avg_number_of_question_user_answers: float
    average_call_time: float


class CountryAnalysis(BaseModel):
    days_90: Optional[AnalysisPeriod] = None
    days_7: Optional[AnalysisPeriod] = None


class AnalysisRead(BaseModel):
    data: Dict[str, CountryAnalysis]