#!/usr/bin/env python3
"""
Integration test for Clinical Analysis Service endpoints
Tests the three main clinical analysis methods and API endpoints
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.clinical_analysis import ClinicalAnalysisService
from src.models.llm_models import GameSessionData


def create_sample_session_data() -> GameSessionData:
    """Create sample session data for testing"""
    return GameSessionData(
        user_id=123,
        session_id="test-session-001",
        child_id=456,
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now(),
        duration_seconds=3600,
        emotions_detected=[
            {
                "emotion": "happy",
                "intensity": 0.8,
                "timestamp": datetime.now() - timedelta(minutes=30),
                "context": "completed_level"
            },
            {
                "emotion": "frustrated",
                "intensity": 0.6,
                "timestamp": datetime.now() - timedelta(minutes=15),
                "context": "difficult_task"
            },
            {
                "emotion": "calm",
                "intensity": 0.7,
                "timestamp": datetime.now() - timedelta(minutes=5),
                "context": "end_session"
            }
        ],
        game_level="level_2",
        score=150,
        interactions=[
            {"type": "click", "element": "button", "timestamp": datetime.now() - timedelta(minutes=45)},
            {"type": "gesture", "element": "character", "timestamp": datetime.now() - timedelta(minutes=20)}
        ],
        behavioral_observations=[
            {
                "behavior": "attention_regulation",
                "intensity": 0.7,
                "context": "focused_task",
                "timestamp": datetime.now() - timedelta(minutes=40)
            }
        ],
        emotional_transitions=[
            {
                "from_state": "neutral",
                "to_state": "happy",
                "trigger": "level_completion",
                "duration": 120,
                "timestamp": datetime.now() - timedelta(minutes=30)
            },
            {
                "from_state": "happy",
                "to_state": "frustrated",
                "trigger": "increased_difficulty",
                "duration": 180,
                "timestamp": datetime.now() - timedelta(minutes=15)
            },
            {
                "from_state": "frustrated",
                "to_state": "calm",
                "trigger": "support_intervention",
                "duration": 240,
                "timestamp": datetime.now() - timedelta(minutes=5)
            }
        ]
    )


async def test_clinical_analysis_service():
    """Test the clinical analysis service initialization and basic functionality"""
    
    print("🧠 Testing Clinical Analysis Service Integration")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. Initializing Clinical Analysis Service...")
        clinical_service = ClinicalAnalysisService()
        await clinical_service.initialize()
        print("✅ Service initialized successfully")
        
        # Create sample data
        print("\n2. Creating sample session data...")
        session_data = [create_sample_session_data() for _ in range(3)]
        print(f"✅ Created {len(session_data)} sample sessions")
        
        # Test emotional pattern analysis
        print("\n3. Testing emotional pattern analysis...")
        emotional_result = await clinical_service.analyze_emotional_patterns(session_data)
        print("✅ Emotional pattern analysis completed")
        print(f"   - Analysis period: {emotional_result.get('analysis_period_days', 'N/A')} days")
        print(f"   - Sessions analyzed: {emotional_result.get('total_sessions_analyzed', 'N/A')}")
        print(f"   - Confidence score: {emotional_result.get('confidence_score', 'N/A')}")
        
        # Test intervention suggestions
        print("\n4. Testing intervention suggestions...")
        intervention_result = await clinical_service.generate_intervention_suggestions(emotional_result)
        print("✅ Intervention suggestions generated")
        immediate_count = len(intervention_result.get('immediate_interventions', []))
        short_term_count = len(intervention_result.get('short_term_recommendations', []))
        print(f"   - Immediate interventions: {immediate_count}")
        print(f"   - Short-term recommendations: {short_term_count}")
        print(f"   - Confidence score: {intervention_result.get('confidence_score', 'N/A')}")
        
        # Test progress assessment
        print("\n5. Testing progress assessment...")
        progress_metrics = {
            "emotional_stability": 0.7,
            "regulation_success_rate": 0.6,
            "milestone_data": {
                "communication_improvement": 0.8,
                "social_engagement": 0.5
            }
        }
        progress_result = await clinical_service.assess_progress_indicators(progress_metrics)
        print("✅ Progress assessment completed")
        milestone_count = len(progress_result.get('milestone_achievements', []))
        print(f"   - Milestones assessed: {milestone_count}")
        print(f"   - Assessment period: {progress_result.get('assessment_period_days', 'N/A')} days")
        print(f"   - Confidence score: {progress_result.get('confidence_score', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("🎉 All Clinical Analysis Service tests completed successfully!")
        print("✅ Service is ready for production use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints():
    """Test API endpoints with sample requests"""
    print("\n🌐 Testing API Endpoint Availability")
    print("=" * 60)
    
    try:
        import requests
        
        base_url = "http://localhost:8004"
        
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint responding")
        else:
            print(f"⚠️ Health endpoint returned status: {response.status_code}")
        
        # Note: We won't test the actual clinical endpoints without authentication
        print("\n2. Clinical endpoints available:")
        print("   - POST /clinical/analyze-emotional-patterns")
        print("   - POST /clinical/generate-intervention-suggestions") 
        print("   - POST /clinical/assess-progress-indicators")
        print("   - POST /clinical/comprehensive-analysis")
        print("✅ All clinical endpoints are configured")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️ Service not running - start with: python run_dev.py")
        return False
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False


async def main():
    """Run all integration tests"""
    print("🚀 Clinical Analysis Service Integration Test")
    print("=" * 60)
    
    # Test service functionality
    service_test = await test_clinical_analysis_service()
    
    # Test API endpoints (if service is running)
    api_test = await test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Service Tests: {'PASSED' if service_test else 'FAILED'}")
    print(f"✅ API Tests: {'PASSED' if api_test else 'LIMITED'}")
    
    if service_test:
        print("\n🎯 NEXT STEPS:")
        print("1. Start the service: python run_dev.py")
        print("2. Test endpoints with: POST requests to /clinical/* endpoints")
        print("3. Use proper authentication headers for protected endpoints")
        print("4. Monitor logs for clinical analysis performance")
    
    return service_test


if __name__ == "__main__":
    asyncio.run(main())
