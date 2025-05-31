from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ASDSupportLevel(int, Enum):
    """ASD Support Levels based on DSM-5"""
    LEVEL_1 = 1  # Requiring support
    LEVEL_2 = 2  # Requiring substantial support
    LEVEL_3 = 3  # Requiring very substantial support


class SensoryProfile(str, Enum):
    """Sensory processing preferences"""
    HYPOSENSITIVE = "hyposensitive"  # Seeks more sensory input
    HYPERSENSITIVE = "hypersensitive"  # Overwhelmed by sensory input
    MIXED = "mixed"  # Combination of both
    TYPICAL = "typical"  # Typical sensory processing


class SensorySensitivity(BaseModel):
    """Individual sensory sensitivity settings"""
    auditory: int = Field(default=50, ge=0, le=100, description="Sound sensitivity (0=very sensitive, 100=needs loud)")
    visual: int = Field(default=50, ge=0, le=100, description="Visual sensitivity (0=very sensitive, 100=needs bright)")
    tactile: int = Field(default=50, ge=0, le=100, description="Touch sensitivity")
    vestibular: int = Field(default=50, ge=0, le=100, description="Movement/balance sensitivity")
    proprioceptive: int = Field(default=50, ge=0, le=100, description="Body awareness sensitivity")


class ChildProfile(BaseModel):
    """Comprehensive child profile for ASD support"""
    child_id: int
    name: str
    age: int
    asd_support_level: ASDSupportLevel
    sensory_profile: SensoryProfile
    sensory_sensitivities: SensorySensitivity
    communication_preferences: Dict[str, Any] = Field(default_factory=dict)
    behavioral_patterns: Dict[str, Any] = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)
    calming_strategies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class OverstimulationIndicator(str, Enum):
    """Indicators of sensory overload or overstimulation"""
    RAPID_CLICKING = "rapid_clicking"
    ERRATIC_MOVEMENT = "erratic_movement"
    LONG_PAUSE = "long_pause"
    REPEATED_ACTIONS = "repeated_actions"
    DIFFICULTY_PROGRESSING = "difficulty_progressing"
    HIGH_ERROR_RATE = "high_error_rate"


class AdaptiveSessionConfig(BaseModel):
    """Configuration for adaptive game sessions"""
    session_id: str
    child_profile: ChildProfile
    current_difficulty: int = Field(default=1, ge=1, le=5)
    sensory_adjustments: Dict[str, Any] = Field(default_factory=dict)
    pacing_adjustments: Dict[str, Any] = Field(default_factory=dict)
    content_modifications: Dict[str, Any] = Field(default_factory=dict)
    break_intervals: int = Field(default=300, description="Seconds between suggested breaks")
    overstimulation_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    adaptation_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)


class SessionMetrics(BaseModel):
    """Real-time session performance metrics"""
    session_id: str
    timestamp: datetime
    actions_per_minute: float
    error_rate: float
    pause_frequency: float
    average_response_time: float
    progress_rate: float
    overstimulation_score: float = Field(ge=0.0, le=1.0)
    stress_indicators: List[OverstimulationIndicator] = Field(default_factory=list)


class CalmingIntervention(BaseModel):
    """Calming intervention recommendation"""
    intervention_type: str
    description: str
    duration_seconds: int
    instructions: List[str]
    success_criteria: List[str]


class ASDRecommendation(BaseModel):
    """Clinical and educational recommendations"""
    recommendation_id: str
    child_id: int
    session_id: str
    recommendation_type: str  # "clinical", "educational", "behavioral", "sensory"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    rationale: str
    action_items: List[str]
    resources: List[str] = Field(default_factory=list)
    target_audience: List[str]  # "parent", "teacher", "therapist", "child"
    timeframe: str
    created_at: datetime = Field(default_factory=datetime.now)


class ProgressInsight(BaseModel):
    """Insights from game session analysis"""
    insight_type: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    description: str
    supporting_data: Dict[str, Any]
    recommendations: List[str]


class ASDSessionReport(BaseModel):
    """Comprehensive session report for ASD support"""
    session_id: str
    child_profile: ChildProfile
    session_duration: int  # seconds
    total_interactions: int
    adaptations_made: List[Dict[str, Any]]
    overstimulation_events: List[Dict[str, Any]]
    calming_interventions_used: List[CalmingIntervention]
    progress_insights: List[ProgressInsight]
    recommendations: List[ASDRecommendation]
    parent_summary: str
    professional_notes: str
    created_at: datetime = Field(default_factory=datetime.now)
