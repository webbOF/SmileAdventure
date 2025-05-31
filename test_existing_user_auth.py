import json

import requests

# Test authentication flow with an existing user
BASE_URL = "http://localhost:8000/api/v1"

def test_with_test_user():
    print("=== TESTING WITH EXISTING USER (test@example.com) ===")
    
    # Try to login with existing user
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"  # Common test password
    }
    
    print("1. Testing login with existing user...")
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        print(f"   Login Status: {login_response.status_code}")
        print(f"   Login Response: {login_response.text}")
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            print(f"   Login successful! Token: {token[:50] if token else 'NO TOKEN'}...")
            
            # Test /me endpoint
            headers = {"Authorization": f"Bearer {token}"}
            print("2. Testing /me endpoint...")
            me_response = requests.get(f"{BASE_URL}/users/me", headers=headers, timeout=10)
            print(f"   /me Status: {me_response.status_code}")
            print(f"   /me Response: {me_response.text}")
        else:
            print(f"   Login failed: {login_response.text}")
            
            # Try different passwords
            common_passwords = ["password", "123456", "test123", "admin", "test"]
            print("   Trying common passwords...")
            for pwd in common_passwords:
                try:
                    test_login = {"email": "test@example.com", "password": pwd}
                    resp = requests.post(f"{BASE_URL}/auth/login", json=test_login, timeout=5)
                    if resp.status_code == 200:
                        print(f"   ✅ Found working password: {pwd}")
                        token = resp.json().get('access_token')
                        if token:
                            headers = {"Authorization": f"Bearer {token}"}
                            me_resp = requests.get(f"{BASE_URL}/users/me", headers=headers, timeout=5)
                            print(f"   /me with correct password: {me_resp.status_code} - {me_resp.text}")
                        break
                    else:
                        print(f"   ❌ Password '{pwd}' failed: {resp.status_code}")
                except Exception as e:
                    print(f"   ❌ Error with password '{pwd}': {e}")
                    
    except Exception as e:
        print(f"   Error during login: {e}")

if __name__ == "__main__":
    test_with_test_user()
