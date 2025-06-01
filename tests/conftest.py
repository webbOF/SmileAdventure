"""
Pytest configuration and shared fixtures for SmileAdventure test suite.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, Generator

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "microservices"))

# Test configuration
TEST_CONFIG = {
    "API_BASE_URL": "http://localhost:8000",
    "AUTH_SERVICE_URL": "http://localhost:8001", 
    "USERS_SERVICE_URL": "http://localhost:8002",
    "GAME_SERVICE_URL": "http://localhost:8003",
    "LLM_SERVICE_URL": "http://localhost:8004",
    "REPORTS_SERVICE_URL": "http://localhost:8005",
    "TEST_TIMEOUT": 30,
    "TEST_USER_EMAIL": "test@example.com",
    "TEST_USER_PASSWORD": "testpassword123",
    "DEBUG": os.getenv("DEBUG", "false").lower() == "true"
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Provide test configuration."""
    return TEST_CONFIG.copy()

@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Provide API base URL."""
    return TEST_CONFIG["API_BASE_URL"]

@pytest.fixture(scope="session")
def test_user_credentials() -> Dict[str, str]:
    """Provide test user credentials."""
    return {
        "email": TEST_CONFIG["TEST_USER_EMAIL"],
        "password": TEST_CONFIG["TEST_USER_PASSWORD"]
    }

@pytest.fixture
def test_session_data() -> Dict[str, Any]:
    """Provide sample test session data."""
    from datetime import datetime
    
    return {
        "user_id": 1,
        "session_id": f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "child_id": 1,
        "scenario_id": "basic_adventure",
        "start_time": datetime.now().isoformat(),
        "game_level": "level_1",
        "difficulty": "normal"
    }

@pytest.fixture
def sample_behavioral_data() -> Dict[str, Any]:
    """Provide sample behavioral data for testing."""
    from datetime import datetime
    
    return {
        "timestamp": datetime.now().isoformat(),
        "behavior_type": "social_interaction",
        "intensity": 0.7,
        "duration_seconds": 120,
        "context": {"environment": "therapy_room"},
        "trigger": "peer_approach",
        "intervention_used": "social_story"
    }

@pytest.fixture
def sample_emotional_data() -> Dict[str, Any]:
    """Provide sample emotional data for testing."""
    from datetime import datetime
    
    return {
        "timestamp": datetime.now().isoformat(),
        "from_state": "calm",
        "to_state": "excited", 
        "trigger_event": "new_activity",
        "transition_duration": 30.0,
        "support_needed": False
    }

@pytest.fixture
def mock_openai_response() -> Dict[str, Any]:
    """Provide mock OpenAI API response."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Test analysis response"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        }
    }

# Pytest configuration
pytest_plugins = [
    "tests.utils.test_helpers",
]

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"  
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "functional: marks tests as functional tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "research: marks tests as research/experimental tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: marks tests related to authentication"
    )
    config.addinivalue_line(
        "markers", "game: marks tests related to game functionality"
    )
    config.addinivalue_line(
        "markers", "progress: marks tests related to progress tracking"
    )

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location."""
    for item in items:
        # Add markers based on test file location
        test_path = str(item.fspath)
        
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
        elif "/end_to_end/" in test_path:
            item.add_marker(pytest.mark.e2e)
        elif "/functional/" in test_path:
            item.add_marker(pytest.mark.functional)
        elif "/performance/" in test_path:
            item.add_marker(pytest.mark.performance)
        elif "/research/" in test_path:
            item.add_marker(pytest.mark.research)
            
        # Add feature-specific markers
        if "/authentication/" in test_path:
            item.add_marker(pytest.mark.auth)
        elif "/game_mechanics/" in test_path:
            item.add_marker(pytest.mark.game)
        elif "/progress_tracking/" in test_path:
            item.add_marker(pytest.mark.progress)
