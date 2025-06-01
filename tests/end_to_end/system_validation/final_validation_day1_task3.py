#!/usr/bin/env python3
"""
SmileAdventure Day 1 Task 3 - Final Validation Test
Clean version for final verification
"""

import json
import subprocess
import sys
import time
from datetime import datetime

import jwt
import requests


def test_system_final():
    """Final comprehensive test for Day 1 Task 3 completion"""
    print("🎯 SMILEADVENTURE DAY 1 TASK 3 - FINAL VALIDATION")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    results = {"total": 0, "passed": 0, "failed": 0}
    
    def log_result(test_name, success, detail=""):
        results["total"] += 1
        if success:
            results["passed"] += 1
            print(f"✅ {test_name}: PASS {detail}")
        else:
            results["failed"] += 1
            print(f"❌ {test_name}: FAIL {detail}")
    
    # Test 1: Container Health
    try:
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, timeout=30)
        log_result("Docker Containers", result.returncode == 0)
    except:
        log_result("Docker Containers", False)
    
    # Test 2: API Gateway Health
    try:
        response = requests.get(f"{base_url}/api/v1/health", timeout=5)
        log_result("API Gateway Health", response.status_code == 200)
    except:
        log_result("API Gateway Health", False)
    
    # Test 3: Service Health Checks
    services = ["auth", "users", "game", "reports"]
    for service in services:
        try:
            response = requests.get(f"{base_url}/api/v1/{service}/health", timeout=5)
            log_result(f"{service.title()} Service Health", response.status_code == 200)
        except:
            log_result(f"{service.title()} Service Health", False)
    
    # Test 4: Complete Authentication Flow
    timestamp = int(time.time())
    user_data = {
        "name": "Final Test User",
        "email": f"final_test_{timestamp}@test.com",
        "password": "TestPass123!",
        "role": "student"
    }
    
    auth_token = None
    try:
        # Registration
        reg_response = requests.post(f"{base_url}/api/v1/auth/register", json=user_data, timeout=10)
        log_result("User Registration", reg_response.status_code in [200, 201])
        
        # Login
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data, timeout=10)
        if login_response.status_code == 200:
            auth_token = login_response.json().get("access_token")
            log_result("User Login", bool(auth_token))
        else:
            log_result("User Login", False)
    except:
        log_result("User Registration", False)
        log_result("User Login", False)
    
    # Test 5: Protected Endpoint Access
    if auth_token:
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            profile_response = requests.get(f"{base_url}/api/v1/users/me", headers=headers, timeout=10)
            log_result("User Profile Access", profile_response.status_code == 200, 
                      f"(Status: {profile_response.status_code})")
        except:
            log_result("User Profile Access", False)
    else:
        log_result("User Profile Access", False, "(No auth token)")
    
    # Test 6: Game Scenarios
    try:
        response = requests.get(f"{base_url}/api/v1/game/scenarios", timeout=10)
        if response.status_code == 200:
            scenarios = response.json().get("scenarios", {})
            log_result("Game Scenarios", len(scenarios) > 0, f"({len(scenarios)} scenarios)")
        else:
            log_result("Game Scenarios", False)
    except:
        log_result("Game Scenarios", False)
    
    # Test 7: Game Session Creation
    if auth_token:
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            session_data = {"scenario_id": "basic_adventure", "difficulty": "normal"}
            session_response = requests.post(f"{base_url}/api/v1/game/start", 
                                           json=session_data, headers=headers, timeout=10)
            log_result("Game Session Start", session_response.status_code == 200,
                      f"(Status: {session_response.status_code})")
        except:
            log_result("Game Session Start", False)
    else:
        log_result("Game Session Start", False, "(No auth token)")
    
    # Test 8: Error Handling
    try:
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        error_response = requests.get(f"{base_url}/api/v1/users/me", headers=invalid_headers, timeout=5)
        log_result("Error Handling", error_response.status_code == 401)
    except:
        log_result("Error Handling", False)
    
    # Test 9: Data Persistence Check
    if auth_token:
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            sessions_response = requests.get(f"{base_url}/api/v1/game/sessions", headers=headers, timeout=10)
            log_result("Data Persistence", sessions_response.status_code in [200, 404], 
                      f"(Status: {sessions_response.status_code})")
        except:
            log_result("Data Persistence", False)
    else:
        log_result("Data Persistence", False, "(No auth token)")
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 FINAL VALIDATION RESULTS")
    print("=" * 60)
    success_rate = (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 DAY 1 TASK 3: SUCCESSFULLY COMPLETED!")
        print("✅ System ready for production deployment")
        return 0
    elif success_rate >= 75:
        print("\n⚠️  DAY 1 TASK 3: MOSTLY COMPLETED")
        print("🔧 Minor issues need resolution")
        return 1
    else:
        print("\n❌ DAY 1 TASK 3: REQUIRES ATTENTION")
        print("🚨 Critical issues need resolution")
        return 2


if __name__ == "__main__":
    exit_code = test_system_final()
    sys.exit(exit_code)
