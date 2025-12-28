from pydantic import BaseModel, Field
from typing import List, Optional

class SensorReading(BaseModel):
    id: str
    type: str
    value: float
    unit: str

class TelemetryData(BaseModel):
    timestamp: float
    sensors: List[SensorReading]
    metadata: Optional[dict] = Field(default_factory=dict)
