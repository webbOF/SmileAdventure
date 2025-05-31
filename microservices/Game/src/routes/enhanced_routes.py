"""
Enhanced Game Routes with integrated ASD support
"""
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from ..models.asd_models import ChildProfile
from ..models.game_models import (EmotionType, EndGameRequest, GameAction,
                                  GameActionData, StartGameRequest)
from ..services.enhanced_game_service import enhanced_game_service

# Constants
USER_ID_DESCRIPTION = "User ID"

router = APIRouter(prefix="/enhanced", tags=["Enhanced Game"])

@router.post("/start", tags=["Enhanced Game"])
async def start_enhanced_game_session(
    request: StartGameRequest,
    child_profile: Optional[ChildProfile] = None
):
    """Start an enhanced game session with optional ASD adaptive features"""
    try:
        result = await enhanced_game_service.start_adaptive_game_session(request, child_profile)
        if result.success:
            return result.dict()
        else:
            raise HTTPException(status_code=400, detail=result.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start enhanced game: {str(e)}")

@router.post("/action", tags=["Enhanced Game"])
async def process_enhanced_game_action(action_data: Dict[str, Any]):
    """Process a game action with ASD monitoring and real-time adaptation"""
    try:
        # Convert dict to GameActionData model
        action = GameActionData(
            session_id=action_data.get("session_id"),
            user_id=action_data.get("user_id"),
            action_type=GameAction(action_data.get("action_type")),
            target=action_data.get("target"),
            position=action_data.get("position"),
            response=action_data.get("response"),
            emotion_detected=EmotionType(action_data.get("emotion_detected")) if action_data.get("emotion_detected") else None,
            timestamp=datetime.now(),
            context=action_data.get("context", {})
        )
        
        result = await enhanced_game_service.process_enhanced_game_action(action)
        if result.success:
            return result.dict()
        else:
            raise HTTPException(status_code=400, detail=result.message)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid action data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process enhanced action: {str(e)}")

@router.post("/end", tags=["Enhanced Game"])
async def end_enhanced_game_session(request: EndGameRequest):
    """End an enhanced game session with comprehensive ASD reporting"""
    try:
        result = await enhanced_game_service.end_enhanced_game_session(request)
        if result.success:
            return result.dict()
        else:
            raise HTTPException(status_code=400, detail=result.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end enhanced game: {str(e)}")

@router.get("/state", tags=["Enhanced Game"])
async def get_enhanced_game_state(
    session_id: str = Query(..., description="Game session ID"),
    user_id: int = Query(..., description=USER_ID_DESCRIPTION)
):
    """Get current enhanced game state"""
    try:
        result = await enhanced_game_service.get_game_state(session_id, user_id)
        if result.success:
            # Add ASD monitoring status
            asd_enabled = enhanced_game_service.asd_enabled_sessions.get(session_id, False)
            result.data["asd_enabled"] = asd_enabled
            
            # Add real-time metrics if ASD is enabled
            if asd_enabled:
                current_metrics = enhanced_game_service.asd_service.session_metrics.get(session_id, [])
                if current_metrics:
                    latest_metrics = current_metrics[-1]
                    result.data["current_overstimulation_score"] = latest_metrics.overstimulation_score
                    result.data["recent_indicators"] = latest_metrics.stress_indicators
            
            return result.dict()
        else:
            raise HTTPException(status_code=404, detail=result.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced game state: {str(e)}")

@router.get("/report/{session_id}", tags=["Enhanced Game"])
async def get_session_report(
    session_id: str,
    user_id: int = Query(..., description=USER_ID_DESCRIPTION)
):
    """Get comprehensive session report with ASD insights"""
    try:
        report = await enhanced_game_service.generate_session_report(session_id, user_id)
        
        if "error" in report:
            if "not found" in report["error"].lower():
                raise HTTPException(status_code=404, detail=report["error"])
            elif "unauthorized" in report["error"].lower():
                raise HTTPException(status_code=403, detail=report["error"])
            else:
                raise HTTPException(status_code=500, detail=report["error"])
        
        return {
            "success": True,
            "message": "Session report generated successfully",
            "data": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate session report: {str(e)}")

@router.get("/scenarios", tags=["Enhanced Game"])
async def get_enhanced_scenarios():
    """Get available game scenarios with ASD adaptation information"""
    try:
        scenarios = await enhanced_game_service.get_available_scenarios()
        
        # Enhance scenarios with ASD adaptation info
        enhanced_scenarios = {}
        for scenario_id, scenario_data in scenarios.get("scenarios", {}).items():
            enhanced_scenarios[scenario_id] = {
                **scenario_data,
                "asd_adaptations": {
                    "sensory_modifications": "Automatic brightness, sound, and animation adjustments",
                    "pacing_adaptations": "Customized timing based on support level",
                    "content_personalization": "Integration of special interests and trigger avoidance",
                    "calming_interventions": "Built-in break suggestions and calming exercises",
                    "progress_monitoring": "Real-time overstimulation detection and response"
                },
                "recommended_for_asd": True
            }
        
        return {
            "success": True,
            "scenarios": enhanced_scenarios,
            "asd_features_available": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced scenarios: {str(e)}")

@router.get("/monitoring/{session_id}", tags=["Enhanced Game"])
async def get_real_time_monitoring(
    session_id: str,
    user_id: int = Query(..., description=USER_ID_DESCRIPTION)
):
    """Get real-time ASD monitoring data for a session"""
    try:
        # Verify session exists and user has access
        game_state = enhanced_game_service.game_service.active_sessions.get(session_id)
        if not game_state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if game_state.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        
        # Check if ASD monitoring is enabled
        asd_enabled = enhanced_game_service.asd_enabled_sessions.get(session_id, False)
        if not asd_enabled:
            return {
                "success": True,
                "asd_enabled": False,
                "message": "ASD monitoring not enabled for this session"
            }
        
        # Get monitoring data
        metrics = enhanced_game_service.asd_service.session_metrics.get(session_id, [])
        config = enhanced_game_service.asd_service.adaptive_sessions.get(session_id)
        
        monitoring_data = {
            "session_id": session_id,
            "asd_enabled": True,
            "current_status": "active",
            "metrics_count": len(metrics),
            "adaptive_config": config.dict() if config else None
        }
        
        if metrics:
            latest_metrics = metrics[-1]
            monitoring_data.update({
                "latest_overstimulation_score": latest_metrics.overstimulation_score,
                "current_indicators": latest_metrics.stress_indicators,
                "actions_per_minute": latest_metrics.actions_per_minute,
                "error_rate": latest_metrics.error_rate,
                "progress_rate": latest_metrics.progress_rate
            })
            
            # Calculate trends from recent metrics
            if len(metrics) >= 3:
                recent_scores = [m.overstimulation_score for m in metrics[-3:]]
                trend = "increasing" if recent_scores[-1] > recent_scores[0] else "decreasing"
                monitoring_data["overstimulation_trend"] = trend
        
        return {
            "success": True,
            "data": monitoring_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring data: {str(e)}")
