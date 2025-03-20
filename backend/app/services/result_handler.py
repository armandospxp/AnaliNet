from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.equipment import Equipment, ProtocolType, CommunicationType
from ..models.test_result import TestResult
from .result_processor import ResultProcessorFactory
from .equipment_interface import EquipmentManager
import asyncio
import logging

logger = logging.getLogger(__name__)

class ResultHandler:
    def __init__(self, db: Session, equipment_manager: EquipmentManager):
        self.db = db
        self.equipment_manager = equipment_manager
        self._active_listeners: Dict[int, asyncio.Task] = {}

    async def start_listening(self, equipment_id: int):
        """Inicia la escucha de resultados para un equipo específico."""
        equipment = self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
        if not equipment:
            raise ValueError(f"Equipment {equipment_id} not found")

        if equipment_id in self._active_listeners:
            logger.warning(f"Already listening to equipment {equipment_id}")
            return

        # Crear el procesador de resultados según el protocolo
        processor = ResultProcessorFactory.create_processor(
            protocol=equipment.protocol,
            communication_type=equipment.communication_type,
            endpoint=equipment.result_endpoint
        )

        # Iniciar tarea de escucha en segundo plano
        task = asyncio.create_task(
            self._listen_for_results(equipment, processor)
        )
        self._active_listeners[equipment_id] = task
        logger.info(f"Started listening to equipment {equipment_id}")

    async def stop_listening(self, equipment_id: int):
        """Detiene la escucha de resultados para un equipo específico."""
        if equipment_id in self._active_listeners:
            self._active_listeners[equipment_id].cancel()
            del self._active_listeners[equipment_id]
            logger.info(f"Stopped listening to equipment {equipment_id}")

    async def _listen_for_results(self, equipment: Equipment, processor: Any):
        """Proceso de escucha continua para un equipo."""
        try:
            while True:
                try:
                    # Obtener datos del equipo
                    raw_data = await self.equipment_manager.receive_data_from_equipment(equipment.id)
                    if not raw_data:
                        if equipment.polling_interval:
                            await asyncio.sleep(equipment.polling_interval)
                        continue

                    # Procesar los resultados
                    processed_results = await processor.process_result(raw_data)

                    # Guardar resultados en la base de datos
                    await self._save_results(equipment, processed_results)

                    # Enviar acknowledgment si es necesario
                    if equipment.communication_type == CommunicationType.BIDIRECTIONAL_WITH_ACK:
                        await processor.send_acknowledgment(processed_results['message_id'])

                except Exception as e:
                    logger.error(f"Error processing results from equipment {equipment.id}: {str(e)}")
                    await asyncio.sleep(5)  # Esperar antes de reintentar

        except asyncio.CancelledError:
            logger.info(f"Listener for equipment {equipment.id} was cancelled")
        except Exception as e:
            logger.error(f"Fatal error in listener for equipment {equipment.id}: {str(e)}")

    async def _save_results(self, equipment: Equipment, processed_results: Dict[str, Any]):
        """Guarda los resultados procesados en la base de datos."""
        try:
            for result in processed_results['results']:
                test_result = TestResult(
                    equipment_id=equipment.id,
                    patient_id=processed_results['patient_id'],
                    test_code=result['test_code'],
                    test_name=result.get('test_name', ''),
                    result_value=result['value'],
                    units=result.get('units', ''),
                    reference_range=result.get('reference_range', ''),
                    flags=result.get('flags', ''),
                    status=result.get('status', ''),
                    result_datetime=datetime.fromisoformat(processed_results['message_datetime']),
                    raw_message=str(processed_results)
                )
                self.db.add(test_result)
            
            self.db.commit()
            logger.info(f"Saved results for equipment {equipment.id}, patient {processed_results['patient_id']}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving results: {str(e)}")
            raise

    async def request_results(self, equipment_id: int, patient_id: Optional[str] = None) -> bool:
        """Solicita resultados a un equipo de forma activa (solo para equipos bidireccionales)."""
        equipment = self.db.query(Equipment).filter(Equipment.id == equipment_id).first()
        if not equipment:
            raise ValueError(f"Equipment {equipment_id} not found")

        if equipment.communication_type == CommunicationType.UNIDIRECTIONAL:
            raise ValueError("Cannot request results from unidirectional equipment")

        try:
            # Construir comando según el protocolo
            command = self._build_request_command(equipment.protocol, patient_id)
            
            # Enviar comando al equipo
            await self.equipment_manager.send_command_to_equipment(equipment_id, command)
            return True

        except Exception as e:
            logger.error(f"Error requesting results from equipment {equipment_id}: {str(e)}")
            return False

    def _build_request_command(self, protocol: ProtocolType, patient_id: Optional[str]) -> str:
        """Construye el comando de solicitud según el protocolo."""
        if protocol == ProtocolType.HL7:
            # Construir mensaje HL7 QRY^R02
            return (
                f"MSH|^~\\&|LIS|LAB|EQP|LAB|{datetime.now().strftime('%Y%m%d%H%M%S')}||QRY^R02|"
                f"MSG{datetime.now().strftime('%Y%m%d%H%M%S')}|P|2.5.1\r"
                f"QRD|{datetime.now().strftime('%Y%m%d%H%M%S')}|R|I|"
                f"QueryID|||RD|{patient_id or ''}|^^^||\r"
            )
        
        elif protocol == ProtocolType.ASTM:
            # Construir mensaje ASTM de solicitud
            return f"\x02H|\\^&|||LIS|LAB||{patient_id or ''}||P|1\rQ|1|{patient_id or ''}^ALL||ALL\r\x03\r\n"
        
        elif protocol == ProtocolType.HL7_FHIR:
            # Para FHIR, la solicitud se maneja vía HTTP en el procesador
            return json.dumps({
                "resourceType": "Parameters",
                "parameter": [
                    {
                        "name": "patient",
                        "valueString": patient_id or ""
                    },
                    {
                        "name": "type",
                        "valueString": "ALL"
                    }
                ]
            })
        
        else:
            raise ValueError(f"Unsupported protocol for result request: {protocol}")
