#!/usr/bin/env python3
"""
Comprehensive Users Microservice Verification Script
Tests all endpoints and functionality systematically
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List

import requests

# Configuration
BASE_URL = "http://localhost:8006"
API_PREFIX = "/api/v1"

def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_test_result(endpoint: str, method: str, status_code: int, 
                     response_time: float, success: bool, note: str = ""):
    """Print formatted test result"""
    status_icon = "✅" if success else "❌"
    print(f"{status_icon} {method:4} {endpoint:30} | {status_code:3} | {response_time:6.2f}ms | {note}")

def test_endpoint(method: str, endpoint: str, data: Dict = None, 
                 headers: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
    """Test a single endpoint and return results"""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    start_time = time.time()
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response_time = (time.time() - start_time) * 1000
        success = response.status_code == expected_status
        
        return {
            "success": success,
            "status_code": response.status_code,
            "response_time": response_time,
            "data": response.json() if response.text else None,
            "error": None
        }
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            "success": False,
            "status_code": 0,
            "response_time": response_time,
            "data": None,
            "error": str(e)
        }

def main():
    """Run comprehensive verification tests"""
    print("🎯 USERS MICROSERVICE - COMPREHENSIVE VERIFICATION")
    print(f"Timestamp: {datetime.now()}")
    print(f"Base URL: {BASE_URL}")
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Service Health Check
    print_test_header("1. SERVICE HEALTH CHECK")
    result = test_endpoint("GET", "/../../status")  # Special case for status endpoint
    if result["success"]:
        passed_tests += 1
    total_tests += 1
    print_test_result("/status", "GET", result["status_code"], 
                     result["response_time"], result["success"], "Service health")
    
    # Test 2: Users Management
    print_test_header("2. USERS MANAGEMENT")
    
    # Get users list
    result = test_endpoint("GET", "/users")
    if result["success"]:
        passed_tests += 1
        users_count = len(result["data"]) if result["data"] else 0
        print_test_result("/users", "GET", result["status_code"], 
                         result["response_time"], result["success"], f"{users_count} users")
    else:
        print_test_result("/users", "GET", result["status_code"], 
                         result["response_time"], result["success"], "Failed")
    total_tests += 1
    
    # Create new user
    new_user_data = {
        "email": f"test.user.{int(time.time())}@example.com",
        "name": "Test",
        "surname": "User",
        "user_type": "child",
        "password": "password123",
        "gender": "M",
        "city": "Roma"
    }
    
    result = test_endpoint("POST", "/users", new_user_data, expected_status=200)
    if result["success"]:
        passed_tests += 1
        print_test_result("/users", "POST", result["status_code"], 
                         result["response_time"], result["success"], "User created")
    else:
        print_test_result("/users", "POST", result["status_code"], 
                         result["response_time"], result["success"], "Creation failed")
    total_tests += 1
    
    # Test 3: Professionals Management
    print_test_header("3. PROFESSIONALS MANAGEMENT")
    
    # Get professionals list
    result = test_endpoint("GET", "/professionals")
    professionals_data = []
    if result["success"]:
        passed_tests += 1
        professionals_data = result["data"] or []
        print_test_result("/professionals", "GET", result["status_code"], 
                         result["response_time"], result["success"], 
                         f"{len(professionals_data)} professionals")
    else:
        print_test_result("/professionals", "GET", result["status_code"], 
                         result["response_time"], result["success"], "Failed")
    total_tests += 1
    
    # Create new professional
    new_professional_data = {
        "email": f"test.prof.{int(time.time())}@example.com",
        "name": "Dr. Test",
        "surname": "Professional",
        "user_type": "professional",
        "password": "password123",
        "bio": "Test professional for verification",
        "experience_years": 5,
        "specialties": [1, 2]  # Assuming specialties 1 and 2 exist
    }
    
    result = test_endpoint("POST", "/professionals", new_professional_data, expected_status=200)
    if result["success"]:
        passed_tests += 1
        created_prof_id = result["data"].get("id") if result["data"] else None
        print_test_result("/professionals", "POST", result["status_code"], 
                         result["response_time"], result["success"], 
                         f"Professional created (ID: {created_prof_id})")
    else:
        print_test_result("/professionals", "POST", result["status_code"], 
                         result["response_time"], result["success"], "Creation failed")
    total_tests += 1
    
    # Test professional detail (if we have professionals)
    if professionals_data:
        prof_id = professionals_data[0].get("id")
        result = test_endpoint("GET", f"/professionals/{prof_id}")
        if result["success"]:
            passed_tests += 1
            print_test_result(f"/professionals/{prof_id}", "GET", result["status_code"], 
                             result["response_time"], result["success"], "Detail retrieved")
        else:
            print_test_result(f"/professionals/{prof_id}", "GET", result["status_code"], 
                             result["response_time"], result["success"], "Detail failed")
        total_tests += 1
    
    # Test 4: Professional Search and Filtering
    print_test_header("4. PROFESSIONAL SEARCH & FILTERING")
    
    search_tests = [
        ("/professionals?specialty_name=Cardiologia", "Specialty filter"),
        ("/professionals?location_city=Roma", "Location filter"),
        ("/professionals?min_rating=3.0", "Rating filter"),
        ("/professionals?skip=0&limit=5", "Pagination"),
        ("/professionals?specialty_name=Cardiologia&location_city=Milano", "Combined filters")
    ]
    
    for endpoint, description in search_tests:
        result = test_endpoint("GET", endpoint)
        if result["success"]:
            passed_tests += 1
            count = len(result["data"]) if result["data"] else 0
            print_test_result(endpoint, "GET", result["status_code"], 
                             result["response_time"], result["success"], 
                             f"{description} - {count} results")
        else:
            print_test_result(endpoint, "GET", result["status_code"], 
                             result["response_time"], result["success"], 
                             f"{description} - Failed")
        total_tests += 1
    
    # Test 5: Specialties Management
    print_test_header("5. SPECIALTIES MANAGEMENT")
    
    # Get specialties
    result = test_endpoint("GET", "/specialties")
    if result["success"]:
        passed_tests += 1
        specialties_count = len(result["data"]) if result["data"] else 0
        print_test_result("/specialties", "GET", result["status_code"], 
                         result["response_time"], result["success"], 
                         f"{specialties_count} specialties")
    else:
        print_test_result("/specialties", "GET", result["status_code"], 
                         result["response_time"], result["success"], "Failed")
    total_tests += 1
    
    # Create new specialty
    new_specialty_data = {
        "name": f"Test Specialty {int(time.time())}",
        "description": "Test specialty for verification"
    }
    
    result = test_endpoint("POST", "/specialties", new_specialty_data, expected_status=200)
    if result["success"]:
        passed_tests += 1
        print_test_result("/specialties", "POST", result["status_code"], 
                         result["response_time"], result["success"], "Specialty created")
    else:
        print_test_result("/specialties", "POST", result["status_code"], 
                         result["response_time"], result["success"], "Creation failed")
    total_tests += 1
    
    # Test 6: Health Records (Authentication Required)
    print_test_header("6. HEALTH RECORDS (AUTH REQUIRED)")
    
    # These should return 401 without proper JWT token
    health_endpoints = [
        ("/health-records/user/1", "GET", "User health records"),
        ("/health-records/", "POST", "Create health record"),
        ("/health-records/shared/professional", "GET", "Shared records for professional")
    ]
    
    for endpoint, method, description in health_endpoints:
        result = test_endpoint(method, endpoint, expected_status=401)
        if result["status_code"] == 401:
            passed_tests += 1
            print_test_result(endpoint, method, result["status_code"], 
                             result["response_time"], True, 
                             f"{description} - Correctly requires auth")
        else:
            print_test_result(endpoint, method, result["status_code"], 
                             result["response_time"], False, 
                             f"{description} - Auth not required (ERROR)")
        total_tests += 1
    
    # Final Results
    print_test_header("VERIFICATION RESULTS SUMMARY")
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT - Service is fully operational!")
    elif success_rate >= 80:
        print("✅ GOOD - Service is operational with minor issues")
    elif success_rate >= 70:
        print("⚠️ FAIR - Service has some issues that need attention")
    else:
        print("❌ POOR - Service needs significant fixes")
    
    print(f"\n🕒 Verification completed at: {datetime.now()}")

if __name__ == "__main__":
    main()
