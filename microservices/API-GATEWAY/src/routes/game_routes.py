# API Gateway Game Routes
import os
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException

from ..auth.jwt_auth import get_current_user

router = APIRouter()

GAME_SERVICE_URL = os.getenv("GAME_SERVICE_URL", "http://game:8005/api/v1")
SERVICE_UNAVAILABLE_MSG = "Game service unavailable"

@router.get("/health", tags=["Game"])
async def game_health():
    """Health check endpoint for game service."""
    try:
        async with httpx.AsyncClient() as client:
            game_status_url = "http://game:8005/status"
            response = await client.get(game_status_url, timeout=5.0)
            if response.status_code == 200:
                return {"status": "online", "service": "game"}
            else:
                return {"status": "degraded", "service": "game", "code": response.status_code}
    except Exception as e:
        return {"status": "offline", "service": "game", "error": str(e)}

@router.post("/start", tags=["Game"])
async def start_game_session(
    game_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Start a new game session."""
    try:
        # Add user ID to game data
        game_data["user_id"] = current_user.get("user_id")
        
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/start"
            response = await client.post(target_url, json=game_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to start game session"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.post("/end", tags=["Game"])
async def end_game_session(
    session_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """End a game session."""
    try:        # Add user ID to session data
        session_data["user_id"] = current_user.get("user_id")
        
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/end"
            response = await client.post(target_url, json=session_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to end game session"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/state", tags=["Game"])
async def get_game_state(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current game state."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/state"
            params = {"session_id": session_id, "user_id": current_user.get("user_id")}
            response = await client.get(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get game state"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.post("/action", tags=["Game"])
async def process_game_action(
    action_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Process a game action."""
    try:        # Add user ID to action data
        action_data["user_id"] = current_user.get("user_id")
        
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/action"
            response = await client.post(target_url, json=action_data, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to process game action"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/scenarios", tags=["Game"])
async def get_scenarios():
    """Get available game scenarios."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/scenarios"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get game scenarios"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/sessions", tags=["Game"])
async def get_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all game sessions for the current user."""
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID not found in token")
            
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/sessions/active"
            params = {"user_id": user_id}
            response = await client.get(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get game sessions"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/sessions/active", tags=["Game"])
async def get_active_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get active game sessions for the current user."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/sessions/active"
            params = {"user_id": current_user.get("user_id")}
            response = await client.get(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get active sessions"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/sessions/{session_id}/history", tags=["Game"])
async def get_session_history(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get session interaction history."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/sessions/{session_id}/history"
            params = {"user_id": current_user.get("user_id")}
            response = await client.get(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get session history"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/leaderboard", tags=["Game"])
async def get_leaderboard(
    scenario_id: str = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get game leaderboard."""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/leaderboard"
            params = {}
            if scenario_id:
                params["scenario_id"] = scenario_id
            response = await client.get(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get leaderboard"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/stats", tags=["Game"])
async def get_game_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get overall game statistics (admin only for now)."""
    try:
        # For now, allow all authenticated users to see stats
        # In the future, you might want to restrict this to admins only
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/stats"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get game statistics"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)