#!/usr/bin/env python3
"""
Comprehensive Reports API Testing Script
Tests all endpoints with progressive complexity
"""

import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8009"

def test_health():
    """Test service health"""
    print("🔍 Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_game_session_submission():
    """Test game session data submission"""
    print("\n🎮 Testing Game Session Submission...")
    
    test_data = {
        "user_id": 123,
        "session_id": "session_001",
        "start_time": "2025-05-28T10:00:00Z",
        "end_time": "2025-05-28T10:30:00Z",
        "emotions_detected": [
            {"emotion": "happy", "intensity": 0.8, "timestamp": "2025-05-28T10:05:00Z"},
            {"emotion": "excited", "intensity": 0.9, "timestamp": "2025-05-28T10:15:00Z"},
            {"emotion": "focused", "intensity": 0.7, "timestamp": "2025-05-28T10:25:00Z"}
        ],
        "game_level": "level_1",
        "score": 85
    }
    
    response = requests.post(f"{BASE_URL}/api/reports/game-session", json=test_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 201

def test_multiple_sessions():
    """Submit multiple sessions for testing"""
    print("\n📊 Submitting Multiple Test Sessions...")
    
    sessions = [
        {
            "user_id": 123,
            "session_id": "session_002",
            "start_time": "2025-05-28T11:00:00Z",
            "end_time": "2025-05-28T11:30:00Z",
            "emotions_detected": [
                {"emotion": "happy", "intensity": 0.6},
                {"emotion": "calm", "intensity": 0.8}
            ],
            "game_level": "level_2",
            "score": 92
        },
        {
            "user_id": 123,
            "session_id": "session_003",
            "start_time": "2025-05-28T12:00:00Z",
            "end_time": "2025-05-28T12:30:00Z",
            "emotions_detected": [
                {"emotion": "excited", "intensity": 0.9},
                {"emotion": "happy", "intensity": 0.7},
                {"emotion": "frustrated", "intensity": 0.3}
            ],
            "game_level": "level_3",
            "score": 78
        },
        {
            "user_id": 456,
            "session_id": "session_004", 
            "start_time": "2025-05-28T13:00:00Z",
            "end_time": "2025-05-28T13:30:00Z",
            "emotions_detected": [
                {"emotion": "calm", "intensity": 0.9},
                {"emotion": "focused", "intensity": 0.8}
            ],
            "game_level": "level_1",
            "score": 95
        }
    ]
    
    success_count = 0
    for i, session in enumerate(sessions):
        response = requests.post(f"{BASE_URL}/api/reports/game-session", json=session)
        print(f"Session {i+1}: Status {response.status_code}")
        if response.status_code == 201:
            success_count += 1
    
    print(f"Successfully submitted {success_count}/{len(sessions)} sessions")
    return success_count == len(sessions)

def test_child_summary():
    """Test child summary generation"""
    print("\n📈 Testing Child Summary Generation...")
    
    child_id = 123
    response = requests.get(f"{BASE_URL}/api/reports/child/{child_id}/summary")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        summary = response.json()
        print(f"Summary for Child {child_id}:")
        print(f"  Total Play Time: {summary.get('total_play_time_hours', 0)} hours")
        print(f"  Average Score: {summary.get('average_score', 'N/A')}")
        print(f"  Most Frequent Emotion: {summary.get('most_frequent_emotion', 'N/A')}")
        print(f"  Progress Summary: {summary.get('progress_summary', {})}")
        return True
    return False

def test_emotion_patterns():
    """Test emotion pattern analysis"""
    print("\n🧠 Testing Emotion Pattern Analysis...")
    
    child_id = 123
    response = requests.get(f"{BASE_URL}/api/reports/child/{child_id}/emotion-patterns")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        patterns = response.json()
        print(f"Emotion patterns for Child {child_id}:")
        for pattern in patterns:
            print(f"  {pattern['emotion']}: frequency={pattern['frequency']}, avg_intensity={pattern.get('average_intensity', 'N/A')}")
        return True
    return False

def test_nonexistent_child():
    """Test behavior with non-existent child"""
    print("\n❓ Testing Non-existent Child...")
    
    child_id = 999
    response = requests.get(f"{BASE_URL}/api/reports/child/{child_id}/summary")
    print(f"Summary Status: {response.status_code}")
    
    response2 = requests.get(f"{BASE_URL}/api/reports/child/{child_id}/emotion-patterns")
    print(f"Patterns Status: {response2.status_code}")
    
    # Should return 404 or empty list
    return response.status_code in [404, 200] and response2.status_code in [200]

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 STARTING COMPREHENSIVE REPORTS API VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Game Session Submission", test_game_session_submission),
        ("Multiple Sessions", test_multiple_sessions), 
        ("Child Summary", test_child_summary),
        ("Emotion Patterns", test_emotion_patterns),
        ("Non-existent Child", test_nonexistent_child)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "✅ PASSED" if result else "❌ FAILED"))
        except Exception as e:
            results.append((test_name, f"💥 ERROR: {str(e)}"))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        print(f"{test_name:25} {result}")
        if "PASSED" in result:
            passed += 1
    
    percentage = (passed / len(results)) * 100
    print(f"\n🎯 Overall Success Rate: {passed}/{len(results)} ({percentage:.1f}%)")
    
    return percentage

if __name__ == "__main__":
    run_comprehensive_test()
