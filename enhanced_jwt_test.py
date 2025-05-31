#!/usr/bin/env python3
"""
Enhanced JWT Authentication Test with User ID Claims
Tests the new JWT token structure that includes user_id in the token payload
"""

import json
import os
import time
from datetime import datetime

import requests
from jose import jwt

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
AUTH_BASE_URL = "http://localhost:8001/api/v1"

# Test user credentials
TEST_USER = {
    "name": "Enhanced JWT Tester",
    "email": "jwt.tester@enhanced.com",
    "password": "SecurePassword123!",
    "role": "parent"
}

def print_separator(title):
    """Print a formatted separator"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def decode_jwt_token(token):
    """Decode JWT token without verification (for testing purposes)"""
    try:
        # Note: This is for testing only - don't do this in production without verification
        decoded = jwt.get_unverified_claims(token)
        return decoded
    except Exception as e:
        print_error(f"Failed to decode JWT token: {e}")
        return None

def test_enhanced_authentication():
    """Test the enhanced authentication flow with user_id in JWT"""
    print_separator("Enhanced JWT Authentication Test")
    
    # Step 1: Register user
    print_info("Step 1: Registering test user...")
    try:
        register_response = requests.post(
            f"{AUTH_BASE_URL}/auth/register",
            json=TEST_USER,
            timeout=10
        )
        
        if register_response.status_code in [200, 201]:
            reg_data = register_response.json()
            if reg_data.get("status") == "success":
                print_success("User registered successfully")
            else:
                print_error(f"Registration failed: {reg_data}")
                return False
        elif register_response.status_code == 400 and "already registered" in register_response.text:
            print_info("User already exists, proceeding with login...")
        else:
            print_error(f"Registration failed: {register_response.status_code} - {register_response.text}")
            return False
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False
    
    # Step 2: Login and get enhanced JWT token
    print_info("Step 2: Logging in to get enhanced JWT token...")
    try:
        login_response = requests.post(
            f"{AUTH_BASE_URL}/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            timeout=10
        )
        
        if login_response.status_code != 200:
            print_error(f"Login failed: {login_response.status_code} - {login_response.text}")
            return False
        
        login_data = login_response.json()
        token = login_data["access_token"]
        user_data = login_data["user"]
        
        print_success("Login successful")
        print_info(f"User ID: {user_data['id']}")
        print_info(f"User Name: {user_data['name']}")
        print_info(f"User Role: {user_data['role']}")
        
        # Step 3: Decode and analyze JWT token
        print_info("Step 3: Analyzing JWT token structure...")
        decoded_token = decode_jwt_token(token)
        
        if decoded_token:
            print_success("JWT token decoded successfully")
            print_info("Token payload:")
            for key, value in decoded_token.items():
                if key != 'exp':  # Don't print expiration timestamp (not human readable)
                    print_info(f"  {key}: {value}")
            
            # Verify enhanced claims
            required_claims = ['sub', 'user_id', 'role', 'name']
            missing_claims = [claim for claim in required_claims if claim not in decoded_token]
            
            if not missing_claims:
                print_success("All required claims present in JWT token")
                
                # Verify user_id matches
                if decoded_token.get('user_id') == user_data['id']:
                    print_success("User ID in token matches login response")
                else:
                    print_error("User ID mismatch between token and login response")
                    return False
            else:
                print_error(f"Missing required claims: {missing_claims}")
                return False
        else:
            print_error("Failed to decode JWT token")
            return False
        
        return token, user_data
        
    except Exception as e:
        print_error(f"Login error: {e}")
        return False

def test_protected_endpoints(token, user_data):
    """Test protected endpoints with enhanced JWT"""
    print_separator("Protected Endpoints Test with Enhanced JWT")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: /me endpoint
    print_info("Test 1: Testing /me endpoint...")
    try:
        me_response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers, timeout=10)
        
        if me_response.status_code == 200:
            me_data = me_response.json()
            print_success("/me endpoint working")
            print_info(f"Retrieved user: {me_data.get('name')} (ID: {me_data.get('id')})")
            
            # Verify data consistency
            if me_data.get('id') == user_data['id']:
                print_success("User data consistency verified")
            else:
                print_error("User data inconsistency detected")
        else:
            print_error(f"/me endpoint failed: {me_response.status_code}")
    except Exception as e:
        print_error(f"/me endpoint error: {e}")
    
    # Test 2: Game scenarios endpoint (no auth required)
    print_info("Test 2: Testing game scenarios endpoint...")
    try:
        scenarios_response = requests.get(f"{API_BASE_URL}/game/scenarios", timeout=10)
        
        if scenarios_response.status_code == 200:
            scenarios_data = scenarios_response.json()
            print_success("Game scenarios endpoint working")
            print_info(f"Available scenarios: {len(scenarios_data.get('scenarios', []))}")
        else:
            print_error(f"Game scenarios failed: {scenarios_response.status_code}")
    except Exception as e:
        print_error(f"Game scenarios error: {e}")
    
    # Test 3: Active sessions endpoint (requires auth)
    print_info("Test 3: Testing active sessions endpoint...")
    try:
        sessions_response = requests.get(
            f"{API_BASE_URL}/game/sessions/active", 
            headers=headers, 
            timeout=10
        )
        
        if sessions_response.status_code == 200:
            sessions_data = sessions_response.json()
            print_success("Active sessions endpoint working")
            print_info(f"Active sessions: {sessions_data.get('count', 0)}")
        else:
            print_error(f"Active sessions failed: {sessions_response.status_code}")
    except Exception as e:
        print_error(f"Active sessions error: {e}")
    
    # Test 4: Game stats endpoint (requires auth)
    print_info("Test 4: Testing game statistics endpoint...")
    try:
        stats_response = requests.get(
            f"{API_BASE_URL}/game/stats", 
            headers=headers, 
            timeout=10
        )
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print_success("Game statistics endpoint working")
            print_info(f"Total sessions: {stats_data.get('total_sessions', 0)}")
            print_info(f"Active sessions: {stats_data.get('active_sessions', 0)}")
        else:
            print_error(f"Game statistics failed: {stats_response.status_code}")
    except Exception as e:
        print_error(f"Game statistics error: {e}")

def test_token_refresh(token):
    """Test token refresh functionality"""
    print_separator("Token Refresh Test")
    
    print_info("Testing token refresh...")
    try:
        refresh_response = requests.post(
            f"{AUTH_BASE_URL}/auth/refresh",
            json={"token": token},
            timeout=10
        )
        
        if refresh_response.status_code == 200:
            new_token = refresh_response.json()
            print_success("Token refresh successful")
            
            # Decode new token
            decoded_new_token = decode_jwt_token(new_token)
            if decoded_new_token:
                print_success("New token decoded successfully")
                print_info("New token contains user_id: " + str('user_id' in decoded_new_token))
                return new_token
            else:
                print_error("Failed to decode refreshed token")
        else:
            print_error(f"Token refresh failed: {refresh_response.status_code}")
    except Exception as e:
        print_error(f"Token refresh error: {e}")
    
    return None

def test_game_session_flow(token):
    """Test complete game session flow with enhanced JWT"""
    print_separator("Game Session Flow Test with Enhanced JWT")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start a game session
    print_info("Starting a new game session...")
    try:
        start_data = {
            "scenario_id": "basic_adventure",
            "player_name": "Enhanced JWT Tester"
        }
        
        start_response = requests.post(
            f"{API_BASE_URL}/game/start",
            headers=headers,
            json=start_data,
            timeout=10
        )
        
        if start_response.status_code == 200:
            session_data = start_response.json()
            print_success("Game session started successfully")
            session_id = session_data.get('session_id')
            print_info(f"Session ID: {session_id}")
            
            # Test game action
            print_info("Processing a game action...")
            action_data = {
                "session_id": session_id,
                "action_type": "MOVE",
                "target": "garden",
                "position": {"x": 10, "y": 20}
            }
            
            action_response = requests.post(
                f"{API_BASE_URL}/game/action",
                headers=headers,
                json=action_data,
                timeout=10
            )
            
            if action_response.status_code == 200:
                print_success("Game action processed successfully")
                action_result = action_response.json()
                print_info(f"Score: {action_result.get('score', 0)}")
            else:
                print_error(f"Game action failed: {action_response.status_code}")
            
            # Get game state
            print_info("Getting game state...")
            state_response = requests.get(
                f"{API_BASE_URL}/game/state",
                headers=headers,
                params={"session_id": session_id},
                timeout=10
            )
            
            if state_response.status_code == 200:
                print_success("Game state retrieved successfully")
                state_data = state_response.json()
                print_info(f"Current level: {state_data.get('current_level', 1)}")
            else:
                print_error(f"Game state failed: {state_response.status_code}")
            
            return session_id
        else:
            print_error(f"Game session start failed: {start_response.status_code}")
    except Exception as e:
        print_error(f"Game session flow error: {e}")
    
    return None

def main():
    """Main test function"""
    print_separator("SmileAdventure Enhanced JWT Authentication System Test")
    print_info(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"API Gateway: {API_BASE_URL}")
    print_info(f"Auth Service: {AUTH_BASE_URL}")
    
    # Test enhanced authentication
    auth_result = test_enhanced_authentication()
    if not auth_result:
        print_error("Authentication test failed. Stopping tests.")
        return
    
    token, user_data = auth_result
    
    # Test protected endpoints
    test_protected_endpoints(token, user_data)
    
    # Test token refresh
    refreshed_token = test_token_refresh(token)
    
    # Test game session flow
    if refreshed_token:
        test_game_session_flow(refreshed_token)
    else:
        test_game_session_flow(token)
    
    print_separator("Enhanced JWT Test Completed")
    print_success("All enhanced JWT authentication tests completed!")

if __name__ == "__main__":
    main()
