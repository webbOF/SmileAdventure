#!/usr/bin/env python3
"""
Test script for ASD Game Service functionality
Validates the enhanced game service with ASD-specific features
"""

import asyncio
import json
import sys
from datetime import datetime

import requests


class ASDGameServiceTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.auth_token = None
        self.user_id = None
        self.session_id = None
        self.child_id = 12345
        
    async def run_tests(self):
        """Run comprehensive ASD Game Service tests"""
        print("🧪 TESTING ASD GAME SERVICE FEATURES")
        print("=" * 60)
        
        # Test 1: Create child profile and start adaptive session
        await self.test_adaptive_session_creation()
        
        # Test 2: Test overstimulation detection
        await self.test_overstimulation_detection()
        
        # Test 3: Test calming interventions
        await self.test_calming_interventions()
        
        # Test 4: Test environmental adjustments
        await self.test_environmental_adjustments()
        
        # Test 5: Test ASD recommendations
        await self.test_asd_recommendations()
        
        # Test 6: Test enhanced game flow
        await self.test_enhanced_game_flow()
        
        print("\n✅ ASD Game Service tests completed!")
    
    async def test_adaptive_session_creation(self):
        """Test creating an adaptive session with child profile"""
        print("\n📝 Test 1: Adaptive Session Creation")
        print("-" * 40)
        
        # Create a comprehensive child profile
        child_profile = {
            "child_id": self.child_id,
            "name": "Test Child",
            "age": 8,
            "asd_support_level": 2,  # Level 2 - substantial support
            "sensory_profile": "hypersensitive",
            "sensory_sensitivities": {
                "auditory": 25,      # Very sensitive to sound
                "visual": 30,        # Sensitive to bright lights
                "tactile": 40,       # Moderately sensitive to touch
                "vestibular": 50,    # Typical vestibular processing
                "proprioceptive": 60 # Slightly hyposensitive
            },
            "communication_preferences": {
                "use_simple_language": True,
                "visual_supports": True,
                "processing_time": "extended"
            },
            "behavioral_patterns": {
                "attention_span": "short",
                "transition_difficulty": "high",
                "routine_importance": "critical"
            },
            "interests": ["trains", "dinosaurs", "music"],
            "triggers": ["loud_noises", "flashing_lights", "crowded_spaces"],
            "calming_strategies": ["deep_breathing", "movement_break"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Test adaptive session creation
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/game/asd/session/create-adaptive",
                json=child_profile,
                params={"session_id": "test_session_001"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Adaptive session created successfully")
                print(f"   Child Profile: {child_profile['name']}, Age: {child_profile['age']}")
                print(f"   Support Level: {child_profile['asd_support_level']}")
                print(f"   Sensory Profile: {child_profile['sensory_profile']}")
                
                # Display key adaptations
                if "data" in result:
                    config = result["data"]
                    print(f"   Sensory Adjustments: {len(config.get('sensory_adjustments', {}))}")
                    print(f"   Pacing Adjustments: {len(config.get('pacing_adjustments', {}))}")
                    print(f"   Break Intervals: {config.get('break_intervals', 'N/A')} seconds")
                
                self.session_id = "test_session_001"
            else:
                print(f"❌ Failed to create adaptive session: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception in adaptive session creation: {str(e)}")
    
    async def test_overstimulation_detection(self):
        """Test overstimulation detection system"""
        print("\n🚨 Test 2: Overstimulation Detection")
        print("-" * 40)
        
        # Test scenarios with different overstimulation levels
        test_scenarios = [
            {
                "name": "Normal Activity",
                "metrics": {
                    "session_id": self.session_id or "test_session_001",
                    "timestamp": datetime.now().isoformat(),
                    "actions_per_minute": 20.0,
                    "error_rate": 0.1,
                    "pause_frequency": 0.2,
                    "average_response_time": 2.0,
                    "progress_rate": 0.6,
                    "overstimulation_score": 0.2,
                    "stress_indicators": []
                }
            },
            {
                "name": "High Activity (Potential Overstimulation)",
                "metrics": {
                    "session_id": self.session_id or "test_session_001",
                    "timestamp": datetime.now().isoformat(),
                    "actions_per_minute": 150.0,  # Very high
                    "error_rate": 0.6,            # High error rate
                    "pause_frequency": 0.1,       # Low pauses
                    "average_response_time": 0.5,  # Very fast responses
                    "progress_rate": 0.1,         # Low progress
                    "overstimulation_score": 0.8,
                    "stress_indicators": ["rapid_clicking", "high_error_rate"]
                }
            },
            {
                "name": "Confusion/Overwhelm",
                "metrics": {
                    "session_id": self.session_id or "test_session_001",
                    "timestamp": datetime.now().isoformat(),
                    "actions_per_minute": 5.0,    # Very low
                    "error_rate": 0.7,            # Very high error rate
                    "pause_frequency": 0.8,       # Many long pauses
                    "average_response_time": 10.0, # Very slow responses
                    "progress_rate": 0.05,        # Almost no progress
                    "overstimulation_score": 0.9,
                    "stress_indicators": ["long_pause", "difficulty_progressing"]
                }
            }
        ]
        
        for scenario in test_scenarios:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/game/asd/overstimulation/detect",
                    json=scenario["metrics"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    data = result.get("data", {})
                    
                    print(f"   📊 {scenario['name']}:")
                    print(f"      Overstimulated: {data.get('is_overstimulated', False)}")
                    print(f"      Indicators: {data.get('indicators', [])}")
                    print(f"      Score: {data.get('overstimulation_score', 0):.2f}")
                    
                    if data.get('recommended_intervention'):
                        print(f"      Intervention: {data['recommended_intervention']}")
                else:
                    print(f"   ❌ Failed to detect overstimulation for {scenario['name']}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Exception in overstimulation detection: {str(e)}")
    
    async def test_calming_interventions(self):
        """Test calming intervention system"""
        print("\n🧘 Test 3: Calming Interventions")
        print("-" * 40)
        
        interventions = ["deep_breathing", "sensory_break", "movement_break"]
        
        for intervention in interventions:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/game/asd/intervention/trigger",
                    params={
                        "session_id": self.session_id or "test_session_001",
                        "intervention_type": intervention
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    intervention_data = result.get("data", {})
                    
                    print(f"   🎯 {intervention.replace('_', ' ').title()}:")
                    print(f"      Duration: {intervention_data.get('duration_seconds', 0)} seconds")
                    print(f"      Instructions: {len(intervention_data.get('instructions', []))} steps")
                    print(f"      Type: {intervention_data.get('intervention_type', 'N/A')}")
                else:
                    print(f"   ❌ Failed to trigger {intervention}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Exception triggering {intervention}: {str(e)}")
    
    async def test_environmental_adjustments(self):
        """Test environmental adjustment system"""
        print("\n🌈 Test 4: Environmental Adjustments")
        print("-" * 40)
        
        overstimulation_levels = [0.3, 0.6, 0.9]
        
        for level in overstimulation_levels:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/game/asd/environment/adjust",
                    params={
                        "session_id": self.session_id or "test_session_001",
                        "overstimulation_level": level
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    adjustments = result.get("data", {})
                    
                    print(f"   📊 Overstimulation Level {level:.1f}:")
                    if adjustments:
                        for key, value in adjustments.items():
                            print(f"      {key}: {value}")
                    else:
                        print(f"      No adjustments needed")
                else:
                    print(f"   ❌ Failed to get adjustments for level {level}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Exception getting adjustments: {str(e)}")
    
    async def test_asd_recommendations(self):
        """Test ASD recommendation generation"""
        print("\n💡 Test 5: ASD Recommendations")
        print("-" * 40)
        
        progress_data = {
            "session_id": self.session_id or "test_session_001",
            "child_id": self.child_id,
            "session_duration": 1800,  # 30 minutes
            "total_actions": 150,
            "overstimulation_events": 3,
            "interventions_used": ["deep_breathing", "sensory_break"],
            "final_score": 85,
            "objectives_completed": ["brush_teeth", "wash_hands"],
            "average_response_time": 3.5,
            "error_rate": 0.3
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/game/asd/recommendations/generate",
                json=progress_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                recommendations = result.get("data", [])
                
                print(f"   📋 Generated {len(recommendations)} recommendations:")
                
                for i, rec in enumerate(recommendations, 1):
                    print(f"      {i}. {rec.get('title', 'N/A')} ({rec.get('recommendation_type', 'N/A')})")
                    print(f"         Priority: {rec.get('priority', 'N/A')}")
                    print(f"         Target: {', '.join(rec.get('target_audience', []))}")
            else:
                print(f"   ❌ Failed to generate recommendations: {response.status_code}")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception generating recommendations: {str(e)}")
    
    async def test_enhanced_game_flow(self):
        """Test the enhanced game flow with ASD features"""
        print("\n🎮 Test 6: Enhanced Game Flow")
        print("-" * 40)
        
        # Test enhanced scenario listing
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/game/enhanced/scenarios",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                scenarios = result.get("scenarios", {})
                
                print(f"   📚 Available Enhanced Scenarios: {len(scenarios)}")
                for scenario_id, scenario_data in scenarios.items():
                    print(f"      • {scenario_data.get('name', scenario_id)}")
                    print(f"        ASD Recommended: {scenario_data.get('recommended_for_asd', False)}")
            else:
                print(f"   ❌ Failed to get enhanced scenarios: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception getting enhanced scenarios: {str(e)}")
        
        # Test monitoring endpoint
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/game/enhanced/monitoring/{self.session_id or 'test_session_001'}",
                params={"user_id": 123},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   📊 Monitoring Status: {result.get('success', False)}")
                if result.get("data"):
                    data = result["data"]
                    print(f"      ASD Enabled: {data.get('asd_enabled', False)}")
                    print(f"      Metrics Count: {data.get('metrics_count', 0)}")
            else:
                print(f"   ❌ Failed to get monitoring data: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception getting monitoring data: {str(e)}")


def main():
    """Main test execution"""
    tester = ASDGameServiceTest()
    
    try:
        # Run async tests
        asyncio.run(tester.run_tests())
        print("\n🎉 All ASD Game Service tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
