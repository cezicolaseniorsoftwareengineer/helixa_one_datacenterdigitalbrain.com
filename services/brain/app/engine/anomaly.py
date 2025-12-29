import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("Helixa-Intelligence")

class IntelligenceEngine:
    """
    Advanced intelligence engine for anomaly detection and predictive maintenance.
    Uses statistical analysis and trend forecasting to anticipate failures.
    """
    
    def __init__(self):
        # Stores recent history for each sensor: [(timestamp, value), ...]
        self.history: Dict[str, List[Tuple[float, float]]] = {}
        self.window_size = 30
        
        # Thresholds for maintenance alerts (e.g., 85% of safety limit)
        self.maintenance_threshold_factor = 0.85

    def analyze(self, sensor_id: str, value: float, sensor_type: str, limits: Dict[str, float]) -> Dict:
        """
        Performs a full intelligence sweep: Anomaly Detection + Predictive Analysis.
        """
        now = datetime.now().timestamp()
        
        if sensor_id not in self.history:
            self.history[sensor_id] = []
        
        self.history[sensor_id].append((now, value))
        
        if len(self.history[sensor_id]) > self.window_size:
            self.history[sensor_id].pop(0)
            
        # 1. Anomaly Detection (Z-Score)
        is_anomaly, z_score = self._detect_anomaly(sensor_id, value)
        
        # 2. Predictive Maintenance (Trend Analysis)
        prediction = self._predict_trend(sensor_id, sensor_type, limits)
        
        return {
            "is_anomaly": is_anomaly,
            "z_score": float(round(z_score, 2)),
            "prediction": prediction
        }

    def _detect_anomaly(self, sensor_id: str, value: float) -> Tuple[bool, float]:
        data = np.array([v for _, v in self.history[sensor_id]])
        if len(data) < 5:
            return False, 0.0
            
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return False, 0.0
            
        z_score = abs((value - mean) / std)
        is_anomaly = bool(z_score > 3.0)
        
        if is_anomaly:
            logger.warning(f"ANOMALY: {sensor_id} value {value} (Z:{z_score:.2f})")
            
        return is_anomaly, float(z_score)

    def _predict_trend(self, sensor_id: str, sensor_type: str, limits: Optional[Dict[str, float]]) -> Dict:
        """
        Calculates the slope of the data to predict when it will hit critical limits.
        """
        history = self.history[sensor_id]
        if len(history) < 10 or not limits:
            return {"status": "stable", "ttf_minutes": None}

        # Linear Regression: y = mx + b
        x = np.array([t for t, _ in history])
        y = np.array([v for _, v in history])
        
        # Normalize x to prevent large numbers
        x_norm = x - x[0]
        
        try:
            slope, intercept = np.polyfit(x_norm, y, 1)
        except Exception:
            return {"status": "stable", "ttf_minutes": None}
        
        # If slope is positive and we have a max limit
        if slope > 0 and "max" in limits:
            critical_val = limits["max"]
            maintenance_val = critical_val * self.maintenance_threshold_factor
            
            # Time to reach maintenance threshold
            if y[-1] < maintenance_val:
                seconds_to_maint = (maintenance_val - y[-1]) / slope
                status = "optimal" if seconds_to_maint > 3600 else "maintenance_required"
                return {
                    "status": status,
                    "ttf_minutes": float(round(seconds_to_maint / 60, 1)),
                    "recommendation": "Check cooling systems" if sensor_type == "temperature" else "Balance load"
                }
            else:
                return {
                    "status": "critical_approaching",
                    "ttf_minutes": float(round((critical_val - y[-1]) / slope / 60, 1)),
                    "recommendation": "IMMEDIATE ACTION REQUIRED"
                }
                
        return {"status": "stable", "ttf_minutes": None}
