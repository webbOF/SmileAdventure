#!/usr/bin/env python3
"""
Debug script to investigate POST endpoint 500 errors in Users service
"""
import json
import sys

import requests


def test_user_creation():
    """Test POST /api/v1/users endpoint with detailed error reporting"""
    print("=== Testing POST /api/v1/users endpoint ===")
    
    data = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
        'user_type': 'patient'
    }
    
    try:
        response = requests.post('http://localhost:8006/api/v1/users', json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        print(f"Response JSON (if valid): ", end="")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print("Not valid JSON")
    except Exception as e:
        print(f"Request Error: {e}")

def test_professional_creation():
    """Test POST /api/v1/professionals endpoint"""
    print("\n=== Testing POST /api/v1/professionals endpoint ===")
    
    data = {
        'email': 'doctor@example.com',
        'password': 'doctorpass123',
        'first_name': 'Dr. Jane',
        'last_name': 'Smith',
        'user_type': 'professional',
        'license_number': 'LIC123456',
        'years_of_experience': 10,
        'specialties': [1]  # Assuming specialty ID 1 exists
    }
    
    try:
        response = requests.post('http://localhost:8006/api/v1/professionals', json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        print(f"Response JSON (if valid): ", end="")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print("Not valid JSON")
    except Exception as e:
        print(f"Request Error: {e}")

def test_professional_search():
    """Test GET /api/v1/professionals endpoint"""
    print("\n=== Testing GET /api/v1/professionals endpoint ===")
    
    try:
        response = requests.get('http://localhost:8006/api/v1/professionals', timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        print(f"Response JSON (if valid): ", end="")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print("Not valid JSON")
    except Exception as e:
        print(f"Request Error: {e}")

def test_health_records():
    """Test health records endpoints"""
    print("\n=== Testing GET /api/v1/health-records endpoint ===")
    
    try:
        response = requests.get('http://localhost:8006/api/v1/health-records', timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        print(f"Response JSON (if valid): ", end="")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print("Not valid JSON")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    print("Users Service POST Endpoints Debug Script")
    print("=" * 50)
    
    test_user_creation()
    test_professional_creation()
    test_professional_search()
    test_health_records()
    
    print("\n" + "=" * 50)
    print("Debug complete. Check server logs for more details.")
