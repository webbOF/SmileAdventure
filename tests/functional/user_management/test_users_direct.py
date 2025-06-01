#!/usr/bin/env python3

import json

import requests


def test_users_service():
    print("=== TESTING USERS SERVICE DIRECTLY ===")
    
    # Test getting all users
    print("\n1. Testing GET /users (all users)...")
    response = requests.get("http://localhost:8006/api/v1/users")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"   Found {len(users)} users")
        for user in users[:3]:  # Show first 3 users
            print(f"   - User: {user.get('id', 'N/A')} - {user.get('email', 'N/A')} - {user.get('name', 'N/A')}")
    
    # Test filtering by email
    email = "test_1748560720@example.com"
    print(f"\n2. Testing GET /users?email={email}...")
    response = requests.get(f"http://localhost:8006/api/v1/users?email={email}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"   Found {len(users)} users")
        for user in users:
            print(f"   - User: {user.get('id', 'N/A')} - {user.get('email', 'N/A')} - {user.get('name', 'N/A')}")
    
    # Test if we need to find the user in the list
    if response.status_code == 200:
        users = response.json()
        target_user = None
        for user in users:
            if user.get('email') == email:
                target_user = user
                break
        
        if target_user:
            print(f"   ✅ Found target user: {target_user}")
        else:
            print(f"   ❌ Target user with email {email} not found in response")

if __name__ == "__main__":
    test_users_service()
