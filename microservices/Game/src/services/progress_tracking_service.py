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
    
    def __init__(self):        # In-memory storage for demo (use database in production)
        self.behavioral_data: Dict[int, List[BehavioralDataPoint]] = defaultdict(list)
        self.emotional_transitions: Dict[int, List[EmotionalStateTransition]] = defaultdict(list)
        self.skill_assessments: Dict[int, List[SkillAssessment]] = defaultdict(list)
        self.milestones: Dict[int, List[ClinicalMilestoneEvent]] = defaultdict(list)
        self.progress_goals: Dict[int, List[ProgressGoal]] = defaultdict(list)
        self.tracking_configs: Dict[int, ProgressTrackingConfig] = {}
        self.real_time_metrics: Dict[str, RealTimeProgressMetrics] = {}
        
        # Additional tracking data structures
        self.emotional_profiles: Dict[int, Dict[str, Any]] = {}
        self.analysis_insights: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.alerts: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        
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
        if child_profile.sensory_profile in ["hypersensitive", "mixed"]:
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
                assessment_method="initial_observation",                notes=f"Baseline assessment for {child_profile.name}"
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
        behavioral_analysis = await self.behavioral_analyzer.analyze_pattern(child_id, behavior_type, [data_point])
        if behavioral_analysis:
            # Store analysis results and trigger interventions if needed
            await self._process_behavioral_analysis(child_id, behavioral_analysis)
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
        emotional_analysis = await self.emotional_analyzer.analyze_emotional_progression(
            child_id, self.emotional_transitions[child_id]
        )
        if emotional_analysis:
            await self._process_emotional_analysis(child_id, emotional_analysis)
        
        # Original emotional pattern analysis for backward compatibility
        await self._analyze_emotional_patterns(child_id)
        
        return transition
    
    async def record_emotional_transitions(self, child_id: int, session_id: str, 
                                         transitions: List[EmotionalStateTransition]) -> Dict[str, Any]:
        """Record multiple emotional state transitions"""
        try:
            recorded_transitions = []
            
            for transition in transitions:
                # Record each transition using the existing method
                recorded_transition = await self.record_emotional_transition(
                    child_id=child_id,
                    session_id=session_id,
                    from_state=transition.from_state,
                    to_state=transition.to_state,
                    trigger_event=transition.trigger_event,
                    transition_duration=transition.transition_duration,
                    support_needed=transition.support_needed,
                    regulation_strategy_used=transition.regulation_strategy_used
                )
                
                recorded_transitions.append({
                    "from_state": transition.from_state.value,
                    "to_state": transition.to_state.value,
                    "timestamp": recorded_transition.timestamp.isoformat(),
                    "transition_duration": transition.transition_duration,
                    "support_needed": transition.support_needed,
                    "trigger_event": transition.trigger_event,
                    "regulation_strategy_used": transition.regulation_strategy_used
                })
            
            # Analyze overall emotional patterns for this batch of transitions
            regulation_events = sum(1 for t in transitions if t.support_needed)
            challenging_transitions = sum(1 for t in transitions 
                                        if t.to_state in [EmotionalState.FRUSTRATED, EmotionalState.OVERWHELMED, EmotionalState.DYSREGULATED])
            
            # Generate insights and recommendations
            insights = {
                "total_transitions": len(transitions),
                "regulation_events": regulation_events,
                "challenging_transitions": challenging_transitions,
                "regulation_success_rate": 1.0 - (challenging_transitions / len(transitions)) if transitions else 0.0
            }
            
            recommendations = []
            if challenging_transitions > len(transitions) * 0.5:
                recommendations.extend([
                    "Consider implementing additional emotional regulation strategies",
                    "Monitor for patterns that trigger challenging emotional states",
                    "Provide additional support during transitions"
                ])
            elif regulation_events == 0:
                recommendations.append("Continue maintaining current emotional support strategies")
            
            return {
                "success": True,
                "message": f"Recorded {len(transitions)} emotional transitions",
                "data": {
                    "child_id": child_id,
                    "session_id": session_id,
                    "transitions_count": len(transitions),
                    "recorded_transitions": recorded_transitions,
                    "insights": insights,
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to record emotional transitions: {str(e)}",
                "data": {
                    "child_id": child_id,
                    "session_id": session_id,
                    "transitions_count": 0,
                    "recorded_transitions": [],
                    "insights": {},
                    "recommendations": []
                }
            }
    
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
                assessment_date=datetime.now(),                assessment_method=assessment_method,
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
        milestone_result = await self.milestone_tracker.check_milestone_achievement(
            child_id, skill_name, new_score, self.skill_assessments[child_id], self.behavioral_data[child_id]
        )
        
        if milestone_result['achieved']:
            await self._record_advanced_milestone_achievement(
                child_id, milestone_result['milestone'], milestone_result['confidence'], 
                milestone_result['evidence']
            )
        
        # Original milestone check for backward compatibility
        await self._check_skill_milestone(child_id, skill_name, new_score)
        
        return assessment
    
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
            session_id=supporting_observations[-1].context.get("session_id", "unknown"),
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
        correlation = np.corrcoef(x_values, intensities)[0, 1] if len(set(intensities)) > 1 else 0
        
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
        
        # Store emotional profile - in a real implementation this would update a database
        self.emotional_profiles[child_id] = {
            "regulation_success_rate": regulation_success_rate,
            "predominant_states": state_counts,
            "last_updated": datetime.now()
        }

    async def record_behavioral_data(self, child_id: int, session_id: str, 
                                   behavioral_data: List[BehavioralDataPoint]) -> Dict[str, Any]:
        """Record behavioral data with comprehensive analysis"""
        try:
            recorded_observations = []
            
            # Process each behavioral data point
            for behavior_data_point in behavioral_data:
                # Extract data from the BehavioralDataPoint object
                behavior_type = behavior_data_point.behavior_type
                intensity = behavior_data_point.intensity
                duration_seconds = behavior_data_point.duration_seconds
                context = behavior_data_point.context
                trigger = behavior_data_point.trigger
                intervention_used = behavior_data_point.intervention_used
                
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
                
                recorded_observations.append({
                    "data_point_id": str(data_point.timestamp),
                    "behavior_type": behavior_type.value,
                    "intensity": intensity,
                    "duration_seconds": duration_seconds
                })
            
            # Get patterns and recommendations based on the latest behavioral data
            if recorded_observations:
                latest_behavior_type = behavioral_data[-1].behavior_type
                latest_intensity = behavioral_data[-1].intensity
                
                # Generate patterns
                patterns = self._analyze_behavioral_patterns_for_response(child_id, latest_behavior_type)
                
                # Generate recommendations
                recommendations = self._generate_behavior_recommendations(
                    latest_behavior_type, ProgressTrend.STABLE, latest_intensity, []
                )
                
                return {
                    "success": True,
                    "recorded_observations": recorded_observations,
                    "patterns_detected": patterns,
                    "recommendations": recommendations,
                    "total_recorded": len(recorded_observations)
                }
            
            return {
                "success": True,
                "recorded_observations": [],
                "patterns_detected": [],
                "recommendations": [],
                "total_recorded": 0
            }
            
        except Exception as e:            return {
                "success": False,
                "error": str(e),
                "recorded_observations": [],
                "patterns_detected": [],
                "recommendations": [],
                "total_recorded": 0
            }

    async def generate_dashboard_data(self, child_id: int, start_date: Optional[datetime] = None, 
                                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate comprehensive dashboard data for progress tracking"""
        try:
            # Set default date range if not provided
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=7)
            
            # Behavioral data summary
            recent_behavioral = [
                dp for dp in self.behavioral_data.get(child_id, [])
                if start_date <= dp.timestamp <= end_date
            ]
              # Emotional transitions summary
            recent_emotional = [
                t for t in self.emotional_transitions.get(child_id, [])
                if start_date <= t.timestamp <= end_date
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
                if start_date <= m.achieved_at <= end_date
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

    async def get_child_metrics(self, child_id: int) -> Dict[str, Any]:
        """Get comprehensive real-time metrics for a child"""
        try:
            # Get recent behavioral data
            behavioral_data = self.behavioral_data.get(child_id, [])
            recent_behavioral = [bd for bd in behavioral_data 
                               if (datetime.now() - bd.timestamp).days <= 7]
            
            # Calculate behavioral scores
            behavioral_scores = {}
            if recent_behavioral:
                # Group by behavior type and calculate averages
                behavior_groups = {}
                for bd in recent_behavioral:
                    if bd.behavior_type not in behavior_groups:
                        behavior_groups[bd.behavior_type] = []
                    behavior_groups[bd.behavior_type].append(bd.intensity)
                
                behavioral_scores = {
                    behavior_type: mean(intensities) 
                    for behavior_type, intensities in behavior_groups.items()
                }
            
            # Get emotional state distribution
            emotional_transitions = self.emotional_transitions.get(child_id, [])
            recent_emotions = [et for et in emotional_transitions 
                             if (datetime.now() - et.timestamp).days <= 7]
            
            emotional_state_distribution = {}
            if recent_emotions:
                emotion_counts = {}
                for et in recent_emotions:
                    emotion = et.to_state.value
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
                total_emotions = sum(emotion_counts.values())
                emotional_state_distribution = {
                    emotion: count / total_emotions 
                    for emotion, count in emotion_counts.items()
                }
              # Get skill progression
            skill_assessments = self.skill_assessments.get(child_id, [])
            recent_skills = [sa for sa in skill_assessments 
                           if (datetime.now() - sa.assessment_date).days <= 30]
            
            skill_progression = {}
            if recent_skills:
                for skill in recent_skills:
                    if skill.skill_name not in skill_progression:
                        skill_progression[skill.skill_name] = []
                    skill_progression[skill.skill_name].append({
                        "level": skill.current_score,
                        "date": skill.assessment_date.isoformat()
                    })
            
            # Get recent achievements
            milestones = self.milestones.get(child_id, [])
            recent_achievements = [
                {
                    "milestone": m.milestone.value,
                    "achieved_at": m.achieved_at.isoformat(),
                    "confidence": m.confidence_level
                }
                for m in milestones
                if (datetime.now() - m.achieved_at).days <= 30
            ]
            
            # Identify areas for improvement
            areas_for_improvement = []
            if behavioral_scores:
                low_scores = [(behavior, score) for behavior, score in behavioral_scores.items() 
                            if score < 0.4]
                areas_for_improvement = [
                    f"Improve {behavior.replace('_', ' ')} (current score: {score:.2f})"
                    for behavior, score in low_scores
                ]
            
            return {
                "behavioral_scores": behavioral_scores,
                "emotional_state_distribution": emotional_state_distribution,
                "skill_progression": skill_progression,
                "recent_achievements": recent_achievements,
                "areas_for_improvement": areas_for_improvement
            }
            
        except Exception as e:
            print(f"Error getting child metrics: {e}")
            # Return default structure on error
            return {
                "behavioral_scores": {},
                "emotional_state_distribution": {},
                "skill_progression": {},
                "recent_achievements": [],
                "areas_for_improvement": []
            }

    async def analyze_behavioral_patterns(self, child_id: int, pattern_type: Optional[str] = None) -> Dict[str, Any]:
        """Analyze behavioral patterns for a child"""
        try:
            behavioral_data = self.behavioral_data.get(child_id, [])
            
            if not behavioral_data:
                return {
                    "overall_score": 0.0,
                    "trend": "no_data",
                    "recommendations": ["No behavioral data available for analysis"],
                    "pattern_details": {}
                }
            
            # Filter by pattern type if specified
            if pattern_type:
                filtered_data = [bd for bd in behavioral_data if bd.behavior_type == pattern_type]
                if not filtered_data:
                    return {
                        "overall_score": 0.0,
                        "trend": "no_data",
                        "recommendations": [f"No data available for {pattern_type}"],
                        "pattern_details": {}
                    }
                data_to_analyze = filtered_data
            else:
                data_to_analyze = behavioral_data
            
            # Calculate overall score (average intensity)
            recent_data = [bd for bd in data_to_analyze 
                          if (datetime.now() - bd.timestamp).days <= 14]
            
            if not recent_data:
                overall_score = 0.0
                trend = "no_recent_data"
            else:
                overall_score = mean([bd.intensity for bd in recent_data])
                
                # Calculate trend (compare last week vs previous week)
                last_week = [bd for bd in recent_data 
                           if (datetime.now() - bd.timestamp).days <= 7]
                prev_week = [bd for bd in recent_data 
                           if 7 < (datetime.now() - bd.timestamp).days <= 14]
                
                if last_week and prev_week:
                    last_week_avg = mean([bd.intensity for bd in last_week])
                    prev_week_avg = mean([bd.intensity for bd in prev_week])
                    
                    if last_week_avg > prev_week_avg + 0.1:
                        trend = "improving"
                    elif last_week_avg < prev_week_avg - 0.1:
                        trend = "declining"
                    else:
                        trend = "stable"
                else:
                    trend = "insufficient_data"
            
            # Generate recommendations
            recommendations = []
            if overall_score < 0.3:
                recommendations.append("Consider increasing support and intervention strategies")
                recommendations.append("Monitor more frequently for early intervention opportunities")
            elif overall_score < 0.6:
                recommendations.append("Continue current interventions with minor adjustments")
                recommendations.append("Focus on consistency in positive reinforcement")
            else:
                recommendations.append("Maintain current successful strategies")
                recommendations.append("Consider advancing to more challenging activities")
            
            if trend == "declining":
                recommendations.append("Review recent changes in environment or routine")
                recommendations.append("Consider additional support measures")
            
            # Pattern details
            pattern_details = {
                "data_points": len(data_to_analyze),
                "recent_data_points": len(recent_data),
                "average_intensity": overall_score,
                "pattern_consistency": self._calculate_pattern_consistency(recent_data)
            }
            
            return {
                "overall_score": overall_score,
                "trend": trend,
                "recommendations": recommendations,
                "pattern_details": pattern_details
            }
            
        except Exception as e:
            print(f"Error analyzing behavioral patterns: {e}")
            return {
                "overall_score": 0.0,
                "trend": "error",                "recommendations": ["Error occurred during analysis"],
                "pattern_details": {"error": str(e)}
            }

    async def generate_long_term_report(self, child_id: int, start_date: datetime, 
                                      end_date: datetime, include_recommendations: bool = True) -> Dict[str, Any]:
        """Generate comprehensive long-term progress report"""
        try:
            # Filter data by date range
            behavioral_data = [
                bd for bd in self.behavioral_data.get(child_id, [])
                if start_date <= bd.timestamp <= end_date
            ]
            
            emotional_transitions = [
                et for et in self.emotional_transitions.get(child_id, [])
                if start_date <= et.timestamp <= end_date
            ]
            
            skill_assessments = [
                sa for sa in self.skill_assessments.get(child_id, [])
                if start_date <= sa.assessment_date <= end_date
            ]
            
            milestones = [
                m for m in self.milestones.get(child_id, [])
                if start_date <= m.achieved_at <= end_date
            ]
            
            # Behavioral summary
            behavioral_summary = {}
            if behavioral_data:
                behavior_groups = {}
                for bd in behavioral_data:
                    if bd.behavior_type not in behavior_groups:
                        behavior_groups[bd.behavior_type] = []
                    behavior_groups[bd.behavior_type].append(bd.intensity)
                
                behavioral_summary = {
                    "total_observations": len(behavioral_data),
                    "behavior_types": list(behavior_groups.keys()),
                    "average_scores": {
                        behavior_type: mean(intensities)
                        for behavior_type, intensities in behavior_groups.items()
                    },
                    "improvement_areas": [
                        behavior_type for behavior_type, intensities in behavior_groups.items()
                        if mean(intensities) < 0.5
                    ]
                }
            
            # Emotional summary
            emotional_summary = {}
            if emotional_transitions:
                emotion_counts = {}
                for et in emotional_transitions:
                    emotion = et.to_state.value
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
                total_transitions = len(emotional_transitions)
                most_common_emotion = max(emotion_counts, key=emotion_counts.get)
                
                emotional_summary = {
                    "total_transitions": total_transitions,
                    "emotion_distribution": emotion_counts,
                    "most_common_emotion": most_common_emotion,
                    "emotional_stability": self._calculate_emotional_stability(emotional_transitions)
                }
              # Skill development
            skill_development = {}
            if skill_assessments:
                skill_progress = {}
                for sa in skill_assessments:
                    if sa.skill_name not in skill_progress:
                        skill_progress[sa.skill_name] = []
                    skill_progress[sa.skill_name].append(sa.current_score)
                
                skill_development = {
                    "skills_assessed": list(skill_progress.keys()),
                    "skill_improvements": {},
                    "areas_of_strength": [],
                    "areas_needing_focus": []
                }
                
                for skill_name, levels in skill_progress.items():
                    if len(levels) > 1:
                        improvement = levels[-1] - levels[0]
                        skill_development["skill_improvements"][skill_name] = improvement
                        
                        if improvement > 0.2:
                            skill_development["areas_of_strength"].append(skill_name)
                        elif improvement < 0.1:
                            skill_development["areas_needing_focus"].append(skill_name)
              # Milestone achievements
            milestone_achievements = [
                {
                    "milestone": m.milestone.value,
                    "achieved_date": m.achieved_at.isoformat(),
                    "confidence": m.confidence_level,
                    "notes": getattr(m, 'notes', '')
                }
                for m in milestones
            ]
            
            # Recommendations
            recommendations = []
            if include_recommendations:
                if behavioral_summary.get("improvement_areas"):
                    recommendations.append(
                        f"Focus on improving: {', '.join(behavioral_summary['improvement_areas'])}"
                    )
                
                if skill_development.get("areas_needing_focus"):
                    recommendations.append(
                        f"Provide additional support for: {', '.join(skill_development['areas_needing_focus'])}"
                    )
                
                if len(milestone_achievements) > 0:
                    recommendations.append("Continue current successful intervention strategies")
                else:
                    recommendations.append("Review and adjust intervention strategies")
                
                recommendations.append("Maintain consistent data collection for ongoing monitoring")
            
            return {
                "behavioral_summary": behavioral_summary,
                "emotional_summary": emotional_summary,
                "skill_development": skill_development,
                "milestone_achievements": milestone_achievements,
                "recommendations": recommendations
            }
            
        except Exception as e:
            print(f"Error generating long-term report: {e}")
            return {
                "behavioral_summary": {},
                "emotional_summary": {},
                "skill_development": {},
                "milestone_achievements": [],
                "recommendations": [f"Error generating report: {str(e)}"]
            }

    def _calculate_pattern_consistency(self, behavioral_data: List[BehavioralDataPoint]) -> float:
        """Calculate consistency score for behavioral patterns"""
        if len(behavioral_data) < 2:
            return 0.0
        
        intensities = [bd.intensity for bd in behavioral_data]
        if len(set(intensities)) == 1:
            return 1.0  # Perfect consistency
        
        # Calculate coefficient of variation (lower = more consistent)
        std_dev = stdev(intensities)
        mean_intensity = mean(intensities)
        
        if mean_intensity == 0:
            return 0.0
        
        cv = std_dev / mean_intensity
        # Convert to consistency score (0-1, where 1 is most consistent)
        consistency = max(0.0, 1.0 - cv)
        return consistency

    def _calculate_emotional_stability(self, emotional_transitions: List[EmotionalStateTransition]) -> float:
        """Calculate emotional stability score"""
        if len(emotional_transitions) < 2:
            return 0.5  # Neutral stability
        
        # Count transitions between different emotional states
        state_changes = 0
        for i in range(1, len(emotional_transitions)):
            if emotional_transitions[i].from_state != emotional_transitions[i-1].to_state:
                state_changes += 1
        
        # Stability decreases with more frequent state changes
        stability = max(0.0, 1.0 - (state_changes / len(emotional_transitions)))
        return stability

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
        if len(challenging_transitions) > len(recent_emotional) * 0.6:  # More than 60% challenging
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
    
    async def _process_behavioral_analysis(self, child_id: int, analysis: Dict[str, Any]):
        """Process results from behavioral pattern analyzer"""
        # Store analysis results and trigger interventions if needed
        if not analysis:
            return
        
        # Extract key insights from analysis
        patterns_detected = analysis.get('patterns_detected', [])
        intervention_recommendations = analysis.get('recommendations', [])
        risk_indicators = analysis.get('risk_indicators', [])
        
        # Store insights for dashboard and reporting
        if child_id not in self.analysis_insights:
            self.analysis_insights[child_id] = []
        
        insight = {
            "timestamp": datetime.now(),
            "type": "behavioral_analysis",
            "patterns": patterns_detected,
            "recommendations": intervention_recommendations,
            "risk_level": analysis.get('risk_level', 'low')
        }
        self.analysis_insights[child_id].append(insight)
          # Trigger alerts if high risk indicators
        if risk_indicators and analysis.get('risk_level', 'low') == 'high':
            await self._trigger_intervention_alert(child_id, risk_indicators)
    
    async def _process_emotional_analysis(self, child_id: int, analysis: Dict[str, Any]):
        """Process results from emotional progress analyzer"""
        # Store analysis results and update emotional profiles
        if not analysis:
            return
        
        # Extract emotional insights
        emotional_trends = analysis.get('emotional_trends', {})
        regulation_patterns = analysis.get('regulation_patterns', {})
        intervention_recommendations = analysis.get('recommendations', [])
        
        # Update emotional profile
        if child_id not in self.emotional_profiles:
            self.emotional_profiles[child_id] = {}
        
        self.emotional_profiles[child_id].update({
            "regulation_success_rate": regulation_patterns.get('success_rate', 0.5),
            "predominant_states": emotional_trends.get('state_distribution', {}),
            "transition_patterns": emotional_trends.get('transition_patterns', {}),
            "last_updated": datetime.now()
        })
        
        # Store insights
        if child_id not in self.analysis_insights:
            self.analysis_insights[child_id] = []
        
        insight = {
            "timestamp": datetime.now(),
            "type": "emotional_analysis",
            "trends": emotional_trends,
            "regulation_patterns": regulation_patterns,
            "recommendations": intervention_recommendations
        }
        self.analysis_insights[child_id].append(insight)
        
        # Trigger alerts for concerning patterns
        concern_level = analysis.get('concern_level', 'low')
        if concern_level in ['high', 'critical']:
            concerning_patterns = analysis.get('concerning_patterns', [])
            await self._trigger_intervention_alert(child_id, concerning_patterns)
        if not analysis:
            return
        
        # Extract emotional progression insights
        regulation_trends = analysis.get('regulation_trends', {})
        emotional_stability = analysis.get('stability_score', 0.5)
        intervention_success = analysis.get('intervention_effectiveness', {})
        
        # Update emotional profile with new insights
        if child_id not in self.emotional_profiles:
            self.emotional_profiles[child_id] = {}
        
        self.emotional_profiles[child_id].update({
            "regulation_trends": regulation_trends,
            "stability_score": emotional_stability,
            "intervention_effectiveness": intervention_success,
            "last_analysis": datetime.now()
        })
        
        # Store insights for reporting
        if child_id not in self.analysis_insights:
            self.analysis_insights[child_id] = []
        
        insight = {
            "timestamp": datetime.now(),
            "type": "emotional_analysis",
            "stability_score": emotional_stability,
            "regulation_success": regulation_trends.get('success_rate', 0.0),
            "recommendations": analysis.get('recommendations', [])
        }
        self.analysis_insights[child_id].append(insight)
    
    def _analyze_behavioral_patterns_for_response(self, child_id: int, behavior_type: BehavioralPattern) -> List[Dict[str, Any]]:
        """Analyze behavioral patterns for API response"""
        if child_id not in self.behavioral_data:
            return []
        
        recent_data = [
            dp for dp in self.behavioral_data[child_id]
            if dp.behavior_type == behavior_type
            and dp.timestamp >= datetime.now() - timedelta(days=7)
        ]
        
        if len(recent_data) < 2:
            return []
        
        # Calculate pattern metrics
        intensities = [dp.intensity for dp in recent_data]
        avg_intensity = sum(intensities) / len(intensities)
        frequency = len(recent_data)
        
        return [{
            "pattern_type": behavior_type.value,
            "frequency": frequency,
            "average_intensity": avg_intensity,
            "trend": "stable",
            "last_occurrence": recent_data[-1].timestamp.isoformat()
        }]
    
    async def _trigger_intervention_alert(self, child_id: int, risk_indicators: List[str]):
        """Trigger intervention alert for high-risk situations"""
        alert = {
            "child_id": child_id,
            "alert_type": "intervention_needed",
            "risk_indicators": risk_indicators,
            "timestamp": datetime.now(),
            "priority": "high"
        }
        
        # Store alert for dashboard
        if not hasattr(self, 'alerts'):
            self.alerts = {}
        if child_id not in self.alerts:
            self.alerts[child_id] = []
        
        self.alerts[child_id].append(alert)
    
    async def _generate_dashboard_alerts(self, child_id: int, behavioral_data: List, emotional_data: List) -> List[Dict[str, Any]]:
        """Generate alerts for dashboard based on recent data"""
        alerts = []
        
        # Check for concerning behavioral patterns
        if behavioral_data:
            high_intensity_behaviors = [dp for dp in behavioral_data if dp.intensity > 0.8]
            if len(high_intensity_behaviors) > 3:
                alerts.append({
                    "type": "behavioral_concern",
                    "message": "High intensity behaviors detected",
                    "priority": "medium",
                    "count": len(high_intensity_behaviors)
                })
        
        # Check for emotional regulation concerns
        if emotional_data:
            regulation_failures = [t for t in emotional_data if t.support_needed]
            if len(regulation_failures) > 2:
                alerts.append({
                    "type": "emotional_regulation",
                    "message": "Multiple regulation support instances",
                    "priority": "medium",
                    "count": len(regulation_failures)
                })
        
        return alerts
    
    async def _record_advanced_milestone_achievement(self, child_id: int, milestone: ClinicalMilestone, 
                                                   confidence: float, evidence: List[str]):
        """Record milestone achievement from advanced analysis"""
        milestone_event = ClinicalMilestoneEvent(
            milestone=milestone,
            achieved_at=datetime.now(),
            session_id="advanced_analysis",
            description=f"Advanced analysis detected {milestone.value}",
            confidence_level=confidence,
            supporting_evidence=evidence,            clinical_significance="high" if confidence > 0.8 else "medium",
            next_target_milestone=self._get_next_milestone(milestone)
        )
        
        if child_id not in self.milestones:
            self.milestones[child_id] = []
        self.milestones[child_id].append(milestone_event)
    
    async def _check_skill_milestone(self, child_id: int, skill_name: str, score: float):
        """Check if skill improvement represents a milestone"""
        # Simple milestone detection based on score thresholds
        if score >= 0.8:
            milestone = ClinicalMilestone.SKILL_MASTERY
            await self._record_milestone_achievement(
                child_id, milestone, score, []
            )

    async def record_skill_assessments(self, child_id: int, session_id: str, 
                                     skill_assessments: List[SkillAssessment]) -> Dict[str, Any]:
        """Record skill assessments with detailed tracking"""
        try:
            recorded_assessments = []
            
            for assessment in skill_assessments:
                # Record the skill assessment
                recorded_assessment = await self.update_skill_assessment(
                    child_id=child_id,
                    skill_name=assessment.skill_name,
                    new_score=assessment.current_score,
                    assessment_method=assessment.assessment_method,
                    notes=assessment.notes
                )
                
                recorded_assessments.append({
                    "skill_name": assessment.skill_name,
                    "skill_category": assessment.skill_category,
                    "current_score": assessment.current_score,
                    "baseline_score": assessment.baseline_score,
                    "target_score": assessment.target_score,
                    "assessment_date": recorded_assessment.assessment_date.isoformat(),
                    "progress": assessment.current_score - assessment.baseline_score
                })
            
            # Analyze skill progression
            skill_progression_analysis = await self._analyze_skill_progression(child_id, skill_assessments)
            
            # Generate recommendations based on assessments
            recommendations = self._generate_skill_recommendations(skill_assessments)
            
            return {
                "success": True,
                "message": f"Recorded {len(skill_assessments)} skill assessments",
                "data": {
                    "child_id": child_id,
                    "session_id": session_id,
                    "assessments_count": len(skill_assessments),
                    "recorded_assessments": recorded_assessments,
                    "skill_progression_analysis": skill_progression_analysis,
                    "recommendations": recommendations
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to record skill assessments: {str(e)}",
                "data": {
                    "child_id": child_id,
                    "session_id": session_id,
                    "assessments_count": 0,
                    "recorded_assessments": [],
                    "skill_progression_analysis": {},
                    "recommendations": []
                }
            }

    async def _analyze_skill_progression(self, child_id: int, new_assessments: List[SkillAssessment]) -> Dict[str, Any]:
        """Analyze skill progression patterns"""
        progression_analysis = {}
        
        for assessment in new_assessments:
            skill_name = assessment.skill_name
            
            # Get historical assessments for this skill
            historical_assessments = [
                sa for sa in self.skill_assessments.get(child_id, [])
                if sa.skill_name == skill_name
            ]
            
            # Calculate progression metrics
            if historical_assessments:
                scores = [sa.current_score for sa in historical_assessments[-5:]]  # Last 5 assessments
                progression_rate = (assessment.current_score - scores[0]) / len(scores) if len(scores) > 1 else 0
                consistency = 1.0 - (max(scores) - min(scores)) / max(scores) if max(scores) > 0 else 0
            else:
                progression_rate = 0
                consistency = 1.0
            
            progression_analysis[skill_name] = {
                "current_score": assessment.current_score,
                "baseline_score": assessment.baseline_score,
                "target_score": assessment.target_score,
                "progression_rate": progression_rate,
                "consistency": consistency,
                "target_progress": (assessment.current_score - assessment.baseline_score) / (assessment.target_score - assessment.baseline_score) if assessment.target_score > assessment.baseline_score else 1.0
            }
        
        return progression_analysis
    
    def _generate_skill_recommendations(self, assessments: List[SkillAssessment]) -> List[str]:
        """Generate recommendations based on skill assessments"""
        recommendations = []
        
        # Analyze skill levels and generate targeted recommendations
        low_skills = [a for a in assessments if a.current_score < 0.4]
        improving_skills = [a for a in assessments if a.current_score > a.baseline_score + 0.1]
        stagnant_skills = [a for a in assessments if abs(a.current_score - a.baseline_score) < 0.05]
        
        if low_skills:
            skill_names = [s.skill_name.replace('_', ' ') for s in low_skills[:3]]
            recommendations.append(f"Focus on developing: {', '.join(skill_names)}")
            recommendations.append("Consider additional support and practice opportunities")
        
        if improving_skills:
            skill_names = [s.skill_name.replace('_', ' ') for s in improving_skills[:2]]
            recommendations.append(f"Continue building on strengths in: {', '.join(skill_names)}")
        
        if stagnant_skills:
            recommendations.append("Review intervention strategies for skills showing little progress")
            recommendations.append("Consider alternative approaches or modified activities")
        
        # General recommendations
        recommendations.extend([
            "Celebrate progress and achievements",
            "Maintain consistent assessment schedule",
            "Document successful strategies for future use"
        ])
        
        return recommendations
    
    async def analyze_behavioral_pattern(self, child_id: int, pattern_type: BehavioralPattern, 
                                       start_date: datetime, end_date: datetime) -> BehavioralPatternAnalysis:
        """Analyze a specific behavioral pattern for a child within a date range"""
        try:
            # Get behavioral data for the child within the date range
            all_behavioral_data = self.behavioral_data.get(child_id, [])
            
            # Filter by date range and pattern type
            pattern_data = [
                bd for bd in all_behavioral_data
                if (start_date <= bd.timestamp <= end_date and 
                    bd.behavior_type == pattern_type.value)
            ]
            
            analysis_period_days = (end_date - start_date).days
            
            if not pattern_data:
                # Return minimal analysis for no data
                return BehavioralPatternAnalysis(
                    pattern_type=pattern_type,
                    analysis_period_days=analysis_period_days,
                    frequency_per_session=0.0,
                    average_intensity=0.0,
                    trend=ProgressTrend.STABLE,
                    triggers_identified=[],
                    effective_interventions=[],
                    recommendations=["No data available for this pattern in the specified period"],
                    confidence_score=0.0
                )
            
            # Calculate frequency per session
            session_ids = set(bd.session_id for bd in pattern_data if bd.session_id)
            frequency_per_session = len(pattern_data) / max(len(session_ids), 1)
            
            # Calculate average intensity
            average_intensity = sum(bd.intensity for bd in pattern_data) / len(pattern_data)
            
            # Determine trend by comparing first half vs second half of period
            mid_date = start_date + (end_date - start_date) / 2
            first_half = [bd for bd in pattern_data if bd.timestamp <= mid_date]
            second_half = [bd for bd in pattern_data if bd.timestamp > mid_date]
            
            if first_half and second_half:
                first_half_avg = sum(bd.intensity for bd in first_half) / len(first_half)
                second_half_avg = sum(bd.intensity for bd in second_half) / len(second_half)
                
                if second_half_avg > first_half_avg + 0.1:
                    trend = ProgressTrend.IMPROVING
                elif second_half_avg < first_half_avg - 0.1:
                    trend = ProgressTrend.DECLINING
                else:
                    trend = ProgressTrend.STABLE
            else:
                trend = ProgressTrend.STABLE
            
            # Identify common triggers
            triggers_identified = []
            trigger_counts = {}
            for bd in pattern_data:
                if bd.context and 'trigger' in bd.context:
                    trigger = bd.context['trigger']
                    trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
            
            # Get most common triggers (appearing in >20% of occurrences)
            min_occurrences = len(pattern_data) * 0.2
            triggers_identified = [
                trigger for trigger, count in trigger_counts.items() 
                if count >= min_occurrences
            ]
            
            # Identify effective interventions
            effective_interventions = []
            if pattern_data:
                # Look for patterns where interventions led to lower intensity
                intervention_outcomes = {}
                for bd in pattern_data:
                    if bd.context and 'intervention' in bd.context:
                        intervention = bd.context['intervention']
                        if intervention not in intervention_outcomes:
                            intervention_outcomes[intervention] = []
                        intervention_outcomes[intervention].append(bd.intensity)
                
                # Consider interventions effective if they result in below-average intensity
                for intervention, intensities in intervention_outcomes.items():
                    avg_intervention_intensity = sum(intensities) / len(intensities)
                    if avg_intervention_intensity < average_intensity - 0.1:
                        effective_interventions.append(intervention)
            
            # Generate recommendations based on analysis
            recommendations = []
            if average_intensity > 0.7:
                recommendations.append(f"High intensity {pattern_type.value} patterns detected - consider additional support")
                recommendations.append("Implement proactive intervention strategies")
            elif average_intensity < 0.3:
                recommendations.append(f"{pattern_type.value} patterns are well-managed")
                recommendations.append("Continue current successful strategies")
            else:
                recommendations.append(f"Moderate {pattern_type.value} patterns - monitor and adjust as needed")
            
            if trend == ProgressTrend.DECLINING:
                recommendations.append("Pattern is worsening - review and intensify interventions")
            elif trend == ProgressTrend.IMPROVING:
                recommendations.append("Positive trend observed - maintain current approach")
            
            if triggers_identified:
                recommendations.append(f"Focus on managing identified triggers: {', '.join(triggers_identified)}")
            
            if effective_interventions:
                recommendations.append(f"Continue using effective interventions: {', '.join(effective_interventions)}")
            
            # Calculate confidence score based on data availability and consistency
            confidence_score = min(1.0, len(pattern_data) / 10.0)  # More data = higher confidence
            if len(session_ids) > 1:
                confidence_score *= 1.2  # Multiple sessions increase confidence
            confidence_score = min(1.0, confidence_score)
            
            return BehavioralPatternAnalysis(
                pattern_type=pattern_type,
                analysis_period_days=analysis_period_days,
                frequency_per_session=frequency_per_session,
                average_intensity=average_intensity,
                trend=trend,
                triggers_identified=triggers_identified,
                effective_interventions=effective_interventions,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            # Return error analysis
            return BehavioralPatternAnalysis(
                pattern_type=pattern_type,
                analysis_period_days=(end_date - start_date).days,
                frequency_per_session=0.0,
                average_intensity=0.0,
                trend=ProgressTrend.STABLE,
                triggers_identified=[],
                effective_interventions=[],
                recommendations=[f"Analysis error: {str(e)}"],
                confidence_score=0.0
            )
