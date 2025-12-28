from fastapi import FastAPI
from prometheus_client import make_asgi_app
from app.api.telemetry import router as telemetry_router
import time

app = FastAPI(
    title="Helixa-One Brain API",
    description="The central intelligence engine for Data Center optimization.",
    version="0.2.0"
)

# Add Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include Routers
app.include_router(telemetry_router, tags=["telemetry"])

@app.get("/")
async def root():
    return {
        "name": "Helixa-One Brain",
        "status": "online",
        "timestamp": time.time(),
        "version": "0.2.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": time.time()
    }
