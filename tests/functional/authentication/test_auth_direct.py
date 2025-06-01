#!/usr/bin/env python3

import requests
import json

def test_auth_direct():
    """Test auth service directly"""
    
    print("=== TESTING AUTH SERVICE DIRECTLY ===")
    
    # Test 1: Health check
    print("\n1. HEALTH CHECK")
    try:
        response = requests.get("http://localhost:8001/status", timeout=5)
        print(f"   Direct auth status: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Login directly
    print("\n2. DIRECT LOGIN")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
      try:
        response = requests.post("http://localhost:8001/api/v1/auth/login", json=login_data, timeout=5)
        print(f"   Direct login status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Direct login successful!")
        
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_auth_direct()
