#!/usr/bin/env python3
"""
🌐 API GATEWAY - Comprehensive Routing and Integration Verification
Tests routing, authentication, service integration, and error handling
"""

import json
import time
from datetime import datetime
from typing import Dict, List

import requests

# Base URLs
GATEWAY_URL = "http://localhost:8000"
AUTH_SERVICE_URL = "http://localhost:8001"
USERS_SERVICE_URL = "http://localhost:8006"
REPORTS_SERVICE_URL = "http://localhost:8007"
GAME_SERVICE_URL = "http://localhost:8005"

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"📋 {title}")
    print(f"{'='*80}")

def print_test_header(title: str):
    """Print test section header"""
    print(f"\n🔍 {title}")
    print("-" * 60)

def test_direct_service_connectivity():
    """Test direct connectivity to all services"""
    print_test_header("DIRECT SERVICE CONNECTIVITY")
    
    services = {
        "API Gateway": f"{GATEWAY_URL}/status",
        "Auth Service": f"{AUTH_SERVICE_URL}/status", 
        "Users Service": f"{USERS_SERVICE_URL}/status",
        "Reports Service": f"{REPORTS_SERVICE_URL}/status",
        "Game Service": f"{GAME_SERVICE_URL}/status"
    }
    
    results = {}
    for service_name, url in services.items():
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            results[service_name] = {
                "status": "✅ UP" if response.status_code == 200 else f"⚠️ HTTP {response.status_code}",
                "response_time": response_time,
                "reachable": True,
                "response": response.json() if response.text else {}
            }
            print(f"   {service_name:<15} {results[service_name]['status']:<15} {response_time}ms")
            
        except requests.exceptions.ConnectionError:
            results[service_name] = {
                "status": "❌ DOWN",
                "response_time": 0,
                "reachable": False,
                "response": "Connection refused"
            }
            print(f"   {service_name:<15} ❌ DOWN{'':<10} Connection refused")
        except Exception as e:
            results[service_name] = {
                "status": f"💥 ERROR",
                "response_time": 0,
                "reachable": False,
                "response": str(e)
            }
            print(f"   {service_name:<15} 💥 ERROR{'':<8} {str(e)[:50]}")
    
    return results

def test_gateway_routing():
    """Test API Gateway routing to services"""
    print_test_header("API GATEWAY ROUTING TESTS")
    
    routing_tests = [
        {
            "name": "Gateway Status",
            "method": "GET",
            "url": f"{GATEWAY_URL}/status",
            "expected_service": "Gateway",
            "auth_required": False
        },
        {
            "name": "Gateway Health Check",
            "method": "GET", 
            "url": f"{GATEWAY_URL}/api/v1/health",
            "expected_service": "All Services",
            "auth_required": False
        },
        {
            "name": "Auth Login Route",
            "method": "POST",
            "url": f"{GATEWAY_URL}/api/v1/auth/login",
            "expected_service": "Auth:8001",
            "auth_required": False,
            "data": {"email": "test@example.com", "password": "testpass"}
        },
        {
            "name": "Users Route (Protected)",
            "method": "GET",
            "url": f"{GATEWAY_URL}/api/v1/users/me",
            "expected_service": "Users:8006",
            "auth_required": True
        },
        {
            "name": "Reports Game Session",
            "method": "POST",
            "url": f"{GATEWAY_URL}/api/v1/reports/game-session",
            "expected_service": "Reports:8007",
            "auth_required": True,
            "data": {
                "user_id": 1,
                "session_id": "test_session",
                "start_time": "2024-01-01T10:00:00Z",
                "end_time": "2024-01-01T10:30:00Z",
                "emotions_detected": [{"emotion": "happy", "intensity": 0.8}]
            }
        }
    ]
    
    results = []
    for test in routing_tests:
        try:
            headers = {"Content-Type": "application/json"}
            
            # Add auth header if required (we'll test without auth for now)
            if test.get("auth_required"):
                headers["Authorization"] = "Bearer dummy_token_for_testing"
            
            if test["method"] == "GET":
                response = requests.get(test["url"], headers=headers, timeout=10)
            else:
                response = requests.post(test["url"], 
                                       json=test.get("data", {}), 
                                       headers=headers, 
                                       timeout=10)
            
            result = {
                "test": test["name"],
                "status": "✅ ROUTED" if response.status_code < 500 else f"❌ HTTP {response.status_code}",
                "http_code": response.status_code,
                "target": test["expected_service"],
                "response_preview": str(response.text)[:100] if response.text else "No content"
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                "test": test["name"],
                "status": "❌ NO_ROUTE",
                "http_code": "N/A",
                "target": test["expected_service"],
                "response_preview": "Gateway not reachable"
            }
        except Exception as e:
            result = {
                "test": test["name"],
                "status": "💥 ERROR",
                "http_code": "N/A", 
                "target": test["expected_service"],
                "response_preview": str(e)[:100]
            }
        
        results.append(result)
        print(f"   {result['test']:<25} {result['status']:<15} → {result['target']:<15} HTTP: {result['http_code']}")
    
    return results

