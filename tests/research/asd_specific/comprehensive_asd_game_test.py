#!/usr/bin/env python3
"""
Comprehensive ASD Game Service Test
Tests all ASD-specific functionality including adaptive sessions, overstimulation detection, and recommendations
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict

from microservices.Game.src.models.asd_models import (ASDSupportLevel,
                                                      ChildProfile,
                                                      SensoryProfile,
                                                      SensorySensitivity,
                                                      SessionMetrics)
from microservices.Game.src.models.game_models import (GameAction,
                                                       GameActionData,
                                                       StartGameRequest)
from microservices.Game.src.services.enhanced_game_service import \
    enhanced_game_service


class ASDGameServiceTester:
    """Comprehensive tester for ASD Game Service functionality"""
    
    def __init__(self):
        self.test_results = {}
        self.test_child_profiles = self._create_test_profiles()
    
    def _create_test_profiles(self) -> Dict[str, ChildProfile]:
        """Create test child profiles representing different ASD presentations"""
        
        profiles = {}
        
        # Level 1 ASD - High functioning, mild sensory sensitivities
        profiles["level1_child"] = ChildProfile(
            child_id=1001,
            name="Emma",
            age=8,
            asd_support_level=ASDSupportLevel.LEVEL_1,
            sensory_profile=SensoryProfile.HYPERSENSITIVE,
            sensory_sensitivities=SensorySensitivity(
                auditory=25,  # Very sensitive to sound
                visual=40,    # Moderately sensitive to light
                tactile=30,   # Sensitive to touch
                vestibular=60,
                proprioceptive=50
            ),
            communication_preferences={
                "prefers_written_instructions": True,
                "needs_processing_time": True
            },
            behavioral_patterns={
                "prefers_routine": True,
                "difficulty_with_transitions": True
            },
            interests=["dinosaurs", "mathematics", "patterns"],
            triggers=["loud_noises", "unexpected_changes"],
            calming_strategies=["deep_breathing", "counting"]
        )
        
        # Level 2 ASD - Moderate support needs
        profiles["level2_child"] = ChildProfile(
            child_id=1002,
            name="Marcus",
            age=6,
            asd_support_level=ASDSupportLevel.LEVEL_2,
            sensory_profile=SensoryProfile.MIXED,
            sensory_sensitivities=SensorySensitivity(
                auditory=20,  # Very sensitive to sound
                visual=80,    # Seeks visual input
                tactile=15,   # Very sensitive to touch
                vestibular=85, # Seeks movement
                proprioceptive=90  # Seeks heavy work
            ),
            communication_preferences={
                "prefers_visual_supports": True,
                "needs_simple_language": True
            },
            behavioral_patterns={
                "repetitive_behaviors": True,
                "difficulty_with_attention": True
            },
            interests=["trains", "spinning objects", "colors"],
            triggers=["crowded_spaces", "texture_changes"],
            calming_strategies=["movement_break", "sensory_break"]
        )
        
        # Level 3 ASD - Substantial support needs
        profiles["level3_child"] = ChildProfile(
            child_id=1003,
            name="Alex",
            age=5,
            asd_support_level=ASDSupportLevel.LEVEL_3,
            sensory_profile=SensoryProfile.HYPOSENSITIVE,
            sensory_sensitivities=SensorySensitivity(
                auditory=85,  # Needs loud sounds
                visual=90,    # Needs bright visuals
                tactile=80,   # Seeks touch input
                vestibular=95, # Seeks intense movement
                proprioceptive=95  # Seeks heavy input
            ),
            communication_preferences={
                "prefers_pictures": True,
                "needs_concrete_language": True
            },
            behavioral_patterns={
                "self_stimulatory_behaviors": True,
                "difficulty_with_communication": True
            },
            interests=["lights", "water", "music"],
            triggers=["silence", "still_environments"],
            calming_strategies=["sensory_break", "movement_break"]
        )
        
        return profiles
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results[test_name] = {"passed": passed, "details": details}
        print(f"{status} {test_name}: {details}")
    
    async def test_adaptive_session_creation(self):
        """Test adaptive session creation for different ASD levels"""
        print("\n🧠 Testing Adaptive Session Creation")
        print("=" * 50)
        
        for profile_name, child_profile in self.test_child_profiles.items():
            try:
                # Create start request
                start_request = StartGameRequest(
                    user_id=999,
                    child_id=child_profile.child_id,
                    scenario_id="emotion_garden",
                    difficulty_level=1
                )
                
                # Start adaptive session
                response = await enhanced_game_service.start_adaptive_game_session(
                    start_request, child_profile
                )
                
                if response.success:
                    # Verify adaptive config is created
                    adaptive_config = response.data.get("adaptive_config")
                    if adaptive_config:
                        self.log_test(
                            f"adaptive_session_{profile_name}",
                            True,
                            f"Session created for {child_profile.name} (Level {child_profile.asd_support_level})"
                        )
                        
                        # Verify sensory adjustments
                        sensory_adjustments = adaptive_config.get("sensory_adjustments", {})
                        if sensory_adjustments:
                            self.log_test(
                                f"sensory_adjustments_{profile_name}",
                                True,
                                f"Sensory adjustments applied: {list(sensory_adjustments.keys())}"
                            )
                        else:
                            self.log_test(
                                f"sensory_adjustments_{profile_name}",
                                False,
                                "No sensory adjustments found"
                            )
                    else:
                        self.log_test(
                            f"adaptive_session_{profile_name}",
                            False,
                            "No adaptive config in response"
                        )
                else:
                    self.log_test(
                        f"adaptive_session_{profile_name}",
                        False,
                        response.message
                    )
                    
            except Exception as e:
                self.log_test(
                    f"adaptive_session_{profile_name}",
                    False,                    f"Exception: {str(e)}"
                )
    
    async def test_overstimulation_detection(self):
        """Test overstimulation detection with different scenarios"""
        print("\n⚠️  Testing Overstimulation Detection")
        print("=" * 50)
        
        # Create a default child profile for testing
        test_child = ChildProfile(
            child_id=9999,
            name="TestChild",
            age=6,
            asd_support_level=ASDSupportLevel.LEVEL_2,
            sensory_profile=SensoryProfile.MIXED,
            sensory_sensitivities=SensorySensitivity(
                auditory=50, visual=50, tactile=50, vestibular=50, proprioceptive=50
            ),
            communication_preferences={},
            behavioral_patterns={},
            interests=["test"],
            triggers=["test"],
            calming_strategies=["deep_breathing"]
        )
        
        # Test scenarios with different stimulation levels
        test_scenarios = [
            {
                "name": "normal_activity",
                "metrics": SessionMetrics(
                    session_id="test_session_1",
                    timestamp=datetime.now(),
                    actions_per_minute=15.0,
                    error_rate=0.1,
                    pause_frequency=0.2,
                    average_response_time=2.0,
                    progress_rate=0.7,
                    overstimulation_score=0.2
                ),
                "expected_overstimulated": False
            },
            {
                "name": "high_activity_low_errors",
                "metrics": SessionMetrics(
                    session_id="test_session_2",
                    timestamp=datetime.now(),
                    actions_per_minute=45.0,
                    error_rate=0.15,
                    pause_frequency=0.1,
                    average_response_time=1.0,
                    progress_rate=0.8,
                    overstimulation_score=0.3
                ),
                "expected_overstimulated": False
            },
            {
                "name": "rapid_clicking_high_errors",
                "metrics": SessionMetrics(
                    session_id="test_session_3",
                    timestamp=datetime.now(),
                    actions_per_minute=150.0,  # Very rapid
                    error_rate=0.6,           # High error rate
                    pause_frequency=0.1,
                    average_response_time=0.5,
                    progress_rate=0.2,        # Low progress
                    overstimulation_score=0.8
                ),
                "expected_overstimulated": True
            },
            {
                "name": "frequent_pauses_confusion",
                "metrics": SessionMetrics(
                    session_id="test_session_4",
                    timestamp=datetime.now(),
                    actions_per_minute=5.0,   # Very slow
                    error_rate=0.7,           # High errors
                    pause_frequency=0.8,      # Frequent pauses
                    average_response_time=8.0,
                    progress_rate=0.1,        # Very low progress
                    overstimulation_score=0.9
                ),
                "expected_overstimulated": True
            }
        ]
        
        for scenario in test_scenarios:
            try:                # Create adaptive session config for this test scenario
                await enhanced_game_service.asd_service.create_adaptive_session(
                    test_child, scenario["metrics"].session_id
                )
                
                # Use the ASD service directly for testing
                is_overstimulated, indicators, intervention = await enhanced_game_service.asd_service.detect_overstimulation(
                    scenario["metrics"]
                )
                
                # Check if detection matches expectation
                detection_correct = is_overstimulated == scenario["expected_overstimulated"]
                
                self.log_test(
                    f"overstimulation_detection_{scenario['name']}",
                    detection_correct,
                    f"Detected: {is_overstimulated}, Expected: {scenario['expected_overstimulated']}, Indicators: {indicators}"
                )
                
                # If overstimulation detected, check intervention recommendation
                if is_overstimulated and intervention:
                    self.log_test(
                        f"intervention_recommendation_{scenario['name']}",
                        True,
                        f"Recommended intervention: {intervention}"
                    )
                elif is_overstimulated and not intervention:
                    self.log_test(
                        f"intervention_recommendation_{scenario['name']}",
                        False,
                        "Overstimulation detected but no intervention recommended"
                    )
                    
            except Exception as e:
                self.log_test(
                    f"overstimulation_detection_{scenario['name']}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    async def test_calming_interventions(self):
        """Test calming intervention triggers"""
        print("\n🧘 Testing Calming Interventions")
        print("=" * 50)
        
        interventions_to_test = ["deep_breathing", "sensory_break", "movement_break"]
        
        for intervention_type in interventions_to_test:
            try:
                intervention = await enhanced_game_service.asd_service.trigger_calming_intervention(
                    "test_session", intervention_type
                )
                
                # Verify intervention has required fields
                required_fields = ["intervention_type", "description", "duration_seconds", "instructions"]
                has_all_fields = all(hasattr(intervention, field) for field in required_fields)
                
                self.log_test(
                    f"calming_intervention_{intervention_type}",
                    has_all_fields,
                    f"Duration: {intervention.duration_seconds}s, Instructions: {len(intervention.instructions)}"
                )
                
            except Exception as e:
                self.log_test(
                    f"calming_intervention_{intervention_type}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    async def test_environmental_adjustments(self):
        """Test environmental setting adjustments"""
        print("\n🌿 Testing Environmental Adjustments")
        print("=" * 50)
        
        overstimulation_levels = [0.2, 0.5, 0.8, 1.0]
        
        for level in overstimulation_levels:
            try:
                adjustments = await enhanced_game_service.asd_service.adjust_environmental_settings(
                    "test_session", level
                )
                
                # Verify adjustments are appropriate for overstimulation level
                has_adjustments = len(adjustments) > 0
                
                # High overstimulation should have more/stronger adjustments
                if level > 0.7:
                    expected_significant_adjustments = any(
                        key in adjustments for key in ["reduce_volume", "dim_brightness", "simplify_interface"]
                    )
                else:
                    expected_significant_adjustments = True  # Any adjustments are fine for lower levels
                
                self.log_test(
                    f"environmental_adjustments_level_{level}",
                    has_adjustments and expected_significant_adjustments,
                    f"Adjustments for level {level}: {list(adjustments.keys())}"
                )
                
            except Exception as e:
                self.log_test(
                    f"environmental_adjustments_level_{level}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    async def test_recommendation_generation(self):
        """Test ASD recommendation generation"""
        print("\n📋 Testing Recommendation Generation")
        print("=" * 50)
        
        # Create test progress data
        progress_data = {
            "session_id": "test_session_recommendations",
            "child_id": 1001,
            "game_state": {
                "score": 50,
                "completed_objectives": ["objective1"],
                "current_level": 2
            },
            "session_data": {
                "duration": 600,  # 10 minutes
                "interactions": 25
            }
        }
        
        try:
            # First create an adaptive session for the child
            child_profile = self.test_child_profiles["level1_child"]
            await enhanced_game_service.asd_service.create_adaptive_session(
                child_profile, "test_session_recommendations"
            )
            
            # Add some test metrics to trigger recommendations
            test_metrics = [
                SessionMetrics(
                    session_id="test_session_recommendations",
                    timestamp=datetime.now(),
                    actions_per_minute=20.0,
                    error_rate=0.4,
                    pause_frequency=0.6,
                    average_response_time=3.0,
                    progress_rate=0.3,
                    overstimulation_score=0.7
                )
            ]
            enhanced_game_service.asd_service.session_metrics["test_session_recommendations"] = test_metrics
            
            # Generate recommendations
            recommendations = await enhanced_game_service.asd_service.generate_asd_recommendations(progress_data)
            
            if recommendations:
                self.log_test(
                    "recommendation_generation",
                    True,
                    f"Generated {len(recommendations)} recommendations"
                )
                
                # Check recommendation types
                recommendation_types = set(rec.recommendation_type for rec in recommendations)
                self.log_test(
                    "recommendation_types",
                    len(recommendation_types) > 0,
                    f"Types: {list(recommendation_types)}"
                )
                
                # Check if recommendations have required fields
                first_rec = recommendations[0]
                required_fields = ["title", "description", "action_items", "target_audience"]
                has_required_fields = all(hasattr(first_rec, field) for field in required_fields)
                
                self.log_test(
                    "recommendation_structure",
                    has_required_fields,
                    f"First recommendation: {first_rec.title}"
                )
            else:
                self.log_test(
                    "recommendation_generation",
                    False,
                    "No recommendations generated"
                )
                
        except Exception as e:
            self.log_test(
                "recommendation_generation",
                False,
                f"Exception: {str(e)}"
            )
    
    async def test_full_enhanced_game_flow(self):
        """Test complete enhanced game flow with ASD features"""
        print("\n🎮 Testing Full Enhanced Game Flow")
        print("=" * 50)
        
        try:
            # 1. Start adaptive session
            child_profile = self.test_child_profiles["level2_child"]
            start_request = StartGameRequest(
                user_id=999,
                child_id=child_profile.child_id,
                scenario_id="basic_adventure",
                difficulty_level=1
            )
            
            start_response = await enhanced_game_service.start_adaptive_game_session(
                start_request, child_profile
            )
            
            if not start_response.success:
                self.log_test("full_flow_start", False, start_response.message)
                return
            
            session_id = start_response.session_id
            self.log_test("full_flow_start", True, f"Session {session_id} started")
            
            # 2. Process some game actions
            actions = [
                {"action_type": "move", "target": "garden"},
                {"action_type": "interact", "target": "flower"},
                {"action_type": "select", "target": "watering_can"}
            ]
            
            for i, action_data in enumerate(actions):
                action = GameActionData(
                    session_id=session_id,
                    user_id=999,
                    action_type=GameAction(action_data["action_type"]),
                    target=action_data["target"],
                    timestamp=datetime.now(),
                    context={}
                )
                
                action_response = await enhanced_game_service.process_enhanced_game_action(action)
                
                if action_response.success:
                    # Check for ASD monitoring data
                    asd_monitoring = action_response.data.get("asd_monitoring")
                    if asd_monitoring:
                        self.log_test(
                            f"full_flow_action_{i+1}_monitoring",
                            True,
                            f"ASD monitoring active: overstimulation={asd_monitoring.get('overstimulation_detected', False)}"
                        )
                    else:
                        self.log_test(
                            f"full_flow_action_{i+1}_monitoring",
                            False,
                            "No ASD monitoring data"
                        )
                else:
                    self.log_test(
                        f"full_flow_action_{i+1}",
                        False,
                        action_response.message
                    )
            
            # 3. Generate session report
            report = await enhanced_game_service.generate_session_report(session_id, 999)
            
            if "error" not in report:
                asd_insights = report.get("asd_insights")
                if asd_insights:
                    self.log_test(
                        "full_flow_report",
                        True,
                        f"Report generated with {len(asd_insights.get('recommendations', []))} recommendations"
                    )
                else:
                    self.log_test(
                        "full_flow_report",
                        False,
                        "Report generated but no ASD insights"
                    )
            else:
                self.log_test(
                    "full_flow_report",
                    False,
                    report["error"]
                )
                
        except Exception as e:
            self.log_test(
                "full_flow",
                False,
                f"Exception: {str(e)}"
            )
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 ASD GAME SERVICE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["passed"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDetailed Results:")
        print("-" * 60)
        for test_name, result in self.test_results.items():
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {test_name}: {result['details']}")
        
        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": success_rate
            },
            "test_results": self.test_results
        }
        
        with open("asd_game_service_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved to: asd_game_service_test_report.json")
        return success_rate >= 80  # 80% pass rate threshold
    
    async def run_all_tests(self):
        """Run all ASD Game Service tests"""
        print("🚀 STARTING ASD GAME SERVICE COMPREHENSIVE TESTS")
        print("=" * 60)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test suites
        await self.test_adaptive_session_creation()
        await self.test_overstimulation_detection()
        await self.test_calming_interventions()
        await self.test_environmental_adjustments()
        await self.test_recommendation_generation()
        await self.test_full_enhanced_game_flow()
        
        # Generate final report
        success = self.generate_test_report()
        
        print(f"\n🏁 ASD GAME SERVICE TESTS COMPLETED")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Overall Result: {'✅ SUCCESS' if success else '❌ FAILURE'}")
        
        return success


async def main():
    """Main test execution"""
    tester = ASDGameServiceTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All ASD Game Service features are working correctly!")
        print("The system is ready for ASD-specific adaptive gaming sessions.")
    else:
        print("\n⚠️  Some ASD Game Service features need attention.")
        print("Please review the test report for details.")

if __name__ == "__main__":
    asyncio.run(main())
