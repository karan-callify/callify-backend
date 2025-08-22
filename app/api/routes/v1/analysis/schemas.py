from pydantic import BaseModel
from typing import Dict, Optional


class WeekDays(BaseModel):
    mon: Optional[Dict[str, Dict[str, float]]] = None
    tue: Optional[Dict[str, Dict[str, float]]] = None
    wed: Optional[Dict[str, Dict[str, float]]] = None
    thu: Optional[Dict[str, Dict[str, float]]] = None
    fri: Optional[Dict[str, Dict[str, float]]] = None
    sat: Optional[Dict[str, Dict[str, float]]] = None
    sun: Optional[Dict[str, Dict[str, float]]] = None

class CompleteAnalysis(WeekDays):
    avg_call_duration: float = 0.0
    avg_number_of_questions_answered: float = 0.0

class CountryAnalysis(BaseModel):
    three_months: CompleteAnalysis
    seven_days: CompleteAnalysis

class AnalysisRead(BaseModel):
    data: Dict[str, CountryAnalysis]
