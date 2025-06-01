#!/usr/bin/env python3
"""
Simplified Progress Tracking System Test
Tests the progress tracking system without authentication
"""

import json
from datetime import datetime, timedelta

import requests

# Test configuration
API_BASE = "http://localhost:8000/api/v1"

class SimpleProgressTest:
    def __init__(self):
        self.session = requests.Session()
        self.child_id = 1
        self.session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/progress/health")
            print(f"🏥 Health Check: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {data}")
                return True
            return False
        except Exception as e:
            print(f"❌ Health Check Error: {e}")
            return False
    
    def test_initialize_progress(self):
        """Test progress initialization"""
        try:
            child_profile = {
                "child_id": self.child_id,
                "name": "Test Child",
                "age": 8,
                "asd_support_level": 2,
                "sensory_profile": "mixed",
                "sensory_sensitivities": {
                    "auditory": 30,
                    "visual": 60,
                    "tactile": 40,
                    "vestibular": 50,
                    "proprioceptive": 55
                },
                "communication_preferences": {
                    "visual_supports": True,
                    "verbal_prompts": False,
                    "gesture_cues": True
                },
                "behavioral_patterns": {
                    "stimming_frequency": "moderate",
                    "transition_difficulty": "high",
                    "social_interaction_level": "emerging"
                },
                "interests": ["trains", "numbers", "music"],
                "triggers": ["loud_noises", "sudden_changes", "crowded_spaces"],
                "calming_strategies": ["deep_breathing", "fidget_toys", "quiet_space"]
            }
            
            request_data = {"child_profile": child_profile}
            
            response = self.session.post(f"{API_BASE}/progress/initialize", json=request_data)
            print(f"🚀 Initialize Progress: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Initialize Error: {e}")
            return False
    
    def test_behavioral_data(self):
        """Test behavioral data recording"""
        try:
            behavioral_data = [
                {
                    "timestamp": datetime.now().isoformat(),
                    "behavior_type": "emotional_regulation",
                    "intensity": 0.7,
                    "duration_seconds": 120,
                    "context": {"activity": "puzzle_solving", "environment": "quiet_room"},
                    "trigger": "task_difficulty",
                    "intervention_used": "visual_support",
                    "effectiveness_score": 0.8
                }
            ]
            
            request_data = {
                "child_id": self.child_id,
                "session_id": self.session_id,
                "behavioral_data": behavioral_data
            }
            
            response = self.session.post(f"{API_BASE}/progress/behavioral-data", json=request_data)
            print(f"📊 Behavioral Data: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Behavioral Data Error: {e}")
            return False
    
    def test_emotional_transitions(self):
        """Test emotional transitions recording"""
        try:
            transitions = [
                {
                    "timestamp": datetime.now().isoformat(),
                    "from_state": "calm",
                    "to_state": "excited",
                    "trigger_event": "new_activity_introduction",
                    "transition_duration": 30.0,
                    "support_needed": False,
                    "regulation_strategy_used": None
                }
            ]
            
            request_data = {
                "child_id": self.child_id,
                "session_id": self.session_id,
                "transitions": transitions
            }
            
            response = self.session.post(f"{API_BASE}/progress/emotional-transitions", json=request_data)
            print(f"😊 Emotional Transitions: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Emotional Transitions Error: {e}")
            return False
    
    def test_dashboard(self):
        """Test dashboard data"""
        try:
            params = {"days": 30}
            response = self.session.get(f"{API_BASE}/progress/dashboard/{self.child_id}", params=params)
            print(f"📈 Dashboard: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Dashboard Error: {e}")
            return False
    
    def run_tests(self):
        """Run all tests"""
        print("🎯 ASD Progress Tracking System - Simple Test")
        print("="*50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Initialize Progress", self.test_initialize_progress),
            ("Behavioral Data", self.test_behavioral_data),
            ("Emotional Transitions", self.test_emotional_transitions),
            ("Dashboard", self.test_dashboard)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔄 Testing {test_name}...")
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅ PASS' if success else '❌ FAIL'} {test_name}")
        
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📈 Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
        
        return passed == total

def main():
    """Main test execution"""
    tester = SimpleProgressTest()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the service status.")
        return 1

if __name__ == "__main__":
    exit(main())
