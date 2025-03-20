from typing import List, Dict, Any
from datetime import datetime, timedelta
from xhtml2pdf import pisa
from io import BytesIO
from jinja2 import Template
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.report import Report, TestResult, ReportTemplate, StatisticalReport
from ..models.test_types import AnalysisType, AlertLevel

class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.template = self.db.query(ReportTemplate).filter_by(name="default").first()
    
    def _generate_pdf(self, html_content: str) -> BytesIO:
        """Convierte HTML a PDF usando xhtml2pdf."""
        result = BytesIO()
        pdf = pisa.pisaDocument(
            BytesIO(html_content.encode("UTF-8")),
            result,
            encoding='UTF-8'
        )
        if pdf.err:
            raise Exception('Error generando PDF')
        return result

    def _group_results_by_category(self, results: List[TestResult]) -> Dict[str, List[TestResult]]:
        """Agrupa los resultados por categoría de análisis."""
        grouped = {}
        for result in results:
            category = result.analysis.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(result)
        return grouped

    def generate_patient_report(self, report_id: int) -> BytesIO:
        """Genera el reporte PDF de resultados para un paciente."""
        report = self.db.query(Report).filter_by(id=report_id).first()
        if not report:
            raise Exception("Reporte no encontrado")

        # Obtener todos los resultados
        results = self.db.query(TestResult).filter_by(report_id=report_id).all()
        grouped_results = self._group_results_by_category(results)

        # Preparar datos para el template
        context = {
            "lab_name": "Laboratorio Clínico",
            "lab_address": "Dirección del Laboratorio",
            "lab_phone": "Teléfono del Laboratorio",
            "patient_name": report.patient.full_name,
            "patient_document": report.patient.document_number,
            "patient_birth_date": report.patient.birth_date.strftime("%d/%m/%Y"),
            "patient_gender": "Masculino" if report.patient.gender == 'M' else "Femenino",
            "doctor_name": report.doctor.full_name if report.doctor else "",
            "admission_number": report.admission_number,
            "report_date": report.report_date.strftime("%d/%m/%Y %H:%M"),
            "technician_name": report.technician.full_name if report.technician else "",
            "validator_name": report.validator.full_name if report.validator else "",
            "grouped_results": grouped_results
        }

        # Generar HTML
        html_content = f"""
        <html>
        <head>
            <style>
                {self.template.css_styles}
            </style>
        </head>
        <body>
            <div id="header_content">
                {Template(self.template.header_html).render(**context)}
            </div>
            
            <div class="content">
                {% for category, results in grouped_results.items() %}
                <div class="category-section">
                    <h2>{{category}}</h2>
                    <table class="result-table">
                        <thead>
                            <tr>
                                <th>Determinación</th>
                                <th>Resultado</th>
                                <th>Unidad</th>
                                <th>Valores de Referencia</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for result in results %}
                            <tr class="result-{{result.alert_level}}">
                                <td>{{result.determination.name}}</td>
                                <td>{{result.value}}</td>
                                <td>{{result.unit}}</td>
                                <td>{{result.reference_range}}</td>
                            </tr>
                            {% if result.observation %}
                            <tr>
                                <td colspan="4" class="observation">
                                    {{result.observation}}
                                </td>
                            </tr>
                            {% endif %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endfor %}
            </div>
            
            <div id="footer_content">
                {Template(self.template.footer_html).render(**context)}
            </div>
        </body>
        </html>
        """
        
        return self._generate_pdf(Template(html_content).render(**context))

    def generate_statistical_report(
        self,
        report_type: str,
        start_date: datetime,
        end_date: datetime,
        user_id: int
    ) -> StatisticalReport:
        """Genera un reporte estadístico para el período especificado."""
        
        # Consultas base
        base_query = self.db.query(TestResult).join(Report).\
            filter(Report.report_date.between(start_date, end_date))
        
        # Total de pacientes únicos
        total_patients = self.db.query(func.count(func.distinct(Report.patient_id))).\
            filter(Report.report_date.between(start_date, end_date)).scalar()
        
        # Total de análisis
        total_tests = base_query.count()
        
        # Análisis por categoría
        tests_by_category = {}
        categories = self.db.query(AnalysisType.category).distinct().all()
        for category, in categories:
            count = base_query.join(AnalysisType).\
                filter(AnalysisType.category == category).count()
            tests_by_category[category] = count
        
        # Resultados por nivel de alerta
        results_by_alert = {}
        for alert_level in AlertLevel:
            count = base_query.filter(TestResult.alert_level == alert_level).count()
            results_by_alert[alert_level.value] = count
        
        # Análisis más frecuentes
        top_analyses = self.db.query(
            AnalysisType.name,
            func.count(TestResult.id).label('count')
        ).join(TestResult).group_by(AnalysisType.name).\
            order_by(func.count(TestResult.id).desc()).limit(10).all()
        
        # Médicos que más solicitan
        top_doctors = self.db.query(
            func.concat(User.full_name).label('doctor'),
            func.count(Report.id).label('count')
        ).join(Report, Report.doctor_id == User.id).\
            group_by(User.id).\
            order_by(func.count(Report.id).desc()).limit(5).all()
        
        # Crear reporte estadístico
        metrics = {
            "total_patients": total_patients,
            "total_tests": total_tests,
            "tests_by_category": tests_by_category,
            "results_by_alert": results_by_alert,
            "top_analyses": dict(top_analyses),
            "top_doctors": dict(top_doctors),
            "average_tests_per_patient": round(total_tests / total_patients if total_patients > 0 else 0, 2)
        }
        
        statistical_report = StatisticalReport(
            report_type=report_type,
            start_date=start_date,
            end_date=end_date,
            generated_by=user_id,
            metrics=metrics
        )
        
        self.db.add(statistical_report)
        self.db.commit()
        
        return statistical_report

    def generate_daily_report(self, date: datetime, user_id: int) -> StatisticalReport:
        """Genera un reporte estadístico diario."""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        return self.generate_statistical_report("daily", start_date, end_date, user_id)

    def generate_monthly_report(self, year: int, month: int, user_id: int) -> StatisticalReport:
        """Genera un reporte estadístico mensual."""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        return self.generate_statistical_report("monthly", start_date, end_date, user_id)
