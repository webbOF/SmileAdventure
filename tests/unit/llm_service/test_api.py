import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.llm_models import (AnalysisType, GameSessionData,
                                   LLMAnalysisRequest)


class TestLLMAPI:
    """Test cases for LLM Service API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_session_data(self):
        """Create sample session data for API testing"""
        return {
            "user_id": 123,
            "session_id": "api_test_session",
            "child_id": 456,
            "start_time": "2025-06-01T10:00:00Z",
            "end_time": "2025-06-01T10:30:00Z",
            "duration_seconds": 1800,
            "emotions_detected": [
                {"emotion": "happy", "intensity": 0.8, "timestamp": "2025-06-01T10:15:00Z"}
            ],
            "behavioral_observations": [
                {"behavior": "social_interaction", "intensity": 0.7, "duration": 120}
            ],
            "progress_metrics": {
                "engagement_level": 0.8
            }
        }
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        with patch('src.main.llm_service.check_openai_connectivity', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = "connected"
            
            response = client.get("/health")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "timestamp" in data
            assert "openai_status" in data
    
    def test_analyze_session_endpoint(self, client, sample_session_data):
        """Test session analysis endpoint"""
        request_data = {
            "session_data": sample_session_data,
            "analysis_type": "comprehensive",
            "include_recommendations": True
        }
        
        with patch('src.main.llm_service.analyze_game_session', new_callable=AsyncMock) as mock_analyze:
            # Mock the response
            mock_response = Mock()
            mock_response.session_id = sample_session_data["session_id"]
            mock_response.child_id = sample_session_data["child_id"]
            mock_response.analysis_type = AnalysisType.COMPREHENSIVE
            mock_response.confidence_score = 0.8
            mock_response.model_used = "gpt-4"
            mock_response.dict.return_value = {
                "session_id": sample_session_data["session_id"],
                "child_id": sample_session_data["child_id"],
                "analysis_type": "comprehensive",
                "confidence_score": 0.8,
                "model_used": "gpt-4"
            }
            
            mock_analyze.return_value = mock_response
            
            response = client.post("/analyze-session", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["session_id"] == sample_session_data["session_id"]
    
    def test_analyze_emotional_patterns_endpoint(self, client, sample_session_data):
        """Test emotional patterns analysis endpoint"""
        with patch('src.main.llm_service.analyze_emotional_patterns', new_callable=AsyncMock) as mock_analyze:
            mock_response = Mock()
            mock_response.dict.return_value = {
                "dominant_emotions": ["happy", "calm"],
                "emotional_stability_score": 0.8,
                "regulation_success_rate": 0.9
            }
            mock_analyze.return_value = mock_response
            
            response = client.post("/analyze-emotional-patterns", json=sample_session_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "dominant_emotions" in data
    
    def test_analyze_behavioral_patterns_endpoint(self, client, sample_session_data):
        """Test behavioral patterns analysis endpoint"""
        with patch('src.main.llm_service.analyze_behavioral_patterns', new_callable=AsyncMock) as mock_analyze:
            mock_response = Mock()
            mock_response.dict.return_value = {
                "behavioral_patterns_observed": ["social_interaction"],
                "social_engagement_level": 0.7,
                "communication_effectiveness": 0.8
            }
            mock_analyze.return_value = mock_response
            
            response = client.post("/analyze-behavioral-patterns", json=sample_session_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "behavioral_patterns_observed" in data
    
    def test_generate_recommendations_endpoint(self, client, sample_session_data):
        """Test recommendations generation endpoint"""
        with patch('src.main.llm_service.generate_recommendations', new_callable=AsyncMock) as mock_generate:
            mock_response = Mock()
            mock_response.dict.return_value = {
                "immediate_interventions": ["Continue current approach"],
                "session_adjustments": ["Maintain engagement level"],
                "environmental_modifications": ["Ensure calm environment"]
            }
            mock_generate.return_value = mock_response
            
            response = client.post("/generate-recommendations", json=sample_session_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "immediate_interventions" in data
    
    def test_analyze_progress_endpoint(self, client, sample_session_data):
        """Test progress analysis endpoint"""
        session_history = [sample_session_data, sample_session_data]
        request_data = {
            "session_history": session_history,
            "child_id": 456,
            "analysis_timeframe_days": 30
        }
        
        with patch('src.main.llm_service.analyze_progress_trends', new_callable=AsyncMock) as mock_analyze:
            mock_response = Mock()
            mock_response.dict.return_value = {
                "overall_progress_trend": "improving",
                "skill_development_trends": {"communication": "improving"},
                "areas_of_improvement": ["Social interaction"]
            }
            mock_analyze.return_value = mock_response
            
            response = client.post("/analyze-progress", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "overall_progress_trend" in data
    
    def test_get_available_models_endpoint(self, client):
        """Test get available models endpoint"""
        with patch('src.main.llm_service.get_available_models', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = ["gpt-4", "gpt-3.5-turbo"]
            
            response = client.get("/models/available")
            assert response.status_code == 200
            
            data = response.json()
            assert "available_models" in data
            assert len(data["available_models"]) >= 1
    
    def test_test_openai_connection_endpoint(self, client):
        """Test OpenAI connection test endpoint"""
        with patch('src.main.llm_service.test_openai_connection', new_callable=AsyncMock) as mock_test:
            mock_test.return_value = {"status": "success", "model": "gpt-4"}
            
            response = client.post("/test-openai-connection")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
    
    def test_invalid_session_data(self, client):
        """Test with invalid session data"""
        invalid_data = {
            "session_data": {
                "invalid_field": "test"
            },
            "analysis_type": "comprehensive"
        }
        
        response = client.post("/analyze-session", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_server_error_handling(self, client, sample_session_data):
        """Test server error handling"""
        request_data = {
            "session_data": sample_session_data,
            "analysis_type": "comprehensive"
        }
        
        with patch('src.main.llm_service.analyze_game_session', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.side_effect = Exception("Internal server error")
            
            response = client.post("/analyze-session", json=request_data)
            assert response.status_code == 500
            
            data = response.json()
            assert "detail" in data

if __name__ == "__main__":
    pytest.main([__file__])
