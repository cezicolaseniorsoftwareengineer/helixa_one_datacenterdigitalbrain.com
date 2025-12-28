import time
import random
import requests
import logging
import os
import psutil
import subprocess
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

def get_hardware_metrics():
    """Captures real hardware metrics from the host machine."""
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    
    # Note: Temperature access via psutil is platform-dependent.
    # On Windows, it often requires administrative privileges or specific drivers.
    # We will map CPU usage to 'Load' and RAM to 'Thermal' for simulation purposes if sensors are unavailable.
    return [
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

def detect_device_type():
    """Detects if the current machine is a Notebook, PC, or Server with high sensitivity."""
    # 1. Check for battery (Primary Notebook indicator)
    has_battery = psutil.sensors_battery() is not None
    
    # 2. Check Chassis Type via WMIC (Windows specific, very reliable)
    is_laptop_chassis = False
    if os.name == 'nt':
        try:
            # ChassisTypes 8, 9, 10, 11, 12, 14 are all laptop/portable forms
            output = subprocess.check_output('wmic chassis get chassistypes', shell=True).decode()
            # Look for any of the laptop codes in the output
            for code in ['8', '9', '10', '11', '12', '14']:
                if code in output:
                    is_laptop_chassis = True
                    break
        except:
            pass

    # 3. Check CPU/RAM (Server/DataCenter indicator)
    cpu_count = psutil.cpu_count(logical=True)
    total_ram_gb = psutil.virtual_memory().total / (1024**3)
    
    if has_battery or is_laptop_chassis:
        logger.info(f"Device detected as NOTEBOOK (Battery: {has_battery}, Chassis: {is_laptop_chassis})")
        return "notebook"
    elif cpu_count > 32 or total_ram_gb > 64:
        logger.info(f"Device detected as DATACENTER (CPUs: {cpu_count}, RAM: {total_ram_gb:.1f}GB)")
        return "datacenter"
    else:
        logger.info("Device detected as PC (Desktop)")
        return "pc"

def generate_telemetry():
    """Simulates or captures data center sensor readings."""
    sensors = []
    device_type = detect_device_type()
    
    if HARDWARE_MODE:
        sensors = get_hardware_metrics()
        # Add a simulated chiller flow to keep the dashboard consistent
        sensors.append({
            "id": "CHILLER-01-FLOW",
            "type": "flow",
            "value": round(random.uniform(100.0, 150.0), 2),
            "unit": "L/m"
        })
    else:
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
    
    while True:
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
        
        time.sleep(5)  # Send data every 5 seconds

if __name__ == "__main__":
    stream_data()
