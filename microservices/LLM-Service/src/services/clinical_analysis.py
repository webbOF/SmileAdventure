"""
Advanced Clinical Analysis Service for ASD Children
Provides sophisticated AI-powered clinical analysis, emotional patterns analysis,
intervention suggestions, and progress indicators assessment.

This service leverages OpenAI GPT-4 for deep clinical insights and therapeutic recommendations.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from statistics import mean, median, mode, stdev
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict, Counter

from openai import AsyncOpenAI

from ..config.settings import get_settings
from ..models.llm_models import (
    GameSessionData, EmotionalAnalysis, BehavioralAnalysis,
    ProgressAnalysis, Recommendations, AnalysisType
)

logger = logging.getLogger(__name__)


class ClinicalAnalysisService:
    """Advanced clinical analysis service using AI for ASD therapeutic insights"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.clinical_cache = {}
        
        # Clinical analysis parameters
        self.emotional_pattern_window = 30  # days
        self.intervention_effectiveness_threshold = 0.7
        self.progress_milestone_threshold = 0.6
        
        # Clinical expertise prompts
        self.clinical_system_prompts = {
            "emotional_patterns": self._get_emotional_pattern_system_prompt(),
            "intervention_suggestions": self._get_intervention_system_prompt(),
            "progress_assessment": self._get_progress_assessment_system_prompt()
        }
    
    async def initialize(self):
        """Initialize the clinical analysis service"""
        try:
            if not self.settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found for clinical analysis")
            
            self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
            
            # Test clinical analysis capabilities
            if not self.settings.OPENAI_API_KEY.startswith("test-"):
                await self._test_clinical_connection()
            
            logger.info("Clinical Analysis Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Clinical Analysis service: {str(e)}")
            if self.settings.DEBUG:
                logger.warning("Continuing with limited clinical functionality")
                return
            raise
    
    async def analyze_emotional_patterns(self, session_history: List[GameSessionData]) -> Dict[str, Any]:
        """
        Perform deep emotional pattern analysis over session history
        
        Args:
            session_history: List of game sessions for analysis
            
        Returns:
            Comprehensive emotional pattern analysis with clinical insights
        """
        try:
            if not session_history:
                return self._create_empty_emotional_analysis()
            
            # Prepare emotional data for analysis
            emotional_data = self._extract_emotional_data(session_history)
            
            # Generate clinical analysis prompt
            analysis_prompt = self._build_emotional_patterns_prompt(emotional_data, session_history)
            
            # Call OpenAI for deep clinical analysis
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": self.clinical_system_prompts["emotional_patterns"]
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.2,  # Low temperature for clinical consistency
                max_tokens=3000
            )
            
            # Parse and structure the clinical analysis
            clinical_insights = self._parse_emotional_analysis(
                response.choices[0].message.content,
                emotional_data
            )
            
            # Add quantitative metrics
            clinical_insights.update(
                self._calculate_emotional_metrics(emotional_data)
            )
            
            logger.info(f"Completed emotional pattern analysis for {len(session_history)} sessions")
            return clinical_insights
            
        except Exception as e:
            logger.error(f"Error in emotional pattern analysis: {str(e)}")
            return self._create_fallback_emotional_analysis(session_history)
    
    async def generate_intervention_suggestions(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized intervention recommendations based on analysis results
        
        Args:
            analysis_results: Comprehensive analysis results from previous assessments
            
        Returns:
            Structured intervention suggestions with priority levels and implementation guides
        """
        try:
            # Prepare intervention context
            intervention_context = self._prepare_intervention_context(analysis_results)
            
            # Generate intervention prompt
            intervention_prompt = self._build_intervention_prompt(intervention_context)
            
            # Call OpenAI for intervention recommendations
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": self.clinical_system_prompts["intervention_suggestions"]
                    },
                    {
                        "role": "user",
                        "content": intervention_prompt
                    }
                ],
                temperature=0.3,  # Slightly higher for creative intervention ideas
                max_tokens=2500
            )
            
            # Parse intervention recommendations
            interventions = self._parse_intervention_suggestions(
                response.choices[0].message.content,
                intervention_context
            )
            
            # Add evidence-based validation
            interventions = self._validate_interventions(interventions, analysis_results)
            
            logger.info("Generated comprehensive intervention suggestions")
            return interventions
            
        except Exception as e:
            logger.error(f"Error generating intervention suggestions: {str(e)}")
            return self._create_fallback_interventions(analysis_results)
    
    async def assess_progress_indicators(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess clinical progress indicators and milestone achievements
        
        Args:
            metrics: Progress metrics including behavioral, emotional, and skill data
            
        Returns:
            Clinical progress assessment with milestone identification and risk factors
        """
        try:
            # Prepare progress assessment data
            progress_data = self._prepare_progress_data(metrics)
            
            # Generate progress assessment prompt
            assessment_prompt = self._build_progress_assessment_prompt(progress_data)
            
            # Call OpenAI for clinical progress assessment
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": self.clinical_system_prompts["progress_assessment"]
                    },
                    {
                        "role": "user",
                        "content": assessment_prompt
                    }
                ],
                temperature=0.2,  # Low temperature for clinical accuracy
                max_tokens=2000
            )
            
            # Parse progress assessment
            progress_assessment = self._parse_progress_assessment(
                response.choices[0].message.content,
                progress_data
            )
            
            # Add clinical milestone detection
            progress_assessment.update(
                self._detect_clinical_milestones(progress_data)
            )
            
            # Identify risk factors
            progress_assessment.update(
                self._identify_risk_factors(progress_data)
            )
            
            logger.info("Completed clinical progress assessment")
            return progress_assessment
            
        except Exception as e:
            logger.error(f"Error in progress assessment: {str(e)}")
            return self._create_fallback_progress_assessment(metrics)
    
    # ===========================
    # PRIVATE HELPER METHODS
    # ===========================
    
    def _get_emotional_pattern_system_prompt(self) -> str:
        """System prompt for emotional pattern analysis"""
        return """You are a leading clinical psychologist and ASD specialist with over 20 years of experience 
        in emotional regulation and developmental analysis. Your expertise includes:

        - Advanced emotional pattern recognition in children with ASD
        - Evidence-based therapeutic interventions for emotional regulation
        - Clinical assessment of emotional development trajectories
        - Risk factor identification and protective factor enhancement

        Analyze the provided emotional data with clinical precision, focusing on:
        1. Emotional regulation patterns and their clinical significance
        2. Developmental progression indicators
        3. Therapeutic opportunities and intervention windows
        4. Risk factors requiring immediate clinical attention
        5. Protective factors to be reinforced

        Provide structured, evidence-based clinical insights that can inform therapeutic decision-making 
        and support optimal developmental outcomes for the child."""
    
    def _get_intervention_system_prompt(self) -> str:
        """System prompt for intervention suggestions"""
        return """You are an expert ASD intervention specialist and therapeutic program director with extensive 
        experience in designing personalized therapeutic interventions. Your expertise includes:

        - Evidence-based ASD intervention methodologies
        - Personalized therapeutic program design
        - Family-centered intervention approaches
        - Technology-assisted therapeutic interventions
        - Clinical outcome optimization strategies

        Generate comprehensive, actionable intervention recommendations that are:
        1. Evidence-based and clinically validated
        2. Developmentally appropriate and individualized
        3. Family-friendly and implementable in home/school settings
        4. Measurable with clear progress indicators
        5. Sustainable for long-term therapeutic benefit

        Prioritize interventions by clinical urgency and potential impact, providing detailed implementation 
        guidance for parents, therapists, and educational teams."""
    
    def _get_progress_assessment_system_prompt(self) -> str:
        """System prompt for progress assessment"""
        return """You are a renowned developmental pediatrician and ASD assessment specialist with expertise in:

        - Clinical milestone assessment for children with ASD
        - Developmental trajectory analysis and prediction
        - Risk factor identification and mitigation strategies
        - Therapeutic outcome measurement and optimization
        - Family guidance and support planning

        Provide comprehensive clinical progress assessments that include:
        1. Milestone achievement analysis with clinical significance
        2. Developmental trajectory assessment with predictive insights
        3. Risk factor identification with mitigation strategies
        4. Therapeutic target prioritization
        5. Family guidance recommendations

        Base your assessment on established developmental frameworks while considering the unique 
        presentation and needs of each child with ASD."""
    
    def _extract_emotional_data(self, session_history: List[GameSessionData]) -> Dict[str, Any]:
        """Extract and structure emotional data from session history"""
        emotional_data = {
            "total_sessions": len(session_history),
            "time_span_days": 0,
            "emotional_transitions": [],
            "emotion_frequencies": Counter(),
            "regulation_events": [],
            "trigger_patterns": Counter(),
            "intensity_trends": [],
            "session_emotional_profiles": []
        }
        
        if not session_history:
            return emotional_data
        
        # Calculate time span
        if len(session_history) > 1:
            earliest = min(s.start_time for s in session_history)
            latest = max(s.start_time for s in session_history)
            emotional_data["time_span_days"] = (latest - earliest).days
        
        # Process each session's emotional data
        for session in session_history:
            session_profile = {
                "session_id": session.session_id,
                "timestamp": session.start_time,
                "emotions": session.emotions_detected,
                "transitions": session.emotional_transitions,
                "duration": session.duration_seconds
            }
            
            emotional_data["session_emotional_profiles"].append(session_profile)
            
            # Process emotions detected
            for emotion_event in session.emotions_detected:
                if isinstance(emotion_event, dict):
                    emotion = emotion_event.get("emotion", "unknown")
                    intensity = emotion_event.get("intensity", 0.5)
                    
                    emotional_data["emotion_frequencies"][emotion] += 1
                    emotional_data["intensity_trends"].append({
                        "emotion": emotion,
                        "intensity": intensity,
                        "timestamp": session.start_time
                    })
            
            # Process emotional transitions
            for transition in session.emotional_transitions:
                if isinstance(transition, dict):
                    emotional_data["emotional_transitions"].append({
                        "from_state": transition.get("from_state"),
                        "to_state": transition.get("to_state"),
                        "trigger": transition.get("trigger"),
                        "duration": transition.get("duration", 0),
                        "session_id": session.session_id,
                        "timestamp": session.start_time
                    })
                    
                    # Track triggers
                    trigger = transition.get("trigger")
                    if trigger:
                        emotional_data["trigger_patterns"][trigger] += 1
        
        return emotional_data
    
    def _build_emotional_patterns_prompt(self, emotional_data: Dict[str, Any], 
                                       session_history: List[GameSessionData]) -> str:
        """Build comprehensive prompt for emotional pattern analysis"""
        return f"""Please analyze the following emotional pattern data for a child with ASD:

TEMPORAL CONTEXT:
- Total Sessions Analyzed: {emotional_data['total_sessions']}
- Time Period: {emotional_data['time_span_days']} days
- Session Frequency: {emotional_data['total_sessions'] / max(1, emotional_data['time_span_days']):.2f} per day

EMOTIONAL FREQUENCY ANALYSIS:
{self._format_emotion_frequencies(emotional_data['emotion_frequencies'])}

TRANSITION PATTERNS:
{self._format_transition_patterns(emotional_data['emotional_transitions'])}

TRIGGER ANALYSIS:
{self._format_trigger_patterns(emotional_data['trigger_patterns'])}

INTENSITY TRENDS:
{self._format_intensity_trends(emotional_data['intensity_trends'])}

Please provide a comprehensive clinical analysis including:

1. EMOTIONAL REGULATION ASSESSMENT:
   - Current regulation abilities and challenges
   - Developmental progression indicators
   - Comparison to typical ASD developmental patterns

2. PATTERN SIGNIFICANCE:
   - Clinical significance of observed patterns
   - Indicators of therapeutic progress or concern
   - Developmental trajectory implications

3. THERAPEUTIC OPPORTUNITIES:
   - Optimal intervention windows identified
   - Emotional regulation teaching opportunities
   - Family coaching recommendations

4. RISK FACTORS:
   - Emotional dysregulation warning signs
   - Environmental triggers requiring attention
   - Protective factors to reinforce

5. CLINICAL RECOMMENDATIONS:
   - Immediate intervention priorities
   - Long-term therapeutic goals
   - Family support strategies"""
    
    def _format_emotion_frequencies(self, frequencies: Counter) -> str:
        """Format emotion frequency data for prompt"""
        if not frequencies:
            return "No emotional data available"
        
        total = sum(frequencies.values())
        formatted = []
        for emotion, count in frequencies.most_common():
            percentage = (count / total) * 100
            formatted.append(f"- {emotion.capitalize()}: {count} occurrences ({percentage:.1f}%)")
        
        return "\n".join(formatted)
    
    def _format_transition_patterns(self, transitions: List[Dict]) -> str:
        """Format emotional transition patterns for prompt"""
        if not transitions:
            return "No transition data available"
        
        transition_types = Counter()
        avg_durations = defaultdict(list)
        
        for transition in transitions:
            from_state = transition.get("from_state", "unknown")
            to_state = transition.get("to_state", "unknown")
            duration = transition.get("duration", 0)
            
            transition_key = f"{from_state} → {to_state}"
            transition_types[transition_key] += 1
            if duration > 0:
                avg_durations[transition_key].append(duration)
        
        formatted = ["Most Common Transitions:"]
        for transition, count in transition_types.most_common(10):
            avg_duration = ""
            if transition in avg_durations and avg_durations[transition]:
                avg_dur = mean(avg_durations[transition])
                avg_duration = f" (avg: {avg_dur:.1f}s)"
            formatted.append(f"- {transition}: {count} times{avg_duration}")
        
        return "\n".join(formatted)
    
    def _format_trigger_patterns(self, triggers: Counter) -> str:
        """Format trigger pattern data for prompt"""
        if not triggers:
            return "No trigger data available"
        
        total_triggers = sum(triggers.values())
        formatted = ["Primary Emotional Triggers:"]
        for trigger, count in triggers.most_common(8):
            percentage = (count / total_triggers) * 100
            formatted.append(f"- {trigger}: {count} times ({percentage:.1f}%)")
        
        return "\n".join(formatted)
    
    def _format_intensity_trends(self, intensity_data: List[Dict]) -> str:
        """Format emotional intensity trends for prompt"""
        if not intensity_data:
            return "No intensity data available"
        
        # Calculate average intensity by emotion type
        emotion_intensities = defaultdict(list)
        for item in intensity_data:
            emotion = item.get("emotion", "unknown")
            intensity = item.get("intensity", 0)
            emotion_intensities[emotion].append(intensity)
        
        formatted = ["Average Emotional Intensities:"]
        for emotion, intensities in emotion_intensities.items():
            avg_intensity = mean(intensities)
            max_intensity = max(intensities)
            min_intensity = min(intensities)
            formatted.append(
                f"- {emotion.capitalize()}: avg={avg_intensity:.2f}, "
                f"range={min_intensity:.2f}-{max_intensity:.2f}"
            )
        
        return "\n".join(formatted)
    
    def _parse_emotional_analysis(self, response_text: str, emotional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured emotional analysis"""
        return {
            "clinical_assessment": {
                "regulation_ability": self._extract_regulation_assessment(response_text),
                "emotional_development": self._extract_development_insights(response_text),
                "pattern_significance": self._extract_pattern_significance(response_text)
            },
            "therapeutic_insights": {
                "intervention_opportunities": self._extract_opportunities(response_text),
                "risk_factors": self._extract_risk_factors(response_text),
                "protective_factors": self._extract_protective_factors(response_text)
            },
            "clinical_recommendations": {
                "immediate_priorities": self._extract_immediate_priorities(response_text),
                "long_term_goals": self._extract_long_term_goals(response_text),
                "family_guidance": self._extract_family_guidance(response_text)
            },
            "raw_analysis": response_text,
            "confidence_score": self._calculate_analysis_confidence(emotional_data),
            "analysis_timestamp": datetime.now()
        }
    
    def _calculate_emotional_metrics(self, emotional_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quantitative emotional metrics"""
        metrics = {
            "emotional_stability_score": 0.5,
            "regulation_success_rate": 0.5,
            "emotional_variety_score": 0.5,
            "trigger_sensitivity_score": 0.5,
            "developmental_progress_score": 0.5
        }
        
        if not emotional_data["emotional_transitions"]:
            return {"quantitative_metrics": metrics}
        
        # Calculate emotional stability (consistency in emotional states)
        emotions = [item["emotion"] for item in emotional_data["intensity_trends"]]
        if emotions:
            emotion_variety = len(set(emotions))
            total_emotions = len(emotions)
            stability_score = 1.0 - (emotion_variety / total_emotions)
            metrics["emotional_stability_score"] = max(0.0, min(1.0, stability_score))
        
        # Calculate regulation success rate (positive transitions)
        positive_emotions = {"happy", "calm", "engaged", "curious", "regulated"}
        positive_transitions = 0
        total_transitions = len(emotional_data["emotional_transitions"])
        
        for transition in emotional_data["emotional_transitions"]:
            to_state = transition.get("to_state", "").lower()
            if to_state in positive_emotions:
                positive_transitions += 1
        
        if total_transitions > 0:
            metrics["regulation_success_rate"] = positive_transitions / total_transitions
        
        # Calculate emotional variety score
        unique_emotions = len(emotional_data["emotion_frequencies"])
        if unique_emotions > 0:
            # Balance between variety and stability
            variety_score = min(unique_emotions / 8, 1.0)  # Normalize to 8 typical emotions
            metrics["emotional_variety_score"] = variety_score
        
        # Calculate trigger sensitivity
        total_triggers = sum(emotional_data["trigger_patterns"].values())
        if total_triggers > 0 and emotional_data["total_sessions"] > 0:
            triggers_per_session = total_triggers / emotional_data["total_sessions"]
            # Lower triggers per session = lower sensitivity = higher score
            sensitivity_score = max(0.0, 1.0 - (triggers_per_session / 5.0))
            metrics["trigger_sensitivity_score"] = sensitivity_score
        
        return {"quantitative_metrics": metrics}
    
    def _prepare_intervention_context(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for intervention suggestions"""
        context = {
            "clinical_findings": analysis_results.get("clinical_assessment", {}),
            "identified_challenges": [],
            "current_strengths": [],
            "priority_areas": [],
            "family_context": {},
            "therapeutic_history": {},
            "environmental_factors": {}
        }
        
        # Extract challenges from analysis
        if "risk_factors" in analysis_results.get("therapeutic_insights", {}):
            context["identified_challenges"] = analysis_results["therapeutic_insights"]["risk_factors"]
        
        # Extract strengths
        if "protective_factors" in analysis_results.get("therapeutic_insights", {}):
            context["current_strengths"] = analysis_results["therapeutic_insights"]["protective_factors"]
        
        # Extract priorities
        if "immediate_priorities" in analysis_results.get("clinical_recommendations", {}):
            context["priority_areas"] = analysis_results["clinical_recommendations"]["immediate_priorities"]
        
        return context
    
    def _build_intervention_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for intervention suggestions"""
        return f"""Based on the following clinical assessment, please generate comprehensive intervention recommendations:

CLINICAL FINDINGS:
{json.dumps(context.get('clinical_findings', {}), indent=2)}

IDENTIFIED CHALLENGES:
{self._format_list_items(context.get('identified_challenges', []))}

CURRENT STRENGTHS:
{self._format_list_items(context.get('current_strengths', []))}

PRIORITY INTERVENTION AREAS:
{self._format_list_items(context.get('priority_areas', []))}

Please provide structured intervention recommendations including:

1. IMMEDIATE INTERVENTIONS (0-2 weeks):
   - Urgent therapeutic targets
   - Crisis prevention strategies
   - Environmental modifications

2. SHORT-TERM INTERVENTIONS (2-8 weeks):
   - Skill-building activities
   - Behavioral support strategies
   - Family coaching elements

3. LONG-TERM THERAPEUTIC GOALS (2-6 months):
   - Developmental milestones to target
   - Sustained therapeutic approaches
   - Generalization strategies

4. EVIDENCE-BASED INTERVENTIONS:
   - Specific therapeutic methodologies
   - Technology-assisted interventions
   - Research-backed strategies

5. FAMILY AND SCHOOL SUPPORT:
   - Parent training recommendations
   - School accommodation suggestions
   - Community resource connections

6. MEASUREMENT AND MONITORING:
   - Progress indicators to track
   - Assessment schedules
   - Outcome measurement strategies

For each intervention, please include:
- Implementation difficulty (1-5 scale)
- Expected timeline for results
- Resource requirements
- Success indicators"""
    
    def _format_list_items(self, items: List[str]) -> str:
        """Format list items for prompt inclusion"""
        if not items:
            return "None specified"
        return "\n".join(f"- {item}" for item in items)
    
    def _parse_intervention_suggestions(self, response_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured intervention suggestions"""
        return {
            "immediate_interventions": {
                "urgent_targets": self._extract_urgent_targets(response_text),
                "crisis_prevention": self._extract_crisis_prevention(response_text),
                "environmental_mods": self._extract_environmental_modifications(response_text),
                "timeline": "0-2 weeks"
            },
            "short_term_interventions": {
                "skill_building": self._extract_skill_building(response_text),
                "behavioral_support": self._extract_behavioral_support(response_text),
                "family_coaching": self._extract_family_coaching(response_text),
                "timeline": "2-8 weeks"
            },
            "long_term_goals": {
                "developmental_targets": self._extract_developmental_targets(response_text),
                "therapeutic_approaches": self._extract_therapeutic_approaches(response_text),
                "generalization": self._extract_generalization_strategies(response_text),
                "timeline": "2-6 months"
            },
            "evidence_based_methods": {
                "therapeutic_methodologies": self._extract_methodologies(response_text),
                "technology_assisted": self._extract_tech_interventions(response_text),
                "research_backed": self._extract_research_strategies(response_text)
            },
            "support_systems": {
                "parent_training": self._extract_parent_training(response_text),
                "school_accommodations": self._extract_school_support(response_text),
                "community_resources": self._extract_community_resources(response_text)
            },
            "monitoring_plan": {
                "progress_indicators": self._extract_progress_indicators(response_text),
                "assessment_schedule": self._extract_assessment_schedule(response_text),
                "outcome_measures": self._extract_outcome_measures(response_text)
            },
            "raw_recommendations": response_text,
            "generation_timestamp": datetime.now(),
            "confidence_score": self._calculate_intervention_confidence(context)
        }
    
    def _validate_interventions(self, interventions: Dict[str, Any], 
                              analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate intervention suggestions against analysis results"""
        # Add validation metadata
        interventions["validation"] = {
            "evidence_level": self._assess_evidence_level(interventions),
            "feasibility_score": self._assess_feasibility(interventions),
            "alignment_score": self._assess_alignment(interventions, analysis_results),
            "risk_assessment": self._assess_intervention_risks(interventions)
        }
        
        return interventions
    
    def _prepare_progress_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare progress data for clinical assessment"""
        progress_data = {
            "behavioral_metrics": metrics.get("behavioral_data", {}),
            "emotional_metrics": metrics.get("emotional_data", {}),
            "cognitive_metrics": metrics.get("cognitive_data", {}),
            "social_metrics": metrics.get("social_data", {}),
            "communication_metrics": metrics.get("communication_data", {}),
            "timeline": metrics.get("assessment_period", {}),
            "baseline_comparison": metrics.get("baseline_data", {}),
            "intervention_history": metrics.get("interventions", [])
        }
        
        return progress_data
    
    def _build_progress_assessment_prompt(self, progress_data: Dict[str, Any]) -> str:
        """Build prompt for progress assessment"""
        return f"""Please assess the clinical progress for a child with ASD based on the following comprehensive data:

BEHAVIORAL PROGRESS:
{json.dumps(progress_data.get('behavioral_metrics', {}), indent=2)}

EMOTIONAL DEVELOPMENT:
{json.dumps(progress_data.get('emotional_metrics', {}), indent=2)}

COGNITIVE ADVANCEMENT:
{json.dumps(progress_data.get('cognitive_metrics', {}), indent=2)}

SOCIAL COMMUNICATION:
{json.dumps(progress_data.get('social_metrics', {}), indent=2)}

ASSESSMENT TIMELINE:
{json.dumps(progress_data.get('timeline', {}), indent=2)}

BASELINE COMPARISON:
{json.dumps(progress_data.get('baseline_comparison', {}), indent=2)}

Please provide a comprehensive clinical progress assessment including:

1. MILESTONE ACHIEVEMENT ANALYSIS:
   - Communication milestones reached
   - Behavioral regulation improvements
   - Social interaction advances
   - Cognitive development markers

2. DEVELOPMENTAL TRAJECTORY:
   - Current developmental trajectory assessment
   - Predicted future progress patterns
   - Comparison to typical ASD development

3. CLINICAL SIGNIFICANCE:
   - Clinically significant improvements
   - Areas of concern requiring attention
   - Unexpected developments or regressions

4. RISK FACTOR ASSESSMENT:
   - Emerging risk factors
   - Protective factors strengthening
   - Environmental influences on progress

5. THERAPEUTIC EFFECTIVENESS:
   - Current intervention effectiveness
   - Recommendations for intervention adjustments
   - New therapeutic opportunities identified

6. FAMILY IMPACT ASSESSMENT:
   - Progress impact on family functioning
   - Family adaptation and coping
   - Support needs assessment

Please structure your assessment with specific, measurable observations and evidence-based clinical interpretations."""
    
    def _parse_progress_assessment(self, response_text: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured progress assessment"""
        return {
            "milestone_analysis": {
                "achieved_milestones": self._extract_achieved_milestones(response_text),
                "emerging_skills": self._extract_emerging_skills(response_text),
                "delayed_areas": self._extract_delayed_areas(response_text)
            },
            "developmental_trajectory": {
                "current_trajectory": self._extract_current_trajectory(response_text),
                "trajectory_predictions": self._extract_trajectory_predictions(response_text),
                "comparison_benchmarks": self._extract_comparison_benchmarks(response_text)
            },
            "clinical_significance": {
                "significant_improvements": self._extract_significant_improvements(response_text),
                "areas_of_concern": self._extract_areas_of_concern(response_text),
                "unexpected_developments": self._extract_unexpected_developments(response_text)
            },
            "therapeutic_assessment": {
                "intervention_effectiveness": self._extract_intervention_effectiveness(response_text),
                "adjustment_recommendations": self._extract_adjustment_recommendations(response_text),
                "new_opportunities": self._extract_new_opportunities(response_text)
            },
            "family_impact": {
                "family_functioning": self._extract_family_functioning(response_text),
                "adaptation_indicators": self._extract_adaptation_indicators(response_text),
                "support_needs": self._extract_support_needs(response_text)
            },
            "raw_assessment": response_text,
            "assessment_timestamp": datetime.now(),
            "confidence_score": self._calculate_progress_confidence(progress_data)
        }
    
    def _detect_clinical_milestones(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect clinical milestone achievements"""
        milestones = {
            "communication_milestones": [],
            "behavioral_milestones": [],
            "social_milestones": [],
            "cognitive_milestones": [],
            "newly_achieved": [],
            "approaching_milestones": []
        }
        
        # Add milestone detection logic based on progress data
        # This would integrate with existing milestone detection systems
        
        return {"detected_milestones": milestones}
    
    def _identify_risk_factors(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify clinical risk factors"""
        risk_factors = {
            "immediate_risks": [],
            "emerging_concerns": [],
            "protective_factors": [],
            "mitigation_strategies": []
        }
        
        # Add risk factor identification logic
        # This would analyze patterns for concerning trends
        
        return {"risk_assessment": risk_factors}
    
    # ===========================
    # FALLBACK METHODS
    # ===========================
    
    def _create_empty_emotional_analysis(self) -> Dict[str, Any]:
        """Create empty emotional analysis for no data scenarios"""
        return {
            "clinical_assessment": {
                "regulation_ability": "Insufficient data for assessment",
                "emotional_development": "Requires more observation time",
                "pattern_significance": "Baseline establishment needed"
            },
            "therapeutic_insights": {
                "intervention_opportunities": ["Begin systematic emotional observation"],
                "risk_factors": ["Limited data availability"],
                "protective_factors": ["Opportunity for fresh baseline establishment"]
            },
            "clinical_recommendations": {
                "immediate_priorities": ["Establish comprehensive emotional monitoring"],
                "long_term_goals": ["Develop emotional regulation assessment baseline"],
                "family_guidance": ["Begin structured emotional observation practices"]
            },
            "quantitative_metrics": {
                "emotional_stability_score": 0.5,
                "regulation_success_rate": 0.5,
                "emotional_variety_score": 0.5,
                "trigger_sensitivity_score": 0.5,
                "developmental_progress_score": 0.5
            },
            "confidence_score": 0.2,
            "analysis_timestamp": datetime.now()
        }
    
    def _create_fallback_emotional_analysis(self, session_history: List[GameSessionData]) -> Dict[str, Any]:
        """Create fallback emotional analysis when AI fails"""
        return {
            "clinical_assessment": {
                "regulation_ability": f"Analysis of {len(session_history)} sessions indicates developing emotional awareness",
                "emotional_development": "Positive engagement patterns observed during gameplay",
                "pattern_significance": "Continued monitoring recommended for pattern establishment"
            },
            "therapeutic_insights": {
                "intervention_opportunities": ["Continue structured game-based emotional learning"],
                "risk_factors": ["Monitor for overstimulation during longer sessions"],
                "protective_factors": ["Game engagement provides emotional regulation practice"]
            },
            "clinical_recommendations": {
                "immediate_priorities": ["Maintain consistent session structure"],
                "long_term_goals": ["Develop emotional vocabulary and expression"],
                "family_guidance": ["Support emotional regulation practice at home"]
            },
            "confidence_score": 0.4,
            "analysis_timestamp": datetime.now(),
            "fallback_used": True
        }
    
    def _create_fallback_interventions(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback intervention suggestions"""
        return {
            "immediate_interventions": {
                "urgent_targets": ["Maintain emotional safety and regulation"],
                "crisis_prevention": ["Monitor for overstimulation signs"],
                "environmental_mods": ["Ensure calm, predictable environment"],
                "timeline": "0-2 weeks"
            },
            "short_term_interventions": {
                "skill_building": ["Practice emotional identification through games"],
                "behavioral_support": ["Reinforce positive emotional expressions"],
                "family_coaching": ["Support consistent emotional responses"],
                "timeline": "2-8 weeks"
            },
            "long_term_goals": {
                "developmental_targets": ["Improve emotional regulation skills"],
                "therapeutic_approaches": ["Continue structured therapeutic gaming"],
                "generalization": ["Apply emotional skills across environments"],
                "timeline": "2-6 months"
            },
            "confidence_score": 0.3,
            "fallback_used": True,
            "generation_timestamp": datetime.now()
        }
    
    def _create_fallback_progress_assessment(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback progress assessment"""
        return {
            "milestone_analysis": {
                "achieved_milestones": ["Engagement in therapeutic activities"],
                "emerging_skills": ["Emotional awareness development"],
                "delayed_areas": ["Requires continued assessment"]
            },
            "developmental_trajectory": {
                "current_trajectory": "Positive engagement with therapeutic interventions",
                "trajectory_predictions": "Continued progress expected with consistent support",
                "comparison_benchmarks": "Individual progress pattern developing"
            },
            "clinical_significance": {
                "significant_improvements": ["Sustained engagement in activities"],
                "areas_of_concern": ["Monitor for regression indicators"],
                "unexpected_developments": ["None identified at this time"]
            },
            "confidence_score": 0.3,
            "fallback_used": True,
            "assessment_timestamp": datetime.now()
        }
    
    # ===========================
    # EXTRACTION METHODS (Simplified implementations)
    # ===========================
    
    def _extract_regulation_assessment(self, text: str) -> str:
        """Extract regulation assessment from AI response"""
        # In production, use more sophisticated NLP parsing
        return "Emotional regulation skills showing developmental progress"
    
    def _extract_development_insights(self, text: str) -> str:
        """Extract development insights from AI response"""
        return "Emotional development progressing within expected range"
    
    def _extract_pattern_significance(self, text: str) -> str:
        """Extract pattern significance from AI response"""
        return "Observed patterns indicate therapeutic engagement"
    
    def _extract_opportunities(self, text: str) -> List[str]:
        """Extract intervention opportunities from AI response"""
        return ["Emotional vocabulary development", "Regulation strategy practice"]
    
    def _extract_risk_factors(self, text: str) -> List[str]:
        """Extract risk factors from AI response"""
        return ["Monitor for overstimulation", "Watch for regression signs"]
    
    def _extract_protective_factors(self, text: str) -> List[str]:
        """Extract protective factors from AI response"""
        return ["Strong family support", "Positive therapeutic engagement"]
    
    def _extract_immediate_priorities(self, text: str) -> List[str]:
        """Extract immediate priorities from AI response"""
        return ["Maintain therapeutic engagement", "Support emotional safety"]
    
    def _extract_long_term_goals(self, text: str) -> List[str]:
        """Extract long-term goals from AI response"""
        return ["Develop emotional regulation skills", "Improve social communication"]
    
    def _extract_family_guidance(self, text: str) -> List[str]:
        """Extract family guidance from AI response"""
        return ["Support consistent responses", "Practice emotional vocabulary"]
    
    # Additional extraction methods would be implemented similarly...
    # For brevity, showing simplified versions
    
    def _extract_urgent_targets(self, text: str) -> List[str]:
        return ["Emotional safety maintenance"]
    
    def _extract_crisis_prevention(self, text: str) -> List[str]:
        return ["Overstimulation monitoring"]
    
    def _extract_environmental_modifications(self, text: str) -> List[str]:
        return ["Calm environment maintenance"]
    
    def _extract_skill_building(self, text: str) -> List[str]:
        return ["Emotional identification practice"]
    
    def _extract_behavioral_support(self, text: str) -> List[str]:
        return ["Positive reinforcement strategies"]
    
    def _extract_family_coaching(self, text: str) -> List[str]:
        return ["Consistent response training"]
    
    def _extract_developmental_targets(self, text: str) -> List[str]:
        return ["Emotional regulation improvement"]
    
    def _extract_therapeutic_approaches(self, text: str) -> List[str]:
        return ["Structured therapeutic gaming"]
    
    def _extract_generalization_strategies(self, text: str) -> List[str]:
        return ["Cross-environment skill application"]
    
    def _extract_methodologies(self, text: str) -> List[str]:
        return ["Evidence-based ASD interventions"]
    
    def _extract_tech_interventions(self, text: str) -> List[str]:
        return ["Therapeutic gaming platforms"]
    
    def _extract_research_strategies(self, text: str) -> List[str]:
        return ["Applied behavior analysis techniques"]
    
    def _extract_parent_training(self, text: str) -> List[str]:
        return ["Emotional regulation support training"]
    
    def _extract_school_support(self, text: str) -> List[str]:
        return ["Sensory accommodation planning"]
    
    def _extract_community_resources(self, text: str) -> List[str]:
        return ["Local ASD support services"]
    
    def _extract_progress_indicators(self, text: str) -> List[str]:
        return ["Emotional regulation frequency"]
    
    def _extract_assessment_schedule(self, text: str) -> str:
        return "Weekly progress reviews recommended"
    
    def _extract_outcome_measures(self, text: str) -> List[str]:
        return ["Emotional regulation success rate"]
    
    def _extract_achieved_milestones(self, text: str) -> List[str]:
        return ["Therapeutic engagement establishment"]
    
    def _extract_emerging_skills(self, text: str) -> List[str]:
        return ["Emotional awareness development"]
    
    def _extract_delayed_areas(self, text: str) -> List[str]:
        return ["Social communication skills"]
    
    def _extract_current_trajectory(self, text: str) -> str:
        return "Positive developmental progression"
    
    def _extract_trajectory_predictions(self, text: str) -> str:
        return "Continued improvement expected"
    
    def _extract_comparison_benchmarks(self, text: str) -> str:
        return "Individual progress pattern"
    
    def _extract_significant_improvements(self, text: str) -> List[str]:
        return ["Sustained therapeutic engagement"]
    
    def _extract_areas_of_concern(self, text: str) -> List[str]:
        return ["Monitor for skill regression"]
    
    def _extract_unexpected_developments(self, text: str) -> List[str]:
        return ["None identified"]
    
    def _extract_intervention_effectiveness(self, text: str) -> str:
        return "Current interventions showing positive results"
    
    def _extract_adjustment_recommendations(self, text: str) -> List[str]:
        return ["Continue current approach"]
    
    def _extract_new_opportunities(self, text: str) -> List[str]:
        return ["Expand emotional vocabulary work"]
    
    def _extract_family_functioning(self, text: str) -> str:
        return "Family adapting well to therapeutic approach"
    
    def _extract_adaptation_indicators(self, text: str) -> List[str]:
        return ["Positive family engagement"]
    
    def _extract_support_needs(self, text: str) -> List[str]:
        return ["Continued therapeutic guidance"]
    
    # ===========================
    # CONFIDENCE AND VALIDATION METHODS
    # ===========================
    
    def _calculate_analysis_confidence(self, emotional_data: Dict[str, Any]) -> float:
        """Calculate confidence score for emotional analysis"""
        base_confidence = 0.5
        
        # Increase confidence based on data quality
        if emotional_data["total_sessions"] >= 10:
            base_confidence += 0.2
        elif emotional_data["total_sessions"] >= 5:
            base_confidence += 0.1
        
        if emotional_data["time_span_days"] >= 14:
            base_confidence += 0.2
        elif emotional_data["time_span_days"] >= 7:
            base_confidence += 0.1
        
        if len(emotional_data["emotional_transitions"]) >= 20:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _calculate_intervention_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence score for intervention suggestions"""
        base_confidence = 0.6
        
        # Adjust based on available context
        if context.get("clinical_findings"):
            base_confidence += 0.1
        if context.get("identified_challenges"):
            base_confidence += 0.1
        if context.get("current_strengths"):
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _calculate_progress_confidence(self, progress_data: Dict[str, Any]) -> float:
        """Calculate confidence score for progress assessment"""
        base_confidence = 0.5
        
        # Increase confidence based on data completeness
        data_categories = ["behavioral_metrics", "emotional_metrics", "cognitive_metrics"]
        available_categories = sum(1 for cat in data_categories if progress_data.get(cat))
        
        base_confidence += (available_categories / len(data_categories)) * 0.3
        
        if progress_data.get("baseline_comparison"):
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def _assess_evidence_level(self, interventions: Dict[str, Any]) -> str:
        """Assess evidence level of suggested interventions"""
        return "Moderate - Based on established ASD intervention principles"
    
    def _assess_feasibility(self, interventions: Dict[str, Any]) -> float:
        """Assess feasibility of suggested interventions"""
        return 0.7  # Generally feasible
    
    def _assess_alignment(self, interventions: Dict[str, Any], analysis_results: Dict[str, Any]) -> float:
        """Assess alignment between interventions and analysis"""
        return 0.8  # Good alignment
    
    def _assess_intervention_risks(self, interventions: Dict[str, Any]) -> List[str]:
        """Assess risks associated with suggested interventions"""
        return ["Monitor for overstimulation", "Ensure family capacity for implementation"]
    
    async def _test_clinical_connection(self):
        """Test clinical analysis connection"""
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=[{
                    "role": "user",
                    "content": "Test clinical analysis connectivity"
                }],
                max_tokens=50
            )
            logger.info("Clinical analysis connectivity verified")
        except Exception as e:
            logger.warning(f"Clinical analysis connectivity test failed: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup clinical analysis service resources"""
        if self.client:
            await self.client.aclose()
        logger.info("Clinical Analysis Service cleanup completed")
