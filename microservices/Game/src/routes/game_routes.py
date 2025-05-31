from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from ..models.game_models import (EmotionType, EndGameRequest, GameAction,
                                  GameActionData, StartGameRequest)
from ..services.game_service import game_service

router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {"status": "online", "service": "game"}

@router.get("/scenarios", tags=["Game"])
async def get_scenarios():
    """Get available game scenarios"""
    try:
        scenarios = await game_service.get_available_scenarios()
        return scenarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scenarios: {str(e)}")

@router.post("/start", tags=["Game"])
async def start_game_session(request: StartGameRequest):
    """Start a new game session"""
    try:
        result = await game_service.start_game_session(request)
        if result.success:
            return result.dict()
        else:
            raise HTTPException(status_code=400, detail=result.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start game: {str(e)}")

@router.get("/state", tags=["Game"])
async def get_game_state(
    session_id: str = Query(..., description="Game session ID"),
    user_id: int = Query(..., description="User ID")
):
    """Get current game state"""
    try:
        result = await game_service.get_game_state(session_id, user_id)
        if result.success:
            return result.dict()
        else:
            raise HTTPException(status_code=404, detail=result.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get game state: {str(e)}")

@router.post("/action", tags=["Game"])
async def process_game_action(action_data: Dict[str, Any]):
    """Process a game action"""
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
        
        result = await game_service.process_game_action(action)
        if result.success:
            return result.dict()
        else:
            raise HTTPException(status_code=400, detail=result.message)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid action data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process action: {str(e)}")

@router.post("/end", tags=["Game"])
async def end_game_session(request: EndGameRequest):
    """End a game session"""
    try:
        result = await game_service.end_game_session(request)
        if result.success:
            return result.dict()
        else:
            raise HTTPException(status_code=400, detail=result.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end game: {str(e)}")

# Additional endpoints for game management

@router.get("/sessions/active", tags=["Game"])
async def get_active_sessions(user_id: int = Query(..., description="User ID")):
    """Get active game sessions for a user"""
    try:
        active_sessions = []
        for session_id, game_state in game_service.active_sessions.items():
            if game_state.user_id == user_id:
                active_sessions.append({
                    "session_id": session_id,
                    "scenario": game_state.current_scenario,
                    "score": game_state.score,
                    "level": game_state.current_level,
                    "current_objective": game_state.current_objective,
                    "last_updated": game_state.last_updated.isoformat()
                })
        
        return {
            "active_sessions": active_sessions,
            "count": len(active_sessions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active sessions: {str(e)}")

@router.get("/sessions/{session_id}/history", tags=["Game"])
async def get_session_history(
    session_id: str,
    user_id: int = Query(..., description="User ID")
):
    """Get session interaction history"""
    try:
        if session_id not in game_service.session_history:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = game_service.session_history[session_id]
        
        # Verify user owns this session
        if session_data.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to session")
        
        return {
            "session_id": session_id,
            "interactions": session_data.interactions,
            "emotions_detected": session_data.emotions_detected,
            "start_time": session_data.start_time.isoformat(),
            "duration_seconds": session_data.duration_seconds,
            "total_interactions": len(session_data.interactions)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session history: {str(e)}")

@router.get("/leaderboard", tags=["Game"])
async def get_leaderboard(scenario_id: str = Query(None, description="Filter by scenario")):
    """Get game leaderboard"""
    try:
        leaderboard = []
        
        for session_id, session_data in game_service.session_history.items():
            if scenario_id and session_data.scenario_id != scenario_id:
                continue
            
            if session_data.completed and session_data.score is not None:
                leaderboard.append({
                    "user_id": session_data.user_id,
                    "scenario": session_data.scenario_id,
                    "score": session_data.score,
                    "duration_seconds": session_data.duration_seconds,
                    "completion_date": session_data.end_time.isoformat() if session_data.end_time else None
                })
        
        # Sort by score (descending)
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "leaderboard": leaderboard[:10],  # Top 10
            "total_entries": len(leaderboard),
            "scenario_filter": scenario_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")

@router.get("/stats", tags=["Game"])
async def get_game_stats():
    """Get overall game statistics"""
    try:
        total_sessions = len(game_service.session_history)
        active_sessions = len(game_service.active_sessions)
        completed_sessions = sum(1 for session in game_service.session_history.values() if session.completed)
        
        # Calculate average session time
        completed_with_duration = [s for s in game_service.session_history.values() 
                                 if s.completed and s.duration_seconds is not None]
        avg_session_time = sum(s.duration_seconds for s in completed_with_duration) / len(completed_with_duration) if completed_with_duration else 0
        
        # Get most popular scenario
        scenario_counts = {}
        for session in game_service.session_history.values():
            scenario_counts[session.scenario_id] = scenario_counts.get(session.scenario_id, 0) + 1
        
        most_popular_scenario = max(scenario_counts.items(), key=lambda x: x[1]) if scenario_counts else ("N/A", 0)
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "average_session_time_seconds": int(avg_session_time),
            "most_popular_scenario": {
                "name": most_popular_scenario[0],
                "count": most_popular_scenario[1]
            },
            "available_scenarios": len(game_service.scenarios)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get game stats: {str(e)}")