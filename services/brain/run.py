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
    
    # In production, host should be 0.0.0.0
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run("app.main:app", host=host, port=port, reload=False, log_level="info")
