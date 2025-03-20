from sqlalchemy.orm import Session
from ...models.test_types import (
    AnalysisType, Determination, ReferenceRange,
    ResultType, Gender
)

def create_lipid_profile(db: Session):
    # 1. Colesterol Total
    cholesterol = Determination(
        code="CHOL_TOTAL",
        name="Colesterol Total",
        description="Medición de colesterol total en sangre",
        unit="mg/dL",
        result_type=ResultType.NUMERIC,
        decimal_places=0
    )
    
    cholesterol.reference_ranges = [
        ReferenceRange(
            gender=Gender.ANY,
            min_age=0,
            max_age=120,
            min_value=150,
            max_value=200,
            warning_low=130,
            warning_high=200,
            critical_low=100,
            critical_high=240
        )
    ]
    
    # 2. HDL Colesterol
    hdl = Determination(
        code="HDL_CHOL",
        name="HDL Colesterol",
        description="Lipoproteínas de alta densidad",
        unit="mg/dL",
        result_type=ResultType.NUMERIC,
        decimal_places=0
    )
    
    hdl.reference_ranges = [
        ReferenceRange(
            gender=Gender.MALE,
            min_age=0,
            max_age=120,
            min_value=40,
            max_value=60,
            warning_low=35,
            warning_high=60,
            critical_low=30,
            critical_high=70
        ),
        ReferenceRange(
            gender=Gender.FEMALE,
            min_age=0,
            max_age=120,
            min_value=50,
            max_value=70,
            warning_low=45,
            warning_high=70,
            critical_low=40,
            critical_high=80
        )
    ]
    
    # 3. LDL Colesterol
    ldl = Determination(
        code="LDL_CHOL",
        name="LDL Colesterol",
        description="Lipoproteínas de baja densidad",
        unit="mg/dL",
        result_type=ResultType.NUMERIC,
        decimal_places=0
    )
    
    ldl.reference_ranges = [
        ReferenceRange(
            gender=Gender.ANY,
            min_age=0,
            max_age=120,
            min_value=0,
            max_value=100,
            warning_low=0,
            warning_high=130,
            critical_low=0,
            critical_high=160
        )
    ]
    
    # 4. Triglicéridos
    triglycerides = Determination(
        code="TRIGLYC",
        name="Triglicéridos",
        description="Medición de triglicéridos en sangre",
        unit="mg/dL",
        result_type=ResultType.NUMERIC,
        decimal_places=0
    )
    
    triglycerides.reference_ranges = [
        ReferenceRange(
            gender=Gender.ANY,
            min_age=0,
            max_age=120,
            min_value=0,
            max_value=150,
            warning_low=0,
            warning_high=150,
            critical_low=0,
            critical_high=200
        )
    ]
    
    # 5. Índice Aterogénico (Colesterol Total/HDL)
    atherogenic_index = Determination(
        code="ATHER_INDEX",
        name="Índice Aterogénico",
        description="Relación Colesterol Total/HDL",
        unit="ratio",
        result_type=ResultType.NUMERIC,
        decimal_places=1
    )
    
    atherogenic_index.reference_ranges = [
        ReferenceRange(
            gender=Gender.MALE,
            min_age=0,
            max_age=120,
            min_value=0,
            max_value=4.5,
            warning_low=0,
            warning_high=4.5,
            critical_low=0,
            critical_high=5.0
        ),
        ReferenceRange(
            gender=Gender.FEMALE,
            min_age=0,
            max_age=120,
            min_value=0,
            max_value=4.0,
            warning_low=0,
            warning_high=4.0,
            critical_low=0,
            critical_high=4.5
        )
    ]
    
    # Agregar todas las determinaciones a la base de datos
    determinations = [cholesterol, hdl, ldl, triglycerides, atherogenic_index]
    for det in determinations:
        db.add(det)
    db.commit()
    
    # Crear el análisis de Perfil Lipídico
    lipid_profile = AnalysisType(
        code="LIPID_PROF",
        name="Perfil Lipídico",
        description="Evaluación completa del metabolismo de lípidos",
        category="Bioquímica",
        sample_type="Sangre",
        instructions=(
            "Ayuno de 12-14 horas\n"
            "No consumir alcohol 24h antes\n"
            "Evitar cambios en la dieta habitual 3 días antes"
        )
    )
    
    # Asociar las determinaciones al perfil lipídico
    lipid_profile.determinations = determinations
    
    db.add(lipid_profile)
    db.commit()
    
    return lipid_profile
