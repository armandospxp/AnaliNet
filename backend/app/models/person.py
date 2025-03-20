from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from datetime import date, datetime
from .base import Base
from enum import Enum as PyEnum

class Gender(str, PyEnum):
    MALE = 'M'
    FEMALE = 'F'

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False)
    neighborhood = Column(String)  # barrio
    department = Column(String, nullable=False)  # departamento
    
    patients = relationship("Patient", back_populates="location")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    document_number = Column(String, unique=True, nullable=False, index=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"))
    
    location = relationship("Location", back_populates="patients")
    reports = relationship("Report", back_populates="patient")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    document_number = Column(String, unique=True, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    registration_number = Column(String, unique=True, nullable=False)  # número de registro
    specialty = Column(String)
    active = Column(Boolean, default=True)
    
    reports = relationship("Report", back_populates="doctor")

    @property
    def full_name(self):
        return f"Dr. {self.first_name} {self.last_name}"

class Biochemist(Base):
    __tablename__ = "biochemists"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    professional_license = Column(String, unique=True, nullable=False)  # nro_registro_profesional
    scanned_signature = Column(LargeBinary)  # firma_escaneada
    digital_signature = Column(String)  # firma_digital (hash/certificado)
    signature_date = Column(Date)  # fecha de registro de la firma
    report_display_name = Column(String)  # nombre a mostrar en reportes
    active = Column(Boolean, default=True)
    
    validated_reports = relationship("Report", back_populates="validator")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_report_signature(self):
        """Retorna la información de firma para reportes."""
        return {
            "name": self.report_display_name or self.full_name,
            "license": self.professional_license,
            "signature": self.scanned_signature
        }

    def validate_report(self, report, db_session):
        """Valida un reporte usando la firma digital."""
        from ..models.report import Report
        if isinstance(report, int):
            report = db_session.query(Report).get(report)
        
        if not report:
            raise ValueError("Reporte no encontrado")
        
        if not self.active:
            raise ValueError("Bioquímico inactivo no puede validar reportes")
        
        report.validator_id = self.id
        report.validation_date = datetime.utcnow()
        report.status = "validated"
        
        # Aquí se podría agregar lógica adicional de firma digital
        
        db_session.commit()
        return report
