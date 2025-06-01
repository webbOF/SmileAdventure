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

# ===========================
# ENHANCED PROGRESS TRACKING MODELS
# ===========================

class BehavioralPattern(str, Enum):
    """Types of behavioral patterns to track"""
    ATTENTION_REGULATION = "attention_regulation"
    EMOTIONAL_REGULATION = "emotional_regulation"
    SENSORY_PROCESSING = "sensory_processing"
    SOCIAL_INTERACTION = "social_interaction"
    COMMUNICATION = "communication"
    ADAPTIVE_BEHAVIOR = "adaptive_behavior"
    REPETITIVE_BEHAVIOR = "repetitive_behavior"
    TRANSITION_BEHAVIOR = "transition_behavior"


class EmotionalState(str, Enum):
    """Emotional states for tracking progression"""
    CALM = "calm"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    HAPPY = "happy"
    CURIOUS = "curious"
    OVERWHELMED = "overwhelmed"
    ENGAGED = "engaged"
    WITHDRAWN = "withdrawn"
    REGULATED = "regulated"


class ClinicalMilestone(str, Enum):
    """ASD-specific clinical milestones"""
    # Communication milestones
    FIRST_INTENTIONAL_COMMUNICATION = "first_intentional_communication"
    IMPROVED_EYE_CONTACT = "improved_eye_contact"
    VERBAL_INITIATION = "verbal_initiation"
    SOCIAL_REFERENCING = "social_referencing"
    
    # Behavioral milestones
    SELF_REGULATION_SKILL = "self_regulation_skill"
    FLEXIBILITY_IMPROVEMENT = "flexibility_improvement"
    REDUCED_RIGIDITY = "reduced_rigidity"
    COPING_STRATEGY_USE = "coping_strategy_use"
    
    # Social milestones
    PEER_INTERACTION_ATTEMPT = "peer_interaction_attempt"
    TURN_TAKING_SUCCESS = "turn_taking_success"
    SHARED_ATTENTION = "shared_attention"
    EMPATHY_DEMONSTRATION = "empathy_demonstration"
    
    # Learning milestones
    GENERALIZATION_SKILL = "generalization_skill"
    PROBLEM_SOLVING_IMPROVEMENT = "problem_solving_improvement"
    MEMORY_RETENTION_GAIN = "memory_retention_gain"
    PROCESSING_SPEED_IMPROVEMENT = "processing_speed_improvement"


class ProgressTrend(str, Enum):
    """Progress trend indicators"""
    SIGNIFICANT_IMPROVEMENT = "significant_improvement"
    MODERATE_IMPROVEMENT = "moderate_improvement"
    STABLE = "stable"
    MINOR_DECLINE = "minor_decline"
    CONCERNING_DECLINE = "concerning_decline"
    INCONSISTENT = "inconsistent"


class BehavioralDataPoint(BaseModel):
    """Individual behavioral observation data point"""
    timestamp: datetime
    behavior_type: BehavioralPattern
    intensity: float = Field(ge=0.0, le=1.0, description="Intensity of behavior (0-1)")
    duration_seconds: int
    context: Dict[str, Any] = Field(default_factory=dict)
    trigger: Optional[str] = None
    intervention_used: Optional[str] = None
    effectiveness_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class EmotionalStateTransition(BaseModel):
    """Tracks emotional state changes during sessions"""
    timestamp: datetime
    from_state: EmotionalState
    to_state: EmotionalState
    trigger_event: Optional[str] = None
    transition_duration: float  # seconds
    support_needed: bool = False
    regulation_strategy_used: Optional[str] = None


class SkillAssessment(BaseModel):
    """Assessment of specific skills"""
    skill_name: str
    skill_category: str  # "communication", "social", "cognitive", "behavioral"
    baseline_score: float = Field(ge=0.0, le=1.0)
    current_score: float = Field(ge=0.0, le=1.0)
    target_score: float = Field(ge=0.0, le=1.0)
    assessment_date: datetime
    assessment_method: str
    notes: str = ""


class ClinicalMilestoneEvent(BaseModel):
    """Records achievement of clinical milestones"""
    milestone: ClinicalMilestone
    achieved_at: datetime
    session_id: str
    description: str
    confidence_level: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    clinical_significance: str  # "high", "medium", "low"
    next_target_milestone: Optional[ClinicalMilestone] = None


class BehavioralPatternAnalysis(BaseModel):
    """Analysis of behavioral patterns over time"""
    pattern_type: BehavioralPattern
    analysis_period_days: int
    frequency_per_session: float
    average_intensity: float = Field(ge=0.0, le=1.0)
    trend: ProgressTrend
    triggers_identified: List[str] = Field(default_factory=list)
    effective_interventions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)


class EmotionalProgressProfile(BaseModel):
    """Comprehensive emotional development tracking"""
    child_id: int
    assessment_date: datetime
    predominant_states: List[EmotionalState] = Field(default_factory=list)
    regulation_ability_score: float = Field(ge=0.0, le=1.0)
    emotional_range_score: float = Field(ge=0.0, le=1.0)  # Variety of emotions expressed
    transition_smoothness: float = Field(ge=0.0, le=1.0)  # How well they handle emotional changes
    trigger_sensitivity: Dict[str, float] = Field(default_factory=dict)
    coping_strategies_effectiveness: Dict[str, float] = Field(default_factory=dict)
    social_emotional_skills: Dict[str, float] = Field(default_factory=dict)


