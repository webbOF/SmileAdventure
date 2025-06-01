#!/usr/bin/env python3
"""
Task 2.2 Progress Tracking System Validation
Comprehensive validation of the enhanced progress tracking system
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from models.asd_models import (ASDSupportLevel, BehavioralDataPoint,
                                   BehavioralPattern, ChildProfile,
                                   ClinicalMilestone, EmotionalState,
                                   EmotionalStateTransition,
                                   ProgressTrackingConfig, SkillAssessment)
    from services.progress_tracking_service import ProgressTrackingService
    print("✅ Successfully imported progress tracking components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

class ProgressTrackingValidator:
    """Comprehensive validator for the progress tracking system"""
    
    def __init__(self):
        self.progress_service = ProgressTrackingService()
        self.test_results = []
        self.validation_summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name: str, status: str, message: str = "", details: dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        if status == "PASS":
            print(f"✅ {test_name}: {message}")
            self.validation_summary["passed"] += 1
        elif status == "FAIL":
            print(f"❌ {test_name}: {message}")
            self.validation_summary["failed"] += 1
        else:
            print(f"ℹ️ {test_name}: {message}")
        
        self.validation_summary["total_tests"] += 1

    async def test_1_service_initialization(self):
        """Test 1: Service Initialization"""
        try:
            service = ProgressTrackingService()
            
            # Check if service is properly initialized
            if hasattr(service, 'behavioral_data') and hasattr(service, 'emotional_transitions'):
                self.log_result("Service Initialization", "PASS", "Service initialized with required attributes")
            else:
                self.log_result("Service Initialization", "FAIL", "Service missing required attributes")
                
        except Exception as e:
            self.log_result("Service Initialization", "FAIL", f"Exception during initialization: {str(e)}")

    async def test_2_child_profile_setup(self):
        """Test 2: Child Profile Setup"""
        try:
            test_profile = ChildProfile(
                child_id=1,
                name="Test Child",
                age_months=60,
                asd_support_level=ASDSupportLevel.LEVEL_2,
                communication_preferences=["visual", "verbal"],
                sensory_sensitivities=["noise", "light"],
                interests=["trains", "counting"],
                triggers=["loud noises", "changes in routine"],
                effective_strategies=["visual schedules", "quiet breaks"]
            )
            
            result = await self.progress_service.setup_child_profile(test_profile)
            
            if result and result.get("status") == "success":
                self.log_result("Child Profile Setup", "PASS", "Profile created successfully", result)
            else:
                self.log_result("Child Profile Setup", "FAIL", "Profile setup failed", result)
                
        except Exception as e:
            self.log_result("Child Profile Setup", "FAIL", f"Exception: {str(e)}")

    async def test_3_behavioral_data_recording(self):
        """Test 3: Behavioral Data Recording"""
        try:
            # Record various behavioral observations
            behaviors_to_test = [
                (BehavioralPattern.REPETITIVE_MOVEMENTS, 0.6, 120),
                (BehavioralPattern.SOCIAL_INTERACTION, 0.8, 300),
                (BehavioralPattern.SENSORY_PROCESSING, 0.4, 180)
            ]
            
            results = []
            for behavior, intensity, duration in behaviors_to_test:
                result = await self.progress_service.record_behavioral_observation(
                    child_id=1,
                    session_id="test_session_1",
                    behavior_type=behavior,
                    intensity=intensity,
                    duration_seconds=duration,
                    context={"environment": "therapy_room", "activity": "free_play"},
                    trigger="routine_change",
                    intervention_used="visual_schedule"
                )
                results.append(result)
            
            if all(results):
                self.log_result("Behavioral Data Recording", "PASS", 
                              f"Recorded {len(results)} behavioral observations")
            else:
                self.log_result("Behavioral Data Recording", "FAIL", "Failed to record some observations")
                
        except Exception as e:
            self.log_result("Behavioral Data Recording", "FAIL", f"Exception: {str(e)}")

    async def test_4_emotional_state_tracking(self):
        """Test 4: Emotional State Tracking"""
        try:
            # Test emotional state transitions
            transitions = [
                (EmotionalState.CALM, EmotionalState.EXCITED, 0.7, False),
                (EmotionalState.EXCITED, EmotionalState.OVERWHELMED, 0.9, True),
                (EmotionalState.OVERWHELMED, EmotionalState.CALM, 0.3, False)
            ]
            
            results = []
            for from_state, to_state, intensity, support_needed in transitions:
                result = await self.progress_service.record_emotional_transition(
                    child_id=1,
                    session_id="test_session_1",
                    from_state=from_state,
                    to_state=to_state,
                    intensity=intensity,
                    support_needed=support_needed,
                    context={"trigger": "sensory_input", "duration": 60},
                    intervention_used="deep_breathing" if support_needed else None
                )
                results.append(result)
            
            if all(results):
                self.log_result("Emotional State Tracking", "PASS", 
                              f"Recorded {len(results)} emotional transitions")
            else:
                self.log_result("Emotional State Tracking", "FAIL", "Failed to record transitions")
                
        except Exception as e:
            self.log_result("Emotional State Tracking", "FAIL", f"Exception: {str(e)}")

    async def test_5_skill_assessments(self):
        """Test 5: Skill Assessments"""
        try:
            # Test skill assessments
            skills = [
                ("attention_span", "cognitive", 0.7, 0.8),
                ("emotional_regulation", "behavioral", 0.6, 0.7),
                ("social_interaction", "social", 0.5, 0.6)
            ]
            
            assessments = []
            for skill_name, category, current, target in skills:
                assessment = SkillAssessment(
                    skill_name=skill_name,
                    category=category,
                    current_score=current,
                    target_score=target,
                    assessment_date=datetime.now(),
                    assessment_method="observation",
                    notes=f"Test assessment for {skill_name}"
                )
                assessments.append(assessment)
            
            result = await self.progress_service.record_skill_assessments(
                child_id=1,
                session_id="test_session_1",
                skill_assessments=assessments
            )
            
            if result and result.get("assessments_recorded", 0) > 0:
                self.log_result("Skill Assessments", "PASS", 
                              f"Recorded {result['assessments_recorded']} assessments")
            else:
                self.log_result("Skill Assessments", "FAIL", "Failed to record assessments")
                
        except Exception as e:
            self.log_result("Skill Assessments", "FAIL", f"Exception: {str(e)}")

    async def test_6_milestone_tracking(self):
        """Test 6: Milestone Tracking"""
        try:
            # Test milestone achievement recording
            result = await self.progress_service.record_milestone_achievement(
                child_id=1,
                milestone=ClinicalMilestone.EMOTIONAL_REGULATION_IMPROVEMENT,
                session_id="test_session_1",
                confidence_level=0.85,
                supporting_evidence=["consistent calm responses", "self-regulation strategies used"]
            )
            
            if result:
                self.log_result("Milestone Tracking", "PASS", "Milestone recorded successfully")
            else:
                self.log_result("Milestone Tracking", "FAIL", "Failed to record milestone")
                
        except Exception as e:
            self.log_result("Milestone Tracking", "FAIL", f"Exception: {str(e)}")

    async def test_7_real_time_metrics(self):
        """Test 7: Real-time Metrics Collection"""
        try:
            metrics = await self.progress_service.get_real_time_metrics(child_id=1)
            
            expected_keys = ["emotional_state", "behavioral_patterns", "skill_progress", "alert_status"]
            missing_keys = [key for key in expected_keys if key not in metrics]
            
            if not missing_keys:
                self.log_result("Real-time Metrics", "PASS", "All expected metrics available")
            else:
                self.log_result("Real-time Metrics", "FAIL", f"Missing metrics: {missing_keys}")
                
        except Exception as e:
            self.log_result("Real-time Metrics", "FAIL", f"Exception: {str(e)}")

    async def test_8_pattern_analysis(self):
        """Test 8: Pattern Analysis"""
        try:
            analysis = await self.progress_service.analyze_behavioral_patterns(child_id=1)
            
            if analysis and len(analysis) > 0:
                self.log_result("Pattern Analysis", "PASS", 
                              f"Generated {len(analysis)} behavioral pattern analyses")
            else:
                self.log_result("Pattern Analysis", "FAIL", "No pattern analysis generated")
                
        except Exception as e:
            self.log_result("Pattern Analysis", "FAIL", f"Exception: {str(e)}")

    async def test_9_dashboard_generation(self):
        """Test 9: Dashboard Generation"""
        try:
            dashboard = await self.progress_service.generate_progress_dashboard(child_id=1)
            
            expected_sections = ["summary", "behavioral_trends", "emotional_progress", "skills_overview"]
            missing_sections = [section for section in expected_sections if section not in dashboard]
            
            if not missing_sections:
                self.log_result("Dashboard Generation", "PASS", "Complete dashboard generated")
            else:
                self.log_result("Dashboard Generation", "FAIL", f"Missing sections: {missing_sections}")
                
        except Exception as e:
            self.log_result("Dashboard Generation", "FAIL", f"Exception: {str(e)}")

    async def test_10_comprehensive_reporting(self):
        """Test 10: Comprehensive Reporting"""
        try:
            report = await self.progress_service.generate_comprehensive_report(
                child_id=1,
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now()
            )
            
            if report and report.get("child_id") == 1:
                self.log_result("Comprehensive Reporting", "PASS", "Report generated successfully")
            else:
                self.log_result("Comprehensive Reporting", "FAIL", "Failed to generate report")
                
        except Exception as e:
            self.log_result("Comprehensive Reporting", "FAIL", f"Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting Progress Tracking System Validation")
        print("=" * 60)
        
        test_methods = [
            self.test_1_service_initialization,
            self.test_2_child_profile_setup,
            self.test_3_behavioral_data_recording,
            self.test_4_emotional_state_tracking,
            self.test_5_skill_assessments,
            self.test_6_milestone_tracking,
            self.test_7_real_time_metrics,
            self.test_8_pattern_analysis,
            self.test_9_dashboard_generation,
            self.test_10_comprehensive_reporting
        ]
        
        for test_method in test_methods:
            await test_method()
            print()  # Add spacing between tests
        
        # Generate summary
        print("=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.validation_summary['total_tests']}")
        print(f"Passed: {self.validation_summary['passed']}")
        print(f"Failed: {self.validation_summary['failed']}")
        
        success_rate = (self.validation_summary['passed'] / self.validation_summary['total_tests']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        return self.validation_summary

    def save_results(self):
        """Save validation results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../../task2_2_progress_tracking_validation_{timestamp}.json"
        
        output = {
            "validation_summary": self.validation_summary,
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat(),
            "task": "Task 2.2: Progress Tracking & Metrics"
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"📁 Results saved to: {filename}")
        return filename

async def main():
    """Main validation function"""
    validator = ProgressTrackingValidator()
    
    try:
        summary = await validator.run_all_tests()
        validator.save_results()
        
        # Return appropriate exit code
        if summary['failed'] > 0:
            print("❌ Some tests failed. Review the results above.")
            return 1
        else:
            print("✅ All tests passed successfully!")
            return 0
            
    except Exception as e:
        print(f"💥 Critical error during validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
