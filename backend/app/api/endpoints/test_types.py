from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Union, Dict
from ...db.session import get_db
from ...models.auth import Permission
from ...core.security import check_permission
from ...models.test_types import (
    AnalysisType, Determination, ReferenceRange,
    CategoricalValue, AlertLevel, ResultType, Gender
)
from ...schemas.test_types import (
    AnalysisTypeCreate, AnalysisTypeResponse, AnalysisTypeUpdate,
    DeterminationCreate, DeterminationResponse, DeterminationUpdate,
    ResultEvaluation
)
from ...services.lipid_evaluator import LipidEvaluator

router = APIRouter()

def evaluate_result(value: float, ranges: ReferenceRange) -> AlertLevel:
    """Evalúa un resultado numérico y determina su nivel de alerta."""
    if value <= ranges.critical_low or value >= ranges.critical_high:
        return AlertLevel.CRITICAL
    elif value <= ranges.warning_low or value >= ranges.warning_high:
        return AlertLevel.WARNING
    return AlertLevel.NORMAL

@router.post("/analysis/", response_model=AnalysisTypeResponse)
async def create_analysis(
    analysis: AnalysisTypeCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.MANAGE_TESTS))
):
    """Crear un nuevo tipo de análisis."""
    # Verificar que las determinaciones existen
    determinations = db.query(Determination).filter(
        Determination.id.in_(analysis.determination_ids)
    ).all()
    
    if len(determinations) != len(analysis.determination_ids):
        raise HTTPException(
            status_code=400,
            detail="Una o más determinaciones no existen"
        )

    db_analysis = AnalysisType(**analysis.model_dump(exclude={'determination_ids'}))
    db_analysis.determinations = determinations
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

@router.get("/analysis/", response_model=List[AnalysisTypeResponse])
async def list_analysis(
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_RESULTS))
):
    """Listar todos los tipos de análisis."""
    return db.query(AnalysisType).all()

@router.get("/analysis/{analysis_id}", response_model=AnalysisTypeResponse)
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_RESULTS))
):
    """Obtener un tipo de análisis específico."""
    analysis = db.query(AnalysisType).filter(AnalysisType.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return analysis

@router.put("/analysis/{analysis_id}", response_model=AnalysisTypeResponse)
async def update_analysis(
    analysis_id: int,
    analysis_update: AnalysisTypeUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.MANAGE_TESTS))
):
    """Actualizar un tipo de análisis."""
    db_analysis = db.query(AnalysisType).filter(AnalysisType.id == analysis_id).first()
    if not db_analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    update_data = analysis_update.model_dump(exclude_unset=True)
    
    if "determination_ids" in update_data:
        determinations = db.query(Determination).filter(
            Determination.id.in_(update_data["determination_ids"])
        ).all()
        if len(determinations) != len(update_data["determination_ids"]):
            raise HTTPException(
                status_code=400,
                detail="Una o más determinaciones no existen"
            )
        db_analysis.determinations = determinations
        del update_data["determination_ids"]

    for field, value in update_data.items():
        setattr(db_analysis, field, value)

    db.commit()
    db.refresh(db_analysis)
    return db_analysis

@router.post("/determinations/", response_model=DeterminationResponse)
async def create_determination(
    determination: DeterminationCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.MANAGE_TESTS))
):
    """Crear una nueva determinación."""
    db_determination = Determination(**determination.model_dump(
        exclude={'reference_ranges', 'categorical_values'}
    ))
    
    if determination.reference_ranges and determination.result_type == ResultType.NUMERIC:
        for range_data in determination.reference_ranges:
            db_range = ReferenceRange(**range_data.model_dump())
            db_determination.reference_ranges.append(db_range)
    
    if determination.categorical_values and determination.result_type == ResultType.CATEGORICAL:
        for value_data in determination.categorical_values:
            db_value = CategoricalValue(**value_data.model_dump())
            db_determination.categorical_values.append(db_value)

    db.add(db_determination)
    db.commit()
    db.refresh(db_determination)
    return db_determination

@router.get("/determinations/", response_model=List[DeterminationResponse])
async def list_determinations(
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_RESULTS))
):
    """Listar todas las determinaciones."""
    return db.query(Determination).all()

