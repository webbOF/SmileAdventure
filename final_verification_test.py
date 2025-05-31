import json
from datetime import datetime

import requests


def comprehensive_final_test():
    print("=" * 60)
    print("SMILEADVENTURE API GATEWAY - FINAL VERIFICATION TEST")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
      # Test 1: Gateway Health Check
    print("1. Testing Gateway Health Check...")
    try:
        response = requests.get("http://localhost:8000/api/v1/health")
        results["health_check"] = response.status_code == 200
        print(f"   Status: {response.status_code} - {'PASS' if results['health_check'] else 'FAIL'}")
        if results["health_check"]:
            health_data = response.json()
            services = health_data.get('services', {})
            if isinstance(services, dict):
                online_count = len([s for s in services.values() if isinstance(s, dict) and s.get('status') == 'online'])
                print(f"   Services online: {online_count}")
            else:
                print(f"   Services data received: {type(services)}")
    except Exception as e:
        results["health_check"] = False
        print(f"   FAIL: {e}")
        print(f"   FAIL: {e}")
      # Test 2: User Registration with Sync
    print("\n2. Testing User Registration with Service Sync...")
    import time
    timestamp = int(time.time())
    register_data = {
        "email": f"final.test.{timestamp}@example.com",
        "password": "TestPassword123!",
        "name": "Final Test User",
        "role": "patient"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/register", json=register_data)
        results["registration"] = response.status_code in [200, 201]
        user_id = response.json().get("user_id") if results["registration"] else None
        print(f"   Status: {response.status_code} - {'PASS' if results['registration'] else 'FAIL'}")
        if results["registration"]:
            print(f"   User ID: {user_id}")
    except Exception as e:
        results["registration"] = False
        print(f"   FAIL: {e}")
      # Test 3: Login and JWT Generation
    print("\n3. Testing Login and JWT Token Generation...")
    login_data = {
        "email": f"final.test.{timestamp}@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        results["login"] = response.status_code == 200
        login_result = response.json() if results["login"] else {}
        token = login_result.get("access_token")
        print(f"   Status: {response.status_code} - {'PASS' if results['login'] else 'FAIL'}")
        if results["login"]:
            print(f"   Token generated: {'Yes' if token else 'No'}")
            print(f"   User data included: {'Yes' if login_result.get('user') else 'No'}")
    except Exception as e:
        results["login"] = False
        token = None
        print(f"   FAIL: {e}")
    
    # Test 4: Authenticated Access to Protected Routes
    print("\n4. Testing Authenticated Access to Protected Routes...")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        protected_routes = [
            f"/api/v1/users/{user_id}",
            "/api/v1/game/sessions"
        ]
        
        protected_access_results = []
        for route in protected_routes:
            try:
                response = requests.get(f"http://localhost:8000{route}", headers=headers)
                success = response.status_code == 200
                protected_access_results.append(success)
                print(f"   {route}: {response.status_code} - {'PASS' if success else 'FAIL'}")
            except Exception as e:
                protected_access_results.append(False)
                print(f"   {route}: FAIL - {e}")
        
        results["protected_access"] = all(protected_access_results)
    else:
        results["protected_access"] = False
        print("   FAIL: No token available for testing")
    
    # Test 5: Service Synchronization Verification
    print("\n5. Testing Service Synchronization...")
    if token and user_id:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            # Check if user exists in Users service
            response = requests.get(f"http://localhost:8000/api/v1/users/{user_id}", headers=headers)
            results["sync_verification"] = response.status_code == 200
            print(f"   Users service sync: {'PASS' if results['sync_verification'] else 'FAIL'}")
            if results["sync_verification"]:
                user_data = response.json()
                print(f"   Synced user email: {user_data.get('email')}")
                print(f"   Synced user name: {user_data.get('name')}")
        except Exception as e:
            results["sync_verification"] = False
            print(f"   FAIL: {e}")
    else:
        results["sync_verification"] = False
        print("   FAIL: Prerequisites not met")
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    all_tests_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():<30} {status}")
    
    print("=" * 60)
    overall_status = "🎉 ALL TESTS PASSED" if all_tests_passed else "❌ SOME TESTS FAILED"
    print(f"OVERALL STATUS: {overall_status}")
    print("=" * 60)
    
    if all_tests_passed:
        print("\n✅ SmileAdventure API Gateway is fully functional!")
        print("✅ JWT authentication flow working end-to-end")
        print("✅ Service synchronization working")
        print("✅ Protected routes accessible")
        print("✅ All microservices integrated properly")
    
    return all_tests_passed

if __name__ == "__main__":
    comprehensive_final_test()
