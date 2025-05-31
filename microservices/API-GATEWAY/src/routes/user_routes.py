# API Gateway User Routes
import os
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException

from ..auth.jwt_auth import get_current_active_user, get_current_user

router = APIRouter()
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users:8006/api/v1")
SERVICE_UNAVAILABLE_MSG = "Users service unavailable"

@router.get("/health", tags=["Users"])
async def users_health():
    """Health check endpoint for users service."""
    try:
        async with httpx.AsyncClient() as client:
            users_status_url = "http://users:8006/status"
            response = await client.get(users_status_url, timeout=5.0)
            if response.status_code == 200:
                return {"status": "online", "service": "users"}
            else:
                return {"status": "degraded", "service": "users", "code": response.status_code}
    except Exception as e:
        return {"status": "offline", "service": "users", "error": str(e)}

@router.get("/me", tags=["Users"])
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Retrieve current user profile."""
    # Extract user identifier from JWT payload - use enhanced JWT structure
    user_id = current_user.get("user_id") or current_user.get("id")  # Try new structure first, fallback to old
    user_email = current_user.get("sub")
    
    # Debug: log what we received
    print(f"DEBUG: current_user = {current_user}")
    print(f"DEBUG: user_id = {user_id}, user_email = {user_email}")
    
    if not user_id and not user_email:
        raise HTTPException(status_code=400, detail=f"User identifier not found in token. Token data: {current_user}")
    
    try:
        async with httpx.AsyncClient() as client:
            if user_id:
                # Direct user ID lookup
                user_url = f"{USERS_SERVICE_URL}/users/{user_id}"
                print(f"DEBUG: Using user ID lookup: {user_url}")
                response = await client.get(user_url, timeout=10.0)
            else:
                # Email-based lookup - get user by email using query parameter
                user_url = f"{USERS_SERVICE_URL}/users/"  # Added trailing slash
                params = {"email": user_email}
                print(f"DEBUG: Using email lookup: {user_url}?email={user_email}")
                response = await client.get(user_url, params=params, timeout=10.0)
            
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response headers: {dict(response.headers)}")
            print(f"DEBUG: Response content: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            # If email lookup returns a list, get the first user
            if isinstance(result, list) and result:
                return result[0]
            return result
    except httpx.HTTPStatusError as exc:
        error_detail = "User not found"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.put("/me", tags=["Users"])
async def update_current_user_profile(
    profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update current user profile."""
    user_id = current_user.get("user_id") or current_user.get("id")  # Try enhanced JWT structure first
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    try:
        async with httpx.AsyncClient() as client:
            user_url = f"{USERS_SERVICE_URL}/users/{user_id}"
            response = await client.put(user_url, json=profile_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Update failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/{user_id}", tags=["Users"])
async def get_user_profile(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve specific user profile."""
    try:
        async with httpx.AsyncClient() as client:
            user_url = f"{USERS_SERVICE_URL}/users/{user_id}"
            response = await client.get(user_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "User not found"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/professionals/search", tags=["Users"])
async def search_professionals(
    specialty: Optional[str] = None,
    location: Optional[str] = None,
    min_rating: Optional[float] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Search professionals based on criteria."""
    try:
        params = {}
        if specialty:
            params["specialty_name"] = specialty
        if location:
            params["location_city"] = location
        if min_rating is not None:
            params["min_rating"] = min_rating
            
        async with httpx.AsyncClient() as client:
            search_url = f"{USERS_SERVICE_URL}/users/professionals/search"
            response = await client.get(search_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Search failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)