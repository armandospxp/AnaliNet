from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .base import Base

class AlertLevel(str, PyEnum):
    NORMAL = "normal"  # Verde
    WARNING = "warning"  # Amarillo
    CRITICAL = "critical"  # Rojo

class ResultType(str, PyEnum):
    NUMERIC = "numeric"  # Valores numéricos con rangos
    CATEGORICAL = "categorical"  # Valores predefinidos (ej: positivo/negativo)
    TEXT = "text"  # Texto libre para observaciones

class Gender(str, PyEnum):
    MALE = "M"
    FEMALE = "F"
    ANY = "A"

# Tabla de asociación entre análisis y determinaciones
analysis_determinations = Table(
    'analysis_determinations',
    Base.metadata,
    Column('analysis_id', Integer, ForeignKey('analysis_types.id')),
    Column('determination_id', Integer, ForeignKey('determinations.id'))
)

class AnalysisType(Base):
    __tablename__ = "analysis_types"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    category = Column(String)  # ej: Hematología, Bioquímica, etc.
    sample_type = Column(String)  # ej: Sangre, Orina, etc.
    instructions = Column(String)  # Instrucciones de toma de muestra
    
    determinations = relationship(
        "Determination",
        secondary=analysis_determinations,
        back_populates="analysis_types"
    )

class Determination(Base):
    __tablename__ = "determinations"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    unit = Column(String)  # ej: mg/dL, g/L, etc.
    result_type = Column(Enum(ResultType))
    decimal_places = Column(Integer, default=2)  # Para resultados numéricos
    
    analysis_types = relationship(
        "AnalysisType",
        secondary=analysis_determinations,
        back_populates="determinations"
    )
    reference_ranges = relationship("ReferenceRange", back_populates="determination")
    categorical_values = relationship("CategoricalValue", back_populates="determination")

class ReferenceRange(Base):
    __tablename__ = "reference_ranges"

    id = Column(Integer, primary_key=True)
    determination_id = Column(Integer, ForeignKey("determinations.id"))
    gender = Column(Enum(Gender))
    min_age = Column(Integer)  # Edad mínima en años
    max_age = Column(Integer)  # Edad máxima en años
    min_value = Column(Float)
    max_value = Column(Float)
    warning_low = Column(Float)  # Valor para alerta amarilla inferior
    warning_high = Column(Float)  # Valor para alerta amarilla superior
    critical_low = Column(Float)  # Valor para alerta roja inferior
    critical_high = Column(Float)  # Valor para alerta roja superior
    
    determination = relationship("Determination", back_populates="reference_ranges")

class CategoricalValue(Base):
    __tablename__ = "categorical_values"

    id = Column(Integer, primary_key=True)
    determination_id = Column(Integer, ForeignKey("determinations.id"))
    value = Column(String)  # ej: "Positivo", "Negativo"
    alert_level = Column(Enum(AlertLevel))  # Nivel de alerta para este valor
    is_default = Column(Boolean, default=False)
    
    determination = relationship("Determination", back_populates="categorical_values")
