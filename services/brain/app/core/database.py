import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseManager:
    """
    Manages connection and operations with Supabase.
    """
    _client: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
            if not url or not key:
                logger.error("SUPABASE_URL or SUPABASE_KEY not found in environment")
                raise ValueError("Supabase credentials missing")
            cls._client = create_client(url, key)
        return cls._client

    @classmethod
    def save_telemetry(cls, sensor_id: str, sensor_type: str, value: float, unit: str, metadata: dict = None):
        """
        Saves a single sensor reading to the 'telemetry' table.
        """
        client = cls.get_client()
        data = {
            "sensor_id": sensor_id,
            "type": sensor_type,
            "value": value,
            "unit": unit,
            "metadata": metadata
        }
        # Note: In a production environment, we would use batch inserts or a queue
        try:
            client.table("telemetry").insert(data).execute()
        except Exception as e:
            # Log error but don't break the ingestion flow (CEZI COLA: Fail-Safe)
            import logging
            logging.getLogger("Helixa-Database").error(f"Failed to save telemetry to Supabase: {str(e)}")
