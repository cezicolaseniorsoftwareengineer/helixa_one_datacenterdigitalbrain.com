import time
import random
import requests
import logging
import os
import psutil
import subprocess
import signal
from threading import Event
from dotenv import load_dotenv

load_dotenv()

# Configure logging for observability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Helixa-Nerves")

BRAIN_API_URL = os.getenv("BRAIN_API_URL", "http://localhost:8000/telemetry")
HARDWARE_MODE = os.getenv("HARDWARE_MODE", "false").lower() == "true"
shutdown_event = Event()


def handle_shutdown(signum, frame):
    logger.info(f"Received signal {signum}. Shutting down telemetry stream gracefully.")
    shutdown_event.set()

def get_hardware_metrics():
    """Captures real hardware metrics from the host machine."""
    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram_usage = psutil.virtual_memory().percent
    
    metrics = [
        {
            "id": "HOST-CPU-LOAD",
            "type": "power",
            "value": cpu_usage,
            "unit": "%"
        },
        {
            "id": "HOST-RAM-USAGE",
            "type": "temperature",
            "value": ram_usage,
            "unit": "%"
        }
    ]
    
    # Try to get battery if available
    battery = psutil.sensors_battery()
    if battery:
        metrics.append({
            "id": "HOST-BATTERY",
            "type": "power",
            "value": battery.percent,
            "unit": "%"
        })
        
    return metrics

def generate_telemetry():
    """Simulates or captures data center sensor readings."""
    device_type = detect_device_type()
    
    if HARDWARE_MODE:
        sensors = get_hardware_metrics()
    else:
        # Enhanced simulation with trends
        # We use a global counter to simulate a slow rise in temperature
        if not hasattr(generate_telemetry, "counter"):
            generate_telemetry.counter = 0
        generate_telemetry.counter += 0.1
        
        base_temp = 22.0 + (generate_telemetry.counter % 10) # Oscillates between 22 and 32
        
        sensors = [
            {
                "id": "RACK-A01-TEMP",
                "type": "temperature",
                "value": round(base_temp + random.uniform(-0.5, 0.5), 2),
                "unit": "C"
            },
            {
                "id": "PDU-01-LOAD",
                "type": "power",
                "value": round(random.uniform(40.0, 60.0), 2),
                "unit": "kW"
            },
            {
                "id": "COOLING-UNIT-01",
                "type": "flow",
                "value": round(random.uniform(100.0, 120.0), 2),
                "unit": "L/m"
            }
        ]

    return {
        "timestamp": time.time(),
        "sensors": sensors,
        "metadata": {
            "site": "DC-ALPHA-01",
            "version": "0.3.0",
            "mode": "hardware" if HARDWARE_MODE else "simulated",
            "device_type": device_type
        }
    }
        sensors = [
            {
                "id": "RACK-A01-TEMP",
                "type": "temperature",
                "value": round(random.uniform(20.0, 26.0), 2),
                "unit": "C"
            },
            {
                "id": "PDU-01-LOAD",
                "type": "power",
                "value": round(random.uniform(5.0, 12.0), 2),
                "unit": "kW"
            },
            {
                "id": "CHILLER-01-FLOW",
                "type": "flow",
                "value": round(random.uniform(100.0, 150.0), 2),
                "unit": "L/m"
            }
        ]

    return {
        "timestamp": time.time(),
        "sensors": sensors,
        "metadata": {
            "site": "DC-ALPHA-01",
            "version": "0.2.0",
            "mode": "hardware" if HARDWARE_MODE else "simulated",
            "device_type": device_type
        }
    }

def stream_data():
    """Streams telemetry to the Brain service."""
    logger.info(f"Starting telemetry stream to {BRAIN_API_URL}")
    
    while not shutdown_event.is_set():
        data = generate_telemetry()
        try:
            # In a real scenario, we would use a message broker like Kafka.
            # For this phase, we use direct HTTP ingestion.
            response = requests.post(BRAIN_API_URL, json=data, timeout=2)
            if response.status_code == 200:
                logger.info(f"Telemetry sent successfully: {len(data['sensors'])} sensors reported.")
            else:
                logger.error(f"Failed to send telemetry. Status: {response.status_code}")
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
        
        shutdown_event.wait(5)  # Send data every 5 seconds or exit on shutdown

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        stream_data()
    finally:
        logger.info("Telemetry stream halted.")
