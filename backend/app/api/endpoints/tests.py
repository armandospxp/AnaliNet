from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...db.session import get_db
from ...schemas.test import TestType, TestTypeCreate, TestResult, TestResultCreate
from ...models.test import TestType as TestTypeModel, TestResult as TestResultModel
from ...services.anomaly_detection import detect_anomalies

router = APIRouter()

@router.post("/types/", response_model=TestType)
def create_test_type(test_type: TestTypeCreate, db: Session = Depends(get_db)):
    db_test_type = TestTypeModel(**test_type.model_dump())
    db.add(db_test_type)
    db.commit()
    db.refresh(db_test_type)
    return db_test_type

@router.get("/types/", response_model=List[TestType])
def list_test_types(db: Session = Depends(get_db)):
    return db.query(TestTypeModel).all()

@router.post("/results/", response_model=TestResult)
async def create_test_result(test_result: TestResultCreate, db: Session = Depends(get_db)):
    # Create test result
    db_test_result = TestResultModel(**test_result.model_dump())
    
    # Get test type for reference range
    test_type = db.query(TestTypeModel).filter(TestTypeModel.id == test_result.test_type_id).first()
    if not test_type:
        raise HTTPException(status_code=404, detail="Test type not found")
    
    # Perform anomaly detection
    is_abnormal = await detect_anomalies(
        value=test_result.value,
        reference_range=test_type.reference_range,
        test_type=test_type.code
    )
    db_test_result.is_abnormal = is_abnormal
    
    db.add(db_test_result)
    db.commit()
    db.refresh(db_test_result)
    return db_test_result

@router.get("/results/patient/{patient_id}", response_model=List[TestResult])
def get_patient_results(patient_id: int, db: Session = Depends(get_db)):
    results = db.query(TestResultModel).filter(
        TestResultModel.patient_id == patient_id
    ).all()
    return results

@router.put("/results/{result_id}/validate", response_model=TestResult)
def validate_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(TestResultModel).filter(TestResultModel.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Test result not found")
    
    result.validated = True
    db.commit()
    db.refresh(result)
    return result
