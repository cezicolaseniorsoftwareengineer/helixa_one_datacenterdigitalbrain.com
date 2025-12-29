from fastapi import APIRouter, Body, HTTPException
from app.schemas.telemetry import TelemetryData
from app.core.safety import SafetyController
from app.core.database import SupabaseManager
from app.engine.anomaly import IntelligenceEngine
from prometheus_client import Counter, Gauge
import logging

logger = logging.getLogger("Helixa-API")
router = APIRouter()
intelligence_suite = IntelligenceEngine()

# Metrics
INGESTION_COUNT = Counter('telemetry_ingestion_total', 'Total telemetry packets ingested')
ANOMALY_COUNT = Counter('anomaly_detection_total', 'Total anomalies detected', ['sensor_id'])
SENSOR_VALUE = Gauge('sensor_reading', 'Current sensor reading', ['sensor_id', 'type'])

@router.post("/telemetry")
async def receive_telemetry(data: TelemetryData):
    """Ingests and analyzes telemetry data with predictive intelligence."""
    try:
        INGESTION_COUNT.inc()
        
        results = []
        safety_violations = 0
        
        device_type = data.metadata.get("device_type", "datacenter") if data.metadata else "datacenter"
        
        for sensor in data.sensors:
            sensor_id = sensor.id
            sensor_type = sensor.type
            
            # 1. Safety Validation (CEZI COLA: Risk)
            is_safe = SafetyController.validate_sensor_reading(sensor_type, sensor.value, device_type)
            if not is_safe:
                safety_violations += 1
                
            # 2. Intelligence Analysis (CEZI COLA: Intelligence)
            limits = SafetyController.get_limits(sensor_type, device_type)
            analysis = intelligence_suite.analyze(sensor_id, sensor.value, sensor_type, limits)
            
            if analysis["is_anomaly"]:
                ANOMALY_COUNT.labels(sensor_id=sensor_id).inc()
                
            # 3. Mitigation Strategy (CEZI COLA: Risk)
            recommended_action = SafetyController.get_mitigation_action(sensor_type, sensor.value, analysis, device_type)

            # 4. Update Metrics (CEZI COLA: Observability)
            SENSOR_VALUE.labels(sensor_id=sensor_id, type=sensor_type).set(sensor.value)

            # 5. Persist to Memory (CEZI COLA: Persistence)
            try:
                # Enrich metadata with intelligence results and actions
                enriched_metadata = {
                    **(data.metadata or {}),
                    "intelligence": analysis,
                    "recommended_action": recommended_action,
                    "is_safe": is_safe
                }
                
                SupabaseManager.save_telemetry(
                    sensor_id=sensor_id,
                    sensor_type=sensor_type,
                    value=sensor.value,
                    unit=sensor.unit,
                    metadata=enriched_metadata
                )
                
                results.append({
                    "sensor_id": sensor_id,
                    "analysis": analysis,
                    "action": recommended_action
                })
                
            except Exception as e:
                logger.error(f"Database persistence failed: {str(e)}")
            
        return {
            "status": "processed",
            "sensors_count": len(data.sensors),
            "safety_violations": safety_violations,
            "intelligence_report": results
        }
    except Exception as e:
        import traceback
        logger.error(f"CRITICAL ERROR IN TELEMETRY INGESTION: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Intelligence Error: {str(e)}")
