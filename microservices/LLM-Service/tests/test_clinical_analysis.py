"""
Unit tests for Clinical Analysis Service
Tests the core functionality of the clinical analysis service
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

# Set mock environment
os.environ['OPENAI_API_KEY'] = 'test-key-for-unit-testing'

# Import after setting environment
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.clinical_analysis import ClinicalAnalysisService
from src.models.llm_models import GameSessionData


class TestClinicalAnalysisService:
    """Test suite for Clinical Analysis Service"""
    
    @pytest.fixture
    async def clinical_service(self):
        """Create and initialize clinical analysis service"""
        service = ClinicalAnalysisService()
        await service.initialize()
        return service
    
    @pytest.fixture
    def sample_session_data(self) -> List[GameSessionData]:
        """Create sample session data for testing"""
        sessions = []
        for i in range(5):
            session = GameSessionData(
                user_id=123,
                session_id=f"test-session-{i:03d}",
                child_id=456,
                start_time=datetime.now() - timedelta(days=i, hours=1),
                end_time=datetime.now() - timedelta(days=i),
                duration_seconds=3600,
                emotions_detected=[
                    {
                        "emotion": "happy" if i % 2 == 0 else "frustrated",
                        "intensity": 0.7 + (i * 0.05),
                        "timestamp": datetime.now() - timedelta(days=i, minutes=30),
                        "context": "gameplay"
                    }
                ],
                emotional_transitions=[
                    {
                        "from_state": "neutral",
                        "to_state": "happy" if i % 2 == 0 else "frustrated", 
                        "trigger": "level_completion" if i % 2 == 0 else "difficulty_spike",
                        "duration": 120 + (i * 10),
                        "timestamp": datetime.now() - timedelta(days=i, minutes=30)
                    }
                ]
            )
            sessions.append(session)
        return sessions

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization"""
        service = ClinicalAnalysisService()
        await service.initialize()
        
        assert service.client is not None
        assert service.settings is not None
        assert len(service.clinical_system_prompts) == 3
        assert "emotional_patterns" in service.clinical_system_prompts
        assert "interventions" in service.clinical_system_prompts
        assert "progress_assessment" in service.clinical_system_prompts

    @pytest.mark.asyncio
    async def test_empty_emotional_analysis_fallback(self, clinical_service):
        """Test fallback for empty emotional analysis"""
        result = clinical_service._create_empty_emotional_analysis()
        
        assert isinstance(result, dict)
        assert "analysis_period_days" in result
        assert "total_sessions_analyzed" in result
        assert result["total_sessions_analyzed"] == 0
        assert "confidence_score" in result
        assert result["confidence_score"] == 0.3

    @pytest.mark.asyncio
    async def test_fallback_emotional_analysis(self, clinical_service, sample_session_data):
        """Test fallback emotional analysis with session data"""
        result = clinical_service._create_fallback_emotional_analysis(sample_session_data)
        
        assert isinstance(result, dict)
        assert result["total_sessions_analyzed"] == len(sample_session_data)
        assert "emotional_regulation_assessment" in result
        assert "therapeutic_opportunities" in result
        assert "quantitative_metrics" in result
        assert result["confidence_score"] == 0.4

    @pytest.mark.asyncio
    async def test_extract_emotional_data(self, clinical_service, sample_session_data):
        """Test emotional data extraction from session history"""
        emotional_data = clinical_service._extract_emotional_data(sample_session_data)
        
        assert isinstance(emotional_data, dict)
        assert "total_sessions" in emotional_data
        assert "time_span_days" in emotional_data
        assert "emotion_frequencies" in emotional_data
        assert "emotional_transitions" in emotional_data
        assert "trigger_patterns" in emotional_data
        assert "intensity_trends" in emotional_data
        
        assert emotional_data["total_sessions"] == len(sample_session_data)
        assert len(emotional_data["emotion_frequencies"]) > 0
        assert len(emotional_data["emotional_transitions"]) > 0

    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_analyze_emotional_patterns_success(self, mock_openai, clinical_service, sample_session_data):
        """Test successful emotional pattern analysis"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        EMOTIONAL REGULATION ASSESSMENT:
        - Current regulation level: developing appropriately
        - Regulation consistency: moderate (7/10)
        - Areas of strength: positive transitions during success
        
        PATTERN SIGNIFICANCE:
        - Moderate clinical significance
        - Typical development pattern for age group
        
        THERAPEUTIC OPPORTUNITIES:
        - Implement structured emotional regulation teaching
        - Use success moments to reinforce positive patterns
        
        RISK FACTORS:
        - Frustration responses to difficulty increases
        
        CLINICAL RECOMMENDATIONS:
        - Continue current supportive approach
        - Monitor for pattern changes over time
        """
        
        clinical_service.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await clinical_service.analyze_emotional_patterns(sample_session_data)
        
        assert isinstance(result, dict)
        assert "emotional_regulation_assessment" in result
        assert "therapeutic_opportunities" in result
        assert "risk_factors" in result
        assert "clinical_recommendations" in result
        assert "confidence_score" in result
        assert result["total_sessions_analyzed"] == len(sample_session_data)

    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI') 
    async def test_generate_intervention_suggestions_success(self, mock_openai, clinical_service):
        """Test successful intervention suggestion generation"""
        # Mock analysis results
        analysis_results = {
            "emotional_regulation_assessment": {
                "current_regulation_level": "developing",
                "areas_of_challenge": ["transition_difficulties"]
            },
            "therapeutic_opportunities": [
                "Implement visual schedules for transitions"
            ],
            "risk_factors": ["frustration during changes"],
            "quantitative_metrics": {
                "emotional_stability_score": 0.6,
                "regulation_success_rate": 0.7
            }
        }
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        IMMEDIATE INTERVENTIONS:
        1. Visual Transition Support (Priority: immediate)
           - Create visual schedule cards
           - Practice transitions during calm periods
           - Expected: Reduced transition anxiety
           - Evidence: High effectiveness in ASD research
           - Feasibility: 0.9
        
        SHORT-TERM RECOMMENDATIONS:
        1. Emotional Regulation Skills (Priority: short-term)
           - Teach deep breathing techniques
           - Use emotion identification tools
           - Expected: Improved self-regulation
           - Evidence: Moderate research support
           - Feasibility: 0.8
        
        PARENT COACHING:
        - Model calm responses during child's frustration
        - Provide advance warning for transitions
        
        EFFECTIVENESS PREDICTION: 0.82
        """
        
        clinical_service.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await clinical_service.generate_intervention_suggestions(analysis_results)
        
        assert isinstance(result, dict)
        assert "immediate_interventions" in result
        assert "short_term_recommendations" in result
        assert "parent_coaching_guidance" in result
        assert "overall_effectiveness_prediction" in result
        assert "confidence_score" in result
        
        # Check intervention structure
        if result["immediate_interventions"]:
            intervention = result["immediate_interventions"][0]
            assert "intervention_type" in intervention
            assert "priority_level" in intervention
            assert "feasibility_score" in intervention

    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_assess_progress_indicators_success(self, mock_openai, clinical_service):
        """Test successful progress indicator assessment"""
        # Mock progress metrics
        progress_metrics = {
            "emotional_stability": 0.75,
            "regulation_success_rate": 0.68,
            "milestone_data": {
                "communication_improvement": 0.8,
                "social_engagement": 0.6,
                "emotional_expression": 0.7
            }
        }
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        MILESTONE ACHIEVEMENTS:
        1. Communication Milestone (Type: communication)
           - Description: Improved verbal expression during gameplay
           - Achievement: 0.8 (80% achieved)
           - Evidence: Increased spontaneous communication, clearer requests
        
        2. Emotional Regulation Milestone (Type: emotional_regulation)
           - Description: Uses self-calming strategies
           - Achievement: 0.7 (70% achieved)
           - Evidence: Deep breathing observed, requests breaks when needed
        
        DEVELOPMENTAL TRAJECTORY:
        - Current progress: appropriate for developmental stage
        - Trajectory: positive trend with steady improvement
        - Accelerating areas: communication, emotional awareness
        
        INTERVENTION EFFECTIVENESS:
        - Visual schedules: 0.85 effectiveness
        - Emotional coaching: 0.78 effectiveness
        - Sensory breaks: 0.82 effectiveness
        
        CLINICAL SIGNIFICANCE:
        - Moderate clinical significance
        - Progress consistent with therapeutic goals
        
        RECOMMENDED ADJUSTMENTS:
        - Continue current intervention approaches
        - Gradually increase challenge levels in communication tasks
        """
        
        clinical_service.client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await clinical_service.assess_progress_indicators(progress_metrics)
        
        assert isinstance(result, dict)
        assert "milestone_achievements" in result
        assert "developmental_trajectory" in result
        assert "intervention_effectiveness" in result
        assert "clinical_significance" in result
        assert "recommended_adjustments" in result
        assert "confidence_score" in result
        
        # Check milestone structure
        if result["milestone_achievements"]:
            milestone = result["milestone_achievements"][0]
            assert "milestone_type" in milestone
            assert "description" in milestone
            assert "achievement_level" in milestone

    @pytest.mark.asyncio
    async def test_analyze_emotional_patterns_with_empty_data(self, clinical_service):
        """Test emotional pattern analysis with empty session data"""
        result = await clinical_service.analyze_emotional_patterns([])
        
        assert isinstance(result, dict)
        assert result["total_sessions_analyzed"] == 0
        assert "confidence_score" in result
        assert result["confidence_score"] == 0.3

    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_analyze_emotional_patterns_api_failure(self, mock_openai, clinical_service, sample_session_data):
        """Test emotional pattern analysis when OpenAI API fails"""
        # Mock API failure
        clinical_service.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        result = await clinical_service.analyze_emotional_patterns(sample_session_data)
        
        # Should return fallback result
        assert isinstance(result, dict)
        assert "emotional_regulation_assessment" in result
        assert result["confidence_score"] == 0.4
        assert "fallback" in str(result).lower() or result["total_sessions_analyzed"] == len(sample_session_data)

    def test_quantitative_metrics_calculation(self, clinical_service):
        """Test quantitative metrics calculation"""
        emotional_data = {
            "emotional_transitions": [
                {"from_state": "calm", "to_state": "happy"},
                {"from_state": "happy", "to_state": "frustrated"}, 
                {"from_state": "frustrated", "to_state": "calm"}
            ],
            "emotion_frequencies": {"happy": 5, "calm": 8, "frustrated": 3},
            "trigger_patterns": {"transition": 2, "difficulty": 1},
            "total_sessions": 5,
            "intensity_trends": [
                {"emotion": "happy", "avg_intensity": 0.8},
                {"emotion": "calm", "avg_intensity": 0.7}
            ]
        }
        
        result = clinical_service._calculate_emotional_metrics(emotional_data)
        
        assert "quantitative_metrics" in result
        metrics = result["quantitative_metrics"]
        assert "emotional_stability_score" in metrics
        assert "regulation_success_rate" in metrics
        assert "emotional_variety_score" in metrics
        assert "trigger_sensitivity_score" in metrics
        
        # Check value ranges
        for metric_name, value in metrics.items():
            assert 0.0 <= value <= 1.0, f"{metric_name} should be between 0 and 1"

    def test_prompt_formatting_methods(self, clinical_service):
        """Test prompt formatting helper methods"""
        from collections import Counter
        
        # Test emotion frequency formatting
        frequencies = Counter({"happy": 5, "calm": 3, "frustrated": 2})
        formatted = clinical_service._format_emotion_frequencies(frequencies)
        assert "happy" in formatted
        assert "5" in formatted
        
        # Test transition pattern formatting
        transitions = [
            {"from_state": "calm", "to_state": "happy", "trigger": "success"},
            {"from_state": "happy", "to_state": "frustrated", "trigger": "difficulty"}
        ]
        formatted = clinical_service._format_transition_patterns(transitions)
        assert "calm" in formatted
        assert "happy" in formatted
        
        # Test trigger pattern formatting
        triggers = Counter({"difficulty": 3, "transition": 2})
        formatted = clinical_service._format_trigger_patterns(triggers)
        assert "difficulty" in formatted
        assert "3" in formatted

    def test_intervention_context_preparation(self, clinical_service):
        """Test intervention context preparation"""
        analysis_results = {
            "emotional_regulation_assessment": {"current_level": "developing"},
            "therapeutic_opportunities": ["visual_schedules"],
            "risk_factors": ["transition_difficulty"],
            "quantitative_metrics": {"stability": 0.7}
        }
        
        context = clinical_service._prepare_intervention_context(analysis_results)
        
        assert isinstance(context, dict)
        assert "regulation_level" in context
        assert "key_opportunities" in context
        assert "primary_risks" in context
        assert "stability_metrics" in context

    @pytest.mark.asyncio
    async def test_service_cleanup(self, clinical_service):
        """Test service cleanup (should not raise errors)"""
        # Cleanup should not raise any exceptions
        try:
            await clinical_service.cleanup()
            success = True
        except Exception:
            success = False
        
        assert success, "Service cleanup should not raise exceptions"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
