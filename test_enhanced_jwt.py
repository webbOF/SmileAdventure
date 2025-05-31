#!/usr/bin/env python3

import json
import sys

import requests


def test_enhanced_jwt():
    """Test enhanced JWT authentication with user_id"""
    
    print("=== TESTING ENHANCED JWT AUTHENTICATION ===")
    
    # Step 1: Health check
    print("\n1. Checking services health...")
    try:
        auth_response = requests.get("http://localhost:8001/status", timeout=5)
        print(f"   Auth service: {auth_response.status_code}")
        
        gateway_response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"   API Gateway: {gateway_response.status_code}")
    except Exception as e:
        print(f"   Health check failed: {e}")
        return False
    
    # Step 2: Register a test user
    print("\n2. Registering test user...")
    register_data = {
        "name": "Enhanced JWT Test User",
        "email": "enhanced_jwt_test@example.com",
        "password": "password123",
        "role": "child"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/register", json=register_data, timeout=10)
        print(f"   Registration status: {response.status_code}")
        if response.status_code in [200, 201]:
            print("   ✅ Registration successful!")
        elif response.status_code == 400 and "already registered" in response.text:
            print("   ℹ️ User already exists, continuing...")
        else:
            print(f"   ❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"   Registration error: {e}")
    
    # Step 3: Login and get enhanced JWT token
    print("\n3. Login to get enhanced JWT token...")
    login_data = {
        "email": "enhanced_jwt_test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/login", json=login_data, timeout=10)
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result.get("access_token")
            user_info = login_result.get("user", {})
            
            print(f"   ✅ Login successful!")
            print(f"   User ID: {user_info.get('id')}")
            print(f"   User Name: {user_info.get('name')}")
            print(f"   User Role: {user_info.get('role')}")
            print(f"   Token received: {token[:50]}...")
            
            # Step 4: Test protected endpoint with enhanced token
            print("\n4. Testing protected endpoint with enhanced JWT...")
            headers = {"Authorization": f"Bearer {token}"}
            
            me_response = requests.get("http://localhost:8000/api/v1/me", headers=headers, timeout=10)
            print(f"   /me endpoint status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                me_data = me_response.json()
                print(f"   ✅ Protected endpoint accessible!")
                print(f"   Token email: {me_data.get('email')}")
                print(f"   Token user_id: {me_data.get('user_id')}")
                print(f"   Token role: {me_data.get('role')}")
                print(f"   Token name: {me_data.get('name')}")
                
                # Step 5: Test Game service with enhanced authentication
                print("\n5. Testing Game service with enhanced JWT...")
                game_start_data = {
                    "scenario_id": "basic_adventure",
                    "difficulty": "easy"
                }
                
                game_response = requests.post("http://localhost:8000/api/v1/game/start", 
                                            json=game_start_data, headers=headers, timeout=10)
                print(f"   Game start status: {game_response.status_code}")
                
                if game_response.status_code == 200:
                    game_result = game_response.json()
                    print(f"   ✅ Game service working with enhanced JWT!")
                    print(f"   Session ID: {game_result.get('session_id', 'N/A')}")
                    print(f"   User ID in game: {game_result.get('user_id', 'N/A')}")
                else:
                    print(f"   ⚠️ Game service issue: {game_response.text}")
                
                return True
            else:
                print(f"   ❌ Protected endpoint failed: {me_response.text}")
                return False
        else:
            print(f"   ❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Login error: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_jwt()
    print(f"\n=== TEST {'PASSED' if success else 'FAILED'} ===")
    sys.exit(0 if success else 1)
