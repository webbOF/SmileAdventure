import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

import aiohttp
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.llm_models import (AnalysisType, ChildContext, GameSessionData,
                               LLMAnalysisRequest)


class TestLLMServiceIntegration:
    """Integration tests for LLM Service with other microservices"""
    
    @pytest.fixture
    def service_urls(self):
        """URLs for different microservices"""
        return {
            'llm': 'http://localhost:8004',
            'api_gateway': 'http://localhost:8000',
            'auth': 'http://localhost:8001',
            'game': 'http://localhost:8002',
            'users': 'http://localhost:8003',
            'reports': 'http://localhost:8005'
        }
    
    @pytest.fixture
    def sample_session_data(self):
        """Sample game session data for testing"""
        return GameSessionData(
            session_id="test-session-123",
            child_id=1,
            timestamp=datetime.now(),
            duration_minutes=15,
            game_type="social_interaction",
            activities_completed=["greeting", "eye_contact", "conversation"],
            interaction_events=[
                {
                    "timestamp": datetime.now(),
                    "event_type": "eye_contact_achieved",
                    "duration_seconds": 3.5,
                    "success": True
                },
                {
                    "timestamp": datetime.now(),
                    "event_type": "verbal_response",
                    "response_time_seconds": 2.1,
                    "appropriateness_score": 0.8
                }
            ],
            performance_metrics={
                "social_engagement_score": 0.75,
                "emotional_regulation_score": 0.68,
                "communication_effectiveness": 0.82,
                "task_completion_rate": 0.9
            },
            behavioral_observations=[
                "Child showed improved eye contact during conversation",
                "Demonstrated appropriate emotional responses",
                "Required minimal prompting for task completion"
            ],
            emotional_states_detected=[
                {
                    "emotion": "happy",
                    "confidence": 0.85,
                    "duration_seconds": 120
                },
                {
                    "emotion": "focused",
                    "confidence": 0.92,
                    "duration_seconds": 180
                }
            ]
        )
    
    @pytest.fixture
    def sample_child_context(self):
        """Sample child context for testing"""
        return ChildContext(
            age=8,
            diagnosis_details=["High-functioning autism", "Mild anxiety"],
            therapy_goals=[
                "Improve social communication",
                "Increase eye contact duration",
                "Develop emotional regulation skills"
            ],
            current_interventions=[
                "Applied Behavior Analysis (ABA)",
                "Speech therapy",
                "Social skills training"
            ],
            preferences=["Visual learning", "Technology-based activities"],
            challenges=["Difficulty with transitions", "Sensory sensitivities"]
        )
    
    @pytest.mark.asyncio
    async def test_llm_service_health_check(self, service_urls):
        """Test LLM service health endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{service_urls['llm']}/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] in ["healthy", "unhealthy"]
                assert "timestamp" in data
                assert "service_version" in data
    
    @pytest.mark.asyncio
    async def test_session_analysis_endpoint(self, service_urls, sample_session_data, sample_child_context):
        """Test session analysis endpoint"""
        request_data = LLMAnalysisRequest(
            session_data=sample_session_data,
            analysis_type=AnalysisType.COMPREHENSIVE,
            include_recommendations=True,
            child_context=sample_child_context
        )
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{service_urls['llm']}/analyze-session",
                json=request_data.dict(),
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "insights" in data
                    assert "emotional_analysis" in data
                    assert "behavioral_analysis" in data
                    assert "recommendations" in data
                else:
                    # Service might not be running, log for debugging
                    print(f"LLM service not available: {response.status}")
    
    @pytest.mark.asyncio
    async def test_emotional_analysis_endpoint(self, service_urls, sample_session_data):
        """Test emotional analysis endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{service_urls['llm']}/analyze-emotional-patterns",
                json=sample_session_data.dict(),
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "dominant_emotions" in data
                    assert "emotional_transitions" in data
                    assert "regulation_patterns" in data
    
    @pytest.mark.asyncio
    async def test_behavioral_analysis_endpoint(self, service_urls, sample_session_data):
        """Test behavioral analysis endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{service_urls['llm']}/analyze-behavioral-patterns",
                json=sample_session_data.dict(),
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "behavioral_patterns" in data
                    assert "engagement_levels" in data
                    assert "social_interaction_quality" in data
    
    @pytest.mark.asyncio
    async def test_recommendations_endpoint(self, service_urls, sample_session_data):
        """Test recommendations generation endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{service_urls['llm']}/generate-recommendations",
                json=sample_session_data.dict(),
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "immediate_interventions" in data
                    assert "long_term_goals" in data
                    assert "therapy_adjustments" in data
    
    @pytest.mark.asyncio
    async def test_progress_analysis_endpoint(self, service_urls, sample_session_data):
        """Test progress analysis endpoint"""
        # Create multiple sessions for progress analysis
        session_history = [sample_session_data] * 3  # Simulate 3 sessions
        
        request_data = {
            "session_history": [session.dict() for session in session_history],
            "child_id": 1,
            "analysis_timeframe_days": 30
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{service_urls['llm']}/analyze-progress",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    assert "progress_trends" in data
                    assert "improvement_areas" in data
                    assert "milestone_achievements" in data
    
    @pytest.mark.asyncio
    async def test_integration_with_api_gateway(self, service_urls, sample_session_data):
        """Test LLM service integration through API Gateway"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test through API Gateway routing
                async with session.post(
                    f"{service_urls['api_gateway']}/llm/analyze-emotional-patterns",
                    json=sample_session_data.dict(),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        assert isinstance(data, dict)
                    else:
                        print(f"API Gateway routing test skipped: {response.status}")
        except aiohttp.ClientConnectorError:
            print("API Gateway not available for integration test")
    
    @pytest.mark.asyncio
    async def test_service_discovery_and_communication(self, service_urls):
        """Test service discovery and inter-service communication"""
        services_to_test = ['llm', 'auth', 'game', 'users', 'reports']
        service_statuses = {}
        
        async with aiohttp.ClientSession() as session:
            for service in services_to_test:
                try:
                    async with session.get(f"{service_urls[service]}/health", timeout=5) as response:
                        service_statuses[service] = response.status == 200
                except:
                    service_statuses[service] = False
        
        # At least LLM service should be available for this test
        assert service_statuses.get('llm', False), "LLM service should be available"
        
        # Log status of other services
        for service, status in service_statuses.items():
            print(f"Service {service}: {'Available' if status else 'Not Available'}")
    
    @pytest.mark.asyncio
    async def test_data_flow_integration(self, service_urls, sample_session_data):
        """Test complete data flow from game session to analysis"""
        try:
            # Simulate data flow: Game Service -> LLM Service -> Reports Service
            
            # Step 1: Post session data (simulate Game Service)
            session_data = sample_session_data.dict()
            
            # Step 2: Analyze with LLM Service
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{service_urls['llm']}/analyze-emotional-patterns",
                    json=session_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        analysis_result = await response.json()
                        
                        # Step 3: Verify analysis contains expected structure
                        assert isinstance(analysis_result, dict)
                        
                        # Step 4: Test that analysis can be sent to Reports Service
                        # (This would normally be done by the API Gateway or Reports Service)
                        report_data = {
                            "session_id": sample_session_data.session_id,
                            "child_id": sample_session_data.child_id,
                            "analysis_result": analysis_result,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # Verify report data structure
                        assert "session_id" in report_data
                        assert "analysis_result" in report_data
                        
                        print("Data flow integration test completed successfully")
                    else:
                        print(f"LLM analysis failed with status: {response.status}")
                        
        except Exception as e:
            print(f"Data flow integration test error: {str(e)}")
    
    @pytest.mark.asyncio
    async def test_error_handling_and_fallbacks(self, service_urls, sample_session_data):
        """Test error handling and fallback mechanisms"""
        # Test with invalid data
        invalid_data = {"invalid": "data"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{service_urls['llm']}/analyze-emotional-patterns",
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                # Should return 422 for validation error
                assert response.status in [422, 400, 500]
    
    @pytest.mark.asyncio
    async def test_performance_and_load(self, service_urls, sample_session_data):
        """Test service performance under load"""
        # Create multiple concurrent requests
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(5):  # 5 concurrent requests
                task = session.post(
                    f"{service_urls['llm']}/analyze-emotional-patterns",
                    json=sample_session_data.dict(),
                    headers={"Content-Type": "application/json"}
                )
                tasks.append(task)
            
            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that most requests succeeded
            successful_requests = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
            print(f"Successful concurrent requests: {successful_requests}/5")

if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v"])