class CognitiveProgressMetrics(BaseModel):
    """Cognitive development and learning progress"""
    child_id: int
    assessment_date: datetime
    attention_span_progression: List[float] = Field(default_factory=list)  # seconds over time
    processing_speed_score: float = Field(ge=0.0, le=1.0)
    working_memory_score: float = Field(ge=0.0, le=1.0)
    problem_solving_score: float = Field(ge=0.0, le=1.0)
    learning_transfer_ability: float = Field(ge=0.0, le=1.0)  # Generalization
    cognitive_flexibility_score: float = Field(ge=0.0, le=1.0)
    executive_function_score: float = Field(ge=0.0, le=1.0)


class SensoryProgressProfile(BaseModel):
    """Sensory processing development tracking"""
    child_id: int
    assessment_date: datetime
    sensory_tolerance_improvements: Dict[str, float] = Field(default_factory=dict)
    self_regulation_strategies: List[str] = Field(default_factory=list)
    overload_frequency_trend: ProgressTrend
    seeking_behavior_trend: ProgressTrend
    preferred_sensory_inputs: List[str] = Field(default_factory=list)
    avoided_sensory_inputs: List[str] = Field(default_factory=list)
    sensory_diet_effectiveness: Dict[str, float] = Field(default_factory=dict)


class SocialCommunicationProgress(BaseModel):
    """Social and communication skill development"""
    child_id: int
    assessment_date: datetime
    eye_contact_frequency: float = Field(ge=0.0, le=1.0)
    social_initiation_rate: float
    turn_taking_success_rate: float = Field(ge=0.0, le=1.0)
    joint_attention_score: float = Field(ge=0.0, le=1.0)
    communication_complexity_score: float = Field(ge=0.0, le=1.0)
    social_reciprocity_score: float = Field(ge=0.0, le=1.0)
    peer_interaction_quality: float = Field(ge=0.0, le=1.0)


class ProgressGoal(BaseModel):
    """Individual progress goals and tracking"""
    goal_id: str
    child_id: int
    goal_category: str  # "behavioral", "social", "communication", "cognitive", "sensory"
    goal_description: str
    target_date: datetime
    baseline_measurement: float = Field(ge=0.0, le=1.0)
    current_measurement: float = Field(ge=0.0, le=1.0)
    target_measurement: float = Field(ge=0.0, le=1.0)
    measurement_method: str
    progress_markers: List[str] = Field(default_factory=list)
    obstacles_identified: List[str] = Field(default_factory=list)
    support_strategies: List[str] = Field(default_factory=list)
    status: str  # "active", "achieved", "modified", "paused"


class LongTermProgressReport(BaseModel):
    """Comprehensive long-term progress report"""
    child_id: int
    report_period_start: datetime
    report_period_end: datetime
    milestones_achieved: List[ClinicalMilestoneEvent] = Field(default_factory=list)
    behavioral_improvements: List[BehavioralPatternAnalysis] = Field(default_factory=list)
    emotional_development: EmotionalProgressProfile
    cognitive_progress: CognitiveProgressMetrics
    sensory_progress: SensoryProgressProfile
    social_communication_progress: SocialCommunicationProgress
    goals_status: List[ProgressGoal] = Field(default_factory=list)
    overall_progress_score: float = Field(ge=0.0, le=1.0)
    areas_of_strength: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    clinical_recommendations: List[ASDRecommendation] = Field(default_factory=list)
    family_support_recommendations: List[str] = Field(default_factory=list)


class ProgressTrackingConfig(BaseModel):
    """Configuration for progress tracking system"""
    child_id: int
    tracking_frequency: str  # "real_time", "session", "daily", "weekly"
    focus_areas: List[BehavioralPattern] = Field(default_factory=list)
    milestone_targets: List[ClinicalMilestone] = Field(default_factory=list)
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)
    reporting_interval_days: int = 30
    clinical_team_notification: bool = True
    parent_notification: bool = True


class RealTimeProgressMetrics(BaseModel):
    """Real-time progress metrics during gameplay"""
    session_id: str
    child_id: int
    timestamp: datetime
    current_emotional_state: EmotionalState
    engagement_level: float = Field(ge=0.0, le=1.0)
    frustration_indicators: List[str] = Field(default_factory=list)
    success_moments: List[str] = Field(default_factory=list)
    skill_demonstrations: Dict[str, bool] = Field(default_factory=dict)
    behavioral_observations: List[BehavioralDataPoint] = Field(default_factory=list)
    intervention_triggers: List[str] = Field(default_factory=list)
    adaptation_recommendations: List[str] = Field(default_factory=list)


class ProgressDashboardData(BaseModel):
    """Data structure for progress dashboard visualization"""
    child_id: int
    generated_at: datetime
    current_session_metrics: Optional[RealTimeProgressMetrics] = None
    recent_milestones: List[ClinicalMilestoneEvent] = Field(default_factory=list)
    progress_trends: Dict[str, ProgressTrend] = Field(default_factory=dict)
    skill_development_chart: Dict[str, List[float]] = Field(default_factory=dict)
    behavioral_pattern_summary: Dict[BehavioralPattern, BehavioralPatternAnalysis] = Field(default_factory=dict)
    goal_progress_summary: List[ProgressGoal] = Field(default_factory=list)
    recommendations_priority: List[ASDRecommendation] = Field(default_factory=list)
    alert_notifications: List[str] = Field(default_factory=list)
