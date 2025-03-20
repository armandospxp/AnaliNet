from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from .base import Base

class ProtocolType(str, Enum):
    HL7 = "HL7"
    ASTM = "ASTM"
    DICOM = "DICOM"
    POCT1_A = "POCT1-A"
    LIS2_A2 = "LIS2-A2"
    MODBUS = "MODBUS"
    IHE_PCD = "IHE-PCD"
    HL7_FHIR = "HL7-FHIR"
    ISO_11073 = "ISO-11073"
    PROPRIETARY = "PROPRIETARY"

class ConnectionType(str, Enum):
    NETWORK = "NETWORK"
    DB25 = "DB25"
    USB = "USB"
    RS232 = "RS232"
    RS485 = "RS485"
    BLUETOOTH = "BLUETOOTH"
    ETHERNET = "ETHERNET"
    WIFI = "WIFI"

class CommunicationType(str, Enum):
    UNIDIRECTIONAL = "UNIDIRECTIONAL"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    BIDIRECTIONAL_WITH_ACK = "BIDIRECTIONAL_WITH_ACK"

class EquipmentCategory(Base):
    __tablename__ = "equipment_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    supported_protocols = Column(JSON)  # List of supported protocols for this category
    equipment = relationship("Equipment", back_populates="category")

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    model = Column(String)
    serial_number = Column(String, unique=True)
    manufacturer = Column(String)
    category_id = Column(Integer, ForeignKey("equipment_categories.id"))
    protocol = Column(SQLAEnum(ProtocolType))
    connection_type = Column(SQLAEnum(ConnectionType))
    communication_type = Column(SQLAEnum(CommunicationType))
    
    # Network configuration
    ip_address = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    
    # Serial/DB25 configuration
    com_port = Column(String, nullable=True)
    baud_rate = Column(Integer, nullable=True)
    data_bits = Column(Integer, nullable=True)
    parity = Column(String, nullable=True)
    stop_bits = Column(Integer, nullable=True)
    
    # Protocol-specific configuration
    requires_ack = Column(Boolean, default=False)  # If ACK is needed for messages
    result_endpoint = Column(String, nullable=True)  # For HL7-FHIR endpoints
    polling_interval = Column(Integer, nullable=True)  # For polling-based equipment
    configuration = Column(JSON, nullable=True)  # Equipment-specific config
    
    category = relationship("EquipmentCategory", back_populates="equipment")
    test_results = relationship("TestResult", back_populates="equipment")
