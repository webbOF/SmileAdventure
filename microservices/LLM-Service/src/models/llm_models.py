from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ===========================
# CORE DATA MODELS
# ===========================

class EmotionType(str, Enum):
    """Emotion types that can be detected/expressed in game"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    DISGUSTED = "disgusted"
    CALM = "calm"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    CONFUSED = "confused"
    FRUSTRATED = "frustrated"
    CONTENT = "content"
    OVERWHELMED = "overwhelmed"

class BehavioralPattern(str, Enum):
    """Types of behavioral patterns to track"""
    SOCIAL_INTERACTION = "social_interaction"
    COMMUNICATION = "communication"
    REPETITIVE_BEHAVIOR = "repetitive_behavior"
    SENSORY_PROCESSING = "sensory_processing"
    EMOTIONAL_REGULATION = "emotional_regulation"
    ATTENTION_REGULATION = "attention_regulation"
    ADAPTIVE_BEHAVIOR = "adaptive_behavior"
    TRANSITION_BEHAVIOR = "transition_behavior"

class AnalysisType(str, Enum):
    """Types of analysis to perform"""
    COMPREHENSIVE = "comprehensive"
    EMOTIONAL_ONLY = "emotional_only"
    BEHAVIORAL_ONLY = "behavioral_only"
    PROGRESS_TRACKING = "progress_tracking"
    INTERVENTION_FOCUSED = "intervention_focused"

class GameSessionData(BaseModel):
    """Game session data for analysis"""
    user_id: int
    session_id: str
    child_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    emotions_detected: List[Dict[str, Any]] = Field(default_factory=list)
    game_level: Optional[str] = None
    score: Optional[int] = None
    interactions: List[Dict[str, Any]] = Field(default_factory=list)
    behavioral_observations: List[Dict[str, Any]] = Field(default_factory=list)
    emotional_transitions: List[Dict[str, Any]] = Field(default_factory=list)
    progress_metrics: Dict[str, Any] = Field(default_factory=dict)
    environmental_factors: Dict[str, Any] = Field(default_factory=dict)
    interventions_used: List[Dict[str, Any]] = Field(default_factory=list)

# ===========================
# REQUEST/RESPONSE MODELS
# ===========================

class LLMAnalysisRequest(BaseModel):
    """Request for LLM analysis of game session"""
    session_data: GameSessionData
    analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE
    include_recommendations: bool = True
    child_context: Optional[Dict[str, Any]] = None
    previous_sessions: Optional[List[GameSessionData]] = None

class SessionInsights(BaseModel):
    """Insights extracted from session analysis"""
    overall_engagement: float = Field(..., ge=0.0, le=1.0, description="Overall engagement score")
    emotional_stability: float = Field(..., ge=0.0, le=1.0, description="Emotional stability score")
    social_interaction_quality: float = Field(..., ge=0.0, le=1.0, description="Quality of social interactions")
    learning_progress: float = Field(..., ge=0.0, le=1.0, description="Learning progress score")
    attention_span: float = Field(..., ge=0.0, le=1.0, description="Attention span score")
    key_observations: List[str] = Field(default_factory=list)
    positive_moments: List[str] = Field(default_factory=list)
    concerning_behaviors: List[str] = Field(default_factory=list)
    breakthrough_moments: List[str] = Field(default_factory=list)

class EmotionalAnalysis(BaseModel):
    """Detailed emotional analysis of session"""
    dominant_emotions: List[str] = Field(default_factory=list)
    emotional_transitions: List[Dict[str, Any]] = Field(default_factory=list)
    regulation_events: List[Dict[str, Any]] = Field(default_factory=list)
    emotional_stability_score: float = Field(..., ge=0.0, le=1.0)
    regulation_success_rate: float = Field(..., ge=0.0, le=1.0)
    triggers_identified: List[str] = Field(default_factory=list)
    calming_strategies_effective: List[str] = Field(default_factory=list)
    emotional_pattern_insights: List[str] = Field(default_factory=list)

class BehavioralAnalysis(BaseModel):
    """Detailed behavioral analysis of session"""
    behavioral_patterns_observed: List[BehavioralPattern] = Field(default_factory=list)
    social_engagement_level: float = Field(..., ge=0.0, le=1.0)
    communication_effectiveness: float = Field(..., ge=0.0, le=1.0)
    sensory_processing_indicators: Dict[str, Any] = Field(default_factory=dict)
    repetitive_behaviors: List[Dict[str, Any]] = Field(default_factory=list)
    adaptive_responses: List[Dict[str, Any]] = Field(default_factory=list)
    attention_patterns: Dict[str, Any] = Field(default_factory=dict)
    behavioral_insights: List[str] = Field(default_factory=list)

class ProgressAnalysis(BaseModel):
    """Analysis of progress over time"""
    overall_progress_trend: str = Field(..., description="improving, stable, declining, or mixed")
    skill_development_trends: Dict[str, str] = Field(default_factory=dict)
    milestone_achievements: List[Dict[str, Any]] = Field(default_factory=list)
    areas_of_improvement: List[str] = Field(default_factory=list)
    areas_needing_attention: List[str] = Field(default_factory=list)
    progress_insights: List[str] = Field(default_factory=list)
    comparative_analysis: Dict[str, Any] = Field(default_factory=dict)

class Recommendations(BaseModel):
    """Personalized recommendations based on analysis"""
    immediate_interventions: List[str] = Field(default_factory=list)
    session_adjustments: List[str] = Field(default_factory=list)
    environmental_modifications: List[str] = Field(default_factory=list)
    skill_development_focus: List[str] = Field(default_factory=list)
    parent_guidance: List[str] = Field(default_factory=list)
    clinical_considerations: List[str] = Field(default_factory=list)
    next_session_preparation: List[str] = Field(default_factory=list)
    long_term_goals: List[str] = Field(default_factory=list)

class LLMAnalysisResponse(BaseModel):
    """Complete response from LLM analysis"""
    session_id: str
    child_id: Optional[int]
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_type: AnalysisType
    insights: SessionInsights
    emotional_analysis: EmotionalAnalysis
    behavioral_analysis: BehavioralAnalysis
    progress_analysis: Optional[ProgressAnalysis] = None
    recommendations: Recommendations
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in analysis")
    model_used: str = Field(default="gpt-4")
    analysis_notes: Optional[str] = None

class LLMHealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="healthy, degraded, or unhealthy")
    timestamp: datetime
    openai_status: str = Field(..., description="connected, disconnected, or limited")
    service_version: str
    error: Optional[str] = None
    response_time_ms: Optional[float] = None

# ===========================
# CHILD CONTEXT MODELS
# ===========================

class ChildContext(BaseModel):
    """Context information about the child for better analysis"""
    child_id: int
    age: int
    asd_support_level: int = Field(..., ge=1, le=3, description="ASD support level (1-3)")
    communication_preferences: List[str] = Field(default_factory=list)
    sensory_sensitivities: Dict[str, Any] = Field(default_factory=dict)
    behavioral_patterns: List[str] = Field(default_factory=list)
    current_goals: List[str] = Field(default_factory=list)
    intervention_history: List[Dict[str, Any]] = Field(default_factory=list)
    family_context: Optional[Dict[str, Any]] = None

# ===========================
# ANALYSIS CONFIGURATION
# ===========================

class AnalysisConfig(BaseModel):
    """Configuration for LLM analysis"""
    model_name: str = "gpt-4"
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=100, le=4000)
    include_emotional_analysis: bool = True
    include_behavioral_analysis: bool = True
    include_progress_tracking: bool = True
    include_recommendations: bool = True
    focus_areas: List[str] = Field(default_factory=list)
    analysis_depth: str = Field(default="comprehensive", description="quick, standard, or comprehensive")
