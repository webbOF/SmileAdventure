# API Gateway JWT Authentication Module
import os
from typing import Any, Dict, Optional

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# HTTP Bearer token security
security = HTTPBearer()

# Auth service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001/api/v1")

async def verify_token_with_auth_service(token: str) -> Dict[str, Any]:
    """
    Verify token by calling the auth service
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/auth/verify",
                json={"token": token}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "invalid",
                    "error": response.text
                }
    except Exception as e:
        return {
            "status": "invalid",
            "error": str(e)
        }

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current user from JWT token by verifying with auth service
    """
    token = credentials.credentials
    result = await verify_token_with_auth_service(token)
    
    if result.get("status") == "invalid":
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result.get("payload", result)

async def get_current_active_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current active user (same as get_current_user for now)
    """
    return await get_current_user(credentials)

async def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify that the user is an admin
    """
    user = await get_current_user(credentials)
    
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied: admin privileges required",
        )
    
    return user
