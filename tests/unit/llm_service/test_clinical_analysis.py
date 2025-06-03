"""
Unit tests for ClinicalAnalysisService
Tests the advanced clinical analysis functionality for ASD therapeutic insights
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the clinical analysis service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'microservices', 'LLM-Service', 'src'))

from services.clinical_analysis import ClinicalAnalysisService
from models.llm_models import GameSessionData


@pytest.fixture
def clinical_service():
    """Create a ClinicalAnalysisService instance for testing"""
    service = ClinicalAnalysisService()
    return service


@pytest.fixture
def sample_session_data():
    """Create sample game session data for testing"""
    return [
        GameSessionData(
            session_id="test_session_1",
            child_id=123,
            timestamp=datetime.now() - timedelta(days=1),
            game_type="emotional_regulation",
            duration_minutes=15,
            emotions_data=[
                {"emotion": "happy", "intensity": 0.8, "timestamp": datetime.now() - timedelta(days=1)},
                {"emotion": "frustrated", "intensity": 0.6, "timestamp": datetime.now() - timedelta(days=1)},
                {"emotion": "calm", "intensity": 0.9, "timestamp": datetime.now() - timedelta(days=1)}
            ],
            interactions_data=[
                {"interaction_type": "touch", "success": True, "timestamp": datetime.now() - timedelta(days=1)}
            ],
            performance_metrics={
                "completion_rate": 0.85,
                "accuracy": 0.78,
                "response_time": 2.5
            }
        ),
        GameSessionData(
            session_id="test_session_2", 
            child_id=123,
            timestamp=datetime.now(),
            game_type="social_interaction",
            duration_minutes=20,
            emotions_data=[
                {"emotion": "engaged", "intensity": 0.7, "timestamp": datetime.now()},
                {"emotion": "anxious", "intensity": 0.4, "timestamp": datetime.now()},
                {"emotion": "regulated", "intensity": 0.8, "timestamp": datetime.now()}
            ],
            interactions_data=[
                {"interaction_type": "verbal", "success": True, "timestamp": datetime.now()}
            ],
            performance_metrics={
                "completion_rate": 0.92,
                "accuracy": 0.83,
                "response_time": 2.1
            }
        )
    ]


@pytest.fixture
def sample_analysis_results():
    """Create sample analysis results for intervention testing"""
    return {
        "emotional_regulation_assessment": {
            "current_abilities": "Developing emotional awareness with support",
            "challenges_identified": ["transition difficulties", "sensory overwhelm"]
        },
        "therapeutic_opportunities": [
            "Emotional regulation skill building",
            "Sensory integration support"
        ],
        "risk_factors": [
            "Increased anxiety during transitions"
        ],
        "quantitative_metrics": {
            "emotional_stability_score": 0.65,
            "regulation_success_rate": 0.72,
            "trigger_sensitivity_score": 0.58
        }
    }


@pytest.fixture 
def sample_progress_metrics():
    """Create sample progress metrics for assessment testing"""
    return {
        "emotional_stability_score": 0.75,
        "regulation_success_rate": 0.82,
        "communication_improvement": 0.68,
        "social_engagement_level": 0.71,
        "adaptive_behavior_score": 0.79
    }


class TestClinicalAnalysisService:
    """Test suite for ClinicalAnalysisService"""

    def test_initialization(self, clinical_service):
        """Test service initialization"""
        assert clinical_service is not None
        assert hasattr(clinical_service, 'client')
        assert hasattr(clinical_service, 'settings')
        assert hasattr(clinical_service, 'clinical_system_prompts')

    @pytest.mark.asyncio
    async def test_initialization_async(self, clinical_service):
        """Test async initialization"""
        # Mock the OpenAI client initialization
        with patch.object(clinical_service, 'client') as mock_client:
            await clinical_service.initialize()
            # Should complete without errors
            assert True

    def test_extract_emotional_data(self, clinical_service, sample_session_data):
        """Test emotional data extraction from session history"""
        emotional_data = clinical_service._extract_emotional_data(sample_session_data)
        
        # Check basic structure
        assert isinstance(emotional_data, dict)
        assert "total_sessions" in emotional_data
        assert "emotion_frequencies" in emotional_data
        assert "emotional_transitions" in emotional_data
        assert "trigger_patterns" in emotional_data
        assert "intensity_trends" in emotional_data
        
        # Check values
        assert emotional_data["total_sessions"] == 2
        assert len(emotional_data["emotion_frequencies"]) > 0
        assert "time_span_days" in emotional_data

    def test_calculate_emotional_metrics(self, clinical_service, sample_session_data):
        """Test quantitative emotional metrics calculation"""
        emotional_data = clinical_service._extract_emotional_data(sample_session_data)
        metrics = clinical_service._calculate_emotional_metrics(emotional_data)
        
        # Check metrics structure
        assert isinstance(metrics, dict)
        assert "quantitative_metrics" in metrics
        
        quant_metrics = metrics["quantitative_metrics"]
        assert "emotional_stability_score" in quant_metrics
        assert "regulation_success_rate" in quant_metrics
        assert "emotional_variety_score" in quant_metrics
        assert "trigger_sensitivity_score" in quant_metrics
        
        # Check value ranges (0.0 to 1.0)
        for metric_name, value in quant_metrics.items():
            assert 0.0 <= value <= 1.0, f"{metric_name} should be between 0.0 and 1.0"

    @pytest.mark.asyncio
    async def test_analyze_emotional_patterns_fallback(self, clinical_service, sample_session_data):
        """Test emotional patterns analysis with fallback"""
        # Mock OpenAI client to simulate failure
        with patch.object(clinical_service, 'client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
            
            result = await clinical_service.analyze_emotional_patterns(sample_session_data)
            
            # Should return fallback analysis
            assert isinstance(result, dict)
            assert "emotional_regulation_assessment" in result
            assert "fallback_analysis" in result["emotional_regulation_assessment"]

    @pytest.mark.asyncio 
    async def test_generate_intervention_suggestions_fallback(self, clinical_service, sample_analysis_results):
        """Test intervention suggestions with fallback"""
        # Mock OpenAI client to simulate failure
        with patch.object(clinical_service, 'client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
            
            result = await clinical_service.generate_intervention_suggestions(sample_analysis_results)
            
            # Should return fallback interventions
            assert isinstance(result, dict)
            assert "immediate_interventions" in result
            assert "fallback_mode" in result

    @pytest.mark.asyncio
    async def test_assess_progress_indicators_fallback(self, clinical_service, sample_progress_metrics):
        """Test progress indicators assessment with fallback"""
        # Mock OpenAI client to simulate failure
        with patch.object(clinical_service, 'client') as mock_client:
            mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
            
            result = await clinical_service.assess_progress_indicators(sample_progress_metrics)
            
            # Should return fallback assessment
            assert isinstance(result, dict)
            assert "milestone_achievements" in result
            assert "fallback_assessment" in result

    def test_empty_session_history(self, clinical_service):
        """Test handling of empty session history"""
        empty_analysis = clinical_service._create_empty_emotional_analysis()
        
        assert isinstance(empty_analysis, dict)
        assert "emotional_regulation_assessment" in empty_analysis
        assert "no_data_available" in empty_analysis["emotional_regulation_assessment"]

    def test_prepare_intervention_context(self, clinical_service, sample_analysis_results):
        """Test intervention context preparation"""
        context = clinical_service._prepare_intervention_context(sample_analysis_results)
        
        assert isinstance(context, dict)
        assert "primary_concerns" in context
        assert "current_strengths" in context
        assert "intervention_targets" in context
        assert "risk_level" in context

    def test_system_prompts_exist(self, clinical_service):
        """Test that all required system prompts are defined"""
        prompts = clinical_service.clinical_system_prompts
        
        assert "emotional_patterns" in prompts
        assert "intervention_suggestions" in prompts
        assert "progress_assessment" in prompts
        
        # Check prompts are not empty
        for prompt_name, prompt_text in prompts.items():
            assert len(prompt_text) > 100, f"{prompt_name} prompt should be substantial"
            assert "clinical" in prompt_text.lower() or "therapeutic" in prompt_text.lower()

    def test_format_helpers(self, clinical_service):
        """Test formatting helper methods"""
        from collections import Counter
        
        # Test emotion frequency formatting
        frequencies = Counter({"happy": 5, "calm": 3, "frustrated": 2})
        formatted = clinical_service._format_emotion_frequencies(frequencies)
        assert isinstance(formatted, str)
        assert "happy" in formatted
        assert "5" in formatted
        
        # Test transition pattern formatting
        transitions = [
            {"from_state": "anxious", "to_state": "calm", "duration": 120},
            {"from_state": "frustrated", "to_state": "regulated", "duration": 180}
        ]
        formatted = clinical_service._format_transition_patterns(transitions)
        assert isinstance(formatted, str)
        assert "anxious" in formatted or "calm" in formatted

    @pytest.mark.asyncio
    async def test_error_handling(self, clinical_service):
        """Test error handling in various scenarios"""
        # Test with invalid session data
        invalid_data = [{"invalid": "data"}]
        
        try:
            # This should handle the error gracefully
            result = await clinical_service.analyze_emotional_patterns(invalid_data)
            assert isinstance(result, dict)
        except Exception as e:
            # If it throws, it should be a specific error type
            assert isinstance(e, (ValueError, TypeError))

    def test_clinical_expertise_validation(self, clinical_service):
        """Test that clinical system prompts contain appropriate expertise indicators"""
        emotional_prompt = clinical_service._get_emotional_pattern_system_prompt()
        intervention_prompt = clinical_service._get_intervention_system_prompt()  
        progress_prompt = clinical_service._get_progress_assessment_system_prompt()
        
        # Check for clinical expertise indicators
        clinical_keywords = ["clinical", "therapeutic", "evidence-based", "developmental", "ASD", "intervention"]
        
        for prompt in [emotional_prompt, intervention_prompt, progress_prompt]:
            found_keywords = [keyword for keyword in clinical_keywords if keyword.lower() in prompt.lower()]
            assert len(found_keywords) >= 3, f"Prompt should contain clinical expertise indicators: {found_keywords}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
