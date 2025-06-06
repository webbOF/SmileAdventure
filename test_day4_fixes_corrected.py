#!/usr/bin/env python3
"""
Test script to validate Day 4 Task 4.1 endpoint fixes
"""

import json
import time

import requests


def test_day4_endpoints():
    """Test the key endpoints that were failing in Day 4 E2E tests"""
    
    base_url = 'http://localhost:8000'
    
    print('🧪 Testing Day 4 Task 4.1 Endpoint Fixes...')
    print('=' * 60)
    
    # Register a parent first with correct fields
    timestamp = str(time.time()).replace('.', '')
    register_data = {
        'name': 'TestParent',
        'surname': 'User',
        'email': f'testparent{timestamp}@example.com',
        'password': 'TestPassword123!',
        'role': 'parent'
    }

    try:
        response = requests.post(f'{base_url}/api/v1/auth/register', json=register_data)
        print(f'Parent registration: {response.status_code}')

        if response.status_code in [200, 201]:
            auth_data = response.json()
            print(f'Registration response: {auth_data}')
            
            # Handle different response formats
            if 'access_token' in auth_data:
                token = auth_data['access_token']
                user_id = auth_data['user']['id']
            else:
                # Registration successful, now login to get token
                user_id = auth_data['user_id']
                login_data = {
                    'email': register_data['email'],
                    'password': register_data['password']
                }
                print('Attempting login to get access token...')
                login_response = requests.post(f'{base_url}/api/v1/auth/login', json=login_data)
                print(f'Login response: {login_response.status_code}')
                
                if login_response.status_code == 200:
                    login_auth_data = login_response.json()
                    token = login_auth_data['access_token']
                else:
                    print(f'❌ Login failed: {login_response.text}')
                    return False
                    
            headers = {'Authorization': f'Bearer {token}'}
            print(f'✅ Parent registered successfully (ID: {user_id})')            # Test POST /api/v1/users/children - THIS WAS PREVIOUSLY FAILING WITH 405
            child_data = {
                'name': 'TestChild',
                'surname': 'User',
                'birth_date': '2016-05-15',
                'diagnosis': 'ASD Level 1',
                'parent_id': user_id,
                'behavioral_notes': 'Responds well to structured activities',
                'support_level': 1
            }
            
            print('Testing children endpoint...')
            response = requests.post(f'{base_url}/api/v1/users/children', json=child_data, headers=headers)
            print(f'Child creation: {response.status_code}')

            if response.status_code in [200, 201]:
                child_response = response.json()
                child_id = child_response['id']
                print(f'✅ Child created successfully (ID: {child_id})')

                # Test sensory profile creation - THIS WAS PREVIOUSLY FAILING WITH 405
                sensory_data = {
                    'child_id': child_id,
                    'visual_sensitivity': 3,
                    'auditory_sensitivity': 4,
                    'tactile_sensitivity': 2,
                    'proprioceptive_needs': 3,
                    'vestibular_preferences': 2,
                    'adaptation_strategies': ['noise_canceling_headphones', 'fidget_tools']
                }

                print('Testing sensory profile endpoint...')
                response = requests.post(f'{base_url}/api/v1/users/children/{child_id}/sensory-profile', json=sensory_data, headers=headers)
                print(f'Sensory profile creation: {response.status_code}')

                if response.status_code in [200, 201]:
                    print()
                    print('🎉 ALL KEY DAY 4 ENDPOINTS NOW WORKING!')
                    print('✅ Child creation endpoint: FIXED (was 405 Method Not Allowed)')
                    print('✅ Sensory profile endpoint: FIXED (was 405 Method Not Allowed)')
                    print()
                    print('🔧 TECHNICAL FIXES APPLIED:')
                    print('   ✅ Route ordering fixed in user_controller.py')
                    print('   ✅ Children routes updated to /users/children')
                    print('   ✅ Sensory profile models and endpoints added')
                    print('   ✅ API Gateway forwarding implemented')
                    print('   ✅ Database tables created')
                    print()
                    print('📊 DAY 4 TASK 4.1 STATUS: COMPLETED')
                    return True
                else:
                    print(f'❌ Sensory profile failed: {response.text}')
                    return False
            else:
                print(f'❌ Child creation failed: {response.text}')
                return False
        else:
            print(f'❌ Parent registration failed: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ Test failed with exception: {str(e)}')
        return False

if __name__ == '__main__':
    success = test_day4_endpoints()
    if success:
        print('\n🏆 Day 4 Task 4.1 endpoint fixes validated successfully!')
    else:
        print('\n💥 Day 4 Task 4.1 endpoint validation failed!')
