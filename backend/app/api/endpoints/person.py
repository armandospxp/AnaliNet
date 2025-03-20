from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from ...db.session import get_db
from ...models.auth import Permission
from ...core.security import check_permission
from ...models.person import Patient, Doctor, Biochemist, Location
from ...schemas.person import (
    LocationCreate, LocationResponse,
    PatientCreate, PatientResponse,
    DoctorCreate, DoctorResponse,
    BiochemistCreate, BiochemistUpdate, BiochemistResponse
)

router = APIRouter()

# Endpoints para Ubicaciones
@router.post("/locations/", response_model=LocationResponse)
async def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_PATIENTS]))
):
    db_location = Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

@router.get("/locations/", response_model=List[LocationResponse])
async def list_locations(
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_PATIENTS]))
):
    return db.query(Location).all()

# Endpoints para Pacientes
@router.post("/patients/", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_PATIENTS]))
):
    # Verificar si ya existe un paciente con ese documento
    if db.query(Patient).filter(Patient.document_number == patient.document_number).first():
        raise HTTPException(
            status_code=400,
            detail="Ya existe un paciente con ese número de documento"
        )
    
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/patients/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_PATIENTS]))
):
    query = db.query(Patient)
    if search:
        query = query.filter(
            (Patient.first_name.ilike(f"%{search}%")) |
            (Patient.last_name.ilike(f"%{search}%")) |
            (Patient.document_number.ilike(f"%{search}%"))
        )
    return query.offset(skip).limit(limit).all()

@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_PATIENTS]))
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return patient

# Endpoints para Médicos
@router.post("/doctors/", response_model=DoctorResponse)
async def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_DOCTORS]))
):
    # Verificar documentos y registro únicos
    if db.query(Doctor).filter(Doctor.document_number == doctor.document_number).first():
        raise HTTPException(
            status_code=400,
            detail="Ya existe un médico con ese número de documento"
        )
    if db.query(Doctor).filter(Doctor.registration_number == doctor.registration_number).first():
        raise HTTPException(
            status_code=400,
            detail="Ya existe un médico con ese número de registro"
        )
    
    db_doctor = Doctor(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

@router.get("/doctors/", response_model=List[DoctorResponse])
async def list_doctors(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_DOCTORS]))
):
    query = db.query(Doctor)
    if active_only:
        query = query.filter(Doctor.active == True)
    return query.offset(skip).limit(limit).all()

# Endpoints para Bioquímicos
@router.post("/biochemists/", response_model=BiochemistResponse)
async def create_biochemist(
    biochemist: BiochemistCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_BIOCHEMISTS]))
):
    # Verificar licencia única
    if db.query(Biochemist).filter(
        Biochemist.professional_license == biochemist.professional_license
    ).first():
        raise HTTPException(
            status_code=400,
            detail="Ya existe un bioquímico con ese número de licencia"
        )
    
    db_biochemist = Biochemist(**biochemist.dict())
    db.add(db_biochemist)
    db.commit()
    db.refresh(db_biochemist)
    return db_biochemist

@router.post("/biochemists/{biochemist_id}/signature")
async def upload_signature(
    biochemist_id: int,
    signature_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_BIOCHEMISTS]))
):
    biochemist = db.query(Biochemist).filter(Biochemist.id == biochemist_id).first()
    if not biochemist:
        raise HTTPException(status_code=404, detail="Bioquímico no encontrado")
    
    # Leer y validar la firma
    contents = await signature_file.read()
    if len(contents) > 1024 * 1024:  # Max 1MB
        raise HTTPException(status_code=400, detail="Archivo de firma muy grande")
    
    biochemist.scanned_signature = contents
    biochemist.signature_date = date.today()
    db.commit()
    
    return {"message": "Firma actualizada exitosamente"}

@router.patch("/biochemists/{biochemist_id}", response_model=BiochemistResponse)
async def update_biochemist(
    biochemist_id: int,
    update_data: BiochemistUpdate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_BIOCHEMISTS]))
):
    biochemist = db.query(Biochemist).filter(Biochemist.id == biochemist_id).first()
    if not biochemist:
        raise HTTPException(status_code=404, detail="Bioquímico no encontrado")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(biochemist, field, value)
    
    db.commit()
    db.refresh(biochemist)
    return biochemist

@router.get("/biochemists/", response_model=List[BiochemistResponse])
async def list_biochemists(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_BIOCHEMISTS]))
):
    query = db.query(Biochemist)
    if active_only:
        query = query.filter(Biochemist.active == True)
    return query.offset(skip).limit(limit).all()

@router.get("/biochemists/{biochemist_id}", response_model=BiochemistResponse)
async def get_biochemist(
    biochemist_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_BIOCHEMISTS]))
):
    biochemist = db.query(Biochemist).filter(Biochemist.id == biochemist_id).first()
    if not biochemist:
        raise HTTPException(status_code=404, detail="Bioquímico no encontrado")
    return biochemist
