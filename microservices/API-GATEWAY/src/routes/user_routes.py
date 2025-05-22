from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException

from ..auth.jwt_auth import get_current_active_user, get_current_user

router = APIRouter()
USERS_SERVICE_URL = "http://users-service:8006/api/v1"

@router.get("/me", tags=["Users"])
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Recupera il profilo dell'utente corrente."""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USERS_SERVICE_URL}/users/{user_id}" # Assumendo che l'endpoint sia /users/{user_id}
            )
            response.raise_for_status() # Solleva eccezione per 4xx/5xx
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servizio utenti non disponibile")

@router.put("/me", tags=["Users"])
async def update_current_user_profile(
    profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Aggiorna il profilo dell'utente corrente."""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{USERS_SERVICE_URL}/users/{user_id}", # Assumendo che l'endpoint sia /users/{user_id}
                json=profile_data
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servizio utenti non disponibile")

@router.get("/{user_id}", tags=["Users"])
async def get_user_profile(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user) # o get_current_active_user se serve utente attivo
):
    """Recupera il profilo di un utente specifico."""
    # Qui potresti voler aggiungere logica di autorizzazione 
    # (es. solo admin o l'utente stesso possono vedere certi profili)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USERS_SERVICE_URL}/users/{user_id}"
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servizio utenti non disponibile")

@router.get("/professionals", tags=["Users"])
async def search_professionals(
    specialty: Optional[str] = None, # Usare Optional per i parametri di query
    location: Optional[str] = None,
    min_rating: Optional[float] = None, # Rinominato per coerenza con user_service
    current_user: Dict[str, Any] = Depends(get_current_user) # Dipende se l'accesso è pubblico o richiede auth
):
    """Cerca professionisti in base a criteri specifici."""
    try:
        params = {}
        if specialty:
            params["specialty_name"] = specialty # Deve corrispondere al parametro atteso dal servizio Users
        if location:
            params["location_city"] = location # Deve corrispondere
        if min_rating is not None: # Controllare se è None, non solo truthiness
            params["min_rating"] = min_rating
            
        async with httpx.AsyncClient() as client:
            # Assicurati che l'endpoint nel servizio Users sia /professionals o simile
            response = await client.get(
                f"{USERS_SERVICE_URL}/users/professionals/search", # Endpoint ipotetico, da verificare
                params=params
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servizio utenti non disponibile")