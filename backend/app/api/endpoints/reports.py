from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
from ...db.session import get_db
from ...models.auth import Permission
from ...core.security import check_permission
from ...models.report import Report, TestResult, StatisticalReport
from ...services.report_generator import ReportGenerator
from ...schemas.reports import (
    ReportCreate,
    ReportResponse,
    TestResultCreate,
    TestResultResponse,
    StatisticalReportResponse
)

router = APIRouter()

@router.post("/reports/", response_model=ReportResponse)
async def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.MANAGE_RESULTS]))
):
    """Crea un nuevo reporte de laboratorio."""
    db_report = Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Obtiene un reporte específico."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return report

@router.post("/reports/{report_id}/results", response_model=TestResultResponse)
async def add_test_result(
    report_id: int,
    result: TestResultCreate,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.ENTER_RESULTS]))
):
    """Agrega un resultado a un reporte."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    db_result = TestResult(**result.dict(), report_id=report_id)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

@router.get("/reports/{report_id}/pdf")
async def get_report_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Genera y descarga el PDF de un reporte."""
    report_generator = ReportGenerator(db)
    try:
        pdf_content = report_generator.generate_patient_report(report_id)
        
        # Actualizar estado del reporte
        report = db.query(Report).filter(Report.id == report_id).first()
        report.status = "printed"
        db.commit()
        
        return Response(
            content=pdf_content.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{report_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando PDF: {str(e)}"
        )

@router.post("/reports/{report_id}/validate")
async def validate_report(
    report_id: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VALIDATE_RESULTS]))
):
    """Valida un reporte por un bioquímico."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    # Actualizar estado y fecha de validación
    report.status = "validated"
    for result in report.results:
        result.validated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Reporte validado exitosamente"}

@router.get("/statistics/daily", response_model=StatisticalReportResponse)
async def get_daily_statistics(
    date: date,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Genera reporte estadístico diario."""
    report_generator = ReportGenerator(db)
    return report_generator.generate_daily_report(
        datetime.combine(date, datetime.min.time()),
        _.id  # ID del usuario actual
    )

@router.get("/statistics/monthly", response_model=StatisticalReportResponse)
async def get_monthly_statistics(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Genera reporte estadístico mensual."""
    report_generator = ReportGenerator(db)
    return report_generator.generate_monthly_report(year, month, _.id)

@router.get("/statistics/custom", response_model=StatisticalReportResponse)
async def get_custom_statistics(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Genera reporte estadístico para un rango de fechas personalizado."""
    report_generator = ReportGenerator(db)
    return report_generator.generate_statistical_report(
        "custom",
        start_date,
        end_date,
        _.id
    )

@router.get("/reports/search")
async def search_reports(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(check_permission([Permission.VIEW_RESULTS]))
):
    """Busca reportes según varios criterios."""
    query = db.query(Report)
    
    if patient_id:
        query = query.filter(Report.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Report.doctor_id == doctor_id)
    if start_date:
        query = query.filter(Report.report_date >= start_date)
    if end_date:
        query = query.filter(Report.report_date <= end_date)
    if status:
        query = query.filter(Report.status == status)
    
    return query.all()
