import json

import requests


def test_game_service():
    """Simple test of enhanced Game service"""
    print("🎮 Testing Enhanced Game Service...")
    
    base_url = "http://localhost:8005/api/v1/game"
    
    # Test 1: Get scenarios
    print("\n1. Testing scenarios endpoint...")
    try:
        response = requests.get(f"{base_url}/scenarios", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scenarios: {data['total_count']} available")
            for scenario_id, scenario in data['scenarios'].items():
                print(f"   - {scenario_id}: {scenario['name']}")
        else:
            print(f"❌ Scenarios failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Scenarios error: {e}")
    
    # Test 2: Start game session
    print("\n2. Testing start game session...")
    try:
        start_data = {
            "user_id": 8,
            "scenario_id": "basic_adventure",
            "difficulty_level": 1
        }
        response = requests.post(f"{base_url}/start", json=start_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print(f"✅ Game session started: {session_id}")
            return session_id
        else:
            print(f"❌ Start session failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Start session error: {e}")
    
    return None

def test_game_action(session_id):
    """Test game action"""
    print(f"\n3. Testing game action for session {session_id}...")
    
    base_url = "http://localhost:8005/api/v1/game"
    
    try:
        action_data = {
            "session_id": session_id,
            "user_id": 8,
            "action_type": "interact",
            "target": "friend"
        }
        response = requests.post(f"{base_url}/action", json=action_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Action processed: {data.get('message')}")
            if 'data' in data:
                score = data['data'].get('updated_state', {}).get('score', 0)
                print(f"   Current score: {score}")
        else:
            print(f"❌ Action failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Action error: {e}")

def test_game_stats():
    """Test game statistics"""
    print("\n4. Testing game statistics...")
    
    base_url = "http://localhost:8005/api/v1/game"
    
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats retrieved:")
            print(f"   Total sessions: {data.get('total_sessions', 0)}")
            print(f"   Active sessions: {data.get('active_sessions', 0)}")
            print(f"   Completion rate: {data.get('completion_rate', 0):.1f}%")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")

if __name__ == "__main__":
    session_id = test_game_service()
    if session_id:
        test_game_action(session_id)
    test_game_stats()
    print("\n🎉 Enhanced Game Service testing complete!")
