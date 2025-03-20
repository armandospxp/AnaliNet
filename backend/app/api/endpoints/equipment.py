from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ...db.session import get_db
from ...schemas.equipment import (
    EquipmentCategoryCreate, EquipmentCategoryResponse,
    EquipmentCreate, EquipmentResponse,
    EquipmentCommand, EquipmentCommandResponse
)
from ...schemas.test_result import TestResultFilter, TestResultResponse
from ...models.equipment import Equipment, EquipmentCategory
from ...models.test_result import TestResult
from ...models.auth import Permission
from ...services.equipment_interface import EquipmentManager
from ...services.result_handler import ResultHandler
from ...core.security import get_current_user, check_permission

router = APIRouter()
equipment_manager = EquipmentManager()

@router.post("/categories/", response_model=EquipmentCategoryResponse)
async def create_category(
    category: EquipmentCategoryCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.MANAGE_EQUIPMENT))
):
    db_category = EquipmentCategory(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories/", response_model=List[EquipmentCategoryResponse])
async def list_categories(
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_EQUIPMENT))
):
    return db.query(EquipmentCategory).all()

@router.post("/", response_model=EquipmentResponse)
async def create_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.MANAGE_EQUIPMENT))
):
    # Validate category exists
    category = db.query(EquipmentCategory).filter(
        EquipmentCategory.id == equipment.category_id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Validate protocol is supported by category
    if equipment.protocol not in category.supported_protocols:
        raise HTTPException(
            status_code=400,
            detail=f"Protocol {equipment.protocol} not supported by category {category.name}"
        )

    db_equipment = Equipment(**equipment.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

@router.get("/", response_model=List[EquipmentResponse])
async def list_equipment(
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_EQUIPMENT))
):
    return db.query(Equipment).all()

@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(
    equipment_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_EQUIPMENT))
):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.post("/{equipment_id}/connect")
async def connect_equipment(
    equipment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.CONNECT_EQUIPMENT))
):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    config = {
        "connection_type": equipment.connection_type,
        "protocol": equipment.protocol,
        "ip_address": equipment.ip_address,
        "port": equipment.port,
        "com_port": equipment.com_port,
        "baud_rate": equipment.baud_rate,
        "data_bits": equipment.data_bits,
        "parity": equipment.parity,
        "stop_bits": equipment.stop_bits
    }

    try:
        # Conectar el equipo
        await equipment_manager.connect_equipment(equipment_id, config)
        
        # Iniciar el manejador de resultados
        result_handler = ResultHandler(db, equipment_manager)
        background_tasks.add_task(result_handler.start_listening, equipment_id)
        
        return {"message": f"Successfully connected to equipment {equipment_id} and started result listening"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{equipment_id}/disconnect")
async def disconnect_equipment(
    equipment_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.CONNECT_EQUIPMENT))
):
    try:
        # Detener el manejador de resultados
        result_handler = ResultHandler(db, equipment_manager)
        background_tasks.add_task(result_handler.stop_listening, equipment_id)
        
        # Desconectar el equipo
        await equipment_manager.disconnect_equipment(equipment_id)
        return {"message": f"Successfully disconnected equipment {equipment_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{equipment_id}/command", response_model=EquipmentCommandResponse)
async def send_command(
    equipment_id: int,
    command: EquipmentCommand,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.MANAGE_EQUIPMENT))
):
    try:
        response = await equipment_manager.send_command_to_equipment(
            equipment_id,
            command.command
        )
        return EquipmentCommandResponse(response=response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{equipment_id}/request-results")
async def request_equipment_results(
    equipment_id: int,
    patient_id: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.ENTER_RESULTS))
):
    """Solicita resultados a un equipo de forma activa (solo equipos bidireccionales)."""
    try:
        result_handler = ResultHandler(db, equipment_manager)
        success = await result_handler.request_results(equipment_id, patient_id)
        if success:
            return {"message": "Results request sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to request results")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{equipment_id}/results", response_model=List[TestResultResponse])
async def get_equipment_results(
    equipment_id: int,
    filter_params: TestResultFilter = Depends(),
    db: Session = Depends(get_db),
    _=Depends(check_permission(Permission.VIEW_RESULTS))
):
    """Obtiene los resultados almacenados de un equipo con filtros opcionales."""
    query = db.query(TestResult).filter(TestResult.equipment_id == equipment_id)

    if filter_params.patient_id:
        query = query.filter(TestResult.patient_id == filter_params.patient_id)
    if filter_params.test_code:
        query = query.filter(TestResult.test_code == filter_params.test_code)
    if filter_params.status:
        query = query.filter(TestResult.status == filter_params.status)
    if filter_params.start_date:
        query = query.filter(TestResult.result_datetime >= filter_params.start_date)
    if filter_params.end_date:
        query = query.filter(TestResult.result_datetime <= filter_params.end_date)

    results = query.order_by(TestResult.result_datetime.desc()).all()
    return results
