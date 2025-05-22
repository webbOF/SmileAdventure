import datetime  # Assicurati che sia importato

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Definizione degli URL base per i microservizi
AUTH_SERVICE_URL = "http://auth-service:8001/api/v1"
USERS_SERVICE_URL = "http://users-service:8006/api/v1"
REPORTS_SERVICE_URL = "http://reports-service:8007/api/v1"  # Aggiunto per il futuro servizio Reports
# NOTIFICATION_SERVICE_URL = "http://notification-service:8004/api/v1" # Esempio se si volesse riaggiungere

# Include i router specifici per ciascun servizio
from .auth_routes import router as auth_router
from .reports_routes import \
    router as reports_router  # Decommentato e importato
from .user_routes import router as user_router

# Registrazione dei router
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(user_router, prefix="/users", tags=["Users"])
router.include_router(reports_router, prefix="/reports", tags=["Reports"]) # Decommentato e incluso

# Endpoint di health check per tutti i servizi
@router.get("/health", tags=["System"])
async def health_check():
    health_status = {}
    
    async with httpx.AsyncClient() as client:
        services_to_check = {
            "auth": f"{AUTH_SERVICE_URL}/auth/status",  # Assumendo che l'endpoint di status sia /auth/status
            "users": f"{USERS_SERVICE_URL}/users/status",  # Assumendo /users/status
            "reports": f"{REPORTS_SERVICE_URL}/reports/status"  # Assumendo /reports/status
            # "notification": f"{NOTIFICATION_SERVICE_URL}/notifications/status", # Esempio
        }
        for service_name, url in services_to_check.items():
            try:
                response = await client.get(url, timeout=2.0)
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