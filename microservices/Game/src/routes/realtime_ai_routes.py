"""
Real-time AI Integration Routes for Game Service
Connects Game Service with LLM Service real-time AI capabilities
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, BackgroundTasks

from ..models.game_models import StartGameRequest, EndGameRequest, GameAction
from ..services.enhanced_game_service import enhanced_game_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/realtime", tags=["Real-time AI Integration"])

# LLM Service URL for real-time AI features
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8004/api/v1")

# Active real-time connections tracking
active_realtime_sessions: Dict[str, Dict[str, Any]] = {}

@router.post("/start-ai-monitoring/{session_id}")
async def start_ai_monitoring(
    session_id: str,
    user_id: int = Query(..., description="User ID"),
    child_id: Optional[int] = Query(None, description="Child ID for ASD monitoring")
):
    """Start real-time AI monitoring for a game session"""
    try:
        # Verify session exists
        game_state = enhanced_game_service.game_service.active_sessions.get(session_id)
        if not game_state:
            raise HTTPException(status_code=404, detail="Game session not found")
        
        if game_state.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to session")
        
        # Start AI monitoring in LLM service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE_URL}/realtime/sessions/{session_id}/start",
                json={
                    "child_id": child_id or user_id,  # Use user_id as fallback
                    "session_type": "enhanced_game",
                    "asd_monitoring_enabled": True
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to start AI monitoring")
            
            ai_response = response.json()
            
            # Track the real-time session
            active_realtime_sessions[session_id] = {
                "user_id": user_id,
                "child_id": child_id or user_id,
                "started_at": datetime.now(),
                "ai_monitoring_active": True,
                "last_analysis": None
            }
            
            return {
                "success": True,
                "message": "Real-time AI monitoring started",
                "session_id": session_id,
                "ai_service_response": ai_response
            }
            
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    except Exception as e:
        logger.error(f"Error starting AI monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start AI monitoring: {str(e)}")

@router.post("/process-with-ai/{session_id}")
async def process_action_with_ai_analysis(
    session_id: str,
    action_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Process game action and trigger real-time AI analysis"""
    try:
        # Process the game action normally
        enhanced_result = await enhanced_game_service.process_enhanced_game_action(
            session_id, action_data
        )
        
        # If real-time monitoring is active, send data to AI service
        if session_id in active_realtime_sessions:
            # Prepare session data for AI analysis
            session_data = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "action_type": action_data.get("action_type"),
                "action_data": action_data,
                "game_result": enhanced_result,
                "current_state": enhanced_result.get("game_state", {}),
                "asd_metrics": enhanced_result.get("asd_metrics", {}),
                "performance_data": {
                    "response_time": enhanced_result.get("response_time", 0),
                    "accuracy": enhanced_result.get("accuracy", 0),
                    "engagement_indicators": enhanced_result.get("engagement_indicators", {})
                }
            }
            
            # Send to AI service in background
            background_tasks.add_task(
                send_session_data_to_ai,
                session_id,
                session_data
            )
        
        return enhanced_result
        
    except Exception as e:
        logger.error(f"Error processing action with AI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process action: {str(e)}")

