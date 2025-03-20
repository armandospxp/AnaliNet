from pydantic import BaseModel, Field, validator
from typing import Optional, List
from ..models.laboratory import SampleState, SamplePreservation

class SampleTypeBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    state: SampleState
    preservation: SamplePreservation
    max_storage_time: int = Field(..., gt=0)
    storage_instructions: str
    container_type: str
    minimum_volume: float = Field(..., gt=0)

    @validator('code')
    def validate_code(cls, v):
        return v.upper()

class SampleTypeCreate(SampleTypeBase):
    pass

class SampleTypeResponse(SampleTypeBase):
    id: int

    class Config:
        orm_mode = True

class MeasurementMethodBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    principle: str
    equipment_type: str

    @validator('code')
    def validate_code(cls, v):
        return v.upper()

class MeasurementMethodCreate(MeasurementMethodBase):
    pass

class MeasurementMethodResponse(MeasurementMethodBase):
    id: int

    class Config:
        orm_mode = True

class MeasurementUnitBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    category: str
    conversion_factor: Optional[float] = None
    si_unit: Optional[str] = None

    @validator('code')
    def validate_code(cls, v):
        return v.strip()

class MeasurementUnitCreate(MeasurementUnitBase):
    pass

class MeasurementUnitResponse(MeasurementUnitBase):
    id: int

    class Config:
        orm_mode = True

# Schemas para asociar métodos y unidades a determinaciones
class DeterminationMethodConfig(BaseModel):
    determination_id: int
    method_id: int
    equipment_id: Optional[int] = None
    is_default: bool = False
    validation_rules: Optional[dict] = None

class DeterminationUnitConfig(BaseModel):
    determination_id: int
    unit_id: int
    is_default: bool = False
    conversion_formula: Optional[str] = None  # Fórmula para convertir a otras unidades