@router.get("/determinations/{determination_id}", response_model=DeterminationResponse)
async def get_determination(
    determination_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_RESULTS))
):
    """Obtener una determinación específica."""
    determination = db.query(Determination).filter(
        Determination.id == determination_id
    ).first()
    if not determination:
        raise HTTPException(status_code=404, detail="Determinación no encontrada")
    return determination

@router.put("/determinations/{determination_id}", response_model=DeterminationResponse)
async def update_determination(
    determination_id: int,
    determination_update: DeterminationUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.MANAGE_TESTS))
):
    """Actualizar una determinación."""
    db_determination = db.query(Determination).filter(
        Determination.id == determination_id
    ).first()
    if not db_determination:
        raise HTTPException(status_code=404, detail="Determinación no encontrada")

    update_data = determination_update.model_dump(exclude_unset=True)
    
    # Actualizar rangos de referencia
    if "reference_ranges" in update_data:
        db.query(ReferenceRange).filter(
            ReferenceRange.determination_id == determination_id
        ).delete()
        
        for range_data in update_data["reference_ranges"]:
            db_range = ReferenceRange(**range_data.model_dump())
            db_determination.reference_ranges.append(db_range)
        del update_data["reference_ranges"]
    
    # Actualizar valores categóricos
    if "categorical_values" in update_data:
        db.query(CategoricalValue).filter(
            CategoricalValue.determination_id == determination_id
        ).delete()
        
        for value_data in update_data["categorical_values"]:
            db_value = CategoricalValue(**value_data.model_dump())
            db_determination.categorical_values.append(db_value)
        del update_data["categorical_values"]

    for field, value in update_data.items():
        setattr(db_determination, field, value)

    db.commit()
    db.refresh(db_determination)
    return db_determination

@router.post("/determinations/{determination_id}/evaluate", response_model=ResultEvaluation)
async def evaluate_determination_result(
    determination_id: int,
    value: Union[float, str],
    patient_age: int,
    patient_gender: Gender,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_RESULTS))
):
    """Evaluar un resultado y determinar su nivel de alerta."""
    determination = db.query(Determination).filter(
        Determination.id == determination_id
    ).first()
    if not determination:
        raise HTTPException(status_code=404, detail="Determinación no encontrada")

    if determination.result_type == ResultType.NUMERIC:
        # Buscar el rango de referencia apropiado para la edad y género
        reference_range = db.query(ReferenceRange).filter(
            ReferenceRange.determination_id == determination_id,
            ReferenceRange.gender.in_([patient_gender, Gender.ANY]),
            ReferenceRange.min_age <= patient_age,
            ReferenceRange.max_age >= patient_age
        ).first()
        
        if not reference_range:
            raise HTTPException(
                status_code=404,
                detail="No se encontró rango de referencia para esta edad y género"
            )
        
        try:
            numeric_value = float(value)
            alert_level = evaluate_result(numeric_value, reference_range)
            
            return ResultEvaluation(
                value=numeric_value,
                alert_level=alert_level,
                reference_range={
                    "min": reference_range.min_value,
                    "max": reference_range.max_value,
                    "warning_low": reference_range.warning_low,
                    "warning_high": reference_range.warning_high,
                    "critical_low": reference_range.critical_low,
                    "critical_high": reference_range.critical_high
                }
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="El valor debe ser numérico para este tipo de determinación"
            )
    
    elif determination.result_type == ResultType.CATEGORICAL:
        # Buscar el valor categórico y su nivel de alerta
        categorical_value = db.query(CategoricalValue).filter(
            CategoricalValue.determination_id == determination_id,
            CategoricalValue.value == value
        ).first()
        
        if not categorical_value:
            raise HTTPException(
                status_code=400,
                detail="Valor no válido para esta determinación"
            )
        
        return ResultEvaluation(
            value=value,
            alert_level=categorical_value.alert_level,
            categorical_value={
                "value": categorical_value.value,
                "alert_level": categorical_value.alert_level.value
            }
        )
    
    else:  # ResultType.TEXT
        return ResultEvaluation(
            value=str(value),
            alert_level=AlertLevel.NORMAL
        )