async def send_session_data_to_ai(session_id: str, session_data: Dict[str, Any]):
    """Background task to send session data to AI service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE_URL}/realtime/sessions/{session_id}/analyze",
                json=session_data,
                timeout=5.0
            )
            
            if response.status_code == 200:
                ai_analysis = response.json()
                
                # Update session tracking with latest analysis
                if session_id in active_realtime_sessions:
                    active_realtime_sessions[session_id]["last_analysis"] = ai_analysis
                    active_realtime_sessions[session_id]["last_update"] = datetime.now()
                
                logger.info(f"AI analysis completed for session {session_id}")
            else:
                logger.warning(f"AI analysis failed for session {session_id}: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error sending session data to AI service: {str(e)}")

@router.get("/ai-dashboard/{session_id}")
async def get_realtime_ai_dashboard(
    session_id: str,
    user_id: int = Query(..., description="User ID")
):
    """Get real-time AI dashboard for a session"""
    try:
        # Verify session access
        if session_id not in active_realtime_sessions:
            raise HTTPException(status_code=404, detail="Real-time monitoring not active for this session")
        
        session_info = active_realtime_sessions[session_id]
        if session_info["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        
        # Get dashboard data from AI service
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LLM_SERVICE_URL}/realtime/sessions/{session_id}/dashboard",
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to get AI dashboard")
            
            ai_dashboard = response.json()
            
            # Get current game state for additional context
            game_state = enhanced_game_service.game_service.active_sessions.get(session_id)
            asd_metrics = enhanced_game_service.asd_service.session_metrics.get(session_id, [])
            
            # Combine AI dashboard with game-specific data
            combined_dashboard = {
                "ai_insights": ai_dashboard.get("dashboard", {}),
                "game_state": {
                    "current_level": game_state.current_level if game_state else 0,
                    "score": game_state.score if game_state else 0,
                    "current_objective": game_state.current_objective if game_state else "None",
                    "session_duration": str(datetime.now() - game_state.start_time) if game_state else "0:00:00"
                },
                "asd_monitoring": {
                    "metrics_count": len(asd_metrics),
                    "latest_overstimulation_score": asd_metrics[-1].overstimulation_score if asd_metrics else 0.0,
                    "monitoring_active": session_info["ai_monitoring_active"]
                },
                "session_info": {
                    "session_id": session_id,
                    "monitoring_duration": str(datetime.now() - session_info["started_at"]),
                    "last_ai_update": session_info.get("last_update", session_info["started_at"]).isoformat()
                }
            }
            
            return {
                "success": True,
                "dashboard": combined_dashboard
            }
            
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    except Exception as e:
        logger.error(f"Error getting AI dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@router.get("/ai-recommendations/{session_id}")
async def get_live_ai_recommendations(
    session_id: str,
    user_id: int = Query(..., description="User ID")
):
    """Get live AI recommendations for ongoing session"""
    try:
        # Verify session access
        if session_id not in active_realtime_sessions:
            raise HTTPException(status_code=404, detail="Real-time monitoring not active")
        
        session_info = active_realtime_sessions[session_id]
        if session_info["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        
        # Get current context for recommendations
        game_state = enhanced_game_service.game_service.active_sessions.get(session_id)
        asd_metrics = enhanced_game_service.asd_service.session_metrics.get(session_id, [])
        
        context = {
            "current_level": game_state.current_level if game_state else 0,
            "current_score": game_state.score if game_state else 0,
            "recent_asd_metrics": [m.dict() for m in asd_metrics[-3:]] if asd_metrics else [],
            "session_duration": str(datetime.now() - game_state.start_time) if game_state else "0:00:00"
        }
        
        # Get recommendations from AI service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE_URL}/realtime/sessions/{session_id}/recommendations",
                json=context,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to get recommendations")
            
            ai_response = response.json()
            
            return {
                "success": True,
                "recommendations": ai_response.get("recommendations", []),
                "context": context
            }
            
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/stop-ai-monitoring/{session_id}")
async def stop_ai_monitoring(
    session_id: str,
    user_id: int = Query(..., description="User ID")
):
    """Stop real-time AI monitoring for a session"""
    try:
        # Verify session access
        if session_id not in active_realtime_sessions:
            raise HTTPException(status_code=404, detail="Real-time monitoring not active")
        
        session_info = active_realtime_sessions[session_id]
        if session_info["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        
        # Stop monitoring in AI service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE_URL}/realtime/sessions/{session_id}/end",
                timeout=10.0
            )
            
            ai_summary = {}
            if response.status_code == 200:
                ai_summary = response.json()
            
            # Clean up local tracking
            del active_realtime_sessions[session_id]
            
            return {
                "success": True,
                "message": "Real-time AI monitoring stopped",
                "session_summary": ai_summary.get("summary", {})
            }
            
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    except Exception as e:
        logger.error(f"Error stopping AI monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")

@router.get("/active-ai-sessions")
async def get_active_ai_sessions():
    """Get all active real-time AI monitoring sessions"""
    try:
        active_sessions = []
        
        for session_id, session_info in active_realtime_sessions.items():
            duration = datetime.now() - session_info["started_at"]
            
            active_sessions.append({
                "session_id": session_id,
                "user_id": session_info["user_id"],
                "child_id": session_info["child_id"],
                "duration_minutes": round(duration.total_seconds() / 60, 2),
                "ai_monitoring_active": session_info["ai_monitoring_active"],
                "last_analysis": session_info.get("last_analysis") is not None
            })
        
        return {
            "success": True,
            "active_sessions": active_sessions,
            "total_count": len(active_sessions)
        }
        
    except Exception as e:
        logger.error(f"Error getting active AI sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get active sessions: {str(e)}")

@router.websocket("/stream/{session_id}")
async def websocket_realtime_connection(websocket: WebSocket, session_id: str):
    """WebSocket connection for real-time game and AI updates"""
    await websocket.accept()
    
    try:
        logger.info(f"WebSocket connection established for session {session_id}")
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive and relay updates
        while True:
            try:
                # Wait for messages from client or send periodic updates
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                if message.get("type") == "heartbeat":
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat_response",
                        "timestamp": datetime.now().isoformat()
                    }))
                
                elif message.get("type") == "request_status":
                    # Send current session status
                    status = {
                        "type": "session_status",
                        "data": {
                            "session_id": session_id,
                            "ai_monitoring_active": session_id in active_realtime_sessions,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    await websocket.send_text(json.dumps(status))
                
            except asyncio.TimeoutError:
                # Send periodic heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
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
                logger.error(f"WebSocket error: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Server error: {str(e)}"
                }))
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    finally:
        logger.info(f"WebSocket connection closed for session {session_id}")
