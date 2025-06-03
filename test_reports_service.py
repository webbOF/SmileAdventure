#!/usr/bin/env python3
"""
Comprehensive Reports Service Testing Script for WEBBOF
Tests the reporting and analytics functionality of the system.
"""

import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000/api/v1"

class ReportsServiceTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_email = f"reportstester_{int(time.time())}@example.com"
        
    def print_test_header(self, test_name: str):
        print(f"\n{'='*60}")
        print(f"📊 {test_name}")
        print(f"{'='*60}")
    
    def print_success(self, message: str):
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        print(f"ℹ️  {message}")

    def setup_test_user(self) -> bool:
        """Register and login a test user"""
        self.print_test_header("Setup Test User for Reports Testing")
        
        # Register user
        user_data = {
            "name": "Reports Tester",
            "email": self.test_email,
            "password": "testpass123",
            "role": "parent"
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/register", json=user_data)
            if response.status_code == 200:
                self.print_success("User registered successfully")
                
                # Login user
                login_data = {
                    "email": self.test_email,
                    "password": "testpass123"
                }
                
                login_response = self.session.post(f"{API_BASE_URL}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    result = login_response.json()
                    self.user_token = result["access_token"]
                    self.user_id = result["user"]["id"]
                    self.session.headers.update({"Authorization": f"Bearer {self.user_token}"})
                    self.print_success(f"Login successful! User ID: {self.user_id}")
                    return True
                else:
                    self.print_error(f"Login failed: {login_response.status_code}")
                    return False
            else:
                self.print_error(f"Registration failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Setup error: {e}")
            return False

    def test_reports_health(self) -> bool:
        """Test Reports service health"""
        self.print_test_header("Reports Service Health Check")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/reports/health")
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"Reports service is healthy: {result}")
                return True
            else:
                self.print_error(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Health check error: {e}")
            return False

    def test_submit_game_session_data(self) -> bool:
        """Test submitting game session data to reports service"""
        self.print_test_header("Submit Game Session Data")
        
        if not self.user_id:
            self.print_error("No user ID available")
            return False
        
        # Create sample game session data
        session_data = {
            "user_id": self.user_id,
            "session_id": f"test-session-{int(time.time())}",
            "start_time": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "end_time": datetime.now().isoformat(),
            "emotions_detected": [
                {"emotion": "happy", "intensity": 0.8, "timestamp": datetime.now().isoformat()},
                {"emotion": "excited", "intensity": 0.6, "timestamp": datetime.now().isoformat()}
            ],
            "game_level": "basic_adventure",
            "score": 85
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/reports/game-session", json=session_data)
            if response.status_code == 201:
                result = response.json()
                self.print_success("Game session data submitted successfully!")
                self.print_info(f"Response: {json.dumps(result, indent=2)}")
                return True
            else:
                self.print_error(f"Failed to submit session data: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Submit session data error: {e}")
            return False

    def test_get_child_summary(self) -> bool:
        """Test getting child progress summary"""
        self.print_test_header("Get Child Progress Summary")
        
        if not self.user_id:
            self.print_error("No user ID available")
            return False
        
        # Use user_id as child_id for testing
        child_id = self.user_id
        
        try:
            response = self.session.get(f"{API_BASE_URL}/reports/child/{child_id}/summary")
            if response.status_code == 200:
                result = response.json()
                self.print_success("Child summary retrieved successfully!")
                self.print_info(f"Summary: {json.dumps(result, indent=2)}")
                return True
            elif response.status_code == 404:
                self.print_info("No summary data available yet (expected for new test user)")
                return True  # This is expected for new users
            else:
                self.print_error(f"Failed to get child summary: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Get child summary error: {e}")
            return False

    def test_get_emotion_patterns(self) -> bool:
        """Test getting child emotion patterns"""
        self.print_test_header("Get Child Emotion Patterns")
        
        if not self.user_id:
            self.print_error("No user ID available")
            return False
        
        # Use user_id as child_id for testing
        child_id = self.user_id
        
        try:
            response = self.session.get(f"{API_BASE_URL}/reports/child/{child_id}/emotion-patterns")
            if response.status_code == 200:
                result = response.json()
                self.print_success("Emotion patterns retrieved successfully!")
                self.print_info(f"Patterns: {json.dumps(result, indent=2)}")
                return True
            else:
                self.print_error(f"Failed to get emotion patterns: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Get emotion patterns error: {e}")
            return False

    def test_platform_activity(self) -> bool:
        """Test platform activity overview endpoint"""
        self.print_test_header("Platform Activity Overview")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/reports/overall-platform-activity")
            if response.status_code == 200:
                result = response.json()
                self.print_success("Platform activity overview retrieved!")
                self.print_info(f"Overview: {json.dumps(result, indent=2)}")
                return True
            else:
                self.print_error(f"Failed to get platform activity: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Platform activity error: {e}")
            return False

    def run_comprehensive_test(self):
        """Run all reports service tests"""
        print("🚀 Starting Comprehensive Reports Service Testing")
        print(f"⏰ Test started at: {datetime.now()}")
        
        tests = [
            ("Reports Service Health", self.test_reports_health),
            ("Setup Test User", self.setup_test_user),
            ("Submit Game Session Data", self.test_submit_game_session_data),
            ("Get Child Summary", self.test_get_child_summary),
            ("Get Emotion Patterns", self.test_get_emotion_patterns),
            ("Platform Activity Overview", self.test_platform_activity)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.print_error(f"Test '{test_name}' crashed: {e}")
                failed += 1
            
            time.sleep(1)  # Brief pause between tests
        
        # Final Results
        print(f"\n{'='*60}")
        print(f"🏁 REPORTS SERVICE TESTING COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "N/A")
        print(f"⏰ Test completed at: {datetime.now()}")

if __name__ == "__main__":
    tester = ReportsServiceTester()
    tester.run_comprehensive_test()
