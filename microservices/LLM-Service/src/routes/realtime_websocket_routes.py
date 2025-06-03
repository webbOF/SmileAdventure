"""
Real-time WebSocket Routes for AI Streaming
Provides WebSocket endpoints for live AI analysis and streaming interventions
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..services.realtime_ai_service import RealTimeAIService
from ..middleware import authenticate_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/realtime", tags=["Real-time AI"])

# Initialize real-time AI service
realtime_ai_service = RealTimeAIService()

@router.on_event("startup")
async def startup_realtime_service():
    """Initialize real-time AI service on startup"""
    await realtime_ai_service.initialize()

@router.on_event("shutdown")
async def shutdown_realtime_service():
    """Cleanup real-time AI service on shutdown"""
    await realtime_ai_service.cleanup()

@router.websocket("/stream/{session_id}")
async def websocket_stream_ai_analysis(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for streaming AI analysis"""
    await websocket.accept()
    
    try:
        # Register WebSocket connection
        await realtime_ai_service.register_websocket_connection(session_id, websocket)
        
        logger.info(f"WebSocket connected for session {session_id}")
        
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "session_id": session_id,
            "message": "Real-time AI streaming active"
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for incoming messages (heartbeat, session updates, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "heartbeat":
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat_response",
                        "timestamp": str(datetime.now())
                    }))
                
                elif message.get("type") == "request_dashboard":
                    # Send current dashboard data
                    dashboard_data = await realtime_ai_service.get_live_session_dashboard(session_id)
                    await websocket.send_text(json.dumps({
                        "type": "dashboard_update",
                        "data": dashboard_data
                    }))                
                elif message.get("type") == "session_data_update":
                    # Process live session data update
                    session_data = message.get("data", {})
                    await realtime_ai_service.process_live_session_data(session_id, session_data)
                    # Analysis will be broadcast automatically via WebSocket
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"Error in WebSocket handler: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Server error: {str(e)}"
                }))
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
    finally:
        # Unregister WebSocket connection
        await realtime_ai_service.unregister_websocket_connection(session_id, websocket)

@router.post("/sessions/{session_id}/start")
async def start_live_monitoring(
    session_id: str, 
    data: Dict[str, Any],
    authenticated: bool = Depends(authenticate_request)
):
    """Start live AI monitoring for a session"""
    try:
        child_id = data.get("child_id")
        if not child_id:
            raise HTTPException(status_code=400, detail="child_id is required")
        
        session_metrics = await realtime_ai_service.start_live_session_monitoring(session_id, child_id)
        
        return {
            "success": True,
            "message": "Live monitoring started",
            "session_id": session_id,
            "metrics": {
                "session_id": session_metrics.session_id,
                "child_id": session_metrics.child_id,
                "start_time": session_metrics.start_time.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error starting live monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start live monitoring: {str(e)}")

@router.post("/sessions/{session_id}/analyze")
async def analyze_live_session_data(
    session_id: str,
    session_data: Dict[str, Any],
    authenticated: bool = Depends(authenticate_request)
):
    """Analyze live session data and trigger streaming AI analysis"""
    try:
        analysis = await realtime_ai_service.process_live_session_data(session_id, session_data)
        
        return {
            "success": True,
            "analysis": {
                "analysis_id": analysis.analysis_id,
                "emotional_state": analysis.emotional_state,
                "engagement_level": analysis.engagement_level,
                "attention_score": analysis.attention_score,
                "overstimulation_risk": analysis.overstimulation_risk,
                "intervention_needed": analysis.intervention_needed,
                "immediate_recommendations": analysis.immediate_recommendations,
                "confidence_score": analysis.confidence_score
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing live session data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze session data: {str(e)}")

@router.get("/sessions/{session_id}/dashboard")
async def get_live_dashboard(
    session_id: str,
    authenticated: bool = Depends(authenticate_request)
):
    """Get real-time dashboard data for a session"""
    try:
        dashboard_data = await realtime_ai_service.get_live_session_dashboard(session_id)
        
        if "error" in dashboard_data:
            raise HTTPException(status_code=404, detail=dashboard_data["error"])
        
        return {
            "success": True,
            "dashboard": dashboard_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting live dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@router.post("/sessions/{session_id}/recommendations")
async def generate_live_recommendations(
    session_id: str,
    context: Dict[str, Any],
    authenticated: bool = Depends(authenticate_request)
):
    """Generate live recommendations for ongoing session"""
    try:
        recommendations = await realtime_ai_service.generate_live_recommendations(session_id, context)
        
        return {
            "success": True,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error generating live recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/sessions/{session_id}/overstimulation-patterns")
async def detect_overstimulation_patterns(
    session_id: str,
    authenticated: bool = Depends(authenticate_request)
):
    """Detect overstimulation patterns in real-time"""
    try:
        patterns = await realtime_ai_service.detect_overstimulation_patterns(session_id)
        
        if "error" in patterns:
            raise HTTPException(status_code=404, detail=patterns["error"])
        
        return {
            "success": True,
            "patterns": patterns
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting overstimulation patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to detect patterns: {str(e)}")

@router.post("/sessions/{session_id}/end")
async def end_live_monitoring(
    session_id: str,
    authenticated: bool = Depends(authenticate_request)
):
    """End live monitoring and generate session summary"""
    try:
        summary = await realtime_ai_service.end_live_session_monitoring(session_id)
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        
        return {
            "success": True,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending live monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to end monitoring: {str(e)}")

@router.get("/sessions/active")
async def get_active_sessions(authenticated: bool = Depends(authenticate_request)):
    """Get all active real-time monitoring sessions"""
    try:
        active_sessions = []
        
        for session_id, metrics in realtime_ai_service.active_sessions.items():
            session_duration = (datetime.now() - metrics.start_time).total_seconds() / 60
            recent_analyses = realtime_ai_service.streaming_analyses.get(session_id, [])[-3:]
            active_alerts = [alert for alert in realtime_ai_service.session_alerts.get(session_id, []) 
                           if not alert.auto_resolved]
            
            active_sessions.append({
                "session_id": session_id,
                "child_id": metrics.child_id,
                "duration_minutes": round(session_duration, 2),
                "total_interactions": metrics.total_interactions,
                "recent_analyses_count": len(recent_analyses),
                "active_alerts_count": len(active_alerts),
                "last_update": metrics.last_update.isoformat()
            })
        
        return {
            "success": True,
            "active_sessions": active_sessions,
            "total_count": len(active_sessions)
        }
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get active sessions: {str(e)}")
