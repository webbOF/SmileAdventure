#!/usr/bin/env python3
"""
Comprehensive Game Session Testing Script for WEBBOF
Tests the complete game session workflow including creation, actions, and state management.
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000/api/v1"

class GameSessionTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.session_id = None
        self.test_email = f"gametester_{int(time.time())}@example.com"
        
    def print_test_header(self, test_name: str):
        print(f"\n{'='*60}")
        print(f"🎮 {test_name}")
        print(f"{'='*60}")
    
    def print_success(self, message: str):
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        print(f"ℹ️  {message}")

    def register_test_user(self) -> bool:
        """Register a test user for game session testing"""
        self.print_test_header("User Registration for Game Testing")
        
        user_data = {
            "name": "Game Tester",
            "email": self.test_email,
            "password": "testpass123",
            "role": "parent"
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/register", json=user_data)
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"User registered successfully: {result}")
                return True
            else:
                self.print_error(f"Registration failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Registration error: {e}")
            return False

    def login_test_user(self) -> bool:
        """Login the test user and get JWT token"""
        self.print_test_header("User Login for Game Testing")
        
        login_data = {
            "email": self.test_email,
            "password": "testpass123"  
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                result = response.json()
                self.user_token = result["access_token"]
                self.user_id = result["user"]["id"]
                self.session.headers.update({"Authorization": f"Bearer {self.user_token}"})
                self.print_success(f"Login successful! User ID: {self.user_id}")
                return True
            else:
                self.print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Login error: {e}")
            return False

    def test_game_health(self) -> bool:
        """Test Game service health"""
        self.print_test_header("Game Service Health Check")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/game/health")
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"Game service is healthy: {result}")
                return True
            else:
                self.print_error(f"Health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Health check error: {e}")
            return False

    def test_get_scenarios(self) -> bool:
        """Test getting available game scenarios"""
        self.print_test_header("Get Available Game Scenarios")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/game/scenarios")
            if response.status_code == 200:
                result = response.json()
                self.print_success(f"Scenarios retrieved: {json.dumps(result, indent=2)}")
                return True
            else:
                self.print_error(f"Failed to get scenarios: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Get scenarios error: {e}")
            return False

    def test_start_game_session(self) -> bool:
        """Test starting a new game session"""
        self.print_test_header("Start New Game Session")
        
        if not self.user_id:
            self.print_error("No user ID available. Please login first.")
            return False
        
        start_game_data = {
            "user_id": self.user_id,
            "scenario_id": "basic_adventure",
            "difficulty_level": 1
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/game/start", json=start_game_data)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.session_id = result.get("session_id")
                    self.print_success(f"Game session started successfully!")
                    self.print_info(f"Session ID: {self.session_id}")
                    self.print_info(f"Response: {json.dumps(result, indent=2)}")
                    return True
                else:
                    self.print_error(f"Game start failed: {result.get('message')}")
                    return False
            else:
                self.print_error(f"Failed to start game: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Start game error: {e}")
            return False

    def test_get_game_state(self) -> bool:
        """Test getting current game state"""
        self.print_test_header("Get Current Game State")
        
        if not self.session_id or not self.user_id:
            self.print_error("No session ID or user ID available.")
            return False
        
        try:
            params = {
                "session_id": self.session_id,
                "user_id": self.user_id
            }
            response = self.session.get(f"{API_BASE_URL}/game/state", params=params)
            if response.status_code == 200:
                result = response.json()
                self.print_success("Game state retrieved successfully!")
                self.print_info(f"Game State: {json.dumps(result, indent=2)}")
                return True
            else:
                self.print_error(f"Failed to get game state: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Get game state error: {e}")
            return False

    def test_game_action(self) -> bool:
        """Test processing a game action"""
        self.print_test_header("Process Game Action")
        
        if not self.session_id or not self.user_id:
            self.print_error("No session ID or user ID available.")
            return False
        
        action_data = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "action_type": "move",
            "position": {"x": 10, "y": 15},
            "target": "garden_entrance",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/game/action", json=action_data)
            if response.status_code == 200:
                result = response.json()
                self.print_success("Game action processed successfully!")
                self.print_info(f"Action Result: {json.dumps(result, indent=2)}")
                return True
            else:
                self.print_error(f"Failed to process action: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Game action error: {e}")
            return False

    def test_end_game_session(self) -> bool:
        """Test ending a game session"""
        self.print_test_header("End Game Session")
        
        if not self.session_id or not self.user_id:
            self.print_error("No session ID or user ID available.")
            return False
        
        end_game_data = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "final_score": 85,
            "completion_reason": "normal"
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/game/end", json=end_game_data)
            if response.status_code == 200:
                result = response.json()
                self.print_success("Game session ended successfully!")
                self.print_info(f"End Game Result: {json.dumps(result, indent=2)}")
                return True
            else:
                self.print_error(f"Failed to end game: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.print_error(f"End game error: {e}")
            return False

    def run_comprehensive_test(self):
        """Run all game session tests"""
        print("🚀 Starting Comprehensive Game Session Testing")
        print(f"⏰ Test started at: {datetime.now()}")
        
        tests = [
            ("Game Service Health", self.test_game_health),
            ("Get Game Scenarios", self.test_get_scenarios),
            ("User Registration", self.register_test_user),
            ("User Login", self.login_test_user),
            ("Start Game Session", self.test_start_game_session),
            ("Get Game State", self.test_get_game_state),
            ("Process Game Action", self.test_game_action),
            ("Get Updated Game State", self.test_get_game_state),
            ("End Game Session", self.test_end_game_session)
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
        print(f"🏁 GAME SESSION TESTING COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "N/A")
        print(f"⏰ Test completed at: {datetime.now()}")

if __name__ == "__main__":
    tester = GameSessionTester()
    tester.run_comprehensive_test()
