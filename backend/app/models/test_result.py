from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    patient_id = Column(String, index=True)
    test_code = Column(String, index=True)
    test_name = Column(String)
    result_value = Column(String)
    units = Column(String)
    reference_range = Column(String)
    flags = Column(String)  # H (High), L (Low), C (Critical), etc.
    status = Column(String)  # F (Final), P (Preliminary), etc.
    result_datetime = Column(DateTime, default=datetime.utcnow)
    raw_message = Column(Text)  # Original message for auditing
    
    equipment = relationship("Equipment", back_populates="test_results")
