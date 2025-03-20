from abc import ABC, abstractmethod
import socket
import serial
import hl7
from hl7.client import MLLPClient
from typing import Optional, Dict, Any
import json
import logging
from ..models.equipment import ProtocolType, ConnectionType

logger = logging.getLogger(__name__)

class EquipmentInterface(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def send_command(self, command: str) -> str:
        pass

    @abstractmethod
    async def receive_data(self) -> str:
        pass

class NetworkEquipment(EquipmentInterface):
    def __init__(self, ip: str, port: int, protocol: ProtocolType):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.client: Optional[MLLPClient] = None
        self.socket: Optional[socket.socket] = None

    async def connect(self):
        try:
            if self.protocol == ProtocolType.HL7:
                self.client = MLLPClient(self.ip, self.port)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.ip, self.port))
            logger.info(f"Connected to equipment at {self.ip}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to equipment: {str(e)}")
            raise

    async def disconnect(self):
        try:
            if self.client:
                self.client.close()
            if self.socket:
                self.socket.close()
            logger.info("Disconnected from equipment")
        except Exception as e:
            logger.error(f"Error disconnecting from equipment: {str(e)}")

    async def send_command(self, command: str) -> str:
        try:
            if self.protocol == ProtocolType.HL7:
                message = hl7.parse(command)
                response = self.client.send_message(message)
                return str(response)
            else:
                self.socket.sendall(command.encode())
                return await self.receive_data()
        except Exception as e:
            logger.error(f"Error sending command: {str(e)}")
            raise

    async def receive_data(self) -> str:
        try:
            if self.protocol == ProtocolType.HL7:
                return str(self.client.recv_message())
            else:
                data = self.socket.recv(4096)
                return data.decode()
        except Exception as e:
            logger.error(f"Error receiving data: {str(e)}")
            raise

class SerialEquipment(EquipmentInterface):
    def __init__(self, port: str, baud_rate: int, protocol: ProtocolType,
                 data_bits: int = 8, parity: str = 'N', stop_bits: int = 1):
        self.port = port
        self.baud_rate = baud_rate
        self.protocol = protocol
        self.data_bits = data_bits
        self.parity = parity
        self.stop_bits = stop_bits
        self.serial: Optional[serial.Serial] = None

    async def connect(self):
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                bytesize=self.data_bits,
                parity=self.parity,
                stopbits=self.stop_bits,
                timeout=1
            )
            logger.info(f"Connected to equipment on {self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to equipment: {str(e)}")
            raise

    async def disconnect(self):
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
            logger.info("Disconnected from equipment")
        except Exception as e:
            logger.error(f"Error disconnecting from equipment: {str(e)}")

    async def send_command(self, command: str) -> str:
        try:
            if self.protocol == ProtocolType.ASTM:
                # Add ASTM frame delimiters
                command = f"\x02{command}\x03\r\n"
            
            self.serial.write(command.encode())
            return await self.receive_data()
        except Exception as e:
            logger.error(f"Error sending command: {str(e)}")
            raise

    async def receive_data(self) -> str:
        try:
            data = self.serial.readline()
            if self.protocol == ProtocolType.ASTM:
                # Remove ASTM frame delimiters
                data = data.strip(b'\x02\x03\r\n')
            return data.decode()
        except Exception as e:
            logger.error(f"Error receiving data: {str(e)}")
            raise

class EquipmentManager:
    def __init__(self):
        self.active_connections: Dict[int, EquipmentInterface] = {}

    async def connect_equipment(self, equipment_id: int, config: Dict[str, Any]) -> EquipmentInterface:
        try:
            if config['connection_type'] == ConnectionType.NETWORK:
                interface = NetworkEquipment(
                    ip=config['ip_address'],
                    port=config['port'],
                    protocol=config['protocol']
                )
            else:  # DB25/Serial
                interface = SerialEquipment(
                    port=config['com_port'],
                    baud_rate=config['baud_rate'],
                    protocol=config['protocol'],
                    data_bits=config.get('data_bits', 8),
                    parity=config.get('parity', 'N'),
                    stop_bits=config.get('stop_bits', 1)
                )

            await interface.connect()
            self.active_connections[equipment_id] = interface
            return interface

        except Exception as e:
            logger.error(f"Failed to connect equipment {equipment_id}: {str(e)}")
            raise

    async def disconnect_equipment(self, equipment_id: int):
        try:
            if equipment_id in self.active_connections:
                await self.active_connections[equipment_id].disconnect()
                del self.active_connections[equipment_id]
                logger.info(f"Equipment {equipment_id} disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting equipment {equipment_id}: {str(e)}")
            raise

    async def send_command_to_equipment(self, equipment_id: int, command: str) -> str:
        try:
            if equipment_id not in self.active_connections:
                raise ValueError(f"Equipment {equipment_id} is not connected")
            
            interface = self.active_connections[equipment_id]
            return await interface.send_command(command)
        except Exception as e:
            logger.error(f"Error sending command to equipment {equipment_id}: {str(e)}")
            raise
