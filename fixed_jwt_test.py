import base64
import json
import time

import requests


def decode_jwt_payload(token):
    """Decode JWT payload without verification for debugging"""
    try:
        # Split the token and get the payload part
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Add padding if needed
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        # Decode base64
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None

def test_enhanced_jwt_authentication():
    """Test the enhanced JWT authentication system with user_id in claims"""
    
    base_url = "http://localhost:8000"
    print("=== ENHANCED JWT AUTHENTICATION TEST ===")
    
    # Test 1: Registration
    print("\n1. USER REGISTRATION")
    register_data = {
        "name": "Enhanced Test User",
        "email": f"enhanced_test_{int(time.time())}@example.com",
        "password": "testpassword123",
        "role": "student"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/register", json=register_data, timeout=10)
        print(f"   Registration Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("   ✅ Registration successful!")
            test_email = register_data["email"]
        else:
            print(f"   ❌ Registration failed: {response.text}")
            # Use existing user for testing
            test_email = "test@example.com"
            
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        test_email = "test@example.com"
    
    # Test 2: Login
    print("\n2. USER LOGIN")
    login_data = {
        "email": test_email,
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data, timeout=10)
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            token = login_response.get("access_token")
            user_info = login_response.get("user", {})
            
            print("   ✅ Login successful!")
            print(f"   User ID: {user_info.get('id')}")
            print(f"   User Name: {user_info.get('name')}")
            print(f"   User Role: {user_info.get('role')}")
            
            # Decode JWT to check claims
            print("\n3. JWT TOKEN ANALYSIS")
            payload = decode_jwt_payload(token)
            if payload:
                print(f"   JWT Claims: {json.dumps(payload, indent=2)}")
                
                # Check if user_id is in claims
                if 'user_id' in payload:
                    print("   ✅ Enhanced JWT: user_id found in claims!")
                else:
                    print("   ⚠️  Standard JWT: user_id not in claims")
            
            # Test 3: Protected endpoint (/me)
            print("\n4. PROTECTED ENDPOINT TEST (/me)")
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(f"{base_url}/api/v1/users/me", headers=headers, timeout=10)
            print(f"   /me Status: {response.status_code}")
            
            if response.status_code == 200:
                profile = response.json()
                print("   ✅ Profile retrieval successful!")
                print(f"   Profile: {json.dumps(profile, indent=2)}")
            else:
                print(f"   ❌ Profile retrieval failed: {response.text}")
            
            # Test 4: Game service endpoint
            print("\n5. GAME SERVICE TEST")
            response = requests.get(f"{base_url}/api/v1/game/sessions", headers=headers, timeout=10)
            print(f"   Game sessions Status: {response.status_code}")
            
            if response.status_code == 200:
                sessions = response.json()
                print("   ✅ Game sessions retrieval successful!")
                print(f"   Sessions: {sessions}")
            else:
                print(f"   ⚠️  Game sessions: {response.text}")
                
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")

if __name__ == "__main__":
    test_enhanced_jwt_authentication()