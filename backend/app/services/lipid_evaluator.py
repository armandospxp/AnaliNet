from typing import Dict, Optional
from ..models.test_types import AlertLevel

class LipidEvaluator:
    @staticmethod
    def evaluate_cardiovascular_risk(
        total_cholesterol: float,
        hdl: float,
        ldl: float,
        triglycerides: float,
        age: int,
        gender: str
    ) -> Dict[str, any]:
        """
        Evalúa el riesgo cardiovascular basado en el perfil lipídico.
        Retorna un diccionario con el nivel de riesgo y recomendaciones.
        """
        risk_factors = []
        recommendations = []
        
        # 1. Evaluar Colesterol Total
        if total_cholesterol >= 240:
            risk_factors.append("Colesterol Total elevado")
            recommendations.append(
                "Reducir consumo de grasas saturadas y trans. "
                "Aumentar consumo de fibra y vegetales."
            )
        
        # 2. Evaluar HDL (diferente por género)
        hdl_risk = False
        if gender == 'M' and hdl < 40:
            hdl_risk = True
        elif gender == 'F' and hdl < 50:
            hdl_risk = True
            
        if hdl_risk:
            risk_factors.append("HDL bajo (colesterol bueno)")
            recommendations.append(
                "Aumentar actividad física. "
                "Consumir ácidos grasos omega-3. "
                "Evitar el tabaquismo."
            )
        
        # 3. Evaluar LDL
        if ldl >= 160:
            risk_factors.append("LDL elevado (colesterol malo)")
            recommendations.append(
                "Reducir consumo de grasas saturadas. "
                "Aumentar consumo de fibra soluble. "
                "Considerar consulta con nutricionista."
            )
        
        # 4. Evaluar Triglicéridos
        if triglycerides >= 200:
            risk_factors.append("Triglicéridos elevados")
            recommendations.append(
                "Reducir consumo de azúcares y alcohol. "
                "Mantener peso saludable. "
                "Aumentar actividad física."
            )
        
        # 5. Calcular índice aterogénico
        atherogenic_index = total_cholesterol / hdl if hdl > 0 else float('inf')
        if (gender == 'M' and atherogenic_index > 4.5) or \
           (gender == 'F' and atherogenic_index > 4.0):
            risk_factors.append("Índice aterogénico elevado")
        
        # Determinar nivel de riesgo general
        risk_level = AlertLevel.NORMAL
        if len(risk_factors) >= 3:
            risk_level = AlertLevel.CRITICAL
        elif len(risk_factors) >= 1:
            risk_level = AlertLevel.WARNING
        
        # Agregar recomendaciones generales si hay riesgo
        if risk_level != AlertLevel.NORMAL:
            recommendations.append(
                "Se recomienda consulta médica para evaluación "
                "cardiovascular completa."
            )
        
        # Considerar factor edad
        age_risk = ""
        if age > 45 and gender == 'M':
            age_risk = "Hombre mayor de 45 años: factor de riesgo adicional"
        elif age > 55 and gender == 'F':
            age_risk = "Mujer mayor de 55 años: factor de riesgo adicional"
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "age_risk": age_risk if age_risk else None,
            "atherogenic_index": round(atherogenic_index, 1)
        }
    
    @staticmethod
    def get_reference_values(age: int, gender: str) -> Dict[str, Dict[str, float]]:
        """Retorna los valores de referencia según edad y género."""
        ref_values = {
            "total_cholesterol": {
                "optimal": "<200 mg/dL",
                "borderline": "200-239 mg/dL",
                "high": "≥240 mg/dL"
            },
            "hdl": {
                "low": f"<{'40' if gender == 'M' else '50'} mg/dL",
                "optimal": f">{'60' if gender == 'M' else '70'} mg/dL"
            },
            "ldl": {
                "optimal": "<100 mg/dL",
                "near_optimal": "100-129 mg/dL",
                "borderline": "130-159 mg/dL",
                "high": "160-189 mg/dL",
                "very_high": "≥190 mg/dL"
            },
            "triglycerides": {
                "normal": "<150 mg/dL",
                "borderline": "150-199 mg/dL",
                "high": "200-499 mg/dL",
                "very_high": "≥500 mg/dL"
            },
            "atherogenic_index": {
                "optimal": f"<{'4.5' if gender == 'M' else '4.0'}",
                "high": f">{'5.0' if gender == 'M' else '4.5'}"
            }
        }
        return ref_values
