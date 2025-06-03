import datetime  # Assicurati che sia importato
import os

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Definizione degli URL base per i microservizi
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8001/api/v1")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users:8006/api/v1")
REPORTS_SERVICE_URL = os.getenv("REPORTS_SERVICE_URL", "http://reports:8007/api/v1")
GAME_SERVICE_URL = os.getenv("GAME_SERVICE_URL", "http://game:8005/api/v1")

# Include i router specifici per ciascun servizio
from .admin_routes import router as admin_router  # Admin health monitoring routes
from .auth_routes import router as auth_router
from .game_routes import router as game_router  # Game routes implementation
from .progress_routes import \
    router as progress_router  # Progress tracking routes
from .realtime_ai_routes import \
    router as realtime_ai_router  # Real-time AI routes
from .reports_routes import \
    router as reports_router  # Decommentato e importato
from .user_routes import router as user_router

# Registrazione dei router
router.include_router(admin_router, prefix="/admin", tags=["Admin"])  # Admin routes for system monitoring
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(user_router, prefix="/users", tags=["Users"])
router.include_router(reports_router, prefix="/reports", tags=["Reports"]) # Decommentato e incluso
router.include_router(game_router, prefix="/game", tags=["Game"]) # Game routes included
router.include_router(progress_router, prefix="/progress", tags=["Progress Tracking"]) # Progress tracking routes
router.include_router(realtime_ai_router, prefix="/realtime-ai", tags=["Real-time AI"]) # Real-time AI routes

# Endpoint di health check per tutti i servizi
@router.get("/health", tags=["System"])
async def health_check():
    health_status = {}
    
    async with httpx.AsyncClient() as client:
        services_to_check = {
            "auth": "http://auth:8001/status",  # Direct status endpoint
            "users": "http://users:8006/status",  # Direct status endpoint
            "reports": "http://reports:8007/status",  # Direct status endpoint
            "game": "http://game:8005/status"  # Game service status endpoint
        }
        for service_name, url in services_to_check.items():
            try:
                response = await client.get(url, timeout=5.0)
                health_status[service_name] = "online" if response.status_code == 200 else f"degraded - {response.status_code}"
            except httpx.TimeoutException:
                health_status[service_name] = "offline (timeout)"
            except httpx.RequestError as e:
                health_status[service_name] = f"offline - {type(e).__name__}"
            except Exception as e:  # Cattura generica per debug, potrebbe essere più specifica
                health_status[service_name] = f"offline - error: {str(e)}"
    
    # Determina lo stato complessivo del sistema
    overall_status = "healthy"
    if "offline" in health_status.values():
        overall_status = "degraded"
    if all(status == "offline" for status in health_status.values()):
        overall_status = "offline"
    
    return {
        "status": overall_status,
        "services": health_status,
        "timestamp": datetime.datetime.now().isoformat()
    }