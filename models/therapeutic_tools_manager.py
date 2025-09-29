"""
Advanced Therapeutic Tools Manager - Phase 3 Implementation
Implements VR/AR therapy, biofeedback integration, and personalized AI therapy
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import random
import math

class TherapyMode(Enum):
    VR_IMMERSIVE = "vr_immersive"
    AR_OVERLAY = "ar_overlay"
    BIOFEEDBACK = "biofeedback"
    AI_PERSONALIZED = "ai_personalized"
    HYBRID = "hybrid"

class BiometricType(Enum):
    HEART_RATE = "heart_rate"
    SKIN_CONDUCTANCE = "skin_conductance"
    BREATHING_RATE = "breathing_rate"
    EEG = "eeg"
    MUSCLE_TENSION = "muscle_tension"
    TEMPERATURE = "temperature"

class TherapyIntensity(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    ADAPTIVE = "adaptive"

class VREnvironment(Enum):
    BEACH_CALM = "beach_calm"
    FOREST_MEDITATION = "forest_meditation"
    MOUNTAIN_TOP = "mountain_top"
    SPACE_EXPLORATION = "space_exploration"
    UNDERWATER = "underwater"
    GARDEN_PEACEFUL = "garden_peaceful"
    EXPOSURE_GRADUAL = "exposure_gradual"
    TRAUMA_PROCESSING = "trauma_processing"

@dataclass
class BiometricReading:
    reading_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    biometric_type: BiometricType = BiometricType.HEART_RATE
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    device_id: str = ""
    quality_score: float = 1.0  # 0-1, measurement reliability
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VRTherapySession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    environment: VREnvironment = VREnvironment.BEACH_CALM
    therapy_type: str = "relaxation"  # anxiety, ptsd, phobia, etc.
    duration_minutes: int = 20
    intensity: TherapyIntensity = TherapyIntensity.MODERATE
    biometric_integration: bool = True
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    effectiveness_score: Optional[float] = None
    user_feedback: Dict[str, Any] = field(default_factory=dict)
    biometric_data: List[BiometricReading] = field(default_factory=list)
    adaptation_notes: List[str] = field(default_factory=list)

@dataclass
class PersonalizedTherapyPlan:
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    primary_conditions: List[str] = field(default_factory=list)
    therapy_preferences: Dict[str, Any] = field(default_factory=dict)
    biometric_baselines: Dict[BiometricType, float] = field(default_factory=dict)
    vr_environments: List[VREnvironment] = field(default_factory=list)
    session_frequency: str = "3x_weekly"  # daily, weekly, 3x_weekly
    progress_milestones: List[Dict[str, Any]] = field(default_factory=list)
    ai_personality_match: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    effectiveness_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class BiofeedbackExercise:
    exercise_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    target_biometric: BiometricType = BiometricType.HEART_RATE
    target_range: Tuple[float, float] = (60.0, 100.0)
    exercise_type: str = "breathing"  # breathing, muscle_relaxation, meditation
    duration_minutes: int = 10
    difficulty_level: int = 1  # 1-5
    instructions: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    real_time_feedback: bool = True

@dataclass
class TherapyOutcome:
    outcome_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    user_id: str = ""
    pre_session_mood: int = 5  # 1-10 scale
    post_session_mood: int = 5
    anxiety_reduction: float = 0.0  # percentage
    engagement_score: float = 0.0  # 0-1
    biometric_improvement: Dict[BiometricType, float] = field(default_factory=dict)
    user_satisfaction: int = 5  # 1-10
    side_effects: List[str] = field(default_factory=list)
    therapist_notes: str = ""
    follow_up_recommended: bool = False

class TherapeuticToolsManager:
    def __init__(self):
        self.active_sessions: Dict[str, VRTherapySession] = {}
        self.therapy_plans: Dict[str, PersonalizedTherapyPlan] = {}
        self.biofeedback_exercises = self._initialize_biofeedback_exercises()
        self.vr_environments = self._initialize_vr_environments()
        self.ai_therapy_models = self._initialize_ai_models()
        self.biometric_devices: Dict[str, Dict[str, Any]] = {}

    def _initialize_biofeedback_exercises(self) -> List[BiofeedbackExercise]:
        """Initialize library of biofeedback exercises"""
        exercises = []

        # Breathing exercises
        exercises.append(BiofeedbackExercise(
            name="4-7-8 Breathing",
            description="Deep breathing technique for anxiety relief",
            target_biometric=BiometricType.BREATHING_RATE,
            target_range=(4.0, 6.0),
            exercise_type="breathing",
            duration_minutes=5,
            difficulty_level=1,
            instructions=[
                "Exhale completely through your mouth",
                "Close mouth and inhale through nose for 4 counts",
                "Hold breath for 7 counts",
                "Exhale through mouth for 8 counts",
                "Repeat cycle 4 times"
            ],
            success_criteria={
                "breathing_rate_stability": 0.8,
                "target_range_maintenance": 0.7
            }
        ))

        # Heart rate variability
        exercises.append(BiofeedbackExercise(
            name="Heart Coherence Training",
            description="Improve heart rate variability for stress reduction",
            target_biometric=BiometricType.HEART_RATE,
            target_range=(60.0, 80.0),
            exercise_type="heart_coherence",
            duration_minutes=10,
            difficulty_level=2,
            instructions=[
                "Breathe slowly and rhythmically",
                "Focus on heart area",
                "Generate positive emotions (gratitude, care)",
                "Match breathing to heart rhythm feedback",
                "Maintain coherent pattern"
            ],
            success_criteria={
                "coherence_ratio": 0.6,
                "sustained_coherence_time": 300  # seconds
            }
        ))

        # Muscle tension release
        exercises.append(BiofeedbackExercise(
            name="Progressive Muscle Relaxation",
            description="Systematic muscle tension and release",
            target_biometric=BiometricType.MUSCLE_TENSION,
            target_range=(0.0, 20.0),  # micro-volts
            exercise_type="muscle_relaxation",
            duration_minutes=15,
            difficulty_level=3,
            instructions=[
                "Tense muscle group for 5 seconds",
                "Release and notice relaxation",
                "Focus on contrast between tension/relaxation",
                "Move systematically through body",
                "End with full body scan"
            ],
            success_criteria={
                "tension_reduction": 0.5,
                "sustained_relaxation": 0.7
            }
        ))

        return exercises

    def _initialize_vr_environments(self) -> Dict[VREnvironment, Dict[str, Any]]:
        """Initialize VR therapy environments"""
        return {
            VREnvironment.BEACH_CALM: {
                "name": "Tranquil Beach",
                "description": "Peaceful ocean waves with warm sand",
                "therapy_types": ["anxiety", "stress", "relaxation"],
                "intensity_levels": [TherapyIntensity.LOW, TherapyIntensity.MODERATE],
                "biometric_targets": {
                    BiometricType.HEART_RATE: (60, 80),
                    BiometricType.BREATHING_RATE: (8, 12)
                },
                "adaptive_elements": ["wave_intensity", "weather", "time_of_day"]
            },
            VREnvironment.FOREST_MEDITATION: {
                "name": "Mindful Forest",
                "description": "Serene forest with meditation guidance",
                "therapy_types": ["mindfulness", "depression", "focus"],
                "intensity_levels": [TherapyIntensity.LOW, TherapyIntensity.MODERATE, TherapyIntensity.HIGH],
                "biometric_targets": {
                    BiometricType.EEG: (8, 13),  # Alpha waves
                    BiometricType.MUSCLE_TENSION: (0, 15)
                },
                "adaptive_elements": ["forest_density", "wildlife_sounds", "lighting"]
            },
            VREnvironment.EXPOSURE_GRADUAL: {
                "name": "Gradual Exposure Therapy",
                "description": "Controlled exposure for phobia treatment",
                "therapy_types": ["phobia", "ptsd", "anxiety"],
                "intensity_levels": [TherapyIntensity.LOW, TherapyIntensity.MODERATE, TherapyIntensity.HIGH, TherapyIntensity.ADAPTIVE],
                "biometric_targets": {
                    BiometricType.HEART_RATE: (70, 120),
                    BiometricType.SKIN_CONDUCTANCE: (2, 8)
                },
                "adaptive_elements": ["exposure_distance", "object_size", "interaction_level"]
            }
        }

    def _initialize_ai_models(self) -> Dict[str, Dict[str, Any]]:
        """Initialize AI therapy personality models"""
        return {
            "cognitive_behavioral": {
                "name": "CBT Therapist",
                "approach": "Structured, goal-oriented cognitive restructuring",
                "personality_traits": {
                    "empathy": 0.8,
                    "directness": 0.9,
                    "patience": 0.7,
                    "analytical": 0.9
                },
                "techniques": ["thought_challenging", "behavioral_experiments", "goal_setting"],
                "suitable_conditions": ["anxiety", "depression", "panic"]
            },
            "mindfulness_based": {
                "name": "Mindfulness Guide",
                "approach": "Present-moment awareness and acceptance",
                "personality_traits": {
                    "empathy": 0.9,
                    "directness": 0.4,
                    "patience": 0.9,
                    "analytical": 0.5
                },
                "techniques": ["meditation", "body_scanning", "breathing_awareness"],
                "suitable_conditions": ["stress", "chronic_pain", "emotional_regulation"]
            },
            "trauma_informed": {
                "name": "Trauma Specialist",
                "approach": "Safety-first trauma processing",
                "personality_traits": {
                    "empathy": 0.95,
                    "directness": 0.6,
                    "patience": 0.95,
                    "analytical": 0.7
                },
                "techniques": ["grounding", "resource_building", "gradual_exposure"],
                "suitable_conditions": ["ptsd", "trauma", "dissociation"]
            }
        }

    def create_personalized_therapy_plan(self, user_id: str, conditions: List[str],
                                       preferences: Dict[str, Any]) -> PersonalizedTherapyPlan:
        """Create personalized therapy plan based on user profile"""

        # Select appropriate VR environments
        recommended_environments = []
        for env, config in self.vr_environments.items():
            if any(condition in config["therapy_types"] for condition in conditions):
                recommended_environments.append(env)

        # Match AI personality
        ai_matches = {}
        for model_name, model_config in self.ai_therapy_models.items():
            compatibility = sum(1 for condition in conditions
                              if condition in model_config["suitable_conditions"])
            ai_matches[model_name] = compatibility / len(conditions) if conditions else 0

        # Set biometric baselines (would normally come from assessment)
        baselines = {
            BiometricType.HEART_RATE: 75.0,
            BiometricType.BREATHING_RATE: 16.0,
            BiometricType.SKIN_CONDUCTANCE: 3.0,
            BiometricType.MUSCLE_TENSION: 25.0
        }

        plan = PersonalizedTherapyPlan(
            user_id=user_id,
            primary_conditions=conditions,
            therapy_preferences=preferences,
            biometric_baselines=baselines,
            vr_environments=recommended_environments[:3],  # Top 3
            session_frequency=preferences.get("frequency", "3x_weekly"),
            ai_personality_match=ai_matches
        )

        # Create progress milestones
        plan.progress_milestones = self._generate_milestones(conditions, plan.session_frequency)

        self.therapy_plans[user_id] = plan
        return plan

    def _generate_milestones(self, conditions: List[str], frequency: str) -> List[Dict[str, Any]]:
        """Generate therapy progress milestones"""
        milestones = []

        base_milestones = [
            {
                "week": 2,
                "goal": "Complete biometric baseline establishment",
                "metrics": ["biometric_stability", "user_comfort"],
                "target_values": [0.8, 0.7]
            },
            {
                "week": 4,
                "goal": "Achieve consistent session engagement",
                "metrics": ["session_completion", "engagement_score"],
                "target_values": [0.9, 0.75]
            },
            {
                "week": 8,
                "goal": "Demonstrate measurable symptom improvement",
                "metrics": ["anxiety_reduction", "mood_improvement"],
                "target_values": [0.3, 0.25]
            },
            {
                "week": 12,
                "goal": "Maintain therapeutic gains independently",
                "metrics": ["self_regulation", "tool_usage"],
                "target_values": [0.8, 0.6]
            }
        ]

        # Customize based on conditions
        for milestone in base_milestones:
            customized = milestone.copy()
            if "ptsd" in conditions:
                customized["metrics"].append("trauma_processing_comfort")
                customized["target_values"].append(0.6)
            if "anxiety" in conditions:
                customized["metrics"].append("panic_frequency_reduction")
                customized["target_values"].append(0.4)

            milestones.append(customized)

        return milestones

    def start_vr_therapy_session(self, user_id: str, environment: VREnvironment,
                                therapy_type: str = "general") -> VRTherapySession:
        """Start a VR therapy session with biometric monitoring"""

        # Get user's therapy plan for personalization
        plan = self.therapy_plans.get(user_id)
        intensity = TherapyIntensity.ADAPTIVE if plan else TherapyIntensity.MODERATE

        session = VRTherapySession(
            user_id=user_id,
            environment=environment,
            therapy_type=therapy_type,
            intensity=intensity,
            biometric_integration=True,
            started_at=datetime.now()
        )

        self.active_sessions[session.session_id] = session

        # Initialize biometric monitoring
        self._start_biometric_monitoring(session.session_id)

        return session

    def _start_biometric_monitoring(self, session_id: str):
        """Start real-time biometric monitoring for session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return

        # Simulate biometric device initialization
        # In real implementation, this would connect to actual devices
        device_types = [BiometricType.HEART_RATE, BiometricType.BREATHING_RATE,
                       BiometricType.SKIN_CONDUCTANCE, BiometricType.MUSCLE_TENSION]

        for device_type in device_types:
            device_id = f"{device_type.value}_{session_id[:8]}"
            self.biometric_devices[device_id] = {
                "session_id": session_id,
                "type": device_type,
                "status": "active",
                "last_reading": datetime.now()
            }

    def process_biometric_reading(self, session_id: str, biometric_type: BiometricType,
                                value: float, device_id: str = "") -> bool:
        """Process real-time biometric reading and adapt session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False

        reading = BiometricReading(
            user_id=session.user_id,
            biometric_type=biometric_type,
            value=value,
            device_id=device_id,
            context={"session_id": session_id}
        )

        session.biometric_data.append(reading)

        # Adaptive session adjustment based on biometric feedback
        if session.intensity == TherapyIntensity.ADAPTIVE:
            self._adapt_session_to_biometrics(session, reading)

        return True

    def _adapt_session_to_biometrics(self, session: VRTherapySession, reading: BiometricReading):
        """Adapt VR session based on biometric feedback"""
        env_config = self.vr_environments[session.environment]
        target_range = env_config["biometric_targets"].get(reading.biometric_type)

        if not target_range:
            return

        min_val, max_val = target_range
        adaptation_needed = False

        if reading.value < min_val:
            # User too relaxed/disengaged - increase intensity
            adaptation = f"Increased {session.environment.value} intensity due to low {reading.biometric_type.value}"
            session.adaptation_notes.append(adaptation)
            adaptation_needed = True

        elif reading.value > max_val:
            # User overstimulated/stressed - decrease intensity
            adaptation = f"Decreased {session.environment.value} intensity due to high {reading.biometric_type.value}"
            session.adaptation_notes.append(adaptation)
            adaptation_needed = True

        if adaptation_needed:
            # In real implementation, this would send commands to VR system
            print(f"Adapting session {session.session_id}: {session.adaptation_notes[-1]}")

    def complete_vr_session(self, session_id: str, user_feedback: Dict[str, Any]) -> TherapyOutcome:
        """Complete VR therapy session and generate outcome"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        session.completed_at = datetime.now()
        session.user_feedback = user_feedback

        # Calculate effectiveness score
        session.effectiveness_score = self._calculate_effectiveness(session)

        # Generate therapy outcome
        outcome = TherapyOutcome(
            session_id=session_id,
            user_id=session.user_id,
            pre_session_mood=user_feedback.get("pre_mood", 5),
            post_session_mood=user_feedback.get("post_mood", 5),
            user_satisfaction=user_feedback.get("satisfaction", 5)
        )

        # Calculate biometric improvements
        outcome.biometric_improvement = self._calculate_biometric_improvements(session)
        outcome.anxiety_reduction = self._calculate_anxiety_reduction(session)
        outcome.engagement_score = session.effectiveness_score

        # Clean up monitoring
        self._stop_biometric_monitoring(session_id)
        del self.active_sessions[session_id]

        return outcome

    def _calculate_effectiveness(self, session: VRTherapySession) -> float:
        """Calculate session effectiveness based on multiple factors"""
        factors = []

        # Duration completion factor
        expected_duration = session.duration_minutes * 60
        actual_duration = (session.completed_at - session.started_at).total_seconds()
        completion_factor = min(actual_duration / expected_duration, 1.0)
        factors.append(completion_factor * 0.3)

        # Biometric stability factor
        if session.biometric_data:
            stability_scores = []
            for biometric_type in [BiometricType.HEART_RATE, BiometricType.BREATHING_RATE]:
                readings = [r.value for r in session.biometric_data if r.biometric_type == biometric_type]
                if readings and len(readings) > 3:
                    # Calculate coefficient of variation (lower is more stable)
                    mean_val = sum(readings) / len(readings)
                    variance = sum((x - mean_val) ** 2 for x in readings) / len(readings)
                    cv = math.sqrt(variance) / mean_val if mean_val > 0 else 1
                    stability = max(0, 1 - cv)  # Convert to 0-1 where 1 is stable
                    stability_scores.append(stability)

            if stability_scores:
                factors.append(sum(stability_scores) / len(stability_scores) * 0.4)

        # User feedback factor
        if session.user_feedback:
            satisfaction = session.user_feedback.get("satisfaction", 5) / 10.0
            factors.append(satisfaction * 0.3)

        return sum(factors) if factors else 0.5

    def _calculate_biometric_improvements(self, session: VRTherapySession) -> Dict[BiometricType, float]:
        """Calculate improvement in biometric measures during session"""
        improvements = {}

        for biometric_type in [BiometricType.HEART_RATE, BiometricType.BREATHING_RATE,
                              BiometricType.MUSCLE_TENSION]:
            readings = [r.value for r in session.biometric_data if r.biometric_type == biometric_type]

            if len(readings) > 5:
                # Compare first and last quartiles
                quarter_point = len(readings) // 4
                early_avg = sum(readings[:quarter_point]) / quarter_point
                late_avg = sum(readings[-quarter_point:]) / quarter_point

                # Calculate improvement (depends on metric)
                if biometric_type in [BiometricType.HEART_RATE, BiometricType.MUSCLE_TENSION]:
                    # Lower is better
                    improvement = (early_avg - late_avg) / early_avg if early_avg > 0 else 0
                else:
                    # Stability is better (less variation)
                    early_std = math.sqrt(sum((x - early_avg) ** 2 for x in readings[:quarter_point]) / quarter_point)
                    late_std = math.sqrt(sum((x - late_avg) ** 2 for x in readings[-quarter_point:]) / quarter_point)
                    improvement = (early_std - late_std) / early_std if early_std > 0 else 0

                improvements[biometric_type] = max(-1.0, min(1.0, improvement))

        return improvements

    def _calculate_anxiety_reduction(self, session: VRTherapySession) -> float:
        """Calculate anxiety reduction based on biometrics and feedback"""
        # Heart rate variability improvement
        hr_readings = [r.value for r in session.biometric_data if r.biometric_type == BiometricType.HEART_RATE]
        hr_reduction = 0

        if len(hr_readings) > 10:
            initial_hr = sum(hr_readings[:5]) / 5
            final_hr = sum(hr_readings[-5:]) / 5
            hr_reduction = max(0, (initial_hr - final_hr) / initial_hr)

        # User-reported mood improvement
        mood_improvement = 0
        if session.user_feedback:
            pre_mood = session.user_feedback.get("pre_mood", 5)
            post_mood = session.user_feedback.get("post_mood", 5)
            mood_improvement = (post_mood - pre_mood) / 10.0

        # Combine metrics
        return (hr_reduction * 0.6 + mood_improvement * 0.4)

    def _stop_biometric_monitoring(self, session_id: str):
        """Stop biometric monitoring for session"""
        devices_to_remove = []
        for device_id, device_info in self.biometric_devices.items():
            if device_info["session_id"] == session_id:
                devices_to_remove.append(device_id)

        for device_id in devices_to_remove:
            del self.biometric_devices[device_id]

    def get_user_therapy_progress(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive therapy progress for user"""
        plan = self.therapy_plans.get(user_id)
        if not plan:
            return {"error": "No therapy plan found"}

        # Simulate historical session data
        sessions_completed = random.randint(5, 25)
        weeks_active = random.randint(2, 12)

        progress = {
            "plan_id": plan.plan_id,
            "weeks_active": weeks_active,
            "sessions_completed": sessions_completed,
            "current_milestone": self._get_current_milestone(plan, weeks_active),
            "biometric_trends": self._generate_biometric_trends(plan),
            "effectiveness_trends": self._generate_effectiveness_trends(sessions_completed),
            "upcoming_sessions": self._get_upcoming_sessions(plan),
            "adaptation_history": self._get_adaptation_history(user_id)
        }

        return progress

    def _get_current_milestone(self, plan: PersonalizedTherapyPlan, weeks_active: int) -> Dict[str, Any]:
        """Get current therapy milestone"""
        current_milestone = None
        for milestone in plan.progress_milestones:
            if weeks_active >= milestone["week"]:
                current_milestone = milestone
            else:
                break

        if current_milestone:
            # Simulate progress on current milestone
            progress = random.uniform(0.4, 0.9)
            current_milestone["progress"] = progress
            current_milestone["on_track"] = progress >= 0.6

        return current_milestone or plan.progress_milestones[0]

    def _generate_biometric_trends(self, plan: PersonalizedTherapyPlan) -> Dict[str, List[float]]:
        """Generate simulated biometric improvement trends"""
        trends = {}
        for biometric_type, baseline in plan.biometric_baselines.items():
            # Simulate gradual improvement over time
            trend = []
            current_value = baseline
            improvement_rate = random.uniform(0.01, 0.05)  # 1-5% improvement per session

            for session in range(10):  # Last 10 sessions
                # Add some noise but overall improvement
                noise = random.uniform(-0.1, 0.1)
                if biometric_type in [BiometricType.HEART_RATE, BiometricType.MUSCLE_TENSION]:
                    # Lower is better
                    current_value *= (1 - improvement_rate + noise)
                else:
                    # Higher stability is better
                    current_value *= (1 + improvement_rate + noise)

                trend.append(round(current_value, 2))

            trends[biometric_type.value] = trend

        return trends

    def _generate_effectiveness_trends(self, sessions_completed: int) -> List[float]:
        """Generate session effectiveness trends"""
        # Simulate learning curve - effectiveness improves over time
        trends = []
        base_effectiveness = 0.4

        for session in range(min(sessions_completed, 20)):
            # Gradual improvement with some variation
            improvement = session * 0.02  # 2% improvement per session
            variation = random.uniform(-0.1, 0.1)
            effectiveness = min(1.0, base_effectiveness + improvement + variation)
            trends.append(round(effectiveness, 2))

        return trends

    def _get_upcoming_sessions(self, plan: PersonalizedTherapyPlan) -> List[Dict[str, Any]]:
        """Get upcoming recommended sessions"""
        sessions = []
        base_time = datetime.now() + timedelta(days=1)

        frequency_map = {
            "daily": 1,
            "3x_weekly": 2,
            "weekly": 7
        }

        interval = frequency_map.get(plan.session_frequency, 2)

        for i in range(3):  # Next 3 sessions
            session_time = base_time + timedelta(days=i * interval)

            # Rotate through preferred VR environments
            environment = plan.vr_environments[i % len(plan.vr_environments)]

            sessions.append({
                "scheduled_time": session_time.isoformat(),
                "environment": environment.value,
                "therapy_type": plan.primary_conditions[0] if plan.primary_conditions else "general",
                "estimated_duration": 20,
                "preparation_needed": True
            })

        return sessions

    def _get_adaptation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get history of session adaptations"""
        # Simulate adaptation history
        adaptations = [
            {
                "date": (datetime.now() - timedelta(days=7)).isoformat(),
                "session_type": "vr_forest",
                "adaptation": "Reduced lighting intensity due to elevated heart rate",
                "biometric_trigger": "heart_rate > 100 bpm",
                "effectiveness": "improved_completion"
            },
            {
                "date": (datetime.now() - timedelta(days=3)).isoformat(),
                "session_type": "vr_beach",
                "adaptation": "Extended breathing exercise segment",
                "biometric_trigger": "breathing_rate > 20/min",
                "effectiveness": "better_relaxation"
            }
        ]

        return adaptations

    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get platform-wide therapeutic tools statistics"""
        return {
            "total_therapy_plans": len(self.therapy_plans),
            "active_vr_sessions": len(self.active_sessions),
            "biofeedback_exercises": len(self.biofeedback_exercises),
            "vr_environments": len(self.vr_environments),
            "ai_therapy_models": len(self.ai_therapy_models),
            "connected_devices": len(self.biometric_devices),
            "weekly_sessions_completed": random.randint(50, 200),
            "average_effectiveness_score": round(random.uniform(0.6, 0.85), 2),
            "user_satisfaction_rating": round(random.uniform(4.2, 4.8), 1),
            "biometric_integration_rate": round(random.uniform(0.75, 0.95), 2)
        }

# Global instance
therapeutic_tools_manager = TherapeuticToolsManager()