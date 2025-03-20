from typing import List, Dict, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime
from fastapi import HTTPException

class DiagnosticAssistant:
    def __init__(self):
        self.scaler = StandardScaler()
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
    async def interpret_results(self, results: Dict) -> Dict:
        """
        Interpreta automáticamente los resultados basándose en valores de referencia
        y patrones conocidos.
        """
        try:
            interpretation = {
                'summary': [],
                'alerts': [],
                'recommendations': []
            }
            
            # Analizar cada resultado
            for test_code, test_data in results.items():
                value = float(test_data.get('value', 0))
                ref_min = float(test_data.get('reference_min', 0))
                ref_max = float(test_data.get('reference_max', float('inf')))
                
                # Evaluar el resultado
                if value < ref_min:
                    severity = self._calculate_severity(value, ref_min, 'low')
                    interpretation['summary'].append({
                        'test_code': test_code,
                        'finding': 'below_reference',
                        'severity': severity,
                        'description': f"{test_data.get('name')} por debajo del rango de referencia"
                    })
                    
                elif value > ref_max:
                    severity = self._calculate_severity(value, ref_max, 'high')
                    interpretation['summary'].append({
                        'test_code': test_code,
                        'finding': 'above_reference',
                        'severity': severity,
                        'description': f"{test_data.get('name')} por encima del rango de referencia"
                    })
                    
                # Generar alertas para valores críticos
                if 'severity' in locals() and severity == 'critical':
                    interpretation['alerts'].append({
                        'level': 'critical',
                        'message': f"Valor crítico en {test_data.get('name')}",
                        'value': value,
                        'reference_range': f"{ref_min}-{ref_max}"
                    })
                    
            # Analizar patrones y correlaciones
            patterns = await self._analyze_patterns(results)
            interpretation['patterns'] = patterns
            
            # Generar recomendaciones
            recommendations = await self._generate_recommendations(interpretation['summary'], patterns)
            interpretation['recommendations'] = recommendations
            
            return interpretation
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en interpretación: {str(e)}")
            
    async def analyze_historical_patterns(self, patient_id: int, timeframe_days: int = 365) -> Dict:
        """
        Analiza patrones históricos en los resultados del paciente.
        """
        try:
            # Obtener historial del paciente
            historical_data = await self._get_patient_history(patient_id, timeframe_days)
            
            if not historical_data:
                return {'status': 'no_data'}
                
            patterns = {
                'recurring_abnormalities': [],
                'improvements': [],
                'deteriorations': [],
                'correlations': []
            }
            
            # Analizar tendencias por prueba
            df = pd.DataFrame(historical_data)
            for test_code in df['test_code'].unique():
                test_data = df[df['test_code'] == test_code]
                
                # Detectar tendencias
                if len(test_data) >= 3:
                    trend = self._analyze_trend(test_data['value'].values)
                    if trend['direction'] == 'improving':
                        patterns['improvements'].append({
                            'test_code': test_code,
                            'confidence': trend['confidence']
                        })
                    elif trend['direction'] == 'deteriorating':
                        patterns['deteriorations'].append({
                            'test_code': test_code,
                            'confidence': trend['confidence']
                        })
                        
            # Analizar correlaciones entre pruebas
            if len(df['test_code'].unique()) >= 2:
                correlations = self._analyze_correlations(df)
                patterns['correlations'] = correlations
                
            return patterns
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en análisis de patrones: {str(e)}")
            
    def _calculate_severity(self, value: float, reference: float, direction: str) -> str:
        """
        Calcula la severidad de la desviación del valor de referencia.
        """
        if direction == 'low':
            ratio = reference / value
        else:
            ratio = value / reference
            
        if ratio > 2:
            return 'critical'
        elif ratio > 1.5:
            return 'severe'
        elif ratio > 1.2:
            return 'moderate'
        else:
            return 'mild'
            
    async def _analyze_patterns(self, results: Dict) -> List[Dict]:
        """
        Analiza patrones y correlaciones en los resultados actuales.
        """
        patterns = []
        
        # Ejemplo: Patrón de anemia
        if all(test in results for test in ['HGB', 'HCT', 'RBC']):
            if all(float(results[test]['value']) < float(results[test]['reference_min']) 
                  for test in ['HGB', 'HCT', 'RBC']):
                patterns.append({
                    'pattern': 'anemia_pattern',
                    'confidence': 0.9,
                    'description': 'Patrón sugestivo de anemia'
                })
                
        # Ejemplo: Patrón de infección
        if all(test in results for test in ['WBC', 'NEUT', 'CRP']):
            if (float(results['WBC']['value']) > float(results['WBC']['reference_max']) and
                float(results['NEUT']['value']) > float(results['NEUT']['reference_max']) and
                float(results['CRP']['value']) > float(results['CRP']['reference_max'])):
                patterns.append({
                    'pattern': 'infection_pattern',
                    'confidence': 0.85,
                    'description': 'Patrón sugestivo de proceso infeccioso'
                })
                
        return patterns
        
    async def _generate_recommendations(self, summary: List[Dict], patterns: List[Dict]) -> List[Dict]:
        """
        Genera recomendaciones basadas en los hallazgos y patrones.
        """
        recommendations = []
        
        # Recomendaciones basadas en hallazgos individuales
        for finding in summary:
            if finding['severity'] in ['critical', 'severe']:
                recommendations.append({
                    'priority': 'high',
                    'type': 'repeat_test',
                    'description': f"Repetir {finding['test_code']} para confirmar resultado"
                })
                
        # Recomendaciones basadas en patrones
        for pattern in patterns:
            if pattern['pattern'] == 'anemia_pattern':
                recommendations.extend([
                    {
                        'priority': 'high',
                        'type': 'additional_test',
                        'description': 'Solicitar perfil de hierro completo'
                    },
                    {
                        'priority': 'medium',
                        'type': 'additional_test',
                        'description': 'Considerar vitamina B12 y ácido fólico'
                    }
                ])
                
            elif pattern['pattern'] == 'infection_pattern':
                recommendations.append({
                    'priority': 'high',
                    'type': 'additional_test',
                    'description': 'Considerar hemocultivos si hay fiebre'
                })
                
        return recommendations
        
    def _analyze_trend(self, values: np.ndarray) -> Dict:
        """
        Analiza la tendencia en una serie de valores.
        """
        try:
            # Calcular pendiente usando regresión lineal
            x = np.arange(len(values)).reshape(-1, 1)
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(x, values)
            
            slope = model.coef_[0]
            confidence = float(model.score(x, values))
            
            if abs(slope) < 0.1:
                direction = 'stable'
            elif slope > 0:
                direction = 'deteriorating' if values[0] < values[-1] else 'improving'
            else:
                direction = 'improving' if values[0] > values[-1] else 'deteriorating'
                
            return {
                'direction': direction,
                'confidence': confidence,
                'slope': float(slope)
            }
            
        except Exception:
            return {
                'direction': 'undefined',
                'confidence': 0.0,
                'slope': 0.0
            }
            
    def _analyze_correlations(self, df: pd.DataFrame) -> List[Dict]:
        """
        Analiza correlaciones entre diferentes pruebas.
        """
        correlations = []
        
        # Pivotar DataFrame para análisis de correlación
        pivot_df = df.pivot(columns='test_code', values='value')
        corr_matrix = pivot_df.corr()
        
        # Encontrar correlaciones significativas
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Correlación significativa
                    correlations.append({
                        'test_1': corr_matrix.columns[i],
                        'test_2': corr_matrix.columns[j],
                        'correlation': float(corr_value),
                        'strength': 'strong' if abs(corr_value) > 0.9 else 'moderate'
                    })
                    
        return correlations
        
    async def _get_patient_history(self, patient_id: int, timeframe_days: int) -> List[Dict]:
        """
        Obtiene el historial de resultados del paciente.
        """
        # Implementar lógica de acceso a base de datos
        # Por ahora retornamos datos de ejemplo
        return [
            {
                'test_code': 'HGB',
                'value': float(np.random.normal(14, 1)),
                'date': datetime.now()
            }
            for _ in range(10)
        ]
