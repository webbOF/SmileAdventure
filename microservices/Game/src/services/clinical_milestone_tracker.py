"""
Clinical Milestone Tracking Service for ASD Children
Provides sophisticated milestone detection, achievement validation,
and progression planning for therapeutic and educational goals.
"""

import asyncio
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from statistics import mean, median
from typing import Any, Dict, List, Optional, Tuple, Set
import logging

from ..models.asd_models import (
    ClinicalMilestone, ClinicalMilestoneEvent, BehavioralDataPoint,
    BehavioralPattern, EmotionalStateTransition, EmotionalState,
    SkillAssessment, ChildProfile, ASDSupportLevel, ProgressGoal,
    SessionMetrics
)

logger = logging.getLogger(__name__)


class ClinicalMilestoneTracker:
    """Advanced clinical milestone tracker for ASD children"""
    
    def __init__(self):
        # Milestone detection parameters
        self.confidence_threshold = 0.7
        self.min_evidence_count = 3
        self.observation_window_days = 14
        self.milestone_validation_period = 7  # Days to validate milestone
        
        # Milestone storage
        self.achieved_milestones: Dict[int, List[ClinicalMilestoneEvent]] = defaultdict(list)
        self.milestone_progress: Dict[int, Dict[ClinicalMilestone, float]] = defaultdict(dict)
        self.milestone_evidence: Dict[int, Dict[ClinicalMilestone, List[Dict]]] = defaultdict(lambda: defaultdict(list))
        
        # Initialize milestone criteria and progression paths
        self._initialize_milestone_framework()
    
    def _initialize_milestone_framework(self):
        """Initialize comprehensive milestone detection framework"""
        self.milestone_criteria = {
            # Communication Milestones
            ClinicalMilestone.FIRST_INTENTIONAL_COMMUNICATION: {
                "behavioral_indicators": [
                    BehavioralPattern.COMMUNICATION,
                    BehavioralPattern.SOCIAL_INTERACTION
                ],
                "required_evidence": [
                    {"type": "behavioral", "pattern": BehavioralPattern.COMMUNICATION, "min_intensity": 0.6, "count": 3},
                    {"type": "skill", "skill_name": "intentional_communication", "min_score": 0.5}
                ],
                "validation_criteria": {
                    "consistency_period_days": 7,
                    "min_occurrences_in_period": 2,
                    "supporting_contexts": ["social_interaction", "game_play", "structured_activity"]
                },
                "age_appropriateness": {"min_age": 3, "max_age": 12},
                "prerequisite_milestones": [],
                "next_milestones": [ClinicalMilestone.VERBAL_INITIATION, ClinicalMilestone.SOCIAL_REFERENCING]
            },
            
            ClinicalMilestone.IMPROVED_EYE_CONTACT: {
                "behavioral_indicators": [BehavioralPattern.SOCIAL_INTERACTION],
                "required_evidence": [
                    {"type": "behavioral", "pattern": BehavioralPattern.SOCIAL_INTERACTION, "min_intensity": 0.5, "count": 5},
                    {"type": "skill", "skill_name": "eye_contact", "min_score": 0.4},
                    {"type": "session_metric", "metric": "social_engagement", "min_value": 0.6}
                ],
                "validation_criteria": {
                    "consistency_period_days": 10,
                    "min_occurrences_in_period": 3,
                    "supporting_contexts": ["social_play", "conversation", "group_activity"]
                },
                "age_appropriateness": {"min_age": 2, "max_age": 15},
                "prerequisite_milestones": [],
                "next_milestones": [ClinicalMilestone.SOCIAL_REFERENCING, ClinicalMilestone.SHARED_ATTENTION]
            },
            
            ClinicalMilestone.VERBAL_INITIATION: {
                "behavioral_indicators": [BehavioralPattern.COMMUNICATION, BehavioralPattern.SOCIAL_INTERACTION],
                "required_evidence": [
                    {"type": "behavioral", "pattern": BehavioralPattern.COMMUNICATION, "min_intensity": 0.7, "count": 4},
                    {"type": "skill", "skill_name": "verbal_communication", "min_score": 0.6},
                    {"type": "emotional", "positive_communication_states": 0.6}
                ],
                "validation_criteria": {
                    "consistency_period_days": 14,
                    "min_occurrences_in_period": 3,
                    "supporting_contexts": ["spontaneous_communication", "requesting", "commenting"]
                },
                "age_appropriateness": {"min_age": 2, "max_age": 18},
                "prerequisite_milestones": [ClinicalMilestone.FIRST_INTENTIONAL_COMMUNICATION],
                "next_milestones": [ClinicalMilestone.TURN_TAKING_SUCCESS, ClinicalMilestone.PEER_INTERACTION_ATTEMPT]
            },
            
            ClinicalMilestone.SOCIAL_REFERENCING: {
                "behavioral_indicators": [BehavioralPattern.SOCIAL_INTERACTION, BehavioralPattern.COMMUNICATION],
                "required_evidence": [
                    {"type": "behavioral", "pattern": BehavioralPattern.SOCIAL_INTERACTION, "min_intensity": 0.6, "count": 4},
                    {"type": "skill", "skill_name": "social_awareness", "min_score": 0.5},
                    {"type": "emotional", "social_emotional_regulation": 0.5}
                ],
                "validation_criteria": {
                    "consistency_period_days": 10,
                    "min_occurrences_in_period": 2,
                    "supporting_contexts": ["uncertain_situations", "new_environments", "social_cues"]
                },
                "age_appropriateness": {"min_age": 3, "max_age": 15},
                "prerequisite_milestones": [ClinicalMilestone.IMPROVED_EYE_CONTACT],
                "next_milestones": [ClinicalMilestone.SHARED_ATTENTION, ClinicalMilestone.EMPATHY_DEMONSTRATION]
            },
            
            # Behavioral Milestones
            ClinicalMilestone.SELF_REGULATION_SKILL: {
                "behavioral_indicators": [BehavioralPattern.EMOTIONAL_REGULATION, BehavioralPattern.SENSORY_PROCESSING],
                "required_evidence": [
                    {"type": "behavioral", "pattern": BehavioralPattern.EMOTIONAL_REGULATION, "min_intensity": 0.6, "count": 5},
                    {"type": "skill", "skill_name": "emotional_regulation", "min_score": 0.6},
                    {"type": "emotional", "regulation_without_support": 0.5}
                ],
                "validation_criteria": {
                    "consistency_period_days": 14,
                    "min_occurrences_in_period": 4,
                    "supporting_contexts": ["stress_response", "transition_management", "sensory_challenges"]
                },
                "age_appropriateness": {"min_age": 3, "max_age": 18},
                "prerequisite_milestones": [],
                "next_milestones": [ClinicalMilestone.COPING_STRATEGY_USE, ClinicalMilestone.FLEXIBILITY_IMPROVEMENT]
            },
            
            ClinicalMilestone.FLEXIBILITY_IMPROVEMENT: {
                "behavioral_indicators": [BehavioralPattern.ADAPTIVE_BEHAVIOR, BehavioralPattern.TRANSITION_BEHAVIOR],
                "required_evidence": [
                    {"type": "behavioral", "pattern": BehavioralPattern.ADAPTIVE_BEHAVIOR, "min_intensity": 0.5, "count": 4},
                    {"type": "behavioral", "pattern": BehavioralPattern.TRANSITION_BEHAVIOR, "min_intensity": 0.6, "count": 3},
                    {"type": "skill", "skill_name": "behavioral_flexibility", "min_score": 0.5}
                ],
                "validation_criteria": {
                    "consistency_period_days": 14,
                    "min_occurrences_in_period": 3,
                    "supporting_contexts": ["routine_changes", "unexpected_events", "new_activities"]
                },
                "age_appropriateness": {"min_age": 4, "max_age": 18},
                "prerequisite_milestones": [ClinicalMilestone.SELF_REGULATION_SKILL],
                "next_milestones": [ClinicalMilestone.REDUCED_RIGIDITY, ClinicalMilestone.GENERALIZATION_SKILL]
            },
            
            # Social Milestones
            ClinicalMilestone.PEER_INTERACTION_ATTEMPT: {
                "behavioral_indicators": [BehavioralPattern.SOCIAL_INTERACTION, BehavioralPattern.COMMUNICATION],
                "required_evidence": [
                    {"type": "behavioral", "pattern": BehavioralPattern.SOCIAL_INTERACTION, "min_intensity": 0.6, "count": 4},
                    {"type": "skill", "skill_name": "peer_interaction", "min_score": 0.4},
                    {"type": "emotional", "positive_social_states": 0.5}
                ],
                "validation_criteria": {
                    "consistency_period_days": 14,
                    "min_occurrences_in_period": 2,
                    "supporting_contexts": ["peer_play", "group_activities", "social_games"]
                },
                "age_appropriateness": {"min_age": 4, "max_age": 18},
                "prerequisite_milestones": [ClinicalMilestone.VERBAL_INITIATION, ClinicalMilestone.SOCIAL_REFERENCING],
                "next_milestones": [ClinicalMilestone.TURN_TAKING_SUCCESS, ClinicalMilestone.SHARED_ATTENTION]
            },
            
            ClinicalMilestone.TURN_TAKING_SUCCESS: {
                "behavioral_indicators": [BehavioralPattern.SOCIAL_INTERACTION, BehavioralPattern.ADAPTIVE_BEHAVIOR],
                "required_evidence": [
                    {"type": "behavioral", "pattern": BehavioralPattern.SOCIAL_INTERACTION, "min_intensity": 0.7, "count": 3},
                    {"type": "skill", "skill_name": "turn_taking", "min_score": 0.6},
                    {"type": "session_metric", "metric": "cooperative_behavior", "min_value": 0.6}
                ],
                "validation_criteria": {
                    "consistency_period_days": 10,
                    "min_occurrences_in_period": 2,
                    "supporting_contexts": ["games", "conversations", "activities"]
                },
                "age_appropriateness": {"min_age": 3, "max_age": 18},
                "prerequisite_milestones": [ClinicalMilestone.PEER_INTERACTION_ATTEMPT],
                "next_milestones": [ClinicalMilestone.SHARED_ATTENTION, ClinicalMilestone.EMPATHY_DEMONSTRATION]
            },
            
            # Learning Milestones
            ClinicalMilestone.GENERALIZATION_SKILL: {
                "behavioral_indicators": [BehavioralPattern.ADAPTIVE_BEHAVIOR, BehavioralPattern.COMMUNICATION],
                "required_evidence": [
                    {"type": "skill", "skill_name": "generalization", "min_score": 0.6},
                    {"type": "behavioral", "pattern": BehavioralPattern.ADAPTIVE_BEHAVIOR, "min_intensity": 0.6, "count": 4},
                    {"type": "session_metric", "metric": "learning_transfer", "min_value": 0.5}
                ],
                "validation_criteria": {
                    "consistency_period_days": 21,
                    "min_occurrences_in_period": 3,
                    "supporting_contexts": ["different_settings", "novel_situations", "varied_materials"]
                },
                "age_appropriateness": {"min_age": 5, "max_age": 18},
                "prerequisite_milestones": [ClinicalMilestone.FLEXIBILITY_IMPROVEMENT],
                "next_milestones": [ClinicalMilestone.PROBLEM_SOLVING_IMPROVEMENT]
            },
            
            ClinicalMilestone.PROBLEM_SOLVING_IMPROVEMENT: {
                "behavioral_indicators": [BehavioralPattern.ADAPTIVE_BEHAVIOR, BehavioralPattern.ATTENTION_REGULATION],
                "required_evidence": [
                    {"type": "skill", "skill_name": "problem_solving", "min_score": 0.6},
                    {"type": "behavioral", "pattern": BehavioralPattern.ADAPTIVE_BEHAVIOR, "min_intensity": 0.7, "count": 3},
                    {"type": "session_metric", "metric": "task_completion", "min_value": 0.7}
                ],
                "validation_criteria": {
                    "consistency_period_days": 14,
                    "min_occurrences_in_period": 3,
                    "supporting_contexts": ["challenging_tasks", "novel_problems", "multi_step_activities"]
                },
                "age_appropriateness": {"min_age": 5, "max_age": 18},
                "prerequisite_milestones": [ClinicalMilestone.GENERALIZATION_SKILL],
                "next_milestones": [ClinicalMilestone.MEMORY_RETENTION_GAIN, ClinicalMilestone.PROCESSING_SPEED_IMPROVEMENT]
            }
        }
        
        # Milestone progression pathways
        self.milestone_pathways = {
            "communication_pathway": [
                ClinicalMilestone.FIRST_INTENTIONAL_COMMUNICATION,
                ClinicalMilestone.VERBAL_INITIATION,
                ClinicalMilestone.TURN_TAKING_SUCCESS,
                ClinicalMilestone.PEER_INTERACTION_ATTEMPT
            ],
            "social_pathway": [
                ClinicalMilestone.IMPROVED_EYE_CONTACT,
                ClinicalMilestone.SOCIAL_REFERENCING,
                ClinicalMilestone.SHARED_ATTENTION,
                ClinicalMilestone.EMPATHY_DEMONSTRATION
            ],
            "regulation_pathway": [
                ClinicalMilestone.SELF_REGULATION_SKILL,
                ClinicalMilestone.COPING_STRATEGY_USE,
                ClinicalMilestone.FLEXIBILITY_IMPROVEMENT,
                ClinicalMilestone.REDUCED_RIGIDITY
            ],
            "learning_pathway": [
                ClinicalMilestone.PROBLEM_SOLVING_IMPROVEMENT,
                ClinicalMilestone.GENERALIZATION_SKILL,
                ClinicalMilestone.MEMORY_RETENTION_GAIN,
                ClinicalMilestone.PROCESSING_SPEED_IMPROVEMENT
            ]
        }
    
    async def analyze_milestone_evidence(self, child_id: int,
                                       behavioral_data: List[BehavioralDataPoint],
                                       emotional_transitions: List[EmotionalStateTransition],
                                       skill_assessments: List[SkillAssessment],
                                       session_metrics: List[SessionMetrics] = None) -> Dict[ClinicalMilestone, float]:
        """Analyze evidence for potential milestone achievements"""
        try:
            milestone_scores = {}
            current_time = datetime.now()
            
            # Filter recent data
            recent_behavioral = [
                bd for bd in behavioral_data 
                if bd.timestamp >= current_time - timedelta(days=self.observation_window_days)
            ]
            recent_emotional = [
                et for et in emotional_transitions 
                if et.timestamp >= current_time - timedelta(days=self.observation_window_days)
            ]
            recent_skills = [
                sa for sa in skill_assessments 
                if sa.assessment_date >= current_time - timedelta(days=self.observation_window_days)
            ]
            recent_sessions = session_metrics or []
            
            # Analyze each milestone
            for milestone, criteria in self.milestone_criteria.items():
                score = await self._calculate_milestone_score(
                    milestone, criteria, recent_behavioral, recent_emotional, recent_skills, recent_sessions
                )
                milestone_scores[milestone] = score
                
                # Store evidence for tracking
                if score >= self.confidence_threshold * 0.8:  # Close to achievement
                    await self._store_milestone_evidence(child_id, milestone, {
                        "score": score,
                        "timestamp": current_time,
                        "behavioral_evidence": len(recent_behavioral),
                        "emotional_evidence": len(recent_emotional),
                        "skill_evidence": len(recent_skills)
                    })
            
            return milestone_scores
            
        except Exception as e:
            logger.error(f"Error analyzing milestone evidence for child {child_id}: {str(e)}")
            return {}
    
    async def _calculate_milestone_score(self, milestone: ClinicalMilestone, criteria: Dict,
                                       behavioral_data: List[BehavioralDataPoint],
                                       emotional_transitions: List[EmotionalStateTransition],
                                       skill_assessments: List[SkillAssessment],
                                       session_metrics: List[SessionMetrics]) -> float:
        """Calculate milestone achievement score based on multiple evidence types"""
        total_score = 0.0
        max_possible_score = 0.0
        
        for evidence_req in criteria["required_evidence"]:
            evidence_score = 0.0
            evidence_weight = 1.0
            
            if evidence_req["type"] == "behavioral":
                evidence_score = await self._score_behavioral_evidence(evidence_req, behavioral_data)
            elif evidence_req["type"] == "skill":
                evidence_score = await self._score_skill_evidence(evidence_req, skill_assessments)
            elif evidence_req["type"] == "emotional":
                evidence_score = await self._score_emotional_evidence(evidence_req, emotional_transitions)
            elif evidence_req["type"] == "session_metric":
                evidence_score = await self._score_session_evidence(evidence_req, session_metrics)
            
            total_score += evidence_score * evidence_weight
            max_possible_score += evidence_weight
        
        # Normalize score
        normalized_score = total_score / max_possible_score if max_possible_score > 0 else 0.0
        
        # Apply contextual validation
        validation_bonus = await self._apply_validation_criteria(criteria, behavioral_data, emotional_transitions)
        
        final_score = min(normalized_score + validation_bonus, 1.0)
        return final_score
    
    async def _score_behavioral_evidence(self, evidence_req: Dict, behavioral_data: List[BehavioralDataPoint]) -> float:
        """Score behavioral evidence for milestone"""
        pattern = evidence_req["pattern"]
        min_intensity = evidence_req["min_intensity"]
        required_count = evidence_req["count"]
        
        # Filter relevant observations
        relevant_obs = [
            bd for bd in behavioral_data 
            if bd.behavior_type == pattern and bd.intensity >= min_intensity
        ]
        
        if len(relevant_obs) >= required_count:
            # Calculate score based on intensity and consistency
            avg_intensity = mean([obs.intensity for obs in relevant_obs])
            count_factor = min(len(relevant_obs) / required_count, 2.0)  # Cap at 2x required
            return avg_intensity * count_factor * 0.5  # Max 1.0
        else:
            # Partial credit for some evidence
            return (len(relevant_obs) / required_count) * 0.3
    
    async def _score_skill_evidence(self, evidence_req: Dict, skill_assessments: List[SkillAssessment]) -> float:
        """Score skill assessment evidence for milestone"""
        skill_name = evidence_req["skill_name"]
        min_score = evidence_req["min_score"]
        
        # Find relevant skill assessments
        relevant_skills = [sa for sa in skill_assessments if skill_name in sa.skill_name.lower()]
        
        if not relevant_skills:
            return 0.0
        
        # Use most recent assessment
        latest_skill = max(relevant_skills, key=lambda x: x.assessment_date)
        
        if latest_skill.current_score >= min_score:
            # Exceeding minimum gives bonus
            excess = latest_skill.current_score - min_score
            return min(1.0, 0.7 + excess)
        else:
            # Partial credit for approaching minimum
            return (latest_skill.current_score / min_score) * 0.5
    
    async def _score_emotional_evidence(self, evidence_req: Dict, emotional_transitions: List[EmotionalStateTransition]) -> float:
        """Score emotional evidence for milestone"""
        if "positive_communication_states" in evidence_req:
            threshold = evidence_req["positive_communication_states"]
            communication_transitions = [
                et for et in emotional_transitions 
                if et.trigger_event and "communication" in et.trigger_event.lower()
            ]
            
            if not communication_transitions:
                return 0.0
            
            positive_outcomes = [
                et for et in communication_transitions 
                if et.to_state in [EmotionalState.HAPPY, EmotionalState.ENGAGED, EmotionalState.CURIOUS]
            ]
            
            positive_ratio = len(positive_outcomes) / len(communication_transitions)
            return 1.0 if positive_ratio >= threshold else positive_ratio * 0.7
        
        elif "regulation_without_support" in evidence_req:
            threshold = evidence_req["regulation_without_support"]
            regulation_transitions = [et for et in emotional_transitions if not et.support_needed]
            
            if not emotional_transitions:
                return 0.0
            
            self_regulation_ratio = len(regulation_transitions) / len(emotional_transitions)
            return 1.0 if self_regulation_ratio >= threshold else self_regulation_ratio * 0.8
        
        return 0.0
    
    async def _score_session_evidence(self, evidence_req: Dict, session_metrics: List[SessionMetrics]) -> float:
        """Score session metric evidence for milestone"""
        if not session_metrics:
            return 0.0
        
        metric_name = evidence_req["metric"]
        min_value = evidence_req["min_value"]
        
        # This would need to be implemented based on actual session metrics structure
        # For now, return a placeholder score
        return 0.5
    
    async def _apply_validation_criteria(self, criteria: Dict,
                                       behavioral_data: List[BehavioralDataPoint],
                                       emotional_transitions: List[EmotionalStateTransition]) -> float:
        """Apply validation criteria for milestone achievement"""
        validation = criteria.get("validation_criteria", {})
        bonus = 0.0
        
        # Check consistency over time
        consistency_days = validation.get("consistency_period_days", 7)
        min_occurrences = validation.get("min_occurrences_in_period", 1)
        
        # Group observations by day
        daily_observations = defaultdict(int)
        for bd in behavioral_data:
            day_key = bd.timestamp.date()
            daily_observations[day_key] += 1
        
        # Count days with sufficient observations
        sufficient_days = sum(1 for count in daily_observations.values() if count >= min_occurrences)
        
        if sufficient_days >= consistency_days * 0.7:  # 70% of required days
            bonus += 0.1
        
        # Check for supporting contexts
        supporting_contexts = validation.get("supporting_contexts", [])
        if supporting_contexts:
            context_evidence = 0
            for bd in behavioral_data:
                context = bd.context or {}
                for support_context in supporting_contexts:
                    if any(support_context in str(value).lower() for value in context.values()):
                        context_evidence += 1
                        break
            
            if context_evidence >= len(supporting_contexts):
                bonus += 0.1
        
        return bonus
    
    async def _store_milestone_evidence(self, child_id: int, milestone: ClinicalMilestone, evidence: Dict):
        """Store evidence for milestone tracking"""
        self.milestone_evidence[child_id][milestone].append(evidence)
        
        # Keep only recent evidence
        cutoff_date = datetime.now() - timedelta(days=30)
        self.milestone_evidence[child_id][milestone] = [
            ev for ev in self.milestone_evidence[child_id][milestone]
            if ev["timestamp"] >= cutoff_date
        ]
    
    async def check_milestone_achievement(self, child_id: int, milestone_scores: Dict[ClinicalMilestone, float],
                                        child_profile: ChildProfile) -> List[ClinicalMilestoneEvent]:
        """Check for milestone achievements and create events"""
        achievements = []
        
        for milestone, score in milestone_scores.items():
            if score >= self.confidence_threshold:
                # Check age appropriateness
                criteria = self.milestone_criteria[milestone]
                age_range = criteria.get("age_appropriateness", {})
                
                if (age_range.get("min_age", 0) <= child_profile.age <= age_range.get("max_age", 100)):
                    # Check if already achieved recently
                    recent_achievements = [
                        ma for ma in self.achieved_milestones[child_id]
                        if (ma.milestone == milestone and 
                            ma.achieved_at >= datetime.now() - timedelta(days=60))
                    ]
                    
                    if not recent_achievements:
                        # Create milestone achievement event
                        event = await self._create_milestone_event(
                            child_id, milestone, score, child_profile
                        )
                        achievements.append(event)
                        self.achieved_milestones[child_id].append(event)
        
        return achievements
    
    async def _create_milestone_event(self, child_id: int, milestone: ClinicalMilestone,
                                    confidence: float, child_profile: ChildProfile) -> ClinicalMilestoneEvent:
        """Create a milestone achievement event"""
        # Gather supporting evidence
        evidence = self.milestone_evidence[child_id].get(milestone, [])
        supporting_evidence = [
            f"Evidence score: {ev['score']:.2f} on {ev['timestamp'].strftime('%Y-%m-%d')}"
            for ev in evidence[-3:]  # Last 3 pieces of evidence
        ]
        
        # Determine clinical significance
        if confidence >= 0.9:
            significance = "high"
        elif confidence >= 0.8:
            significance = "medium"
        else:
            significance = "low"
        
        # Determine next milestone
        next_milestone = await self._determine_next_milestone(milestone, child_profile)
        
        event = ClinicalMilestoneEvent(
            milestone=milestone,
            achieved_at=datetime.now(),
            session_id=f"milestone_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=f"Achieved {milestone.value} with {confidence:.1%} confidence for {child_profile.name}",
            confidence_level=confidence,
            supporting_evidence=supporting_evidence,
            clinical_significance=significance,
            next_target_milestone=next_milestone
        )
        
        return event
    
    async def _determine_next_milestone(self, achieved_milestone: ClinicalMilestone,
                                      child_profile: ChildProfile) -> Optional[ClinicalMilestone]:
        """Determine the next appropriate milestone based on achievement"""
        criteria = self.milestone_criteria[achieved_milestone]
        next_milestones = criteria.get("next_milestones", [])
        
        if not next_milestones:
            return None
        
        # Check which next milestones are age-appropriate
        appropriate_next = []
        for next_milestone in next_milestones:
            next_criteria = self.milestone_criteria.get(next_milestone, {})
            age_range = next_criteria.get("age_appropriateness", {})
            
            if (age_range.get("min_age", 0) <= child_profile.age <= age_range.get("max_age", 100)):
                appropriate_next.append(next_milestone)
        
        # Return the first appropriate next milestone
        return appropriate_next[0] if appropriate_next else None
    
    async def generate_milestone_progression_plan(self, child_id: int, child_profile: ChildProfile,
                                                current_milestone_scores: Dict[ClinicalMilestone, float]) -> Dict[str, Any]:
        """Generate a comprehensive milestone progression plan"""
        plan = {
            "child_id": child_id,
            "current_achievements": [],
            "near_achievements": [],
            "recommended_targets": [],
            "pathway_progress": {},
            "estimated_timelines": {},
            "intervention_recommendations": []
        }
        
        # Identify current achievements
        achieved = [
            milestone for milestone, score in current_milestone_scores.items()
            if score >= self.confidence_threshold
        ]
        plan["current_achievements"] = [m.value for m in achieved]
        
        # Identify near achievements (70-90% threshold)
        near_achievements = [
            milestone for milestone, score in current_milestone_scores.items()
            if 0.7 <= score < self.confidence_threshold
        ]
        plan["near_achievements"] = [
            {"milestone": m.value, "progress": current_milestone_scores[m]} 
            for m in near_achievements
        ]
        
        # Analyze pathway progress
        for pathway_name, pathway_milestones in self.milestone_pathways.items():
            pathway_progress = []
            for milestone in pathway_milestones:
                score = current_milestone_scores.get(milestone, 0.0)
                pathway_progress.append({
                    "milestone": milestone.value,
                    "score": score,
                    "achieved": score >= self.confidence_threshold
                })
            plan["pathway_progress"][pathway_name] = pathway_progress
        
        # Generate recommendations
        plan["intervention_recommendations"] = await self._generate_milestone_recommendations(
            child_profile, current_milestone_scores, near_achievements
        )
        
        return plan
    
    async def _generate_milestone_recommendations(self, child_profile: ChildProfile,
                                                milestone_scores: Dict[ClinicalMilestone, float],
                                                near_achievements: List[ClinicalMilestone]) -> List[str]:
        """Generate specific recommendations for milestone progression"""
        recommendations = []
        
        # Focus on near achievements first
        for milestone in near_achievements:
            criteria = self.milestone_criteria[milestone]
            
            if milestone == ClinicalMilestone.IMPROVED_EYE_CONTACT:
                recommendations.append("Practice eye contact during preferred activities and social games")
            elif milestone == ClinicalMilestone.VERBAL_INITIATION:
                recommendations.append("Create opportunities for child to initiate communication")
            elif milestone == ClinicalMilestone.SELF_REGULATION_SKILL:
                recommendations.append("Teach and practice emotional regulation strategies")
            elif milestone == ClinicalMilestone.FLEXIBILITY_IMPROVEMENT:
                recommendations.append("Gradually introduce small changes to routines")
            elif milestone == ClinicalMilestone.PEER_INTERACTION_ATTEMPT:
                recommendations.append("Facilitate structured peer interaction opportunities")
        
        # Add support level specific recommendations
        if child_profile.asd_support_level == ASDSupportLevel.LEVEL_3:
            recommendations.extend([
                "Focus on foundational communication and regulation skills",
                "Use visual supports and structured environments",
                "Implement sensory accommodation strategies"
            ])
        elif child_profile.asd_support_level == ASDSupportLevel.LEVEL_2:
            recommendations.extend([
                "Balance structured support with independence opportunities",
                "Focus on social communication development",
                "Practice flexibility in familiar contexts"
            ])
        else:  # Level 1
            recommendations.extend([
                "Encourage self-advocacy and independence",
                "Focus on social nuances and peer relationships",
                "Support academic and vocational skill development"
            ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def validate_milestone_achievement(self, child_id: int, 
                                           milestone_event: ClinicalMilestoneEvent) -> bool:
        """Validate a milestone achievement over time"""
        validation_period = timedelta(days=self.milestone_validation_period)
        
        # Check if milestone has been consistently demonstrated
        evidence_count = len(self.milestone_evidence[child_id].get(milestone_event.milestone, []))
        
        # Simple validation based on evidence count and confidence
        return evidence_count >= self.min_evidence_count and milestone_event.confidence_level >= self.confidence_threshold
    
    async def get_child_milestone_status(self, child_id: int) -> Dict[str, Any]:
        """Get comprehensive milestone status for a child"""
        return {
            "achieved_milestones": [
                {
                    "milestone": event.milestone.value,
                    "achieved_at": event.achieved_at.isoformat(),
                    "confidence": event.confidence_level,
                    "significance": event.clinical_significance
                }
                for event in self.achieved_milestones[child_id]
            ],
            "milestone_progress": {
                milestone.value: score 
                for milestone, score in self.milestone_progress[child_id].items()
            },
            "evidence_count": {
                milestone.value: len(evidence)
                for milestone, evidence in self.milestone_evidence[child_id].items()
            }
        }
