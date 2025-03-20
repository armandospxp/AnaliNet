from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .auth import User
from .test_types import AnalysisType, AlertLevel

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    admission_number = Column(String, unique=True, index=True)  # Número de ingreso
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))  # Médico solicitante
    technician_id = Column(Integer, ForeignKey("users.id"))  # Técnico que procesa
    validator_id = Column(Integer, ForeignKey("users.id"))  # Bioquímico que valida
    report_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # draft, validated, printed
    
    patient = relationship("Patient", back_populates="reports")
    doctor = relationship("User", foreign_keys=[doctor_id])
    technician = relationship("User", foreign_keys=[technician_id])
    validator = relationship("User", foreign_keys=[validator_id])
    results = relationship("TestResult", back_populates="report")

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    analysis_id = Column(Integer, ForeignKey("analysis_types.id"))
    determination_id = Column(Integer, ForeignKey("determinations.id"))
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    
    value = Column(String)  # Valor del resultado
    unit = Column(String)  # Unidad de medida
    reference_range = Column(JSON)  # Rango de referencia aplicado
    alert_level = Column(Enum(AlertLevel))
    observation = Column(String, nullable=True)  # Observaciones adicionales
    processed_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)
    
    report = relationship("Report", back_populates="results")
    analysis = relationship("AnalysisType")
    determination = relationship("Determination")
    equipment = relationship("Equipment")

class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    header_html = Column(String)  # Template HTML para la cabecera
    footer_html = Column(String)  # Template HTML para el pie
    css_styles = Column(String)  # Estilos CSS para el reporte
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def create_default_template(cls, db_session):
        """Crea el template por defecto si no existe."""
        if not db_session.query(cls).filter_by(name="default").first():
            default_template = cls(
                name="default",
                description="Template por defecto para reportes de laboratorio",
                header_html="""
                    <div class="header">
                        <div class="logo">
                            <img src="logo.png" alt="Logo Laboratorio">
                        </div>
                        <div class="lab-info">
                            <h1>{{lab_name}}</h1>
                            <p>{{lab_address}}</p>
                            <p>Tel: {{lab_phone}}</p>
                        </div>
                        <div class="patient-info">
                            <table>
                                <tr><td>Paciente:</td><td>{{patient_name}}</td></tr>
                                <tr><td>DNI:</td><td>{{patient_document}}</td></tr>
                                <tr><td>Fecha Nac.:</td><td>{{patient_birth_date}}</td></tr>
                                <tr><td>Sexo:</td><td>{{patient_gender}}</td></tr>
                                <tr><td>Médico:</td><td>{{doctor_name}}</td></tr>
                            </table>
                        </div>
                        <div class="report-info">
                            <table>
                                <tr><td>Nro. Ingreso:</td><td>{{admission_number}}</td></tr>
                                <tr><td>Fecha:</td><td>{{report_date}}</td></tr>
                            </table>
                        </div>
                    </div>
                """,
                footer_html="""
                    <div class="footer">
                        <div class="signatures">
                            <div class="signature">
                                <p>_____________________</p>
                                <p>{{technician_name}}</p>
                                <p>Técnico de Laboratorio</p>
                            </div>
                            <div class="signature">
                                <p>_____________________</p>
                                <p>{{validator_name}}</p>
                                <p>Bioquímico</p>
                            </div>
                        </div>
                        <div class="page-number">
                            Página <pdf:pagenumber> de <pdf:pagecount>
                        </div>
                    </div>
                """,
                css_styles="""
                    @page {
                        size: letter portrait;
                        margin: 2cm;
                        @frame header_frame {
                            -pdf-frame-content: header_content;
                            left: 50pt; width: 512pt; top: 50pt; height: 160pt;
                        }
                        @frame content_frame {
                            left: 50pt; width: 512pt; top: 210pt; height: 632pt;
                        }
                        @frame footer_frame {
                            -pdf-frame-content: footer_content;
                            left: 50pt; width: 512pt; top: 842pt; height: 100pt;
                        }
                    }
                    .header { width: 100%; }
                    .logo { float: left; width: 20%; }
                    .lab-info { float: left; width: 40%; }
                    .patient-info { float: left; width: 40%; }
                    .report-info { clear: both; width: 100%; }
                    table { width: 100%; border-collapse: collapse; }
                    td, th { padding: 4px; }
                    .result-table { width: 100%; margin-top: 20px; }
                    .result-table th { background-color: #f0f0f0; }
                    .result-normal { color: green; }
                    .result-warning { color: orange; }
                    .result-critical { color: red; }
                    .footer { width: 100%; text-align: center; }
                    .signatures { margin-top: 30px; }
                    .signature { display: inline-block; margin: 0 20px; }
                    .page-number { margin-top: 20px; }
                """
            )
            db_session.add(default_template)
            db_session.commit()

class StatisticalReport(Base):
    __tablename__ = "statistical_reports"

    id = Column(Integer, primary_key=True)
    report_type = Column(String)  # daily, monthly, date_range
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, ForeignKey("users.id"))
    
    metrics = Column(JSON)  # Métricas calculadas
    # Ejemplo de métricas:
    # {
    #     "total_patients": 150,
    #     "total_tests": 450,
    #     "tests_by_category": {
    #         "Hematología": 200,
    #         "Bioquímica": 150,
    #         "Uroanálisis": 100
    #     },
    #     "results_by_alert": {
    #         "normal": 350,
    #         "warning": 70,
    #         "critical": 30
    #     }
    # }
    
    user = relationship("User")
