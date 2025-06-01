import json
import time

import requests

print('=== COMPREHENSIVE JWT AUTHENTICATION FLOW TESTING ===\n')

# Test 1: Authentication Service Health
print('1. Testing Auth Service Health...')
try:
    response = requests.get('http://localhost:8000/auth/health', timeout=5)
    print(f'   Status: {response.status_code}')
    print(f'   Response: {response.json()}\n')
except Exception as e:
    print(f'   ERROR: {e}\n')

# Test 2: User Registration
print('2. Testing User Registration...')
test_user = {
    'username': 'testuser_flow_' + str(int(time.time())),
    'email': f'testflow{int(time.time())}@example.com',
    'password': 'testpassword123'
}
try:
    response = requests.post('http://localhost:8000/auth/register', 
                           json=test_user, timeout=10)
    print(f'   Status: {response.status_code}')
    if response.status_code == 201:
        print(f'   User registered successfully: {response.json()}')
    else:
        print(f'   Response: {response.text}')
    print()
except Exception as e:
    print(f'   ERROR: {e}\n')

# Test 3: User Login and Token Generation
print('3. Testing User Login and JWT Token Generation...')
login_data = {
    'username': test_user['username'],
    'password': test_user['password']
}
token = None
try:
    response = requests.post('http://localhost:8000/auth/login', 
                           json=login_data, timeout=10)
    print(f'   Status: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        token = result.get('access_token')
        print(f'   Login successful! Token received: {token[:50]}...')
        print(f'   Token type: {result.get("token_type")}')
    else:
        print(f'   Login failed: {response.text}')
    print()
except Exception as e:
    print(f'   ERROR: {e}\n')

# Test 4: Protected Route Access with JWT
if token:
    print('4. Testing Protected Route Access with JWT Token...')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test user profile access
    try:
        response = requests.get('http://localhost:8000/users/profile', 
                              headers=headers, timeout=10)
        print(f'   User Profile Status: {response.status_code}')
        if response.status_code == 200:
            print(f'   Profile data: {response.json()}')
        else:
            print(f'   Response: {response.text}')
        print()
    except Exception as e:
        print(f'   ERROR accessing profile: {e}\n')
    
    # Test game session start
    try:
        response = requests.post('http://localhost:8000/game/start', 
                               headers=headers, timeout=10)
        print(f'   Game Start Status: {response.status_code}')
        if response.status_code in [200, 201]:
            print(f'   Game session: {response.json()}')
        else:
            print(f'   Response: {response.text}')
        print()
    except Exception as e:
        print(f'   ERROR starting game: {e}\n')
        
    # Test reports access
    try:
        response = requests.get('http://localhost:8000/reports/health', 
                              headers=headers, timeout=10)
        print(f'   Reports Health Status: {response.status_code}')
        if response.status_code == 200:
            print(f'   Reports health: {response.json()}')
        else:
            print(f'   Response: {response.text}')
        print()
    except Exception as e:
        print(f'   ERROR accessing reports: {e}\n')
else:
    print('4. SKIPPED: No token available for protected route testing\n')

# Test 5: Invalid Token Handling
print('5. Testing Invalid Token Handling...')
invalid_headers = {'Authorization': 'Bearer invalid_token_here'}
try:
    response = requests.get('http://localhost:8000/users/profile', 
                          headers=invalid_headers, timeout=10)
    print(f'   Status with invalid token: {response.status_code}')
    print(f'   Response: {response.text}')
    print()
except Exception as e:
    print(f'   ERROR: {e}\n')

# Test 6: No Token Handling
print('6. Testing Access Without Token...')
try:
    response = requests.get('http://localhost:8000/users/profile', timeout=10)
    print(f'   Status without token: {response.status_code}')
    print(f'   Response: {response.text}')
    print()
except Exception as e:
    print(f'   ERROR: {e}\n')

print('=== JWT AUTHENTICATION FLOW TESTING COMPLETE ===')
