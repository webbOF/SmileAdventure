from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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
