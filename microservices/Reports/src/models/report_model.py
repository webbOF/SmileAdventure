from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)

from ..db.session import Base  # If using SQLAlchemy


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, index=True) # Assuming child_id is an integer. Add ForeignKey('users.id') if direct relation is planned and 'users' table exists in this DB.
    game_type = Column(String, index=True)
    score = Column(Integer)
    emotions_data = Column(JSON) # Using JSON type for flexibility. Use Text if JSON is not supported or preferred.
    played_at = Column(DateTime, default=datetime.utcnow)

class GameSessionData(BaseModel):
    user_id: int # or child_id
    session_id: str
    start_time: datetime
    end_time: datetime
    emotions_detected: List[Dict[str, Any]] # e.g., [{"emotion": "happy", "timestamp": "...", "intensity": 0.8}]
    game_level: Optional[str] = None
    score: Optional[int] = None
    # other relevant game metrics

class ReportSummary(BaseModel):
    child_id: int
    total_play_time_hours: float 
    average_score: Optional[float] = None
    most_frequent_emotion: Optional[str] = None
    progress_summary: Optional[Dict[str, Any]] = None # e.g. {"level_1": "completed", "level_2": "in_progress"}

class EmotionPattern(BaseModel):
    emotion: str
    frequency: int # How many times this emotion was dominant or significantly present
    average_intensity: Optional[float] = None
    triggers: Optional[List[str]] = None # Events or game parts that often trigger this emotion
