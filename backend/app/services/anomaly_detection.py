import numpy as np
from typing import Dict, Any
from sklearn.ensemble import IsolationForest
import pandas as pd

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.historical_data = {}  # Cache for historical data per test type

    async def is_statistical_anomaly(self, value: float, test_type: str) -> bool:
        """
        Detect if a value is an anomaly using statistical methods and machine learning
        """
        # First check: Basic reference range
        if test_type in self.historical_data:
            data = self.historical_data[test_type]
            mean = np.mean(data)
            std = np.std(data)
            z_score = abs((value - mean) / std)
            if z_score > 3:  # More than 3 standard deviations
                return True

            # Reshape for isolation forest
            X = np.array(data + [value]).reshape(-1, 1)
            predictions = self.model.fit_predict(X)
            if predictions[-1] == -1:  # Isolation Forest marks anomalies as -1
                return True

        return False

async def detect_anomalies(value: float, reference_range: Dict[str, Any], test_type: str) -> bool:
    """
    Main function to detect anomalies in test results
    """
    # Basic range check
    if 'min' in reference_range and value < reference_range['min']:
        return True
    if 'max' in reference_range and value > reference_range['max']:
        return True

    # Initialize detector if needed
    detector = AnomalyDetector()
    
    # Statistical anomaly detection
    is_anomaly = await detector.is_statistical_anomaly(value, test_type)
    
    return is_anomaly

# Additional AI features can be added here:
# 1. Pattern recognition across multiple tests
# 2. Time series analysis for patient history
# 3. Correlation analysis between different test types
# 4. Machine learning models for specific conditions
