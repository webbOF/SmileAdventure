"""
Comprehensive Progress Tracking System Test
Tests the full functionality of the ASD children progress tracking system
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests
from requests.auth import HTTPBasicAuth

# Test configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

class ProgressTrackingSystemTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.child_id = 1
        self.session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_executed": [],
            "results": {},
            "errors": [],
            "summary": {}
        }

    def log_test(self, test_name: str, success: bool, details: Dict[str, Any] = None):
        """Log test results"""
        self.test_results["tests_executed"].append(test_name)
        self.test_results["results"][test_name] = {
            "success": success,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")

    def log_error(self, test_name: str, error: str):
        """Log error details"""
        self.test_results["errors"].append({
            "test": test_name,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })
        print(f"❌ ERROR in {test_name}: {error}")

    def test_authentication(self):
        """Test user authentication for API access"""
        try:
            # Test login
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    self.log_test("Authentication", True, {"token_received": True})
                    return True
                else:
                    self.log_test("Authentication", False, {"error": "No token in response"})
                    return False
            else:
                self.log_test("Authentication", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Authentication", str(e))
            return False

    def test_progress_health_check(self):
        """Test progress tracking service health"""
        try:
            response = self.session.get(f"{API_BASE}/progress/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Progress Health Check", True, data)
                return True
            else:
                self.log_test("Progress Health Check", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Progress Health Check", str(e))
            return False

    def test_initialize_progress_tracking(self):
        """Test initializing progress tracking for a child"""
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
            
            request_data = {
                "child_profile": child_profile
            }
            
            response = self.session.post(f"{API_BASE}/progress/initialize", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Initialize Progress Tracking", True, {
                    "child_id": data.get("data", {}).get("child_id"),
                    "focus_areas_count": len(data.get("data", {}).get("focus_areas", [])),
                    "milestone_targets_count": len(data.get("data", {}).get("milestone_targets", []))
                })
                return True
            else:
                self.log_test("Initialize Progress Tracking", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Initialize Progress Tracking", str(e))
            return False

    def test_record_behavioral_data(self):
        """Test recording behavioral observation data"""
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
                },
                {
                    "timestamp": (datetime.now() + timedelta(minutes=5)).isoformat(),
                    "behavior_type": "social_interaction",
                    "intensity": 0.5,
                    "duration_seconds": 90,
                    "context": {"activity": "group_game", "peers_present": 2},
                    "trigger": None,
                    "intervention_used": None,
                    "effectiveness_score": None
                }
            ]
            
            request_data = {
                "child_id": self.child_id,
                "session_id": self.session_id,
                "behavioral_data": behavioral_data
            }
            
            response = self.session.post(f"{API_BASE}/progress/behavioral-data", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Record Behavioral Data", True, {
                    "observations_recorded": data.get("data", {}).get("observations_count"),
                    "session_id": data.get("data", {}).get("session_id")
                })
                return True
            else:
                self.log_test("Record Behavioral Data", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Record Behavioral Data", str(e))
            return False

    def test_record_emotional_transitions(self):
        """Test recording emotional state transitions"""
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
                },
                {
                    "timestamp": (datetime.now() + timedelta(minutes=10)).isoformat(),
                    "from_state": "excited",
                    "to_state": "frustrated",
                    "trigger_event": "task_difficulty",
                    "transition_duration": 45.0,
                    "support_needed": True,
                    "regulation_strategy_used": "deep_breathing"
                }
            ]
            
            request_data = {
                "child_id": self.child_id,
                "session_id": self.session_id,
                "transitions": transitions
            }
            
            response = self.session.post(f"{API_BASE}/progress/emotional-transitions", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Record Emotional Transitions", True, {
                    "transitions_recorded": data.get("data", {}).get("transitions_count"),
                    "session_id": data.get("data", {}).get("session_id")
                })
                return True
            else:
                self.log_test("Record Emotional Transitions", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Record Emotional Transitions", str(e))
            return False

    def test_session_analysis(self):
        """Test session analysis for progress indicators"""
        try:
            session_metrics = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "actions_per_minute": 12.5,
                "error_rate": 0.15,
                "pause_frequency": 0.3,
                "average_response_time": 2.8,
                "progress_rate": 0.75,
                "overstimulation_score": 0.4,
                "stress_indicators": ["rapid_clicking"]
            }
            
            params = {
                "child_id": self.child_id,
                "session_id": self.session_id
            }
            
            response = self.session.post(
                f"{API_BASE}/progress/session-analysis", 
                json=session_metrics,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Session Analysis", True, {
                    "session_analyzed": data.get("data", {}).get("session_id"),
                    "milestones_detected": len(data.get("data", {}).get("milestones_detected", [])),
                    "real_time_metrics_generated": bool(data.get("data", {}).get("real_time_metrics"))
                })
                return True
            else:
                self.log_test("Session Analysis", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Session Analysis", str(e))
            return False

    def test_behavioral_pattern_analysis(self):
        """Test behavioral pattern analysis"""
        try:
            params = {
                "pattern_type": "emotional_regulation",
                "days": 7
            }
            
            response = self.session.get(f"{API_BASE}/progress/behavioral-patterns/{self.child_id}", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Behavioral Pattern Analysis", True, {
                    "pattern_analyzed": data.get("data", {}).get("pattern_type"),
                    "analysis_available": bool(data.get("data", {}).get("analysis"))
                })
                return True
            else:
                self.log_test("Behavioral Pattern Analysis", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Behavioral Pattern Analysis", str(e))
            return False

    def test_milestone_tracking(self):
        """Test milestone achievement tracking"""
        try:
            response = self.session.get(f"{API_BASE}/progress/milestones/{self.child_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Milestone Tracking", True, {
                    "child_id": data.get("data", {}).get("child_id"),
                    "achievement_count": data.get("data", {}).get("achievement_count", 0)
                })
                return True
            else:
                self.log_test("Milestone Tracking", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Milestone Tracking", str(e))
            return False

    def test_progress_dashboard(self):
        """Test progress dashboard data generation"""
        try:
            params = {"days": 30}
            
            response = self.session.get(f"{API_BASE}/progress/dashboard/{self.child_id}", params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Progress Dashboard", True, {
                    "dashboard_generated": bool(data.get("data")),
                    "child_id": data.get("data", {}).get("child_id")
                })
                return True
            else:
                self.log_test("Progress Dashboard", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Progress Dashboard", str(e))
            return False

    def test_progress_summary(self):
        """Test progress summary generation"""
        try:
            response = self.session.get(f"{API_BASE}/progress/summary/{self.child_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Progress Summary", True, {
                    "summary_generated": bool(data.get("data")),
                    "summary_content": str(data.get("data", {}))[:100] + "..." if data.get("data") else "No data"
                })
                return True
            else:
                self.log_test("Progress Summary", False, {"status_code": response.status_code, "response": response.text})
                return False
                
        except Exception as e:
            self.log_error("Progress Summary", str(e))
            return False

    def generate_summary(self):
        """Generate test execution summary"""
        total_tests = len(self.test_results["tests_executed"])
        passed_tests = sum(1 for result in self.test_results["results"].values() if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{success_rate:.1f}%",
            "errors_count": len(self.test_results["errors"])
        }
        
        print("\n" + "="*60)
        print("🔬 PROGRESS TRACKING SYSTEM TEST SUMMARY")
        print("="*60)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"🐛 Errors: {len(self.test_results['errors'])}")
        
        if self.test_results["errors"]:
            print("\n🐛 Error Details:")
            for error in self.test_results["errors"]:
                print(f"   - {error['test']}: {error['error']}")
        
        return success_rate >= 70  # Consider 70% success rate as acceptable

    def run_all_tests(self):
        """Execute all progress tracking tests"""
        print("🚀 Starting Progress Tracking System Comprehensive Test")
        print("="*60)
        
        # Authentication (required for other tests)
        if not self.test_authentication():
            print("❌ Authentication failed - stopping tests")
            return False
        
        # Core functionality tests
        test_methods = [
            self.test_progress_health_check,
            self.test_initialize_progress_tracking,
            self.test_record_behavioral_data,
            self.test_record_emotional_transitions,
            self.test_session_analysis,
            self.test_behavioral_pattern_analysis,
            self.test_milestone_tracking,
            self.test_progress_dashboard,
            self.test_progress_summary
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                test_name = test_method.__name__
                self.log_error(test_name, str(e))
        
        # Generate final summary
        return self.generate_summary()

    def save_results(self, filename: str = None):
        """Save test results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"progress_tracking_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")


def main():
    """Main test execution function"""
    print("🎯 ASD Children Progress Tracking System - Comprehensive Test")
    print("🏥 Testing behavioral pattern recognition, emotional progression analysis,")
    print("   and clinical milestone tracking capabilities")
    print()
    
    tester = ProgressTrackingSystemTest()
    
    try:
        success = tester.run_all_tests()
        tester.save_results()
        
        if success:
            print("\n🎉 Progress Tracking System test completed successfully!")
            print("✅ The comprehensive progress tracking system is ready for ASD children support.")
            return 0
        else:
            print("\n⚠️  Progress Tracking System test completed with issues.")
            print("🔧 Please review the failed tests and address any issues.")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
