import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Helixa-Migration")

def run_migration():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        logger.error("SUPABASE_URL or SUPABASE_KEY not found in .env")
        return

    try:
        supabase: Client = create_client(url, key)
        
        # Note: Standard Supabase API keys (anon/public) cannot run ALTER TABLE.
        # This script serves as a guide and attempt.
        logger.info("Attempting to verify 'metadata' column in 'telemetry' table...")
        
        # We try to insert a dummy record with metadata to see if it fails
        test_data = {
            "sensor_id": "MIGRATION-TEST",
            "type": "system",
            "value": 0.0,
            "unit": "test",
            "metadata": {"test": True}
        }
        
        response = supabase.table("telemetry").insert(test_data).execute()
        logger.info("Migration check: 'metadata' column seems to exist and is working!")
        
    except Exception as e:
        if "column \"metadata\" of relation \"telemetry\" does not exist" in str(e) or "PGRST204" in str(e):
            logger.error("CRITICAL: The 'metadata' column is missing in Supabase.")
            logger.info("Please run the following SQL in your Supabase SQL Editor:")
            logger.info("\nALTER TABLE telemetry ADD COLUMN metadata JSONB;\n")
        else:
            logger.error(f"Migration check failed: {str(e)}")

if __name__ == "__main__":
    run_migration()
