from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict
from ..models.test_types import AlertLevel, ResultType, Gender

class ReferenceRangeBase(BaseModel):
    gender: Gender
    min_age: int = Field(ge=0)
    max_age: int = Field(ge=0)
    min_value: float
    max_value: float
    warning_low: float
    warning_high: float
    critical_low: float
    critical_high: float

class ReferenceRangeCreate(ReferenceRangeBase):
    pass

class ReferenceRangeResponse(ReferenceRangeBase):
    id: int
    determination_id: int

    class Config:
        from_attributes = True

class CategoricalValueBase(BaseModel):
    value: str
    alert_level: AlertLevel
    is_default: bool = False

class CategoricalValueCreate(CategoricalValueBase):
    pass

class CategoricalValueResponse(CategoricalValueBase):
    id: int
    determination_id: int

    class Config:
        from_attributes = True

class DeterminationBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None
    result_type: ResultType
    decimal_places: Optional[int] = 2

class DeterminationCreate(DeterminationBase):
    reference_ranges: Optional[List[ReferenceRangeCreate]] = None
    categorical_values: Optional[List[CategoricalValueCreate]] = None

class DeterminationResponse(DeterminationBase):
    id: int
    reference_ranges: List[ReferenceRangeResponse]
    categorical_values: List[CategoricalValueResponse]

    class Config:
        from_attributes = True

class DeterminationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    decimal_places: Optional[int] = None
    reference_ranges: Optional[List[ReferenceRangeCreate]] = None
    categorical_values: Optional[List[CategoricalValueCreate]] = None

class AnalysisTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category: str
    sample_type: str
    instructions: Optional[str] = None

class AnalysisTypeCreate(AnalysisTypeBase):
    determination_ids: List[int]

class AnalysisTypeResponse(AnalysisTypeBase):
    id: int
    determinations: List[DeterminationResponse]

    class Config:
        from_attributes = True

class AnalysisTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    sample_type: Optional[str] = None
    instructions: Optional[str] = None
    determination_ids: Optional[List[int]] = None

class ResultEvaluation(BaseModel):
    value: Union[float, str]
    alert_level: AlertLevel
    reference_range: Optional[Dict[str, float]] = None  # Para valores numéricos
    categorical_value: Optional[Dict[str, str]] = None  # Para valores categóricos
