from typing import List, Dict, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException
from pydantic import BaseModel

class TestCost(BaseModel):
    test_id: int
    name: str
    base_cost: Decimal
    reagent_cost: Decimal
    labor_cost: Decimal
    overhead_cost: Decimal
    profit_margin: float
    total_price: Decimal
    insurance_coverage: Optional[Dict[str, float]]
    
class OrderCost(BaseModel):
    order_id: int
    patient_id: int
    tests: List[TestCost]
    subtotal: Decimal
    discounts: Decimal
    taxes: Decimal
    total: Decimal
    insurance_id: Optional[int]
    payment_status: str
    created_at: datetime

class CostManagement:
    def __init__(self):
        self.tax_rate = Decimal('0.21')  # 21% IVA
        
    async def calculate_test_price(self, test_id: int) -> TestCost:
        """
        Calcula el precio de un análisis incluyendo todos los costos.
        """
        try:
            # Obtener información del test
            test_info = await self._get_test_info(test_id)
            reagent_costs = await self._calculate_reagent_costs(test_id)
            
            # Calcular costos
            base_cost = test_info['base_cost']
            labor_cost = test_info['labor_cost']
            overhead_cost = test_info['overhead_cost']
            
            # Calcular precio total
            subtotal = base_cost + reagent_costs + labor_cost + overhead_cost
            profit = subtotal * Decimal(str(test_info['profit_margin']))
            total_price = subtotal + profit
            
            return TestCost(
                test_id=test_id,
                name=test_info['name'],
                base_cost=base_cost,
                reagent_cost=reagent_costs,
                labor_cost=labor_cost,
                overhead_cost=overhead_cost,
                profit_margin=test_info['profit_margin'],
                total_price=total_price,
                insurance_coverage=test_info.get('insurance_coverage')
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculando precio: {str(e)}")
            
    async def calculate_order_cost(
        self,
        patient_id: int,
        test_ids: List[int],
        insurance_id: Optional[int] = None
    ) -> OrderCost:
        """
        Calcula el costo total de una orden de análisis.
        """
        try:
            # Calcular costos individuales
            tests_costs = []
            subtotal = Decimal('0')
            
            for test_id in test_ids:
                test_cost = await self.calculate_test_price(test_id)
                tests_costs.append(test_cost)
                subtotal += test_cost.total_price
                
            # Calcular descuentos por seguro si aplica
            discounts = await self._calculate_insurance_discount(
                insurance_id,
                tests_costs
            ) if insurance_id else Decimal('0')
                
            # Calcular impuestos
            taxable_amount = subtotal - discounts
            taxes = taxable_amount * self.tax_rate
            
            # Calcular total
            total = taxable_amount + taxes
            
            return OrderCost(
                order_id=await self._generate_order_id(),
                patient_id=patient_id,
                tests=tests_costs,
                subtotal=subtotal,
                discounts=discounts,
                taxes=taxes,
                total=total,
                insurance_id=insurance_id,
                payment_status='pending',
                created_at=datetime.now()
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculando orden: {str(e)}")
            
    async def generate_financial_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str = 'detailed'
    ) -> Dict:
        """
        Genera un informe financiero para el período especificado.
        """
        try:
            # Obtener órdenes del período
            orders = await self._get_orders_by_date_range(start_date, end_date)
            
            # Calcular métricas básicas
            total_revenue = sum(order.total for order in orders)
            total_costs = sum(
                sum(test.base_cost + test.reagent_cost + test.labor_cost + test.overhead_cost
                    for test in order.tests)
                for order in orders
            )
            total_profit = total_revenue - total_costs
            
            report = {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'summary': {
                    'total_orders': len(orders),
                    'total_revenue': float(total_revenue),
                    'total_costs': float(total_costs),
                    'total_profit': float(total_profit),
                    'profit_margin': float(total_profit / total_revenue) if total_revenue > 0 else 0
                }
            }
            
            if report_type == 'detailed':
                # Análisis por tipo de test
                test_analysis = await self._analyze_tests_performance(orders)
                report['test_analysis'] = test_analysis
                
                # Análisis por método de pago
                payment_analysis = await self._analyze_payment_methods(orders)
                report['payment_analysis'] = payment_analysis
                
                # Análisis de seguros
                insurance_analysis = await self._analyze_insurance_coverage(orders)
                report['insurance_analysis'] = insurance_analysis
                
                # Tendencias diarias
                daily_trends = await self._calculate_daily_trends(orders)
                report['daily_trends'] = daily_trends
                
            return report
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")
            
    async def get_daily_revenue(self, date: Optional[datetime] = None) -> Dict:
        """
        Obtiene el informe de ingresos del día.
        """
        try:
            target_date = date or datetime.now()
            start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            # Obtener órdenes del día
            orders = await self._get_orders_by_date_range(start_date, end_date)
            
            # Calcular métricas
            total_revenue = sum(order.total for order in orders)
            total_tests = sum(len(order.tests) for order in orders)
            
            return {
                'date': target_date.date(),
                'metrics': {
                    'total_orders': len(orders),
                    'total_tests': total_tests,
                    'total_revenue': float(total_revenue),
                    'average_order_value': float(total_revenue / len(orders)) if orders else 0
                },
                'payment_status': {
                    'paid': sum(1 for order in orders if order.payment_status == 'paid'),
                    'pending': sum(1 for order in orders if order.payment_status == 'pending'),
                    'overdue': sum(1 for order in orders if order.payment_status == 'overdue')
                },
                'hourly_distribution': await self._calculate_hourly_distribution(orders)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error obteniendo ingresos diarios: {str(e)}")
            
    async def _get_test_info(self, test_id: int) -> Dict:
        """
        Obtiene información de costos de un test.
        """
        # Implementar lógica de base de datos
        # Por ahora retornamos datos de ejemplo
        return {
            'name': 'Test Example',
            'base_cost': Decimal('100.00'),
            'labor_cost': Decimal('50.00'),
            'overhead_cost': Decimal('25.00'),
            'profit_margin': 0.3,
            'insurance_coverage': {
                'basic': 0.6,
                'premium': 0.8
            }
        }
        
    async def _calculate_reagent_costs(self, test_id: int) -> Decimal:
        """
        Calcula el costo de reactivos para un test.
        """
        # Implementar lógica de cálculo de reactivos
        # Por ahora retornamos un valor de ejemplo
        return Decimal('75.00')
        
    async def _calculate_insurance_discount(
        self,
        insurance_id: int,
        tests: List[TestCost]
    ) -> Decimal:
        """
        Calcula descuento por seguro médico.
        """
        # Implementar lógica de descuentos
        # Por ahora retornamos un descuento de ejemplo
        return sum(test.total_price * Decimal('0.5') for test in tests)
        
    async def _get_orders_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[OrderCost]:
        """
        Obtiene órdenes en un rango de fechas.
        """
        # Implementar lógica de base de datos
        # Por ahora retornamos datos de ejemplo
        return [
            OrderCost(
                order_id=1,
                patient_id=1,
                tests=[await self.calculate_test_price(1)],
                subtotal=Decimal('250.00'),
                discounts=Decimal('50.00'),
                taxes=Decimal('42.00'),
                total=Decimal('242.00'),
                insurance_id=None,
                payment_status='paid',
                created_at=datetime.now()
            )
        ]
        
    async def _analyze_tests_performance(self, orders: List[OrderCost]) -> List[Dict]:
        """
        Analiza el rendimiento financiero por tipo de test.
        """
        performance = {}
        
        for order in orders:
            for test in order.tests:
                if test.test_id not in performance:
                    performance[test.test_id] = {
                        'test_id': test.test_id,
                        'name': test.name,
                        'total_revenue': Decimal('0'),
                        'total_cost': Decimal('0'),
                        'count': 0
                    }
                    
                perf = performance[test.test_id]
                perf['total_revenue'] += test.total_price
                perf['total_cost'] += (
                    test.base_cost + test.reagent_cost +
                    test.labor_cost + test.overhead_cost
                )
                perf['count'] += 1
                
        # Calcular métricas finales
        return [
            {
                **perf,
                'average_revenue': float(perf['total_revenue'] / perf['count']),
                'profit': float(perf['total_revenue'] - perf['total_cost']),
                'profit_margin': float(
                    (perf['total_revenue'] - perf['total_cost']) / perf['total_revenue']
                ) if perf['total_revenue'] > 0 else 0
            }
            for perf in performance.values()
        ]
        
    async def _analyze_payment_methods(self, orders: List[OrderCost]) -> Dict:
        """
        Analiza la distribución de métodos de pago.
        """
        # Implementar análisis de pagos
        return {
            'cash': {'count': 10, 'total': 1000.0},
            'credit_card': {'count': 15, 'total': 1500.0},
            'insurance': {'count': 20, 'total': 2000.0}
        }
        
    async def _analyze_insurance_coverage(self, orders: List[OrderCost]) -> Dict:
        """
        Analiza la cobertura de seguros médicos.
        """
        # Implementar análisis de seguros
        return {
            'total_orders_with_insurance': 20,
            'total_coverage_amount': 2000.0,
            'average_coverage': 60.0,
            'insurance_distribution': {
                'basic': {'count': 10, 'total': 800.0},
                'premium': {'count': 10, 'total': 1200.0}
            }
        }
        
    async def _calculate_daily_trends(self, orders: List[OrderCost]) -> List[Dict]:
        """
        Calcula tendencias diarias de ingresos.
        """
        # Implementar cálculo de tendencias
        return [
            {
                'date': datetime.now().date(),
                'total_revenue': 1000.0,
                'order_count': 10,
                'average_order_value': 100.0
            }
        ]
        
    async def _calculate_hourly_distribution(self, orders: List[OrderCost]) -> Dict:
        """
        Calcula la distribución de ingresos por hora.
        """
        distribution = {str(hour): 0 for hour in range(24)}
        
        for order in orders:
            hour = str(order.created_at.hour)
            distribution[hour] += float(order.total)
            
        return distribution
        
    async def _generate_order_id(self) -> int:
        """
        Genera un nuevo ID de orden.
        """
        # Implementar generación de ID
        return 1
