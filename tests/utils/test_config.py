"""
Test environment configuration and settings.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ServiceConfig:
    """Configuration for a microservice."""
    name: str
    url: str
    port: int
    health_endpoint: str = "/status"
    timeout: int = 30


@dataclass 
class TestEnvironmentConfig:
    """Test environment configuration."""
    
    # Environment settings
    environment: str = "test"
    debug: bool = False
    
    # API Gateway
    api_gateway_url: str = "http://localhost:8000"
    
    # Microservices
    auth_service: ServiceConfig = ServiceConfig("auth", "http://localhost:8001", 8001)
    users_service: ServiceConfig = ServiceConfig("users", "http://localhost:8002", 8002)
    game_service: ServiceConfig = ServiceConfig("game", "http://localhost:8003", 8003)
    llm_service: ServiceConfig = ServiceConfig("llm", "http://localhost:8004", 8004)
    reports_service: ServiceConfig = ServiceConfig("reports", "http://localhost:8005", 8005)
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/smileadventure_test"
    
    # Test data
    test_user_email: str = "test@example.com"
    test_user_password: str = "testpassword123"
    test_child_id: int = 1
    
    # Test timeouts
    default_timeout: int = 30
    health_check_timeout: int = 10
    auth_timeout: int = 15
    
    # Performance thresholds
    max_response_time: float = 2.0
    max_health_check_time: float = 0.5
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        self.environment = os.getenv("TEST_ENV", self.environment)
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Override URLs from environment
        self.api_gateway_url = os.getenv("API_GATEWAY_URL", self.api_gateway_url)
        self.auth_service.url = os.getenv("AUTH_SERVICE_URL", self.auth_service.url)
        self.users_service.url = os.getenv("USERS_SERVICE_URL", self.users_service.url)
        self.game_service.url = os.getenv("GAME_SERVICE_URL", self.game_service.url)
        self.llm_service.url = os.getenv("LLM_SERVICE_URL", self.llm_service.url)
        self.reports_service.url = os.getenv("REPORTS_SERVICE_URL", self.reports_service.url)
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", self.database_url)
        
        # Test credentials
        self.test_user_email = os.getenv("TEST_USER_EMAIL", self.test_user_email)
        self.test_user_password = os.getenv("TEST_USER_PASSWORD", self.test_user_password)
    
    def get_all_services(self) -> Dict[str, ServiceConfig]:
        """Get all service configurations."""
        return {
            "auth": self.auth_service,
            "users": self.users_service,
            "game": self.game_service,
            "llm": self.llm_service,
            "reports": self.reports_service
        }
    
    def get_service_url(self, service_name: str) -> Optional[str]:
        """Get URL for a specific service."""
        services = self.get_all_services()
        service = services.get(service_name)
        return service.url if service else None


class TestCategories:
    """Test category definitions and markers."""
    
    # Test types
    UNIT = "unit"
    INTEGRATION = "integration"
    END_TO_END = "e2e"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    RESEARCH = "research"
    
    # Feature areas
    AUTHENTICATION = "auth"
    USER_MANAGEMENT = "users"
    GAME_MECHANICS = "game"
    PROGRESS_TRACKING = "progress"
    REPORTING = "reports"
    LLM_ANALYSIS = "llm"
    
    # Test characteristics
    SLOW = "slow"
    FAST = "fast"
    CRITICAL = "critical"
    EXPERIMENTAL = "experimental"
    
    @classmethod
    def get_all_categories(cls) -> Dict[str, list]:
        """Get all test categories."""
        return {
            "types": [cls.UNIT, cls.INTEGRATION, cls.END_TO_END, cls.FUNCTIONAL, cls.PERFORMANCE, cls.RESEARCH],
            "features": [cls.AUTHENTICATION, cls.USER_MANAGEMENT, cls.GAME_MECHANICS, cls.PROGRESS_TRACKING, cls.REPORTING, cls.LLM_ANALYSIS],
            "characteristics": [cls.SLOW, cls.FAST, cls.CRITICAL, cls.EXPERIMENTAL]
        }


class TestDataConfig:
    """Configuration for test data and fixtures."""
    
    # Sample user data
    SAMPLE_USERS = [
        {
            "email": "parent1@example.com",
            "password": "password123",
            "name": "Parent One",
            "role": "parent"
        },
        {
            "email": "therapist1@example.com", 
            "password": "password123",
            "name": "Therapist One",
            "role": "therapist"
        },
        {
            "email": "admin1@example.com",
            "password": "password123", 
            "name": "Admin One",
            "role": "admin"
        }
    ]
    
    # Sample child profiles
    SAMPLE_CHILDREN = [
        {
            "child_id": 1,
            "name": "Test Child One",
            "age_months": 60,
            "asd_support_level": "LEVEL_2",
            "communication_preferences": ["visual"],
            "sensory_sensitivities": ["noise"],
            "interests": ["trains"],
            "triggers": ["loud sounds"],
            "effective_strategies": ["visual schedules"]
        },
        {
            "child_id": 2,
            "name": "Test Child Two", 
            "age_months": 48,
            "asd_support_level": "LEVEL_1",
            "communication_preferences": ["verbal", "visual"],
            "sensory_sensitivities": ["lights"],
            "interests": ["animals"],
            "triggers": ["crowds"],
            "effective_strategies": ["social stories"]
        }
    ]
    
    # Game scenarios
    SAMPLE_SCENARIOS = [
        {
            "scenario_id": "basic_adventure",
            "name": "Basic Adventure",
            "description": "Simple adventure game for beginners",
            "difficulty": "easy"
        },
        {
            "scenario_id": "emotion_garden",
            "name": "Emotion Garden",
            "description": "Exploring emotions through gardening",
            "difficulty": "normal"
        },
        {
            "scenario_id": "friendship_quest",
            "name": "Friendship Quest",
            "description": "Learning social skills through quests",
            "difficulty": "normal"
        }
    ]
    
    # Behavioral patterns
    BEHAVIORAL_PATTERNS = [
        "social_interaction",
        "communication_attempt",
        "repetitive_behavior",
        "sensory_seeking",
        "emotional_regulation",
        "attention_focus",
        "adaptive_behavior"
    ]
    
    # Emotional states
    EMOTIONAL_STATES = [
        "calm", "happy", "excited", "anxious", 
        "frustrated", "overwhelmed", "focused", 
        "tired", "confused", "comfortable"
    ]


# Global test configuration instance
TEST_CONFIG = TestEnvironmentConfig()


def get_test_config() -> TestEnvironmentConfig:
    """Get the global test configuration."""
    return TEST_CONFIG


def update_test_config(**kwargs):
    """Update test configuration with new values."""
    global TEST_CONFIG
    for key, value in kwargs.items():
        if hasattr(TEST_CONFIG, key):
            setattr(TEST_CONFIG, key, value)


def reset_test_config():
    """Reset test configuration to defaults."""
    global TEST_CONFIG
    TEST_CONFIG = TestEnvironmentConfig()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return TEST_CONFIG.debug


def get_service_health_urls() -> Dict[str, str]:
    """Get health check URLs for all services."""
    services = TEST_CONFIG.get_all_services()
    return {
        name: f"{config.url}{config.health_endpoint}" 
        for name, config in services.items()
    }


def get_test_database_url() -> str:
    """Get test database URL."""
    return TEST_CONFIG.database_url


def get_performance_thresholds() -> Dict[str, float]:
    """Get performance testing thresholds."""
    return {
        "max_response_time": TEST_CONFIG.max_response_time,
        "max_health_check_time": TEST_CONFIG.max_health_check_time
    }
