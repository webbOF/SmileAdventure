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
            search_url = f"{USERS_SERVICE_URL}/professionals/search"
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

# Children endpoints forwarding
@router.post("/children", tags=["Children"])
async def create_child(
    child_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new child for the current user."""
    try:
        async with httpx.AsyncClient() as client:
            children_url = f"{USERS_SERVICE_URL}/children"
            response = await client.post(children_url, json=child_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Child creation failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/children/my", tags=["Children"])
async def get_my_children(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get children for the current user."""
    try:
        async with httpx.AsyncClient() as client:
            children_url = f"{USERS_SERVICE_URL}/children/my"
            response = await client.get(children_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to retrieve children"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/children/{child_id}", tags=["Children"])
async def get_child(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific child by ID."""
    try:
        async with httpx.AsyncClient() as client:
            child_url = f"{USERS_SERVICE_URL}/children/{child_id}"
            response = await client.get(child_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Child not found"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.put("/children/{child_id}", tags=["Children"])
async def update_child(
    child_id: int,
    child_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update a child's information."""
    try:
        async with httpx.AsyncClient() as client:
            child_url = f"{USERS_SERVICE_URL}/children/{child_id}"
            response = await client.put(child_url, json=child_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Child update failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.delete("/children/{child_id}", tags=["Children"])
async def delete_child(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a child."""
    try:
        async with httpx.AsyncClient() as client:
            child_url = f"{USERS_SERVICE_URL}/children/{child_id}"
            response = await client.delete(child_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Child deletion failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/children/{child_id}/clinical", tags=["Children"])
async def get_child_clinical_view(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get clinical view of a child (for professionals)."""
    try:
        async with httpx.AsyncClient() as client:
            clinical_url = f"{USERS_SERVICE_URL}/children/{child_id}/clinical"
            response = await client.get(clinical_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Clinical view access failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/children", tags=["Children"])
async def get_all_children(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all children (admin/professional access)."""
    try:
        async with httpx.AsyncClient() as client:
            children_url = f"{USERS_SERVICE_URL}/children"
            response = await client.get(children_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to retrieve all children"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

# Sensory Profile endpoints forwarding
@router.post("/sensory-profiles", tags=["Sensory Profiles"])
async def create_sensory_profile(
    sensory_profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new sensory profile for a child."""
    try:
        async with httpx.AsyncClient() as client:
            sensory_profiles_url = f"{USERS_SERVICE_URL}/sensory-profiles"
            response = await client.post(sensory_profiles_url, json=sensory_profile_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Sensory profile creation failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/sensory-profiles", tags=["Sensory Profiles"])
async def get_sensory_profiles(
    skip: int = 0,
    limit: int = 100,
    child_id: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get sensory profiles."""
    try:
        params = {"skip": skip, "limit": limit}
        if child_id:
            params["child_id"] = child_id
            
        async with httpx.AsyncClient() as client:
            sensory_profiles_url = f"{USERS_SERVICE_URL}/sensory-profiles"
            response = await client.get(sensory_profiles_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to retrieve sensory profiles"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/sensory-profiles/{profile_id}", tags=["Sensory Profiles"])
async def get_sensory_profile(
    profile_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific sensory profile."""
    try:
        async with httpx.AsyncClient() as client:
            sensory_profile_url = f"{USERS_SERVICE_URL}/sensory-profiles/{profile_id}"
            response = await client.get(sensory_profile_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Sensory profile not found"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.put("/sensory-profiles/{profile_id}", tags=["Sensory Profiles"])
async def update_sensory_profile(
    profile_id: int,
    sensory_profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update a sensory profile."""
    try:
        async with httpx.AsyncClient() as client:
            sensory_profile_url = f"{USERS_SERVICE_URL}/sensory-profiles/{profile_id}"
            response = await client.put(sensory_profile_url, json=sensory_profile_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Sensory profile update failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.delete("/sensory-profiles/{profile_id}", tags=["Sensory Profiles"])
async def delete_sensory_profile(
    profile_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a sensory profile."""
    try:
        async with httpx.AsyncClient() as client:
            sensory_profile_url = f"{USERS_SERVICE_URL}/sensory-profiles/{profile_id}"
            response = await client.delete(sensory_profile_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Sensory profile deletion failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/children/{child_id}/sensory-profile", tags=["Sensory Profiles"])
async def get_child_sensory_profile(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get sensory profile for a specific child."""
    try:
        async with httpx.AsyncClient() as client:
            sensory_profile_url = f"{USERS_SERVICE_URL}/children/{child_id}/sensory-profile"
            response = await client.get(sensory_profile_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Sensory profile not found for this child"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.post("/children/{child_id}/sensory-profile", tags=["Sensory Profiles"])
async def create_child_sensory_profile(
    child_id: int,
    sensory_profile_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a sensory profile for a specific child."""
    try:
        # Ensure the child_id in the data matches the path parameter
        sensory_profile_data['child_id'] = child_id
        
        async with httpx.AsyncClient() as client:
            sensory_profiles_url = f"{USERS_SERVICE_URL}/sensory-profiles"
            response = await client.post(sensory_profiles_url, json=sensory_profile_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Sensory profile creation failed"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)
