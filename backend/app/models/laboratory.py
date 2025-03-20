from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from .base import Base
from enum import Enum as PyEnum

class SamplePreservation(str, PyEnum):
    ROOM_TEMP = 'room_temperature'
    REFRIGERATED = 'refrigerated'
    FROZEN = 'frozen'

class SampleState(str, PyEnum):
    LIQUID = 'liquid'
    SOLID = 'solid'
    SEMI_SOLID = 'semi_solid'

class SampleType(Base):
    __tablename__ = "sample_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    state = Column(Enum(SampleState), nullable=False)
    preservation = Column(Enum(SamplePreservation), nullable=False)
    max_storage_time = Column(Integer)  # en horas
    storage_instructions = Column(String)
    container_type = Column(String)  # tipo de tubo o recipiente
    minimum_volume = Column(Float)  # en ml
    
    determinations = relationship("Determination", back_populates="sample_type")

    @classmethod
    def create_initial_types(cls, db_session):
        """Crea los tipos de muestra iniciales."""
        initial_types = [
            {
                "name": "Sangre Total EDTA",
                "code": "BLOOD_EDTA",
                "description": "Sangre con anticoagulante EDTA",
                "state": SampleState.LIQUID,
                "preservation": SamplePreservation.ROOM_TEMP,
                "max_storage_time": 24,
                "storage_instructions": "Mantener a temperatura ambiente. No refrigerar.",
                "container_type": "Tubo tapa lila",
                "minimum_volume": 3.0
            },
            {
                "name": "Sangre Total Citrato",
                "code": "BLOOD_CITRATE",
                "description": "Sangre con citrato de sodio",
                "state": SampleState.LIQUID,
                "preservation": SamplePreservation.ROOM_TEMP,
                "max_storage_time": 4,
                "storage_instructions": "Procesar dentro de las 4 horas",
                "container_type": "Tubo tapa celeste",
                "minimum_volume": 2.7
            },
            {
                "name": "Suero",
                "code": "SERUM",
                "description": "Suero obtenido tras coagulación",
                "state": SampleState.LIQUID,
                "preservation": SamplePreservation.REFRIGERATED,
                "max_storage_time": 48,
                "storage_instructions": "Refrigerar a 2-8°C",
                "container_type": "Tubo tapa roja",
                "minimum_volume": 5.0
            },
            {
                "name": "Orina 24h",
                "code": "URINE_24H",
                "description": "Orina de 24 horas",
                "state": SampleState.LIQUID,
                "preservation": SamplePreservation.REFRIGERATED,
                "max_storage_time": 24,
                "storage_instructions": "Refrigerar durante la recolección",
                "container_type": "Recipiente estéril 2L",
                "minimum_volume": 1000.0
            },
            {
                "name": "Orina Simple",
                "code": "URINE_SIMPLE",
                "description": "Orina espontánea",
                "state": SampleState.LIQUID,
                "preservation": SamplePreservation.ROOM_TEMP,
                "max_storage_time": 2,
                "storage_instructions": "Procesar dentro de 2 horas",
                "container_type": "Recipiente estéril",
                "minimum_volume": 50.0
            },
            {
                "name": "Materia Fecal",
                "code": "STOOL",
                "description": "Muestra de heces",
                "state": SampleState.SEMI_SOLID,
                "preservation": SamplePreservation.ROOM_TEMP,
                "max_storage_time": 2,
                "storage_instructions": "Procesar inmediatamente",
                "container_type": "Recipiente estéril",
                "minimum_volume": 5.0
            },
            {
                "name": "Líquido Cefalorraquídeo",
                "code": "CSF",
                "description": "Líquido cefalorraquídeo",
                "state": SampleState.LIQUID,
                "preservation": SamplePreservation.ROOM_TEMP,
                "max_storage_time": 1,
                "storage_instructions": "Procesar inmediatamente",
                "container_type": "Tubo estéril",
                "minimum_volume": 1.0
            }
        ]
        
        for type_data in initial_types:
            if not db_session.query(cls).filter_by(code=type_data["code"]).first():
                db_session.add(cls(**type_data))
        
        db_session.commit()

