from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import Base
from enum import Enum as PyEnum

class PrinterType(str, PyEnum):
    REPORT = 'report'
    BARCODE = 'barcode'
    TICKET = 'ticket'

class PrinterProtocol(str, PyEnum):
    RAW = 'raw'
    CUPS = 'cups'
    WINDOWS = 'windows'
    NETWORK = 'network'

class Printer(Base):
    __tablename__ = "printers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(PrinterType), nullable=False)
    protocol = Column(Enum(PrinterProtocol), nullable=False)
    network_address = Column(String)  # IP o nombre de red
    port = Column(Integer)  # Puerto para impresoras de red
    queue_name = Column(String)  # Nombre de cola de impresión
    is_default = Column(Boolean, default=False)
    paper_width = Column(Integer)  # Ancho del papel en mm
    paper_height = Column(Integer)  # Alto del papel en mm
    dpi = Column(Integer, default=203)  # Resolución de impresión
    
    @classmethod
    def get_default_printer(cls, db_session, type: PrinterType):
        """Obtiene la impresora predeterminada para un tipo específico."""
        return db_session.query(cls).filter_by(type=type, is_default=True).first()
