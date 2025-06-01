import json
import time

import requests


def test_token_inspection():
    print('=== TOKEN INSPECTION TEST ===\n')
    
    base_url = 'http://localhost:8000/api/v1'
    
    # Register and login to get a token
    timestamp = str(int(time.time()))
    test_user = {
        'name': f'Test User {timestamp}',
        'username': f'testuser_{timestamp}',
        'email': f'test_{timestamp}@example.com',
        'password': 'testpassword123',
        'role': 'student'
    }
    
    print('1. Registering user...')
    response = requests.post(f'{base_url}/auth/register', json=test_user, timeout=10)
    print(f'   Registration Status: {response.status_code}')
    
    print('2. Logging in...')
    login_data = {'email': test_user['email'], 'password': test_user['password']}
    response = requests.post(f'{base_url}/auth/login', json=login_data, timeout=10)
    print(f'   Login Status: {response.status_code}')
    
    if response.status_code == 200:
        login_result = response.json()
        token = login_result.get('access_token')
        print(f'   Token received: {token[:30]}...')
        print(f'   Full login response: {json.dumps(login_result, indent=2)}')
        
        # Test token verification directly
        print('\n3. Testing token verification...')
        verify_data = {'token': token}
        try:
            # Test auth service verification directly
            response = requests.post(f'{base_url}/auth/verify-token', json=verify_data, timeout=10)
            print(f'   Token verification status: {response.status_code}')
            print(f'   Token verification response: {json.dumps(response.json(), indent=2)}')
        except Exception as e:
            print(f'   Token verification error: {e}')
        
        print('\n4. Testing protected endpoint with diagnostics...')
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{base_url}/users/me', headers=headers, timeout=10)
        print(f'   Profile access status: {response.status_code}')
        print(f'   Profile response: {response.text}')
    
    print('\n=== TOKEN INSPECTION COMPLETE ===')

if __name__ == "__main__":
    test_token_inspection()
