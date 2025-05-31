import json
import time

import jwt
import requests

print('Debug user profile access issue...')

timestamp = int(time.time())
registration_data = {
    'name': 'Profile Debug User',
    'email': f'profile_debug_{timestamp}@test.com',
    'password': 'TestPass123!',
    'role': 'student'
}

try:
    # Register and login
    register_response = requests.post('http://localhost:8000/api/v1/auth/register', json=registration_data, timeout=10)
    print(f'Register: {register_response.status_code}')
    
    login_response = requests.post('http://localhost:8000/api/v1/auth/login', json={'email': registration_data['email'], 'password': registration_data['password']}, timeout=10)
    print(f'Login: {login_response.status_code}')
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data['access_token']
        
        # Decode JWT
        decoded = jwt.decode(token, options={'verify_signature': False})
        user_id = decoded.get('user_id')
        sub = decoded.get('sub')
        print(f'JWT user_id: {user_id}')
        print(f'JWT sub: {sub}')
        
        # Test different profile endpoints
        headers = {'Authorization': f'Bearer {token}'}
        
        endpoints_to_try = [
            '/api/v1/users/me',
            f'/api/v1/users/{user_id}',
            '/api/v1/users/profile'
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(f'http://localhost:8000{endpoint}', headers=headers, timeout=10)
                print(f'{endpoint}: {response.status_code}')
                if response.status_code == 200:
                    data = response.json()
                    print(f'  Success: {data.get("name", "No name")}')
                elif response.status_code != 200:
                    print(f'  Error: {response.text[:100]}')
            except Exception as e:
                print(f'{endpoint}: ERROR - {e}')
        
        # Also test session listing
        session_response = requests.get('http://localhost:8000/api/v1/game/sessions', headers=headers, timeout=10)
        print(f'Sessions: {session_response.status_code}')
        if session_response.status_code != 200:
            print(f'  Sessions error: {session_response.text[:100]}')
    
except Exception as e:
    print(f'Error: {e}')
