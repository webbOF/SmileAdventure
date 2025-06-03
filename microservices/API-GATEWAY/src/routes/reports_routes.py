# API Gateway Reports Routes
import os
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from ..auth.jwt_auth import get_current_user

router = APIRouter()

REPORTS_SERVICE_URL = os.getenv("REPORTS_SERVICE_URL", "http://reports:8007/api/v1")
SERVICE_UNAVAILABLE_MSG = "Reports service unavailable"

@router.get("/health", tags=["Reports"])
async def reports_health():
    """Health check endpoint for reports service."""
    try:
        async with httpx.AsyncClient() as client:
            reports_status_url = "http://reports:8007/status"
            response = await client.get(reports_status_url, timeout=5.0)
            if response.status_code == 200:
                return {"status": "online", "service": "reports"}
            else:
                return {"status": "degraded", "service": "reports", "code": response.status_code}
    except Exception as e:
        return {"status": "offline", "service": "reports", "error": str(e)}

@router.post("/game-session", tags=["Reports"])
async def forward_game_session(
    request_body: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Forwards game session data to the Reports microservice."""
    target_url = f"{REPORTS_SERVICE_URL}/reports/game-session"
      # You might want to add the user_id from the token to the body 
    # if the Reports service needs it and doesn't get it from elsewhere.
    # request_body["user_id"] = current_user.get("id")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(target_url, json=request_body)
            response.raise_for_status() # Raise an exception for 4xx or 5xx status codes
            return response.json()
    except httpx.HTTPStatusError as exc:
        # Forward the error from the Reports service
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.json())
    except httpx.RequestError as exc:
        # Handle network errors or if the service is down
        raise HTTPException(status_code=503, detail=f"Reports service unavailable: {exc}")
    except Exception as e:
        # Catch-all for other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/child/{child_id}/summary", tags=["Reports"])
async def get_child_summary(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get child progress summary from Reports service."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{REPORTS_SERVICE_URL}/reports/child/{child_id}/summary"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Child summary not found")
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to get child summary")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/child/{child_id}/emotion-patterns", tags=["Reports"])
async def get_emotion_patterns(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get child emotion patterns from Reports service."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{REPORTS_SERVICE_URL}/reports/child/{child_id}/emotion-patterns"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to get emotion patterns")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/overall-platform-activity", tags=["Reports"])
async def get_platform_activity(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get platform activity overview from Reports service."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{REPORTS_SERVICE_URL}/reports/overall-platform-activity"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to get platform activity")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/child/{child_id}/summary", tags=["Reports"])
async def get_child_summary(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get child progress summary from Reports service."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{REPORTS_SERVICE_URL}/reports/child/{child_id}/summary"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Child summary not found")
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to get child summary")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Reports service unavailable")

@router.get("/child/{child_id}/emotion-patterns", tags=["Reports"])
async def get_emotion_patterns(
    child_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get child emotion patterns from Reports service."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{REPORTS_SERVICE_URL}/reports/child/{child_id}/emotion-patterns"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to get emotion patterns")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Reports service unavailable")

@router.get("/overall-platform-activity", tags=["Reports"])
async def get_platform_activity(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get platform activity overview from Reports service."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{REPORTS_SERVICE_URL}/reports/overall-platform-activity"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to get platform activity")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Reports service unavailable")
