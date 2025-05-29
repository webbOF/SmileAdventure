from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Use absolute imports when running directly
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models.simple_models import GameSessionData, ReportSummary, EmotionPattern

# Temporary in-memory storage for testing
game_sessions_storage = []

def save_game_session(game_data: GameSessionData, db=None) -> Dict[str, Any]:
    """Saves a game session (temporarily to memory for testing)."""
    session_record = {
        "id": len(game_sessions_storage) + 1,
        "child_id": game_data.user_id,
        "game_type": game_data.game_level or "Unknown",
        "score": game_data.score,
        "emotions_data": game_data.emotions_detected,
        "played_at": datetime.now(timezone.utc),
        "session_id": game_data.session_id
    }
    game_sessions_storage.append(session_record)
    return session_record

def generate_child_summary(child_id: int, db=None) -> Optional[ReportSummary]:
    """Generates a summary report for a child based on their game sessions."""
    child_sessions = [s for s in game_sessions_storage if s["child_id"] == child_id]

    if not child_sessions:
        return None

    # Calculate total play time (placeholder - would need start/end times)
    total_play_time_hours = len(child_sessions) * 0.5  # Assume 30min per session

    # Calculate average score
    all_scores = [s["score"] for s in child_sessions if s["score"] is not None]
    average_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else None

    # Calculate most frequent emotion
    emotion_counts = {}
    for session in child_sessions:
        if session["emotions_data"]:
            for emo_event in session["emotions_data"]:
                if isinstance(emo_event, dict):
                    emotion = emo_event.get("emotion")
                    if emotion:
                        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    most_frequent_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else None

    # Progress summary
    progress_summary = {
        "total_sessions": len(child_sessions),
        "games_played": list(set(s["game_type"] for s in child_sessions)),
        "overall_engagement": "good" if len(child_sessions) > 3 else "moderate"
    }

    return ReportSummary(
        child_id=child_id,
        total_play_time_hours=total_play_time_hours,
        average_score=average_score,
        most_frequent_emotion=most_frequent_emotion,
        progress_summary=progress_summary
    )

def analyze_emotion_patterns(child_id: int, db=None) -> List[EmotionPattern]:
    """Analyzes emotion patterns for a child from their game sessions."""
    child_sessions = [s for s in game_sessions_storage if s["child_id"] == child_id]

    if not child_sessions:
        return []

    emotion_analysis = {}

    for session in child_sessions:
        if session["emotions_data"]:
            for emo_event in session["emotions_data"]:
                if isinstance(emo_event, dict):
                    emotion = emo_event.get("emotion")
                    intensity = emo_event.get("intensity")
                    if emotion:
                        if emotion not in emotion_analysis:
                            emotion_analysis[emotion] = {"count": 0, "total_intensity": 0.0, "intensity_records": 0}
                        emotion_analysis[emotion]["count"] += 1
                        if isinstance(intensity, (int, float)):
                            emotion_analysis[emotion]["total_intensity"] += intensity
                            emotion_analysis[emotion]["intensity_records"] += 1
    
    patterns = []
    for emotion, data in emotion_analysis.items():
        avg_intensity = None
        if data["intensity_records"] > 0:
            avg_intensity = round(data["total_intensity"] / data["intensity_records"], 2)
        
        patterns.append(EmotionPattern(
            emotion=emotion,
            frequency=data["count"],
            average_intensity=avg_intensity,
            triggers=["game_interaction", "level_completion"] # Placeholder triggers
        ))
    
    return patterns

def get_all_sessions() -> List[Dict[str, Any]]:
    """Get all stored sessions for debugging."""
    return game_sessions_storage

def clear_all_sessions():
    """Clear all stored sessions for testing."""
    global game_sessions_storage
    game_sessions_storage = []
