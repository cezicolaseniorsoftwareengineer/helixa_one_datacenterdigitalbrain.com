from fastapi import APIRouter, Body, HTTPException
from app.schemas.telemetry import TelemetryData
from app.core.safety import SafetyController
from app.core.database import SupabaseManager
from app.engine.anomaly import AnomalyEngine
from prometheus_client import Counter, Gauge
import logging

logger = logging.getLogger("Helixa-API")
router = APIRouter()
anomaly_engine = AnomalyEngine()

# Metrics
INGESTION_COUNT = Counter('telemetry_ingestion_total', 'Total telemetry packets ingested')
ANOMALY_COUNT = Counter('anomaly_detection_total', 'Total anomalies detected', ['sensor_id'])
SENSOR_VALUE = Gauge('sensor_reading', 'Current sensor reading', ['sensor_id', 'type'])

@router.post("/telemetry")
async def receive_telemetry(data: TelemetryData):
    """Ingests and analyzes telemetry data."""
    INGESTION_COUNT.inc()
    
    anomalies_found = 0
    safety_violations = 0
    
    device_type = data.metadata.get("device_type", "datacenter") if data.metadata else "datacenter"
    
    for sensor in data.sensors:
        sensor_id = sensor.id
        sensor_type = sensor.type
        
        # 1. Safety Validation (CEZI COLA: Risk)
        if not SafetyController.validate_sensor_reading(sensor_type, sensor.value, device_type):
            safety_violations += 1
            
        # 2. Anomaly Detection (CEZI COLA: Intelligence)
        if anomaly_engine.analyze(sensor_id, sensor.value):
            anomalies_found += 1
            ANOMALY_COUNT.labels(sensor_id=sensor_id).inc()
            
        # 3. Update Metrics (CEZI COLA: Observability)
        SENSOR_VALUE.labels(sensor_id=sensor_id, type=sensor_type).set(sensor.value)

        # 4. Persist to Memory (CEZI COLA: Persistence)
        try:
            SupabaseManager.save_telemetry(
                sensor_id=sensor_id,
                sensor_type=sensor_type,
                value=sensor.value,
                unit=sensor.unit,
                metadata=data.metadata
            )
        except Exception as e:
            logger.error(f"Database persistence failed: {str(e)}")
        
    return {
        "status": "processed",
        "sensors_count": len(data.sensors),
        "anomalies": anomalies_found,
        "safety_violations": safety_violations
    }
