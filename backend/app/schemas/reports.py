from pydantic import BaseModel, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from .test_types import AnalysisTypeResponse, DeterminationResponse
from ..models.test_types import AlertLevel

class TestResultBase(BaseModel):
    analysis_id: int
    determination_id: int
    equipment_id: Optional[int]
    value: str
    unit: str
    reference_range: Dict[str, Any]
    alert_level: AlertLevel
    observation: Optional[str]

class TestResultCreate(TestResultBase):
    pass

class TestResultResponse(TestResultBase):
    id: int
    report_id: int
    processed_at: datetime
    validated_at: Optional[datetime]
    analysis: AnalysisTypeResponse
    determination: DeterminationResponse

    class Config:
        orm_mode = True

class ReportBase(BaseModel):
    admission_number: str
    patient_id: int
    doctor_id: Optional[int]
    technician_id: Optional[int]
    validator_id: Optional[int]
    status: str

    @validator('status')
    def validate_status(cls, v):
        allowed = {'draft', 'validated', 'printed'}
        if v not in allowed:
            raise ValueError(f'Status debe ser uno de: {allowed}')
        return v

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: int
    report_date: datetime
    results: List[TestResultResponse]

    class Config:
        orm_mode = True

class StatisticalMetrics(BaseModel):
    total_patients: int
    total_tests: int
    tests_by_category: Dict[str, int]
    results_by_alert: Dict[str, int]
    top_analyses: Dict[str, int]
    top_doctors: Dict[str, int]
    average_tests_per_patient: float

class StatisticalReportBase(BaseModel):
    report_type: str
    start_date: datetime
    end_date: datetime
    metrics: StatisticalMetrics

    @validator('report_type')
    def validate_report_type(cls, v):
        allowed = {'daily', 'monthly', 'custom'}
        if v not in allowed:
            raise ValueError(f'Report type debe ser uno de: {allowed}')
        return v

class StatisticalReportCreate(StatisticalReportBase):
    pass

class StatisticalReportResponse(StatisticalReportBase):
    id: int
    generated_at: datetime
    generated_by: int

    class Config:
        orm_mode = True