def test_authentication_flow():
    """Test authentication middleware and protected routes"""
    print_test_header("AUTHENTICATION & MIDDLEWARE TESTS")
    
    auth_tests = [
        {
            "name": "No Token Access",
            "url": f"{GATEWAY_URL}/api/v1/users/me",
            "headers": {},
            "expected": "401 Unauthorized"
        },
        {
            "name": "Invalid Token",
            "url": f"{GATEWAY_URL}/api/v1/users/me", 
            "headers": {"Authorization": "Bearer invalid_token"},
            "expected": "401 Unauthorized"
        },
        {
            "name": "Malformed Auth Header",
            "url": f"{GATEWAY_URL}/api/v1/users/me",
            "headers": {"Authorization": "NotBearer token"},
            "expected": "422 or 401"
        }
    ]
    
    results = []
    for test in auth_tests:
        try:
            response = requests.get(test["url"], headers=test["headers"], timeout=5)
            
            result = {
                "test": test["name"],
                "status": "✅ PROTECTED" if response.status_code in [401, 422] else f"⚠️ HTTP {response.status_code}",
                "http_code": response.status_code,
                "expected": test["expected"],
                "response": response.text[:100] if response.text else "No content"
            }
            
        except Exception as e:
            result = {
                "test": test["name"],
                "status": "💥 ERROR",
                "http_code": "N/A",
                "expected": test["expected"],
                "response": str(e)[:100]
            }
        
        results.append(result)
        print(f"   {result['test']:<20} {result['status']:<15} Expected: {result['expected']}")
    
    return results

def test_error_handling():
    """Test error handling when services are down"""
    print_test_header("ERROR HANDLING & RESILIENCE")
    
    # Test routes that would fail if services are down
    error_tests = [
        {
            "name": "Service Down Response",
            "url": f"{GATEWAY_URL}/api/v1/users/1",
            "headers": {"Authorization": "Bearer dummy_token"},
            "expected_behavior": "503 Service Unavailable or timeout"
        },
        {
            "name": "Invalid Route",
            "url": f"{GATEWAY_URL}/api/v1/nonexistent/endpoint", 
            "headers": {},
            "expected_behavior": "404 Not Found"
        },
        {
            "name": "Method Not Allowed",
            "url": f"{GATEWAY_URL}/api/v1/health",
            "method": "POST",
            "headers": {},
            "expected_behavior": "405 Method Not Allowed"
        }
    ]
    
    results = []
    for test in error_tests:
        try:
            method = test.get("method", "GET")
            if method == "GET":
                response = requests.get(test["url"], headers=test["headers"], timeout=10)
            else:
                response = requests.post(test["url"], headers=test["headers"], timeout=10)
            
            result = {
                "test": test["name"],
                "status": f"📋 HTTP {response.status_code}",
                "behavior": test["expected_behavior"],
                "actual_response": response.text[:150] if response.text else "No content"
            }
            
        except requests.exceptions.Timeout:
            result = {
                "test": test["name"],
                "status": "⏰ TIMEOUT",
                "behavior": test["expected_behavior"],
                "actual_response": "Request timed out"
            }
        except Exception as e:
            result = {
                "test": test["name"],
                "status": "💥 ERROR",
                "behavior": test["expected_behavior"],
                "actual_response": str(e)[:150]
            }
        
        results.append(result)
        print(f"   {result['test']:<20} {result['status']:<15} Expected: {result['behavior']}")
    
    return results

def analyze_service_urls():
    """Analyze configured service URLs vs docker-compose"""
    print_test_header("SERVICE URL CONFIGURATION ANALYSIS")
    
    # Expected URLs from docker-compose.yml
    expected_urls = {
        "auth": "http://auth:8001/api/v1",
        "users": "http://users:8006/api/v1", 
        "reports": "http://reports:8007/api/v1",
        "game": "http://game:8005/api/v1"  # If Game service was added
    }
    
    # Check if we can determine configured URLs (this would need env var access)
    print("   📋 Expected Docker Compose URLs:")
    for service, url in expected_urls.items():
        print(f"      {service:<15} → {url}")
    
    print("\\n   ⚠️  Note: In localhost testing, these should be localhost:PORT")
    print("      Gateway should handle localhost→service mapping")
    
    return expected_urls

