from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base
from .auth import User

class BiochemistProfile(Base):
    __tablename__ = "biochemist_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    registration_number = Column(String, unique=True, nullable=False)
    digital_signature = Column(String)  # Certificado de firma digital
    signature_image = Column(LargeBinary)  # Firma escaneada
    professional_license = Column(String, nullable=False)
    specialties = Column(String)  # Lista de especialidades separadas por comas
    
    # Relación con el usuario
    user = relationship("User", back_populates="biochemist_profile")
    
    # Relación con las validaciones de resultados
    validated_results = relationship("Result", back_populates="validator")

    def verify_digital_signature(self, data: str, signature: str) -> bool:
        """Verifica una firma digital usando el certificado almacenado."""
        # Implementar verificación de firma digital
        pass

    def sign_report(self, report_data: dict) -> tuple[str, str]:
        """Firma digitalmente un reporte y devuelve el hash y la firma."""
        # Implementar firma digital de reportes
        pass

# Agregar la relación inversa en el modelo User
User.biochemist_profile = relationship("BiochemistProfile", back_populates="user", uselist=False)
