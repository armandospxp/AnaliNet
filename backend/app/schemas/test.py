from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TestTypeBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    reference_range: Dict[str, Any]
    machine_interface: Optional[str] = None

class TestTypeCreate(TestTypeBase):
    pass

class TestType(TestTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TestResultBase(BaseModel):
    patient_id: int
    test_type_id: int
    value: float
    unit: str
    notes: Optional[str] = None
    analyzed_by: str
    raw_data: Optional[Dict[str, Any]] = None

class TestResultCreate(TestResultBase):
    pass

class TestResult(TestResultBase):
    id: int
    is_abnormal: bool
    validated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
