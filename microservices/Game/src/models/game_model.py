from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Table, Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Enums per il sistema
class EmotionalState(str, Enum):
    very_calm = "very_calm"
    calm = "calm"
    neutral = "neutral"
    anxious = "anxious"
    very_anxious = "very_anxious"
    overstimulated = "overstimulated"

class DifficultyLevel(str, Enum):
    very_easy = "very_easy"
    easy = "easy"
    medium = "medium"
    hard = "hard"
    very_hard = "very_hard"

class ModuleType(str, Enum):
    introduction = "introduction"
    tool_exploration = "tool_exploration"
    breathing_exercise = "breathing_exercise"
    social_story = "social_story"
    video_modeling = "video_modeling"
    full_simulation = "full_simulation"

class ContentType(str, Enum):
    video = "video"
    audio = "audio"
    image = "image"
    text = "text"
    interactive_3d = "interactive_3d"

class ASDSupportLevel(int, Enum):
    level_1 = 1  # Requiring support
    level_2 = 2  # Requiring substantial support
    level_3 = 3  # Requiring very substantial support

# Tabelle di associazione
session_modules = Table(
    'session_modules',
    Base.metadata,
    Column('session_id', Integer, ForeignKey('game_sessions.id')),
    Column('module_id', Integer, ForeignKey('learning_modules.id'))
)

module_content = Table(
    'module_content',
    Base.metadata,
    Column('module_id', Integer, ForeignKey('learning_modules.id')),
    Column('content_id', Integer, ForeignKey('content_items.id'))
)

# =============== SQLALCHEMY MODELS ===============

class SensoryProfile(Base):
    __tablename__ = "sensory_profiles"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, nullable=False, index=True)  # Reference to Users service
    
    # Sensibilità visive
    light_sensitivity = Column(Integer, default=3)  # 1-5 scale
    color_preference = Column(String, default="calm_blues")  # calm_blues, soft_greens, neutrals
    motion_sensitivity = Column(Integer, default=3)  # 1-5, tolerance for animations
    
    # Sensibilità auditive
    sound_sensitivity = Column(Integer, default=3)  # 1-5 scale
    preferred_volume = Column(Float, default=0.7)  # 0.0-1.0
    background_music_tolerance = Column(Boolean, default=True)
    
    # Preferenze tattili (per haptic feedback)
    haptic_feedback_enabled = Column(Boolean, default=True)
    vibration_intensity = Column(Float, default=0.5)  # 0.0-1.0
    
    # Preferenze sociali
    eye_contact_comfortable = Column(Boolean, default=False)
    prefer_robot_interaction = Column(Boolean, default=True)
    social_interaction_level = Column(Integer, default=2)  # 1-5
    
    # Support level ASD
    asd_support_level = Column(Integer, default=1)  # 1-3 based on DSM-5
    
    # Metadati
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    game_sessions = relationship("GameSession", back_populates="sensory_profile")

class LearningModule(Base):
    __tablename__ = "learning_modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    module_type = Column(String, nullable=False)  # ModuleType enum
    
    # Configurazione modulo
    estimated_duration_minutes = Column(Integer, default=5)
    difficulty_level = Column(String, default="easy")  # DifficultyLevel enum
    min_age = Column(Integer, default=3)
    max_age = Column(Integer, default=12)
    
    # ASD-specific configuration
    suitable_for_asd_levels = Column(JSON)  # [1, 2, 3] - which ASD support levels
    sensory_considerations = Column(JSON)  # {"low_audio": true, "calm_colors": true}
    
    # Obiettivi educativi
    learning_objectives = Column(JSON)  # ["familiarize_with_dental_chair", "reduce_anxiety"]
    success_criteria = Column(JSON)  # {"completion_time": "< 10 min", "anxiety_level": "< 3"}
    
    # Contenuti del modulo
    introduction_text = Column(Text)
    instructions = Column(Text)
    
    # Personalizzazione
    customizable_elements = Column(JSON)  # elementi che possono essere personalizzati
    
    # Metadati
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    content_items = relationship("ContentItem", secondary=module_content, back_populates="modules")
    session_modules = relationship("GameSession", secondary=session_modules, back_populates="completed_modules")
    progress_metrics = relationship("ProgressMetric", back_populates="module")

