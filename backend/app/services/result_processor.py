from abc import ABC, abstractmethod
import hl7
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
import requests
from ..models.equipment import ProtocolType, CommunicationType

class ResultProcessor(ABC):
    @abstractmethod
    async def process_result(self, raw_data: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def send_acknowledgment(self, message_id: str) -> bool:
        pass

class HL7ResultProcessor(ResultProcessor):
    def __init__(self, communication_type: CommunicationType):
        self.communication_type = communication_type

    async def process_result(self, raw_data: str) -> Dict[str, Any]:
        try:
            # Parse HL7 message
            message = hl7.parse(raw_data)
            
            # Extract patient information from PID segment
            pid = message.segment('PID')
            patient_id = str(pid[3][0] if pid[3][0] else '')
            patient_name = str(pid[5][0] if pid[5][0] else '')
            
            # Extract observation results from OBX segments
            results = []
            for obx in message.segments('OBX'):
                result = {
                    'test_code': str(obx[3][0] if obx[3][0] else ''),
                    'test_name': str(obx[3][1] if obx[3][1] else ''),
                    'value': str(obx[5][0] if obx[5][0] else ''),
                    'units': str(obx[6][0] if obx[6][0] else ''),
                    'reference_range': str(obx[7][0] if obx[7][0] else ''),
                    'flags': str(obx[8][0] if obx[8][0] else ''),
                    'status': str(obx[11][0] if obx[11][0] else '')
                }
                results.append(result)
            
            return {
                'message_id': str(message.segment('MSH')[10]),
                'message_datetime': str(message.segment('MSH')[7]),
                'patient_id': patient_id,
                'patient_name': patient_name,
                'results': results
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing HL7 message: {str(e)}")

    async def send_acknowledgment(self, message_id: str) -> bool:
        if self.communication_type != CommunicationType.BIDIRECTIONAL_WITH_ACK:
            return True

        # Create HL7 ACK message
        ack = f"MSH|^~\\&|LIS|LAB|EQP|LAB|{datetime.now().strftime('%Y%m%d%H%M%S')}||ACK|{message_id}|P|2.5.1\r"
        ack += "MSA|AA|{message_id}|Message received successfully\r"
        return ack

class ASTMResultProcessor(ResultProcessor):
    def __init__(self, communication_type: CommunicationType):
        self.communication_type = communication_type

    async def process_result(self, raw_data: str) -> Dict[str, Any]:
        try:
            # Remove ASTM frame delimiters
            data = raw_data.strip('\x02\x03\r\n')
            records = data.split('\r')
            
            header = None
            patient = None
            results = []
            
            for record in records:
                if not record:
                    continue
                    
                record_type = record[0]
                fields = record.split('|')
                
                if record_type == 'H':  # Header Record
                    header = {
                        'sender': fields[4] if len(fields) > 4 else '',
                        'message_id': fields[5] if len(fields) > 5 else ''
                    }
                elif record_type == 'P':  # Patient Record
                    patient = {
                        'id': fields[3] if len(fields) > 3 else '',
                        'name': fields[4] if len(fields) > 4 else ''
                    }
                elif record_type == 'R':  # Result Record
                    result = {
                        'test_code': fields[2] if len(fields) > 2 else '',
                        'value': fields[3] if len(fields) > 3 else '',
                        'units': fields[4] if len(fields) > 4 else '',
                        'reference_range': fields[5] if len(fields) > 5 else '',
                        'flags': fields[6] if len(fields) > 6 else '',
                        'status': fields[8] if len(fields) > 8 else ''
                    }
                    results.append(result)
            
            return {
                'message_id': header['message_id'] if header else '',
                'message_datetime': datetime.now().isoformat(),
                'patient_id': patient['id'] if patient else '',
                'patient_name': patient['name'] if patient else '',
                'results': results
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing ASTM message: {str(e)}")

    async def send_acknowledgment(self, message_id: str) -> bool:
        if self.communication_type != CommunicationType.BIDIRECTIONAL_WITH_ACK:
            return True

        # Create ASTM ACK message
        ack = f"\x02H|\\^&|||LIS|LAB||{message_id}||P|1\r\x03\r\n"
        return ack

class HL7FHIRResultProcessor(ResultProcessor):
    def __init__(self, communication_type: CommunicationType, endpoint: str):
        self.communication_type = communication_type
        self.endpoint = endpoint

    async def process_result(self, raw_data: str) -> Dict[str, Any]:
        try:
            # Parse FHIR JSON data
            fhir_data = json.loads(raw_data)
            
            # Extract patient information
            patient = fhir_data.get('subject', {}).get('reference', '').split('/')[-1]
            patient_name = fhir_data.get('subject', {}).get('display', '')
            
            # Extract results from observation resource
            results = []
            for component in fhir_data.get('component', []):
                result = {
                    'test_code': component.get('code', {}).get('coding', [{}])[0].get('code', ''),
                    'test_name': component.get('code', {}).get('coding', [{}])[0].get('display', ''),
                    'value': str(component.get('valueQuantity', {}).get('value', '')),
                    'units': component.get('valueQuantity', {}).get('unit', ''),
                    'reference_range': component.get('referenceRange', [{}])[0].get('text', ''),
                    'status': fhir_data.get('status', '')
                }
                results.append(result)
            
            return {
                'message_id': fhir_data.get('id', ''),
                'message_datetime': fhir_data.get('effectiveDateTime', datetime.now().isoformat()),
                'patient_id': patient,
                'patient_name': patient_name,
                'results': results
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing FHIR message: {str(e)}")

    async def send_acknowledgment(self, message_id: str) -> bool:
        if self.communication_type != CommunicationType.BIDIRECTIONAL_WITH_ACK:
            return True

        try:
            # Send FHIR acknowledgment using REST
            ack_data = {
                "resourceType": "MessageHeader",
                "response": {
                    "identifier": message_id,
                    "code": "ok"
                }
            }
            response = requests.post(f"{self.endpoint}/$process-message", json=ack_data)
            return response.status_code == 200
        except Exception:
            return False

class ResultProcessorFactory:
    @staticmethod
    def create_processor(protocol: ProtocolType, communication_type: CommunicationType, 
                        endpoint: Optional[str] = None) -> ResultProcessor:
        if protocol == ProtocolType.HL7:
            return HL7ResultProcessor(communication_type)
        elif protocol == ProtocolType.ASTM:
            return ASTMResultProcessor(communication_type)
        elif protocol == ProtocolType.HL7_FHIR:
            if not endpoint:
                raise ValueError("FHIR endpoint is required for HL7-FHIR protocol")
            return HL7FHIRResultProcessor(communication_type, endpoint)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
