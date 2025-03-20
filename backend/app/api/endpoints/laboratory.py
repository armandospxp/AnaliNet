from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...db.session import get_db
from ...models.auth import Permission
from ...core.security import check_permission
from ...models.laboratory import (
    SampleType, MeasurementMethod, MeasurementUnit,
    SampleState, SamplePreservation
)
from ...schemas.laboratory import (
    SampleTypeCreate, SampleTypeResponse,
    MeasurementMethodCreate, MeasurementMethodResponse,
    MeasurementUnitCreate, MeasurementUnitResponse,
    DeterminationMethodConfig, DeterminationUnitConfig
)
from ...models.test_types import Determination

router = APIRouter()

# Endpoints para Tipos de Muestra
@router.post("/samples/types/", response_model=SampleTypeResponse)
async def create_sample_type(
    sample_type: SampleTypeCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_TESTS]))
):
    """Crea un nuevo tipo de muestra."""
    if db.query(SampleType).filter(SampleType.code == sample_type.code).first():
        raise HTTPException(
            status_code=400,
            detail="Ya existe un tipo de muestra con ese código"
        )
    
    db_sample_type = SampleType(**sample_type.dict())
    db.add(db_sample_type)
    db.commit()
    db.refresh(db_sample_type)
    return db_sample_type

@router.get("/samples/types/", response_model=List[SampleTypeResponse])
async def list_sample_types(
    state: Optional[SampleState] = None,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Lista todos los tipos de muestra, opcionalmente filtrados por estado."""
    query = db.query(SampleType)
    if state:
        query = query.filter(SampleType.state == state)
    return query.all()

@router.get("/samples/types/{type_id}", response_model=SampleTypeResponse)
async def get_sample_type(
    type_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Obtiene un tipo de muestra específico."""
    sample_type = db.query(SampleType).filter(SampleType.id == type_id).first()
    if not sample_type:
        raise HTTPException(status_code=404, detail="Tipo de muestra no encontrado")
    return sample_type

# Endpoints para Métodos de Medición
@router.post("/methods/", response_model=MeasurementMethodResponse)
async def create_method(
    method: MeasurementMethodCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_TESTS]))
):
    """Crea un nuevo método de medición."""
    if db.query(MeasurementMethod).filter(MeasurementMethod.code == method.code).first():
        raise HTTPException(
            status_code=400,
            detail="Ya existe un método con ese código"
        )
    
    db_method = MeasurementMethod(**method.dict())
    db.add(db_method)
    db.commit()
    db.refresh(db_method)
    return db_method

@router.get("/methods/", response_model=List[MeasurementMethodResponse])
async def list_methods(
    equipment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Lista todos los métodos de medición, opcionalmente filtrados por tipo de equipo."""
    query = db.query(MeasurementMethod)
    if equipment_type:
        query = query.filter(MeasurementMethod.equipment_type == equipment_type)
    return query.all()

# Endpoints para Unidades de Medida
@router.post("/units/", response_model=MeasurementUnitResponse)
async def create_unit(
    unit: MeasurementUnitCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_TESTS]))
):
    """Crea una nueva unidad de medida."""
    if db.query(MeasurementUnit).filter(MeasurementUnit.code == unit.code).first():
        raise HTTPException(
            status_code=400,
            detail="Ya existe una unidad con ese código"
        )
    
    db_unit = MeasurementUnit(**unit.dict())
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

@router.get("/units/", response_model=List[MeasurementUnitResponse])
async def list_units(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Lista todas las unidades de medida, opcionalmente filtradas por categoría."""
    query = db.query(MeasurementUnit)
    if category:
        query = query.filter(MeasurementUnit.category == category)
    return query.all()

# Endpoints para Configuración de Determinaciones
@router.post("/determinations/{determination_id}/methods")
async def set_determination_method(
    determination_id: int,
    config: DeterminationMethodConfig,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_TESTS]))
):
    """Configura el método de medición para una determinación."""
    determination = db.query(Determination).get(determination_id)
    if not determination:
        raise HTTPException(status_code=404, detail="Determinación no encontrada")
    
    method = db.query(MeasurementMethod).get(config.method_id)
    if not method:
        raise HTTPException(status_code=404, detail="Método no encontrado")
    
    # Si es método por defecto, desactivar otros métodos por defecto
    if config.is_default:
        db.query(DeterminationMethodConfig).\
            filter_by(determination_id=determination_id, is_default=True).\
            update({"is_default": False})
    
    # Crear o actualizar configuración
    db_config = db.query(DeterminationMethodConfig).\
        filter_by(
            determination_id=determination_id,
            method_id=config.method_id
        ).first()
    
    if db_config:
        for key, value in config.dict().items():
            setattr(db_config, key, value)
    else:
        db_config = DeterminationMethodConfig(**config.dict())
        db.add(db_config)
    
    db.commit()
    return {"message": "Método configurado exitosamente"}

@router.post("/determinations/{determination_id}/units")
async def set_determination_unit(
    determination_id: int,
    config: DeterminationUnitConfig,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_TESTS]))
):
    """Configura la unidad de medida para una determinación."""
    determination = db.query(Determination).get(determination_id)
    if not determination:
        raise HTTPException(status_code=404, detail="Determinación no encontrada")
    
    unit = db.query(MeasurementUnit).get(config.unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    
    # Si es unidad por defecto, desactivar otras unidades por defecto
    if config.is_default:
        db.query(DeterminationUnitConfig).\
            filter_by(determination_id=determination_id, is_default=True).\
            update({"is_default": False})
    
    # Crear o actualizar configuración
    db_config = db.query(DeterminationUnitConfig).\
        filter_by(
            determination_id=determination_id,
            unit_id=config.unit_id
        ).first()
    
    if db_config:
        for key, value in config.dict().items():
            setattr(db_config, key, value)
    else:
        db_config = DeterminationUnitConfig(**config.dict())
        db.add(db_config)
    
    db.commit()
    return {"message": "Unidad configurada exitosamente"}

@router.get("/determinations/{determination_id}/methods")
async def get_determination_methods(
    determination_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Obtiene los métodos configurados para una determinación."""
    determination = db.query(Determination).get(determination_id)
    if not determination:
        raise HTTPException(status_code=404, detail="Determinación no encontrada")
    
    configs = db.query(DeterminationMethodConfig).\
        filter_by(determination_id=determination_id).all()
    
    return configs

@router.get("/determinations/{determination_id}/units")
async def get_determination_units(
    determination_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Obtiene las unidades configuradas para una determinación."""
    determination = db.query(Determination).get(determination_id)
    if not determination:
        raise HTTPException(status_code=404, detail="Determinación no encontrada")
    
    configs = db.query(DeterminationUnitConfig).\
        filter_by(determination_id=determination_id).all()
    
    return configs
