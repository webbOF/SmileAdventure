#!/usr/bin/env python3
import json

import requests


# Test with an existing user
def test_with_existing_user():
    print("=== Testing with existing user ===")
    
    # Use an existing user's credentials
    login_data = {
        "email": "test.professional1@example.com",
        "password": "password123"
    }
    
    # Login
    print("1. Attempting login...")
    login_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
    print(f"   Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token = login_response.json().get('access_token')
        print(f"   Token obtained: {token[:50]}...")
        
        # Test /me endpoint
        print("2. Testing /me endpoint...")
        headers = {'Authorization': f'Bearer {token}'}
        me_response = requests.get('http://localhost:8000/api/v1/users/me', headers=headers)
        print(f"   /me Status: {me_response.status_code}")
        print(f"   /me Response: {me_response.text}")
        
        # Test direct users service call
        print("3. Testing direct users service...")
        email = "test.professional1@example.com"
        direct_response = requests.get(f'http://localhost:8006/api/v1/users?email={email}')
        print(f"   Direct Status: {direct_response.status_code}")
        if direct_response.status_code == 200:
            users = direct_response.json()
            print(f"   Found {len(users)} users")
            if users:
                print(f"   First user: {users[0]}")
    else:
        print(f"   Login failed: {login_response.text}")

if __name__ == "__main__":
    test_with_existing_user()
