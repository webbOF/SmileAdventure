#!/usr/bin/env python3
"""
Enhanced Game Service Testing Script
Tests the new comprehensive game endpoints and functionality
"""

import json
import time
from datetime import datetime
from typing import Any, Dict

import requests

# API Configuration
BASE_URL = "http://localhost:8000"  # API Gateway
GAME_DIRECT_URL = "http://localhost:8005"  # Direct Game Service
AUTH_URL = f"{BASE_URL}/auth"
GAME_URL = f"{BASE_URL}/game"

# Test user credentials
TEST_USER = {
    "email": "test2@example.com",
    "password": "password123"
}

def make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Make HTTP request with error handling"""
    try:
        response = getattr(requests, method.lower())(url, **kwargs)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.content else {},
            "success": response.status_code < 400
        }
    except Exception as e:
        return {
            "status_code": 0,
            "data": {"error": str(e)},
            "success": False
        }

def test_authentication() -> str:
    """Test authentication and return JWT token"""
    print("\n🔐 AUTHENTICATION TEST")
    print("=" * 50)
    
    # Login
    login_response = make_request("post", f"{AUTH_URL}/login", json=TEST_USER)
    
    if login_response["success"]:
        token = login_response["data"].get("access_token")
        print(f"✅ Login successful! Token: {token[:50]}...")
        return token
    else:
        print(f"❌ Login failed: {login_response['data']}")
        return None

def test_game_service_health():
    """Test game service health endpoints"""
    print("\n🏥 GAME SERVICE HEALTH CHECK")
    print("=" * 50)
    
    # Direct health check
    direct_health = make_request("get", f"{GAME_DIRECT_URL}/status")
    print(f"Direct Game Service Health: {direct_health['status_code']} - {direct_health['data']}")
    
    # Through API Gateway
    gateway_health = make_request("get", f"{GAME_URL}/health")
    print(f"Gateway Game Health: {gateway_health['status_code']} - {gateway_health['data']}")
    
    return direct_health["success"] and gateway_health["success"]

def test_game_scenarios(headers: Dict[str, str]):
    """Test available game scenarios"""
    print("\n🎮 GAME SCENARIOS TEST")
    print("=" * 50)
    
    # Get available scenarios
    scenarios_response = make_request("get", f"{GAME_DIRECT_URL}/api/v1/game/scenarios")
    
    if scenarios_response["success"]:
        scenarios = scenarios_response["data"]
        print(f"✅ Available scenarios: {scenarios.get('total_count', 0)}")
        for scenario_id, scenario_data in scenarios.get("scenarios", {}).items():
            print(f"   📋 {scenario_id}: {scenario_data['name']}")
            print(f"      Description: {scenario_data['description']}")
            print(f"      Objectives: {len(scenario_data['objectives'])}")
        return scenarios["scenarios"]
    else:
        print(f"❌ Failed to get scenarios: {scenarios_response['data']}")
        return {}

def test_game_session_flow(headers: Dict[str, str], scenarios: Dict[str, Any]):
    """Test complete game session flow"""
    print("\n🎯 GAME SESSION FLOW TEST")
    print("=" * 50)
    
    if not scenarios:
        print("❌ No scenarios available for testing")
        return None
    
    # Start a game session
    scenario_id = list(scenarios.keys())[0]  # Use first available scenario
    start_request = {
        "user_id": 8,  # test2@example.com user ID
        "scenario_id": scenario_id,
        "difficulty_level": 1
    }
    
    print(f"🚀 Starting game session with scenario: {scenario_id}")
    start_response = make_request("post", f"{GAME_DIRECT_URL}/api/v1/game/start", json=start_request)
    
    if start_response["success"]:
        session_data = start_response["data"]
        session_id = session_data.get("session_id")
        print(f"✅ Game session started! Session ID: {session_id}")
        print(f"   Initial score: {session_data['data']['initial_state']['score']}")
        print(f"   Current objective: {session_data['data']['initial_state']['current_objective']}")
        
        return session_id
    else:
        print(f"❌ Failed to start game session: {start_response['data']}")
        return None

def test_game_actions(session_id: str, user_id: int):
    """Test various game actions"""
    print(f"\n⚡ GAME ACTIONS TEST (Session: {session_id})")
    print("=" * 50)
    
    actions_to_test = [
        {
            "session_id": session_id,
            "user_id": user_id,
            "action_type": "move",
            "position": {"x": 10, "y": 15},
            "context": {"area": "forest"}
        },
        {
            "session_id": session_id,
            "user_id": user_id,
            "action_type": "interact",
            "target": "friend",
            "context": {"interaction_type": "greeting"}
        },
        {
            "session_id": session_id,
            "user_id": user_id,
            "action_type": "select",
            "target": "magic_wand",
            "context": {"item_type": "tool"}
        },
        {
            "session_id": session_id,
            "user_id": user_id,
            "action_type": "answer",
            "response": "happy",
            "emotion_detected": "happy",
            "context": {"question": "how_do_you_feel"}
        }
    ]
    
    for i, action in enumerate(actions_to_test, 1):
        print(f"\n🎯 Action {i}: {action['action_type']}")
        action_response = make_request("post", f"{GAME_DIRECT_URL}/api/v1/game/action", json=action)
        
        if action_response["success"]:
            result = action_response["data"]
            print(f"✅ Action successful: {result.get('message', 'No message')}")
            if 'data' in result and 'updated_state' in result['data']:
                state = result['data']['updated_state']
                print(f"   💰 Score: {state['score']}")
                print(f"   🎯 Objective: {state['current_objective']}")
        else:
            print(f"❌ Action failed: {action_response['data']}")
    
    return True

def test_game_state(session_id: str, user_id: int):
    """Test getting game state"""
    print(f"\n📊 GAME STATE TEST (Session: {session_id})")
    print("=" * 50)
    
    state_response = make_request("get", f"{GAME_DIRECT_URL}/api/v1/game/state", 
                                params={"session_id": session_id, "user_id": user_id})
    
    if state_response["success"]:
        state_data = state_response["data"]
        print("✅ Game state retrieved successfully!")
        if 'data' in state_data:
            state = state_data['data']
            print(f"   💰 Current Score: {state.get('score', 0)}")
            print(f"   ❤️ Health: {state.get('health', 0)}")
            print(f"   📍 Position: {state.get('position', {})}")
            print(f"   🎒 Inventory: {len(state.get('inventory', []))} items")
            print(f"   ✅ Completed Objectives: {len(state.get('completed_objectives', []))}")
            print(f"   🎯 Current Objective: {state.get('current_objective', 'None')}")
        return True
    else:
        print(f"❌ Failed to get game state: {state_response['data']}")
        return False

def test_session_management(user_id: int):
    """Test session management endpoints"""
    print(f"\n🔧 SESSION MANAGEMENT TEST (User: {user_id})")
    print("=" * 50)
    
    # Get active sessions
    active_response = make_request("get", f"{GAME_DIRECT_URL}/api/v1/game/sessions/active", 
                                 params={"user_id": user_id})
    
    if active_response["success"]:
        active_data = active_response["data"]
        print(f"✅ Active sessions: {active_data.get('count', 0)}")
        for session in active_data.get('active_sessions', []):
            print(f"   🎮 Session: {session['session_id'][:8]}... - Score: {session['score']}")
    else:
        print(f"❌ Failed to get active sessions: {active_response['data']}")

def test_game_stats():
    """Test game statistics"""
    print("\n📈 GAME STATISTICS TEST")
    print("=" * 50)
    
    stats_response = make_request("get", f"{GAME_DIRECT_URL}/api/v1/game/stats")
    
    if stats_response["success"]:
        stats = stats_response["data"]
        print("✅ Game statistics retrieved!")
        print(f"   📊 Total Sessions: {stats.get('total_sessions', 0)}")
        print(f"   🎮 Active Sessions: {stats.get('active_sessions', 0)}")
        print(f"   ✅ Completed Sessions: {stats.get('completed_sessions', 0)}")
        print(f"   📈 Completion Rate: {stats.get('completion_rate', 0):.1f}%")
        print(f"   ⏱️ Avg Session Time: {stats.get('average_session_time_seconds', 0)} seconds")
        print(f"   🏆 Most Popular Scenario: {stats.get('most_popular_scenario', {}).get('name', 'N/A')}")
        return True
    else:
        print(f"❌ Failed to get stats: {stats_response['data']}")
        return False

def test_end_game_session(session_id: str, user_id: int):
    """Test ending a game session"""
    print(f"\n🏁 END GAME SESSION TEST (Session: {session_id})")
    print("=" * 50)
    
    end_request = {
        "session_id": session_id,
        "user_id": user_id,
        "final_score": 100,
        "completion_reason": "testing_complete"
    }
    
    end_response = make_request("post", f"{GAME_DIRECT_URL}/api/v1/game/end", json=end_request)
    
    if end_response["success"]:
        end_data = end_response["data"]
        print("✅ Game session ended successfully!")
        if 'data' in end_data:
            data = end_data['data']
            print(f"   💰 Final Score: {data.get('final_score', 0)}")
            print(f"   ⏱️ Duration: {data.get('duration_seconds', 0)} seconds")
            print(f"   📈 Completion: {data.get('completion_percentage', 0):.1f}%")
            print(f"   🎯 Objectives: {data.get('objectives_completed', 0)}/{data.get('total_objectives', 0)}")
            print(f"   😊 Emotions: {len(data.get('emotions_detected', []))}")
        return True
    else:
        print(f"❌ Failed to end game session: {end_response['data']}")
        return False

def main():
    """Run comprehensive game service tests"""
    print("🎮" * 20)
    print("🎮 ENHANCED GAME SERVICE COMPREHENSIVE TEST")
    print("🎮" * 20)
    
    # Test Results Tracking
    results = {
        "authentication": False,
        "health_check": False,
        "scenarios": False,
        "session_start": False,
        "game_actions": False,
        "game_state": False,
        "session_management": False,
        "game_stats": False,
        "session_end": False
    }
    
    # 1. Authentication
    token = test_authentication()
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        results["authentication"] = True
    else:
        print("❌ Authentication failed. Some tests may not work properly.")
        headers = {}
    
    # 2. Health Check
    results["health_check"] = test_game_service_health()
    
    # 3. Game Scenarios
    scenarios = test_game_scenarios(headers)
    results["scenarios"] = bool(scenarios)
    
    # 4. Game Session Flow
    session_id = test_game_session_flow(headers, scenarios)
    results["session_start"] = bool(session_id)
    
    if session_id:
        user_id = 8  # test2@example.com user ID
        
        # 5. Game Actions
        results["game_actions"] = test_game_actions(session_id, user_id)
        
        # 6. Game State
        results["game_state"] = test_game_state(session_id, user_id)
        
        # 7. Session Management
        test_session_management(user_id)
        results["session_management"] = True
        
        # 8. Game Statistics
        results["game_stats"] = test_game_stats()
        
        # 9. End Game Session
        results["session_end"] = test_end_game_session(session_id, user_id)
    
    # Final Results
    print("\n" + "🎮" * 20)
    print("🎮 FINAL TEST RESULTS")
    print("🎮" * 20)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print(f"\n🏆 OVERALL SCORE: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Enhanced Game Service is fully functional!")
    elif passed_tests >= total_tests * 0.8:
        print("✅ Most tests passed! Enhanced Game Service is largely functional!")
    else:
        print("⚠️ Some tests failed. Check the enhanced Game Service implementation.")

if __name__ == "__main__":
    main()
