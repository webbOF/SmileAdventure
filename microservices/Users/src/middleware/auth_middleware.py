# Users/src/middleware/auth_middleware.py
# Middleware per l'autenticazione nel servizio Users

import os
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Classe per la gestione del token di autenticazione
security = HTTPBearer()

# Chiave segreta per la verifica del JWT (dovrebbe essere la stessa dell'Auth service)
JWT_SECRET = os.getenv("JWT_SECRET", "smile_adventure_secret_key_2024")
JWT_ALGORITHM = "HS256"

def verify_token(token: str) -> dict:
    """
    Verifica un token JWT e restituisce il payload decodificato.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"status": "valid", "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"status": "invalid", "error": "Token scaduto"}
    except jwt.InvalidTokenError:
        return {"status": "invalid", "error": "Token non valido"}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware che verifica il token JWT e restituisce i dati dell'utente autenticato.
    Da utilizzare con Depends() per proteggere le route che richiedono autenticazione.
    """
    token = credentials.credentials
    result = verify_token(token)
    
    if result["status"] == "invalid":
        raise HTTPException(
            status_code=401,
            detail="Token di autenticazione non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result["payload"]

async def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware che verifica che l'utente sia un amministratore.
    Da utilizzare per route riservate agli amministratori.
    """
    token = credentials.credentials
    result = verify_token(token)
    
    if result["status"] == "invalid":
        raise HTTPException(
            status_code=401,
            detail="Token di autenticazione non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = result["payload"]
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Accesso negato: richiesti privilegi di amministratore",
        )
    
    return payload
