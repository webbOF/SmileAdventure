import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from src.models.llm_models import (AnalysisType, BehavioralAnalysis,
                                   EmotionalAnalysis, GameSessionData,
                                   LLMAnalysisResponse, Recommendations)
from src.services.llm_service import LLMService


class TestLLMService:
    """Test cases for LLM Service"""
    
    @pytest.fixture
    def llm_service(self):
        """Create LLM service instance for testing"""
        return LLMService()
    
    @pytest.fixture
    def sample_session_data(self):
        """Create sample session data for testing"""
        return GameSessionData(
            user_id=123,
            session_id="test_session_456",
            child_id=789,
            start_time=datetime.now() - timedelta(minutes=30),
            end_time=datetime.now(),
            duration_seconds=1800,
            emotions_detected=[
                {"emotion": "happy", "intensity": 0.8, "timestamp": "2025-06-01T10:15:00Z"},
                {"emotion": "calm", "intensity": 0.9, "timestamp": "2025-06-01T10:20:00Z"}
            ],
            behavioral_observations=[
                {"behavior": "social_interaction", "intensity": 0.7, "duration": 120},
                {"behavior": "attention_focus", "intensity": 0.8, "duration": 300}
            ],
            progress_metrics={
                "engagement_level": 0.8,
                "task_completion": 0.9,
                "social_interaction": 0.7
            }
        )
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, llm_service):
        """Test service initialization"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            with patch('openai.AsyncOpenAI'):
                with patch.object(llm_service, 'test_openai_connection', new_callable=AsyncMock):
                    await llm_service.initialize()
                    assert llm_service.client is not None
    
    @pytest.mark.asyncio
    async def test_analyze_game_session_success(self, llm_service, sample_session_data):
        """Test successful game session analysis"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Comprehensive analysis: The child showed good engagement..."
        
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            
            result = await llm_service.analyze_game_session(
                session_data=sample_session_data,
                analysis_type=AnalysisType.COMPREHENSIVE
            )
            
            assert isinstance(result, LLMAnalysisResponse)
            assert result.session_id == sample_session_data.session_id
            assert result.child_id == sample_session_data.child_id
            assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_analyze_game_session_fallback(self, llm_service, sample_session_data):
        """Test fallback when OpenAI fails"""
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
            
            result = await llm_service.analyze_game_session(
                session_data=sample_session_data,
                analysis_type=AnalysisType.COMPREHENSIVE
            )
            
            assert isinstance(result, LLMAnalysisResponse)
            assert result.model_used == "fallback"
            assert result.confidence_score == 0.3
    
    @pytest.mark.asyncio
    async def test_emotional_analysis(self, llm_service, sample_session_data):
        """Test emotional pattern analysis"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Emotional analysis: Positive emotional states..."
        
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            
            result = await llm_service.analyze_emotional_patterns(sample_session_data)
            
            assert isinstance(result, EmotionalAnalysis)
            assert len(result.dominant_emotions) > 0
            assert 0 <= result.emotional_stability_score <= 1
    
    @pytest.mark.asyncio
    async def test_behavioral_analysis(self, llm_service, sample_session_data):
        """Test behavioral pattern analysis"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Behavioral analysis: Good social engagement..."
        
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            
            result = await llm_service.analyze_behavioral_patterns(sample_session_data)
            
            assert isinstance(result, BehavioralAnalysis)
            assert 0 <= result.social_engagement_level <= 1
            assert 0 <= result.communication_effectiveness <= 1
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, llm_service, sample_session_data):
        """Test recommendation generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Recommendations: Continue current approach..."
        
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            
            result = await llm_service.generate_recommendations(sample_session_data)
            
            assert isinstance(result, Recommendations)
            assert len(result.immediate_interventions) >= 0
            assert len(result.session_adjustments) >= 0
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, llm_service, sample_session_data):
        """Test caching mechanism"""
        llm_service.settings.ENABLE_CACHING = True
        
        # First call should hit the API
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Analysis result..."
        
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            
            # First call
            result1 = await llm_service.analyze_game_session(
                session_data=sample_session_data,
                analysis_type=AnalysisType.COMPREHENSIVE
            )
            
            # Second call should use cache
            result2 = await llm_service.analyze_game_session(
                session_data=sample_session_data,
                analysis_type=AnalysisType.COMPREHENSIVE
            )
            
            # API should only be called once
            mock_client.chat.completions.create.assert_called_once()
            assert result1.session_id == result2.session_id
    
    def test_cache_key_generation(self, llm_service, sample_session_data):
        """Test cache key generation"""
        key = llm_service._generate_cache_key(sample_session_data, AnalysisType.COMPREHENSIVE)
        expected_key = f"{sample_session_data.session_id}_comprehensive_{sample_session_data.child_id}"
        assert key == expected_key
    
    @pytest.mark.asyncio
    async def test_openai_connectivity_check(self, llm_service):
        """Test OpenAI connectivity check"""
        mock_models = Mock()
        mock_models.data = []
        
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.models.list = AsyncMock(return_value=mock_models)
            
            status = await llm_service.check_openai_connectivity()
            assert status == "connected"
    
    @pytest.mark.asyncio
    async def test_openai_connectivity_failure(self, llm_service):
        """Test OpenAI connectivity failure"""
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.models.list = AsyncMock(side_effect=Exception("Connection failed"))
            
            status = await llm_service.check_openai_connectivity()
            assert status == "disconnected"
    
    @pytest.mark.asyncio
    async def test_get_available_models(self, llm_service):
        """Test getting available models"""
        mock_models = Mock()
        mock_models.data = [
            Mock(id="gpt-4"),
            Mock(id="gpt-3.5-turbo"),
            Mock(id="other-model")
        ]
        
        with patch.object(llm_service, 'client') as mock_client:
            mock_client.models.list = AsyncMock(return_value=mock_models)
            
            models = await llm_service.get_available_models()
            gpt_models = [m for m in models if 'gpt' in m]
            assert len(gpt_models) >= 2
    
    @pytest.mark.asyncio
    async def test_cleanup(self, llm_service):
        """Test service cleanup"""
        mock_client = Mock()
        mock_client.close = AsyncMock()
        llm_service.client = mock_client
        
        await llm_service.cleanup()
        mock_client.close.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
