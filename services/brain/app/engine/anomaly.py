import logging
import numpy as np
from typing import Dict, List

logger = logging.getLogger("Helixa-Anomaly")

class AnomalyEngine:
    """
    Analyzes telemetry streams to detect deviations from normal behavior.
    """
    
    def __init__(self):
        # Stores recent history for each sensor to calculate moving averages/std
        self.history: Dict[str, List[float]] = {}
        self.window_size = 20

    def analyze(self, sensor_id: str, value: float) -> bool:
        """
        Detects if a value is an anomaly based on Z-score.
        Returns True if an anomaly is detected.
        """
        if sensor_id not in self.history:
            self.history[sensor_id] = []
        
        self.history[sensor_id].append(value)
        
        # Keep only the last N readings
        if len(self.history[sensor_id]) > self.window_size:
            self.history[sensor_id].pop(0)
            
        # Need at least 5 readings to start detecting anomalies
        if len(self.history[sensor_id]) < 5:
            return False
            
        data = np.array(self.history[sensor_id])
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return False
            
        z_score = abs((value - mean) / std)
        
        # Threshold of 3 standard deviations
        is_anomaly = z_score > 3.0
        
        if is_anomaly:
            logger.error(f"ANOMALY DETECTED: Sensor {sensor_id} value {value} (Z-Score: {z_score:.2f})")
            
        return is_anomaly
