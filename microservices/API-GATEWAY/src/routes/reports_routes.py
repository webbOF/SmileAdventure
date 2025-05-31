# API Gateway Reports Routes
import os
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from ..auth.jwt_auth import get_current_user

router = APIRouter()

REPORTS_SERVICE_URL = os.getenv("REPORTS_SERVICE_URL", "http://reports:8007/api/v1")

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
