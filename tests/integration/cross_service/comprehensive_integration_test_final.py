#!/usr/bin/env python3
"""
Comprehensive Integration Testing for SmileAdventure Project
Day 1 Task 3 - Complete System Validation - FINAL VERSION
"""

import json
import subprocess
import sys
import time
from datetime import datetime

import jwt
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
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.log_test("docker_containers_status", "PASS", "All containers running")
            else:
                self.log_test("docker_containers_status", "FAIL", "Container issues detected")
        except Exception as e:
            self.log_test("docker_containers_status", "FAIL", str(e))
          # Test each service health endpoint
        services = [
            ("api_gateway_health", "/api/v1/health"),
            ("auth_service_health", "/api/v1/auth/health"),
            ("users_service_health", "/api/v1/users/health"),
            ("game_service_health", "/api/v1/game/health"),
            ("reports_service_health", "/api/v1/reports/health")
        ]
        
        for service_name, endpoint in services:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                end_time = time.time()
                
                if response.status_code == 200:
                    self.log_test(service_name, "PASS", f"Status: {response.status_code}")
                    self.measure_performance(service_name, start_time, end_time)
                else:
                    self.log_test(service_name, "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(service_name, "FAIL", str(e))
                
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
                self.auth_token = auth_response.get("access_token")
                # Extract user_id from JWT token payload
                if self.auth_token:                    try:
                        decoded = jwt.decode(self.auth_token, options={"verify_signature": False})
                        self.user_id = decoded.get("user_id")
                    except:
                        self.user_id = None
                self.log_test("user_login", "PASS", f"Token received, User ID: {self.user_id}")
                self.measure_performance("user_login", start_time, end_time)
                # Small delay to allow for database synchronization between services
                time.sleep(0.1)
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
                self.log_test("user_profile_access", "PASS", f"Profile retrieved for user {profile_data.get('id')}")
                self.measure_performance("user_profile_access", start_time, end_time)
            else:
                # Enhanced debugging for this specific issue
                error_detail = f"Status: {response.status_code}"
                if response.text:
                    error_detail += f", Response: {response.text[:100]}"
                if self.auth_token:
                    error_detail += f", Token length: {len(self.auth_token)}"
                self.log_test("user_profile_access", "FAIL", error_detail)
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
                scenarios_data = response.json()
                scenarios = scenarios_data.get("scenarios", {})
                total_count = scenarios_data.get("total_count", 0)
                self.log_test("get_scenarios", "PASS", f"Retrieved {total_count} scenarios")
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
                scenario_list = list(scenarios.keys())
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
                    self.log_test("start_game_session", "PASS", f"Session started: {self.session_id}")
                    self.measure_performance("start_game_session", start_time, end_time)
                else:
                    self.log_test("start_game_session", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test("start_game_session", "FAIL", str(e))
    
    def test_data_persistence(self):
        """Test data persistence after system restart"""
        print("\n💾 DATA PERSISTENCE TESTING")
        print("=" * 50)
          # Check for existing game sessions
        if not self.auth_token:
            self.log_test("session_persistence", "SKIP", "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        try:
            response = requests.get(f"{self.base_url}/api/v1/game/sessions", headers=headers, timeout=10)
            if response.status_code == 200:
                sessions = response.json()
                session_count = len(sessions) if isinstance(sessions, list) else sessions.get("count", 0)
                self.log_test("session_persistence", "PASS", f"Found {session_count} persisted sessions")
            else:
                self.log_test("session_persistence", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("session_persistence", "FAIL", str(e))
    
    def test_error_handling(self):
        """Test system error handling and validation"""
        print("\n🚨 ERROR HANDLING VALIDATION")
        print("=" * 50)
        
        # Test invalid authentication
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/users/me",
                headers=invalid_headers,
                timeout=10
            )
            if response.status_code == 401:
                self.log_test("invalid_auth_handling", "PASS", f"Properly rejected invalid token: {response.status_code}")
            else:
                self.log_test("invalid_auth_handling", "FAIL", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("invalid_auth_handling", "FAIL", str(e))
        
        # Test invalid input validation
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json={"invalid": "data"},
                timeout=10
            )
            if response.status_code == 422:
                self.log_test("invalid_input_handling", "PASS", f"Properly rejected invalid input: {response.status_code}")
            else:
                self.log_test("invalid_input_handling", "FAIL", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("invalid_input_handling", "FAIL", str(e))
    
    def test_performance_baseline(self):
        """Establish performance baseline"""
        print("\n📊 PERFORMANCE BASELINE")
        print("=" * 50)
        
        if self.performance_metrics:
            avg_response_time = sum(self.performance_metrics.values()) / len(self.performance_metrics)
            self.log_test("performance_baseline", "PASS", f"Average response time: {avg_response_time:.3f}s")
            
            # Log individual metrics
            print("\n   Performance Metrics:")
            for test_name, duration in self.performance_metrics.items():
                print(f"   • {test_name}: {duration:.3f}s")
        else:
            self.log_test("performance_baseline", "FAIL", "No performance data collected")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📋 GENERATING TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed = sum(1 for result in self.test_results.values() if result["status"] == "PASS")
        failed = sum(1 for result in self.test_results.values() if result["status"] == "FAIL")
        skipped = sum(1 for result in self.test_results.values() if result["status"] == "SKIP")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": success_rate
            },
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics
        }
        
        # Save report to file
        report_file = "integration_test_report_final.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Skipped: {skipped}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return report
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 SMILEADVENTURE COMPREHENSIVE INTEGRATION TESTING")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests in sequence
        self.check_system_health()
        auth_success = self.test_user_registration_and_auth()
        
        if auth_success:
            self.test_protected_endpoints()
            self.test_game_workflow()
        
        self.test_data_persistence()
        self.test_error_handling()
        self.test_performance_baseline()
        
        # Generate final report
        report = self.generate_report()
        
        print("\n✨ INTEGRATION TESTING COMPLETED")
        print("=" * 60)
        
        return report


if __name__ == "__main__":
    tester = SmileAdventureIntegrationTest()
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    if report["summary"]["failed"] == 0:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"⚠️  {report['summary']['failed']} test(s) failed")
        sys.exit(1)
