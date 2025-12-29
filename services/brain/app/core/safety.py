import logging
from typing import Optional

logger = logging.getLogger("Helixa-Safety")

class SafetyController:
    """
    The Safety Controller is the final gatekeeper for all system decisions.
    It ensures that no action or metric violates physical safety boundaries.
    """
    
    # Physical limits adjusted by device type
    DEFAULT_LIMITS = {
        "temperature": {"min": 15.0, "max": 32.0},  # Celsius (Data Center)
        "power": {"min": 0.0, "max": 500.0},       # kW per PDU
        "humidity": {"min": 20.0, "max": 80.0}     # %
    }

    HARDWARE_LIMITS = {
        "temperature": {"min": 0.0, "max": 100.0}, # % or Celsius (PC/Notebook)
        "power": {"min": 0.0, "max": 100.0},       # % Load
        "humidity": {"min": 0.0, "max": 100.0}
    }

    @classmethod
    def get_limits(cls, sensor_type: str, device_type: str = "datacenter") -> dict:
        """Returns the safety limits for a specific sensor and device type."""
        dt = device_type.lower()
        base_limits = cls.HARDWARE_LIMITS if any(k in dt for k in ["notebook", "pc", "laptop"]) else cls.DEFAULT_LIMITS
        return base_limits.get(sensor_type, {})

    @classmethod
    def validate_sensor_reading(cls, sensor_type: str, value: float, device_type: str = "datacenter") -> bool:
        """Validates if a sensor reading is within safe physical bounds."""
        dt = device_type.lower()
        base_limits = cls.HARDWARE_LIMITS if any(k in dt for k in ["notebook", "pc", "laptop"]) else cls.DEFAULT_LIMITS
        limits = base_limits.get(sensor_type)
        
        if not limits:
            return True  # No limits defined for this type
        
        is_safe = limits["min"] <= value <= limits["max"]
        
        if not is_safe:
            logger.warning(f"SAFETY VIOLATION [{device_type}]: {sensor_type} value {value} is out of bounds ({limits['min']}-{limits['max']})")
            
        return is_safe

    @classmethod
    def get_mitigation_action(cls, sensor_type: str, value: float, analysis: dict, device_type: str) -> Optional[dict]:
        """
        Determines the best autonomous action to mitigate a risk before it becomes critical.
        (CEZI COLA: Risk & Architecture)
        """
        prediction = analysis.get("prediction", {})
        status = prediction.get("status")
        
        if status == "stable" and not analysis.get("is_anomaly"):
            return None

        # Mitigation Logic based on device and sensor
        if sensor_type == "temperature":
            if status == "critical_approaching" or value > cls.get_limits("temperature", device_type).get("max", 100) * 0.9:
                return {
                    "action": "INCREASE_COOLING",
                    "intensity": "HIGH",
                    "target": "FAN_CONTROLLER",
                    "reason": "Thermal runaway predicted"
                }
            elif status == "maintenance_required":
                return {
                    "action": "OPTIMIZE_AIRFLOW",
                    "intensity": "MEDIUM",
                    "target": "HVAC_SYSTEM",
                    "reason": "Rising thermal trend detected"
                }

        if sensor_type == "power":
            if status == "critical_approaching":
                return {
                    "action": "SHED_LOAD",
                    "intensity": "CRITICAL",
                    "target": "NON_ESSENTIAL_RACKS",
                    "reason": "Power capacity limit imminent"
                }
        
        return None

    @classmethod
    def validate_action(cls, action_type: str, params: dict) -> bool:
        """Validates if a system-proposed action is safe to execute."""
        # Placeholder for future action validation logic
        return True
