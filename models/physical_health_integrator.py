"""
Physical Health Integration Module
==================================
Comprehensive physical health integration for mental wellness optimization.
Includes exercise prescription, nutrition tracking, sleep optimization, and biometric analysis.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sqlalchemy import text

logger = logging.getLogger(__name__)

class ExerciseIntensity(Enum):
    """Exercise intensity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    RECOVERY = "recovery"

class MentalHealthCondition(Enum):
    """Mental health conditions for exercise prescription"""
    ANXIETY = "anxiety"
    DEPRESSION = "depression"
    STRESS = "stress"
    PTSD = "ptsd"
    BIPOLAR = "bipolar"
    ADHD = "adhd"
    GENERAL_WELLNESS = "general_wellness"

@dataclass
class ExercisePrescription:
    """Exercise prescription data structure"""
    user_id: int
    condition: MentalHealthCondition
    exercise_type: str
    intensity: ExerciseIntensity
    duration_minutes: int
    frequency_per_week: int
    specific_exercises: List[str]
    mental_health_benefits: List[str]
    precautions: List[str]
    expected_mood_improvement: float

@dataclass
class NutritionRecommendation:
    """Nutrition recommendation for mental health"""
    user_id: int
    recommended_foods: List[str]
    foods_to_avoid: List[str]
    supplements: List[str]
    meal_timing: Dict[str, str]
    hydration_goal_ml: int
    mental_health_nutrients: List[str]

@dataclass
class SleepOptimizationPlan:
    """Sleep optimization recommendations"""
    user_id: int
    recommended_bedtime: str
    recommended_wake_time: str
    sleep_duration_hours: float
    sleep_hygiene_tips: List[str]
    environmental_factors: Dict[str, str]
    pre_sleep_routine: List[str]

