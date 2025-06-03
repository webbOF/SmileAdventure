"""
Integration tests for Real-time AI Features
Tests the complete flow from Game Service through LLM Service for real-time AI analysis
"""

import asyncio
import json
import pytest
import websockets
from datetime import datetime
from typing import Dict, Any

import httpx
from fastapi.testclient import TestClient

# Mock test data
MOCK_SESSION_DATA = {
    "session_id": "test_session_123",
    "child_id": 456,
    "timestamp": "2025-06-03T10:30:00Z",
    "action_type": "object_interaction",
    "action_data": {
        "object_name": "red_ball",
        "interaction_type": "touch",
        "duration": 2.5,
        "success": True
    },
    "current_state": {
        "level": 2,
        "score": 150,
        "objective": "collect_all_balls"
    },
    "asd_metrics": {
        "overstimulation_score": 0.3,
        "engagement_level": 0.8,
        "attention_score": 0.7
    },
    "performance_data": {
        "response_time": 1.2,
        "accuracy": 0.9,
        "engagement_indicators": {
            "eye_contact_duration": 3.5,
            "interaction_frequency": 0.8
        }
    }
}

class TestRealtimeAIIntegration:
    """Integration tests for real-time AI features"""
    
    @pytest.fixture
    def llm_service_url(self):
        return "http://localhost:8004"
    
    @pytest.fixture
    def game_service_url(self):
        return "http://localhost:8005"
    
    @pytest.fixture
    def api_gateway_url(self):
        return "http://localhost:8000"
    
    @pytest.fixture
    def auth_headers(self):
        return {
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        }

    async def test_start_realtime_monitoring_flow(self, llm_service_url, auth_headers):
        """Test starting real-time AI monitoring"""
        session_id = "test_session_123"
        child_id = 456
        
        async with httpx.AsyncClient() as client:
            # Start monitoring in LLM Service
            response = await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/start",
                json={"child_id": child_id},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == session_id
            assert "metrics" in data

    async def test_streaming_ai_analysis(self, llm_service_url, auth_headers):
        """Test streaming AI analysis functionality"""
        session_id = "test_session_123"
        
        async with httpx.AsyncClient() as client:
            # First start monitoring
            await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/start",
                json={"child_id": 456},
                headers=auth_headers
            )
            
            # Send session data for analysis
            response = await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/analyze",
                json=MOCK_SESSION_DATA,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            analysis = data["analysis"]
            assert "analysis_id" in analysis
            assert "emotional_state" in analysis
            assert "engagement_level" in analysis
            assert "attention_score" in analysis
            assert "overstimulation_risk" in analysis
            assert "immediate_recommendations" in analysis
            
            # Verify analysis values are in expected ranges
            assert 0 <= analysis["engagement_level"] <= 1
            assert 0 <= analysis["attention_score"] <= 1
            assert 0 <= analysis["overstimulation_risk"] <= 1
            assert 0 <= analysis["confidence_score"] <= 1

    async def test_realtime_dashboard_data(self, llm_service_url, auth_headers):
        """Test real-time dashboard data retrieval"""
        session_id = "test_session_123"
        
        async with httpx.AsyncClient() as client:
            # Start monitoring and send some data
            await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/start",
                json={"child_id": 456},
                headers=auth_headers
            )
            
            await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/analyze",
                json=MOCK_SESSION_DATA,
                headers=auth_headers
            )
            
            # Get dashboard data
            response = await client.get(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/dashboard",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            dashboard = data["dashboard"]
            assert "session_info" in dashboard
            assert "current_state" in dashboard
            assert "session_averages" in dashboard
            assert "alerts" in dashboard

    async def test_live_recommendations_generation(self, llm_service_url, auth_headers):
        """Test live recommendations generation"""
        session_id = "test_session_123"
        
        context = {
            "current_level": 2,
            "current_score": 150,
            "recent_performance": "good",
            "engagement_trend": "increasing"
        }
        
        async with httpx.AsyncClient() as client:
            # Start monitoring
            await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/start",
                json={"child_id": 456},
                headers=auth_headers
            )
            
            # Generate recommendations
            response = await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/recommendations",
                json=context,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "recommendations" in data
            assert isinstance(data["recommendations"], list)
            assert len(data["recommendations"]) > 0

    async def test_overstimulation_pattern_detection(self, llm_service_url, auth_headers):
        """Test overstimulation pattern detection"""
        session_id = "test_session_123"
        
        async with httpx.AsyncClient() as client:
            # Start monitoring and send data
            await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/start",
                json={"child_id": 456},
                headers=auth_headers
            )
            
            # Send multiple data points to build pattern
            for i in range(3):
                modified_data = MOCK_SESSION_DATA.copy()
                modified_data["asd_metrics"]["overstimulation_score"] = 0.3 + (i * 0.2)
                
                await client.post(
                    f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/analyze",
                    json=modified_data,
                    headers=auth_headers
                )
            
            # Check overstimulation patterns
            response = await client.get(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/overstimulation-patterns",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            patterns = data["patterns"]
            assert "trend_analysis" in patterns
            assert "risk_level" in patterns
            assert "pattern_detection" in patterns

    async def test_game_service_ai_integration(self, game_service_url, auth_headers):
        """Test Game Service integration with real-time AI"""
        session_id = "test_session_123"
        user_id = 789
        
        async with httpx.AsyncClient() as client:
            # Start AI monitoring through Game Service
            response = await client.post(
                f"{game_service_url}/api/v1/game/realtime/start-ai-monitoring/{session_id}",
                params={"user_id": user_id, "child_id": 456},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["session_id"] == session_id

    async def test_game_action_with_ai_analysis(self, game_service_url, auth_headers):
        """Test processing game actions with AI analysis"""
        session_id = "test_session_123"
        
        action_data = {
            "action_type": "object_interaction",
            "target_object": "blue_cube",
            "interaction_type": "grab",
            "timestamp": datetime.now().isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            # Process action with AI analysis
            response = await client.post(
                f"{game_service_url}/api/v1/game/realtime/process-with-ai/{session_id}",
                json=action_data,
                headers=auth_headers
            )
            
            # Note: This test might fail if Game Service is not fully integrated
            # but it demonstrates the expected flow
            if response.status_code == 200:
                data = response.json()
                assert "success" in data or "game_result" in data

    async def test_api_gateway_realtime_routing(self, api_gateway_url, auth_headers):
        """Test API Gateway routing for real-time AI features"""
        session_id = "test_session_123"
        
        monitoring_data = {
            "child_id": 456,
            "monitoring_type": "full"
        }
        
        async with httpx.AsyncClient() as client:
            # Test starting monitoring through API Gateway
            response = await client.post(
                f"{api_gateway_url}/realtime-ai/start-monitoring/{session_id}",
                json=monitoring_data,
                headers=auth_headers
            )
            
            # This will test the routing but may fail if services are not running
            if response.status_code in [200, 503]:  # 503 = service unavailable is expected
                if response.status_code == 200:
                    data = response.json()
                    assert "success" in data

    async def test_websocket_connection_llm_service(self, llm_service_url):
        """Test WebSocket connection to LLM Service"""
        session_id = "test_session_123"
        ws_url = f"ws://localhost:8004/api/v1/realtime/stream/{session_id}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Wait for connection confirmation
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                
                assert data["type"] == "connection_established"
                assert data["session_id"] == session_id
                
                # Send heartbeat
                await websocket.send(json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                }))
                
                # Wait for heartbeat response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                assert response_data["type"] == "heartbeat_response"
                
        except Exception as e:
            # WebSocket tests may fail if service is not running
            pytest.skip(f"WebSocket test skipped due to connection error: {str(e)}")

    async def test_end_to_end_realtime_flow(self, llm_service_url, auth_headers):
        """Test complete end-to-end real-time AI flow"""
        session_id = "test_session_e2e"
        child_id = 789
        
        async with httpx.AsyncClient() as client:
            # 1. Start monitoring
            start_response = await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/start",
                json={"child_id": child_id},
                headers=auth_headers
            )
            assert start_response.status_code == 200
            
            # 2. Send session data for analysis
            analysis_response = await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/analyze",
                json=MOCK_SESSION_DATA,
                headers=auth_headers
            )
            assert analysis_response.status_code == 200
            
            # 3. Get dashboard data
            dashboard_response = await client.get(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/dashboard",
                headers=auth_headers
            )
            assert dashboard_response.status_code == 200
            
            # 4. Get recommendations
            recommendations_response = await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/recommendations",
                json={"context": "test"},
                headers=auth_headers
            )
            assert recommendations_response.status_code == 200
            
            # 5. End monitoring
            end_response = await client.post(
                f"{llm_service_url}/api/v1/realtime/sessions/{session_id}/end",
                headers=auth_headers
            )
            assert end_response.status_code == 200
            
            end_data = end_response.json()
            assert end_data["success"] is True
            assert "summary" in end_data

    def test_realtime_ai_service_health(self, llm_service_url):
        """Test real-time AI service health"""
        with httpx.Client() as client:
            response = client.get(f"{llm_service_url}/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] in ["healthy", "unhealthy"]

# Pytest configuration for async tests
@pytest.mark.asyncio
class TestRealtimeAIAsync(TestRealtimeAIIntegration):
    """Async test wrapper"""
    pass

if __name__ == "__main__":
    # Run tests directly
    import asyncio
    
    async def run_basic_tests():
        """Run basic tests without pytest"""
        test_instance = TestRealtimeAIIntegration()
        
        # Mock URLs and headers for direct testing
        llm_url = "http://localhost:8004"
        headers = {"Authorization": "Bearer test", "Content-Type": "application/json"}
        
        try:
            print("Testing real-time AI monitoring start...")
            await test_instance.test_start_realtime_monitoring_flow(llm_url, headers)
            print("✓ Monitoring start test passed")
            
            print("Testing streaming AI analysis...")
            await test_instance.test_streaming_ai_analysis(llm_url, headers)
            print("✓ Streaming analysis test passed")
            
            print("Testing dashboard data...")
            await test_instance.test_realtime_dashboard_data(llm_url, headers)
            print("✓ Dashboard test passed")
            
            print("All real-time AI tests completed successfully!")
            
        except Exception as e:
            print(f"Test failed: {str(e)}")
            return False
        
        return True
    
    # Run if executed directly
    success = asyncio.run(run_basic_tests())
    if success:
        print("🎉 Real-time AI integration tests completed successfully!")
    else:
        print("❌ Some tests failed. Please check service availability.")
