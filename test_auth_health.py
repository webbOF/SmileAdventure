#!/usr/bin/env python3

import requests


def test_auth_endpoints():
    """Test auth service endpoints directly"""
    
    print("=== TESTING AUTH SERVICE ENDPOINTS ===")
    
    # Test direct auth service
    print("\n1. DIRECT AUTH SERVICE STATUS")
    try:
        response = requests.get("http://localhost:8001/status", timeout=5)
        print(f"   Direct /status: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   Direct status error: {e}")
    
    # Test through API Gateway
    print("\n2. AUTH HEALTH THROUGH API GATEWAY")
    try:
        response = requests.get("http://localhost:8000/api/v1/auth/health", timeout=5)
        print(f"   Gateway health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   Gateway health error: {e}")
    
    # Test login directly on auth service
    print("\n3. DIRECT AUTH LOGIN")
    login_data = {"email": "test@example.com", "password": "password123"}
    try:
        response = requests.post("http://localhost:8001/api/v1/auth/login", json=login_data, timeout=5)
        print(f"   Direct login: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Direct login error: {e}")

if __name__ == "__main__":
    test_auth_endpoints()
