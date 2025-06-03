#!/usr/bin/env python3
"""
Day 4 Quick System Validation
Fast comprehensive validation for production readiness
"""

import json
import time
import requests
import subprocess
import asyncio
import websockets
from datetime import datetime
from typing import Dict, Any
import statistics

class Day4QuickValidation:
    """Quick but comprehensive system validation"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.websocket_url = "ws://localhost:8008"
        self.session = requests.Session()
        self.results = {
            "validation_time": datetime.now().isoformat(),
            "system_health": {},
            "workflows": {},
            "performance": {},
            "security": {}
        }
    
    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"🚀 {title}")
        print(f"{'='*60}")
    
    def log_result(self, test: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test}: {details}")
        return success
    
    def test_system_health(self):
        """Test all microservices health"""
        self.print_header("System Health Validation")
        
        services = [
            ("API Gateway", f"{self.base_url}/api/v1/health"),
            ("Auth Service", f"{self.base_url}/api/v1/auth/health"),
            ("Users Service", f"{self.base_url}/api/v1/users/health"),
            ("Game Service", f"{self.base_url}/api/v1/game/health"),
            ("Reports Service", f"{self.base_url}/api/v1/reports/health"),
            ("LLM Service", "http://localhost:8008/health")
        ]
        
        health_results = {}
        all_healthy = True
        
        for service_name, url in services:
            try:
                start_time = time.time()
                response = self.session.get(url, timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    health_results[service_name] = {
                        "status": "healthy",
                        "response_time": response_time
                    }
                    self.log_result(f"{service_name} Health", True, f"{response_time:.3f}s")
                else:
                    health_results[service_name] = {
                        "status": "unhealthy",
                        "status_code": response.status_code
                    }
                    self.log_result(f"{service_name} Health", False, f"Status: {response.status_code}")
                    all_healthy = False
                    
            except Exception as e:
                health_results[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
                self.log_result(f"{service_name} Health", False, str(e))
                all_healthy = False
        
        self.results["system_health"] = health_results
        return all_healthy
    
    def test_complete_user_workflow(self):
        """Test complete user workflow: registration → login → game session"""
        self.print_header("Complete User Workflow Test")
        
        timestamp = int(time.time())
        user_data = {
            "name": "QuickTest",
            "surname": "User",
            "email": f"quicktest_{timestamp}@example.com",
            "password": "TestPass123!",
            "user_type": "parent"
        }
        
        workflow_success = True
        
        # Step 1: User Registration
        try:
            reg_response = self.session.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
            if reg_response.status_code in [200, 201]:
                self.log_result("User Registration", True, f"Status: {reg_response.status_code}")
            else:
                self.log_result("User Registration", False, f"Status: {reg_response.status_code}")
                workflow_success = False
        except Exception as e:
            self.log_result("User Registration", False, str(e))
            workflow_success = False
        
        # Step 2: User Login
        try:
            login_data = {"email": user_data["email"], "password": user_data["password"]}
            login_response = self.session.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                token = login_result.get("access_token")
                user_id = login_result.get("user", {}).get("id")
                
                if token and user_id:
                    self.log_result("User Login", True, "Token and user ID received")
                    headers = {"Authorization": f"Bearer {token}"}
                else:
                    self.log_result("User Login", False, "Missing token or user ID")
                    workflow_success = False
                    return workflow_success
            else:
                self.log_result("User Login", False, f"Status: {login_response.status_code}")
                workflow_success = False
                return workflow_success
        except Exception as e:
            self.log_result("User Login", False, str(e))
            workflow_success = False
            return workflow_success
        
        # Step 3: Game Session
        try:
            game_data = {
                "user_id": user_id,
                "scenario_id": "basic_adventure",
                "difficulty_level": 1
            }
            
            session_response = self.session.post(f"{self.base_url}/api/v1/game/start", json=game_data, headers=headers)
            if session_response.status_code == 200:
                session_result = session_response.json()
                session_id = session_result.get("session_id")
                
                if session_id:
                    self.log_result("Game Session Start", True, f"Session ID: {session_id}")
                    
                    # End the session
                    end_data = {
                        "session_id": session_id,
                        "user_id": user_id,
                        "completion_status": "completed"
                    }
                    
                    end_response = self.session.post(f"{self.base_url}/api/v1/game/end", json=end_data, headers=headers)
                    if end_response.status_code == 200:
                        self.log_result("Game Session End", True)
                    else:
                        self.log_result("Game Session End", False, f"Status: {end_response.status_code}")
                        workflow_success = False
                else:
                    self.log_result("Game Session Start", False, "No session ID received")
                    workflow_success = False
            else:
                self.log_result("Game Session Start", False, f"Status: {session_response.status_code}")
                workflow_success = False
        except Exception as e:
            self.log_result("Game Session", False, str(e))
            workflow_success = False
        
        self.results["workflows"]["complete_user_workflow"] = workflow_success
        return workflow_success
    
    async def test_websocket_connectivity(self):
        """Test WebSocket connectivity"""
        self.print_header("WebSocket Connectivity Test")
        
        try:
            uri = f"{self.websocket_url}/api/v1/realtime/stream"
            
            async with websockets.connect(uri, timeout=10) as websocket:
                # Send test message
                test_message = {
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Try to receive response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    self.log_result("WebSocket Connection", True, "Connected and messaging successful")
                    self.results["websocket_connectivity"] = True
                    return True
                except asyncio.TimeoutError:
                    self.log_result("WebSocket Connection", True, "Connected but no response (expected)")
                    self.results["websocket_connectivity"] = True
                    return True
                    
        except Exception as e:
            self.log_result("WebSocket Connection", False, str(e))
            self.results["websocket_connectivity"] = False
            return False
    
    def test_performance_benchmarks(self):
        """Test basic performance benchmarks"""
        self.print_header("Performance Benchmarks")
        
        endpoints = [
            ("/api/v1/health", "Health Check"),
            ("/api/v1/auth/health", "Auth Health"),
            ("/api/v1/users/health", "Users Health"),
            ("/api/v1/game/health", "Game Health")
        ]
        
        performance_results = {}
        
        for endpoint, name in endpoints:
            response_times = []
            success_count = 0
            
            for i in range(10):  # 10 requests per endpoint
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                    response_time = time.time() - start_time
                    
                    response_times.append(response_time)
                    if response.status_code == 200:
                        success_count += 1
                        
                except Exception:
                    pass
            
            if response_times:
                avg_time = statistics.mean(response_times)
                max_time = max(response_times)
                success_rate = (success_count / 10) * 100
                
                performance_results[name] = {
                    "avg_response_time": avg_time,
                    "max_response_time": max_time,
                    "success_rate": success_rate
                }
                
                if avg_time < 1.0 and success_rate >= 90:
                    self.log_result(f"{name} Performance", True, f"Avg: {avg_time:.3f}s, Success: {success_rate}%")
                else:
                    self.log_result(f"{name} Performance", False, f"Avg: {avg_time:.3f}s, Success: {success_rate}%")
            else:
                self.log_result(f"{name} Performance", False, "No successful requests")
        
        self.results["performance"] = performance_results
        return len(performance_results) > 0
    
    def test_security_basics(self):
        """Test basic security measures"""
        self.print_header("Security Validation")
        
        security_results = {}
        
        # Test 1: Unauthorized access to protected endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/v1/users/me")
            if response.status_code == 401:
                self.log_result("Unauthorized Access Protection", True, "Correctly rejected")
                security_results["unauthorized_protection"] = True
            else:
                self.log_result("Unauthorized Access Protection", False, f"Status: {response.status_code}")
                security_results["unauthorized_protection"] = False
        except Exception as e:
            self.log_result("Unauthorized Access Protection", False, str(e))
            security_results["unauthorized_protection"] = False
        
        # Test 2: Invalid token handling
        try:
            headers = {"Authorization": "Bearer invalid_token_here"}
            response = self.session.get(f"{self.base_url}/api/v1/users/me", headers=headers)
            if response.status_code == 401:
                self.log_result("Invalid Token Handling", True, "Correctly rejected")
                security_results["invalid_token_handling"] = True
            else:
                self.log_result("Invalid Token Handling", False, f"Status: {response.status_code}")
                security_results["invalid_token_handling"] = False
        except Exception as e:
            self.log_result("Invalid Token Handling", False, str(e))
            security_results["invalid_token_handling"] = False
        
        self.results["security"] = security_results
        return all(security_results.values()) if security_results else False
    
    def generate_final_report(self):
        """Generate final validation report"""
        self.print_header("Final Validation Report")
        
        total_tests = 0
        passed_tests = 0
        
        # Count system health tests
        if "system_health" in self.results:
            for service, result in self.results["system_health"].items():
                total_tests += 1
                if result.get("status") == "healthy":
                    passed_tests += 1
        
        # Count workflow tests
        if "workflows" in self.results:
            for workflow, success in self.results["workflows"].items():
                total_tests += 1
                if success:
                    passed_tests += 1
        
        # Count WebSocket test
        if "websocket_connectivity" in self.results:
            total_tests += 1
            if self.results["websocket_connectivity"]:
                passed_tests += 1
        
        # Count performance tests
        if "performance" in self.results:
            for endpoint, metrics in self.results["performance"].items():
                total_tests += 1
                if metrics.get("success_rate", 0) >= 90 and metrics.get("avg_response_time", 999) < 1.0:
                    passed_tests += 1
        
        # Count security tests
        if "security" in self.results:
            for test, success in self.results["security"].items():
                total_tests += 1
                if success:
                    passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 VALIDATION SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"\n🎉 SYSTEM VALIDATION: ✅ PASSED")
            print(f"✅ System is ready for production deployment!")
        elif success_rate >= 75:
            print(f"\n⚠️  SYSTEM VALIDATION: 🔄 CONDITIONAL PASS")
            print(f"🔧 Some issues detected, review required")
        else:
            print(f"\n❌ SYSTEM VALIDATION: ❌ FAILED")
            print(f"🚨 Critical issues must be resolved")
        
        # Save results
        with open("day4_quick_validation_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: day4_quick_validation_report.json")
        
        return success_rate >= 90

async def main():
    """Run complete validation suite"""
    validator = Day4QuickValidation()
    
    print("🚀 DAY 4 QUICK SYSTEM VALIDATION")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Target: SmileAdventure Production Readiness")
    
    # Run all validation tests
    health_ok = validator.test_system_health()
    workflow_ok = validator.test_complete_user_workflow()
    websocket_ok = await validator.test_websocket_connectivity()
    performance_ok = validator.test_performance_benchmarks()
    security_ok = validator.test_security_basics()
    
    # Generate final report
    overall_success = validator.generate_final_report()
    
    return overall_success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n❌ Validation interrupted by user")
        exit(2)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        exit(3)
