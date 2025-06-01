"""
Common test helper functions and utilities for SmileAdventure test suite.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt
import requests


class TestAPIClient:
    """Test API client for making requests to microservices."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
    def set_auth_token(self, token: str):
        """Set authentication token for requests."""
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request and return structured response."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "headers": dict(response.headers)
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.text,
                "headers": dict(response.headers)
            }


class AuthTestHelper:
    """Helper for authentication-related test operations."""
    
    def __init__(self, api_client: TestAPIClient):
        self.api_client = api_client
    
    def register_test_user(self, email: str = "test@example.com", 
                          password: str = "testpassword123", 
                          name: str = "Test User") -> Dict[str, Any]:
        """Register a test user."""
        user_data = {
            "email": email,
            "password": password,
            "name": name,
            "role": "parent"
        }
        
        return self.api_client.make_request("post", "/api/v1/auth/register", json=user_data)
    
    def login_test_user(self, email: str = "test@example.com", 
                       password: str = "testpassword123") -> Dict[str, Any]:
        """Login a test user and return token."""
        login_data = {
            "email": email,
            "password": password
        }
        
        response = self.api_client.make_request("post", "/api/v1/auth/login", json=login_data)
        
        if response.get("success") and "access_token" in response.get("data", {}):
            token = response["data"]["access_token"]
            self.api_client.set_auth_token(token)
            response["token"] = token
            
        return response
    
    def decode_jwt_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token (without verification for testing)."""
        try:
            # Decode without verification for testing purposes
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            return {"error": str(e)}


class GameTestHelper:
    """Helper for game-related test operations."""
    
    def __init__(self, api_client: TestAPIClient):
        self.api_client = api_client
    
    def get_scenarios(self) -> Dict[str, Any]:
        """Get available game scenarios."""
        return self.api_client.make_request("get", "/api/v1/game/scenarios")
    
    def start_game_session(self, scenario_id: str = "basic_adventure", 
                          difficulty: str = "normal") -> Dict[str, Any]:
        """Start a new game session."""
        session_data = {
            "scenario_id": scenario_id,
            "difficulty": difficulty
        }
        
        return self.api_client.make_request("post", "/api/v1/game/start", json=session_data)
    
    def process_game_action(self, session_id: str, action_type: str, 
                           action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a game action."""
        action_payload = {
            "session_id": session_id,
            "action_type": action_type,
            "action_data": action_data
        }
        
        return self.api_client.make_request("post", "/api/v1/game/action", json=action_payload)
    
    def get_game_state(self, session_id: str) -> Dict[str, Any]:
        """Get current game state."""
        return self.api_client.make_request("get", f"/api/v1/game/state/{session_id}")


