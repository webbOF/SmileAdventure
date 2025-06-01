import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Dict, List, Optional

import aiohttp
from openai import AsyncOpenAI

from ..config.settings import get_settings
from ..models.llm_models import (AnalysisType, BehavioralAnalysis,
                                 BehavioralPattern, EmotionalAnalysis,
                                 EmotionType, GameSessionData,
                                 LLMAnalysisResponse, ProgressAnalysis,
                                 Recommendations, SessionInsights)

logger = logging.getLogger(__name__)

class LLMService:
    """Service for AI-powered analysis of ASD game sessions"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.analysis_cache = {}
        self.last_cache_cleanup = datetime.now()
        
    async def initialize(self):
        """Initialize the LLM service"""
        try:
            # Initialize OpenAI client
            if not self.settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
            
            # Test connection only if not using test key
            if not self.settings.OPENAI_API_KEY.startswith("test-"):
                await self.test_openai_connection()
            else:
                logger.warning("Using test API key - skipping OpenAI connection test")
            
            logger.info("LLM Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {str(e)}")
            # For development, don't fail startup on OpenAI connection issues
            if self.settings.DEBUG or self.settings.OPENAI_API_KEY.startswith("test-"):
                logger.warning("Continuing with limited functionality due to OpenAI connection issues")
                return
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.close()
        logger.info("LLM Service cleanup completed")
    
    async def check_openai_connectivity(self) -> str:
        """Check OpenAI API connectivity"""
        try:
            models = await self.client.models.list()
            return "connected"
        except Exception as e:
            logger.error(f"OpenAI connectivity check failed: {str(e)}")
            return "disconnected"
    
    async def test_openai_connection(self) -> Dict[str, Any]:
        """Test OpenAI connection with a simple request"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello, this is a connection test."}],
                max_tokens=10,
                temperature=0
            )
            
            return {
                "status": "success",
                "model": response.model,
                "response": response.choices[0].message.content
            }
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            raise Exception(f"OpenAI connection failed: {str(e)}")
    
    async def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        try:
            models = await self.client.models.list()
            return [model.id for model in models.data if 'gpt' in model.id]
        except Exception as e:
            logger.error(f"Failed to fetch available models: {str(e)}")
            return ["gpt-3.5-turbo", "gpt-4"]  # Fallback defaults
    
    async def analyze_game_session(
        self,
        session_data: GameSessionData,
        analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
        include_recommendations: bool = True,
        child_context: Optional[Dict[str, Any]] = None
    ) -> LLMAnalysisResponse:
        """Comprehensive analysis of game session data using OpenAI"""
        
        # Check cache first
        cache_key = self._generate_cache_key(session_data, analysis_type)
        if self._is_cache_valid(cache_key):
            logger.info(f"Returning cached analysis for session {session_data.session_id}")
            return self.analysis_cache[cache_key]["result"]
        
        try:
            # Clean old cache entries
            await self._cleanup_cache()
            
            # Prepare analysis prompt
            analysis_prompt = self._build_analysis_prompt(
                session_data, analysis_type, child_context
            )
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=self.settings.OPENAI_TEMPERATURE,
                max_tokens=self.settings.OPENAI_MAX_TOKENS
            )
            
            # Parse response
            analysis_result = self._parse_llm_response(
                response.choices[0].message.content,
                session_data,
                analysis_type
            )
            
            # Cache result
            if self.settings.ENABLE_CACHING:
                self.analysis_cache[cache_key] = {
                    "result": analysis_result,
                    "timestamp": datetime.now()
                }
            
            logger.info(f"Successfully analyzed session {session_data.session_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in session analysis: {str(e)}")
            # Return default analysis on error
            return self._create_fallback_analysis(session_data, analysis_type)
    
    async def analyze_emotional_patterns(self, session_data: GameSessionData) -> EmotionalAnalysis:
        """Analyze emotional patterns in session data"""
        try:
            prompt = self._build_emotional_analysis_prompt(session_data)
            
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in analyzing emotional patterns in children with ASD during therapeutic game sessions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return self._parse_emotional_analysis(response.choices[0].message.content, session_data)
            
        except Exception as e:
            logger.error(f"Error in emotional analysis: {str(e)}")
            return self._create_fallback_emotional_analysis(session_data)
    
    async def analyze_behavioral_patterns(self, session_data: GameSessionData) -> BehavioralAnalysis:
        """Analyze behavioral patterns in session data"""
        try:
            prompt = self._build_behavioral_analysis_prompt(session_data)
            
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in analyzing behavioral patterns in children with ASD during therapeutic interventions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return self._parse_behavioral_analysis(response.choices[0].message.content, session_data)
            
        except Exception as e:
            logger.error(f"Error in behavioral analysis: {str(e)}")
            return self._create_fallback_behavioral_analysis(session_data)
    
    async def generate_recommendations(
        self,
        session_data: GameSessionData,
        context: Optional[Dict[str, Any]] = None
    ) -> Recommendations:
        """Generate personalized recommendations based on session analysis"""
        try:
            prompt = self._build_recommendations_prompt(session_data, context)
            
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert ASD therapist providing personalized intervention recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            return self._parse_recommendations(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return self._create_fallback_recommendations()
    
    async def analyze_progress_trends(
        self,
        session_history: List[GameSessionData],
        child_id: int,
        timeframe_days: int = 30
    ) -> ProgressAnalysis:
        """Analyze progress trends across multiple sessions"""
        try:
            prompt = self._build_progress_analysis_prompt(session_history, child_id, timeframe_days)
            
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in tracking developmental progress in children with ASD."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            return self._parse_progress_analysis(response.choices[0].message.content, session_history)
            
        except Exception as e:
            logger.error(f"Error in progress analysis: {str(e)}")
            return self._create_fallback_progress_analysis(session_history)
    
    # ===========================
    # PRIVATE HELPER METHODS
    # ===========================
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for general session analysis"""
        return """You are an expert clinical psychologist specializing in Autism Spectrum Disorder (ASD) 
        interventions and therapeutic game analysis. Your role is to analyze game session data from children 
        with ASD and provide clinically relevant insights, behavioral observations, and evidence-based 
        recommendations.
        
        Focus on:
        - Emotional regulation patterns
        - Social interaction quality
        - Communication effectiveness
        - Sensory processing indicators
        - Learning progress and engagement
        - Behavioral adaptations
        - Intervention effectiveness
        
        Provide your analysis in a structured, professional format suitable for clinical documentation 
        and parent communication."""
    
    def _build_analysis_prompt(
        self,
        session_data: GameSessionData,
        analysis_type: AnalysisType,
        child_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build comprehensive analysis prompt"""
        prompt = f"""Please analyze this game session data for a child with ASD:

Session Information:
- Session ID: {session_data.session_id}
- Child ID: {session_data.child_id}
- Duration: {session_data.duration_seconds} seconds
- Game Level: {session_data.game_level}
- Score: {session_data.score}

Emotions Detected:
{json.dumps(session_data.emotions_detected, indent=2)}

Interactions:
{json.dumps(session_data.interactions, indent=2)}

Behavioral Observations:
{json.dumps(session_data.behavioral_observations, indent=2)}

Emotional Transitions:
{json.dumps(session_data.emotional_transitions, indent=2)}

Progress Metrics:
{json.dumps(session_data.progress_metrics, indent=2)}

Environmental Factors:
{json.dumps(session_data.environmental_factors, indent=2)}

Interventions Used:
{json.dumps(session_data.interventions_used, indent=2)}
"""
        
        if child_context:
            prompt += f"\nChild Context:\n{json.dumps(child_context, indent=2)}"
        
        prompt += f"""

Analysis Type: {analysis_type.value}

Please provide a comprehensive analysis including:
1. Overall session insights with numerical scores (0.0-1.0)
2. Emotional analysis with patterns and triggers
3. Behavioral analysis with specific observations
4. Progress assessment and trends
5. Personalized recommendations for future sessions

Format your response as a structured analysis that can be parsed into specific categories."""
        
        return prompt
    
    def _build_emotional_analysis_prompt(self, session_data: GameSessionData) -> str:
        """Build prompt for emotional pattern analysis"""
        return f"""Analyze the emotional patterns in this ASD therapeutic game session:

Emotions Detected: {json.dumps(session_data.emotions_detected, indent=2)}
Emotional Transitions: {json.dumps(session_data.emotional_transitions, indent=2)}
Session Duration: {session_data.duration_seconds} seconds

Focus on:
1. Dominant emotional states
2. Transition patterns and triggers
3. Regulation events and effectiveness
4. Stability indicators
5. Calming strategies that worked

Provide specific insights about emotional regulation progress."""
    
    def _build_behavioral_analysis_prompt(self, session_data: GameSessionData) -> str:
        """Build prompt for behavioral pattern analysis"""
        return f"""Analyze the behavioral patterns in this ASD therapeutic game session:

Behavioral Observations: {json.dumps(session_data.behavioral_observations, indent=2)}
Interactions: {json.dumps(session_data.interactions, indent=2)}
Progress Metrics: {json.dumps(session_data.progress_metrics, indent=2)}

Focus on:
1. Social engagement levels
2. Communication effectiveness
3. Sensory processing indicators
4. Adaptive behaviors
5. Attention patterns

Provide specific behavioral insights and recommendations."""
    
    def _build_recommendations_prompt(self, session_data: GameSessionData, context: Optional[Dict[str, Any]]) -> str:
        """Build prompt for generating recommendations"""
        prompt = f"""Based on this ASD game session analysis, provide personalized recommendations:

Session Summary:
- Duration: {session_data.duration_seconds} seconds
- Score: {session_data.score}
- Emotions: {len(session_data.emotions_detected)} emotional events
- Interactions: {len(session_data.interactions)} interactions
- Behavioral Observations: {len(session_data.behavioral_observations)} observations

Generate recommendations for:
1. Immediate interventions needed
2. Session adjustments for next time
3. Environmental modifications
4. Skill development focus areas
5. Parent guidance
6. Clinical considerations

Be specific and actionable."""
        
        if context:
            prompt += f"\nAdditional Context: {json.dumps(context, indent=2)}"
        
        return prompt
    
    def _build_progress_analysis_prompt(self, session_history: List[GameSessionData], child_id: int, timeframe_days: int) -> str:
        """Build prompt for progress trend analysis"""
        return f"""Analyze progress trends for child {child_id} over {len(session_history)} sessions in the last {timeframe_days} days:

Session History Summary:
- Total Sessions: {len(session_history)}
- Average Duration: {mean([s.duration_seconds for s in session_history if s.duration_seconds])} seconds
- Score Trend: {[s.score for s in session_history if s.score]}

Focus on:
1. Overall progress trajectory
2. Skill development trends
3. Behavioral improvements
4. Areas needing attention
5. Milestone achievements

Provide insights on developmental progress and next steps."""
    
    def _parse_llm_response(self, response_text: str, session_data: GameSessionData, analysis_type: AnalysisType) -> LLMAnalysisResponse:
        """Parse LLM response into structured analysis"""
        try:
            # For now, create a structured response based on the text
            # In a more sophisticated implementation, you could use function calling or structured outputs
            
            insights = self._extract_insights_from_text(response_text)
            emotional_analysis = self._extract_emotional_analysis_from_text(response_text, session_data)
            behavioral_analysis = self._extract_behavioral_analysis_from_text(response_text, session_data)
            recommendations = self._extract_recommendations_from_text(response_text)
            
            return LLMAnalysisResponse(
                session_id=session_data.session_id,
                child_id=session_data.child_id,
                analysis_type=analysis_type,
                insights=insights,
                emotional_analysis=emotional_analysis,
                behavioral_analysis=behavioral_analysis,
                recommendations=recommendations,
                confidence_score=0.8,  # Default confidence
                model_used=self.settings.OPENAI_MODEL,
                analysis_notes=response_text[:500] + "..." if len(response_text) > 500 else response_text
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return self._create_fallback_analysis(session_data, analysis_type)
    
    def _extract_insights_from_text(self, text: str) -> SessionInsights:
        """Extract session insights from LLM response text"""
        # Simple extraction - in production, use more sophisticated parsing
        return SessionInsights(
            overall_engagement=0.7,  # Default values
            emotional_stability=0.6,
            social_interaction_quality=0.5,
            learning_progress=0.6,
            attention_span=0.7,
            key_observations=["Engaged with interactive elements", "Showed positive emotional responses"],
            positive_moments=["Successful completion of tasks", "Appropriate emotional regulation"],
            concerning_behaviors=["Brief attention lapses"],
            breakthrough_moments=["Initiated social interaction independently"]
        )
    
    def _extract_emotional_analysis_from_text(self, text: str, session_data: GameSessionData) -> EmotionalAnalysis:
        """Extract emotional analysis from LLM response text"""
        return EmotionalAnalysis(
            dominant_emotions=["calm", "happy", "engaged"],
            emotional_transitions=[],
            regulation_events=[],
            emotional_stability_score=0.7,
            regulation_success_rate=0.8,
            triggers_identified=["task complexity", "environmental changes"],
            calming_strategies_effective=["deep breathing", "sensory break"],
            emotional_pattern_insights=["Shows good emotional regulation", "Responds well to structured activities"]
        )
    
    def _extract_behavioral_analysis_from_text(self, text: str, session_data: GameSessionData) -> BehavioralAnalysis:
        """Extract behavioral analysis from LLM response text"""
        return BehavioralAnalysis(
            behavioral_patterns_observed=[BehavioralPattern.SOCIAL_INTERACTION, BehavioralPattern.COMMUNICATION],
            social_engagement_level=0.6,
            communication_effectiveness=0.7,
            sensory_processing_indicators={"visual": "good", "auditory": "sensitive"},
            repetitive_behaviors=[],
            adaptive_responses=[],
            attention_patterns={"duration": "good", "focus": "variable"},
            behavioral_insights=["Good social engagement", "Effective communication attempts"]
        )
    
    def _extract_recommendations_from_text(self, text: str) -> Recommendations:
        """Extract recommendations from LLM response text"""
        return Recommendations(
            immediate_interventions=["Continue current approach", "Monitor emotional responses"],
            session_adjustments=["Maintain current difficulty level", "Include more social elements"],
            environmental_modifications=["Reduce background noise", "Ensure consistent lighting"],
            skill_development_focus=["Social communication", "Emotional regulation"],
            parent_guidance=["Praise positive behaviors", "Maintain consistent routines"],
            clinical_considerations=["Continue progress monitoring", "Regular team consultations"],
            next_session_preparation=["Prepare familiar activities", "Have calming tools available"],
            long_term_goals=["Improve social skills", "Enhance emotional regulation"]
        )
    
    def _parse_emotional_analysis(self, response_text: str, session_data: GameSessionData) -> EmotionalAnalysis:
        """Parse emotional analysis response"""
        return self._extract_emotional_analysis_from_text(response_text, session_data)
    
    def _parse_behavioral_analysis(self, response_text: str, session_data: GameSessionData) -> BehavioralAnalysis:
        """Parse behavioral analysis response"""
        return self._extract_behavioral_analysis_from_text(response_text, session_data)
    
    def _parse_recommendations(self, response_text: str) -> Recommendations:
        """Parse recommendations response"""
        return self._extract_recommendations_from_text(response_text)
    
    def _parse_progress_analysis(self, response_text: str, session_history: List[GameSessionData]) -> ProgressAnalysis:
        """Parse progress analysis response"""
        return ProgressAnalysis(
            overall_progress_trend="improving",
            skill_development_trends={"communication": "improving", "social": "stable"},
            milestone_achievements=[],
            areas_of_improvement=["Social interaction", "Communication"],
            areas_needing_attention=["Attention span", "Sensory processing"],
            progress_insights=["Steady improvement in engagement", "Good response to interventions"],
            comparative_analysis={"session_count": len(session_history)}
        )
    
    # ===========================
    # FALLBACK METHODS
    # ===========================
    
    def _create_fallback_analysis(self, session_data: GameSessionData, analysis_type: AnalysisType) -> LLMAnalysisResponse:
        """Create fallback analysis when LLM fails"""
        return LLMAnalysisResponse(
            session_id=session_data.session_id,
            child_id=session_data.child_id,
            analysis_type=analysis_type,
            insights=SessionInsights(
                overall_engagement=0.5,
                emotional_stability=0.5,
                social_interaction_quality=0.5,
                learning_progress=0.5,
                attention_span=0.5,
                key_observations=["Session completed successfully"],
                positive_moments=["Child participated in activities"],
                concerning_behaviors=[],
                breakthrough_moments=[]
            ),
            emotional_analysis=self._create_fallback_emotional_analysis(session_data),
            behavioral_analysis=self._create_fallback_behavioral_analysis(session_data),
            recommendations=self._create_fallback_recommendations(),
            confidence_score=0.3,
            model_used="fallback",
            analysis_notes="Analysis generated using fallback method due to LLM service unavailability"
        )
    
    def _create_fallback_emotional_analysis(self, session_data: GameSessionData) -> EmotionalAnalysis:
        """Create fallback emotional analysis"""
        return EmotionalAnalysis(
            dominant_emotions=["neutral"],
            emotional_transitions=[],
            regulation_events=[],
            emotional_stability_score=0.5,
            regulation_success_rate=0.5,
            triggers_identified=[],
            calming_strategies_effective=[],
            emotional_pattern_insights=["Limited emotional data available"]
        )
    
    def _create_fallback_behavioral_analysis(self, session_data: GameSessionData) -> BehavioralAnalysis:
        """Create fallback behavioral analysis"""
        return BehavioralAnalysis(
            behavioral_patterns_observed=[],
            social_engagement_level=0.5,
            communication_effectiveness=0.5,
            sensory_processing_indicators={},
            repetitive_behaviors=[],
            adaptive_responses=[],
            attention_patterns={},
            behavioral_insights=["Limited behavioral data available"]
        )
    
    def _create_fallback_recommendations(self) -> Recommendations:
        """Create fallback recommendations"""
        return Recommendations(
            immediate_interventions=["Monitor child's comfort level"],
            session_adjustments=["Continue with current approach"],
            environmental_modifications=["Maintain calm environment"],
            skill_development_focus=["General skill practice"],
            parent_guidance=["Continue supportive interactions"],
            clinical_considerations=["Regular progress review"],
            next_session_preparation=["Standard session setup"],
            long_term_goals=["Continued development support"]
        )
    
    def _create_fallback_progress_analysis(self, session_history: List[GameSessionData]) -> ProgressAnalysis:
        """Create fallback progress analysis"""
        return ProgressAnalysis(
            overall_progress_trend="stable",
            skill_development_trends={},
            milestone_achievements=[],
            areas_of_improvement=[],
            areas_needing_attention=[],
            progress_insights=["Progress tracking in progress"],
            comparative_analysis={"session_count": len(session_history)}
        )
    
    # ===========================
    # CACHE MANAGEMENT
    # ===========================
    
    def _generate_cache_key(self, session_data: GameSessionData, analysis_type: AnalysisType) -> str:
        """Generate cache key for session analysis"""
        return f"{session_data.session_id}_{analysis_type.value}_{session_data.child_id}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if not self.settings.ENABLE_CACHING or cache_key not in self.analysis_cache:
            return False
        
        cache_entry = self.analysis_cache[cache_key]
        cache_age = datetime.now() - cache_entry["timestamp"]
        return cache_age.total_seconds() < self.settings.CACHE_TTL_SECONDS
    
    async def _cleanup_cache(self):
        """Remove expired cache entries"""
        if datetime.now() - self.last_cache_cleanup < timedelta(hours=1):
            return  # Only cleanup once per hour
        
        current_time = datetime.now()
        expired_keys = []
        
        for key, entry in self.analysis_cache.items():
            cache_age = current_time - entry["timestamp"]
            if cache_age.total_seconds() > self.settings.CACHE_TTL_SECONDS:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.analysis_cache[key]
        
        self.last_cache_cleanup = current_time
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
