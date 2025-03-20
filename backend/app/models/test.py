from sqlalchemy import Column, String, Float, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class TestType(BaseModel):
    __tablename__ = "test_types"

    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    reference_range = Column(JSON)  # Store min/max values and units
    machine_interface = Column(String(50))  # Equipment interface identifier

class TestResult(BaseModel):
    __tablename__ = "test_results"

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    test_type_id = Column(Integer, ForeignKey("test_types.id"), nullable=False)
    value = Column(Float)
    unit = Column(String(20))
    is_abnormal = Column(Boolean, default=False)
    notes = Column(Text)
    analyzed_by = Column(String(100))
    validated = Column(Boolean, default=False)
    raw_data = Column(JSON)  # Store machine output

    # Relationships
    patient = relationship("Patient", backref="test_results")
    test_type = relationship("TestType", backref="results")
