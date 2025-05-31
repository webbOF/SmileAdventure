#!/usr/bin/env python3

import json

import requests


def check_users():
    """Check what users exist in both Auth and Users services"""
    
    print("=== CHECKING USERS IN SERVICES ===")
    
    # Check Users service
    print("\n1. USERS IN USERS SERVICE:")
    try:
        response = requests.get("http://localhost:8006/api/v1/users/", timeout=5)
        if response.status_code == 200:
            users = response.json()
            print(f"   Found {len(users)} users:")
            for user in users:
                print(f"   - Email: {user.get('email')}, Name: {user.get('name')} {user.get('surname')}, Type: {user.get('user_type')}")
        else:
            print(f"   Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Error connecting to Users service: {e}")
    
    # Check if specific user exists
    print(f"\n2. SEARCHING FOR 'test2@example.com' IN USERS SERVICE:")
    try:
        response = requests.get("http://localhost:8006/api/v1/users/?email=test2@example.com", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Try to login to see what auth service knows
    print(f"\n3. TESTING LOGIN WITH 'test2@example.com':")
    try:
        login_data = {
            "email": "test2@example.com",
            "password": "password123"
        }
        response = requests.post("http://localhost:8001/api/v1/auth/login", json=login_data, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    check_users()
