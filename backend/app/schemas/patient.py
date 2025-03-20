from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    document_id: str
    birth_date: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
