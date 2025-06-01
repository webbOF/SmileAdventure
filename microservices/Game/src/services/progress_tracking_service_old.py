"""
Advanced Progress Tracking Service for ASD Children
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


class ProgressTrackingService:
    """Advanced progress tracking service for ASD children"""
    
    def __init__(self):
        # In-memory storage for demo (use database in production)
        self.behavioral_data: Dict[int, List[BehavioralDataPoint]] = defaultdict(list)
        self.emotional_transitions: Dict[int, List[EmotionalStateTransition]] = defaultdict(list)
        self.skill_assessments: Dict[int, List[SkillAssessment]] = defaultdict(list)
        self.milestones: Dict[int, List[ClinicalMilestoneEvent]] = defaultdict(list)
        self.progress_goals: Dict[int, List[ProgressGoal]] = defaultdict(list)
        self.tracking_configs: Dict[int, ProgressTrackingConfig] = {}
        self.real_time_metrics: Dict[str, RealTimeProgressMetrics] = {}
        
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
        
        # Analyze patterns and update tracking
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
        
        # Analyze emotional regulation patterns
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
        
        # Check if this represents a milestone achievement
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
            
            analysis = await self._analyze_behavior_type(child_id, behavior_type, behavior_data)
            if analysis:
                analyses.append(analysis)
        
        return analyses
    
    async def _analyze_behavior_type(self, child_id: int, behavior_type: BehavioralPattern,
                                   behavior_data: List[BehavioralDataPoint]) -> Optional[BehavioralPatternAnalysis]:
        """Analyze specific behavior type for patterns"""
        if not behavior_data:
            return None
        
        # Calculate metrics
        intensities = [dp.intensity for dp in behavior_data]
        average_intensity = mean(intensities)
        frequency_per_session = len(behavior_data) / max(1, self.trend_analysis_days / 7)  # Estimate sessions per week
        
        # Determine trend
        if len(intensities) >= 5:
            # Simple trend analysis using linear regression slope
            x_values = list(range(len(intensities)))
            correlation = np.corrcoef(x_values, intensities)[0, 1] if len(set(intensities)) > 1 else 0
            
            if correlation > 0.3:
                trend = ProgressTrend.MODERATE_IMPROVEMENT if correlation > 0.6 else ProgressTrend.STABLE
            elif correlation < -0.3:
                trend = ProgressTrend.MINOR_DECLINE if correlation > -0.6 else ProgressTrend.CONCERNING_DECLINE
            else:
                trend = ProgressTrend.STABLE
        else:
            trend = ProgressTrend.STABLE
        
        # Identify triggers
        triggers = [dp.trigger for dp in behavior_data if dp.trigger]
        trigger_counts = {}
        for trigger in triggers:
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        common_triggers = [
            trigger for trigger, count in trigger_counts.items()
            if count >= 2
        ]
        
        # Identify effective interventions
        interventions = [dp.intervention_used for dp in behavior_data if dp.intervention_used]
        effective_interventions = list(set(interventions))
        
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
            confidence_score=min(1.0, len(behavior_data) / 10.0)  # Higher confidence with more data
        )
    
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
                recommendations.append(f"Focus on trigger management: {', '.join(triggers[:3])}")
        
        # Behavior-specific recommendations
        if behavior_type == BehavioralPattern.SENSORY_PROCESSING:
            recommendations.append("Review sensory diet and environmental modifications")
        elif behavior_type == BehavioralPattern.EMOTIONAL_REGULATION:
            recommendations.append("Increase coping strategy practice and emotional support")
        elif behavior_type == BehavioralPattern.SOCIAL_INTERACTION:
            recommendations.append("Provide more structured social opportunities")
        
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
        
        regulation_success_rate = len(regulation_transitions) / len(recent_transitions) if recent_transitions else 0
        
        # Update emotional progress profile
        await self._update_emotional_profile(child_id, regulation_success_rate, recent_transitions)
    
    async def _update_emotional_profile(self, child_id: int, regulation_success_rate: float,
                                      recent_transitions: List[EmotionalStateTransition]):
        """Update emotional progress profile based on recent data"""
        # This would typically update a stored profile
        # For now, we'll just track the key metrics
        
        # Calculate predominant states
        states = [t.to_state for t in recent_transitions]
        state_counts = {}
        for state in states:
            state_counts[state] = state_counts.get(state, 0) + 1
        
        predominant_states = [
            state for state, count in state_counts.items()
            if count >= 2
        ]
        
        # This data would be stored and used for reporting
        # Implementation would depend on your data persistence strategy
    
    async def generate_real_time_metrics(self, session_id: str, child_id: int,
                                       session_metrics: SessionMetrics) -> RealTimeProgressMetrics:
        """Generate real-time progress metrics during gameplay"""
        # Determine current emotional state based on session metrics
        current_emotional_state = self._infer_emotional_state(session_metrics)
        
        # Calculate engagement level
        engagement_level = self._calculate_engagement_level(session_metrics)
        
        # Identify frustration indicators
        frustration_indicators = self._identify_frustration_indicators(session_metrics)
        
        # Identify success moments
        success_moments = self._identify_success_moments(session_metrics)
        
        # Get recent behavioral observations for this session
        recent_observations = [
            dp for dp in self.behavioral_data[child_id]
            if dp.context.get("session_id") == session_id
        ]
        
        metrics = RealTimeProgressMetrics(
            session_id=session_id,
            child_id=child_id,
            timestamp=datetime.now(),
            current_emotional_state=current_emotional_state,
            engagement_level=engagement_level,
            frustration_indicators=frustration_indicators,
            success_moments=success_moments,
            skill_demonstrations={},  # Would be populated based on specific observations
            behavioral_observations=recent_observations,
            intervention_triggers=[],
            adaptation_recommendations=[]
        )
        
        self.real_time_metrics[session_id] = metrics
        return metrics
    
    def _infer_emotional_state(self, session_metrics: SessionMetrics) -> EmotionalState:
        """Infer emotional state from session metrics"""
        if session_metrics.overstimulation_score > 0.7:
            return EmotionalState.OVERWHELMED
        elif session_metrics.error_rate > 0.6:
            return EmotionalState.FRUSTRATED
        elif session_metrics.progress_rate > 0.7:
            return EmotionalState.ENGAGED
        elif session_metrics.actions_per_minute < 5:
            return EmotionalState.WITHDRAWN
        else:
            return EmotionalState.CALM
    
    def _calculate_engagement_level(self, session_metrics: SessionMetrics) -> float:
        """Calculate engagement level from session metrics"""
        engagement_factors = [
            min(1.0, session_metrics.actions_per_minute / 30),  # Activity level
            1.0 - session_metrics.pause_frequency,  # Continuous engagement
            session_metrics.progress_rate,  # Achievement
            1.0 - min(1.0, session_metrics.error_rate)  # Success rate
        ]
        
        return mean(engagement_factors)
    
    def _identify_frustration_indicators(self, session_metrics: SessionMetrics) -> List[str]:
        """Identify frustration indicators from session metrics"""
        indicators = []
        
        if session_metrics.error_rate > 0.5:
            indicators.append("high_error_rate")
        
        if session_metrics.actions_per_minute > 60:
            indicators.append("rapid_actions")
        
        if session_metrics.pause_frequency > 0.4:
            indicators.append("frequent_pauses")
        
        if session_metrics.progress_rate < 0.2:
            indicators.append("low_progress")
        
        return indicators
    
    def _identify_success_moments(self, session_metrics: SessionMetrics) -> List[str]:
        """Identify success moments from session metrics"""
        moments = []
        
        if session_metrics.progress_rate > 0.8:
            moments.append("high_achievement")
        
        if session_metrics.error_rate < 0.1:
            moments.append("accurate_performance")
        
        if session_metrics.overstimulation_score < 0.2:
            moments.append("well_regulated")
        
        return moments
    
    async def generate_progress_dashboard_data(self, child_id: int) -> ProgressDashboardData:
        """Generate comprehensive dashboard data for progress visualization"""
        dashboard_data = ProgressDashboardData(
            child_id=child_id,
            generated_at=datetime.now()
        )
        
        # Get current session metrics if available
        active_sessions = [
            metrics for session_id, metrics in self.real_time_metrics.items()
            if metrics.child_id == child_id
        ]
        
        if active_sessions:
            dashboard_data.current_session_metrics = active_sessions[-1]
        
        # Recent milestones (last 30 days)
        recent_milestones = [
            milestone for milestone in self.milestones[child_id]
            if milestone.achieved_at >= datetime.now() - timedelta(days=30)
        ]
        dashboard_data.recent_milestones = recent_milestones
        
        # Progress trends
        behavioral_analyses = await self._analyze_behavioral_patterns(child_id)
        progress_trends = {
            analysis.pattern_type.value: analysis.trend
            for analysis in behavioral_analyses
        }
        dashboard_data.progress_trends = progress_trends
        
        # Skill development chart data
        skill_chart_data = {}
        for skill_assessment in self.skill_assessments[child_id]:
            skill_name = skill_assessment.skill_name
            if skill_name not in skill_chart_data:
                skill_chart_data[skill_name] = []
            skill_chart_data[skill_name].append(skill_assessment.current_score)
        
        dashboard_data.skill_development_chart = skill_chart_data
        
        # Behavioral pattern summary
        behavioral_summary = {
            analysis.pattern_type: analysis
            for analysis in behavioral_analyses
        }
        dashboard_data.behavioral_pattern_summary = behavioral_summary
        
        # Goal progress summary
        dashboard_data.goal_progress_summary = self.progress_goals[child_id]
        
        return dashboard_data
    
    async def generate_long_term_progress_report(self, child_id: int,
                                               start_date: datetime,
                                               end_date: datetime) -> LongTermProgressReport:
        """Generate comprehensive long-term progress report"""
        # Filter data for the specified period
        period_milestones = [
            m for m in self.milestones[child_id]
            if start_date <= m.achieved_at <= end_date
        ]
        
        period_behavioral_data = [
            dp for dp in self.behavioral_data[child_id]
            if start_date <= dp.timestamp <= end_date
        ]
        
        # Generate behavioral improvements analysis
        behavioral_improvements = await self._analyze_behavioral_patterns(child_id)
        
        # Generate emotional development profile
        emotional_development = await self._generate_emotional_profile(child_id, start_date, end_date)
        
        # Generate cognitive progress metrics
        cognitive_progress = await self._generate_cognitive_metrics(child_id, start_date, end_date)
        
        # Generate sensory progress profile
        sensory_progress = await self._generate_sensory_profile(child_id, start_date, end_date)
        
        # Generate social communication progress
        social_communication_progress = await self._generate_social_communication_metrics(
            child_id, start_date, end_date
        )
        
        # Calculate overall progress score
        overall_score = self._calculate_overall_progress_score(
            period_milestones, behavioral_improvements
        )
        
        # Identify strengths and improvement areas
        strengths, improvements = self._analyze_strengths_and_improvements(behavioral_improvements)
        
        report = LongTermProgressReport(
            child_id=child_id,
            report_period_start=start_date,
            report_period_end=end_date,
            milestones_achieved=period_milestones,
            behavioral_improvements=behavioral_improvements,
            emotional_development=emotional_development,
            cognitive_progress=cognitive_progress,
            sensory_progress=sensory_progress,
            social_communication_progress=social_communication_progress,
            goals_status=self.progress_goals[child_id],
            overall_progress_score=overall_score,
            areas_of_strength=strengths,
            areas_for_improvement=improvements,
            clinical_recommendations=[],  # Would be generated based on analysis
            family_support_recommendations=[]  # Would be generated based on analysis
        )
        
        return report
    
    async def _generate_emotional_profile(self, child_id: int, start_date: datetime,
                                        end_date: datetime) -> EmotionalProgressProfile:
        """Generate emotional development profile for period"""
        period_transitions = [
            t for t in self.emotional_transitions[child_id]
            if start_date <= t.timestamp <= end_date
        ]
        
        if not period_transitions:
            return EmotionalProgressProfile(
                child_id=child_id,
                assessment_date=datetime.now(),
                regulation_ability_score=0.5,
                emotional_range_score=0.5,
                transition_smoothness=0.5
            )
        
        # Calculate regulation ability
        regulation_transitions = [
            t for t in period_transitions
            if t.to_state in [EmotionalState.CALM, EmotionalState.REGULATED]
        ]
        regulation_ability = len(regulation_transitions) / len(period_transitions)
        
        # Calculate emotional range
        unique_states = set([t.to_state for t in period_transitions])
        emotional_range = len(unique_states) / len(EmotionalState)
        
        # Calculate transition smoothness (average transition time)
        transition_times = [t.transition_duration for t in period_transitions if t.transition_duration > 0]
        transition_smoothness = 1.0 - (mean(transition_times) / 300.0) if transition_times else 0.5
        
        return EmotionalProgressProfile(
            child_id=child_id,
            assessment_date=datetime.now(),
            predominant_states=list(unique_states),
            regulation_ability_score=regulation_ability,
            emotional_range_score=emotional_range,
            transition_smoothness=max(0.0, min(1.0, transition_smoothness))
        )
    
    async def _generate_cognitive_metrics(self, child_id: int, start_date: datetime,
                                        end_date: datetime) -> CognitiveProgressMetrics:
        """Generate cognitive progress metrics for period"""
        # This would analyze cognitive-related behavioral data and assessments
        cognitive_assessments = [
            a for a in self.skill_assessments[child_id]
            if a.skill_category == "cognitive" and start_date <= a.assessment_date <= end_date
        ]
        
        # Calculate average scores for cognitive skills
        attention_scores = [a.current_score for a in cognitive_assessments if "attention" in a.skill_name]
        problem_solving_scores = [a.current_score for a in cognitive_assessments if "problem" in a.skill_name]
        
        return CognitiveProgressMetrics(
            child_id=child_id,
            assessment_date=datetime.now(),
            attention_span_progression=attention_scores,
            processing_speed_score=mean(attention_scores) if attention_scores else 0.5,
            working_memory_score=0.5,  # Would be calculated from specific assessments
            problem_solving_score=mean(problem_solving_scores) if problem_solving_scores else 0.5,
            learning_transfer_ability=0.5,  # Would be calculated from generalization observations
            cognitive_flexibility_score=0.5,  # Would be calculated from flexibility behaviors
            executive_function_score=0.5  # Would be calculated from executive function tasks
        )
    
    async def _generate_sensory_profile(self, child_id: int, start_date: datetime,
                                      end_date: datetime) -> SensoryProgressProfile:
        """Generate sensory progress profile for period"""
        sensory_behaviors = [
            dp for dp in self.behavioral_data[child_id]
            if dp.behavior_type == BehavioralPattern.SENSORY_PROCESSING
            and start_date <= dp.timestamp <= end_date
        ]
        
        # Analyze sensory overload frequency trend
        overload_frequency = len([dp for dp in sensory_behaviors if dp.intensity > 0.7])
        overload_trend = (
            ProgressTrend.MODERATE_IMPROVEMENT if overload_frequency < 3
            else ProgressTrend.CONCERNING_DECLINE if overload_frequency > 10
            else ProgressTrend.STABLE
        )
        
        return SensoryProgressProfile(
            child_id=child_id,
            assessment_date=datetime.now(),
            overload_frequency_trend=overload_trend,
            seeking_behavior_trend=ProgressTrend.STABLE,  # Would be calculated from seeking behaviors
        )
    
    async def _generate_social_communication_metrics(self, child_id: int, start_date: datetime,
                                                   end_date: datetime) -> SocialCommunicationProgress:
        """Generate social and communication progress metrics"""
        social_behaviors = [
            dp for dp in self.behavioral_data[child_id]
            if dp.behavior_type in [BehavioralPattern.SOCIAL_INTERACTION, BehavioralPattern.COMMUNICATION]
            and start_date <= dp.timestamp <= end_date
        ]
        
        # Calculate basic metrics
        social_initiation_count = len([
            dp for dp in social_behaviors 
            if dp.behavior_type == BehavioralPattern.SOCIAL_INTERACTION and dp.intensity > 0.5
        ])
        
        communication_count = len([
            dp for dp in social_behaviors 
            if dp.behavior_type == BehavioralPattern.COMMUNICATION and dp.intensity > 0.5
        ])
        
        return SocialCommunicationProgress(
            child_id=child_id,
            assessment_date=datetime.now(),
            eye_contact_frequency=0.5,  # Would be calculated from specific observations
            social_initiation_rate=float(social_initiation_count),
            turn_taking_success_rate=0.5,  # Would be calculated from turn-taking observations
            joint_attention_score=0.5,  # Would be calculated from joint attention tasks
            communication_complexity_score=0.5,  # Would be calculated from communication complexity
            social_reciprocity_score=0.5,  # Would be calculated from reciprocity observations
            peer_interaction_quality=0.5  # Would be calculated from peer interaction quality
        )
    
    def _calculate_overall_progress_score(self, milestones: List[ClinicalMilestoneEvent],
                                        behavioral_improvements: List[BehavioralPatternAnalysis]) -> float:
        """Calculate overall progress score"""
        milestone_score = len(milestones) * 0.1  # Each milestone worth 0.1
        
        improvement_score = 0.0
        for analysis in behavioral_improvements:
            if analysis.trend == ProgressTrend.SIGNIFICANT_IMPROVEMENT:
                improvement_score += 0.15
            elif analysis.trend == ProgressTrend.MODERATE_IMPROVEMENT:
                improvement_score += 0.1
            elif analysis.trend == ProgressTrend.STABLE:
                improvement_score += 0.05
        
        return min(1.0, milestone_score + improvement_score)
    
    def _analyze_strengths_and_improvements(self, behavioral_improvements: List[BehavioralPatternAnalysis]) -> Tuple[List[str], List[str]]:
        """Analyze areas of strength and areas for improvement"""
        strengths = []
        improvements = []
        
        for analysis in behavioral_improvements:
            if analysis.trend in [ProgressTrend.SIGNIFICANT_IMPROVEMENT, ProgressTrend.MODERATE_IMPROVEMENT]:
                strengths.append(f"{analysis.pattern_type.value} showing improvement")
            elif analysis.trend in [ProgressTrend.MINOR_DECLINE, ProgressTrend.CONCERNING_DECLINE]:
                improvements.append(f"{analysis.pattern_type.value} needs attention")
        
        return strengths, improvements
    
    # ===========================
    # API INTEGRATION METHODS
    # ===========================
    
    async def record_behavioral_data(self, child_id: int, session_id: str, 
                                   behavioral_data: List[BehavioralDataPoint]):
        """Record multiple behavioral observations from API"""
        for data_point in behavioral_data:
            # Update context with session info
            data_point.context["session_id"] = session_id
            self.behavioral_data[child_id].append(data_point)
            
            # Check for milestone achievements
            await self._check_milestone_achievement(child_id, data_point)
        
        # Analyze patterns after recording new data
        await self._analyze_behavioral_patterns(child_id)
    
    async def record_emotional_transitions(self, child_id: int, session_id: str,
                                         transitions: List[EmotionalStateTransition]):
        """Record multiple emotional transitions from API"""
        for transition in transitions:
            self.emotional_transitions[child_id].append(transition)
            
            # Update real-time metrics if session is active
            if session_id in self.real_time_metrics:
                self.real_time_metrics[session_id].current_emotional_state = transition.to_state
        
        # Analyze emotional patterns after recording
        await self._analyze_emotional_patterns(child_id)
    
    async def record_skill_assessments(self, child_id: int, assessments: List[SkillAssessment]):
        """Record multiple skill assessments from API"""
        for assessment in assessments:
            self.skill_assessments[child_id].append(assessment)
            
            # Check if this represents a milestone achievement
            await self._check_skill_milestone(child_id, assessment.skill_name, assessment.current_score)
    
    async def set_progress_goals(self, child_id: int, goals: List[ProgressGoal]):
        """Set progress goals for a child"""
        # Clear existing active goals and set new ones
        self.progress_goals[child_id] = goals
    
    async def evaluate_goal_progress(self, child_id: int) -> Dict[str, Any]:
        """Evaluate progress toward goals for a child"""
        goals = self.progress_goals.get(child_id, [])
        evaluation = {}
        
        for goal in goals:
            progress_percentage = (goal.current_measurement / goal.target_measurement) * 100
            evaluation[goal.goal_id] = {
                "goal_name": goal.goal_name,
                "progress_percentage": min(100, progress_percentage),
                "status": goal.status,
                "target_date": goal.target_date,
                "days_remaining": (goal.target_date - datetime.now()).days if goal.target_date else None,
                "recent_progress": goal.progress_markers[-3:] if goal.progress_markers else []
            }
        
        return evaluation
    
    async def detect_milestone_achievements(self, child_id: int, session_id: str,
                                          session_metrics: SessionMetrics) -> List[ClinicalMilestoneEvent]:
        """Detect milestone achievements from session data"""
        detected_milestones = []
        
        # Convert session metrics to behavioral observations for analysis
        behavioral_observations = self._session_metrics_to_behavioral_data(
            session_metrics, session_id
        )
        
        # Check each observation for potential milestones
        for observation in behavioral_observations:
            await self._check_milestone_achievement(child_id, observation)
        
        # Return milestones detected in the last few minutes
        recent_milestones = [
            m for m in self.milestones[child_id]
            if m.achieved_at >= datetime.now() - timedelta(minutes=5)
        ]
        
        return recent_milestones
    
    def _session_metrics_to_behavioral_data(self, session_metrics: SessionMetrics, 
                                          session_id: str) -> List[BehavioralDataPoint]:
        """Convert session metrics to behavioral data points for analysis"""
        observations = []
        timestamp = datetime.now()
        
        # Create behavioral observations based on session metrics
        if session_metrics.progress_rate > 0.7:
            observations.append(BehavioralDataPoint(
                timestamp=timestamp,
                behavior_type=BehavioralPattern.ATTENTION_REGULATION,
                intensity=session_metrics.progress_rate,
                duration_seconds=int(session_metrics.session_duration),
                context={"session_id": session_id, "metric_type": "progress_rate"}
            ))
        
        if session_metrics.error_rate < 0.2:
            observations.append(BehavioralDataPoint(
                timestamp=timestamp,
                behavior_type=BehavioralPattern.ADAPTIVE_BEHAVIOR,
                intensity=1.0 - session_metrics.error_rate,
                duration_seconds=int(session_metrics.session_duration),
                context={"session_id": session_id, "metric_type": "low_error_rate"}
            ))
        
        if session_metrics.overstimulation_score < 0.3:
            observations.append(BehavioralDataPoint(
                timestamp=timestamp,
                behavior_type=BehavioralPattern.SENSORY_PROCESSING,
                intensity=1.0 - session_metrics.overstimulation_score,
                duration_seconds=int(session_metrics.session_duration),
                context={"session_id": session_id, "metric_type": "good_sensory_regulation"}
            ))
        
        return observations
    
    async def analyze_behavioral_pattern(self, child_id: int, pattern_type: BehavioralPattern,
                                       start_date: datetime, end_date: datetime) -> BehavioralPatternAnalysis:
        """Analyze specific behavioral pattern for a time period"""
        period_data = [
            dp for dp in self.behavioral_data[child_id]
            if dp.behavior_type == pattern_type 
            and start_date <= dp.timestamp <= end_date
        ]
        
        if not period_data:
            # Return default analysis for patterns with no data
            return BehavioralPatternAnalysis(
                pattern_type=pattern_type,
                analysis_period_days=(end_date - start_date).days,
                frequency_per_session=0.0,
                average_intensity=0.0,
                trend=ProgressTrend.STABLE,
                triggers_identified=[],
                effective_interventions=[],
                recommendations=["Insufficient data for analysis"],
                confidence_score=0.0
            )
        
        return await self._analyze_behavior_type(child_id, pattern_type, period_data)
    
    async def analyze_emotional_progression(self, child_id: int, start_date: datetime,
                                          end_date: datetime) -> EmotionalProgressProfile:
        """Analyze emotional progression for a time period"""
        return await self._generate_emotional_profile(child_id, start_date, end_date)
    
    async def generate_dashboard_data(self, child_id: int, start_date: datetime,
                                    end_date: datetime) -> ProgressDashboardData:
        """Generate dashboard data for a specific time period"""
        dashboard_data = await self.generate_progress_dashboard_data(child_id)
        
        # Filter data for the specified period
        period_milestones = [
            milestone for milestone in dashboard_data.recent_milestones
            if start_date <= milestone.achieved_at <= end_date
        ]
        dashboard_data.recent_milestones = period_milestones
        
        return dashboard_data
    
    async def generate_long_term_report(self, child_id: int, start_date: datetime,
                                      end_date: datetime) -> LongTermProgressReport:
        """Generate long-term progress report (alias for API consistency)"""
        return await self.generate_long_term_progress_report(child_id, start_date, end_date)
    
    async def analyze_progress_trends(self, child_id: int, metric_type: str,
                                    start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze progress trends for specific metric types"""
        trends = {}
        
        if metric_type == "behavioral":
            behavioral_analyses = await self._analyze_behavioral_patterns(child_id)
            trends = {
                analysis.pattern_type.value: {
                    "trend": analysis.trend.value,
                    "frequency": analysis.frequency_per_session,
                    "intensity": analysis.average_intensity,
                    "confidence": analysis.confidence_score
                }
                for analysis in behavioral_analyses
            }
        
        elif metric_type == "emotional":
            emotional_profile = await self._generate_emotional_profile(child_id, start_date, end_date)
            trends = {
                "regulation_ability": emotional_profile.regulation_ability_score,
                "emotional_range": emotional_profile.emotional_range_score,
                "transition_smoothness": emotional_profile.transition_smoothness,
                "predominant_states": [state.value for state in emotional_profile.predominant_states]
            }
        
        elif metric_type == "cognitive":
            cognitive_metrics = await self._generate_cognitive_metrics(child_id, start_date, end_date)
            trends = {
                "attention_span": mean(cognitive_metrics.attention_span_progression) if cognitive_metrics.attention_span_progression else 0.0,
                "processing_speed": cognitive_metrics.processing_speed_score,
                "problem_solving": cognitive_metrics.problem_solving_score,
                "cognitive_flexibility": cognitive_metrics.cognitive_flexibility_score
            }
        
        elif metric_type == "social":
            social_metrics = await self._generate_social_communication_metrics(child_id, start_date, end_date)
            trends = {
                "social_initiation": social_metrics.social_initiation_rate,
                "turn_taking": social_metrics.turn_taking_success_rate,
                "joint_attention": social_metrics.joint_attention_score,
                "peer_interaction": social_metrics.peer_interaction_quality
            }
        
        return trends
    
    async def generate_clinical_insights(self, child_id: int, insight_type: str) -> List[Dict[str, Any]]:
        """Generate clinical insights and recommendations"""
        insights = []
        
        # Get recent behavioral analyses
        behavioral_analyses = await self._analyze_behavioral_patterns(child_id)
        
        if insight_type == "behavioral" or insight_type == "all":
            for analysis in behavioral_analyses:
                if analysis.trend in [ProgressTrend.MINOR_DECLINE, ProgressTrend.CONCERNING_DECLINE]:
                    insights.append({
                        "type": "behavioral_concern",
                        "priority": "high" if analysis.trend == ProgressTrend.CONCERNING_DECLINE else "medium",
                        "area": analysis.pattern_type.value,
                        "description": f"Declining trend in {analysis.pattern_type.value}",
                        "recommendations": analysis.recommendations
                    })
                elif analysis.trend in [ProgressTrend.SIGNIFICANT_IMPROVEMENT, ProgressTrend.MODERATE_IMPROVEMENT]:
                    insights.append({
                        "type": "behavioral_success",
                        "priority": "positive",
                        "area": analysis.pattern_type.value,
                        "description": f"Improvement observed in {analysis.pattern_type.value}",
                        "recommendations": ["Continue current strategies", "Consider expanding to related areas"]
                    })
        
        if insight_type == "developmental" or insight_type == "all":
            recent_milestones = [
                m for m in self.milestones[child_id]
                if m.achieved_at >= datetime.now() - timedelta(days=30)
            ]
            
            if len(recent_milestones) >= 2:
                insights.append({
                    "type": "developmental_progress",
                    "priority": "positive",
                    "area": "milestone_achievement",
                    "description": f"Achieved {len(recent_milestones)} milestones in the last 30 days",
                    "recommendations": ["Celebrate achievements", "Focus on next developmental targets"]
                })
            elif len(recent_milestones) == 0:
                insights.append({
                    "type": "developmental_plateau",
                    "priority": "medium",
                    "area": "milestone_achievement",
                    "description": "No milestones achieved in the last 30 days",
                    "recommendations": ["Review current goals", "Consider intervention adjustments"]
                })
        
        return insights
    
    async def check_progress_alerts(self, child_id: int) -> List[Dict[str, Any]]:
        """Check for progress alerts and warnings"""
        alerts = []
        
        # Check for regression patterns
        behavioral_analyses = await self._analyze_behavioral_patterns(child_id)
        for analysis in behavioral_analyses:
            if analysis.trend == ProgressTrend.CONCERNING_DECLINE:
                alerts.append({
                    "type": "regression_alert",
                    "severity": "high",
                    "area": analysis.pattern_type.value,
                    "message": f"Concerning decline detected in {analysis.pattern_type.value}",
                    "action_required": True,
                    "recommendations": ["Immediate review recommended", "Consider increasing support level"]
                })
            elif analysis.trend == ProgressTrend.MINOR_DECLINE:
                alerts.append({
                    "type": "monitoring_alert",
                    "severity": "medium",
                    "area": analysis.pattern_type.value,
                    "message": f"Minor decline observed in {analysis.pattern_type.value}",
                    "action_required": False,
                    "recommendations": ["Continue monitoring", "Review intervention effectiveness"]
                })
        
        # Check goal progress
        goal_evaluation = await self.evaluate_goal_progress(child_id)
        for goal_id, goal_data in goal_evaluation.items():
            if goal_data["days_remaining"] and goal_data["days_remaining"] < 30:
                if goal_data["progress_percentage"] < 50:
                    alerts.append({
                        "type": "goal_progress_alert",
                        "severity": "medium",
                        "area": "goal_achievement",
                        "message": f"Goal '{goal_data['goal_name']}' behind schedule",
                        "action_required": True,
                        "recommendations": ["Review goal timeline", "Adjust intervention strategies"]
                    })
        
        return alerts
    
    async def export_progress_data(self, child_id: int, format: str,
                                 start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Export progress data in various formats"""
        # Gather all relevant data for the period
        period_milestones = [
            m for m in self.milestones[child_id]
            if start_date <= m.achieved_at <= end_date
        ]
        
        period_behavioral_data = [
            dp for dp in self.behavioral_data[child_id]
            if start_date <= dp.timestamp <= end_date
        ]
        
        period_emotional_transitions = [
            t for t in self.emotional_transitions[child_id]
            if start_date <= t.timestamp <= end_date
        ]
        
        period_skill_assessments = [
            a for a in self.skill_assessments[child_id]
            if start_date <= a.assessment_date <= end_date
        ]
        
        export_data = {
            "child_id": child_id,
            "export_date": datetime.now().isoformat(),
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "format": format,
            "data": {
                "milestones": [m.dict() for m in period_milestones],
                "behavioral_observations": [dp.dict() for dp in period_behavioral_data],
                "emotional_transitions": [t.dict() for t in period_emotional_transitions],
                "skill_assessments": [a.dict() for a in period_skill_assessments],
                "progress_goals": [g.dict() for g in self.progress_goals[child_id]]
            },
            "summary": {
                "total_milestones": len(period_milestones),
                "total_behavioral_observations": len(period_behavioral_data),
                "total_emotional_transitions": len(period_emotional_transitions),
                "total_skill_assessments": len(period_skill_assessments)
            }
        }
        
        if format == "csv":
            # In a real implementation, this would convert to CSV format
            export_data["note"] = "CSV conversion would be implemented here"
        elif format == "pdf":
            # In a real implementation, this would generate a PDF report
            export_data["note"] = "PDF generation would be implemented here"
        
        return export_data
    
    async def generate_progress_summary(self, child_id: int) -> Dict[str, Any]:
        """Generate a concise progress summary for quick overview"""
        # Get recent data (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        recent_milestones = [
            m for m in self.milestones[child_id]
            if m.achieved_at >= start_date
        ]
        
        # Get latest skill assessments
        latest_assessments = {}
        for assessment in self.skill_assessments[child_id]:
            skill_name = assessment.skill_name
            if skill_name not in latest_assessments or assessment.assessment_date > latest_assessments[skill_name].assessment_date:
                latest_assessments[skill_name] = assessment
        
        # Calculate average progress across skills
        if latest_assessments:
            skill_progress = [
                (assessment.current_score - assessment.baseline_score) / max(0.1, assessment.baseline_score)
                for assessment in latest_assessments.values()
            ]
            average_skill_improvement = mean(skill_progress) * 100
        else:
            average_skill_improvement = 0.0
        
        # Get behavioral trend summary
        behavioral_analyses = await self._analyze_behavioral_patterns(child_id)
        positive_trends = len([a for a in behavioral_analyses if a.trend in [ProgressTrend.MODERATE_IMPROVEMENT, ProgressTrend.SIGNIFICANT_IMPROVEMENT]])
        concerning_trends = len([a for a in behavioral_analyses if a.trend in [ProgressTrend.MINOR_DECLINE, ProgressTrend.CONCERNING_DECLINE]])
        
        # Get goal progress
        goal_evaluation = await self.evaluate_goal_progress(child_id)
        goals_on_track = len([g for g in goal_evaluation.values() if g["progress_percentage"] >= 70])
        total_goals = len(goal_evaluation)
        
        summary = {
            "child_id": child_id,
            "summary_date": datetime.now().isoformat(),
            "period": "Last 30 days",
            "key_metrics": {
                "milestones_achieved": len(recent_milestones),
                "average_skill_improvement_percentage": round(average_skill_improvement, 1),
                "positive_behavioral_trends": positive_trends,
                "concerning_behavioral_trends": concerning_trends,
                "goals_on_track": goals_on_track,
                "total_active_goals": total_goals
            },
            "recent_achievements": [
                {
                    "milestone": m.milestone.value,
                    "date": m.achieved_at.isoformat(),
                    "confidence": m.confidence_level
                }
                for m in recent_milestones[-3:]  # Last 3 milestones
            ],
            "areas_of_progress": [
                a.pattern_type.value for a in behavioral_analyses
                if a.trend in [ProgressTrend.MODERATE_IMPROVEMENT, ProgressTrend.SIGNIFICANT_IMPROVEMENT]
            ][:3],  # Top 3 areas of progress
            "areas_needing_attention": [
                a.pattern_type.value for a in behavioral_analyses
                if a.trend in [ProgressTrend.MINOR_DECLINE, ProgressTrend.CONCERNING_DECLINE]
            ][:3],  # Top 3 areas needing attention
            "overall_status": self._determine_overall_status(positive_trends, concerning_trends, len(recent_milestones))
        }
        
        return summary
    
    def _determine_overall_status(self, positive_trends: int, concerning_trends: int, milestones_count: int) -> str:
        """Determine overall progress status"""
        if milestones_count >= 2 and positive_trends > concerning_trends:
            return "excellent_progress"
        elif milestones_count >= 1 and positive_trends >= concerning_trends:
            return "good_progress"
        elif positive_trends > concerning_trends:
            return "steady_progress"
        elif concerning_trends > positive_trends:
            return "needs_attention"
        else:
            return "stable"
    
    async def _check_skill_milestone(self, child_id: int, skill_name: str, new_score: float):
        """Check if skill improvement represents a milestone achievement"""
        # Get previous assessments for this skill
        skill_assessments = [
            a for a in self.skill_assessments[child_id]
            if a.skill_name == skill_name
        ]
        
        if len(skill_assessments) < 2:
            return  # Need at least 2 assessments to determine improvement
        
        # Sort by date and get the previous score
        skill_assessments.sort(key=lambda x: x.assessment_date)
        previous_score = skill_assessments[-2].current_score
        baseline_score = skill_assessments[0].baseline_score
        
        # Check for significant improvement
        improvement_threshold = 0.2  # 20% improvement
        if new_score - previous_score >= improvement_threshold:
            # This could represent a milestone - check which milestones relate to this skill
            skill_milestone_mapping = {
                "attention_span": ClinicalMilestone.PROBLEM_SOLVING_IMPROVEMENT,
                "emotional_regulation": ClinicalMilestone.SELF_REGULATION_SKILL,
                "social_interaction": ClinicalMilestone.PEER_INTERACTION_ATTEMPT,
                "communication_clarity": ClinicalMilestone.VERBAL_INITIATION
            }
            
            related_milestone = skill_milestone_mapping.get(skill_name)
            if related_milestone:
                # Record milestone achievement
                milestone_event = ClinicalMilestoneEvent(
                    milestone=related_milestone,
                    achieved_at=datetime.now(),
                    session_id="skill_assessment",
                    description=f"Achieved through significant improvement in {skill_name}",
                    confidence_level=min(1.0, (new_score - baseline_score) / 0.5),
                    supporting_evidence=[f"Skill score improved from {previous_score:.2f} to {new_score:.2f}"],
                    clinical_significance="medium",
                    next_target_milestone=self._get_next_milestone(related_milestone)
                )
                
                self.milestones[child_id].append(milestone_event)
