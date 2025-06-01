"""
Advanced Behavioral Pattern Analysis Service for ASD Children
Provides sophisticated behavioral pattern recognition, trend analysis, 
and predictive insights for therapeutic intervention planning.
"""

import asyncio
import numpy as np
from collections import defaultdict, deque
from datetime import datetime, timedelta
from statistics import mean, stdev, median
from typing import Any, Dict, List, Optional, Tuple
import logging

from ..models.asd_models import (
    BehavioralDataPoint, BehavioralPattern, BehavioralPatternAnalysis,
    ProgressTrend, EmotionalState, EmotionalStateTransition,
    ChildProfile, SessionMetrics, ASDSupportLevel
)

logger = logging.getLogger(__name__)


class BehavioralPatternAnalyzer:
    """Advanced behavioral pattern analyzer for ASD children"""
    
    def __init__(self):
        # Pattern detection parameters
        self.min_observations_for_analysis = 5
        self.trend_analysis_window_days = 14
        self.pattern_significance_threshold = 0.6
        self.behavioral_correlation_threshold = 0.5
        
        # In-memory pattern storage (use database in production)
        self.behavioral_sequences: Dict[int, deque] = defaultdict(lambda: deque(maxlen=100))
        self.pattern_templates: Dict[BehavioralPattern, Dict] = {}
        self.child_baselines: Dict[int, Dict[BehavioralPattern, float]] = defaultdict(dict)
        
        # Initialize pattern templates
        self._initialize_pattern_templates()
    
    def _initialize_pattern_templates(self):
        """Initialize behavioral pattern recognition templates"""
        self.pattern_templates = {
            BehavioralPattern.ATTENTION_REGULATION: {
                "indicators": ["focus_duration", "distraction_frequency", "task_completion"],
                "positive_thresholds": {"focus_duration": 0.7, "task_completion": 0.8},
                "negative_thresholds": {"distraction_frequency": 0.4},
                "contextual_factors": ["time_of_day", "task_complexity", "sensory_environment"]
            },
            BehavioralPattern.EMOTIONAL_REGULATION: {
                "indicators": ["emotional_stability", "recovery_time", "strategy_use"],
                "positive_thresholds": {"emotional_stability": 0.6, "strategy_use": 0.7},
                "negative_thresholds": {"recovery_time": 300},  # seconds
                "contextual_factors": ["transition_events", "social_interaction", "sensory_overload"]
            },
            BehavioralPattern.SENSORY_PROCESSING: {
                "indicators": ["sensory_tolerance", "seeking_behavior", "avoidance_behavior"],
                "positive_thresholds": {"sensory_tolerance": 0.6},
                "negative_thresholds": {"avoidance_behavior": 0.5},
                "contextual_factors": ["sensory_modality", "intensity_level", "duration"]
            },
            BehavioralPattern.SOCIAL_INTERACTION: {
                "indicators": ["eye_contact", "social_initiation", "reciprocity"],
                "positive_thresholds": {"eye_contact": 0.5, "social_initiation": 0.4},
                "negative_thresholds": {},
                "contextual_factors": ["group_size", "familiarity", "structure_level"]
            },
            BehavioralPattern.COMMUNICATION: {
                "indicators": ["verbal_attempts", "non_verbal_communication", "comprehension"],
                "positive_thresholds": {"verbal_attempts": 0.5, "comprehension": 0.7},
                "negative_thresholds": {},
                "contextual_factors": ["communication_partner", "topic_interest", "environment"]
            },
            BehavioralPattern.ADAPTIVE_BEHAVIOR: {
                "indicators": ["flexibility", "problem_solving", "routine_adaptation"],
                "positive_thresholds": {"flexibility": 0.6, "problem_solving": 0.5},
                "negative_thresholds": {},
                "contextual_factors": ["change_magnitude", "preparation_time", "support_available"]
            },
            BehavioralPattern.REPETITIVE_BEHAVIOR: {
                "indicators": ["stimming_frequency", "routine_rigidity", "restricted_interests"],
                "positive_thresholds": {},  # Lower frequency is better
                "negative_thresholds": {"stimming_frequency": 0.7, "routine_rigidity": 0.8},
                "contextual_factors": ["stress_level", "sensory_environment", "activity_type"]
            },
            BehavioralPattern.TRANSITION_BEHAVIOR: {
                "indicators": ["transition_success", "preparation_effectiveness", "recovery_time"],
                "positive_thresholds": {"transition_success": 0.7, "preparation_effectiveness": 0.6},
                "negative_thresholds": {"recovery_time": 180},  # seconds
                "contextual_factors": ["transition_type", "warning_time", "support_provided"]
            }
        }
    
    async def analyze_behavioral_pattern(self, child_id: int, pattern_type: BehavioralPattern,
                                       observations: List[BehavioralDataPoint]) -> BehavioralPatternAnalysis:
        """Analyze a specific behavioral pattern for trends and insights"""
        try:
            if not observations:
                return self._create_empty_analysis(child_id, pattern_type)
            
            # Filter observations for the specific pattern
            pattern_observations = [obs for obs in observations if obs.behavior_type == pattern_type]
            
            if len(pattern_observations) < self.min_observations_for_analysis:
                return self._create_insufficient_data_analysis(child_id, pattern_type, len(pattern_observations))
            
            # Calculate basic statistics
            analysis_period_days = (max(obs.timestamp for obs in pattern_observations) - 
                                  min(obs.timestamp for obs in pattern_observations)).days or 1
            
            frequency_per_session = len(pattern_observations) / max(1, analysis_period_days)
            average_intensity = mean([obs.intensity for obs in pattern_observations])
            
            # Determine trend
            trend = await self._calculate_behavioral_trend(pattern_observations)
            
            # Identify triggers and effective interventions
            triggers = await self._identify_behavioral_triggers(pattern_observations)
            effective_interventions = await self._identify_effective_interventions(pattern_observations)
            
            # Generate recommendations
            recommendations = await self._generate_behavioral_recommendations(
                pattern_type, pattern_observations, trend, triggers, effective_interventions
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(pattern_observations, trend)
            
            return BehavioralPatternAnalysis(
                pattern_type=pattern_type,
                analysis_period_days=analysis_period_days,
                frequency_per_session=frequency_per_session,
                average_intensity=average_intensity,
                trend=trend,
                triggers_identified=triggers,
                effective_interventions=effective_interventions,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error analyzing behavioral pattern {pattern_type} for child {child_id}: {str(e)}")
            return self._create_error_analysis(child_id, pattern_type, str(e))
    
    async def _calculate_behavioral_trend(self, observations: List[BehavioralDataPoint]) -> ProgressTrend:
        """Calculate the trend for behavioral observations"""
        if len(observations) < 3:
            return ProgressTrend.STABLE
        
        # Sort by timestamp
        sorted_obs = sorted(observations, key=lambda x: x.timestamp)
        
        # Calculate moving averages
        window_size = min(5, len(sorted_obs) // 2)
        if window_size < 2:
            return ProgressTrend.STABLE
        
        early_avg = mean([obs.intensity for obs in sorted_obs[:window_size]])
        late_avg = mean([obs.intensity for obs in sorted_obs[-window_size:]])
        
        # Calculate percentage change
        change = (late_avg - early_avg) / early_avg if early_avg > 0 else 0
        
        # Classify trend
        if change > 0.2:
            return ProgressTrend.SIGNIFICANT_IMPROVEMENT
        elif change > 0.1:
            return ProgressTrend.MODERATE_IMPROVEMENT
        elif change < -0.2:
            return ProgressTrend.CONCERNING_DECLINE
        elif change < -0.1:
            return ProgressTrend.MINOR_DECLINE
        else:
            # Check for inconsistency
            intensities = [obs.intensity for obs in sorted_obs]
            if len(intensities) > 4 and stdev(intensities) > 0.3:
                return ProgressTrend.INCONSISTENT
            return ProgressTrend.STABLE
    
    async def _identify_behavioral_triggers(self, observations: List[BehavioralDataPoint]) -> List[str]:
        """Identify common triggers for behavioral patterns"""
        triggers = []
        trigger_count = defaultdict(int)
        
        for obs in observations:
            if obs.trigger:
                trigger_count[obs.trigger] += 1
            
            # Analyze contextual factors
            context = obs.context or {}
            for key, value in context.items():
                if key in ["stressor", "trigger", "challenge"]:
                    trigger_count[str(value)] += 1
        
        # Return triggers that appear in at least 20% of observations
        threshold = len(observations) * 0.2
        triggers = [trigger for trigger, count in trigger_count.items() if count >= threshold]
        
        return triggers[:5]  # Return top 5 triggers
    
    async def _identify_effective_interventions(self, observations: List[BehavioralDataPoint]) -> List[str]:
        """Identify interventions that were effective for this behavioral pattern"""
        intervention_effectiveness = defaultdict(list)
        
        for obs in observations:
            if obs.intervention_used and obs.effectiveness_score is not None:
                intervention_effectiveness[obs.intervention_used].append(obs.effectiveness_score)
        
        # Calculate average effectiveness for each intervention
        effective_interventions = []
        for intervention, scores in intervention_effectiveness.items():
            avg_effectiveness = mean(scores)
            if avg_effectiveness >= 0.6:  # 60% effectiveness threshold
                effective_interventions.append(intervention)
        
        return effective_interventions
    
    async def _generate_behavioral_recommendations(self, pattern_type: BehavioralPattern,
                                                 observations: List[BehavioralDataPoint],
                                                 trend: ProgressTrend,
                                                 triggers: List[str],
                                                 effective_interventions: List[str]) -> List[str]:
        """Generate specific recommendations based on behavioral analysis"""
        recommendations = []
        
        # Pattern-specific recommendations
        if pattern_type == BehavioralPattern.ATTENTION_REGULATION:
            if trend in [ProgressTrend.MINOR_DECLINE, ProgressTrend.CONCERNING_DECLINE]:
                recommendations.extend([
                    "Consider shorter task intervals with frequent breaks",
                    "Implement visual attention cues and timers",
                    "Reduce environmental distractions during focused activities"
                ])
            elif trend == ProgressTrend.INCONSISTENT:
                recommendations.extend([
                    "Identify optimal times of day for focused activities",
                    "Monitor environmental factors affecting attention",
                    "Consider sensory regulation activities before focused tasks"
                ])
        
        elif pattern_type == BehavioralPattern.EMOTIONAL_REGULATION:
            if trend in [ProgressTrend.MINOR_DECLINE, ProgressTrend.CONCERNING_DECLINE]:
                recommendations.extend([
                    "Increase use of emotional regulation strategies",
                    "Provide more predictable routines and structure",
                    "Consider additional emotional support resources"
                ])
            if "transition" in triggers:
                recommendations.append("Implement transition preparation strategies")
        
        elif pattern_type == BehavioralPattern.SENSORY_PROCESSING:
            recommendations.extend([
                "Adjust sensory environment based on observed patterns",
                "Provide sensory breaks as needed",
                "Consider sensory diet recommendations"
            ])
            if trend == ProgressTrend.CONCERNING_DECLINE:
                recommendations.append("Consult with occupational therapist for sensory assessment")
        
        # Add intervention-based recommendations
        if effective_interventions:
            recommendations.append(f"Continue using effective interventions: {', '.join(effective_interventions)}")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _calculate_confidence_score(self, observations: List[BehavioralDataPoint], trend: ProgressTrend) -> float:
        """Calculate confidence score for the analysis"""
        base_confidence = min(len(observations) / 20, 1.0)  # More observations = higher confidence
        
        # Adjust based on data quality
        has_interventions = sum(1 for obs in observations if obs.intervention_used) / len(observations)
        has_context = sum(1 for obs in observations if obs.context) / len(observations)
        
        quality_factor = (has_interventions + has_context) / 2
        
        # Adjust based on trend clarity
        trend_clarity = {
            ProgressTrend.SIGNIFICANT_IMPROVEMENT: 1.0,
            ProgressTrend.MODERATE_IMPROVEMENT: 0.9,
            ProgressTrend.CONCERNING_DECLINE: 1.0,
            ProgressTrend.MINOR_DECLINE: 0.8,
            ProgressTrend.STABLE: 0.7,
            ProgressTrend.INCONSISTENT: 0.4
        }
        
        final_confidence = base_confidence * quality_factor * trend_clarity.get(trend, 0.5)
        return min(final_confidence, 1.0)
    
    def _create_empty_analysis(self, child_id: int, pattern_type: BehavioralPattern) -> BehavioralPatternAnalysis:
        """Create analysis for when no observations are available"""
        return BehavioralPatternAnalysis(
            pattern_type=pattern_type,
            analysis_period_days=0,
            frequency_per_session=0.0,
            average_intensity=0.0,
            trend=ProgressTrend.STABLE,
            triggers_identified=[],
            effective_interventions=[],
            recommendations=["Begin collecting behavioral observations for this pattern"],
            confidence_score=0.0
        )
    
    def _create_insufficient_data_analysis(self, child_id: int, pattern_type: BehavioralPattern, 
                                         observation_count: int) -> BehavioralPatternAnalysis:
        """Create analysis for insufficient data"""
        return BehavioralPatternAnalysis(
            pattern_type=pattern_type,
            analysis_period_days=1,
            frequency_per_session=observation_count,
            average_intensity=0.0,
            trend=ProgressTrend.STABLE,
            triggers_identified=[],
            effective_interventions=[],
            recommendations=[f"Need at least {self.min_observations_for_analysis} observations for reliable analysis"],
            confidence_score=0.2
        )
    
    def _create_error_analysis(self, child_id: int, pattern_type: BehavioralPattern, error: str) -> BehavioralPatternAnalysis:
        """Create analysis for error cases"""
        return BehavioralPatternAnalysis(
            pattern_type=pattern_type,
            analysis_period_days=0,
            frequency_per_session=0.0,
            average_intensity=0.0,
            trend=ProgressTrend.STABLE,
            triggers_identified=[],
            effective_interventions=[],
            recommendations=[f"Analysis error: {error}"],
            confidence_score=0.0
        )
    
    async def detect_behavioral_anomalies(self, child_id: int, recent_observations: List[BehavioralDataPoint]) -> List[str]:
        """Detect unusual behavioral patterns that may require attention"""
        anomalies = []
        
        if not recent_observations:
            return anomalies
        
        # Group by pattern type
        patterns = defaultdict(list)
        for obs in recent_observations:
            patterns[obs.behavior_type].append(obs)
        
        for pattern_type, observations in patterns.items():
            # Check for sudden intensity spikes
            intensities = [obs.intensity for obs in observations]
            if len(intensities) >= 3:
                recent_avg = mean(intensities[-3:])
                if recent_avg > 0.8:
                    anomalies.append(f"High intensity {pattern_type.value} behavior detected")
            
            # Check for concerning frequency
            time_span = max(obs.timestamp for obs in observations) - min(obs.timestamp for obs in observations)
            if time_span.seconds > 0:
                frequency = len(observations) / (time_span.seconds / 3600)  # per hour
                if frequency > 5:  # More than 5 occurrences per hour
                    anomalies.append(f"High frequency {pattern_type.value} behavior detected")
        
        return anomalies
    
    async def generate_pattern_insights(self, child_id: int, 
                                      pattern_analyses: List[BehavioralPatternAnalysis]) -> Dict[str, Any]:
        """Generate high-level insights from multiple pattern analyses"""
        insights = {
            "overall_progress": "stable",
            "areas_of_strength": [],
            "areas_of_concern": [],
            "recommended_focus": [],
            "intervention_priorities": []
        }
        
        improving_patterns = []
        declining_patterns = []
        
        for analysis in pattern_analyses:
            if analysis.trend in [ProgressTrend.SIGNIFICANT_IMPROVEMENT, ProgressTrend.MODERATE_IMPROVEMENT]:
                improving_patterns.append(analysis.pattern_type.value)
            elif analysis.trend in [ProgressTrend.MINOR_DECLINE, ProgressTrend.CONCERNING_DECLINE]:
                declining_patterns.append(analysis.pattern_type.value)
        
        insights["areas_of_strength"] = improving_patterns
        insights["areas_of_concern"] = declining_patterns
        
        # Determine overall progress
        if len(improving_patterns) > len(declining_patterns):
            insights["overall_progress"] = "improving"
        elif len(declining_patterns) > len(improving_patterns):
            insights["overall_progress"] = "concerning"
        
        # Generate focus recommendations
        if declining_patterns:
            insights["recommended_focus"] = declining_patterns[:3]  # Top 3 concerns
        else:
            # Focus on patterns with inconsistent trends
            inconsistent_patterns = [
                analysis.pattern_type.value for analysis in pattern_analyses
                if analysis.trend == ProgressTrend.INCONSISTENT
            ]
            insights["recommended_focus"] = inconsistent_patterns[:3]
        
        return insights
    
    async def analyze_pattern(self, child_id: int, pattern_type: BehavioralPattern, 
                             behavioral_data: List[BehavioralDataPoint]) -> Dict[str, Any]:
        """Analyze a specific behavioral pattern for a child"""
        try:
            if len(behavioral_data) < self.min_observations_for_analysis:
                return {
                    "pattern_type": pattern_type.value,
                    "analysis_status": "insufficient_data",
                    "recommendation": "Need more observations for meaningful analysis"
                }
            
            # Filter data for the specific pattern
            pattern_data = [dp for dp in behavioral_data if dp.behavior_type == pattern_type]
            
            if not pattern_data:
                return {
                    "pattern_type": pattern_type.value,
                    "analysis_status": "no_matching_data",
                    "recommendation": "No data found for this behavioral pattern"
                }
            
            # Calculate pattern score
            pattern_score = await self.calculate_pattern_score(child_id, pattern_type, pattern_data)
            
            # Detect trends
            trend_analysis = await self.detect_trends(child_id, pattern_type, pattern_data)
            
            # Generate recommendations
            recommendations = await self.generate_recommendations(child_id, pattern_type, pattern_score, trend_analysis)
            
            return {
                "pattern_type": pattern_type.value,
                "analysis_status": "complete",
                "pattern_score": pattern_score,
                "trend_analysis": trend_analysis,
                "recommendations": recommendations,
                "data_points_analyzed": len(pattern_data),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pattern {pattern_type} for child {child_id}: {str(e)}")
            return {
                "pattern_type": pattern_type.value,
                "analysis_status": "error",
                "error": str(e)
            }
    
    async def detect_trends(self, child_id: int, pattern_type: BehavioralPattern, 
                           pattern_data: List[BehavioralDataPoint]) -> Dict[str, Any]:
        """Detect trends in behavioral patterns"""
        try:
            # Sort data by timestamp
            sorted_data = sorted(pattern_data, key=lambda x: x.timestamp)
            
            if len(sorted_data) < 3:
                return {"trend": "insufficient_data", "confidence": 0.0}
            
            # Calculate trend direction using intensity values
            intensities = [dp.intensity for dp in sorted_data]
            durations = [dp.duration_seconds for dp in sorted_data]
            
            # Simple linear regression for trend detection
            n = len(intensities)
            x_values = list(range(n))
            
            # Calculate slope for intensity trend
            intensity_slope = self._calculate_slope(x_values, intensities)
            duration_slope = self._calculate_slope(x_values, durations)
            
            # Determine trend direction
            if abs(intensity_slope) < 0.01:
                trend_direction = "stable"
            elif intensity_slope > 0:
                trend_direction = "improving"
            else:
                trend_direction = "declining"
            
            # Calculate confidence based on consistency
            confidence = min(1.0, abs(intensity_slope) * 10)
            
            return {
                "trend": trend_direction,
                "confidence": confidence,
                "intensity_slope": intensity_slope,
                "duration_slope": duration_slope,
                "data_consistency": self._calculate_consistency(intensities),
                "pattern_frequency": len(sorted_data) / max(1, (sorted_data[-1].timestamp - sorted_data[0].timestamp).days)
            }
            
        except Exception as e:
            logger.error(f"Error detecting trends for {pattern_type}: {str(e)}")
            return {"trend": "error", "confidence": 0.0, "error": str(e)}
    
    async def calculate_pattern_score(self, child_id: int, pattern_type: BehavioralPattern, 
                                     pattern_data: List[BehavioralDataPoint]) -> float:
        """Calculate a normalized score for a behavioral pattern"""
        try:
            if not pattern_data:
                return 0.0
            
            # Get pattern template for scoring criteria
            template = self.pattern_templates.get(pattern_type, {})
            
            # Calculate base score from intensity and duration
            intensities = [dp.intensity for dp in pattern_data]
            durations = [dp.duration_seconds for dp in pattern_data]
            
            # Normalize durations to 0-1 scale (assuming max duration of 600 seconds)
            normalized_durations = [min(1.0, d / 600.0) for d in durations]
            
            # Weighted score calculation
            base_score = mean(intensities) * 0.7 + mean(normalized_durations) * 0.3
            
            # Apply contextual adjustments
            contextual_adjustment = await self._calculate_contextual_adjustment(
                child_id, pattern_type, pattern_data
            )
            
            # Final score with contextual adjustment
            final_score = min(1.0, max(0.0, base_score * contextual_adjustment))
            
            return round(final_score, 3)
            
        except Exception as e:
            logger.error(f"Error calculating pattern score for {pattern_type}: {str(e)}")
            return 0.0
    
    async def generate_recommendations(self, child_id: int, pattern_type: BehavioralPattern, 
                                     pattern_score: float, trend_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on pattern analysis"""
        try:
            recommendations = []
            
            # Get pattern template
            template = self.pattern_templates.get(pattern_type, {})
            
            # Score-based recommendations
            if pattern_score < 0.3:
                recommendations.append(f"Immediate intervention needed for {pattern_type.value}")
                recommendations.append("Consider structured behavioral support strategies")
            elif pattern_score < 0.6:
                recommendations.append(f"Monitor {pattern_type.value} closely and implement targeted interventions")
            else:
                recommendations.append(f"Continue current approach for {pattern_type.value}")
            
            # Trend-based recommendations
            trend = trend_analysis.get("trend", "unknown")
            confidence = trend_analysis.get("confidence", 0.0)
            
            if trend == "declining" and confidence > 0.5:
                recommendations.append("Pattern is declining - review current intervention strategies")
                recommendations.append("Consider environmental or approach modifications")
            elif trend == "improving" and confidence > 0.5:
                recommendations.append("Positive trend detected - maintain current approaches")
                recommendations.append("Consider generalizing successful strategies to other areas")
            
            # Pattern-specific recommendations
            pattern_specific = self._get_pattern_specific_recommendations(pattern_type, pattern_score)
            recommendations.extend(pattern_specific)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Error generating recommendations - consult with clinical team"]

    def _calculate_slope(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate slope using linear regression"""
        n = len(x_values)
        if n < 2:
            return 0.0
        
        x_mean = mean(x_values)
        y_mean = mean(y_values)
        
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _calculate_consistency(self, values: List[float]) -> float:
        """Calculate consistency score (lower standard deviation = higher consistency)"""
        if len(values) < 2:
            return 1.0
        
        try:
            std_dev = stdev(values)
            mean_val = mean(values)
            cv = std_dev / mean_val if mean_val != 0 else 1.0
            return max(0.0, 1.0 - cv)
        except:
            return 0.5
    
    async def _calculate_contextual_adjustment(self, child_id: int, pattern_type: BehavioralPattern, 
                                             pattern_data: List[BehavioralDataPoint]) -> float:
        """Calculate contextual adjustment factor for pattern score"""
        try:
            # Default adjustment
            adjustment = 1.0
            
            # Time-based adjustments
            recent_data = [dp for dp in pattern_data if dp.timestamp >= datetime.now() - timedelta(days=7)]
            if len(recent_data) > len(pattern_data) * 0.5:
                # More recent data is weighted higher
                adjustment *= 1.1
            
            # Intervention effectiveness
            intervention_data = [dp for dp in pattern_data if dp.intervention_used]
            if intervention_data:
                intervention_effectiveness = mean([dp.intensity for dp in intervention_data])
                no_intervention_effectiveness = mean([dp.intensity for dp in pattern_data if not dp.intervention_used])
                
                if intervention_effectiveness > no_intervention_effectiveness:
                    adjustment *= 1.2  # Interventions are helping
                else:
                    adjustment *= 0.9  # Interventions may need adjustment
            
            return min(1.5, max(0.5, adjustment))
            
        except Exception as e:
            logger.error(f"Error calculating contextual adjustment: {str(e)}")
            return 1.0
    
    def _get_pattern_specific_recommendations(self, pattern_type: BehavioralPattern, 
                                            pattern_score: float) -> List[str]:
        """Get pattern-specific recommendations"""
        recommendations = []
        
        if pattern_type == BehavioralPattern.ATTENTION_REGULATION:
            if pattern_score < 0.5:
                recommendations.extend([
                    "Use visual schedules and timers to support attention",
                    "Break tasks into smaller, manageable chunks",
                    "Minimize distracting stimuli in the environment"
                ])
            else:
                recommendations.append("Gradually increase task complexity to build attention skills")
        
        elif pattern_type == BehavioralPattern.EMOTIONAL_REGULATION:
            if pattern_score < 0.5:
                recommendations.extend([
                    "Teach and practice coping strategies",
                    "Use emotion identification tools and charts",
                    "Implement calming techniques and safe spaces"
                ])
            else:
                recommendations.append("Expand emotional vocabulary and self-advocacy skills")
        
        elif pattern_type == BehavioralPattern.SOCIAL_INTERACTION:
            if pattern_score < 0.5:
                recommendations.extend([
                    "Use structured social activities with clear expectations",
                    "Practice turn-taking and social scripts",
                    "Provide visual cues for social interactions"
                ])
            else:
                recommendations.append("Encourage natural peer interactions and social exploration")
        
        # Add more pattern-specific recommendations as needed
        
        return recommendations
