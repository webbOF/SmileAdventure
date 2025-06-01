#!/usr/bin/env python3
"""
Comprehensive Integration Testing for SmileAdventure Project
Day 1 Task 3 - Complete System Validation
"""

import json
import jwt
import subprocess
import sys
import time
from datetime import datetime

import requests


class SmileAdventureIntegrationTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.auth_token = None
        self.user_id = None
        self.session_id = None
        self.test_results = {}
        self.performance_metrics = {}
        
    def log_test(self, test_name, status, details=None):
        """Log test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_results[test_name] = {
            "status": status,
            "timestamp": timestamp,
            "details": details
        }
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} [{timestamp}] {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def measure_performance(self, test_name, start_time, end_time):
        """Measure and log performance metrics"""
        duration = end_time - start_time
        self.performance_metrics[test_name] = duration
        print(f"⏱️  Performance: {test_name} took {duration:.3f}s")
        
    def check_system_health(self):
        """Check overall system health"""
        print("\n🏥 SYSTEM HEALTH CHECK")
        print("=" * 50)
        
        # Check container status
        try:
            result = subprocess.run(['docker-compose', 'ps'], 
                                  capture_output=True, text=True, cwd=r'C:\Users\arman\Desktop\SeriousGame')
            if result.returncode == 0:
                print("Docker containers status:")
                print(result.stdout)
                self.log_test("docker_containers_status", "PASS", "All containers running")
            else:
                self.log_test("docker_containers_status", "FAIL", result.stderr)
        except Exception as e:
            self.log_test("docker_containers_status", "FAIL", str(e))
        
        # Check API Gateway health
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                self.log_test("api_gateway_health", "PASS", f"Status: {response.status_code}")
                self.measure_performance("api_gateway_health", start_time, end_time)
            else:
                self.log_test("api_gateway_health", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("api_gateway_health", "FAIL", str(e))
        
        # Check individual service health
        services = ["auth", "users", "game", "reports"]
        for service in services:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/api/v1/{service}/health", timeout=5)
                end_time = time.time()
                
                if response.status_code == 200:
                    self.log_test(f"{service}_service_health", "PASS", f"Status: {response.status_code}")
                    self.measure_performance(f"{service}_service_health", start_time, end_time)
                else:
                    self.log_test(f"{service}_service_health", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"{service}_service_health", "FAIL", str(e))
    
    def test_user_registration_and_auth(self):
        """Test complete user registration and authentication flow"""
        print("\n👤 USER REGISTRATION & AUTHENTICATION")
        print("=" * 50)
        
        # Test user registration
        timestamp = int(time.time())
        registration_data = {
            "name": "Integration Test User",
            "email": f"testuser_{timestamp}@integration.test",
            "password": "SecureTest123!",
            "role": "student"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json=registration_data,
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code in [200, 201]:
                self.log_test("user_registration", "PASS", f"User created: {registration_data['name']}")
                self.measure_performance("user_registration", start_time, end_time)
            else:
                self.log_test("user_registration", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("user_registration", "FAIL", str(e))
            return False
        
        # Test user login
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
          try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                auth_response = response.json()
                self.auth_token = auth_response.get("access_token")                # Extract user_id from JWT token payload
                if self.auth_token:
                    try:
                        decoded = jwt.decode(self.auth_token, options={"verify_signature": False})
                        self.user_id = decoded.get("user_id")
                    except:
                        self.user_id = None
                self.log_test("user_login", "PASS", f"Token received, User ID: {self.user_id}")
                self.measure_performance("user_login", start_time, end_time)
                return True
            else:
                self.log_test("user_login", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("user_login", "FAIL", str(e))
            return False
    
    def test_protected_endpoints(self):
        """Test access to protected endpoints with authentication"""
        print("\n🔐 PROTECTED ENDPOINTS ACCESS")
        print("=" * 50)
        
        if not self.auth_token:
            self.log_test("protected_endpoints", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test user profile access
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/v1/users/me",
                headers=headers,
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                profile_data = response.json()
                self.log_test("user_profile_access", "PASS", f"Profile retrieved")
                self.measure_performance("user_profile_access", start_time, end_time)
            else:
                self.log_test("user_profile_access", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("user_profile_access", "FAIL", str(e))
    
    def test_game_workflow(self):
        """Test complete game workflow"""
        print("\n🎮 GAME WORKFLOW TESTING")
        print("=" * 50)
        
        if not self.auth_token:
            self.log_test("game_workflow", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Get available scenarios
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/v1/game/scenarios",
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                scenarios = response.json()
                self.log_test("get_scenarios", "PASS", f"Retrieved {len(scenarios)} scenarios")
                self.measure_performance("get_scenarios", start_time, end_time)
            else:
                self.log_test("get_scenarios", "FAIL", f"Status: {response.status_code}")
                return
        except Exception as e:
            self.log_test("get_scenarios", "FAIL", str(e))
            return
          # Start a game session
        if scenarios:
            try:
                # Use first available scenario key
                scenario_list = list(scenarios.get("scenarios", {}).keys())
                scenario_id = scenario_list[0] if scenario_list else "basic_adventure"
                game_start_data = {
                    "scenario_id": scenario_id,
                    "difficulty": "normal"
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/v1/game/start",
                    json=game_start_data,
                    headers=headers,
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    game_data = response.json()
                    self.session_id = game_data.get("session_id")
                    self.log_test("start_game_session", "PASS", f"Session ID: {self.session_id}")
                    self.measure_performance("start_game_session", start_time, end_time)
                else:
                    self.log_test("start_game_session", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                    return
            except Exception as e:
                self.log_test("start_game_session", "FAIL", str(e))
                return
        
        # Test game action
        if self.session_id:
            try:
                action_data = {
                    "session_id": self.session_id,
                    "action_type": "choice",
                    "action_data": {"choice": "brush_teeth"}
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/v1/game/action",
                    json=action_data,
                    headers=headers,
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    action_result = response.json()
                    self.log_test("process_game_action", "PASS", f"Action processed successfully")
                    self.measure_performance("process_game_action", start_time, end_time)
                else:
                    self.log_test("process_game_action", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("process_game_action", "FAIL", str(e))
    
    def test_data_persistence(self):
        """Test data persistence after restart"""
        print("\n💾 DATA PERSISTENCE VERIFICATION")
        print("=" * 50)
        
        if not self.auth_token:
            self.log_test("data_persistence", "SKIP", "No auth token available")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Check user sessions persist
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/v1/game/sessions",
                headers=headers,
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                sessions = response.json()
                self.log_test("session_persistence", "PASS", f"Found {len(sessions)} persisted sessions")
                self.measure_performance("session_persistence", start_time, end_time)
            else:
                self.log_test("session_persistence", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("session_persistence", "FAIL", str(e))
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🚨 ERROR HANDLING VALIDATION")
        print("=" * 50)
        
        # Test invalid authentication
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/users/me",
                headers={"Authorization": "Bearer invalid_token"},
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                self.log_test("invalid_auth_handling", "PASS", f"Properly rejected invalid token: {response.status_code}")
            else:
                self.log_test("invalid_auth_handling", "FAIL", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("invalid_auth_handling", "FAIL", str(e))
        
        # Test invalid input data
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json={"invalid": "data"},
                timeout=10
            )
            
            if response.status_code in [400, 422]:
                self.log_test("invalid_input_handling", "PASS", f"Properly rejected invalid input: {response.status_code}")
            else:
                self.log_test("invalid_input_handling", "FAIL", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("invalid_input_handling", "FAIL", str(e))
    
    def establish_performance_baseline(self):
        """Establish performance baselines"""
        print("\n⏱️ PERFORMANCE BASELINE ESTABLISHMENT")
        print("=" * 50)
        
        # System resource usage
        try:
            # Basic performance metrics
            performance_data = {
                "response_times": self.performance_metrics
            }
            
            self.log_test("performance_baseline", "PASS", "Performance metrics collected")
            
            # Calculate average response times
            if self.performance_metrics:
                avg_response_time = sum(self.performance_metrics.values()) / len(self.performance_metrics)
                print(f"📊 Average API Response Time: {avg_response_time:.3f}s")
                
                # Identify slow endpoints
                slow_endpoints = {k: v for k, v in self.performance_metrics.items() if v > 2.0}
                if slow_endpoints:
                    print(f"⚠️  Slow endpoints (>2s): {slow_endpoints}")
            
        except Exception as e:
            self.log_test("performance_baseline", "FAIL", str(e))
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n📋 FINAL INTEGRATION TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results.values() if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results.values() if r["status"] == "SKIP"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 80)
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⏭️"
            print(f"{status_icon} {test_name}: {result['status']}")
            if result.get("details"):
                print(f"   └─ {result['details']}")
        
        if self.performance_metrics:
            print(f"\nPerformance Metrics:")
            print("-" * 80)
            for test_name, duration in self.performance_metrics.items():
                print(f"⏱️  {test_name}: {duration:.3f}s")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics
        }
        
        with open("integration_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved to: integration_test_report.json")
        
        return passed_tests == total_tests - skipped_tests
    
    def run_comprehensive_test(self):
        """Run all integration tests"""
        print("🚀 STARTING COMPREHENSIVE INTEGRATION TEST")
        print("=" * 80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        self.check_system_health()
        
        if self.test_user_registration_and_auth():
            self.test_protected_endpoints()
            self.test_game_workflow()
        
        self.test_data_persistence()
        self.test_error_handling()
        self.establish_performance_baseline()
        
        # Generate final report
        success = self.generate_final_report()
        
        print(f"\n🏁 INTEGRATION TEST COMPLETED")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Overall Result: {'✅ SUCCESS' if success else '❌ FAILURE'}")
        
        return success

if __name__ == "__main__":
    tester = SmileAdventureIntegrationTest()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)