class PhysicalHealthIntegrator:
    """Manages physical health integration for mental wellness"""

    def __init__(self):
        self.exercise_database = self._initialize_exercise_database()
        self.nutrition_database = self._initialize_nutrition_database()
        self.sleep_guidelines = self._initialize_sleep_guidelines()
        self.biometric_thresholds = self._initialize_biometric_thresholds()

    def _initialize_exercise_database(self) -> Dict[str, Any]:
        """Initialize comprehensive exercise database"""
        return {
            "anxiety": {
                "recommended_types": [
                    "yoga", "tai_chi", "walking", "swimming", "cycling",
                    "pilates", "stretching", "breathing_exercises"
                ],
                "intensity_preferences": {
                    ExerciseIntensity.LOW: ["gentle_yoga", "walking", "stretching"],
                    ExerciseIntensity.MODERATE: ["swimming", "cycling", "hiking"],
                    ExerciseIntensity.HIGH: ["running", "strength_training", "dance"]
                },
                "benefits": [
                    "Reduces cortisol levels",
                    "Increases GABA production",
                    "Improves heart rate variability",
                    "Enhances mindfulness and present-moment awareness",
                    "Releases endorphins naturally"
                ],
                "duration_recommendations": {
                    "beginner": 15,
                    "intermediate": 30,
                    "advanced": 45
                }
            },
            "depression": {
                "recommended_types": [
                    "aerobic_exercise", "strength_training", "group_fitness",
                    "outdoor_activities", "dancing", "martial_arts"
                ],
                "intensity_preferences": {
                    ExerciseIntensity.LOW: ["walking", "gentle_swimming"],
                    ExerciseIntensity.MODERATE: ["jogging", "weight_lifting", "group_classes"],
                    ExerciseIntensity.HIGH: ["running", "HIIT", "competitive_sports"]
                },
                "benefits": [
                    "Increases serotonin and dopamine",
                    "Reduces inflammatory markers",
                    "Improves neuroplasticity",
                    "Enhances social connection (group activities)",
                    "Builds self-efficacy and confidence"
                ],
                "duration_recommendations": {
                    "beginner": 20,
                    "intermediate": 40,
                    "advanced": 60
                }
            },
            "stress": {
                "recommended_types": [
                    "yoga", "meditation_movement", "nature_walks", "swimming",
                    "tai_chi", "qigong", "recreational_sports"
                ],
                "intensity_preferences": {
                    ExerciseIntensity.LOW: ["restorative_yoga", "walking", "gentle_stretching"],
                    ExerciseIntensity.MODERATE: ["hatha_yoga", "swimming", "cycling"],
                    ExerciseIntensity.HIGH: ["power_yoga", "running", "kickboxing"]
                },
                "benefits": [
                    "Activates parasympathetic nervous system",
                    "Reduces chronic inflammation",
                    "Improves sleep quality",
                    "Increases stress resilience",
                    "Enhances emotional regulation"
                ],
                "duration_recommendations": {
                    "beginner": 15,
                    "intermediate": 30,
                    "advanced": 45
                }
            },
            "ptsd": {
                "recommended_types": [
                    "yoga", "swimming", "walking", "cycling", "strength_training",
                    "martial_arts", "equine_therapy", "rock_climbing"
                ],
                "intensity_preferences": {
                    ExerciseIntensity.LOW: ["gentle_yoga", "walking", "water_therapy"],
                    ExerciseIntensity.MODERATE: ["swimming", "cycling", "hiking"],
                    ExerciseIntensity.HIGH: ["martial_arts", "rock_climbing", "CrossFit"]
                },
                "benefits": [
                    "Reduces hypervigilance",
                    "Improves body awareness and control",
                    "Releases trauma stored in muscles",
                    "Builds confidence and empowerment",
                    "Creates positive body experiences"
                ],
                "duration_recommendations": {
                    "beginner": 20,
                    "intermediate": 35,
                    "advanced": 50
                }
            },
            "general_wellness": {
                "recommended_types": [
                    "walking", "cycling", "swimming", "yoga", "strength_training",
                    "pilates", "dancing", "hiking", "recreational_sports"
                ],
                "intensity_preferences": {
                    ExerciseIntensity.LOW: ["walking", "gentle_yoga", "stretching"],
                    ExerciseIntensity.MODERATE: ["cycling", "swimming", "pilates"],
                    ExerciseIntensity.HIGH: ["running", "strength_training", "HIIT"]
                },
                "benefits": [
                    "Improves overall cardiovascular health",
                    "Enhances mood and energy levels",
                    "Builds strength and endurance",
                    "Promotes better sleep quality",
                    "Supports healthy brain function"
                ],
                "duration_recommendations": {
                    "beginner": 20,
                    "intermediate": 30,
                    "advanced": 45
                }
            }
        }

    def _initialize_nutrition_database(self) -> Dict[str, Any]:
        """Initialize nutrition recommendations for mental health"""
        return {
            "brain_foods": {
                "omega3_sources": [
                    "salmon", "mackerel", "sardines", "walnuts", "chia_seeds",
                    "flax_seeds", "hemp_seeds", "algae_supplements"
                ],
                "antioxidant_rich": [
                    "blueberries", "dark_chocolate", "green_tea", "spinach",
                    "kale", "pomegranate", "turmeric", "ginger"
                ],
                "b_vitamin_sources": [
                    "nutritional_yeast", "leafy_greens", "eggs", "legumes",
                    "quinoa", "sunflower_seeds", "avocado"
                ],
                "magnesium_rich": [
                    "dark_leafy_greens", "nuts", "seeds", "whole_grains",
                    "dark_chocolate", "bananas", "avocados"
                ],
                "probiotics": [
                    "kefir", "yogurt", "sauerkraut", "kimchi", "miso",
                    "kombucha", "tempeh", "pickles"
                ]
            },
            "mood_supporting_nutrients": {
                "serotonin_precursors": [
                    "turkey", "eggs", "cheese", "salmon", "nuts", "seeds"
                ],
                "dopamine_supporters": [
                    "lean_proteins", "beets", "apples", "watermelon", "almonds"
                ],
                "gaba_enhancers": [
                    "fermented_foods", "sprouted_grains", "broccoli", "kale"
                ],
                "cortisol_reducers": [
                    "ashwagandha", "holy_basil", "phosphatidylserine",
                    "omega3_supplements", "magnesium"
                ]
            },
            "foods_to_minimize": {
                "anxiety_triggers": [
                    "caffeine", "alcohol", "processed_sugar", "artificial_sweeteners",
                    "processed_foods", "trans_fats"
                ],
                "depression_aggravators": [
                    "high_sugar_foods", "processed_meats", "refined_carbs",
                    "alcohol", "excessive_caffeine"
                ],
                "inflammation_causers": [
                    "processed_foods", "refined_sugar", "trans_fats",
                    "excessive_omega6", "gluten_for_sensitive_individuals"
                ]
            },
            "meal_timing_strategies": {
                "blood_sugar_stability": {
                    "frequency": "every_3_4_hours",
                    "composition": "protein_healthy_fats_complex_carbs",
                    "avoid": "long_fasting_periods_without_medical_supervision"
                },
                "circadian_rhythm_support": {
                    "morning": "protein_rich_breakfast_within_2_hours_of_waking",
                    "evening": "lighter_dinner_3_hours_before_bed",
                    "avoid": "late_night_eating_blue_light_exposure"
                }
            }
        }

    def _initialize_sleep_guidelines(self) -> Dict[str, Any]:
        """Initialize sleep optimization guidelines"""
        return {
            "optimal_duration": {
                "adults_18_64": {"min": 7, "max": 9},
                "adults_65_plus": {"min": 7, "max": 8},
                "teens_14_17": {"min": 8, "max": 10}
            },
            "sleep_hygiene_fundamentals": [
                "Consistent sleep schedule (same bedtime/wake time daily)",
                "Dark, cool (65-68°F), quiet sleeping environment",
                "No screens 1 hour before bedtime",
                "Avoid caffeine 6 hours before sleep",
                "No large meals 3 hours before bed",
                "Regular exposure to natural light during day",
                "Comfortable mattress and pillows"
            ],
            "pre_sleep_routine": [
                "Dim lights 2 hours before bedtime",
                "Relaxation techniques (deep breathing, meditation)",
                "Light stretching or gentle yoga",
                "Reading or listening to calming music",
                "Warm bath or shower",
                "Journaling or gratitude practice"
            ],
            "sleep_disruptors": [
                "Irregular sleep schedule",
                "Excessive screen time before bed",
                "Caffeine late in the day",
                "Alcohol before sleep",
                "Stress and racing thoughts",
                "Uncomfortable sleep environment",
                "Lack of physical activity during day"
            ],
            "mental_health_sleep_connections": {
                "anxiety": {
                    "sleep_issues": "difficulty_falling_asleep",
                    "recommendations": "relaxation_techniques_before_bed",
                    "supplements": "magnesium_l_theanine_melatonin"
                },
                "depression": {
                    "sleep_issues": "early_morning_awakening_non_restorative_sleep",
                    "recommendations": "light_therapy_consistent_schedule",
                    "supplements": "vitamin_d_omega3_5htp"
                }
            }
        }

    def _initialize_biometric_thresholds(self) -> Dict[str, Any]:
        """Initialize biometric thresholds for mental health"""
        return {
            "heart_rate_variability": {
                "excellent": {"min": 50, "max": 100},
                "good": {"min": 30, "max": 49},
                "fair": {"min": 20, "max": 29},
                "poor": {"min": 0, "max": 19}
            },
            "resting_heart_rate": {
                "excellent": {"min": 40, "max": 60},
                "good": {"min": 61, "max": 70},
                "fair": {"min": 71, "max": 80},
                "needs_attention": {"min": 81, "max": 100}
            },
            "stress_indicators": {
                "cortisol_levels": {
                    "morning_optimal": {"min": 10, "max": 20},  # μg/dL
                    "evening_optimal": {"min": 3, "max": 8}
                },
                "blood_pressure": {
                    "optimal": {"systolic": 120, "diastolic": 80},
                    "concerning": {"systolic": 140, "diastolic": 90}
                }
            }
        }

    def create_exercise_prescription(self, user_id: int, mental_health_conditions: List[str],
                                   fitness_level: str, available_time: int,
                                   preferences: List[str] = None) -> ExercisePrescription:
        """Create personalized exercise prescription for mental health"""

        primary_condition = mental_health_conditions[0] if mental_health_conditions else "general_wellness"
        condition_data = self.exercise_database.get(primary_condition.lower(),
                                                   self.exercise_database["general_wellness"])

        # Determine intensity based on fitness level
        intensity_map = {
            "beginner": ExerciseIntensity.LOW,
            "intermediate": ExerciseIntensity.MODERATE,
            "advanced": ExerciseIntensity.HIGH
        }
        recommended_intensity = intensity_map.get(fitness_level.lower(), ExerciseIntensity.MODERATE)

        # Get exercises for this intensity
        intensity_exercises = condition_data["intensity_preferences"][recommended_intensity]

        # Filter by user preferences if provided
        if preferences:
            preferred_exercises = [ex for ex in intensity_exercises
                                 if any(pref.lower() in ex.lower() for pref in preferences)]
            if preferred_exercises:
                intensity_exercises = preferred_exercises

        # Determine duration and frequency
        base_duration = condition_data["duration_recommendations"].get(fitness_level.lower(), 30)
        duration = min(base_duration, available_time) if available_time else base_duration

        # Calculate expected mood improvement (evidence-based estimates)
        mood_improvement_map = {
            "anxiety": 0.25,  # 25% reduction in anxiety scores
            "depression": 0.30,  # 30% improvement in mood scores
            "stress": 0.35,  # 35% stress reduction
            "ptsd": 0.20,  # 20% symptom improvement
        }
        expected_improvement = mood_improvement_map.get(primary_condition.lower(), 0.20)

        return ExercisePrescription(
            user_id=user_id,
            condition=MentalHealthCondition(primary_condition.lower()) if primary_condition.lower() in [c.value for c in MentalHealthCondition] else MentalHealthCondition.GENERAL_WELLNESS,
            exercise_type=", ".join(intensity_exercises[:3]),
            intensity=recommended_intensity,
            duration_minutes=duration,
            frequency_per_week=4 if primary_condition.lower() in ["depression", "anxiety"] else 3,
            specific_exercises=intensity_exercises,
            mental_health_benefits=condition_data["benefits"],
            precautions=self._get_exercise_precautions(primary_condition),
            expected_mood_improvement=expected_improvement
        )

    def create_nutrition_plan(self, user_id: int, mental_health_conditions: List[str],
                            dietary_restrictions: List[str] = None,
                            current_medications: List[str] = None) -> NutritionRecommendation:
        """Create personalized nutrition plan for mental health"""

        primary_condition = mental_health_conditions[0] if mental_health_conditions else "general_wellness"

        # Get brain-supporting foods
        brain_foods = self.nutrition_database["brain_foods"]
        mood_nutrients = self.nutrition_database["mood_supporting_nutrients"]

        recommended_foods = []
        recommended_foods.extend(brain_foods["omega3_sources"][:3])
        recommended_foods.extend(brain_foods["antioxidant_rich"][:3])
        recommended_foods.extend(brain_foods["b_vitamin_sources"][:2])

        # Condition-specific recommendations
        if primary_condition.lower() == "anxiety":
            recommended_foods.extend(mood_nutrients["gaba_enhancers"])
            recommended_foods.extend(mood_nutrients["cortisol_reducers"])
            supplements = ["magnesium", "l_theanine", "omega3", "probiotics"]
        elif primary_condition.lower() == "depression":
            recommended_foods.extend(mood_nutrients["serotonin_precursors"])
            recommended_foods.extend(mood_nutrients["dopamine_supporters"])
            supplements = ["vitamin_d", "omega3", "b_complex", "5htp"]
        else:
            supplements = ["omega3", "vitamin_d", "magnesium", "probiotics"]

        # Filter out foods based on dietary restrictions
        if dietary_restrictions:
            recommended_foods = self._filter_foods_by_restrictions(recommended_foods, dietary_restrictions)

        # Foods to avoid based on condition
        foods_to_avoid = []
        if primary_condition.lower() == "anxiety":
            foods_to_avoid.extend(self.nutrition_database["foods_to_minimize"]["anxiety_triggers"])
        elif primary_condition.lower() == "depression":
            foods_to_avoid.extend(self.nutrition_database["foods_to_minimize"]["depression_aggravators"])

        return NutritionRecommendation(
            user_id=user_id,
            recommended_foods=list(set(recommended_foods)),  # Remove duplicates
            foods_to_avoid=foods_to_avoid,
            supplements=supplements,
            meal_timing=self.nutrition_database["meal_timing_strategies"]["blood_sugar_stability"],
            hydration_goal_ml=2500,  # Standard recommendation
            mental_health_nutrients=["omega3", "b_vitamins", "magnesium", "vitamin_d", "probiotics"]
        )

    def create_sleep_optimization_plan(self, user_id: int, age: int, mental_health_conditions: List[str],
                                     current_sleep_duration: float = None,
                                     sleep_issues: List[str] = None) -> SleepOptimizationPlan:
        """Create personalized sleep optimization plan"""

        # Determine age category
        if age < 18:
            age_category = "teens_14_17"
        elif age < 65:
            age_category = "adults_18_64"
        else:
            age_category = "adults_65_plus"

        optimal_duration = self.sleep_guidelines["optimal_duration"][age_category]
        recommended_duration = (optimal_duration["min"] + optimal_duration["max"]) / 2

        # Adjust based on mental health condition
        primary_condition = mental_health_conditions[0] if mental_health_conditions else None
        if primary_condition and primary_condition.lower() in ["depression", "bipolar"]:
            recommended_duration += 0.5  # May need slightly more sleep

        # Calculate optimal bedtime and wake time (assuming 7am wake time)
        wake_time = "07:00"
        bedtime_hour = 7 - recommended_duration
        if bedtime_hour < 0:
            bedtime_hour += 24
        bedtime = f"{int(bedtime_hour):02d}:{int((bedtime_hour % 1) * 60):02d}"

        # Get condition-specific recommendations
        condition_specific_tips = []
        if primary_condition:
            condition_info = self.sleep_guidelines["mental_health_sleep_connections"].get(
                primary_condition.lower(), {}
            )
            if condition_info:
                condition_specific_tips.append(f"Condition-specific: {condition_info.get('recommendations', '')}")

        sleep_tips = self.sleep_guidelines["sleep_hygiene_fundamentals"] + condition_specific_tips

        return SleepOptimizationPlan(
            user_id=user_id,
            recommended_bedtime=bedtime,
            recommended_wake_time=wake_time,
            sleep_duration_hours=recommended_duration,
            sleep_hygiene_tips=sleep_tips,
            environmental_factors={
                "temperature": "65-68°F (18-20°C)",
                "light": "Complete darkness or blackout curtains",
                "noise": "Quiet environment or white noise machine",
                "humidity": "30-50% relative humidity"
            },
            pre_sleep_routine=self.sleep_guidelines["pre_sleep_routine"]
        )

    def analyze_biometric_data(self, user_id: int, biometric_data: Dict[str, float]) -> Dict[str, Any]:
        """Analyze biometric data for mental health insights"""

        analysis = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_analyzed": [],
            "insights": [],
            "recommendations": [],
            "risk_factors": [],
            "overall_score": 0
        }

        total_score = 0
        metrics_count = 0

        # Analyze Heart Rate Variability
        if "hrv" in biometric_data:
            hrv_score = self._analyze_hrv(biometric_data["hrv"])
            analysis["metrics_analyzed"].append({"metric": "HRV", "value": biometric_data["hrv"], "score": hrv_score})
            total_score += hrv_score
            metrics_count += 1

            if hrv_score < 50:
                analysis["risk_factors"].append("Low HRV indicates high stress levels")
                analysis["recommendations"].append("Increase stress-reduction activities (meditation, yoga)")

        # Analyze Resting Heart Rate
        if "resting_hr" in biometric_data:
            hr_score = self._analyze_resting_hr(biometric_data["resting_hr"])
            analysis["metrics_analyzed"].append({"metric": "Resting HR", "value": biometric_data["resting_hr"], "score": hr_score})
            total_score += hr_score
            metrics_count += 1

        # Analyze Sleep Quality
        if "sleep_efficiency" in biometric_data:
            sleep_score = biometric_data["sleep_efficiency"] * 100  # Convert to percentage
            analysis["metrics_analyzed"].append({"metric": "Sleep Efficiency", "value": sleep_score, "score": sleep_score})
            total_score += sleep_score
            metrics_count += 1

            if sleep_score < 85:
                analysis["risk_factors"].append("Poor sleep efficiency affects mental health")
                analysis["recommendations"].append("Optimize sleep environment and bedtime routine")

        # Calculate overall score
        if metrics_count > 0:
            analysis["overall_score"] = total_score / metrics_count

        # Generate insights based on overall score
        if analysis["overall_score"] >= 80:
            analysis["insights"].append("Excellent biometric indicators for mental wellness")
        elif analysis["overall_score"] >= 60:
            analysis["insights"].append("Good biometric health with room for improvement")
        else:
            analysis["insights"].append("Biometric data suggests high stress - consider lifestyle interventions")

        return analysis

    def _get_exercise_precautions(self, condition: str) -> List[str]:
        """Get exercise precautions for specific conditions"""
        precautions = {
            "anxiety": [
                "Start slowly to avoid overwhelming the nervous system",
                "Focus on breathing during exercise",
                "Avoid overly competitive environments initially"
            ],
            "depression": [
                "Set realistic, achievable goals",
                "Consider group activities for social support",
                "Monitor for exercise addiction/over-training"
            ],
            "ptsd": [
                "Maintain awareness of surroundings during exercise",
                "Avoid triggering environments or activities",
                "Have an exit strategy if feeling overwhelmed"
            ]
        }
        return precautions.get(condition.lower(), ["Consult healthcare provider before starting new exercise program"])

    def _filter_foods_by_restrictions(self, foods: List[str], restrictions: List[str]) -> List[str]:
        """Filter food recommendations based on dietary restrictions"""
        restriction_filters = {
            "vegetarian": ["salmon", "mackerel", "sardines", "turkey", "eggs", "cheese"],
            "vegan": ["salmon", "mackerel", "sardines", "turkey", "eggs", "cheese", "yogurt", "kefir"],
            "gluten_free": ["sprouted_grains", "quinoa"],
            "dairy_free": ["yogurt", "kefir", "cheese"],
            "nut_free": ["walnuts", "almonds", "nuts", "sunflower_seeds"]
        }

        filtered_foods = foods.copy()
        for restriction in restrictions:
            if restriction.lower() in restriction_filters:
                filtered_foods = [food for food in filtered_foods
                                if food not in restriction_filters[restriction.lower()]]

        return filtered_foods

    def _analyze_hrv(self, hrv_value: float) -> float:
        """Analyze Heart Rate Variability and return score (0-100)"""
        thresholds = self.biometric_thresholds["heart_rate_variability"]

        if hrv_value >= thresholds["excellent"]["min"]:
            return 90 + min(10, (hrv_value - 50) / 5)  # 90-100
        elif hrv_value >= thresholds["good"]["min"]:
            return 70 + (hrv_value - 30) * 20 / 19  # 70-89
        elif hrv_value >= thresholds["fair"]["min"]:
            return 50 + (hrv_value - 20) * 20 / 9   # 50-69
        else:
            return max(0, hrv_value * 50 / 19)      # 0-49

    def _analyze_resting_hr(self, hr_value: float) -> float:
        """Analyze Resting Heart Rate and return score (0-100)"""
        thresholds = self.biometric_thresholds["resting_heart_rate"]

        if thresholds["excellent"]["min"] <= hr_value <= thresholds["excellent"]["max"]:
            return 95
        elif thresholds["good"]["min"] <= hr_value <= thresholds["good"]["max"]:
            return 80
        elif thresholds["fair"]["min"] <= hr_value <= thresholds["fair"]["max"]:
            return 65
        else:
            return 40  # Needs attention

# Create singleton instance
physical_health_integrator = PhysicalHealthIntegrator()