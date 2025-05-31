from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class GameAction(str, Enum):
    """Available game actions"""
    MOVE = "move"
    INTERACT = "interact"
    SELECT = "select"
    ANSWER = "answer"
    COMPLETE = "complete"

class EmotionType(str, Enum):
    """Emotion types that can be detected/expressed in game"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    CALM = "calm"
    CONFUSED = "confused"
    PROUD = "proud"

class GameSessionData(BaseModel):
    """Model for game session data"""
    user_id: int
    session_id: str
    child_id: Optional[int] = None
    scenario_id: str
    difficulty_level: int = 1
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    completed: bool = False
    score: Optional[int] = None
    emotions_detected: List[EmotionType] = []
    interactions: List[Dict[str, Any]] = []
    progress_data: Dict[str, Any] = {}

class GameActionData(BaseModel):
    """Model for individual game actions"""
    session_id: str
    user_id: int
    action_type: GameAction
    target: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    response: Optional[str] = None
    emotion_detected: Optional[EmotionType] = None
    timestamp: datetime
    context: Dict[str, Any] = {}

class GameState(BaseModel):
    """Current state of a game session"""
    session_id: str
    user_id: int
    current_scenario: str
    current_level: int
    score: int
    health: int = 100
    position: Dict[str, float] = {"x": 0, "y": 0}
    inventory: List[str] = []
    completed_objectives: List[str] = []
    current_objective: Optional[str] = None
    emotions_state: Dict[EmotionType, int] = {}
    last_updated: datetime

class StartGameRequest(BaseModel):
    """Request to start a new game session"""
    user_id: int
    child_id: Optional[int] = None
    scenario_id: str = "basic_adventure"
    difficulty_level: int = 1

class EndGameRequest(BaseModel):
    """Request to end a game session"""
    session_id: str
    user_id: int
    final_score: Optional[int] = None
    completion_reason: str = "normal"

class GameResponse(BaseModel):
    """Standard game response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
