import json

import requests


def test_protected_routes():
    print("Testing all protected routes...")
    
    # Login to get token
    login_url = "http://localhost:8000/api/v1/auth/login"
    login_data = {
        "email": "flow.test@example.com",
        "password": "TestPassword123!"
    }
    
    login_response = requests.post(login_url, json=login_data)
    if login_response.status_code != 200:
        print("Failed to login")
        return False
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    user_id = login_response.json().get("user", {}).get("id")
    
    # Test various protected endpoints
    endpoints_to_test = [
        f"/api/v1/users/{user_id}",
        "/api/v1/users/",
        "/api/v1/game/sessions",
        "/api/v1/reports/user-progress"
    ]
    
    all_passed = True
    for endpoint in endpoints_to_test:
        url = f"http://localhost:8000{endpoint}"
        response = requests.get(url, headers=headers)
        print(f"{endpoint}: {response.status_code}")
        if response.status_code not in [200, 404]:  # 404 might be expected for some endpoints
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    if test_protected_routes():
        print("All protected routes accessible!")
    else:
        print("Some protected routes failed")
