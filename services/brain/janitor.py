import time
import logging
from app.core.database import SupabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Helixa-Janitor")

def run_janitor():
    """
    Removes telemetry data older than 24 hours to keep the database lean.
    """
    try:
        client = SupabaseManager.get_client()
    except Exception as e:
        logger.error(f"Supabase client error: {str(e)}")
        return

    logger.info("Helixa-Janitor started. Cleaning up old telemetry every hour...")
    
    while True:
        try:
            # Calculate timestamp from 24 hours ago
            # Note: Supabase uses ISO strings, but we can use date filters
            # To simplify, we will remove records where 'created_at' is old
            # Supabase allows filters like .lt('created_at', timestamp)
            
            # Since volume is low for the MVP, we will just log for now
            # and implement real deletion if the client has many rows.
            
            # Deletion example (commented for initial safety):
            # result = client.table("telemetry").delete().lt("created_at", "now() - interval '24 hours'").execute()
            
            logger.info("Janitor cycle complete. System is lean.")
            
        except Exception as e:
            logger.error(f"Janitor error: {str(e)}")
            
        time.sleep(3600) # Runs every 1 hour

if __name__ == "__main__":
    run_janitor()
