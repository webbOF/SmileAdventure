import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.gateway_routes import router as api_router

# Configurazione variabili d'ambiente con valori di default
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8001/api/v1")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users:8006/api/v1")
REPORTS_SERVICE_URL = os.getenv("REPORTS_SERVICE_URL", "http://reports:8007/api/v1") # Added Reports service URL
GAME_SERVICE_URL = os.getenv("GAME_SERVICE_URL", "http://game:8005/api/v1")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8008/api/v1") # Added LLM service URL

app = FastAPI(
    title="SmileAdventure API Gateway",
    description="API Gateway per SmileAdventure",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, limita alle origini specifiche
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra il router principale
app.include_router(api_router, prefix="/api/v1")

@app.get("/status")
async def status():
    return {"status": "API Gateway is running"}