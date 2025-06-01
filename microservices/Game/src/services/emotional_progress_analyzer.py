"""
Advanced Emotional State Progression Analysis Service for ASD Children
Provides sophisticated emotional state tracking, transition analysis,
and emotional regulation support recommendations.
"""

import asyncio
import numpy as np
from collections import defaultdict, deque
from datetime import datetime, timedelta
from statistics import mean, stdev, mode
from typing import Any, Dict, List, Optional, Tuple
import logging

from ..models.asd_models import (
    EmotionalState, EmotionalStateTransition, EmotionalProgressProfile,
    BehavioralDataPoint, BehavioralPattern, ProgressTrend,
    ChildProfile, ASDSupportLevel
)

logger = logging.getLogger(__name__)


class EmotionalProgressAnalyzer:
    """Advanced emotional progression analyzer for ASD children"""
    
    def __init__(self):
        # Analysis parameters
        self.min_transitions_for_analysis = 5
        self.regulation_time_threshold = 300  # 5 minutes
        self.positive_emotional_states = {
            EmotionalState.HAPPY, EmotionalState.CURIOUS, 
            EmotionalState.ENGAGED, EmotionalState.REGULATED, EmotionalState.CALM
        }
        self.challenging_emotional_states = {
            EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED, 
            EmotionalState.OVERWHELMED, EmotionalState.WITHDRAWN
        }
        
        # Emotional regulation patterns
        self.regulation_patterns = {
            "quick_recovery": {"max_duration": 60, "score_bonus": 0.3},
            "self_regulation": {"requires_support": False, "score_bonus": 0.4},
            "effective_strategy": {"success_rate": 0.8, "score_bonus": 0.2},
            "consistent_regulation": {"variance_threshold": 0.2, "score_bonus": 0.3}
        }
        
        # In-memory storage for emotional data
        self.emotional_sequences: Dict[int, deque] = defaultdict(lambda: deque(maxlen=200))
        self.regulation_strategies: Dict[int, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        self.emotional_baselines: Dict[int, Dict[str, float]] = defaultdict(dict)
    
    async def analyze_emotional_progress(self, child_id: int, 
                                       transitions: List[EmotionalStateTransition],
                                       assessment_date: datetime = None) -> EmotionalProgressProfile:
        """Analyze comprehensive emotional progress for a child"""
        try:
            assessment_date = assessment_date or datetime.now()
            
            if not transitions:
                return self._create_baseline_profile(child_id, assessment_date)
            
            # Filter recent transitions (last 30 days)
            recent_transitions = [
                t for t in transitions 
                if t.timestamp >= assessment_date - timedelta(days=30)
            ]
            
            if len(recent_transitions) < self.min_transitions_for_analysis:
                return self._create_insufficient_data_profile(child_id, assessment_date, len(recent_transitions))
            
            # Analyze predominant emotional states
            predominant_states = await self._identify_predominant_states(recent_transitions)
            
            # Calculate regulation ability score
            regulation_ability = await self._calculate_regulation_ability(recent_transitions)
            
            # Calculate emotional range score
            emotional_range = await self._calculate_emotional_range(recent_transitions)
            
            # Calculate transition smoothness
            transition_smoothness = await self._calculate_transition_smoothness(recent_transitions)
            
            # Identify trigger sensitivity
            trigger_sensitivity = await self._analyze_trigger_sensitivity(recent_transitions)
            
            # Evaluate coping strategies effectiveness
            coping_effectiveness = await self._evaluate_coping_strategies(recent_transitions)
            
            # Assess social emotional skills
            social_emotional_skills = await self._assess_social_emotional_skills(recent_transitions)
            
            return EmotionalProgressProfile(
                child_id=child_id,
                assessment_date=assessment_date,
                predominant_states=predominant_states,
                regulation_ability_score=regulation_ability,
                emotional_range_score=emotional_range,
                transition_smoothness=transition_smoothness,
                trigger_sensitivity=trigger_sensitivity,
                coping_strategies_effectiveness=coping_effectiveness,
                social_emotional_skills=social_emotional_skills
            )
            
        except Exception as e:
            logger.error(f"Error analyzing emotional progress for child {child_id}: {str(e)}")
            return self._create_error_profile(child_id, assessment_date, str(e))
    
    async def _identify_predominant_states(self, transitions: List[EmotionalStateTransition]) -> List[EmotionalState]:
        """Identify the most common emotional states"""
        state_counts = defaultdict(int)
        
        # Count occurrences of each emotional state
        for transition in transitions:
            state_counts[transition.to_state] += 1
        
        # Sort by frequency and return top states
        sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return states that appear in at least 10% of transitions
        threshold = len(transitions) * 0.1
        predominant = [state for state, count in sorted_states if count >= threshold]
        
        return predominant[:5]  # Top 5 predominant states
    
    async def _calculate_regulation_ability(self, transitions: List[EmotionalStateTransition]) -> float:
        """Calculate emotional regulation ability score (0-1)"""
        if not transitions:
            return 0.5  # Neutral baseline
        
        regulation_scores = []
        
        for transition in transitions:
            score = 0.5  # Base score
            
            # Positive transitions (moving to better emotional states)
            if (transition.from_state in self.challenging_emotional_states and 
                transition.to_state in self.positive_emotional_states):
                score += 0.3
            
            # Quick regulation (fast recovery)
            if transition.transition_duration <= self.regulation_time_threshold:
                score += 0.2
            
            # Self-regulation (no support needed)
            if not transition.support_needed:
                score += 0.2
            
            # Effective strategy use
            if transition.regulation_strategy_used:
                score += 0.1
            
            regulation_scores.append(min(score, 1.0))
        
        return mean(regulation_scores) if regulation_scores else 0.5
    
    async def _calculate_emotional_range(self, transitions: List[EmotionalStateTransition]) -> float:
        """Calculate emotional range score (variety of emotions expressed)"""
        if not transitions:
            return 0.0
        
        # Count unique emotional states
        unique_states = set()
        for transition in transitions:
            unique_states.add(transition.from_state)
            unique_states.add(transition.to_state)
        
        # Calculate range score (more variety is generally positive for emotional development)
        total_possible_states = len(EmotionalState)
        range_score = len(unique_states) / total_possible_states
        
        # Adjust for balance (having mostly positive states is good)
        positive_states = unique_states.intersection(self.positive_emotional_states)
        negative_states = unique_states.intersection(self.challenging_emotional_states)
        
        balance_factor = 1.0
        if len(negative_states) > len(positive_states) * 2:
            balance_factor = 0.7  # Reduce score if too many challenging states
        elif len(positive_states) > len(negative_states) * 2:
            balance_factor = 1.2  # Boost score for predominantly positive states
        
        return min(range_score * balance_factor, 1.0)
    
    async def _calculate_transition_smoothness(self, transitions: List[EmotionalStateTransition]) -> float:
        """Calculate how smoothly the child handles emotional changes"""
        if len(transitions) < 2:
            return 0.5
        
        smoothness_scores = []
        
        for transition in transitions:
            score = 0.5  # Base score
            
            # Shorter transition times indicate smoother changes
            if transition.transition_duration <= 30:  # Less than 30 seconds
                score += 0.3
            elif transition.transition_duration <= 120:  # Less than 2 minutes
                score += 0.2
            elif transition.transition_duration <= 300:  # Less than 5 minutes
                score += 0.1
            
            # Gradual transitions (similar emotional valence) are smoother
            from_valence = self._get_emotional_valence(transition.from_state)
            to_valence = self._get_emotional_valence(transition.to_state)
            valence_difference = abs(from_valence - to_valence)
            
            if valence_difference <= 1:
                score += 0.2
            elif valence_difference <= 2:
                score += 0.1
            
            smoothness_scores.append(min(score, 1.0))
        
        return mean(smoothness_scores)
    
    def _get_emotional_valence(self, state: EmotionalState) -> int:
        """Get emotional valence (-2 to +2, negative to positive)"""
        valence_map = {
            EmotionalState.HAPPY: 2,
            EmotionalState.CURIOUS: 1,
            EmotionalState.ENGAGED: 2,
            EmotionalState.REGULATED: 1,
            EmotionalState.CALM: 1,
            EmotionalState.EXCITED: 1,
            EmotionalState.ANXIOUS: -1,
            EmotionalState.FRUSTRATED: -2,
            EmotionalState.OVERWHELMED: -2,
            EmotionalState.WITHDRAWN: -1
        }
        return valence_map.get(state, 0)
    
    async def _analyze_trigger_sensitivity(self, transitions: List[EmotionalStateTransition]) -> Dict[str, float]:
        """Analyze sensitivity to different triggers"""
        trigger_impacts = defaultdict(list)
        
        for transition in transitions:
            if transition.trigger_event:
                # Calculate impact (how negative the resulting emotional state is)
                impact = 1.0 - self._get_emotional_valence(transition.to_state) / 2.0
                trigger_impacts[transition.trigger_event].append(impact)
        
        # Calculate average impact for each trigger
        sensitivity_scores = {}
        for trigger, impacts in trigger_impacts.items():
            sensitivity_scores[trigger] = mean(impacts) if impacts else 0.5
        
        return sensitivity_scores
    
    async def _evaluate_coping_strategies(self, transitions: List[EmotionalStateTransition]) -> Dict[str, float]:
        """Evaluate effectiveness of different coping strategies"""
        strategy_effectiveness = defaultdict(list)
        
        for transition in transitions:
            if transition.regulation_strategy_used:
                # Calculate effectiveness based on outcome
                effectiveness = 0.5  # Base effectiveness
                
                # Positive outcome
                if transition.to_state in self.positive_emotional_states:
                    effectiveness += 0.3
                
                # Fast regulation
                if transition.transition_duration <= self.regulation_time_threshold:
                    effectiveness += 0.2
                
                # No additional support needed
                if not transition.support_needed:
                    effectiveness += 0.2
                
                strategy_effectiveness[transition.regulation_strategy_used].append(min(effectiveness, 1.0))
        
        # Calculate average effectiveness for each strategy
        effectiveness_scores = {}
        for strategy, scores in strategy_effectiveness.items():
            effectiveness_scores[strategy] = mean(scores) if scores else 0.5
        
        return effectiveness_scores
    
    async def _assess_social_emotional_skills(self, transitions: List[EmotionalStateTransition]) -> Dict[str, float]:
        """Assess various social-emotional skills"""
        skills = {
            "emotional_awareness": 0.5,
            "social_responsiveness": 0.5,
            "empathy_demonstration": 0.5,
            "emotional_expression": 0.5,
            "social_regulation": 0.5
        }
        
        # Analyze transitions for social-emotional indicators
        social_transitions = [
            t for t in transitions 
            if t.trigger_event and any(keyword in t.trigger_event.lower() 
                                     for keyword in ["social", "peer", "interaction", "group"])
        ]
        
        if social_transitions:
            # Social responsiveness based on social interaction outcomes
            positive_social_outcomes = sum(
                1 for t in social_transitions 
                if t.to_state in self.positive_emotional_states
            )
            skills["social_responsiveness"] = positive_social_outcomes / len(social_transitions)
            
            # Social regulation based on support needed in social situations
            self_regulated_social = sum(
                1 for t in social_transitions 
                if not t.support_needed
            )
            skills["social_regulation"] = self_regulated_social / len(social_transitions)
        
        # Emotional awareness based on variety of emotional expressions
        unique_emotions = set(t.to_state for t in transitions)
        skills["emotional_awareness"] = min(len(unique_emotions) / len(EmotionalState), 1.0)
        
        # Emotional expression based on transition frequency
        transition_frequency = len(transitions) / 30  # Assuming 30-day period
        skills["emotional_expression"] = min(transition_frequency / 5, 1.0)  # Normalized to 5 transitions per day
        
        return skills
    
    def _create_baseline_profile(self, child_id: int, assessment_date: datetime) -> EmotionalProgressProfile:
        """Create baseline emotional progress profile"""
        return EmotionalProgressProfile(
            child_id=child_id,
            assessment_date=assessment_date,
            predominant_states=[EmotionalState.CALM],
            regulation_ability_score=0.5,
            emotional_range_score=0.3,
            transition_smoothness=0.5,
            trigger_sensitivity={},
            coping_strategies_effectiveness={},
            social_emotional_skills={
                "emotional_awareness": 0.3,
                "social_responsiveness": 0.3,
                "empathy_demonstration": 0.3,
                "emotional_expression": 0.3,
                "social_regulation": 0.3
            }
        )
    
    def _create_insufficient_data_profile(self, child_id: int, assessment_date: datetime, 
                                        transition_count: int) -> EmotionalProgressProfile:
        """Create profile when insufficient data is available"""
        return EmotionalProgressProfile(
            child_id=child_id,
            assessment_date=assessment_date,
            predominant_states=[EmotionalState.CALM],
            regulation_ability_score=0.5,
            emotional_range_score=0.2,
            transition_smoothness=0.5,
            trigger_sensitivity={"insufficient_data": 0.5},
            coping_strategies_effectiveness={"need_more_observations": 0.5},
            social_emotional_skills={
                "emotional_awareness": 0.3,
                "social_responsiveness": 0.3,
                "empathy_demonstration": 0.3,
                "emotional_expression": 0.3,
                "social_regulation": 0.3
            }
        )
    
    def _create_error_profile(self, child_id: int, assessment_date: datetime, error: str) -> EmotionalProgressProfile:
        """Create error profile"""
        return EmotionalProgressProfile(
            child_id=child_id,
            assessment_date=assessment_date,
            predominant_states=[],
            regulation_ability_score=0.0,
            emotional_range_score=0.0,
            transition_smoothness=0.0,
            trigger_sensitivity={"error": 0.0},
            coping_strategies_effectiveness={"error": 0.0},
            social_emotional_skills={
                "emotional_awareness": 0.0,
                "social_responsiveness": 0.0,
                "empathy_demonstration": 0.0,
                "emotional_expression": 0.0,
                "social_regulation": 0.0
            }
        )
    
    async def detect_emotional_patterns(self, child_id: int, 
                                      transitions: List[EmotionalStateTransition]) -> Dict[str, Any]:
        """Detect specific emotional patterns that may require attention"""
        patterns = {
            "concerning_patterns": [],
            "positive_patterns": [],
            "recommendations": []
        }
        
        if not transitions:
            return patterns
        
        # Recent transitions (last 7 days)
        recent = [t for t in transitions if t.timestamp >= datetime.now() - timedelta(days=7)]
        
        if not recent:
            return patterns
        
        # Check for concerning patterns
        
        # 1. Frequent overwhelming episodes
        overwhelmed_count = sum(1 for t in recent if t.to_state == EmotionalState.OVERWHELMED)
        if overwhelmed_count > len(recent) * 0.3:
            patterns["concerning_patterns"].append("Frequent overwhelming episodes detected")
            patterns["recommendations"].append("Consider sensory environment modifications")
        
        # 2. Difficulty with emotional recovery
        slow_recovery = [t for t in recent if t.transition_duration > 600]  # > 10 minutes
        if len(slow_recovery) > len(recent) * 0.4:
            patterns["concerning_patterns"].append("Prolonged emotional regulation times")
            patterns["recommendations"].append("Implement additional emotional regulation strategies")
        
        # 3. Social withdrawal pattern
        withdrawn_count = sum(1 for t in recent if t.to_state == EmotionalState.WITHDRAWN)
        if withdrawn_count > len(recent) * 0.2:
            patterns["concerning_patterns"].append("Social withdrawal pattern observed")
            patterns["recommendations"].append("Focus on gentle social engagement activities")
        
        # Check for positive patterns
        
        # 1. Self-regulation improvement
        self_regulated = [t for t in recent if not t.support_needed and t.regulation_strategy_used]
        if len(self_regulated) > len(recent) * 0.6:
            patterns["positive_patterns"].append("Strong self-regulation skills developing")
        
        # 2. Quick emotional recovery
        quick_recovery = [t for t in recent if t.transition_duration <= 120]  # < 2 minutes
        if len(quick_recovery) > len(recent) * 0.7:
            patterns["positive_patterns"].append("Quick emotional recovery ability")
        
        # 3. Positive emotional predominance
        positive_transitions = [t for t in recent if t.to_state in self.positive_emotional_states]
        if len(positive_transitions) > len(recent) * 0.6:
            patterns["positive_patterns"].append("Predominantly positive emotional states")
        
        return patterns
    
    async def generate_emotional_regulation_recommendations(self, 
                                                          profile: EmotionalProgressProfile,
                                                          child_profile: ChildProfile = None) -> List[str]:
        """Generate specific recommendations for emotional regulation support"""
        recommendations = []
        
        # Based on regulation ability
        if profile.regulation_ability_score < 0.4:
            recommendations.extend([
                "Implement structured emotional regulation teaching",
                "Use visual emotional regulation tools and charts",
                "Practice calming strategies during calm periods"
            ])
        elif profile.regulation_ability_score < 0.6:
            recommendations.extend([
                "Continue reinforcing effective regulation strategies",
                "Gradually increase emotional challenges in safe environments"
            ])
        
        # Based on emotional range
        if profile.emotional_range_score < 0.3:
            recommendations.append("Encourage emotional vocabulary development")
        elif profile.emotional_range_score > 0.8:
            recommendations.append("Focus on emotional regulation rather than expanding range")
        
        # Based on transition smoothness
        if profile.transition_smoothness < 0.4:
            recommendations.extend([
                "Provide transition warnings and preparation",
                "Use visual schedules and timers for emotional transitions"
            ])
        
        # Based on trigger sensitivity
        high_sensitivity_triggers = [
            trigger for trigger, sensitivity in profile.trigger_sensitivity.items()
            if sensitivity > 0.7
        ]
        if high_sensitivity_triggers:
            recommendations.append(f"Develop coping strategies for triggers: {', '.join(high_sensitivity_triggers)}")
        
        # Based on social emotional skills
        low_social_skills = [
            skill for skill, score in profile.social_emotional_skills.items()
            if score < 0.4
        ]
        if low_social_skills:
            recommendations.append(f"Focus on developing: {', '.join(low_social_skills)}")
        
        return recommendations[:5]  # Return top 5 recommendations
