"""
Advanced Progress Tracking Service for ASD Children - Enhanced with AI-Powered Analysis
Provides comprehensive behavioral pattern recognition, emotional state progression analysis,
and clinical milestone tracking with real-time monitoring capabilities.
"""

import asyncio
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..models.asd_models import (ASDSupportLevel, BehavioralDataPoint,
                                 BehavioralPattern, BehavioralPatternAnalysis,
                                 ChildProfile, ClinicalMilestone,
                                 ClinicalMilestoneEvent,
                                 CognitiveProgressMetrics,
                                 EmotionalProgressProfile, EmotionalState,
                                 EmotionalStateTransition,
                                 LongTermProgressReport, ProgressDashboardData,
                                 ProgressGoal, ProgressTrackingConfig,
                                 ProgressTrend, RealTimeProgressMetrics,
                                 SensoryProgressProfile, SessionMetrics,
                                 SkillAssessment, SocialCommunicationProgress)
from .behavioral_pattern_analyzer import BehavioralPatternAnalyzer
from .clinical_milestone_tracker import ClinicalMilestoneTracker
from .emotional_progress_analyzer import EmotionalProgressAnalyzer


class ProgressTrackingService:
    """Advanced progress tracking service for ASD children with AI-powered analysis"""
    
    def __init__(self):
        # In-memory storage for demo (use database in production)
        self.behavioral_data: Dict[int, List[BehavioralDataPoint]] = defaultdict(list)
        self.emotional_transitions: Dict[int, List[EmotionalStateTransition]] = defaultdict(list)
        self.skill_assessments: Dict[int, List[SkillAssessment]] = defaultdict(list)
        self.milestones: Dict[int, List[ClinicalMilestoneEvent]] = defaultdict(list)
        self.progress_goals: Dict[int, List[ProgressGoal]] = defaultdict(list)
        self.tracking_configs: Dict[int, ProgressTrackingConfig] = {}
        self.real_time_metrics: Dict[str, RealTimeProgressMetrics] = {}
        
        # Initialize advanced analyzers
        self.behavioral_analyzer = BehavioralPatternAnalyzer()
        self.emotional_analyzer = EmotionalProgressAnalyzer()
        self.milestone_tracker = ClinicalMilestoneTracker()
        
        # Behavioral pattern detection parameters
        self.pattern_detection_window = 10  # Number of recent observations to analyze
        self.milestone_confidence_threshold = 0.7
        self.trend_analysis_days = 14
        
        # Initialize milestone tracking templates
        self._initialize_milestone_templates()
        
    def _initialize_milestone_templates(self):
        """Initialize templates for milestone detection"""
        self.milestone_criteria = {
            ClinicalMilestone.FIRST_INTENTIONAL_COMMUNICATION: {
                "behavioral_indicators": [
                    BehavioralPattern.COMMUNICATION,
                    BehavioralPattern.SOCIAL_INTERACTION
                ],
                "required_skills": ["verbal_initiation", "non_verbal_communication"],
                "min_occurrences": 3,
                "confidence_threshold": 0.8
            },
            ClinicalMilestone.IMPROVED_EYE_CONTACT: {
                "behavioral_indicators": [BehavioralPattern.SOCIAL_INTERACTION],
                "required_skills": ["eye_contact_duration", "social_referencing"],
                "min_occurrences": 5,
                "confidence_threshold": 0.7
            },
            ClinicalMilestone.SELF_REGULATION_SKILL: {
                "behavioral_indicators": [
                    BehavioralPattern.EMOTIONAL_REGULATION,
                    BehavioralPattern.SENSORY_PROCESSING
                ],
                "required_skills": ["coping_strategy_use", "emotional_recovery"],
                "min_occurrences": 3,
                "confidence_threshold": 0.8
            },
            ClinicalMilestone.FLEXIBILITY_IMPROVEMENT: {
                "behavioral_indicators": [
                    BehavioralPattern.ADAPTIVE_BEHAVIOR,
                    BehavioralPattern.TRANSITION_BEHAVIOR
                ],
                "required_skills": ["transition_acceptance", "routine_flexibility"],
                "min_occurrences": 4,
                "confidence_threshold": 0.75
            }
        }
    
    async def initialize_child_tracking(self, child_profile: ChildProfile, 
                                      config: Optional[ProgressTrackingConfig] = None) -> ProgressTrackingConfig:
        """Initialize progress tracking for a child"""
        if not config:
            config = ProgressTrackingConfig(
                child_id=child_profile.child_id,
                tracking_frequency="session",
                focus_areas=self._determine_focus_areas(child_profile),
                milestone_targets=self._determine_milestone_targets(child_profile),
                alert_thresholds=self._calculate_alert_thresholds(child_profile),
                reporting_interval_days=30,
                clinical_team_notification=True,
                parent_notification=True
            )
        
        self.tracking_configs[child_profile.child_id] = config
        
        # Initialize baseline assessments
        await self._create_baseline_assessments(child_profile)
        
        return config
    
    def _determine_focus_areas(self, child_profile: ChildProfile) -> List[BehavioralPattern]:
        """Determine focus areas based on child's ASD profile"""
        focus_areas = []
        
        # Base focus areas for all children
        focus_areas.extend([
            BehavioralPattern.EMOTIONAL_REGULATION,
            BehavioralPattern.SOCIAL_INTERACTION,
            BehavioralPattern.COMMUNICATION
        ])
        
        # Add specific focus areas based on support level
        if child_profile.asd_support_level == ASDSupportLevel.LEVEL_3:
            focus_areas.extend([
                BehavioralPattern.SENSORY_PROCESSING,
                BehavioralPattern.ADAPTIVE_BEHAVIOR
            ])
        elif child_profile.asd_support_level == ASDSupportLevel.LEVEL_2:
            focus_areas.extend([
                BehavioralPattern.ATTENTION_REGULATION,
                BehavioralPattern.TRANSITION_BEHAVIOR
            ])
        else:  # Level 1
            focus_areas.extend([
                BehavioralPattern.REPETITIVE_BEHAVIOR
            ])
        
        # Add sensory processing if hypersensitive or mixed profile
        if hasattr(child_profile, 'sensory_profile') and child_profile.sensory_profile in ["hypersensitive", "mixed"]:
            if BehavioralPattern.SENSORY_PROCESSING not in focus_areas:
                focus_areas.append(BehavioralPattern.SENSORY_PROCESSING)
        
        return focus_areas
    
    def _determine_milestone_targets(self, child_profile: ChildProfile) -> List[ClinicalMilestone]:
        """Determine appropriate milestone targets for child"""
        milestones = []
        
        # Base milestones for communication and social interaction
        milestones.extend([
            ClinicalMilestone.IMPROVED_EYE_CONTACT,
            ClinicalMilestone.SOCIAL_REFERENCING,
            ClinicalMilestone.SELF_REGULATION_SKILL
        ])
        
        # Age-appropriate milestones
        if child_profile.age >= 6:
            milestones.extend([
                ClinicalMilestone.TURN_TAKING_SUCCESS,
                ClinicalMilestone.PROBLEM_SOLVING_IMPROVEMENT
            ])
        
        if child_profile.age >= 8:
            milestones.extend([
                ClinicalMilestone.PEER_INTERACTION_ATTEMPT,
                ClinicalMilestone.GENERALIZATION_SKILL
            ])
        
        # Support level specific milestones
        if child_profile.asd_support_level <= ASDSupportLevel.LEVEL_2:
            milestones.extend([
                ClinicalMilestone.VERBAL_INITIATION,
                ClinicalMilestone.FLEXIBILITY_IMPROVEMENT
            ])
        
        return milestones
    
    def _calculate_alert_thresholds(self, child_profile: ChildProfile) -> Dict[str, float]:
        """Calculate alert thresholds based on child's profile"""
        base_thresholds = {
            "emotional_regulation_decline": 0.3,
            "sensory_overload_frequency": 0.6,
            "social_withdrawal": 0.4,
            "regression_indicator": 0.25,
            "goal_progress_stagnation": 0.2
        }
        
        # Adjust based on support level
        if child_profile.asd_support_level == ASDSupportLevel.LEVEL_3:
            # More sensitive thresholds for higher support needs
            base_thresholds = {k: v * 0.8 for k, v in base_thresholds.items()}
        elif child_profile.asd_support_level == ASDSupportLevel.LEVEL_1:
            # Less sensitive thresholds for lower support needs
            base_thresholds = {k: v * 1.2 for k, v in base_thresholds.items()}
        
        return base_thresholds
    
    async def _create_baseline_assessments(self, child_profile: ChildProfile):
        """Create baseline skill assessments for tracking progress"""
        baseline_skills = [
            ("attention_span", "cognitive", 0.3),
            ("emotional_regulation", "behavioral", 0.4),
            ("social_interaction", "social", 0.3),
            ("communication_clarity", "communication", 0.3),
            ("sensory_tolerance", "sensory", 0.4),
            ("problem_solving", "cognitive", 0.3),
            ("adaptive_behavior", "behavioral", 0.4)
        ]
        
        for skill_name, category, baseline_score in baseline_skills:
            assessment = SkillAssessment(
                skill_name=skill_name,
                skill_category=category,
                baseline_score=baseline_score,
                current_score=baseline_score,
                target_score=min(1.0, baseline_score + 0.3),
                assessment_date=datetime.now(),
                assessment_method="initial_observation",
                notes=f"Baseline assessment for {child_profile.name}"
            )
            self.skill_assessments[child_profile.child_id].append(assessment)
    
    async def record_behavioral_observation(self, child_id: int, session_id: str,
                                          behavior_type: BehavioralPattern,
                                          intensity: float, duration_seconds: int,
                                          context: Dict[str, Any] = None,
                                          trigger: str = None,
                                          intervention_used: str = None) -> BehavioralDataPoint:
        """Record a behavioral observation"""
        data_point = BehavioralDataPoint(
            timestamp=datetime.now(),
            behavior_type=behavior_type,
            intensity=intensity,
            duration_seconds=duration_seconds,
            context=context or {},
            trigger=trigger,
            intervention_used=intervention_used
        )
        self.behavioral_data[child_id].append(data_point)
        
        # Update real-time metrics if session is active
        if session_id in self.real_time_metrics:
            self.real_time_metrics[session_id].behavioral_observations.append(data_point)
        
        # Check for milestone achievements
        await self._check_milestone_achievement(child_id, data_point)
        
        # Analyze patterns using the advanced behavioral analyzer
        try:
            behavioral_analysis = await self.behavioral_analyzer.analyze_pattern(child_id, behavior_type, [data_point])
            if behavioral_analysis:
                await self._process_behavioral_analysis(child_id, behavioral_analysis)
        except Exception:
            pass  # Continue if advanced analyzer fails
        
        # Original pattern analysis for backward compatibility
        await self._analyze_behavioral_patterns(child_id)
        
        return data_point
    
    async def record_emotional_transition(self, child_id: int, session_id: str,
                                        from_state: EmotionalState, to_state: EmotionalState,
                                        trigger_event: str = None,
                                        transition_duration: float = 0.0,
                                        support_needed: bool = False,
                                        regulation_strategy_used: str = None) -> EmotionalStateTransition:
        """Record an emotional state transition"""
        transition = EmotionalStateTransition(
            timestamp=datetime.now(),
            from_state=from_state,
            to_state=to_state,
            trigger_event=trigger_event,
            transition_duration=transition_duration,
            support_needed=support_needed,
            regulation_strategy_used=regulation_strategy_used
        )
        
        self.emotional_transitions[child_id].append(transition)
        
        # Update real-time metrics
        if session_id in self.real_time_metrics:
            self.real_time_metrics[session_id].current_emotional_state = to_state
        
        # Analyze emotional regulation patterns using the advanced analyzer
        try:
            emotional_analysis = await self.emotional_analyzer.analyze_emotional_progression(
                child_id, self.emotional_transitions[child_id]
            )
            if emotional_analysis:
                await self._process_emotional_analysis(child_id, emotional_analysis)
        except Exception:
            pass  # Continue if advanced analyzer fails
        
        # Original emotional pattern analysis for backward compatibility
        await self._analyze_emotional_patterns(child_id)
        
        return transition
    
    async def update_skill_assessment(self, child_id: int, skill_name: str,
                                    new_score: float, assessment_method: str,
                                    notes: str = "") -> SkillAssessment:
        """Update a skill assessment with new score"""
        # Find existing assessment or create new one
        existing_assessments = [
            a for a in self.skill_assessments[child_id] 
            if a.skill_name == skill_name
        ]
        
        if existing_assessments:
            latest_assessment = max(existing_assessments, key=lambda x: x.assessment_date)
            # Create new assessment based on latest
            assessment = SkillAssessment(
                skill_name=skill_name,
                skill_category=latest_assessment.skill_category,
                baseline_score=latest_assessment.baseline_score,
                current_score=new_score,
                target_score=latest_assessment.target_score,
                assessment_date=datetime.now(),
                assessment_method=assessment_method,
                notes=notes
            )
        else:
            # Create new baseline assessment
            assessment = SkillAssessment(
                skill_name=skill_name,
                skill_category="general",
                baseline_score=new_score,
                current_score=new_score,
                target_score=min(1.0, new_score + 0.2),
                assessment_date=datetime.now(),
                assessment_method=assessment_method,
                notes=notes
            )
        
        self.skill_assessments[child_id].append(assessment)
        
        # Check if this represents a milestone achievement using the clinical milestone tracker
        try:
            milestone_result = await self.milestone_tracker.check_milestone_achievement(
                child_id, skill_name, new_score, self.skill_assessments[child_id], self.behavioral_data[child_id]
            )
            
            if milestone_result['achieved']:
                await self._record_advanced_milestone_achievement(
                    child_id, milestone_result['milestone'], milestone_result['confidence'], 
                    milestone_result['evidence']
                )
        except Exception:
            pass  # Continue if advanced tracker fails
        
        # Original milestone check for backward compatibility
        await self._check_skill_milestone(child_id, skill_name, new_score)
        
        return assessment
    
    async def record_behavioral_data(self, child_id: int, session_id: str, 
                                   behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record behavioral data with comprehensive analysis"""
        try:
            behavior_type = BehavioralPattern(behavior_data.get('behavior_type', 'attention_regulation'))
            intensity = float(behavior_data.get('intensity', 0.5))
            duration_seconds = int(behavior_data.get('duration_seconds', 30))
            context = behavior_data.get('context', {})
            trigger = behavior_data.get('trigger')
            intervention_used = behavior_data.get('intervention_used')
            
            # Record the observation
            data_point = await self.record_behavioral_observation(
                child_id=child_id,
                session_id=session_id,
                behavior_type=behavior_type,
                intensity=intensity,
                duration_seconds=duration_seconds,
                context=context,
                trigger=trigger,
                intervention_used=intervention_used
            )
            
            return {
                "success": True,
                "data_point_id": str(data_point.timestamp),
                "behavior_type": behavior_type.value,
                "intensity": intensity,
                "patterns_detected": await self._get_recent_patterns(child_id, behavior_type),
                "recommendations": await self._get_behavior_recommendations(child_id, behavior_type, intensity)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "behavior_type": behavior_data.get('behavior_type', 'unknown')
            }

    async def generate_dashboard_data(self, child_id: int) -> Dict[str, Any]:
        """Generate comprehensive dashboard data for progress tracking"""
        try:
            # Get recent data (last 7 days)
            recent_cutoff = datetime.now() - timedelta(days=7)
            
            # Behavioral data summary
            recent_behavioral = [
                dp for dp in self.behavioral_data.get(child_id, [])
                if dp.timestamp >= recent_cutoff
            ]
            
            # Emotional transitions summary
            recent_emotional = [
                t for t in self.emotional_transitions.get(child_id, [])
                if t.timestamp >= recent_cutoff
            ]
            
            # Current skill levels
            current_skills = {}
            for assessment in self.skill_assessments.get(child_id, []):
                skill_name = assessment.skill_name
                if skill_name not in current_skills or assessment.assessment_date > current_skills[skill_name]['date']:
                    current_skills[skill_name] = {
                        'current_score': assessment.current_score,
                        'target_score': assessment.target_score,
                        'baseline_score': assessment.baseline_score,
                        'date': assessment.assessment_date,
                        'progress': assessment.current_score - assessment.baseline_score
                    }
            
            # Recent milestones
            recent_milestones = [
                m for m in self.milestones.get(child_id, [])
                if m.achieved_at >= recent_cutoff
            ]
            
            # Calculate daily behavior frequency
            daily_behavior_counts = {}
            for dp in recent_behavioral:
                day_key = dp.timestamp.strftime('%Y-%m-%d')
                if day_key not in daily_behavior_counts:
                    daily_behavior_counts[day_key] = {}
                behavior_key = dp.behavior_type.value
                daily_behavior_counts[day_key][behavior_key] = daily_behavior_counts[day_key].get(behavior_key, 0) + 1
            
            # Calculate emotional state distribution
            emotional_state_counts = {}
            for transition in recent_emotional:
                state = transition.to_state.value
                emotional_state_counts[state] = emotional_state_counts.get(state, 0) + 1
            
            # Generate alerts
            alerts = await self._generate_dashboard_alerts(child_id, recent_behavioral, recent_emotional)
            
            dashboard_data = {
                "child_id": child_id,
                "last_updated": datetime.now().isoformat(),
                "period": "7_days",
                "behavioral_summary": {
                    "total_observations": len(recent_behavioral),
                    "daily_counts": daily_behavior_counts,
                    "top_behaviors": self._get_top_behaviors(recent_behavioral),
                    "average_intensity": round(mean([dp.intensity for dp in recent_behavioral]) if recent_behavioral else 0, 2)
                },
                "emotional_summary": {
                    "total_transitions": len(recent_emotional),
                    "state_distribution": emotional_state_counts,
                    "regulation_success_rate": self._calculate_regulation_success_rate(recent_emotional),
                    "average_transition_time": self._calculate_average_transition_time(recent_emotional)
                },
                "skill_progress": current_skills,
                "recent_milestones": [
                    {
                        "milestone": m.milestone.value,
                        "achieved_at": m.achieved_at.isoformat(),
                        "confidence": round(m.confidence_level, 2),
                        "description": m.description
                    } for m in recent_milestones
                ],
                "alerts": alerts,
                "progress_trends": await self._calculate_progress_trends(child_id),
                "recommendations": await self._generate_dashboard_recommendations(child_id, recent_behavioral, recent_emotional)
            }
            
            return dashboard_data
            
        except Exception as e:
            return {
                "child_id": child_id,
                "error": f"Failed to generate dashboard data: {str(e)}",
                "last_updated": datetime.now().isoformat()
            }

    async def get_real_time_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get real-time metrics for an active session"""
        try:
            if session_id not in self.real_time_metrics:
                # Initialize if not exists
                self.real_time_metrics[session_id] = RealTimeProgressMetrics(
                    session_id=session_id,
                    start_time=datetime.now(),
                    current_emotional_state=EmotionalState.CALM,
                    behavioral_observations=[],
                    skill_demonstrations=[],
                    engagement_level=0.5,
                    attention_score=0.5,
                    regulation_events=0,
                    milestone_progress={}
                )
            
            metrics = self.real_time_metrics[session_id]
            session_duration = (datetime.now() - metrics.start_time).total_seconds() / 60  # minutes
            
            return {
                "session_id": session_id,
                "session_duration_minutes": round(session_duration, 2),
                "current_emotional_state": metrics.current_emotional_state.value,
                "engagement_level": round(metrics.engagement_level, 2),
                "attention_score": round(metrics.attention_score, 2),
                "total_behavioral_observations": len(metrics.behavioral_observations),
                "regulation_events": metrics.regulation_events,
                "recent_behaviors": [
                    {
                        "behavior": obs.behavior_type.value,
                        "intensity": obs.intensity,
                        "timestamp": obs.timestamp.isoformat()
                    } for obs in metrics.behavioral_observations[-5:]  # Last 5 observations
                ],
                "milestone_progress": metrics.milestone_progress,
                "recommendations": await self._get_real_time_recommendations(session_id)
            }
            
        except Exception as e:
            return {
                "session_id": session_id,
                "error": f"Failed to get real-time metrics: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def generate_progress_summary(self, child_id: int, period_days: int = 30) -> Dict[str, Any]:
        """Generate a comprehensive progress summary for a child"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get data for the period
            recent_behavioral_data = [
                dp for dp in self.behavioral_data.get(child_id, [])
                if start_date <= dp.timestamp <= end_date
            ]
            
            recent_emotional_data = [
                t for t in self.emotional_transitions.get(child_id, [])
                if start_date <= t.timestamp <= end_date
            ]
            
            # Calculate behavioral pattern scores
            behavioral_scores = {}
            for pattern in BehavioralPattern:
                pattern_data = [dp for dp in recent_behavioral_data if dp.behavior_type == pattern]
                if pattern_data:
                    behavioral_scores[pattern.value] = {
                        "average_intensity": round(mean([dp.intensity for dp in pattern_data]), 2),
                        "frequency": len(pattern_data),
                        "trend": self._calculate_trend([dp.intensity for dp in pattern_data]).value
                    }
                else:
                    behavioral_scores[pattern.value] = {"average_intensity": 0, "frequency": 0, "trend": "no_data"}
            
            # Calculate emotional state distribution
            emotional_distribution = {}
            for transition in recent_emotional_data:
                state = transition.to_state.value
                emotional_distribution[state] = emotional_distribution.get(state, 0) + 1
            
            # Get current skill progression
            current_skills = {}
            for assessment in self.skill_assessments.get(child_id, []):
                skill_name = assessment.skill_name
                if skill_name not in current_skills or assessment.assessment_date > current_skills[skill_name].get('date', datetime.min):
                    current_skills[skill_name] = {
                        'current_score': assessment.current_score,
                        'baseline_score': assessment.baseline_score,
                        'target_score': assessment.target_score,
                        'progress_percentage': round(((assessment.current_score - assessment.baseline_score) / 
                                                   max(0.01, assessment.target_score - assessment.baseline_score)) * 100, 2),
                        'date': assessment.assessment_date
                    }
            
            skill_progression = {k: {**v, 'date': v['date'].isoformat()} for k, v in current_skills.items()}
            
            # Get recent milestones
            recent_milestones = [
                milestone for milestone in self.milestones.get(child_id, [])
                if milestone.achieved_at >= start_date
            ]
            
            # Generate summary
            summary = {
                "child_id": child_id,
                "summary_date": datetime.now().isoformat(),
                "period_days": period_days,
                "behavioral_scores": behavioral_scores,
                "emotional_state_distribution": emotional_distribution,
                "skill_progression": skill_progression,
                "recent_milestones": [
                    {
                        "milestone": milestone.milestone.value,
                        "achieved_date": milestone.achieved_at.isoformat(),
                        "confidence_score": round(milestone.confidence_level, 2)
                    } for milestone in recent_milestones
                ],
                "data_points": {
                    "behavioral_observations": len(recent_behavioral_data),
                    "emotional_transitions": len(recent_emotional_data),
                    "skill_assessments": len(current_skills),
                    "milestones_achieved": len(recent_milestones)
                },
                "overall_progress_score": round(mean([
                    score["average_intensity"] for score in behavioral_scores.values() if score["average_intensity"] > 0
                ]) if any(score["average_intensity"] > 0 for score in behavioral_scores.values()) else 0.0, 2)
            }
            
            return summary
            
        except Exception as e:
            # Return basic summary on error
            return {
                "child_id": child_id,
                "summary_date": datetime.now().isoformat(),
                "period_days": period_days,
                "error": f"Failed to generate complete summary: {str(e)}",
                "behavioral_scores": {},
                "emotional_state_distribution": {},
                "skill_progression": {},
                "recent_milestones": [],
                "data_points": {
                    "behavioral_observations": 0,
                    "emotional_transitions": 0,
                    "skill_assessments": 0,
                    "milestones_achieved": 0
                },
                "overall_progress_score": 0.0
            }

    # Helper methods
    async def _check_milestone_achievement(self, child_id: int, data_point: BehavioralDataPoint):
        """Check if behavioral observation indicates milestone achievement"""
        if not data_point.behavior_type:
            return
        
        # Check each potential milestone
        for milestone, criteria in self.milestone_criteria.items():
            if data_point.behavior_type in criteria["behavioral_indicators"]:
                # Count recent relevant observations
                recent_observations = [
                    dp for dp in self.behavioral_data[child_id][-20:]
                    if dp.behavior_type in criteria["behavioral_indicators"]
                    and dp.intensity >= 0.6  # Significant intensity
                    and dp.timestamp >= datetime.now() - timedelta(days=7)
                ]
                
                if len(recent_observations) >= criteria["min_occurrences"]:
                    confidence = min(mean([dp.intensity for dp in recent_observations]), 1.0)
                    
                    if confidence >= criteria["confidence_threshold"]:
                        await self._record_milestone_achievement(
                            child_id, milestone, confidence, recent_observations
                        )
    
    async def _record_milestone_achievement(self, child_id: int, milestone: ClinicalMilestone,
                                          confidence: float, supporting_observations: List[BehavioralDataPoint]):
        """Record achievement of a clinical milestone"""
        # Check if milestone was already achieved recently
        recent_milestones = [
            m for m in self.milestones[child_id]
            if m.milestone == milestone
            and m.achieved_at >= datetime.now() - timedelta(days=30)
        ]
        
        if recent_milestones:
            return  # Already recorded recently
        
        milestone_event = ClinicalMilestoneEvent(
            milestone=milestone,
            achieved_at=datetime.now(),
            session_id=supporting_observations[-1].context.get("session_id", "unknown") if supporting_observations else "unknown",
            description=f"Achieved {milestone.value} with {confidence:.2f} confidence",
            confidence_level=confidence,
            supporting_evidence=[
                f"{obs.behavior_type.value} at {obs.intensity:.2f} intensity"
                for obs in supporting_observations[-3:]
            ],
            clinical_significance="high" if confidence > 0.8 else "medium",
            next_target_milestone=self._get_next_milestone(milestone)
        )
        
        self.milestones[child_id].append(milestone_event)
        
        # Update progress goals if related
        await self._update_related_goals(child_id, milestone)
    
    def _get_next_milestone(self, achieved_milestone: ClinicalMilestone) -> Optional[ClinicalMilestone]:
        """Get the next logical milestone after achieving one"""
        milestone_progression = {
            ClinicalMilestone.IMPROVED_EYE_CONTACT: ClinicalMilestone.SOCIAL_REFERENCING,
            ClinicalMilestone.SOCIAL_REFERENCING: ClinicalMilestone.VERBAL_INITIATION,
            ClinicalMilestone.VERBAL_INITIATION: ClinicalMilestone.TURN_TAKING_SUCCESS,
            ClinicalMilestone.SELF_REGULATION_SKILL: ClinicalMilestone.COPING_STRATEGY_USE,
            ClinicalMilestone.COPING_STRATEGY_USE: ClinicalMilestone.FLEXIBILITY_IMPROVEMENT,
        }
        
        return milestone_progression.get(achieved_milestone)
    
    async def _update_related_goals(self, child_id: int, milestone: ClinicalMilestone):
        """Update progress goals related to achieved milestone"""
        milestone_goal_mapping = {
            ClinicalMilestone.IMPROVED_EYE_CONTACT: "social_interaction",
            ClinicalMilestone.VERBAL_INITIATION: "communication",
            ClinicalMilestone.SELF_REGULATION_SKILL: "emotional_regulation",
            ClinicalMilestone.FLEXIBILITY_IMPROVEMENT: "behavioral_flexibility"
        }
        
        goal_category = milestone_goal_mapping.get(milestone)
        if not goal_category:
            return
        
        related_goals = [
            goal for goal in self.progress_goals[child_id]
            if goal.goal_category == goal_category and goal.status == "active"
        ]
        
        for goal in related_goals:
            # Update goal progress
            goal.current_measurement = min(1.0, goal.current_measurement + 0.2)
            goal.progress_markers.append(f"Milestone achieved: {milestone.value}")
            
            # Check if goal is now achieved
            if goal.current_measurement >= goal.target_measurement:
                goal.status = "achieved"
    
    async def _analyze_behavioral_patterns(self, child_id: int) -> List[BehavioralPatternAnalysis]:
        """Analyze behavioral patterns for trends and insights"""
        if child_id not in self.behavioral_data:
            return []
        
        all_data = self.behavioral_data[child_id]
        recent_data = [
            dp for dp in all_data
            if dp.timestamp >= datetime.now() - timedelta(days=self.trend_analysis_days)
        ]
        
        if not recent_data:
            return []
        
        analyses = []
        
        # Analyze each behavior type
        for behavior_type in BehavioralPattern:
            behavior_data = [dp for dp in recent_data if dp.behavior_type == behavior_type]
            
            if len(behavior_data) < 3:  # Need minimum data points
                continue
            
            analysis = await self._analyze_behavior_type(behavior_type, behavior_data)
            if analysis:
                analyses.append(analysis)
        
        return analyses
    
    async def _analyze_behavior_type(self, behavior_type: BehavioralPattern,
                                   behavior_data: List[BehavioralDataPoint]) -> Optional[BehavioralPatternAnalysis]:
        """Analyze specific behavior type for patterns"""
        if not behavior_data:
            return None
        
        # Calculate basic metrics
        intensities = [dp.intensity for dp in behavior_data]
        average_intensity = mean(intensities)
        frequency_per_session = len(behavior_data) / max(1, self.trend_analysis_days / 7)
        
        # Determine trend using correlation
        trend = self._calculate_trend(intensities)
        
        # Identify triggers and interventions
        common_triggers = self._analyze_triggers(behavior_data)
        effective_interventions = self._analyze_interventions(behavior_data)
        
        # Generate recommendations
        recommendations = self._generate_behavior_recommendations(
            behavior_type, trend, average_intensity, common_triggers
        )
        
        return BehavioralPatternAnalysis(
            pattern_type=behavior_type,
            analysis_period_days=self.trend_analysis_days,
            frequency_per_session=frequency_per_session,
            average_intensity=average_intensity,
            trend=trend,
            triggers_identified=common_triggers,
            effective_interventions=effective_interventions,
            recommendations=recommendations,
            confidence_score=min(1.0, len(behavior_data) / 10.0)
        )
    
    def _calculate_trend(self, intensities: List[float]) -> ProgressTrend:
        """Calculate trend from intensity data"""
        if len(intensities) < 5:
            return ProgressTrend.STABLE
        
        x_values = list(range(len(intensities)))
        try:
            correlation = np.corrcoef(x_values, intensities)[0, 1] if len(set(intensities)) > 1 else 0
        except:
            correlation = 0
        
        if correlation > 0.6:
            return ProgressTrend.MODERATE_IMPROVEMENT
        elif correlation > 0.3:
            return ProgressTrend.STABLE
        elif correlation < -0.6:
            return ProgressTrend.CONCERNING_DECLINE
        elif correlation < -0.3:
            return ProgressTrend.MINOR_DECLINE
        else:
            return ProgressTrend.STABLE
    
    def _analyze_triggers(self, behavior_data: List[BehavioralDataPoint]) -> List[str]:
        """Analyze common triggers from behavioral data"""
        triggers = [dp.trigger for dp in behavior_data if dp.trigger]
        trigger_counts = {}
        for trigger in triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        return [
            trigger for trigger, count in trigger_counts.items()
            if count >= 2
        ]
    
    def _analyze_interventions(self, behavior_data: List[BehavioralDataPoint]) -> List[str]:
        """Analyze effective interventions from behavioral data"""
        interventions = [dp.intervention_used for dp in behavior_data if dp.intervention_used]
        return list(set(interventions))
    
    def _generate_behavior_recommendations(self, behavior_type: BehavioralPattern,
                                         trend: ProgressTrend, average_intensity: float,
                                         triggers: List[str]) -> List[str]:
        """Generate recommendations based on behavioral analysis"""
        recommendations = []
        
        if trend in [ProgressTrend.MINOR_DECLINE, ProgressTrend.CONCERNING_DECLINE]:
            recommendations.append(f"Review and adjust intervention strategies for {behavior_type.value}")
            recommendations.append("Consider increasing support level temporarily")
        
        if average_intensity > 0.7:
            recommendations.append(f"Implement intensive support for {behavior_type.value}")
            if triggers:
                recommendations.append(f"Focus on addressing triggers: {', '.join(triggers[:3])}")
        
        # Behavior-specific recommendations
        if behavior_type == BehavioralPattern.SENSORY_PROCESSING:
            recommendations.append("Consider sensory break scheduling")
            recommendations.append("Review environmental sensory factors")
        elif behavior_type == BehavioralPattern.EMOTIONAL_REGULATION:
            recommendations.append("Implement emotional regulation strategies")
            recommendations.append("Consider mindfulness or breathing exercises")
        elif behavior_type == BehavioralPattern.SOCIAL_INTERACTION:
            recommendations.append("Provide structured social interaction opportunities")
            recommendations.append("Use visual supports for social cues")
        
        return recommendations
    
    async def _analyze_emotional_patterns(self, child_id: int):
        """Analyze emotional state transition patterns"""
        if child_id not in self.emotional_transitions:
            return
        
        recent_transitions = [
            t for t in self.emotional_transitions[child_id]
            if t.timestamp >= datetime.now() - timedelta(days=7)
        ]
        
        if not recent_transitions:
            return
        
        # Analyze regulation ability
        regulation_transitions = [
            t for t in recent_transitions
            if t.to_state in [EmotionalState.CALM, EmotionalState.REGULATED]
        ]
        
        if recent_transitions:
            regulation_success_rate = len(regulation_transitions) / len(recent_transitions)
            # Update emotional progress profile
            await self._update_emotional_profile(child_id, recent_transitions, regulation_success_rate)
    
    async def _update_emotional_profile(self, child_id: int, recent_transitions: List[EmotionalStateTransition], 
                                      regulation_success_rate: float):
        """Update emotional progress profile based on recent data"""
        # Calculate predominant states
        state_counts = {}
        for transition in recent_transitions:
            state = transition.to_state.value
            state_counts[state] = state_counts.get(state, 0) + 1
        
        # Store emotional profile update logic here
        # This would typically update a database or profile store

    async def _get_recent_patterns(self, child_id: int, behavior_type: BehavioralPattern) -> List[str]:
        """Get recently detected patterns for a behavior type"""
        recent_data = [
            dp for dp in self.behavioral_data.get(child_id, [])
            if dp.behavior_type == behavior_type and dp.timestamp >= datetime.now() - timedelta(hours=24)
        ]
        
        patterns = []
        if len(recent_data) >= 3:
            avg_intensity = mean([dp.intensity for dp in recent_data])
            if avg_intensity > 0.7:
                patterns.append("high_intensity_pattern")
            
            # Check for clustering in time
            time_diffs = [
                (recent_data[i].timestamp - recent_data[i-1].timestamp).total_seconds() / 60
                for i in range(1, len(recent_data))
            ]
            if time_diffs and mean(time_diffs) < 30:  # Within 30 minutes
                patterns.append("frequent_occurrence_pattern")
        
        return patterns

    async def _get_behavior_recommendations(self, child_id: int, behavior_type: BehavioralPattern, intensity: float) -> List[str]:
        """Generate behavior-specific recommendations"""
        recommendations = []
        
        if intensity > 0.8:
            recommendations.append("Consider implementing immediate intervention strategies")
            
        if behavior_type == BehavioralPattern.SENSORY_PROCESSING:
            recommendations.extend([
                "Provide sensory break opportunity",
                "Check environmental sensory factors",
                "Consider sensory tools or aids"
            ])
        elif behavior_type == BehavioralPattern.EMOTIONAL_REGULATION:
            recommendations.extend([
                "Use calming strategies",
                "Practice breathing exercises",
                "Provide emotional support"
            ])
        elif behavior_type == BehavioralPattern.SOCIAL_INTERACTION:
            recommendations.extend([
                "Encourage peer interaction",
                "Model appropriate social behaviors",
                "Provide social scripts if needed"
            ])
        
        return recommendations

    async def _generate_dashboard_alerts(self, child_id: int, recent_behavioral: List, recent_emotional: List) -> List[Dict[str, Any]]:
        """Generate alerts for the dashboard"""
        alerts = []
        
        # Check for high-intensity behaviors
        high_intensity_behaviors = [dp for dp in recent_behavioral if dp.intensity > 0.8]
        if len(high_intensity_behaviors) > 3:
            alerts.append({
                "type": "high_intensity_pattern",
                "severity": "medium",
                "message": f"Multiple high-intensity behaviors detected ({len(high_intensity_behaviors)} instances)",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for emotional regulation challenges
        challenging_transitions = [
            t for t in recent_emotional 
            if t.to_state in [EmotionalState.FRUSTRATED, EmotionalState.OVERWHELMED, EmotionalState.DYSREGULATED]
        ]
        if recent_emotional and len(challenging_transitions) > len(recent_emotional) * 0.6:  # More than 60% challenging
            alerts.append({
                "type": "emotional_regulation_concern",
                "severity": "high",
                "message": "Frequent challenging emotional states detected",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts

    def _get_top_behaviors(self, behavioral_data: List) -> List[Dict[str, Any]]:
        """Get top observed behaviors with counts"""
        behavior_counts = {}
        for dp in behavioral_data:
            behavior = dp.behavior_type.value
            behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
        
        sorted_behaviors = sorted(behavior_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"behavior": behavior, "count": count}
            for behavior, count in sorted_behaviors[:5]
        ]

    def _calculate_regulation_success_rate(self, emotional_data: List) -> float:
        """Calculate emotional regulation success rate"""
        if not emotional_data:
            return 0.0
        
        positive_transitions = [
            t for t in emotional_data
            if t.to_state in [EmotionalState.CALM, EmotionalState.REGULATED, EmotionalState.HAPPY]
        ]
        
        return round(len(positive_transitions) / len(emotional_data), 2)

    def _calculate_average_transition_time(self, emotional_data: List) -> float:
        """Calculate average emotional transition time"""
        if not emotional_data:
            return 0.0
        
        transition_times = [t.transition_duration for t in emotional_data if t.transition_duration > 0]
        return round(mean(transition_times) if transition_times else 0.0, 2)

    async def _calculate_progress_trends(self, child_id: int) -> Dict[str, str]:
        """Calculate progress trends for different areas"""
        trends = {}
        
        # Analyze behavioral trends
        recent_behavioral = [
            dp for dp in self.behavioral_data.get(child_id, [])
            if dp.timestamp >= datetime.now() - timedelta(days=14)
        ]
        
        if recent_behavioral:
            first_half = recent_behavioral[:len(recent_behavioral)//2]
            second_half = recent_behavioral[len(recent_behavioral)//2:]
            
            if first_half and second_half:
                first_avg = mean([dp.intensity for dp in first_half])
                second_avg = mean([dp.intensity for dp in second_half])
                
                if second_avg < first_avg - 0.1:
                    trends['behavioral'] = 'improving'
                elif second_avg > first_avg + 0.1:
                    trends['behavioral'] = 'concerning'
                else:
                    trends['behavioral'] = 'stable'
            else:
                trends['behavioral'] = 'insufficient_data'
        else:
            trends['behavioral'] = 'no_data'
        
        # Add other trend calculations for emotional, social, etc.
        trends['emotional'] = 'stable'  # Placeholder
        trends['social'] = 'improving'  # Placeholder
        
        return trends

    async def _generate_dashboard_recommendations(self, child_id: int, recent_behavioral: List, recent_emotional: List) -> List[str]:
        """Generate recommendations for the dashboard"""
        recommendations = []
        
        if recent_behavioral:
            avg_intensity = mean([dp.intensity for dp in recent_behavioral])
            if avg_intensity > 0.6:
                recommendations.append("Consider implementing more frequent breaks")
                recommendations.append("Review environmental factors for sensory overload")
        
        if recent_emotional:
            challenging_states = [
                t for t in recent_emotional
                if t.to_state in [EmotionalState.FRUSTRATED, EmotionalState.OVERWHELMED]
            ]
            if len(challenging_states) > 2:
                recommendations.append("Focus on emotional regulation strategies")
                recommendations.append("Consider additional support during transitions")
        
        # Always include some general recommendations
        recommendations.extend([
            "Continue consistent routine and structure",
            "Celebrate small victories and progress",
            "Maintain regular communication with care team"
        ])
        
        return recommendations

    async def _get_real_time_recommendations(self, session_id: str) -> List[str]:
        """Get real-time recommendations based on current session metrics"""
        recommendations = []
        
        if session_id in self.real_time_metrics:
            metrics = self.real_time_metrics[session_id]
            
            if metrics.engagement_level < 0.4:
                recommendations.append("Consider changing activity to increase engagement")
                
            if metrics.attention_score < 0.3:
                recommendations.append("Provide attention-focusing strategies")
                
            if metrics.current_emotional_state in [EmotionalState.FRUSTRATED, EmotionalState.OVERWHELMED]:
                recommendations.append("Implement calming strategies immediately")
                
            if metrics.regulation_events > 3:
                recommendations.append("Consider taking a break or reducing stimulation")
        
        return recommendations

    async def _check_skill_milestone(self, child_id: int, skill_name: str, new_score: float):
        """Check if skill assessment represents a milestone achievement"""
        # Get baseline for this skill
        skill_assessments = [
            a for a in self.skill_assessments[child_id]
            if a.skill_name == skill_name
        ]
        
        if not skill_assessments:
            return
        
        baseline_assessment = min(skill_assessments, key=lambda x: x.assessment_date)
        improvement = new_score - baseline_assessment.baseline_score
        
        # Check for significant improvement (milestone)
        if improvement >= 0.3:  # 30% improvement
            milestone = self._determine_skill_milestone(skill_name, improvement)
            if milestone:
                await self._record_milestone_achievement(
                    child_id, milestone, new_score, []
                )

    def _determine_skill_milestone(self, skill_name: str, improvement: float) -> Optional[ClinicalMilestone]:
        """Determine which milestone a skill improvement represents"""
        skill_milestone_mapping = {
            'social_interaction': ClinicalMilestone.IMPROVED_EYE_CONTACT,
            'communication_clarity': ClinicalMilestone.VERBAL_INITIATION,
            'emotional_regulation': ClinicalMilestone.SELF_REGULATION_SKILL,
            'adaptive_behavior': ClinicalMilestone.FLEXIBILITY_IMPROVEMENT,
            'problem_solving': ClinicalMilestone.PROBLEM_SOLVING_IMPROVEMENT
        }
        
        return skill_milestone_mapping.get(skill_name)

    async def _record_advanced_milestone_achievement(self, child_id: int, milestone: ClinicalMilestone,
                                                   confidence: float, evidence: List[str]):
        """Record milestone achievement with advanced tracking"""
        milestone_event = ClinicalMilestoneEvent(
            milestone=milestone,
            achieved_at=datetime.now(),
            session_id="advanced_tracking",
            description=f"Advanced milestone achievement: {milestone.value}",
            confidence_level=confidence,
            supporting_evidence=evidence,
            clinical_significance="high" if confidence > 0.8 else "medium",
            next_target_milestone=self._get_next_milestone(milestone)
        )
        
        self.milestones[child_id].append(milestone_event)

    async def _process_behavioral_analysis(self, child_id: int, analysis: Dict[str, Any]):
        """Process results from behavioral pattern analyzer"""
        # Store analysis results and trigger interventions if needed
        # This would integrate with the advanced behavioral analyzer results
        pass

    async def _process_emotional_analysis(self, child_id: int, analysis: Dict[str, Any]):
        """Process results from emotional progress analyzer"""
        # Store analysis results and update emotional profiles
        # This would integrate with the advanced emotional analyzer results
        pass
