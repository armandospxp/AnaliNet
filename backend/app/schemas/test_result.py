from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TestResultBase(BaseModel):
    patient_id: str
    test_code: str
    test_name: str
    result_value: str
    units: Optional[str] = None
    reference_range: Optional[str] = None
    flags: Optional[str] = None
    status: Optional[str] = None

class TestResultCreate(TestResultBase):
    equipment_id: int
    raw_message: Optional[str] = None

class TestResultResponse(TestResultBase):
    id: int
    equipment_id: int
    result_datetime: datetime
    raw_message: Optional[str] = None

    class Config:
        from_attributes = True

class TestResultFilter(BaseModel):
    patient_id: Optional[str] = None
    test_code: Optional[str] = None
    equipment_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
