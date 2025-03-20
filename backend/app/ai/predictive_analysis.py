from typing import List, Dict, Optional
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta
from fastapi import HTTPException

class PredictiveAnalysis:
    def __init__(self):
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        
    async def detect_anomalies(self, results: List[Dict]) -> List[Dict]:
        """
        Detecta valores anómalos en los resultados utilizando Isolation Forest.
        """
        try:
            # Preparar datos
            df = pd.DataFrame(results)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                return []
                
            # Normalizar datos
            X = self.scaler.fit_transform(df[numeric_cols])
            
            # Detectar anomalías
            predictions = self.isolation_forest.fit_predict(X)
            
            # Identificar resultados anómalos
            anomalies = []
            for i, pred in enumerate(predictions):
                if pred == -1:  # -1 indica anomalía
                    anomalies.append({
                        'result_id': results[i].get('id'),
                        'value': results[i].get('value'),
                        'test_name': results[i].get('test_name'),
                        'confidence_score': float(self.isolation_forest.score_samples([X[i]])[0])
                    })
                    
            return anomalies
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en detección de anomalías: {str(e)}")
            
    async def predict_trends(self, patient_id: int, test_code: str, timeframe_days: int = 90) -> Dict:
        """
        Predice tendencias futuras basadas en resultados históricos.
        """
        try:
            # Aquí iría la lógica para obtener datos históricos de la base de datos
            # Por ahora usamos datos de ejemplo
            historical_data = await self._get_historical_data(patient_id, test_code, timeframe_days)
            
            if len(historical_data) < 3:
                return {'status': 'insufficient_data'}
                
            # Análisis de tendencia
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Calcular tendencia usando regresión lineal simple
            X = np.arange(len(df)).reshape(-1, 1)
            y = df['value'].values
            
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X, y)
            
            # Predecir próximo valor
            next_point = model.predict([[len(df)]])[0]
            
            # Calcular dirección y velocidad de cambio
            slope = model.coef_[0]
            trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
            
            return {
                'current_value': float(df['value'].iloc[-1]),
                'predicted_next': float(next_point),
                'trend_direction': trend_direction,
                'change_rate': float(slope),
                'confidence_score': float(model.score(X, y))
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en predicción de tendencias: {str(e)}")
            
    async def suggest_complementary_tests(self, current_results: Dict) -> List[Dict]:
        """
        Sugiere pruebas complementarias basadas en los resultados actuales.
        """
        try:
            # Implementar lógica de recomendación basada en reglas y patrones históricos
            suggestions = []
            
            # Ejemplo: Si hemoglobina baja, sugerir ferritina y vitamina B12
            if current_results.get('test_code') == 'HGB' and \
               float(current_results.get('value', 0)) < current_results.get('reference_min', 0):
                suggestions.extend([
                    {
                        'test_code': 'FERR',
                        'test_name': 'Ferritina',
                        'reason': 'Evaluación de anemia',
                        'priority': 'high'
                    },
                    {
                        'test_code': 'B12',
                        'test_name': 'Vitamina B12',
                        'reason': 'Evaluación de anemia',
                        'priority': 'medium'
                    }
                ])
                
            return suggestions
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en sugerencias: {str(e)}")
            
    async def _get_historical_data(self, patient_id: int, test_code: str, timeframe_days: int) -> List[Dict]:
        """
        Obtiene datos históricos de la base de datos.
        """
        # Implementar lógica de acceso a base de datos
        # Por ahora retornamos datos de ejemplo
        return [
            {'date': datetime.now() - timedelta(days=i), 'value': float(np.random.normal(100, 10))}
            for i in range(timeframe_days, 0, -7)
        ]
