#!/usr/bin/env python3
"""
API Gateway Routing Validation Script
=====================================

This script validates that the API Gateway routing fixes have been properly applied.
It checks that all URLs now correctly use the /api/v1 prefix without duplication.

USERS_SERVICE_URL = "http://users:8006/api/v1"

Expected URL patterns after fixes:
- http://users:8006/api/v1/professionals/search (NOT /users/professionals/search)
- http://users:8006/api/v1/children (NOT /users/children)
- http://users:8006/api/v1/sensory-profiles (NOT /users/sensory-profiles)
"""

import os
import re
from pathlib import Path


def validate_routing_fixes():
    """Validate that all routing fixes have been applied correctly."""
    
    user_routes_file = Path("microservices/API-GATEWAY/src/routes/user_routes.py")
    
    if not user_routes_file.exists():
        print(f"❌ File not found: {user_routes_file}")
        return False
    
    print(f"🔍 Analyzing routing patterns in {user_routes_file}")
    
    with open(user_routes_file, 'r') as f:
        content = f.read()
    
    # Extract all URL patterns that use USERS_SERVICE_URL
    url_pattern = re.compile(r'f"{USERS_SERVICE_URL}([^"]*)"')
    matches = url_pattern.findall(content)
    
    print(f"\n📋 Found {len(matches)} URL patterns using USERS_SERVICE_URL:")
    
    correct_patterns = []
    incorrect_patterns = []
    
    for match in matches:
        full_url = f"{{USERS_SERVICE_URL}}{match}"
        resolved_url = f"http://users:8006/api/v1{match}"
        
        # Check for problematic patterns
        if "/users/professionals" in match or "/users/children" in match or "/users/sensory-profiles" in match:
            incorrect_patterns.append((full_url, resolved_url))
            print(f"❌ INCORRECT: {resolved_url}")
        else:
            correct_patterns.append((full_url, resolved_url))
            print(f"✅ CORRECT:   {resolved_url}")
    
    print(f"\n📊 Summary:")
    print(f"✅ Correct patterns: {len(correct_patterns)}")
    print(f"❌ Incorrect patterns: {len(incorrect_patterns)}")
    
    if incorrect_patterns:
        print(f"\n🚨 ISSUES FOUND - The following URLs still have redundant '/users/' prefixes:")
        for pattern, resolved in incorrect_patterns:
            print(f"   {pattern} → {resolved}")
        return False
    else:
        print(f"\n🎉 SUCCESS - All routing patterns are correctly configured!")
        print(f"   USERS_SERVICE_URL already includes '/api/v1' prefix")
        print(f"   No redundant '/users/' prefixes found")
        return True

def show_url_examples():
    """Show examples of correct vs incorrect URL patterns."""
    
    print(f"\n📚 URL Pattern Examples:")
    print(f"USERS_SERVICE_URL = 'http://users:8006/api/v1'")
    print(f"")
    print(f"✅ CORRECT:")
    print(f"   f'{{USERS_SERVICE_URL}}/professionals/search' → http://users:8006/api/v1/professionals/search")
    print(f"   f'{{USERS_SERVICE_URL}}/children' → http://users:8006/api/v1/children")
    print(f"   f'{{USERS_SERVICE_URL}}/sensory-profiles' → http://users:8006/api/v1/sensory-profiles")
    print(f"")
    print(f"❌ INCORRECT (what we fixed):")
    print(f"   f'{{USERS_SERVICE_URL}}/users/professionals/search' → http://users:8006/api/v1/users/professionals/search")
    print(f"   f'{{USERS_SERVICE_URL}}/users/children' → http://users:8006/api/v1/users/children")
    print(f"   f'{{USERS_SERVICE_URL}}/users/sensory-profiles' → http://users:8006/api/v1/users/sensory-profiles")

if __name__ == "__main__":
    print("🔧 API Gateway Routing Validation")
    print("=" * 50)
    
    show_url_examples()
    
    success = validate_routing_fixes()
    
    if success:
        print(f"\n✅ VALIDATION PASSED - API Gateway routing is correctly configured!")
        exit(0)
    else:
        print(f"\n❌ VALIDATION FAILED - Issues found in routing configuration!")
        exit(1)