class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(String, nullable=False)  # ContentType enum
    
    # File information
    file_url = Column(String)  # URL or path to the content file
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String)
    
    # Content metadata
    duration_seconds = Column(Integer)  # for video/audio content
    dimensions = Column(JSON)  # {"width": 1920, "height": 1080} for images/videos
    
    # ASD-specific properties
    sensory_safe = Column(Boolean, default=True)
    calm_content = Column(Boolean, default=True)
    contains_flashing = Column(Boolean, default=False)
    audio_level = Column(String, default="soft")  # soft, medium, loud
    
    # Customization support
    dentist_customizable = Column(Boolean, default=False)
    parent_customizable = Column(Boolean, default=False)
    
    # Categorization
    tags = Column(JSON)  # ["dental_tools", "calming", "educational"]
    age_appropriate = Column(JSON)  # [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    
    # Metadati
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    modules = relationship("LearningModule", secondary=module_content, back_populates="content_items")

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, nullable=False, index=True)  # Reference to Users service
    sensory_profile_id = Column(Integer, ForeignKey("sensory_profiles.id"), nullable=True)
    
    # Session info
    session_type = Column(String, default="standard")  # standard, assessment, custom
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    total_duration_minutes = Column(Float, default=0)
    
    # Progress tracking
    current_module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=True)
    modules_completed = Column(Integer, default=0)
    overall_completion_percentage = Column(Float, default=0.0)
    
    # Emotional state tracking
    initial_emotional_state = Column(String, default="neutral")  # EmotionalState enum
    final_emotional_state = Column(String, default="neutral")
    emotional_state_changes = Column(JSON)  # [{"timestamp": "...", "state": "calm", "trigger": "..."}]
    
    # Interaction quality
    engagement_level = Column(Float, default=0.5)  # 0.0-1.0
    response_time_average = Column(Float)  # average response time in seconds
    successful_interactions = Column(Integer, default=0)
    total_interactions = Column(Integer, default=0)
    
    # Adaptive learning data
    difficulty_adjustments = Column(JSON)  # automatic difficulty changes during session
    intervention_triggers = Column(JSON)  # when and why interventions were suggested
    
    # Device and environment
    device_info = Column(JSON)  # device type, OS version, etc.
    environment_settings = Column(JSON)  # lighting, volume, haptic settings used
    
    # Session outcome
    session_rating = Column(Integer, nullable=True)  # 1-5, child's self-rating if capable
    parent_feedback = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Metadati
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relazioni
    sensory_profile = relationship("SensoryProfile", back_populates="game_sessions")
    current_module = relationship("LearningModule", foreign_keys=[current_module_id])
    completed_modules = relationship("LearningModule", secondary=session_modules, back_populates="session_modules")
    progress_metrics = relationship("ProgressMetric", back_populates="session")

class ProgressMetric(Base):
    __tablename__ = "progress_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=True)
    child_id = Column(Integer, nullable=False, index=True)
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Behavioral metrics
    attention_span_seconds = Column(Float)
    anxiety_level = Column(Integer)  # 1-5 scale
    comfort_level = Column(Integer)  # 1-5 scale
    cooperation_level = Column(Integer)  # 1-5 scale
    
    # Interaction metrics
    task_completion_time = Column(Float)  # seconds
    number_of_attempts = Column(Integer, default=1)
    help_requests = Column(Integer, default=0)
    spontaneous_interactions = Column(Integer, default=0)
    
    # Learning metrics
    skill_demonstration = Column(JSON)  # {"opened_mouth": true, "stayed_calm": true}
    knowledge_retention = Column(JSON)  # quiz/assessment results
    generalization_evidence = Column(JSON)  # applying skills to new contexts
    
    # Sensory response metrics
    sensory_overload_incidents = Column(Integer, default=0)
    sensory_seeking_behaviors = Column(Integer, default=0)
    preferred_sensory_inputs = Column(JSON)  # what worked well
    
    # Social interaction metrics (with Pepper robot)
    robot_interaction_quality = Column(Float, default=0.5)  # 0.0-1.0
    social_initiation_attempts = Column(Integer, default=0)
    turn_taking_success = Column(Float, default=0.0)  # percentage
    
    # Communication metrics
    verbal_responses = Column(Integer, default=0)
    non_verbal_responses = Column(Integer, default=0)
    communication_clarity = Column(Float, default=0.5)  # 0.0-1.0
    
    # Goal achievement
    session_goals_met = Column(JSON)  # {"stay_calm": true, "explore_tools": false}
    breakthrough_moments = Column(JSON)  # significant positive moments
    regression_indicators = Column(JSON)  # any concerning behaviors
    
    # Contextual factors
    environmental_factors = Column(JSON)  # noise level, lighting, etc.
    physical_state = Column(String)  # tired, energetic, sick, etc.
    emotional_context = Column(String)  # had_good_day, stressed, excited, etc.
    
    # Metadati
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relazioni
    session = relationship("GameSession", back_populates="progress_metrics")
    module = relationship("LearningModule", back_populates="progress_metrics")