@router.post("/analysis/lipid-profile/evaluate")
async def evaluate_lipid_profile(
    total_cholesterol: float,
    hdl: float,
    ldl: float,
    triglycerides: float,
    patient_age: int,
    patient_gender: str,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_RESULTS))
):
    """
    Evalúa un perfil lipídico completo y proporciona análisis de riesgo cardiovascular.
    
    Parameters:
    - total_cholesterol: Colesterol total en mg/dL
    - hdl: HDL (colesterol bueno) en mg/dL
    - ldl: LDL (colesterol malo) en mg/dL
    - triglycerides: Triglicéridos en mg/dL
    - patient_age: Edad del paciente en años
    - patient_gender: Género del paciente (M/F)
    
    Returns:
    - Evaluación completa del perfil lipídico con niveles de riesgo y recomendaciones
    """
    # Validar género
    if patient_gender not in ['M', 'F']:
        raise HTTPException(
            status_code=400,
            detail="Género debe ser 'M' o 'F'"
        )
    
    # Validar valores numéricos
    if any(value <= 0 for value in [total_cholesterol, hdl, ldl, triglycerides]):
        raise HTTPException(
            status_code=400,
            detail="Todos los valores deben ser positivos"
        )
    
    # Obtener análisis de perfil lipídico
    lipid_profile = db.query(AnalysisType).filter(
        AnalysisType.code == "LIPID_PROF"
    ).first()
    
    if not lipid_profile:
        raise HTTPException(
            status_code=404,
            detail="Perfil lipídico no encontrado en la base de datos"
        )
    
    # Evaluar cada componente individualmente
    evaluator = LipidEvaluator()
    
    # Obtener evaluación de riesgo cardiovascular
    risk_evaluation = evaluator.evaluate_cardiovascular_risk(
        total_cholesterol=total_cholesterol,
        hdl=hdl,
        ldl=ldl,
        triglycerides=triglycerides,
        age=patient_age,
        gender=patient_gender
    )
    
    # Obtener valores de referencia
    reference_values = evaluator.get_reference_values(
        age=patient_age,
        gender=patient_gender
    )
    
    # Preparar respuesta detallada
    response = {
        "analysis_info": {
            "name": lipid_profile.name,
            "code": lipid_profile.code,
            "category": lipid_profile.category
        },
        "results": {
            "total_cholesterol": {
                "value": total_cholesterol,
                "unit": "mg/dL",
                "alert_level": AlertLevel.CRITICAL if total_cholesterol >= 240
                    else AlertLevel.WARNING if total_cholesterol >= 200
                    else AlertLevel.NORMAL
            },
            "hdl": {
                "value": hdl,
                "unit": "mg/dL",
                "alert_level": AlertLevel.CRITICAL if (
                    (patient_gender == 'M' and hdl < 30) or
                    (patient_gender == 'F' and hdl < 40)
                ) else AlertLevel.WARNING if (
                    (patient_gender == 'M' and hdl < 40) or
                    (patient_gender == 'F' and hdl < 50)
                ) else AlertLevel.NORMAL
            },
            "ldl": {
                "value": ldl,
                "unit": "mg/dL",
                "alert_level": AlertLevel.CRITICAL if ldl >= 160
                    else AlertLevel.WARNING if ldl >= 130
                    else AlertLevel.NORMAL
            },
            "triglycerides": {
                "value": triglycerides,
                "unit": "mg/dL",
                "alert_level": AlertLevel.CRITICAL if triglycerides >= 500
                    else AlertLevel.WARNING if triglycerides >= 150
                    else AlertLevel.NORMAL
            },
            "atherogenic_index": {
                "value": risk_evaluation["atherogenic_index"],
                "unit": "ratio",
                "alert_level": AlertLevel.CRITICAL if (
                    (patient_gender == 'M' and risk_evaluation["atherogenic_index"] > 5.0) or
                    (patient_gender == 'F' and risk_evaluation["atherogenic_index"] > 4.5)
                ) else AlertLevel.WARNING if (
                    (patient_gender == 'M' and risk_evaluation["atherogenic_index"] > 4.5) or
                    (patient_gender == 'F' and risk_evaluation["atherogenic_index"] > 4.0)
                ) else AlertLevel.NORMAL
            }
        },
        "risk_assessment": {
            "overall_risk_level": risk_evaluation["risk_level"],
            "risk_factors": risk_evaluation["risk_factors"],
            "age_risk": risk_evaluation["age_risk"],
            "recommendations": risk_evaluation["recommendations"]
        },
        "reference_values": reference_values
    }
    
    return response
