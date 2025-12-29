import logging

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
    def validate_sensor_reading(cls, sensor_type: str, value: float, device_type: str = "datacenter") -> bool:
        """Validates if a sensor reading is within safe physical bounds."""
        base_limits = cls.HARDWARE_LIMITS if device_type in ["notebook", "pc"] else cls.DEFAULT_LIMITS
        limits = base_limits.get(sensor_type)
        
        if not limits:
            return True  # No limits defined for this type
        
        is_safe = limits["min"] <= value <= limits["max"]
        
        if not is_safe:
            logger.warning(f"SAFETY VIOLATION [{device_type}]: {sensor_type} value {value} is out of bounds ({limits['min']}-{limits['max']})")
            
        return is_safe

    @classmethod
    def validate_action(cls, action_type: str, params: dict) -> bool:
        """Validates if a system-proposed action is safe to execute."""
        # Placeholder for future action validation logic
        return True
