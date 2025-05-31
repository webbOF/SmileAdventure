import os
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

# URL del servizio di autenticazione
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8001/api/v1")

@router.get("/health")
async def health_check():
    """Controlla lo stato del servizio di autenticazione."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Use the base service URL without /api/v1 for health check
            auth_base_url = os.getenv("AUTH_SERVICE_URL", "http://auth:8001/api/v1").replace("/api/v1", "")
            response = await client.get(f"{auth_base_url}/status")
            if response.status_code == 200:
                return {"status": "healthy", "service": "auth", "timestamp": response.json()}
            else:
                return {"status": "unhealthy", "service": "auth", "code": response.status_code}
    except Exception as e:
        return {"status": "unhealthy", "service": "auth", "error": str(e)}

@router.post("/login")
async def login(user_data: Dict[str, Any]):
    """Effettua il login di un utente."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{AUTH_SERVICE_URL}/auth/login", json=user_data)
            
            if response.status_code != 200: # Generalmente il login di successo è 200
                # Prova a parsare il JSON per un messaggio di errore più specifico
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                raise HTTPException(status_code=response.status_code, detail=detail)
                
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servizio di autenticazione non disponibile")

@router.post("/register")
async def register(user_data: Dict[str, Any]):
    """Registra un nuovo utente."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{AUTH_SERVICE_URL}/auth/register", json=user_data)
            
            # La registrazione di successo potrebbe restituire 201 Created
            if response.status_code not in [200, 201]: 
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                raise HTTPException(status_code=response.status_code, detail=detail)
                
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servizio di autenticazione non disponibile")

@router.post("/verify-token")
async def verify_token(token_data: Dict[str, Any]): # Il body dovrebbe contenere {"token": "your_jwt_token"}
    """Verifica un token JWT."""
    try:
        async with httpx.AsyncClient() as client:
            # Assicurati che l'endpoint nel servizio Auth sia /auth/verify e accetti POST con JSON
            response = await client.post(f"{AUTH_SERVICE_URL}/auth/verify", json=token_data) 
            
            if response.status_code != 200:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                raise HTTPException(status_code=response.status_code, detail=detail)
                
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servizio di autenticazione non disponibile")

@router.post("/refresh-token")
async def refresh_token(token_data: Dict[str, Any]): # Il body dovrebbe contenere {"token": "your_refresh_token"}
    """Rinnova un token JWT."""
    try:
        async with httpx.AsyncClient() as client:
            # Assicurati che l'endpoint nel servizio Auth sia /auth/refresh e accetti POST con JSON
            response = await client.post(f"{AUTH_SERVICE_URL}/auth/refresh", json=token_data)
            
            if response.status_code != 200:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                raise HTTPException(status_code=response.status_code, detail=detail)
                
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servizio di autenticazione non disponibile")