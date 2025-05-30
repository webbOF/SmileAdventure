from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from sqlalchemy import JSON, Column, DateTime, Integer, String

from ..db.session import Base


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, index=True)
    game_type = Column(String, index=True)
    score = Column(Integer)
    emotions_data = Column(JSON)
    played_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GameSessionData(BaseModel):
    user_id: int
    session_id: str
    start_time: datetime
    end_time: datetime
    emotions_detected: List[Dict[str, Any]]
    game_level: Optional[str] = None
    score: Optional[int] = None

    class Config:
        from_attributes = True


class ReportSummary(BaseModel):
    child_id: int
    total_play_time_hours: float
    average_score: Optional[float] = None
    most_frequent_emotion: Optional[str] = None
    progress_summary: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class EmotionPattern(BaseModel):
    emotion: str
    frequency: int
    average_intensity: Optional[float] = None
    triggers: Optional[List[str]] = None

    class Config:
        from_attributes = True
