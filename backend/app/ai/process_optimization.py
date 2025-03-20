from typing import List, Dict, Optional
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
from datetime import datetime, timedelta
from fastapi import HTTPException

class ProcessOptimization:
    def __init__(self):
        self.scaler = StandardScaler()
        self.load_predictor = None
        
    async def predict_workload(self, timeframe_hours: int = 24) -> Dict:
        """
        Predice la carga de trabajo futura basada en patrones históricos.
        """
        try:
            # Obtener datos históricos
            historical_data = await self._get_workload_history()
            
            if not historical_data:
                return {'status': 'insufficient_data'}
                
            df = pd.DataFrame(historical_data)
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Preparar características para predicción
            X = df[['hour', 'day_of_week']].values
            y = df['sample_count'].values
            
            # Entrenar modelo si no existe
            if not self.load_predictor:
                from sklearn.ensemble import RandomForestRegressor
                self.load_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
                self.load_predictor.fit(X, y)
                
            # Generar predicciones para las próximas horas
            future_hours = []
            current_time = datetime.now()
            for i in range(timeframe_hours):
                future_time = current_time + timedelta(hours=i)
                future_hours.append([
                    future_time.hour,
                    future_time.weekday()
                ])
                
            predictions = self.load_predictor.predict(np.array(future_hours))
            
            return {
                'predictions': [
                    {
                        'hour': current_time + timedelta(hours=i),
                        'predicted_samples': int(pred),
                        'confidence': float(self.load_predictor.score(X, y))
                    }
                    for i, pred in enumerate(predictions)
                ],
                'peak_hours': self._identify_peak_hours(predictions, future_hours),
                'resource_recommendations': self._generate_resource_recommendations(predictions)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en predicción de carga: {str(e)}")
            
    async def optimize_sample_routes(self, pending_samples: List[Dict]) -> List[Dict]:
        """
        Optimiza las rutas de procesamiento de muestras usando clustering.
        """
        try:
            if not pending_samples:
                return []
                
            # Preparar datos para clustering
            sample_data = []
            for sample in pending_samples:
                sample_data.append([
                    sample.get('processing_time', 0),
                    sample.get('priority_level', 1),
                    sample.get('equipment_id', 0)
                ])
                
            X = np.array(sample_data)
            X = self.scaler.fit_transform(X)
            
            # Determinar número óptimo de clusters
            n_clusters = min(len(pending_samples) // 5 + 1, 8)
            
            # Realizar clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X)
            
            # Organizar muestras por clusters
            optimized_routes = []
            for i in range(n_clusters):
                cluster_samples = [
                    {**sample, 'processing_order': order}
                    for order, (sample, cluster) in enumerate(zip(pending_samples, clusters))
                    if cluster == i
                ]
                
                # Ordenar por prioridad dentro del cluster
                cluster_samples.sort(key=lambda x: (
                    -x.get('priority_level', 0),
                    x.get('processing_time', 0)
                ))
                
                optimized_routes.append({
                    'route_id': i + 1,
                    'samples': cluster_samples,
                    'estimated_duration': sum(s.get('processing_time', 0) for s in cluster_samples),
                    'priority_level': max(s.get('priority_level', 0) for s in cluster_samples)
                })
                
            return optimized_routes
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en optimización de rutas: {str(e)}")
            
    async def predict_maintenance(self, equipment_data: List[Dict]) -> List[Dict]:
        """
        Predice necesidades de mantenimiento basado en patrones de uso y rendimiento.
        """
        try:
            predictions = []
            
            for equipment in equipment_data:
                # Analizar indicadores de rendimiento
                performance_score = self._calculate_performance_score(equipment)
                usage_intensity = self._calculate_usage_intensity(equipment)
                error_frequency = self._analyze_error_frequency(equipment)
                
                # Calcular probabilidad de mantenimiento necesario
                maintenance_probability = self._calculate_maintenance_probability(
                    performance_score,
                    usage_intensity,
                    error_frequency
                )
                
                if maintenance_probability > 0.7:  # Alta probabilidad
                    predictions.append({
                        'equipment_id': equipment.get('id'),
                        'equipment_name': equipment.get('name'),
                        'maintenance_probability': float(maintenance_probability),
                        'recommended_date': self._suggest_maintenance_date(
                            maintenance_probability,
                            equipment.get('last_maintenance')
                        ),
                        'reasons': self._get_maintenance_reasons(
                            performance_score,
                            usage_intensity,
                            error_frequency
                        ),
                        'priority': 'high' if maintenance_probability > 0.9 else 'medium'
                    })
                    
            return predictions
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en predicción de mantenimiento: {str(e)}")
            
    def _identify_peak_hours(self, predictions: np.ndarray, hours: List[List[int]]) -> List[Dict]:
        """
        Identifica las horas pico basadas en predicciones.
        """
        peak_threshold = np.percentile(predictions, 75)
        peak_hours = []
        
        for i, (pred, hour_data) in enumerate(zip(predictions, hours)):
            if pred > peak_threshold:
                peak_hours.append({
                    'hour': hour_data[0],
                    'day_of_week': hour_data[1],
                    'predicted_load': int(pred)
                })
                
        return peak_hours
        
    def _generate_resource_recommendations(self, predictions: np.ndarray) -> List[Dict]:
        """
        Genera recomendaciones de recursos basadas en predicciones de carga.
        """
        avg_load = np.mean(predictions)
        peak_load = np.max(predictions)
        
        recommendations = []
        
        # Recomendaciones de personal
        staff_needed = int(np.ceil(peak_load / 20))  # 20 muestras por técnico
        recommendations.append({
            'resource_type': 'staff',
            'recommended_amount': staff_needed,
            'reason': f"Carga máxima esperada de {int(peak_load)} muestras"
        })
        
        # Recomendaciones de equipos
        if peak_load > avg_load * 2:
            recommendations.append({
                'resource_type': 'equipment',
                'recommendation': 'Consider additional backup equipment for peak hours',
                'reason': 'High variation between average and peak load'
            })
            
        return recommendations
        
    def _calculate_performance_score(self, equipment: Dict) -> float:
        """
        Calcula score de rendimiento del equipo.
        """
        # Implementar lógica de cálculo de rendimiento
        return np.random.random()  # Placeholder
        
    def _calculate_usage_intensity(self, equipment: Dict) -> float:
        """
        Calcula la intensidad de uso del equipo.
        """
        # Implementar lógica de cálculo de uso
        return np.random.random()  # Placeholder
        
    def _analyze_error_frequency(self, equipment: Dict) -> float:
        """
        Analiza la frecuencia de errores del equipo.
        """
        # Implementar lógica de análisis de errores
        return np.random.random()  # Placeholder
        
    def _calculate_maintenance_probability(
        self,
        performance: float,
        usage: float,
        errors: float
    ) -> float:
        """
        Calcula la probabilidad de necesidad de mantenimiento.
        """
        # Implementar modelo de predicción
        return (performance * 0.4 + usage * 0.3 + errors * 0.3)
        
    def _suggest_maintenance_date(
        self,
        probability: float,
        last_maintenance: datetime
    ) -> datetime:
        """
        Sugiere fecha para próximo mantenimiento.
        """
        if probability > 0.9:
            days_to_add = 7
        elif probability > 0.8:
            days_to_add = 14
        else:
            days_to_add = 30
            
        return datetime.now() + timedelta(days=days_to_add)
        
    def _get_maintenance_reasons(
        self,
        performance: float,
        usage: float,
        errors: float
    ) -> List[str]:
        """
        Genera lista de razones para mantenimiento.
        """
        reasons = []
        
        if performance < 0.7:
            reasons.append("Bajo rendimiento detectado")
        if usage > 0.8:
            reasons.append("Alto uso acumulado")
        if errors > 0.6:
            reasons.append("Frecuencia de errores elevada")
            
        return reasons
        
    async def _get_workload_history(self) -> List[Dict]:
        """
        Obtiene historial de carga de trabajo.
        """
        # Implementar lógica de acceso a base de datos
        # Por ahora retornamos datos de ejemplo
        history = []
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(30 * 24):  # 30 días x 24 horas
            timestamp = start_date + timedelta(hours=i)
            base_load = 20  # Carga base
            
            # Añadir variación por hora del día
            hour_factor = 1 + np.sin(timestamp.hour * np.pi / 12) * 0.5
            
            # Añadir variación por día de la semana
            day_factor = 1.2 if timestamp.weekday() < 5 else 0.7
            
            # Calcular carga final con algo de ruido aleatorio
            load = int(base_load * hour_factor * day_factor * (1 + np.random.normal(0, 0.1)))
            
            history.append({
                'timestamp': timestamp,
                'sample_count': max(0, load)
            })
            
        return history
