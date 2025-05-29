from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from ..models.simple_models import (EmotionPattern, GameSessionData,
                                   ReportSummary)
from ..services import temp_service as report_service

router = APIRouter()

@router.post("/game-session", status_code=201, response_model=Dict[str, Any])
async def submit_game_session_data(
    session_data: GameSessionData
):
    """
    Receive and store data from a completed game session.
    """
    try:
        result = report_service.save_game_session(session_data)
        return {"message": "Game session saved successfully", "session_id": result["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process game session data: {str(e)}")

@router.get("/child/{child_id}/summary", response_model=ReportSummary)
async def get_child_progress_summary(
    child_id: int
):
    """
    Get a summary of a child's progress and overall emotional state.
    """
    try:
        summary = report_service.generate_child_summary(child_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Summary not found for this child.")
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.get("/child/{child_id}/emotion-patterns", response_model=List[EmotionPattern])
async def get_child_emotion_patterns(
    child_id: int
):
    """
    Analyze and retrieve emotional patterns for a child based on game sessions.
    """
    try:
        patterns = report_service.analyze_emotion_patterns(child_id)
        if not patterns:
            return [] 
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze emotion patterns: {str(e)}")

@router.get("/overall-platform-activity", tags=["Admin"])
async def get_platform_activity_overview():
    """
    (Admin) Get an overview of platform activity.
    """
    return {"message": "Platform activity overview endpoint - to be implemented"}
