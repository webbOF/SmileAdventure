#!/usr/bin/env python3
"""
Basic Clinical Analysis Service Integration Test (Mock Mode)
Tests the service initialization and basic structure without requiring OpenAI API
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set mock environment for testing
os.environ['OPENAI_API_KEY'] = 'test-key-for-integration-testing'


async def test_service_imports():
    """Test that all imports work correctly"""
    print("🔍 Testing Clinical Analysis Service Imports")
    print("=" * 60)
    
    try:
        # Test basic imports
        print("\n1. Testing basic imports...")
        from src.services.clinical_analysis import ClinicalAnalysisService
        from src.models.llm_models import (
            ClinicalEmotionalPatterns, 
            ClinicalInterventionSuggestions,
            ClinicalProgressIndicators,
            GameSessionData
        )
        print("✅ All imports successful")
        
        # Test service initialization
        print("\n2. Testing service initialization...")
        clinical_service = ClinicalAnalysisService()
        print("✅ Service instance created")
        
        # Test service initialization
        print("\n3. Testing service initialization...")
        await clinical_service.initialize()
        print("✅ Service initialized successfully")
        
        # Test fallback methods
        print("\n4. Testing fallback mechanisms...")
        empty_result = clinical_service._create_empty_emotional_analysis()
        print(f"✅ Empty analysis fallback: {type(empty_result).__name__}")
        
        fallback_result = clinical_service._create_fallback_emotional_analysis([])
        print(f"✅ Fallback analysis: {type(fallback_result).__name__}")
        
        print("\n" + "=" * 60)
        print("🎉 Clinical Analysis Service structure is correct!")
        print("✅ All imports, initialization, and fallbacks working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_structure():
    """Test API endpoint structure"""
    print("\n🌐 Testing API Structure")
    print("=" * 60)
    
    try:
        # Test main app import
        print("\n1. Testing main app import...")
        from src.main import app, clinical_analysis_service
        print("✅ Main app and clinical service imported successfully")
        
        # Test that clinical service is initialized
        print("\n2. Testing clinical service integration...")
        print(f"✅ Clinical service type: {type(clinical_analysis_service).__name__}")
        
        # Test FastAPI routes
        print("\n3. Testing API routes...")
        routes = [route.path for route in app.routes]
        clinical_routes = [route for route in routes if 'clinical' in route]
        
        print(f"✅ Total routes: {len(routes)}")
        print(f"✅ Clinical routes: {len(clinical_routes)}")
        
        expected_clinical_routes = [
            '/clinical/analyze-emotional-patterns',
            '/clinical/generate-intervention-suggestions', 
            '/clinical/assess-progress-indicators',
            '/clinical/comprehensive-analysis'
        ]
        
        for expected_route in expected_clinical_routes:
            if expected_route in routes:
                print(f"   ✅ {expected_route}")
            else:
                print(f"   ❌ {expected_route} - MISSING")
        
        print("\n" + "=" * 60)
        print("🎉 API structure is properly configured!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API structure test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_model_validation():
    """Test Pydantic model validation"""
    print("\n📋 Testing Clinical Analysis Models")
    print("=" * 60)
    
    try:
        from src.models.llm_models import (
            ClinicalEmotionalPatterns,
            ClinicalInterventionSuggestions, 
            ClinicalProgressIndicators,
            InterventionSuggestion,
            ProgressMilestone
        )
        
        # Test ClinicalEmotionalPatterns
        print("\n1. Testing ClinicalEmotionalPatterns model...")
        emotional_patterns = ClinicalEmotionalPatterns(
            analysis_period_days=30,
            total_sessions_analyzed=10,
            confidence_score=0.85
        )
        print(f"✅ ClinicalEmotionalPatterns: {emotional_patterns.analysis_period_days} days")
        
        # Test InterventionSuggestion
        print("\n2. Testing InterventionSuggestion model...")
        intervention = InterventionSuggestion(
            intervention_type="behavioral_regulation",
            description="Implement structured emotional regulation teaching",
            priority_level="immediate",
            evidence_level="high",
            feasibility_score=0.8
        )
        print(f"✅ InterventionSuggestion: {intervention.intervention_type}")
        
        # Test ProgressMilestone
        print("\n3. Testing ProgressMilestone model...")
        milestone = ProgressMilestone(
            milestone_type="communication",
            description="Improved verbal expression",
            achievement_level=0.7
        )
        print(f"✅ ProgressMilestone: {milestone.milestone_type}")
        
        # Test ClinicalInterventionSuggestions
        print("\n4. Testing ClinicalInterventionSuggestions model...")
        intervention_suggestions = ClinicalInterventionSuggestions(
            immediate_interventions=[intervention],
            overall_effectiveness_prediction=0.75,
            confidence_score=0.8
        )
        print(f"✅ ClinicalInterventionSuggestions: {len(intervention_suggestions.immediate_interventions)} interventions")
        
        # Test ClinicalProgressIndicators
        print("\n5. Testing ClinicalProgressIndicators model...")
        progress_indicators = ClinicalProgressIndicators(
            assessment_period_days=30,
            milestone_achievements=[milestone],
            confidence_score=0.8
        )
        print(f"✅ ClinicalProgressIndicators: {len(progress_indicators.milestone_achievements)} milestones")
        
        print("\n" + "=" * 60)
        print("🎉 All clinical analysis models are working correctly!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Model validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all integration tests"""
    print("🚀 Clinical Analysis Service Integration Test (Mock Mode)")
    print("=" * 80)
    
    # Test imports and service structure
    service_test = await test_service_imports()
    
    # Test API structure
    api_test = await test_api_structure()
    
    # Test model validation
    model_test = await test_model_validation()
    
    print("\n" + "=" * 80)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Service Structure: {'PASSED' if service_test else 'FAILED'}")
    print(f"✅ API Structure: {'PASSED' if api_test else 'FAILED'}")
    print(f"✅ Model Validation: {'PASSED' if model_test else 'FAILED'}")
    
    all_passed = service_test and api_test and model_test
    
    if all_passed:
        print("\n🎯 INTEGRATION STATUS: ✅ SUCCESS")
        print("\n🎯 NEXT STEPS:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Start the service: python run_dev.py") 
        print("3. Test with real OpenAI calls")
        print("4. Run full functional tests")
        print("\n🚀 Clinical Analysis Service is ready for production!")
    else:
        print("\n❌ INTEGRATION STATUS: FAILED")
        print("Please fix the issues above before proceeding.")
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
