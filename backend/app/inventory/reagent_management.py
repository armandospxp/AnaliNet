from typing import List, Dict, Optional
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from fastapi import HTTPException
from pydantic import BaseModel

class Reagent(BaseModel):
    id: int
    name: str
    code: str
    current_stock: float
    unit: str
    min_stock: float
    optimal_stock: float
    price_per_unit: float
    supplier: str
    last_order_date: Optional[datetime]
    expiration_date: datetime
    tests_per_unit: float
    status: str  # active, discontinued, pending_order

class ReagentManagement:
    def __init__(self):
        self.stock_predictor = LinearRegression()
        
    async def check_stock_status(self, reagent_id: int) -> Dict:
        """
        Verifica el estado del stock de un reactivo y predice necesidades futuras.
        """
        try:
            # Obtener datos del reactivo
            reagent = await self._get_reagent(reagent_id)
            usage_history = await self._get_usage_history(reagent_id)
            
            # Calcular predicción de consumo
            predicted_usage = await self._predict_usage(usage_history)
            days_until_min_stock = self._calculate_days_until_min_stock(
                reagent.current_stock,
                reagent.min_stock,
                predicted_usage['daily_usage']
            )
            
            # Calcular cantidad óptima de pedido
            optimal_order = self._calculate_optimal_order(
                reagent.current_stock,
                reagent.optimal_stock,
                predicted_usage['daily_usage'],
                predicted_usage['trend']
            )
            
            return {
                'reagent_id': reagent_id,
                'current_stock': reagent.current_stock,
                'min_stock': reagent.min_stock,
                'days_until_min_stock': days_until_min_stock,
                'status': self._determine_status(days_until_min_stock, reagent.expiration_date),
                'predicted_usage': predicted_usage,
                'recommended_order': {
                    'quantity': optimal_order,
                    'urgency': 'high' if days_until_min_stock < 7 else 'medium' if days_until_min_stock < 14 else 'low'
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error checking stock status: {str(e)}")
            
    async def predict_restock_needs(self, days_ahead: int = 30) -> List[Dict]:
        """
        Predice necesidades de reabastecimiento para todos los reactivos activos.
        """
        try:
            # Obtener todos los reactivos activos
            reagents = await self._get_all_active_reagents()
            predictions = []
            
            for reagent in reagents:
                usage_history = await self._get_usage_history(reagent.id)
                predicted_usage = await self._predict_usage(usage_history)
                
                # Calcular stock proyectado
                projected_stock = reagent.current_stock - (predicted_usage['daily_usage'] * days_ahead)
                
                if projected_stock <= reagent.min_stock:
                    predictions.append({
                        'reagent_id': reagent.id,
                        'reagent_name': reagent.name,
                        'current_stock': reagent.current_stock,
                        'projected_stock': projected_stock,
                        'days_until_min': self._calculate_days_until_min_stock(
                            reagent.current_stock,
                            reagent.min_stock,
                            predicted_usage['daily_usage']
                        ),
                        'recommended_order': self._calculate_optimal_order(
                            reagent.current_stock,
                            reagent.optimal_stock,
                            predicted_usage['daily_usage'],
                            predicted_usage['trend']
                        ),
                        'supplier': reagent.supplier,
                        'last_order_date': reagent.last_order_date,
                        'priority': self._calculate_order_priority(
                            projected_stock,
                            reagent.min_stock,
                            reagent.expiration_date
                        )
                    })
                    
            return sorted(predictions, key=lambda x: x['priority'], reverse=True)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error predicting restock needs: {str(e)}")
            
    async def update_stock(self, reagent_id: int, quantity_change: float, transaction_type: str) -> Dict:
        """
        Actualiza el stock de un reactivo y registra el movimiento.
        """
        try:
            reagent = await self._get_reagent(reagent_id)
            
            # Validar la operación
            if transaction_type == 'consumption' and (reagent.current_stock - quantity_change) < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Stock insuficiente para la operación"
                )
                
            # Actualizar stock
            new_stock = reagent.current_stock + quantity_change if transaction_type == 'restock' \
                       else reagent.current_stock - quantity_change
                       
            # Registrar movimiento
            await self._record_stock_movement(
                reagent_id=reagent_id,
                quantity_change=quantity_change,
                transaction_type=transaction_type,
                new_stock=new_stock
            )
            
            # Verificar si se necesita generar alerta
            if new_stock <= reagent.min_stock:
                await self._create_stock_alert(reagent_id, new_stock)
                
            return {
                'reagent_id': reagent_id,
                'previous_stock': reagent.current_stock,
                'quantity_change': quantity_change,
                'new_stock': new_stock,
                'transaction_type': transaction_type,
                'timestamp': datetime.now(),
                'alert_generated': new_stock <= reagent.min_stock
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating stock: {str(e)}")
            
    async def _predict_usage(self, usage_history: List[Dict]) -> Dict:
        """
        Predice el uso futuro basado en el historial.
        """
        if not usage_history:
            return {'daily_usage': 0, 'trend': 'stable', 'confidence': 0}
            
        # Preparar datos para predicción
        dates = [(datetime.strptime(h['date'], '%Y-%m-%d') - datetime.now()).days 
                for h in usage_history]
        quantities = [h['quantity'] for h in usage_history]
        
        X = np.array(dates).reshape(-1, 1)
        y = np.array(quantities)
        
        # Entrenar modelo
        self.stock_predictor.fit(X, y)
        
        # Calcular tendencia
        slope = self.stock_predictor.coef_[0]
        trend = 'increasing' if slope > 0.1 else 'decreasing' if slope < -0.1 else 'stable'
        
        return {
            'daily_usage': float(np.mean(quantities)),
            'trend': trend,
            'confidence': float(self.stock_predictor.score(X, y))
        }
        
    def _calculate_days_until_min_stock(
        self,
        current_stock: float,
        min_stock: float,
        daily_usage: float
    ) -> int:
        """
        Calcula días hasta alcanzar el stock mínimo.
        """
        if daily_usage <= 0:
            return 999  # Valor alto para indicar que no hay consumo
            
        return int((current_stock - min_stock) / daily_usage)
        
    def _calculate_optimal_order(
        self,
        current_stock: float,
        optimal_stock: float,
        daily_usage: float,
        trend: str
    ) -> float:
        """
        Calcula la cantidad óptima a pedir.
        """
        base_order = optimal_stock - current_stock
        
        # Ajustar según tendencia
        if trend == 'increasing':
            base_order *= 1.2  # Aumentar 20% si el consumo está creciendo
        elif trend == 'decreasing':
            base_order *= 0.8  # Reducir 20% si el consumo está decreciendo
            
        return max(0, round(base_order, 2))
        
    def _determine_status(self, days_until_min: int, expiration_date: datetime) -> str:
        """
        Determina el estado del reactivo.
        """
        if days_until_min <= 0:
            return 'critical'
        elif days_until_min < 7:
            return 'warning'
        elif (expiration_date - datetime.now()).days < 30:
            return 'near_expiration'
        else:
            return 'ok'
            
    def _calculate_order_priority(
        self,
        projected_stock: float,
        min_stock: float,
        expiration_date: datetime
    ) -> float:
        """
        Calcula la prioridad de pedido (0-1).
        """
        stock_factor = max(0, min_stock - projected_stock) / min_stock
        days_to_expiration = (expiration_date - datetime.now()).days
        expiration_factor = 1 if days_to_expiration < 30 else 0
        
        return (stock_factor * 0.7) + (expiration_factor * 0.3)
        
    async def _get_reagent(self, reagent_id: int) -> Reagent:
        """
        Obtiene información de un reactivo.
        """
        # Implementar lógica de base de datos
        # Por ahora retornamos datos de ejemplo
        return Reagent(
            id=reagent_id,
            name="Reactivo Example",
            code="RE001",
            current_stock=100,
            unit="ml",
            min_stock=50,
            optimal_stock=200,
            price_per_unit=10.5,
            supplier="Supplier Inc",
            last_order_date=datetime.now() - timedelta(days=30),
            expiration_date=datetime.now() + timedelta(days=180),
            tests_per_unit=10,
            status="active"
        )
        
    async def _get_all_active_reagents(self) -> List[Reagent]:
        """
        Obtiene todos los reactivos activos.
        """
        # Implementar lógica de base de datos
        # Por ahora retornamos datos de ejemplo
        return [await self._get_reagent(1)]
        
    async def _get_usage_history(self, reagent_id: int) -> List[Dict]:
        """
        Obtiene historial de uso de un reactivo.
        """
        # Implementar lógica de base de datos
        # Por ahora retornamos datos de ejemplo
        return [
            {
                'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                'quantity': float(np.random.normal(10, 2))
            }
            for i in range(30)
        ]
        
    async def _record_stock_movement(
        self,
        reagent_id: int,
        quantity_change: float,
        transaction_type: str,
        new_stock: float
    ) -> None:
        """
        Registra un movimiento de stock.
        """
        # Implementar lógica de base de datos
        pass
        
    async def _create_stock_alert(self, reagent_id: int, current_stock: float) -> None:
        """
        Crea una alerta de stock bajo.
        """
        # Implementar lógica de alertas
        pass
