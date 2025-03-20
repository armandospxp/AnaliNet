from sqlalchemy import Column, String, Date
from .base import BaseModel

class Patient(BaseModel):
    __tablename__ = "patients"

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    document_id = Column(String(20), unique=True, nullable=False)
    birth_date = Column(Date)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(200))
