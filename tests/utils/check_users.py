import json

import requests

response = requests.get('http://localhost:8006/api/v1/users')
users = response.json()

print('Looking for recent test users:')
for user in users:
    if 'test_1748560' in user.get('email', '') or 'test_' in user.get('email', ''):
        print(f'Found: ID={user["id"]}, Email={user["email"]}, Name={user["name"]}')
        
print(f'Total users in system: {len(users)}')
print('Last 5 users:')
for user in users[-5:]:
    print(f'  ID={user["id"]}, Email={user["email"]}')