class ProgressTestHelper:
    """Helper for progress tracking test operations."""
    
    def __init__(self, api_client: TestAPIClient):
        self.api_client = api_client
    
    def initialize_tracking(self, child_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize progress tracking for a child."""
        payload = {
            "child_id": child_id,
            "config": config
        }
        
        return self.api_client.make_request("post", "/api/v1/progress/initialize", json=payload)
    
    def record_behavioral_data(self, child_id: int, behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record behavioral observation data."""
        payload = {
            "child_id": child_id,
            "behavioral_data": behavioral_data
        }
        
        return self.api_client.make_request("post", "/api/v1/progress/behavioral-data", json=payload)
    
    def record_emotional_transition(self, child_id: int, transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record emotional state transition."""
        payload = {
            "child_id": child_id,
            "transition_data": transition_data
        }
        
        return self.api_client.make_request("post", "/api/v1/progress/emotional-transitions", json=payload)
    
    def get_progress_dashboard(self, child_id: int) -> Dict[str, Any]:
        """Get progress dashboard data."""
        return self.api_client.make_request("get", f"/api/v1/progress/dashboard/{child_id}")


class TestDataBuilder:
    """Builder for creating test data objects."""
    
    @staticmethod
    def create_child_profile(child_id: int = 1, name: str = "Test Child", 
                           age_months: int = 60) -> Dict[str, Any]:
        """Create a test child profile."""
        return {
            "child_id": child_id,
            "name": name,
            "age_months": age_months,
            "asd_support_level": "LEVEL_2",
            "communication_preferences": ["visual"],
            "sensory_sensitivities": ["noise"],
            "interests": ["trains"],
            "triggers": ["loud sounds"],
            "effective_strategies": ["visual schedules"]
        }
    
    @staticmethod
    def create_behavioral_data_point(behavior_type: str = "social_interaction", 
                                   intensity: float = 0.7) -> Dict[str, Any]:
        """Create a test behavioral data point."""
        return {
            "timestamp": datetime.now().isoformat(),
            "behavior_type": behavior_type,
            "intensity": intensity,
            "duration_seconds": 120,
            "context": {"environment": "therapy_room"},
            "trigger": "peer_approach",
            "intervention_used": "social_story"
        }
    
    @staticmethod
    def create_emotional_transition(from_state: str = "calm", 
                                  to_state: str = "excited") -> Dict[str, Any]:
        """Create a test emotional transition."""
        return {
            "timestamp": datetime.now().isoformat(),
            "from_state": from_state,
            "to_state": to_state,
            "trigger_event": "new_activity",
            "transition_duration": 30.0,
            "support_needed": False,
            "regulation_strategy_used": None
        }
    
    @staticmethod
    def create_game_session_data(session_id: str = None, user_id: int = 1) -> Dict[str, Any]:
        """Create test game session data."""
        if not session_id:
            session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        return {
            "session_id": session_id,
            "user_id": user_id,
            "scenario_id": "basic_adventure",
            "start_time": datetime.now().isoformat(),
            "difficulty": "normal",
            "initial_state": {
                "score": 0,
                "level": 1,
                "objective": "Welcome to the adventure!"
            }
        }


class TestPerformanceTracker:
    """Track performance metrics during tests."""
    
    def __init__(self):
        self.metrics = []
    
    def start_timer(self, operation: str) -> float:
        """Start timing an operation."""
        start_time = time.time()
        return start_time
    
    def end_timer(self, operation: str, start_time: float):
        """End timing and record metric."""
        end_time = time.time()
        duration = end_time - start_time
        
        self.metrics.append({
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
        
        return duration
    
    def get_average_duration(self, operation: str) -> float:
        """Get average duration for an operation."""
        operation_metrics = [m for m in self.metrics if m["operation"] == operation]
        if not operation_metrics:
            return 0.0
        
        total_duration = sum(m["duration"] for m in operation_metrics)
        return total_duration / len(operation_metrics)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        operations = set(m["operation"] for m in self.metrics)
        
        summary = {
            "total_operations": len(self.metrics),
            "unique_operations": len(operations),
            "operations": {}
        }
        
        for operation in operations:
            op_metrics = [m for m in self.metrics if m["operation"] == operation]
            durations = [m["duration"] for m in op_metrics]
            
            summary["operations"][operation] = {
                "count": len(op_metrics),
                "average_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations)
            }
        
        return summary


def wait_for_service(url: str, timeout: int = 30) -> bool:
    """Wait for a service to become available."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/status", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
    
    return False


def assert_response_success(response: Dict[str, Any], expected_status: int = 200):
    """Assert that an API response is successful."""
    assert response.get("success") is True, f"Request failed: {response.get('error', 'Unknown error')}"
    assert response.get("status_code") == expected_status, f"Expected status {expected_status}, got {response.get('status_code')}"


def assert_has_keys(data: Dict[str, Any], required_keys: List[str]):
    """Assert that a dictionary has all required keys."""
    missing_keys = [key for key in required_keys if key not in data]
    assert not missing_keys, f"Missing required keys: {missing_keys}"


def create_test_report(test_results: List[Dict[str, Any]], 
                      performance_metrics: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a comprehensive test report."""
    total_tests = len(test_results)
    passed_tests = len([r for r in test_results if r.get("status") == "PASS"])
    failed_tests = total_tests - passed_tests
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        },
        "test_results": test_results
    }
    
    if performance_metrics:
        report["performance_metrics"] = performance_metrics
    
    return report
