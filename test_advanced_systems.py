"""
Comprehensive Testing Suite for Advanced MindMend Features
Tests all major systems and their integrations
"""

import sys
import os
import pytest
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all managers
from models.enhancement_manager import enhancement_manager, FeatureModule
from models.physical_health_integrator import physical_health_integrator, ExerciseIntensity
from models.social_connection_manager import social_connection_manager, ConnectionType
from models.therapeutic_tools_manager import therapeutic_tools_manager, VREnvironment, TherapyIntensity
from models.predictive_analytics_manager import predictive_analytics_manager, PredictionType, RiskLevel
from models.iot_wearable_manager import iot_wearable_manager, DeviceType, DeviceBrand
from models.crisis_intervention_system import crisis_intervention_system, CrisisLevel, InterventionType

class TestRunner:
    def __init__(self):
        self.test_results = {}
        self.test_user_id = "test_user_12345"
        self.errors = []

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.test_results[test_name] = {
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if not success:
            self.errors.append(f"{test_name}: {details}")
        print(f"{'✅' if success else '❌'} {test_name}: {details}")

    def test_enhancement_manager(self):
        """Test Enhancement Manager functionality"""
        print("\n🔧 Testing Enhancement Manager...")

        try:
            # Test module installation
            result = enhancement_manager.install_module(FeatureModule.PHYSICAL_HEALTH.value)
            self.log_test("Enhancement Manager - Module Installation",
                         result["success"], "Physical health module installed")

            # Test module activation
            activation = enhancement_manager.activate_module(FeatureModule.PHYSICAL_HEALTH.value, self.test_user_id)
            self.log_test("Enhancement Manager - Module Activation",
                         activation["success"], "Module activated for test user")

            # Test status retrieval
            status = enhancement_manager.get_module_status()
            self.log_test("Enhancement Manager - Status Retrieval",
                         isinstance(status, dict), f"Retrieved status for {len(status)} modules")

        except Exception as e:
            self.log_test("Enhancement Manager - General", False, f"Error: {str(e)}")

    def test_physical_health_integration(self):
        """Test Physical Health Integration"""
        print("\n💪 Testing Physical Health Integration...")

        try:
            # Test exercise prescription
            prescription = physical_health_integrator.create_exercise_prescription(
                self.test_user_id, ["anxiety", "depression"], "intermediate", 60
            )
            self.log_test("Physical Health - Exercise Prescription",
                         prescription.user_id == self.test_user_id,
                         f"Created {len(prescription.specific_exercises)} exercises")

            # Test nutrition planning
            nutrition = physical_health_integrator.create_nutrition_plan(
                self.test_user_id, ["stress", "low_energy"]
            )
            self.log_test("Physical Health - Nutrition Planning",
                         nutrition.user_id == self.test_user_id,
                         f"Created plan with {len(nutrition.recommended_foods)} foods")

            # Test sleep optimization
            sleep_plan = physical_health_integrator.create_sleep_optimization_plan(
                self.test_user_id, 30, ["anxiety"], 7.0, ["difficulty_falling_asleep"]
            )
            self.log_test("Physical Health - Sleep Optimization",
                         sleep_plan.user_id == self.test_user_id,
                         f"Created plan with {len(sleep_plan.sleep_hygiene_tips)} recommendations")

        except Exception as e:
            self.log_test("Physical Health Integration - General", False, f"Error: {str(e)}")

    def test_social_connection_features(self):
        """Test Social Connection Features"""
        print("\n👥 Testing Social Connection Features...")

        try:
            # Test peer matching
            from models.social_connection_manager import ConnectionType
            matches = social_connection_manager.find_peer_matches(self.test_user_id, ConnectionType.SUPPORT_BUDDY)
            self.log_test("Social Connection - Peer Matching",
                         isinstance(matches, list), f"Found {len(matches)} potential matches")

            # Test group session creation
            from models.social_connection_manager import GroupSessionType
            from datetime import datetime, timedelta
            session = social_connection_manager.create_group_session(
                session_type=GroupSessionType.ANXIETY_SUPPORT,
                moderator_id=1,
                scheduled_time=datetime.now() + timedelta(hours=24)
            )
            self.log_test("Social Connection - Group Session Creation",
                         session.session_type == GroupSessionType.ANXIETY_SUPPORT,
                         f"Created session {session.session_id}")

            # Test community challenge
            challenge = social_connection_manager.create_community_challenge(
                challenge_type="mindfulness",
                start_date=datetime.now() + timedelta(days=1)
            )
            self.log_test("Social Connection - Community Challenge",
                         challenge.challenge_type == "mindfulness",
                         f"Created challenge {challenge.challenge_id}")

        except Exception as e:
            self.log_test("Social Connection Features - General", False, f"Error: {str(e)}")

    def test_therapeutic_tools(self):
        """Test Advanced Therapeutic Tools"""
        print("\n🎮 Testing Therapeutic Tools...")

        try:
            # Test therapy plan creation
            plan = therapeutic_tools_manager.create_personalized_therapy_plan(
                self.test_user_id, ["anxiety", "depression"], {"frequency": "3x_weekly"}
            )
            self.log_test("Therapeutic Tools - Therapy Plan Creation",
                         plan.user_id == self.test_user_id,
                         f"Created plan with {len(plan.vr_environments)} VR environments")

            # Test VR session
            session = therapeutic_tools_manager.start_vr_therapy_session(
                self.test_user_id, VREnvironment.BEACH_CALM, "relaxation"
            )
            self.log_test("Therapeutic Tools - VR Session Start",
                         session.user_id == self.test_user_id,
                         f"Started VR session {session.session_id}")

            # Test biometric processing
            from models.therapeutic_tools_manager import BiometricType
            biometric_result = therapeutic_tools_manager.process_biometric_reading(
                session.session_id,
                BiometricType.HEART_RATE,
                75.0
            )
            self.log_test("Therapeutic Tools - Biometric Processing",
                         biometric_result, "Processed heart rate reading")

        except Exception as e:
            self.log_test("Therapeutic Tools - General", False, f"Error: {str(e)}")

    def test_predictive_analytics(self):
        """Test Predictive Analytics"""
        print("\n🤖 Testing Predictive Analytics...")

        try:
            # Test behavioral analysis
            from models.predictive_analytics_manager import DataSource
            test_data = {
                DataSource.BIOMETRIC_SENSORS: {
                    "sleep_hours": 5.5,
                    "heart_rate_variability": 20
                },
                DataSource.APP_USAGE: {
                    "social_app_minutes": 10,
                    "messages_sent_daily": 3
                }
            }

            indicators = predictive_analytics_manager.analyze_behavioral_patterns(
                self.test_user_id, test_data
            )
            self.log_test("Predictive Analytics - Behavioral Analysis",
                         isinstance(indicators, list),
                         f"Detected {len(indicators)} behavioral indicators")

            # Test risk assessment
            assessment = predictive_analytics_manager.generate_risk_assessment(
                self.test_user_id, PredictionType.CRISIS_RISK
            )
            self.log_test("Predictive Analytics - Risk Assessment",
                         assessment.user_id == self.test_user_id,
                         f"Generated {assessment.risk_level.value} risk assessment")

            # Test voice analysis
            voice_features = {
                "words_per_minute": 120,
                "pitch_mean": 150,
                "tremor_score": 0.3,
                "confidence": 0.9
            }
            voice_analysis = predictive_analytics_manager.process_voice_analysis(
                self.test_user_id, "session_123", voice_features
            )
            self.log_test("Predictive Analytics - Voice Analysis",
                         voice_analysis.user_id == self.test_user_id,
                         f"Analyzed voice with {voice_analysis.stress_level:.2f} stress level")

        except Exception as e:
            self.log_test("Predictive Analytics - General", False, f"Error: {str(e)}")

    def test_iot_wearable_integration(self):
        """Test IoT & Wearable Integration"""
        print("\n⌚ Testing IoT & Wearable Integration...")

        try:
            # Test device registration
            device = iot_wearable_manager.register_device(
                self.test_user_id, DeviceType.SMARTWATCH, DeviceBrand.APPLE_WATCH,
                "Apple Watch Series 9", ["health_data", "fitness_data"]
            )
            self.log_test("IoT Integration - Device Registration",
                         device.user_id == self.test_user_id,
                         f"Registered {device.brand.value} device")

            # Test data collection
            readings = iot_wearable_manager.collect_real_time_data(device.device_id)
            self.log_test("IoT Integration - Data Collection",
                         len(readings) > 0,
                         f"Collected {len(readings)} sensor readings")

            # Test sleep analysis
            sleep_analysis = iot_wearable_manager.analyze_sleep_data(
                self.test_user_id, datetime.now()
            )
            self.log_test("IoT Integration - Sleep Analysis",
                         sleep_analysis.user_id == self.test_user_id,
                         f"Sleep score: {sleep_analysis.sleep_score}")

            # Test environmental data
            env_data = iot_wearable_manager.collect_environmental_data(self.test_user_id)
            self.log_test("IoT Integration - Environmental Data",
                         env_data.user_id == self.test_user_id,
                         f"AQI: {env_data.air_quality_index}")

        except Exception as e:
            self.log_test("IoT Integration - General", False, f"Error: {str(e)}")

    def test_crisis_intervention(self):
        """Test Crisis Intervention System"""
        print("\n🚨 Testing Crisis Intervention System...")

        try:
            # Test safety plan creation
            plan_data = {
                "warning_signs": ["Feeling hopeless", "Social withdrawal"],
                "coping_strategies": ["Deep breathing", "Call friend"],
                "support_contacts": [{"name": "John Doe", "phone": "555-1234"}]
            }
            safety_plan = crisis_intervention_system.create_safety_plan(
                self.test_user_id, plan_data
            )
            self.log_test("Crisis Intervention - Safety Plan Creation",
                         safety_plan.user_id == self.test_user_id,
                         f"Created plan with {len(safety_plan.warning_signs)} warning signs")

            # Test emergency contact
            contact = crisis_intervention_system.add_emergency_contact(
                self.test_user_id, {
                    "name": "Emergency Contact",
                    "relationship": "family",
                    "phone_number": "555-0000"
                }
            )
            self.log_test("Crisis Intervention - Emergency Contact",
                         contact.user_id == self.test_user_id,
                         f"Added contact: {contact.name}")

            # Test crisis assessment
            trigger_data = {
                "suicidal_thoughts": False,
                "hopelessness_score": 6,
                "stress_level": 0.8
            }
            alert = crisis_intervention_system.assess_crisis_level(
                self.test_user_id, trigger_data, "user_report"
            )
            self.log_test("Crisis Intervention - Crisis Assessment",
                         alert.user_id == self.test_user_id,
                         f"Crisis level: {alert.crisis_level.value}")

        except Exception as e:
            self.log_test("Crisis Intervention - General", False, f"Error: {str(e)}")

    def test_system_integration(self):
        """Test cross-system integration"""
        print("\n🔗 Testing System Integration...")

        try:
            # Test data flow between predictive analytics and crisis intervention
            # Simulate high-risk behavioral indicators
            from models.predictive_analytics_manager import DataSource
            high_risk_data = {
                DataSource.TEXT_SENTIMENT: {
                    "sentiment_score": -0.8,
                    "crisis_help_requested": True
                }
            }

            indicators = predictive_analytics_manager.analyze_behavioral_patterns(
                self.test_user_id, high_risk_data
            )

            assessment = predictive_analytics_manager.generate_risk_assessment(
                self.test_user_id, PredictionType.CRISIS_RISK
            )

            # This should trigger crisis intervention
            integration_success = (len(indicators) > 0 and
                                 assessment.risk_level in [RiskLevel.HIGH, RiskLevel.MODERATE])

            self.log_test("System Integration - Predictive to Crisis",
                         integration_success,
                         f"Risk assessment triggered with {len(indicators)} indicators")

            # Test enhancement manager coordination
            modules_active = 0
            for module in [FeatureModule.PHYSICAL_HEALTH, FeatureModule.SOCIAL_CONNECTION]:
                # Install module first
                install_result = enhancement_manager.install_module(module.value)
                if install_result["success"]:
                    # Then activate it
                    result = enhancement_manager.activate_module(module.value, self.test_user_id)
                    if result["success"]:
                        modules_active += 1

            self.log_test("System Integration - Enhancement Coordination",
                         modules_active >= 2,
                         f"Activated {modules_active} enhancement modules")

        except Exception as e:
            self.log_test("System Integration - General", False, f"Error: {str(e)}")

    def test_admin_interfaces(self):
        """Test admin interface functionality"""
        print("\n⚙️ Testing Admin Interfaces...")

        try:
            # Test platform statistics
            enhancement_stats = enhancement_manager.get_platform_statistics()
            social_stats = social_connection_manager.get_platform_statistics()
            therapeutic_stats = therapeutic_tools_manager.get_platform_statistics()
            predictive_stats = predictive_analytics_manager.get_platform_statistics()
            iot_stats = iot_wearable_manager.get_platform_statistics()
            crisis_stats = crisis_intervention_system.get_platform_statistics()

            all_stats_valid = all([
                isinstance(stats, dict) and len(stats) > 0
                for stats in [enhancement_stats, social_stats, therapeutic_stats,
                            predictive_stats, iot_stats, crisis_stats]
            ])

            self.log_test("Admin Interfaces - Platform Statistics",
                         all_stats_valid,
                         "All 6 systems returning valid statistics")

            # Test user dashboards
            predictive_dashboard = predictive_analytics_manager.get_user_analytics_dashboard(self.test_user_id)
            iot_dashboard = iot_wearable_manager.get_user_device_dashboard(self.test_user_id)
            crisis_dashboard = crisis_intervention_system.get_crisis_dashboard(self.test_user_id)

            dashboards_valid = all([
                isinstance(dashboard, dict) and "user_id" in dashboard
                for dashboard in [predictive_dashboard, iot_dashboard, crisis_dashboard]
            ])

            self.log_test("Admin Interfaces - User Dashboards",
                         dashboards_valid,
                         "User dashboards generated successfully")

        except Exception as e:
            self.log_test("Admin Interfaces - General", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting Comprehensive MindMend Testing Suite...")
        print("=" * 60)

        # Run all test categories
        self.test_enhancement_manager()
        self.test_physical_health_integration()
        self.test_social_connection_features()
        self.test_therapeutic_tools()
        self.test_predictive_analytics()
        self.test_iot_wearable_integration()
        self.test_crisis_intervention()
        self.test_system_integration()
        self.test_admin_interfaces()

        # Generate test report
        self.generate_test_report()

        return len(self.errors) == 0

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r["success"]])
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if self.errors:
            print(f"\n❌ FAILED TESTS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print("\n🎉 ALL TESTS PASSED!")

        # Save detailed report
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "test_details": self.test_results,
            "errors": self.errors,
            "generated_at": datetime.now().isoformat()
        }

        with open("/home/sticky/Desktop/MindMend/MindMend/test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: test_report.json")

if __name__ == "__main__":
    tester = TestRunner()
    success = tester.run_all_tests()

    if success:
        print("\n🚀 SYSTEM READY FOR DEPLOYMENT!")
    else:
        print("\n⚠️  FIX ERRORS BEFORE DEPLOYMENT")

    exit(0 if success else 1)