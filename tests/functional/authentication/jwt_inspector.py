#!/usr/bin/env python3
"""
JWT Token Inspector Utility
A simple tool to decode and inspect JWT tokens for debugging
"""

import json
import sys
from datetime import datetime

import requests
from jose import jwt


def decode_token(token):
    """Decode JWT token without verification"""
    try:
        # Decode without verification (for debugging only)
        header = jwt.get_unverified_header(token)
        claims = jwt.get_unverified_claims(token)
        
        print("📋 JWT Token Analysis")
        print("=" * 50)
        
        print("\n🔧 Header:")
        for key, value in header.items():
            print(f"  {key}: {value}")
        
        print("\n🎫 Claims:")
        for key, value in claims.items():
            if key == 'exp':
                # Convert timestamp to readable date
                exp_date = datetime.fromtimestamp(value)
                print(f"  {key}: {value} ({exp_date})")
            else:
                print(f"  {key}: {value}")
        
        # Check token validity
        exp_timestamp = claims.get('exp')
        if exp_timestamp:
            exp_date = datetime.fromtimestamp(exp_timestamp)
            now = datetime.now()
            if now < exp_date:
                print(f"\n✅ Token is valid until: {exp_date}")
            else:
                print(f"\n❌ Token expired at: {exp_date}")
        
        return True
    except Exception as e:
        print(f"❌ Error decoding token: {e}")
        return False

def get_token_from_login():
    """Get a fresh token by logging in"""
    print("🔐 Getting fresh token via login...")
    
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    try:
        response = requests.post(
            "http://localhost:8001/api/v1/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print("✅ Login successful!")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def main():
    """Main function"""
    print("🔍 JWT Token Inspector")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        # Token provided as command line argument
        token = sys.argv[1]
        print("Using token from command line...")
    else:
        # Ask user for token or login
        choice = input("\n1. Paste token directly\n2. Login to get token\nChoose (1/2): ")
        
        if choice == "1":
            token = input("Paste JWT token: ").strip()
        elif choice == "2":
            token = get_token_from_login()
            if not token:
                return
        else:
            print("Invalid choice")
            return
    
    if token:
        decode_token(token)
    else:
        print("No token provided")

if __name__ == "__main__":
    main()
