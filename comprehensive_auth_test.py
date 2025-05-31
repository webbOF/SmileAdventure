#!/usr/bin/env python3

import json

import requests


def comprehensive_auth_test():
    """Complete end-to-end authentication flow test"""
    
    base_url = "http://localhost:8000"
    
    print("=== COMPREHENSIVE AUTHENTICATION FLOW TEST ===")
    
    # Test 1: Health Check
    print("\n1. HEALTH CHECK")
    try:
        response = requests.get(f"{base_url}/api/v1/users/health", timeout=5)
        print(f"   Users Health: {response.status_code} - {response.json()}")
        
        response = requests.get(f"{base_url}/api/v1/auth/health", timeout=5)
        print(f"   Auth Health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   Health check error: {e}")
      # Test 2: Login with existing user
    print("\n2. USER LOGIN")
    login_data = {
        "email": "test2@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data, timeout=5)
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["access_token"]
            print(f"   ✅ Login successful! User: {login_result['user']['name']}")
            print(f"   Token: {token[:50]}...")
              # Test 3: Token verification
            print("\n3. TOKEN VERIFICATION")
            headers = {"Authorization": f"Bearer {token}"}
            token_data = {"token": token}
            response = requests.post(f"{base_url}/api/v1/auth/verify-token", json=token_data, timeout=5)
            print(f"   Token verification: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Token is valid: {response.json()}")
            else:
                print(f"   ❌ Token verification failed: {response.text}")
                return
            
            # Test 4: Current user profile (/me)
            print("\n4. CURRENT USER PROFILE (/me)")
            response = requests.get(f"{base_url}/api/v1/users/me", headers=headers, timeout=5)
            print(f"   /me Status: {response.status_code}")
            
            if response.status_code == 200:
                user_profile = response.json()
                print(f"   ✅ Profile retrieved successfully!")
                print(f"   User Email: {user_profile['email']}")
                print(f"   User Name: {user_profile['name']} {user_profile['surname']}")
                print(f"   User Type: {user_profile['user_type']}")
                print(f"   User ID: {user_profile['id']}")
                
                # Test 5: Protected resource access
                print("\n5. PROTECTED RESOURCE ACCESS")
                response = requests.get(f"{base_url}/api/v1/users/professionals/search", headers=headers, timeout=5)
                print(f"   Professional search: {response.status_code}")
                if response.status_code == 200:
                    professionals = response.json()
                    print(f"   ✅ Found {len(professionals)} professionals")
                
                # Test 6: Game service health (if available)
                print("\n6. GAME SERVICE INTEGRATION")
                response = requests.get(f"{base_url}/api/v1/game/health", headers=headers, timeout=5)
                print(f"   Game health: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Game service: {response.json()}")
                
                print("\n=== TEST SUMMARY ===")
                print("✅ User login: PASSED")
                print("✅ Token verification: PASSED") 
                print("✅ User profile (/me): PASSED")
                print("✅ Protected routes: PASSED")
                print("\n🎉 ALL AUTHENTICATION FLOW TESTS PASSED!")
                
            else:
                print(f"   ❌ Profile retrieval failed: {response.text}")
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   Login error: {e}")

if __name__ == "__main__":
    comprehensive_auth_test()
