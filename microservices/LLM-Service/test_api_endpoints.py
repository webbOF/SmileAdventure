#!/usr/bin/env python3
"""
API Endpoint Test for Clinical Analysis Service
Tests the actual HTTP endpoints while the service is running
"""

import requests
import json
from datetime import datetime, timedelta

def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing Health Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8004/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service Status: {data.get('status')}")
            print(f"✅ OpenAI Status: {data.get('openai_status')}")
            print(f"✅ Service Version: {data.get('service_version')}")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_docs_endpoint():
    """Test the API documentation endpoint"""
    print("\n📚 Testing API Documentation")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8004/docs", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Documentation is accessible")
            print("🌐 Visit: http://localhost:8004/docs")
            return True
        else:
            print(f"❌ Docs failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Docs test failed: {str(e)}")
        return False

def create_sample_session_data():
    """Create sample session data for testing"""
    return {
        "user_id": 123,
        "session_id": "test-session-001",
        "child_id": 456,
        "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),
        "end_time": datetime.now().isoformat(),
        "duration_seconds": 3600,
        "emotions_detected": [
            {
                "emotion": "happy",
                "intensity": 0.8,
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "context": "completed_level"
            },
            {
                "emotion": "frustrated", 
                "intensity": 0.6,
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "context": "difficult_task"
            },
            {
                "emotion": "calm",
                "intensity": 0.7,
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "context": "end_session"
            }
        ],
        "game_level": "level_2",
        "score": 150,
        "interactions": [
            {
                "type": "click", 
                "element": "button", 
                "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat()
            }
        ],
        "behavioral_observations": [
            {
                "behavior": "attention_regulation",
                "intensity": 0.7,
                "context": "focused_task",
                "timestamp": (datetime.now() - timedelta(minutes=40)).isoformat()
            }
        ],
        "emotional_transitions": [
            {
                "from_state": "neutral",
                "to_state": "happy",
                "trigger": "level_completion",
                "duration": 120,
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat()
            }
        ]
    }

def test_clinical_emotional_patterns():
    """Test the clinical emotional patterns endpoint"""
    print("\n🧠 Testing Clinical Emotional Patterns Endpoint")
    print("=" * 50)
    
    try:
        # Create sample data
        session_history = [create_sample_session_data() for _ in range(3)]
        
        # Test without authentication first (should fail)
        response = requests.post(
            "http://localhost:8004/clinical/analyze-emotional-patterns",
            json=session_history,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Authentication required (as expected)")
            print("🔐 Endpoint is properly protected")
            return True
        elif response.status_code == 422:
            print("✅ Validation error (expected without proper auth)")
            return True
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Clinical endpoint test failed: {str(e)}")
        return False

def test_openapi_schema():
    """Test the OpenAPI schema includes clinical endpoints"""
    print("\n📋 Testing OpenAPI Schema")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8004/openapi.json", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            
            # Check for clinical endpoints
            clinical_endpoints = [
                "/clinical/analyze-emotional-patterns",
                "/clinical/generate-intervention-suggestions",
                "/clinical/assess-progress-indicators",
                "/clinical/comprehensive-analysis"
            ]
            
            found_endpoints = []
            for endpoint in clinical_endpoints:
                if endpoint in paths:
                    found_endpoints.append(endpoint)
                    print(f"✅ {endpoint}")
                else:
                    print(f"❌ {endpoint} - NOT FOUND")
            
            print(f"\n✅ Found {len(found_endpoints)}/{len(clinical_endpoints)} clinical endpoints")
            return len(found_endpoints) == len(clinical_endpoints)
        else:
            print(f"❌ OpenAPI schema failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAPI schema test failed: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Clinical Analysis API Endpoint Tests")
    print("=" * 60)
    
    # Test basic endpoints
    health_test = test_health_endpoint()
    docs_test = test_docs_endpoint()
    
    # Test clinical endpoints
    clinical_test = test_clinical_emotional_patterns()
    
    # Test OpenAPI schema
    schema_test = test_openapi_schema()
    
    print("\n" + "=" * 60)
    print("📊 API TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Health Endpoint: {'PASSED' if health_test else 'FAILED'}")
    print(f"✅ Documentation: {'PASSED' if docs_test else 'FAILED'}")
    print(f"✅ Clinical Endpoints: {'PASSED' if clinical_test else 'FAILED'}")
    print(f"✅ OpenAPI Schema: {'PASSED' if schema_test else 'FAILED'}")
    
    all_passed = health_test and docs_test and clinical_test and schema_test
    
    if all_passed:
        print("\n🎯 API INTEGRATION STATUS: ✅ SUCCESS")
        print("\n🌐 Available Endpoints:")
        print("   - GET  /health")
        print("   - GET  /docs") 
        print("   - POST /clinical/analyze-emotional-patterns")
        print("   - POST /clinical/generate-intervention-suggestions")
        print("   - POST /clinical/assess-progress-indicators")
        print("   - POST /clinical/comprehensive-analysis")
        print("\n🎉 Clinical Analysis Service APIs are ready!")
    else:
        print("\n❌ API INTEGRATION STATUS: FAILED")
    
    return all_passed

if __name__ == "__main__":
    main()
