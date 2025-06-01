#!/usr/bin/env python3
"""
Simple test script to verify LLM Service can start
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def test_imports():
    """Test if all imports work"""
    try:
        print("Testing imports...")
        
        # Test config import
        from src.config.settings import get_settings
        print("✓ Config import successful")
        
        # Test settings
        settings = get_settings()
        print(f"✓ Settings loaded: {settings.SERVICE_NAME}")
        
        # Test models import
        from src.models.llm_models import GameSessionData, LLMAnalysisRequest
        print("✓ Models import successful")
        
        # Test middleware import
        from src.middleware import (rate_limit_middleware,
                                    security_headers_middleware)
        print("✓ Middleware import successful")
        
        # Test monitoring import
        from src.monitoring import metrics, setup_logging
        print("✓ Monitoring import successful")
        
        # Test service import
        from src.services.llm_service import LLMService
        print("✓ LLM Service import successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

async def test_service_basic():
    """Test basic service functionality"""
    try:
        from src.services.llm_service import LLMService

        # Create service instance
        service = LLMService()
        print("✓ LLM Service instance created")
        
        # Test without actual OpenAI key (should fail gracefully)
        # await service.initialize()
        
        return True
        
    except Exception as e:
        print(f"Service test error: {e}")
        return False

if __name__ == "__main__":
    print("LLM Service Import Test")
    print("=" * 40)
    
    # Set minimal environment
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    
    # Run tests
    success = asyncio.run(test_imports())
    if success:
        print("\n✓ All imports successful!")
        asyncio.run(test_service_basic())
    else:
        print("\n✗ Import tests failed!")
        sys.exit(1)
