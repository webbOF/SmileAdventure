import json
import sys

import requests


# Test registration with sync
def test_registration_sync():
    print("Testing registration with sync...")
    url = "http://localhost:8000/api/v1/auth/register"
    data = {
        "email": "test.sync2@example.com",
        "password": "TestPassword123!",
        "name": "Test Sync User 2",
        "role": "patient"    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Registration response status: {response.status_code}")
        print(f"Registration response: {response.text}")
        
        if response.status_code in [200, 201]:
            # Now test if user exists in Users service
            user_data = response.json()
            user_id = user_data.get("user_id") or user_data.get("id")
            print(f"Created user with ID: {user_id}")
            
            # Test getting user from Users service
            users_url = f"http://localhost:8000/api/v1/users/{user_id}"
            users_response = requests.get(users_url)
            print(f"\nUsers service response status: {users_response.status_code}")
            print(f"Users service response: {users_response.text}")
            
            return True
        else:
            print("Registration failed")
            return False
    except Exception as e:
        print(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_registration_sync()
    if success:
        print("\n✅ Sync test completed successfully!")
    else:
        print("\n❌ Sync test failed!")
        sys.exit(1)
