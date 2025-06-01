import json
import time

import requests


def test_auth_flow():
    print('=== JWT AUTHENTICATION FLOW TESTING ===\n')
    
    base_url = 'http://localhost:8000/api/v1'
    
    # Test 1: System Health Check
    print('1. Testing System Health...')
    try:
        response = requests.get(f'{base_url}/health', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            print(f'   Response: {response.json()}')
        else:
            print(f'   Response: {response.text}')
    except Exception as e:
        print(f'   ERROR: {e}')
    print()
      # Test 2: User Registration
    print('2. Testing User Registration...')
    timestamp = str(int(time.time()))
    test_user = {
        'name': f'Test User {timestamp}',
        'username': f'testuser_{timestamp}',
        'email': f'test_{timestamp}@example.com',
        'password': 'testpassword123',
        'role': 'student'
    }
    
    try:
        response = requests.post(f'{base_url}/auth/register', 
                               json=test_user, timeout=10)
        print(f'   Status: {response.status_code}')
        if response.status_code in [200, 201]:
            print(f'   Registration successful: {response.json()}')
        else:
            print(f'   Registration failed: {response.text}')
    except Exception as e:
        print(f'   ERROR: {e}')
    print()
    
    # Test 3: User Login
    print('3. Testing User Login...')
    login_data = {
        'email': test_user['email'],
        'password': test_user['password']
    }
    
    token = None
    try:
        response = requests.post(f'{base_url}/auth/login', 
                               json=login_data, timeout=10)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            if token:
                print(f'   Login successful! Token: {token[:30]}...')
            else:
                print(f'   Login response: {result}')
        else:
            print(f'   Login failed: {response.text}')
    except Exception as e:
        print(f'   ERROR: {e}')
    print()
      # Test 4: Protected Route Access
    if token:
        print('4. Testing Protected Route Access...')
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            response = requests.get(f'{base_url}/users/me', 
                                  headers=headers, timeout=10)
            print(f'   User Profile Status: {response.status_code}')
            if response.status_code == 200:
                print(f'   Profile: {response.json()}')
            else:
                print(f'   Response: {response.text}')
        except Exception as e:
            print(f'   ERROR: {e}')
    else:
        print('4. SKIPPED: No token available')
    print()
    
    # Test 5: Game Service Integration
    if token:
        print('5. Testing Game Service Integration...')
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            response = requests.get(f'{base_url}/game/health', 
                                  headers=headers, timeout=10)
            print(f'   Game Health Status: {response.status_code}')
            if response.status_code == 200:
                print(f'   Game Health: {response.json()}')
            else:
                print(f'   Response: {response.text}')
        except Exception as e:
            print(f'   ERROR: {e}')
        
        # Test game session start
        try:
            game_data = {'game_type': 'memory', 'difficulty': 'easy'}
            response = requests.post(f'{base_url}/game/start', 
                                   json=game_data, headers=headers, timeout=10)
            print(f'   Game Start Status: {response.status_code}')
            if response.status_code in [200, 201]:
                print(f'   Game Session: {response.json()}')
            else:
                print(f'   Game Start Response: {response.text}')
        except Exception as e:
            print(f'   ERROR starting game: {e}')
    else:
        print('5. SKIPPED: No token available')
    print()
    
    # Test 6: Invalid Token Handling
    print('6. Testing Invalid Token Handling...')
    invalid_headers = {'Authorization': 'Bearer invalid_token_here'}
    try:
        response = requests.get(f'{base_url}/users/me', 
                              headers=invalid_headers, timeout=10)
        print(f'   Status with invalid token: {response.status_code}')
        print(f'   Response: {response.text}')
    except Exception as e:
        print(f'   ERROR: {e}')
    print()
    
    print('=== TESTING COMPLETE ===')

if __name__ == "__main__":
    test_auth_flow()
