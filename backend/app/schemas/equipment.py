from pydantic import BaseModel, IPvAnyAddress
from typing import Optional, List, Dict, Any
from enum import Enum
from ..models.equipment import ProtocolType, ConnectionType

class EquipmentCategoryBase(BaseModel):
    name: str
    description: str
    supported_protocols: List[ProtocolType]

class EquipmentCategoryCreate(EquipmentCategoryBase):
    pass

class EquipmentCategoryResponse(EquipmentCategoryBase):
    id: int

    class Config:
        from_attributes = True

class EquipmentBase(BaseModel):
    name: str
    model: str
    serial_number: str
    manufacturer: str
    category_id: int
    protocol: ProtocolType
    connection_type: ConnectionType
    
    # Network configuration
    ip_address: Optional[str] = None
    port: Optional[int] = None
    
    # Serial/DB25 configuration
    com_port: Optional[str] = None
    baud_rate: Optional[int] = None
    data_bits: Optional[int] = None
    parity: Optional[str] = None
    stop_bits: Optional[int] = None
    
    # Equipment-specific configuration
    configuration: Optional[Dict[str, Any]] = None

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentResponse(EquipmentBase):
    id: int
    category: EquipmentCategoryResponse

    class Config:
        from_attributes = True

class EquipmentCommand(BaseModel):
    command: str

class EquipmentCommandResponse(BaseModel):
    response: str
