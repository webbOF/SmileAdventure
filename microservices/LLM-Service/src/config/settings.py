import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
      # Service configuration
    SERVICE_NAME: str = "LLM-Service"
    SERVICE_PORT: int = 8004
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = "INFO"
    
    # OpenAI configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.3
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TIMEOUT: int = 30
    
    # Analysis configuration
    DEFAULT_ANALYSIS_DEPTH: str = "comprehensive"
    ENABLE_CACHING: bool = True
    CACHE_TTL_SECONDS: int = 3600
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_TOKENS_PER_MINUTE: int = 90000
    
    # Database (if needed for caching)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./llm_service.db")
    
    # External services
    GAME_SERVICE_URL: str = os.getenv("GAME_SERVICE_URL", "http://localhost:8002")
    USERS_SERVICE_URL: str = os.getenv("USERS_SERVICE_URL", "http://localhost:8001")
    REPORTS_SERVICE_URL: str = os.getenv("REPORTS_SERVICE_URL", "http://localhost:8003")
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    ALLOWED_ORIGINS: list = ["*"]  # Configure properly in production
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
