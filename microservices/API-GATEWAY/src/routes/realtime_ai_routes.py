"""
API Gateway Real-time AI Routes
Routes real-time AI requests to appropriate services
"""

import os
from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse

from ..auth.jwt_auth import get_current_user

router = APIRouter()

# Service URLs
GAME_SERVICE_URL = os.getenv("GAME_SERVICE_URL", "http://game:8005/api/v1")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8004/api/v1")
SERVICE_UNAVAILABLE_MSG = "Service unavailable"

@router.post("/start-monitoring/{session_id}", tags=["Real-time AI"])
async def start_realtime_monitoring(
    session_id: str,
    monitoring_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Start real-time AI monitoring for a game session"""
    try:
        # Add user context
        monitoring_data["user_id"] = current_user.get("user_id")
        
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/realtime/start-ai-monitoring/{session_id}"
            params = {"user_id": current_user.get("user_id")}
            
            # Add child_id from request body if provided
            if "child_id" in monitoring_data:
                params["child_id"] = monitoring_data["child_id"]
            
            response = await client.post(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to start real-time monitoring"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.post("/process-with-ai/{session_id}", tags=["Real-time AI"])
async def process_action_with_ai(
    session_id: str,
    action_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Process game action with real-time AI analysis"""
    try:
        # Add user context
        action_data["user_id"] = current_user.get("user_id")
        
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/realtime/process-with-ai/{session_id}"
            response = await client.post(target_url, json=action_data, timeout=15.0)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to process action with AI"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/dashboard/{session_id}", tags=["Real-time AI"])
async def get_realtime_dashboard(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get real-time AI dashboard for a session"""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/realtime/ai-dashboard/{session_id}"
            params = {"user_id": current_user.get("user_id")}
            response = await client.get(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get real-time dashboard"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/recommendations/{session_id}", tags=["Real-time AI"])
async def get_live_recommendations(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get live AI recommendations for ongoing session"""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/realtime/ai-recommendations/{session_id}"
            params = {"user_id": current_user.get("user_id")}
            response = await client.get(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get live recommendations"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.post("/stop-monitoring/{session_id}", tags=["Real-time AI"])
async def stop_realtime_monitoring(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Stop real-time AI monitoring for a session"""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/realtime/stop-ai-monitoring/{session_id}"
            params = {"user_id": current_user.get("user_id")}
            response = await client.post(target_url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to stop real-time monitoring"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.get("/active-sessions", tags=["Real-time AI"])
async def get_active_realtime_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all active real-time AI monitoring sessions"""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{GAME_SERVICE_URL}/game/realtime/active-ai-sessions"
            response = await client.get(target_url, timeout=10.0)
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

@router.get("/overstimulation-patterns/{session_id}", tags=["Real-time AI"])
async def get_overstimulation_patterns(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get real-time overstimulation pattern detection"""
    try:
        async with httpx.AsyncClient() as client:
            target_url = f"{LLM_SERVICE_URL}/realtime/sessions/{session_id}/overstimulation-patterns"
            response = await client.get(target_url, timeout=10.0)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as exc:
        error_detail = "Failed to get overstimulation patterns"
        try:
            error_detail = exc.response.json().get("detail", error_detail)
        except Exception:
            pass
        raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MSG)

@router.websocket("/stream/{session_id}")
async def websocket_realtime_stream(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time AI streaming"""
    await websocket.accept()
    
    try:
        # Forward WebSocket connection to appropriate service
        # This implementation routes to the Game Service WebSocket
        # which then coordinates with LLM Service for AI streaming
        
        import asyncio
        import json
        from datetime import datetime
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "gateway_connection_established",
            "session_id": session_id,
            "message": "Real-time AI streaming via API Gateway",
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for incoming messages with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "heartbeat":
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat_response",
                        "timestamp": datetime.now().isoformat()
                    }))
                
                elif message.get("type") == "request_status":
                    # Forward status request to Game Service
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(
                                f"{GAME_SERVICE_URL}/game/realtime/active-ai-sessions",
                                timeout=5.0
                            )
                            if response.status_code == 200:
                                data = response.json()
                                await websocket.send_text(json.dumps({
                                    "type": "status_response",
                                    "data": data
                                }))
                            else:
                                await websocket.send_text(json.dumps({
                                    "type": "error",
                                    "message": "Failed to get status"
                                }))
                    except Exception as e:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": f"Service error: {str(e)}"
                        }))
                
                elif message.get("type") == "session_update":
                    # Forward session updates to processing
                    session_data = message.get("data", {})
                    await websocket.send_text(json.dumps({
                        "type": "update_acknowledged",
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    }))
                
            except asyncio.TimeoutError:
                # Send periodic heartbeat
                await websocket.send_text(json.dumps({
                    "type": "gateway_heartbeat",
                    "timestamp": datetime.now().isoformat()
                }))
                
            except WebSocketDisconnect:
                break
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
                
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Gateway error: {str(e)}"
                }))
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "fatal_error",
                "message": f"Connection error: {str(e)}"
            }))
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
