# filepath: c:\Users\arman\Desktop\SeriousGame\test_task2_2_progress_tracking_fixed.py
"""
Task 2.2: Progress Tracking & Metrics - Comprehensive Validation Test
Tests the complete progress tracking system including behavioral pattern recognition,
emotional state progression analysis, and clinical milestone tracking.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests


class Task22ProgressTrackingValidator:
    """Comprehensive validator for Task 2.2: Progress Tracking & Metrics"""
    
    def __init__(self):
        self.base_url = "http://localhost:8005/api/v1/game"
        self.results = {
            "test_suite": "Task 2.2: Progress Tracking & Metrics",
            "timestamp": datetime.now().isoformat(),
            "overall_status": "PENDING",
            "tests": {},
            "summary": {}
        }
        
    def log_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test result"""
        self.results["tests"][test_name] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details        }
        print(f"✅ {test_name}: {status}" if status == "PASSED" else f"❌ {test_name}: {status}")
    
    def test_service_health(self) -> bool:
        """Test if the Game service with progress tracking is running"""
        try:
            response = requests.get(f"http://localhost:8005/status", timeout=10)
            if response.status_code == 200:
                self.log_result("service_health", "PASSED", {"response": response.json()})
                return True
            else:
                self.log_result("service_health", "FAILED", {"status_code": response.status_code})
                return False
        except Exception as e:
            self.log_result("service_health", "FAILED", {"error": str(e)})
            return False
    
    def test_progress_tracking_initialization(self) -> bool:
        """Test progress tracking initialization endpoint"""
        try:
            # Sample child profile data with correct validation format
            child_profile = {
                "child_id": 12345,
                "name": "Test Child",
                "age": 8,
                "asd_support_level": 2,  # Integer instead of string "level_2"
                "communication_preferences": {  # Object instead of array
                    "visual": True,
                    "simple_language": True,
                    "verbal": False,
                    "gestures": True
                },                "sensory_sensitivities": {
                    "auditory": 25,
                    "visual": 40,
                    "tactile": 30,
                    "vestibular": 60,
                    "proprioceptive": 50
                },"sensory_profile": "mixed",  # Fixed: Use enum string value directly
                "behavioral_triggers": ["sudden_changes", "crowded_spaces"],
                "interests": ["puzzles", "animals"],
                "attention_span_minutes": 15,
                "motor_skills_level": "developing",
                "social_comfort_level": "small_groups"
            }
            
            init_data = {
                "child_profile": child_profile,
                "config": {
                    "child_id": 12345,  # Added missing required field
                    "tracking_frequency": "5_minutes",  # Fixed: Use string value
                    "tracking_frequency_minutes": 5,
                    "behavioral_analysis_enabled": True,
                    "emotional_tracking_enabled": True,
                    "milestone_tracking_enabled": True,
                    "intervention_threshold": 0.7,
                    "alert_threshold": 0.8
                }
            }
            
            response = requests.post(
                f"{self.base_url}/progress/initialize",
                json=init_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_result("progress_tracking_initialization", "PASSED", {
                    "response": response.json(),
                    "child_profile": child_profile
                })
                return True
            else:
                self.log_result("progress_tracking_initialization", "FAILED", {
                    "status_code": response.status_code,
                    "response": response.text,
                    "data_sent": init_data
                })
                return False
                
        except Exception as e:
            self.log_result("progress_tracking_initialization", "FAILED", {"error": str(e)})
            return False

    def test_behavioral_data_recording(self) -> bool:
        """Test behavioral data recording endpoint"""
        try:
            behavioral_data = {
                "child_id": 12345,
                "session_id": "test_session_001",
                "observations": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "behavior_type": "sensory_processing",
                        "intensity": 0.7,
                        "duration_seconds": 120,
                        "context": {"activity": "puzzle_solving", "environment": "quiet_room"},
                        "triggers": ["new_texture"],
                        "interventions_used": ["sensory_break"]
                    },
                    {
                        "timestamp": (datetime.now() + timedelta(minutes=5)).isoformat(),
                        "behavior_type": "emotional_regulation",
                        "intensity": 0.8,
                        "duration_seconds": 180,
                        "context": {"activity": "group_activity", "environment": "classroom"},
                        "triggers": ["peer_interaction"],
                        "interventions_used": ["calming_strategy"]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/progress/behavioral-data",
                json=behavioral_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_result("behavioral_data_recording", "PASSED", {"response": response.json()})
                return True
            else:
                self.log_result("behavioral_data_recording", "FAILED", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("behavioral_data_recording", "FAILED", {"error": str(e)})
            return False

    def test_emotional_transition_tracking(self) -> bool:
        """Test emotional transition tracking endpoint"""
        try:
            emotional_data = {
                "child_id": 12345,
                "session_id": "test_session_001",
                "transitions": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "from_state": "calm",
                        "to_state": "excited",
                        "trigger": "new_activity",
                        "duration_minutes": 3,
                        "transition_duration": 180,  # Added missing required field (in seconds)
                        "intensity_change": 0.4,
                        "context": {"activity": "game_start", "social_setting": "individual"}
                    },
                    {
                        "timestamp": (datetime.now() + timedelta(minutes=10)).isoformat(),
                        "from_state": "excited",
                        "to_state": "frustrated",
                        "trigger": "difficulty_increase",
                        "duration_minutes": 2,
                        "transition_duration": 120,  # Added missing required field (in seconds)
                        "intensity_change": 0.6,
                        "context": {"activity": "puzzle_challenge", "social_setting": "individual"}
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/progress/emotional-transitions",
                json=emotional_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_result("emotional_transition_tracking", "PASSED", {"response": response.json()})
                return True
            else:
                self.log_result("emotional_transition_tracking", "FAILED", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("emotional_transition_tracking", "FAILED", {"error": str(e)})
            return False

    def test_skill_assessment_recording(self) -> bool:
        """Test skill assessment recording endpoint"""
        try:
            skill_data = {
                "child_id": 12345,
                "session_id": "test_session_001",
                "assessments": [
                    {
                        "skill_name": "communication_verbal",
                        "skill_category": "communication",
                        "current_score": 0.75,
                        "baseline_score": 0.6,
                        "target_score": 0.9,
                        "assessment_method": "structured_observation",
                        "notes": "Improved sentence structure and vocabulary usage"
                    },
                    {
                        "skill_name": "social_interaction",
                        "skill_category": "social",
                        "current_score": 0.65,
                        "baseline_score": 0.5,
                        "target_score": 0.8,
                        "assessment_method": "peer_interaction_assessment",
                        "notes": "Better turn-taking and eye contact"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/progress/skill-assessments",
                json=skill_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_result("skill_assessment_recording", "PASSED", {"response": response.json()})
                return True
            else:
                self.log_result("skill_assessment_recording", "FAILED", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("skill_assessment_recording", "FAILED", {"error": str(e)})
            return False

    def test_real_time_metrics(self) -> bool:
        """Test real-time metrics endpoint"""
        try:
            session_id = "test_session_001"
            response = requests.get(
                f"{self.base_url}/progress/real-time-metrics/{session_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                metrics = response.json()
                self.log_result("real_time_metrics", "PASSED", {"metrics": metrics})
                return True
            else:
                self.log_result("real_time_metrics", "FAILED", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("real_time_metrics", "FAILED", {"error": str(e)})
            return False

    def test_behavioral_pattern_analysis(self) -> bool:
        """Test behavioral pattern analysis endpoint"""
        try:
            child_id = 12345
            response = requests.get(
                f"{self.base_url}/progress/behavioral-patterns/{child_id}?pattern_type=sensory_processing",
                timeout=30
            )
            
            if response.status_code == 200:
                patterns = response.json()
                self.log_result("behavioral_pattern_analysis", "PASSED", {"patterns": patterns})
                return True
            else:
                self.log_result("behavioral_pattern_analysis", "FAILED", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("behavioral_pattern_analysis", "FAILED", {"error": str(e)})
            return False

    def test_child_metrics_retrieval(self) -> bool:
        """Test child metrics retrieval endpoint"""
        try:
            child_id = 12345
            response = requests.get(
                f"{self.base_url}/progress/child-metrics/{child_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                metrics = response.json()
                self.log_result("child_metrics_retrieval", "PASSED", {"metrics": metrics})
                return True
            else:
                self.log_result("child_metrics_retrieval", "FAILED", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("child_metrics_retrieval", "FAILED", {"error": str(e)})
            return False

    def test_dashboard_data_generation(self) -> bool:
        """Test dashboard data generation endpoint"""
        try:
            child_id = 12345
            days = 7
            response = requests.get(
                f"{self.base_url}/progress/dashboard/{child_id}?days={days}",
                timeout=30
            )
            
            if response.status_code == 200:
                dashboard = response.json()
                self.log_result("dashboard_data_generation", "PASSED", {"dashboard": dashboard})
                return True
            else:
                self.log_result("dashboard_data_generation", "FAILED", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("dashboard_data_generation", "FAILED", {"error": str(e)})
            return False

    def test_long_term_progress_report(self) -> bool:
        """Test long-term progress report endpoint"""
        try:
            child_id = 12345
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
            end_date = datetime.now().isoformat()
            
            response = requests.get(
                f"{self.base_url}/progress/long-term-report/{child_id}?start_date={start_date}&end_date={end_date}&include_recommendations=true",
                timeout=30
            )
            
            if response.status_code == 200:
                report = response.json()
                self.log_result("long_term_progress_report", "PASSED", {"report": report})
                return True
            else:
                self.log_result("long_term_progress_report", "FAILED", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("long_term_progress_report", "FAILED", {"error": str(e)})
            return False

    def run_all_tests(self):
        """Run all validation tests"""
        print("🧪 Starting Task 2.2: Progress Tracking & Metrics Validation")
        print("=" * 60)
        
        # List of all test methods
        tests = [
            self.test_service_health,
            self.test_progress_tracking_initialization,
            self.test_behavioral_data_recording,
            self.test_emotional_transition_tracking,
            self.test_skill_assessment_recording,
            self.test_real_time_metrics,
            self.test_behavioral_pattern_analysis,
            self.test_child_metrics_retrieval,
            self.test_dashboard_data_generation,
            self.test_long_term_progress_report
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ {test.__name__}: EXCEPTION - {str(e)}")
        
        # Generate summary
        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": f"{(passed/total)*100:.1f}%",
            "overall_status": "PASSED" if passed == total else "PARTIAL" if passed > 0 else "FAILED"
        }
        
        self.results["overall_status"] = self.results["summary"]["overall_status"]
        
        # Print summary
        print("\n" + "=" * 60)
        print("🧪 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Overall Status: {self.results['summary']['overall_status']}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"task2_2_progress_tracking_validation_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n📊 Detailed results saved to: {filename}")
        
        return self.results


if __name__ == "__main__":
    validator = Task22ProgressTrackingValidator()
    results = validator.run_all_tests()