# =============== PYDANTIC SCHEMAS ===============

# SensoryProfile Schemas
class SensoryProfileBase(BaseModel):
    child_id: int
    light_sensitivity: int = Field(default=3, ge=1, le=5)
    color_preference: str = "calm_blues"
    motion_sensitivity: int = Field(default=3, ge=1, le=5)
    sound_sensitivity: int = Field(default=3, ge=1, le=5)
    preferred_volume: float = Field(default=0.7, ge=0.0, le=1.0)
    background_music_tolerance: bool = True
    haptic_feedback_enabled: bool = True
    vibration_intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    eye_contact_comfortable: bool = False
    prefer_robot_interaction: bool = True
    social_interaction_level: int = Field(default=2, ge=1, le=5)
    asd_support_level: int = Field(default=1, ge=1, le=3)

class SensoryProfileCreate(SensoryProfileBase):
    pass

class SensoryProfileUpdate(BaseModel):
    light_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    color_preference: Optional[str] = None
    motion_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    sound_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    preferred_volume: Optional[float] = Field(None, ge=0.0, le=1.0)
    background_music_tolerance: Optional[bool] = None
    haptic_feedback_enabled: Optional[bool] = None
    vibration_intensity: Optional[float] = Field(None, ge=0.0, le=1.0)
    eye_contact_comfortable: Optional[bool] = None
    prefer_robot_interaction: Optional[bool] = None
    social_interaction_level: Optional[int] = Field(None, ge=1, le=5)
    asd_support_level: Optional[int] = Field(None, ge=1, le=3)

