import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..models.asd_models import (AdaptiveSessionConfig, ASDRecommendation,
                                 ASDSessionReport, ASDSupportLevel,
                                 CalmingIntervention, ChildProfile,
                                 OverstimulationIndicator, ProgressInsight,
                                 SensoryProfile, SensorySensitivity,
                                 SessionMetrics)
from ..models.game_models import GameResponse, GameState


class ASDGameService:
    """Advanced Game Service with ASD-specific adaptive features"""
    
    def __init__(self):
        # Adaptive session configurations
        self.adaptive_sessions: Dict[str, AdaptiveSessionConfig] = {}
        self.session_metrics: Dict[str, List[SessionMetrics]] = {}
        self.child_profiles: Dict[int, ChildProfile] = {}
        
        # Overstimulation detection thresholds
        self.overstimulation_thresholds = {
            ASDSupportLevel.LEVEL_1: 0.8,
            ASDSupportLevel.LEVEL_2: 0.6,
            ASDSupportLevel.LEVEL_3: 0.4
        }
        
        # Calming intervention library
        self.calming_interventions = {
            "deep_breathing": CalmingIntervention(
                intervention_type="breathing",
                description="Guided deep breathing exercise",
                duration_seconds=60,
                instructions=[
                    "Let's take some slow, deep breaths together",
                    "Breathe in slowly through your nose for 4 counts",
                    "Hold your breath for 2 counts",
                    "Breathe out slowly through your mouth for 6 counts",
                    "Repeat 3 times"
                ],
                success_criteria=["Heart rate stabilized", "Reduced fidgeting", "Improved focus"]
            ),
            "sensory_break": CalmingIntervention(
                intervention_type="sensory",
                description="Sensory regulation break",
                duration_seconds=120,
                instructions=[
                    "Let's take a break from the screen",
                    "Look around the room and find 3 different colors",
                    "Listen for 2 different sounds",
                    "Feel the texture of your chair or desk",
                    "Take 3 deep breaths"
                ],
                success_criteria=["Reduced sensory overload", "Calmer behavior", "Ready to continue"]
            ),
            "movement_break": CalmingIntervention(
                intervention_type="movement",
                description="Physical movement for regulation",
                duration_seconds=90,
                instructions=[
                    "Stand up and stretch your arms up high",
                    "Roll your shoulders backwards 5 times",
                    "March in place for 10 steps",
                    "Do 5 gentle neck rolls",
                    "Sit down slowly and take a deep breath"
                ],
                success_criteria=["Improved proprioceptive input", "Reduced restlessness", "Better focus"]
            )
        }
    
    async def create_adaptive_session(self, child_profile: ChildProfile, session_id: str) -> AdaptiveSessionConfig:
        """
        Create an adaptive game session based on child's ASD profile
        
        Args:
            child_profile: Comprehensive child profile with ASD support needs
            session_id: Unique session identifier
            
        Returns:
            AdaptiveSessionConfig: Configured adaptive session
        """
        try:
            # Store child profile
            self.child_profiles[child_profile.child_id] = child_profile
            
            # Calculate initial sensory adjustments
            sensory_adjustments = await self._calculate_sensory_adjustments(child_profile)
            
            # Determine pacing based on support level
            pacing_adjustments = await self._calculate_pacing_adjustments(child_profile)
            
            # Configure content modifications
            content_modifications = await self._calculate_content_modifications(child_profile)
            
            # Set break intervals based on support level and age
            break_intervals = self._calculate_break_intervals(child_profile)
            
            # Set overstimulation threshold
            threshold = self.overstimulation_thresholds.get(
                child_profile.asd_support_level, 
                0.7
            )
            
            # Create adaptive configuration
            config = AdaptiveSessionConfig(
                session_id=session_id,
                child_profile=child_profile,
                current_difficulty=1,  # Start with easiest level
                sensory_adjustments=sensory_adjustments,
                pacing_adjustments=pacing_adjustments,
                content_modifications=content_modifications,
                break_intervals=break_intervals,
                overstimulation_threshold=threshold,
                adaptation_sensitivity=0.5
            )
            
            # Store configuration
            self.adaptive_sessions[session_id] = config
            self.session_metrics[session_id] = []
            
            return config
            
        except Exception as e:
            raise Exception(f"Failed to create adaptive session: {str(e)}")
    
    async def _calculate_sensory_adjustments(self, child_profile: ChildProfile) -> Dict[str, Any]:
        """Calculate sensory environment adjustments"""
        adjustments = {}
        sensitivities = child_profile.sensory_sensitivities
        
        # Audio adjustments
        if sensitivities.auditory < 30:  # Hypersensitive to sound
            adjustments["audio"] = {
                "volume_reduction": 0.3,
                "remove_sudden_sounds": True,
                "use_gentle_notifications": True,
                "background_music_volume": 0.1
            }
        elif sensitivities.auditory > 70:  # Hyposensitive to sound
            adjustments["audio"] = {
                "volume_boost": 0.2,
                "enhanced_audio_feedback": True,
                "use_rhythmic_sounds": True,
                "background_music_volume": 0.4
            }
        
        # Visual adjustments
        if sensitivities.visual < 30:  # Hypersensitive to light/visuals
            adjustments["visual"] = {
                "brightness_reduction": 0.4,
                "reduce_animations": True,
                "muted_colors": True,
                "minimize_flashing": True,
                "simplified_ui": True
            }
        elif sensitivities.visual > 70:  # Hyposensitive to visuals
            adjustments["visual"] = {
                "brightness_boost": 0.2,
                "enhanced_animations": True,
                "vibrant_colors": True,
                "additional_visual_feedback": True
            }
        
        # Tactile feedback adjustments (for touch interfaces)
        if sensitivities.tactile < 30:
            adjustments["tactile"] = {
                "gentle_haptics": True,
                "reduced_vibration": 0.3
            }
        elif sensitivities.tactile > 70:
            adjustments["tactile"] = {
                "enhanced_haptics": True,
                "increased_vibration": 0.2
            }
        
        return adjustments
    
    async def _calculate_pacing_adjustments(self, child_profile: ChildProfile) -> Dict[str, Any]:
        """Calculate pacing adjustments based on profile"""
        pacing = {}
        
        # Base pacing on support level
        if child_profile.asd_support_level == ASDSupportLevel.LEVEL_3:
            pacing.update({
                "instruction_delay": 3.0,  # Longer delays between instructions
                "response_timeout": 30.0,  # More time to respond
                "transition_delay": 2.0,   # Slower transitions
                "repetition_allowed": True,
                "pause_frequency": 0.3     # More frequent pauses
            })
        elif child_profile.asd_support_level == ASDSupportLevel.LEVEL_2:
            pacing.update({
                "instruction_delay": 2.0,
                "response_timeout": 20.0,
                "transition_delay": 1.5,
                "repetition_allowed": True,
                "pause_frequency": 0.2
            })
        else:  # Level 1
            pacing.update({
                "instruction_delay": 1.0,
                "response_timeout": 15.0,
                "transition_delay": 1.0,
                "repetition_allowed": True,
                "pause_frequency": 0.1
            })
        
        # Age-based adjustments
        if child_profile.age < 6:
            pacing["response_timeout"] *= 1.5
            pacing["instruction_delay"] *= 1.2
        elif child_profile.age > 12:
            pacing["response_timeout"] *= 0.8
            pacing["instruction_delay"] *= 0.8
        
        return pacing
    
    async def _calculate_content_modifications(self, child_profile: ChildProfile) -> Dict[str, Any]:
        """Calculate content modifications based on interests and triggers"""
        modifications = {}
        
        # Incorporate special interests
        if child_profile.interests:
            modifications["special_interests"] = {
                "themes": child_profile.interests[:3],  # Top 3 interests
                "integration_frequency": 0.4,  # 40% of content relates to interests
                "reward_system": "interest_based"
            }
        
        # Avoid known triggers
        if child_profile.triggers:
            modifications["content_filters"] = {
                "avoid_themes": child_profile.triggers,
                "alternative_scenarios": True,
                "gentle_exposure_therapy": False  # Only with explicit permission
            }
        
        # Communication preferences
        modifications["communication"] = {
            "use_simple_language": child_profile.asd_support_level in [ASDSupportLevel.LEVEL_2, ASDSupportLevel.LEVEL_3],
            "visual_supports": True,
            "social_stories": child_profile.asd_support_level != ASDSupportLevel.LEVEL_1,
            "literal_instructions": True
        }
        
        return modifications
    
    def _calculate_break_intervals(self, child_profile: ChildProfile) -> int:
        """Calculate appropriate break intervals"""
        base_interval = 300  # 5 minutes
        
        # Adjust for support level
        if child_profile.asd_support_level == ASDSupportLevel.LEVEL_3:
            base_interval = 180  # 3 minutes
        elif child_profile.asd_support_level == ASDSupportLevel.LEVEL_2:
            base_interval = 240  # 4 minutes
        
        # Adjust for age
        if child_profile.age < 6:
            base_interval = min(base_interval, 180)
        elif child_profile.age > 12:
            base_interval = max(base_interval, 360)
        
        return base_interval
    
    async def detect_overstimulation(self, session_metrics: SessionMetrics) -> Tuple[bool, List[OverstimulationIndicator], Optional[str]]:
        """
        Detect overstimulation based on behavioral patterns in session metrics
        
        Args:
            session_metrics: Current session performance metrics
            
        Returns:
            Tuple of (is_overstimulated, indicators, recommended_intervention)
        """
        try:
            session_id = session_metrics.session_id
            config = self.adaptive_sessions.get(session_id)
            
            if not config:
                return False, [], None
            
            indicators = []
            
            # Store metrics for trend analysis
            if session_id not in self.session_metrics:
                self.session_metrics[session_id] = []
            self.session_metrics[session_id].append(session_metrics)
            
            # Keep only last 10 metrics for analysis
            recent_metrics = self.session_metrics[session_id][-10:]
            
            # Detect rapid clicking/tapping
            if session_metrics.actions_per_minute > 120:  # More than 2 actions per second
                indicators.append(OverstimulationIndicator.RAPID_CLICKING)
            
            # Detect erratic movement patterns
            if len(recent_metrics) >= 3:
                recent_apm = [m.actions_per_minute for m in recent_metrics[-3:]]
                apm_variance = max(recent_apm) - min(recent_apm)
                if apm_variance > 50:
                    indicators.append(OverstimulationIndicator.ERRATIC_MOVEMENT)
            
            # Detect long pauses
            if session_metrics.pause_frequency > 0.3:  # More than 30% of time pausing
                indicators.append(OverstimulationIndicator.LONG_PAUSE)
              # Detect repeated actions (simplified approach - low activity with high errors)
            if session_metrics.actions_per_minute < 10 and session_metrics.error_rate > 0.3:
                indicators.append(OverstimulationIndicator.REPEATED_ACTIONS)
            
            # Detect difficulty progressing
            if session_metrics.progress_rate < 0.2 and session_metrics.error_rate > 0.4:
                indicators.append(OverstimulationIndicator.DIFFICULTY_PROGRESSING)
            
            # Detect high error rate
            if session_metrics.error_rate > 0.5:
                indicators.append(OverstimulationIndicator.HIGH_ERROR_RATE)
            
            # Calculate overall overstimulation score
            overstimulation_score = len(indicators) / 6.0  # Normalize to 0-1
            
            # Add weight based on specific indicators
            if OverstimulationIndicator.RAPID_CLICKING in indicators:
                overstimulation_score += 0.2
            if OverstimulationIndicator.HIGH_ERROR_RATE in indicators:
                overstimulation_score += 0.2
            
            overstimulation_score = min(overstimulation_score, 1.0)
            
            # Check if intervention is needed
            is_overstimulated = overstimulation_score >= config.overstimulation_threshold
            
            # Recommend intervention
            recommended_intervention = None
            if is_overstimulated:
                recommended_intervention = await self._select_calming_intervention(config, indicators)
            
            return is_overstimulated, indicators, recommended_intervention
            
        except Exception as e:
            # Log error but don't break the game flow
            print(f"Error in overstimulation detection: {str(e)}")
            return False, [], None
    
    async def _select_calming_intervention(self, config: AdaptiveSessionConfig, indicators: List[OverstimulationIndicator]) -> str:
        """Select appropriate calming intervention based on indicators"""
        child_profile = config.child_profile
        
        # Check child's preferred calming strategies
        if child_profile.calming_strategies:
            for strategy in child_profile.calming_strategies:
                if strategy in self.calming_interventions:
                    return strategy
        
        # Select based on indicators
        if OverstimulationIndicator.RAPID_CLICKING in indicators:
            return "deep_breathing"
        elif OverstimulationIndicator.ERRATIC_MOVEMENT in indicators:
            return "movement_break"
        else:
            return "sensory_break"
    
    async def generate_asd_recommendations(self, progress_data: Dict[str, Any]) -> List[ASDRecommendation]:
        """
        Generate clinical and educational recommendations based on game progress
        
        Args:
            progress_data: Comprehensive session and progress data
            
        Returns:
            List of ASD-specific recommendations
        """
        try:
            session_id = progress_data.get("session_id")
            child_id = progress_data.get("child_id")
            
            if not session_id or not child_id:
                return []
            
            config = self.adaptive_sessions.get(session_id)
            if not config:
                return []
            
            recommendations = []
            
            # Analyze session metrics for patterns
            session_metrics_list = self.session_metrics.get(session_id, [])
            if not session_metrics_list:
                return []
            
            # Generate sensory processing recommendations
            sensory_recommendations = await self._generate_sensory_recommendations(
                config, session_metrics_list, progress_data
            )
            recommendations.extend(sensory_recommendations)
            
            # Generate behavioral recommendations
            behavioral_recommendations = await self._generate_behavioral_recommendations(
                config, session_metrics_list, progress_data
            )
            recommendations.extend(behavioral_recommendations)
            
            # Generate educational recommendations
            educational_recommendations = await self._generate_educational_recommendations(
                config, session_metrics_list, progress_data
            )
            recommendations.extend(educational_recommendations)
            
            # Generate parent guidance recommendations
            parent_recommendations = await self._generate_parent_recommendations(
                config, session_metrics_list, progress_data
            )
            recommendations.extend(parent_recommendations)
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating ASD recommendations: {str(e)}")
            return []
    
    async def _generate_sensory_recommendations(self, config: AdaptiveSessionConfig, 
                                             metrics: List[SessionMetrics], 
                                             progress_data: Dict[str, Any]) -> List[ASDRecommendation]:
        """Generate sensory processing recommendations"""
        recommendations = []
        child_profile = config.child_profile
        
        # Analyze overstimulation patterns
        overstimulation_events = sum(1 for m in metrics if m.overstimulation_score > 0.6)
        
        if overstimulation_events > len(metrics) * 0.3:  # More than 30% of sessions
            recommendations.append(ASDRecommendation(
                recommendation_id=str(uuid.uuid4()),
                child_id=child_profile.child_id,
                session_id=config.session_id,
                recommendation_type="sensory",
                priority="high",
                title="Sensory Environment Optimization",
                description="Child shows frequent signs of sensory overload during digital activities",
                rationale=f"Detected overstimulation in {overstimulation_events} out of {len(metrics)} session segments",
                action_items=[
                    "Assess and modify sensory environment before digital activities",
                    "Implement regular sensory breaks every 3-5 minutes",
                    "Consider noise-canceling headphones or dimmed lighting",
                    "Provide proprioceptive input tools (fidget items, weighted lap pad)"
                ],
                resources=[
                    "Sensory Processing Disorder Foundation guidelines",
                    "Environmental modification checklist",
                    "Calming strategies toolkit"
                ],
                target_audience=["parent", "teacher"],
                timeframe="immediate",
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _generate_behavioral_recommendations(self, config: AdaptiveSessionConfig,
                                                 metrics: List[SessionMetrics],
                                                 progress_data: Dict[str, Any]) -> List[ASDRecommendation]:
        """Generate behavioral support recommendations"""
        recommendations = []
        child_profile = config.child_profile
        
        # Analyze attention and focus patterns
        avg_pause_frequency = sum(m.pause_frequency for m in metrics) / len(metrics)
        
        if avg_pause_frequency > 0.4:  # High pause frequency indicates attention challenges
            recommendations.append(ASDRecommendation(
                recommendation_id=str(uuid.uuid4()),
                child_id=child_profile.child_id,
                session_id=config.session_id,
                recommendation_type="behavioral",
                priority="medium",
                title="Attention and Focus Support",
                description="Child demonstrates need for additional attention support strategies",
                rationale=f"Average pause frequency of {avg_pause_frequency:.2f} indicates attention regulation needs",
                action_items=[
                    "Implement visual attention cues and timers",
                    "Break tasks into smaller, manageable steps",
                    "Use first-then visual schedules",
                    "Provide regular movement breaks"
                ],
                resources=[
                    "Visual supports library",
                    "Attention regulation strategies",
                    "Task breakdown templates"
                ],
                target_audience=["parent", "teacher", "therapist"],
                timeframe="1-2 weeks",
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _generate_educational_recommendations(self, config: AdaptiveSessionConfig,
                                                  metrics: List[SessionMetrics],
                                                  progress_data: Dict[str, Any]) -> List[ASDRecommendation]:
        """Generate educational support recommendations"""
        recommendations = []
        child_profile = config.child_profile
        
        # Analyze learning patterns
        avg_progress_rate = sum(m.progress_rate for m in metrics) / len(metrics)
        avg_error_rate = sum(m.error_rate for m in metrics) / len(metrics)
        
        if avg_progress_rate < 0.3 and avg_error_rate > 0.4:
            recommendations.append(ASDRecommendation(
                recommendation_id=str(uuid.uuid4()),
                child_id=child_profile.child_id,
                session_id=config.session_id,
                recommendation_type="educational",
                priority="high",
                title="Learning Strategy Adaptation",
                description="Current learning approach may need modification for optimal progress",
                rationale=f"Low progress rate ({avg_progress_rate:.2f}) with high error rate ({avg_error_rate:.2f})",
                action_items=[
                    "Implement multi-sensory learning approaches",
                    "Use child's special interests to motivate learning",
                    "Provide additional processing time",
                    "Consider alternative assessment methods"
                ],
                resources=[
                    "ASD-specific learning strategies guide",
                    "Special interests integration toolkit",
                    "Alternative assessment methods"
                ],
                target_audience=["teacher", "therapist"],
                timeframe="2-4 weeks",
                created_at=datetime.now()
            ))
        
        return recommendations
    
    async def _generate_parent_recommendations(self, config: AdaptiveSessionConfig,
                                             metrics: List[SessionMetrics],
                                             progress_data: Dict[str, Any]) -> List[ASDRecommendation]:
        """Generate parent guidance recommendations"""
        recommendations = []
        child_profile = config.child_profile
        
        recommendations.append(ASDRecommendation(
            recommendation_id=str(uuid.uuid4()),
            child_id=child_profile.child_id,
            session_id=config.session_id,
            recommendation_type="parent_guidance",
            priority="medium",
            title="Home Support Strategies",
            description="Strategies to support your child's continued progress at home",
            rationale="Based on observed patterns during digital learning activities",
            action_items=[
                "Create consistent routines around screen time",
                "Practice calming strategies learned in game at home",
                "Celebrate small achievements and progress",
                "Monitor for signs of overstimulation during other activities"
            ],
            resources=[
                "Parent support guide for ASD",
                "Home environment checklist",
                "Progress tracking tools"
            ],            target_audience=["parent"],
            timeframe="ongoing",
            created_at=datetime.now()
        ))
        
        return recommendations
    
    async def trigger_calming_intervention(self, session_id: str, intervention_type: str) -> CalmingIntervention:
        """Trigger a specific calming intervention"""
        if intervention_type in self.calming_interventions:
            return self.calming_interventions[intervention_type]
        else:
            # Default to sensory break
            return self.calming_interventions["sensory_break"]
    
    async def adjust_environmental_settings(self, session_id: str, overstimulation_level: float) -> Dict[str, Any]:
        """Dynamically adjust environmental settings based on overstimulation level"""
        adjustments = {}
        
        if overstimulation_level > 0.7:  # High overstimulation
            adjustments.update({
                "reduce_volume": 0.5,
                "dim_brightness": 0.4,
                "slow_animations": 0.3,
                "simplify_interface": True,
                "extend_timeouts": 2.0
            })
        elif overstimulation_level > 0.4:  # Moderate overstimulation
            adjustments.update({
                "reduce_volume": 0.2,
                "dim_brightness": 0.2,
                "slow_animations": 0.15,
                "extend_timeouts": 1.5
            })
        elif overstimulation_level > 0.1:  # Mild overstimulation
            adjustments.update({
                "reduce_volume": 0.1,
                "extend_timeouts": 1.2
            })
        
        return adjustments
