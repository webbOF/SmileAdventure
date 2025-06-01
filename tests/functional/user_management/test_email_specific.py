#!/usr/bin/env python3

import json

import requests


def test_email_query():
    """Test the email query functionality specifically"""
    
    base_url = "http://localhost:8006"
    
    print("=== TESTING EMAIL QUERY FUNCTIONALITY ===")
    
    # Test with the known email
    email = "test@example.com"
    print(f"Testing with email: {email}")
    
    try:
        response = requests.get(f"{base_url}/api/v1/users", params={"email": email}, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            if isinstance(data, list):
                print(f"Number of users returned: {len(data)}")
                for user in data:
                    print(f"- User email: {user.get('email', 'N/A')}")
            else:
                print(f"Single user: {data.get('email', 'N/A')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_email_query()
