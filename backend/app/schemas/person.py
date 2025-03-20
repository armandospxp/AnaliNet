from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import date
from ..models.person import Gender

class LocationBase(BaseModel):
    city: str
    neighborhood: Optional[str] = None
    department: str

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    id: int

    class Config:
        orm_mode = True

class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    document_number: str = Field(..., min_length=6, max_length=20)
    birth_date: date
    gender: Gender
    location_id: int

    @validator('document_number')
    def validate_document(cls, v):
        if not v.isdigit():
            raise ValueError('Número de documento debe contener solo dígitos')
        return v

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    age: int
    location: LocationResponse

    class Config:
        orm_mode = True

class DoctorBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    document_number: str = Field(..., min_length=6, max_length=20)
    gender: Gender
    registration_number: str = Field(..., min_length=4, max_length=20)
    specialty: Optional[str] = None
    active: bool = True

    @validator('registration_number')
    def validate_registration(cls, v):
        if not v.isalnum():
            raise ValueError('Número de registro debe ser alfanumérico')
        return v.upper()

class DoctorCreate(DoctorBase):
    pass

class DoctorResponse(DoctorBase):
    id: int
    full_name: str

    class Config:
        orm_mode = True

class BiochemistBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    professional_license: str = Field(..., min_length=4, max_length=20)
    report_display_name: Optional[str] = None
    active: bool = True

    @validator('professional_license')
    def validate_license(cls, v):
        if not v.isalnum():
            raise ValueError('Número de licencia debe ser alfanumérico')
        return v.upper()

class BiochemistCreate(BiochemistBase):
    pass

class BiochemistUpdate(BaseModel):
    report_display_name: Optional[str]
    active: Optional[bool]
    digital_signature: Optional[str]

class BiochemistResponse(BiochemistBase):
    id: int
    signature_date: Optional[date]
    has_scanned_signature: bool
    has_digital_signature: bool

    class Config:
        orm_mode = True

    @validator('has_scanned_signature', pre=True)
    def validate_scanned_signature(cls, v, values):
        return bool(values.get('scanned_signature'))

    @validator('has_digital_signature', pre=True)
    def validate_digital_signature(cls, v, values):
        return bool(values.get('digital_signature'))
