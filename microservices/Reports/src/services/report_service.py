from datetime import (datetime,  # Removed timedelta, not used in new logic
                      timezone)
from typing import Any, Dict, List, Optional

from sqlalchemy import func  # Added for aggregate functions like COUNT, AVG
from sqlalchemy.orm import Session

from ..models.report_model import (
    EmotionPattern,
    GameSession as GameSessionModel,
    GameSessionData,
    ReportSummary
)


def save_game_session(db: Session, game_data: GameSessionData) -> GameSessionModel:
    """Saves a game session to the database."""
    db_game_session = GameSessionModel(
        child_id=game_data.user_id,
        game_type=game_data.game_level if game_data.game_level else "Unknown",
        score=game_data.score,
        emotions_data=game_data.emotions_detected,
        played_at=datetime.now(timezone.utc)
    )
    db.add(db_game_session)
    db.commit()
    db.refresh(db_game_session)
    return db_game_session

# Removed save_game_session_placeholder as save_game_session is the actual implementation

def generate_child_summary(db: Session, child_id: int) -> Optional[ReportSummary]:
    """Generates a summary report for a child based on their game sessions from the database."""
    child_sessions = db.query(GameSessionModel).filter(GameSessionModel.child_id == child_id).all()

    if not child_sessions:
        return None

    # total_play_time_hours: Cannot be accurately calculated from current GameSessionModel.
    # GameSessionModel only has 'played_at'. If 'emotions_data' contains start/end or duration,
    # that logic would be complex here. For now, returning a placeholder.
    # If individual session durations were stored, we could sum them.
    total_play_time_hours = 0.0 # Placeholder

    all_scores = [s.score for s in child_sessions if s.score is not None]
    average_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else None

    emotion_counts: Dict[str, int] = {}
    for session in child_sessions:
        if session.emotions_data: # Ensure emotions_data is not None
            for emo_event in session.emotions_data: # Assuming emotions_data is a list of dicts
                if isinstance(emo_event, dict):
                    emotion = emo_event.get("emotion")
                    if emotion:
                        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    most_frequent_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else None

    # Placeholder for progress summary - this would likely involve more complex logic
    # based on game types, levels completed, etc.
    progress_summary = {"overall_engagement": "moderate_mock"} # Updated placeholder

    return ReportSummary(
        child_id=child_id,
        total_play_time_hours=total_play_time_hours,
        average_score=average_score,
        most_frequent_emotion=most_frequent_emotion,
        progress_summary=progress_summary
    )

def analyze_emotion_patterns(db: Session, child_id: int) -> List[EmotionPattern]:
    """Analyzes emotion patterns for a child from their game sessions in the database."""
    child_sessions = db.query(GameSessionModel).filter(GameSessionModel.child_id == child_id).all()

    if not child_sessions:
        return []

    emotion_analysis: Dict[str, Dict[str, Any]] = {}

    for session in child_sessions:
        if session.emotions_data: # Ensure emotions_data is not None
            for emo_event in session.emotions_data: # Assuming emotions_data is a list of dicts
                if isinstance(emo_event, dict):
                    emotion = emo_event.get("emotion")
                    intensity = emo_event.get("intensity") # Assuming intensity is part of the dict
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
        
        # Placeholder for triggers - this would require more detailed event logging
        patterns.append(EmotionPattern(
            emotion=emotion,
            frequency=data["count"],
            average_intensity=avg_intensity,
            triggers=["trigger_placeholder_db"] 
        ))
    
    return patterns

# Placeholder for fetching detailed session data - can be expanded later
def get_session_details(db: Session, session_id: int) -> Optional[GameSessionModel]:
    return db.query(GameSessionModel).filter(GameSessionModel.id == session_id).first()

# Placeholder for fetching all sessions for a child - can be expanded later
def get_all_child_sessions(db: Session, child_id: int) -> List[GameSessionModel]:
    return db.query(GameSessionModel).filter(GameSessionModel.child_id == child_id).order_by(GameSessionModel.played_at.desc()).all()
