import json

import requests

# Test authentication flow with an existing user
BASE_URL = "http://localhost:8000/api/v1"

def test_existing_user():
    print("=== TESTING WITH EXISTING USER ===")
    
    # Try to login with existing user
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"  # Assuming this is the password
    }
    
    print("1. Testing login with existing user...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token = login_response.json().get('token')
        print(f"   Login successful! Token: {token[:50]}...")
        
        # Test /me endpoint
        headers = {"Authorization": f"Bearer {token}"}
        print("2. Testing /me endpoint...")
        me_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"   Status: {me_response.status_code}")
        print(f"   Response: {me_response.text}")
    else:
        print(f"   Login failed: {login_response.text}")

if __name__ == "__main__":
    test_existing_user()
