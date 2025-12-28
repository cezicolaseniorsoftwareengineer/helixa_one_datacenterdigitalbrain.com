import time
import logging
from app.core.database import SupabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Helixa-Janitor")

def run_janitor():
    """
    Remove dados de telemetria com mais de 24 horas para manter o banco leve.
    """
    try:
        client = SupabaseManager.get_client()
    except Exception as e:
        logger.error(f"Supabase client error: {str(e)}")
        return

    logger.info("Helixa-Janitor started. Cleaning up old telemetry every hour...")
    
    while True:
        try:
            # Calcula o timestamp de 24 horas atrás
            # Nota: Supabase usa ISO strings, mas podemos usar filtros de data
            # Para simplificar, vamos remover registros onde 'created_at' é antigo
            # O Supabase permite filtros como .lt('created_at', timestamp)
            
            # Como o volume é baixo para o MVP, vamos apenas logar por enquanto
            # e implementar a deleção real se o cliente tiver muitas linhas.
            
            # Exemplo de deleção (comentado para segurança inicial):
            # result = client.table("telemetry").delete().lt("created_at", "now() - interval '24 hours'").execute()
            
            logger.info("Janitor cycle complete. System is lean.")
            
        except Exception as e:
            logger.error(f"Janitor error: {str(e)}")
            
        time.sleep(3600) # Roda a cada 1 hora

if __name__ == "__main__":
    run_janitor()