def check_cors_configuration():
    """Test CORS configuration"""
    print_test_header("CORS CONFIGURATION CHECK")
    
    cors_test_url = f"{GATEWAY_URL}/status"
    
    try:
        response = requests.options(cors_test_url, headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type"
        })
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin", "Not set"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods", "Not set"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers", "Not set"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials", "Not set")
        }
        
        print(f"   CORS Headers Response (HTTP {response.status_code}):")
        for header, value in cors_headers.items():
            print(f"      {header:<30} {value}")
        
        return cors_headers
        
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
        return {}

def generate_comprehensive_report():
    """Generate comprehensive API Gateway assessment report"""
    print_header("API GATEWAY - COMPREHENSIVE VERIFICATION")
    print(f"📅 Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: SmileAdventure API Gateway")
    print(f"🌐 Base URL: {GATEWAY_URL}")
    
    # Run all tests
    connectivity_results = test_direct_service_connectivity()
    routing_results = test_gateway_routing()
    auth_results = test_authentication_flow()
    error_results = test_error_handling()
    url_analysis = analyze_service_urls()
    cors_config = check_cors_configuration()
    
    # Calculate scores
    total_services = len(connectivity_results)
    reachable_services = sum(1 for r in connectivity_results.values() if r['reachable'])
    connectivity_score = (reachable_services / total_services) * 100 if total_services > 0 else 0
    
    total_routes = len(routing_results)
    working_routes = sum(1 for r in routing_results if "✅" in r['status'])
    routing_score = (working_routes / total_routes) * 100 if total_routes > 0 else 0
    
    total_auth = len(auth_results)
    protected_routes = sum(1 for r in auth_results if "✅" in r['status'])
    auth_score = (protected_routes / total_auth) * 100 if total_auth > 0 else 0
    
    overall_score = (connectivity_score * 0.4 + routing_score * 0.4 + auth_score * 0.2)
    
    # Summary Report
    print_header("ASSESSMENT SUMMARY")
    print(f"📊 Service Connectivity: {connectivity_score:.1f}% ({reachable_services}/{total_services} services up)")
    print(f"📊 Gateway Routing: {routing_score:.1f}% ({working_routes}/{total_routes} routes working)")
    print(f"📊 Authentication: {auth_score:.1f}% ({protected_routes}/{total_auth} properly protected)")
    print(f"📊 **OVERALL SCORE: {overall_score:.1f}%**")
    
    # Status Assessment
    if overall_score >= 80:
        status = "✅ EXCELLENT - Gateway ready for production"
        effort = "Minor optimizations only"
    elif overall_score >= 60:
        status = "🔄 GOOD - Core functionality working"
        effort = "1-2 days for improvements"
    elif overall_score >= 40:
        status = "⚠️ PARTIAL - Significant gaps"
        effort = "2-3 days for stability"
    else:
        status = "❌ CRITICAL - Major issues"
        effort = "3-5 days for basic functionality"
    
    print(f"\\n🎯 Status: {status}")
    print(f"🕒 Estimated effort: {effort}")
    
    # Action Items
    print_header("PRIORITY ACTION ITEMS")
    action_items = []
    
    if connectivity_score < 80:
        action_items.append("🚨 CRITICAL: Start missing services")
    if routing_score < 60:
        action_items.append("🔥 HIGH: Fix gateway routing configuration")
    if auth_score < 70:
        action_items.append("🔒 HIGH: Implement proper authentication middleware")
    if not cors_config.get("Access-Control-Allow-Origin"):
        action_items.append("🌐 MEDIUM: Configure CORS properly")
    
    if not action_items:
        print("   ✅ No critical issues identified!")
    else:
        for i, item in enumerate(action_items, 1):
            print(f"   {i}. {item}")
    
    return {
        "overall_score": overall_score,
        "connectivity": connectivity_results,
        "routing": routing_results,
        "authentication": auth_results,
        "error_handling": error_results,
        "cors": cors_config,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    try:
        report = generate_comprehensive_report()
        
        # Save detailed report
        with open("api_gateway_assessment.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\\n💾 Detailed report saved to: api_gateway_assessment.json")
        
    except Exception as e:
        print(f"❌ Assessment failed: {e}")
        import traceback
        traceback.print_exc()