class MeasurementMethod(Base):
    __tablename__ = "measurement_methods"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    principle = Column(String)  # principio del método
    equipment_type = Column(String)  # tipo de equipo que usa este método
    
    determinations = relationship("Determination", back_populates="method")

    @classmethod
    def create_initial_methods(cls, db_session):
        """Crea los métodos de medición iniciales."""
        initial_methods = [
            {
                "name": "Espectrofotometría",
                "code": "SPECTROPHOTOMETRY",
                "description": "Medición de la absorción de luz",
                "principle": "Medición de la absorción de luz a longitudes de onda específicas",
                "equipment_type": "Espectrofotómetro"
            },
            {
                "name": "Impedancia Eléctrica",
                "code": "IMPEDANCE",
                "description": "Medición por impedancia eléctrica",
                "principle": "Detección de cambios en la conductividad eléctrica",
                "equipment_type": "Contador hematológico"
            },
            {
                "name": "Citometría de Flujo",
                "code": "FLOW_CYTOMETRY",
                "description": "Análisis por citometría de flujo",
                "principle": "Análisis de características físicas y químicas de células",
                "equipment_type": "Citómetro de flujo"
            },
            {
                "name": "Inmunoturbidimetría",
                "code": "IMMUNOTURBIDIMETRY",
                "description": "Medición por inmunoturbidimetría",
                "principle": "Medición de la turbidez producida por complejos antígeno-anticuerpo",
                "equipment_type": "Autoanalizador bioquímico"
            },
            {
                "name": "Electroquimioluminiscencia",
                "code": "ECLIA",
                "description": "Electroquimioluminiscencia",
                "principle": "Medición de la emisión de luz en reacciones electroquímicas",
                "equipment_type": "Analizador de inmunología"
            },
            {
                "name": "Microscopía",
                "code": "MICROSCOPY",
                "description": "Observación microscópica",
                "principle": "Observación directa con microscopio",
                "equipment_type": "Microscopio"
            }
        ]
        
        for method_data in initial_methods:
            if not db_session.query(cls).filter_by(code=method_data["code"]).first():
                db_session.add(cls(**method_data))
        
        db_session.commit()

class MeasurementUnit(Base):
    __tablename__ = "measurement_units"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String)
    category = Column(String)  # concentración, volumen, etc.
    conversion_factor = Column(Float, nullable=True)  # factor para conversión SI
    si_unit = Column(String, nullable=True)  # unidad SI correspondiente
    
    determinations = relationship("Determination", back_populates="unit")

    @classmethod
    def create_initial_units(cls, db_session):
        """Crea las unidades de medida iniciales."""
        initial_units = [
            {
                "name": "gramos por decilitro",
                "code": "g/dL",
                "description": "Concentración en gramos por decilitro",
                "category": "concentración",
                "conversion_factor": 10,
                "si_unit": "g/L"
            },
            {
                "name": "porcentaje",
                "code": "%",
                "description": "Porcentaje",
                "category": "ratio",
                "conversion_factor": 0.01,
                "si_unit": "ratio"
            },
            {
                "name": "femtolitros",
                "code": "fL",
                "description": "Volumen celular en femtolitros",
                "category": "volumen",
                "conversion_factor": 1e-15,
                "si_unit": "L"
            },
            {
                "name": "picogramos",
                "code": "pg",
                "description": "Masa en picogramos",
                "category": "masa",
                "conversion_factor": 1e-12,
                "si_unit": "g"
            },
            {
                "name": "células por milímetro cúbico",
                "code": "/mm³",
                "description": "Conteo celular por mm³",
                "category": "concentración",
                "conversion_factor": 1e6,
                "si_unit": "/L"
            },
            {
                "name": "miligramos por decilitro",
                "code": "mg/dL",
                "description": "Concentración en mg/dL",
                "category": "concentración",
                "conversion_factor": 0.01,
                "si_unit": "g/L"
            },
            {
                "name": "unidades internacionales por litro",
                "code": "UI/L",
                "description": "Actividad enzimática",
                "category": "actividad",
                "conversion_factor": 1,
                "si_unit": "UI/L"
            }
        ]
        
        for unit_data in initial_units:
            if not db_session.query(cls).filter_by(code=unit_data["code"]).first():
                db_session.add(cls(**unit_data))
        
        db_session.commit()
