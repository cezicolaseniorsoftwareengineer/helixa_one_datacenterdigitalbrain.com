import uvicorn
import os
import sys
import threading
from janitor import run_janitor

# Add the current directory to sys.path to ensure 'app' is findable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🧠 HELIXA-ONE BRAIN: Starting Intelligence Engine...")
    
    # Start Janitor in background
    janitor_thread = threading.Thread(target=run_janitor, daemon=True)
    janitor_thread.start()
    print("🧹 HELIXA-ONE JANITOR: Maintenance service active.")
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
