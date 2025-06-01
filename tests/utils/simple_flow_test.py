import json

import requests


def test_auth_flow():
    print("Testing authentication flow...")
    
    # Register
    register_url = "http://localhost:8000/api/v1/auth/register"
    register_data = {
        "email": "flow.test@example.com",
        "password": "TestPassword123!",
        "name": "Flow Test User",
        "role": "patient"
    }
    
    register_response = requests.post(register_url, json=register_data)
    print(f"Register: {register_response.status_code} - {register_response.text}")
    
    if register_response.status_code not in [200, 201]:
        return False
    
    # Login
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "email": "flow.test@example.com",
        "password": "TestPassword123!"
    }
    
    login_response = requests.post(login_url, json=login_data)
    print(f"Login: {login_response.status_code} - {login_response.text}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get("access_token")
        print(f"Token received: {token is not None}")
        
        # Test protected route
        user_id = register_response.json().get("user_id", 1)
        headers = {"Authorization": f"Bearer {token}"}
        users_url = f"http://localhost:8000/api/v1/users/{user_id}"
        
        users_response = requests.get(users_url, headers=headers)
        print(f"Protected route: {users_response.status_code} - {users_response.text}")
        
        return users_response.status_code == 200
    
    return False

if __name__ == "__main__":
    if test_auth_flow():
        print("SUCCESS: Complete flow working!")
    else:
        print("FAILED: Flow not working")
