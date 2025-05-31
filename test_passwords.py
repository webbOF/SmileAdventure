#!/usr/bin/env python3

import requests


def test_passwords():
    """Test different passwords for test@example.com"""
    
    passwords = ['password', 'test', 'test123', '123456', 'admin', 'password123']
    
    for pwd in passwords:
        try:
            response = requests.post('http://localhost:8001/api/v1/auth/login', 
                                   json={'email': 'test@example.com', 'password': pwd})
            print(f'Password "{pwd}": {response.status_code}')
            if response.status_code == 200:
                print(f'  ✅ SUCCESS! Password is: {pwd}')
                print(f'  Token: {response.json()["access_token"][:50]}...')
                break
        except Exception as e:
            print(f'Password "{pwd}": Error - {e}')

if __name__ == "__main__":
    test_passwords()
