from datetime import datetime, timedelta, timezone  # Added timezone import
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session  # Added Session import

from ..models.report_model import (EmotionPattern, GameSessionData,
                                   ReportSummary, GameSession as GameSessionModel)  # SQLAlchemy model, aliased to avoid name clash

# This is a placeholder service. 
# In a real application, this would interact with a database.

# Placeholder storage (in-memory, replace with database)
_game_sessions_db: List[GameSessionData] = []  # This will be replaced by DB interaction

def save_game_session(db: Session, game_data: GameSessionData) -> GameSessionModel:
    """Saves a game session to the database."""
    db_game_session = GameSessionModel(
        child_id=game_data.user_id,  # Assuming user_id from Pydantic model maps to child_id in DB
        game_type=game_data.game_level if game_data.game_level else "Unknown",  # Example: use game_level or a default
        score=game_data.score,
        emotions_data=game_data.emotions_detected,  # Assuming this is a list of dicts suitable for JSON
        played_at=datetime.now(timezone.utc)  # Changed from datetime.utcnow()
    )
    db.add(db_game_session)
    db.commit()
    db.refresh(db_game_session)
    return db_game_session

async def save_game_session_placeholder(session_data: GameSessionData) -> Dict[str, Any]:
    print(f"Received game session data for user {session_data.user_id}")
    _game_sessions_db.append(session_data)
    # In a real scenario, you'd save to DB and return an ID or confirmation
    return {"message": "Game session data received successfully", "session_id": session_data.session_id}

async def generate_child_summary_placeholder(child_id: int) -> Optional[ReportSummary]:
    child_sessions = [s for s in _game_sessions_db if s.user_id == child_id]
    if not child_sessions:
        return None

    total_play_seconds = sum((s.end_time - s.start_time).total_seconds() for s in child_sessions)
    total_play_time_hours = round(total_play_seconds / 3600, 2)

    all_scores = [s.score for s in child_sessions if s.score is not None]
    average_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else None

    # Basic emotion frequency (most frequent dominant emotion)
    emotion_counts: Dict[str, int] = {}
    for session in child_sessions:
        for emo_event in session.emotions_detected:
            emotion = emo_event.get("emotion")
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    most_frequent_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else None

    # Placeholder for progress summary
    progress_summary = {"level_1_status": "completed_mock", "overall_engagement": "high_mock"}

    return ReportSummary(
        child_id=child_id,
        total_play_time_hours=total_play_time_hours,
        average_score=average_score,
        most_frequent_emotion=most_frequent_emotion,
        progress_summary=progress_summary
    )

async def analyze_emotion_patterns_placeholder(child_id: int) -> List[EmotionPattern]:
    child_sessions = [s for s in _game_sessions_db if s.user_id == child_id]
    if not child_sessions:
        return []

    emotion_analysis: Dict[str, Dict[str, Any]] = {}

    for session in child_sessions:
        for emo_event in session.emotions_detected:
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
            triggers=["mock_trigger_1", "mock_trigger_2"] # Placeholder
        ))
    
    return sorted(patterns, key=lambda p: p.frequency, reverse=True)