class SensoryProfileInDB(SensoryProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# LearningModule Schemas
class LearningModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    module_type: ModuleType
    estimated_duration_minutes: int = 5
    difficulty_level: DifficultyLevel = DifficultyLevel.easy
    min_age: int = 3
    max_age: int = 12
    suitable_for_asd_levels: List[int] = [1, 2, 3]
    sensory_considerations: Dict[str, Any] = {}
    learning_objectives: List[str] = []
    success_criteria: Dict[str, Any] = {}
    introduction_text: Optional[str] = None
    instructions: Optional[str] = None
    customizable_elements: Dict[str, Any] = {}

class LearningModuleCreate(LearningModuleBase):
    pass

class LearningModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    module_type: Optional[ModuleType] = None
    estimated_duration_minutes: Optional[int] = None
    difficulty_level: Optional[DifficultyLevel] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    suitable_for_asd_levels: Optional[List[int]] = None
    sensory_considerations: Optional[Dict[str, Any]] = None
    learning_objectives: Optional[List[str]] = None
    success_criteria: Optional[Dict[str, Any]] = None
    introduction_text: Optional[str] = None
    instructions: Optional[str] = None
    customizable_elements: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class LearningModuleInDB(LearningModuleBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ContentItem Schemas
class ContentItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    dimensions: Optional[Dict[str, int]] = None
    sensory_safe: bool = True
    calm_content: bool = True
    contains_flashing: bool = False
    audio_level: str = "soft"
    dentist_customizable: bool = False
    parent_customizable: bool = False
    tags: List[str] = []
    age_appropriate: List[int] = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

class ContentItemCreate(ContentItemBase):
    pass

class ContentItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    duration_seconds: Optional[int] = None
    dimensions: Optional[Dict[str, int]] = None
    sensory_safe: Optional[bool] = None
    calm_content: Optional[bool] = None
    contains_flashing: Optional[bool] = None
    audio_level: Optional[str] = None
    dentist_customizable: Optional[bool] = None
    parent_customizable: Optional[bool] = None
    tags: Optional[List[str]] = None
    age_appropriate: Optional[List[int]] = None
    is_active: Optional[bool] = None

class ContentItemInDB(ContentItemBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# GameSession Schemas
class GameSessionBase(BaseModel):
    child_id: int
    sensory_profile_id: Optional[int] = None
    session_type: str = "standard"
    current_module_id: Optional[int] = None
    initial_emotional_state: EmotionalState = EmotionalState.neutral
    device_info: Optional[Dict[str, Any]] = None
    environment_settings: Optional[Dict[str, Any]] = None

class GameSessionCreate(GameSessionBase):
    pass

class GameSessionUpdate(BaseModel):
    current_module_id: Optional[int] = None
    modules_completed: Optional[int] = None
    overall_completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    final_emotional_state: Optional[EmotionalState] = None
    emotional_state_changes: Optional[List[Dict[str, Any]]] = None
    engagement_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    response_time_average: Optional[float] = None
    successful_interactions: Optional[int] = None
    total_interactions: Optional[int] = None
    difficulty_adjustments: Optional[List[Dict[str, Any]]] = None
    intervention_triggers: Optional[List[Dict[str, Any]]] = None
    session_rating: Optional[int] = Field(None, ge=1, le=5)
    parent_feedback: Optional[str] = None
    notes: Optional[str] = None
    ended_at: Optional[datetime] = None

class GameSessionInDB(GameSessionBase):
    id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    total_duration_minutes: float
    modules_completed: int
    overall_completion_percentage: float
    final_emotional_state: EmotionalState
    engagement_level: float
    successful_interactions: int
    total_interactions: int
    session_rating: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ProgressMetric Schemas
class ProgressMetricBase(BaseModel):
    session_id: int
    module_id: Optional[int] = None
    child_id: int
    attention_span_seconds: Optional[float] = None
    anxiety_level: Optional[int] = Field(None, ge=1, le=5)
    comfort_level: Optional[int] = Field(None, ge=1, le=5)
    cooperation_level: Optional[int] = Field(None, ge=1, le=5)
    task_completion_time: Optional[float] = None
    number_of_attempts: int = 1
    help_requests: int = 0
    spontaneous_interactions: int = 0
    skill_demonstration: Dict[str, Any] = {}
    knowledge_retention: Dict[str, Any] = {}
    sensory_overload_incidents: int = 0
    sensory_seeking_behaviors: int = 0
    preferred_sensory_inputs: Dict[str, Any] = {}
    robot_interaction_quality: float = Field(default=0.5, ge=0.0, le=1.0)
    social_initiation_attempts: int = 0
    turn_taking_success: float = Field(default=0.0, ge=0.0, le=1.0)
    verbal_responses: int = 0
    non_verbal_responses: int = 0
    communication_clarity: float = Field(default=0.5, ge=0.0, le=1.0)
    session_goals_met: Dict[str, bool] = {}
    breakthrough_moments: List[Dict[str, Any]] = []
    regression_indicators: List[Dict[str, Any]] = []
    environmental_factors: Dict[str, Any] = {}
    physical_state: Optional[str] = None
    emotional_context: Optional[str] = None

class ProgressMetricCreate(ProgressMetricBase):
    pass

class ProgressMetricInDB(ProgressMetricBase):
    id: int
    recorded_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Response models for API
class SessionProgressSummary(BaseModel):
    child_id: int
    total_sessions: int
    total_play_time_hours: float
    average_engagement: float
    anxiety_trend: List[float]  # last 10 sessions
    skills_progress: Dict[str, float]  # skill -> progress percentage
    recent_breakthroughs: List[str]
    recommended_next_modules: List[int]

class AdaptiveLearningRecommendation(BaseModel):
    child_id: int
    recommended_difficulty: DifficultyLevel
    suggested_module_ids: List[int]
    environmental_adjustments: Dict[str, Any]
    intervention_suggestions: List[str]
    rationale: str