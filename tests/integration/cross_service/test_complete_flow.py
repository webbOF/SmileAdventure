import json
import sys

import requests


def test_complete_auth_flow():
    print("Testing complete authentication flow...")
    
    # Step 1: Register a user
    print("\n1. Testing registration...")
    register_url = "http://localhost:8000/api/v1/auth/register"
    register_data = {
        "email": "complete.test@example.com",
        "password": "TestPassword123!",
        "name": "Complete Test User",
        "role": "patient"
    }
    
    try:
        register_response = requests.post(register_url, json=register_data)
        print(f"Registration status: {register_response.status_code}")
        print(f"Registration response: {register_response.text}")
        
        if register_response.status_code not in [200, 201]:
            print("❌ Registration failed")
            return False
        
        user_data = register_response.json()
        user_id = user_data.get("user_id") or user_data.get("id")
        print(f"✅ User registered with ID: {user_id}")
        
        # Step 2: Login to get JWT token
        print("\n2. Testing login...")
        login_url = "http://localhost:8000/api/v1/auth/login"
        login_data = {
            "email": "complete.test@example.com",
            "password": "TestPassword123!"
        }
        
        login_response = requests.post(login_url, json=login_data)
        print(f"Login status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return False
        
        login_result = login_response.json()
        token = login_result.get("access_token")
        if not token:
            print("❌ No access token received")
            return False
        
        print(f"✅ Login successful, token received")
        
        # Step 3: Test authenticated access to Users service
        print("\n3. Testing authenticated access to Users service...")
        headers = {"Authorization": f"Bearer {token}"}
        users_url = f"http://localhost:8000/api/v1/users/{user_id}"
        
        users_response = requests.get(users_url, headers=headers)
        print(f"Users service status: {users_response.status_code}")
        print(f"Users service response: {users_response.text}")
        
        if users_response.status_code == 200:
            print("✅ Authenticated access to Users service successful!")
            print("✅ User synchronization between Auth and Users services working!")
            return True
        else:
            print("❌ Authenticated access to Users service failed")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_auth_flow()
    if success:
        print("\n🎉 Complete authentication flow test PASSED!")
        print("✅ Registration works")
        print("✅ User synchronization works") 
        print("✅ Login works")
        print("✅ JWT authentication works")
        print("✅ Protected routes work")
    else:
        print("\n❌ Complete authentication flow test FAILED!")
        sys.exit(1)
