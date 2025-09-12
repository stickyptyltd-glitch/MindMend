"""
Advanced Treatment Recommendation System
Uses multiple AI models to provide personalized treatment recommendations
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TreatmentType(Enum):
    """Types of treatment modalities"""
    COGNITIVE_BEHAVIORAL = "cbt"
    DIALECTICAL_BEHAVIORAL = "dbt"
    ACCEPTANCE_COMMITMENT = "act"
    MINDFULNESS_BASED = "mbsr"
    PSYCHODYNAMIC = "psychodynamic"
    SOMATIC = "somatic"
    EMDR = "emdr"
    MEDICATION = "medication"
    LIFESTYLE = "lifestyle"
    COMPLEMENTARY = "complementary"

class TreatmentIntensity(Enum):
    """Treatment intensity levels"""
    SELF_GUIDED = "self_guided"
    WEEKLY_SESSIONS = "weekly"
    BIWEEKLY_SESSIONS = "biweekly"
    INTENSIVE = "intensive"
    CRISIS = "crisis"

@dataclass
class TreatmentPlan:
    """Comprehensive treatment plan"""
    primary_modality: TreatmentType
    secondary_modalities: List[TreatmentType]
    intensity: TreatmentIntensity
    duration_weeks: int
    activities: List[Dict[str, Any]]
    goals: List[Dict[str, Any]]
    monitoring_plan: Dict[str, Any]
    confidence_score: float
    ai_consensus: Dict[str, Any]

class TreatmentRecommender:
    """Advanced treatment recommendation system"""
    
    def __init__(self, ai_model_manager):
        self.ai_manager = ai_model_manager
        self.treatment_database = self._initialize_treatment_database()
        self.activity_library = self._initialize_activity_library()
        self.evidence_base = {}
        
    def _initialize_treatment_database(self) -> Dict[str, Any]:
        """Initialize comprehensive treatment database"""
        return {
            'anxiety': {
                'primary_modalities': [TreatmentType.COGNITIVE_BEHAVIORAL, TreatmentType.ACCEPTANCE_COMMITMENT],
                'evidence_level': 'high',
                'typical_duration': 12,
                'success_rate': 0.78
            },
            'depression': {
                'primary_modalities': [TreatmentType.COGNITIVE_BEHAVIORAL, TreatmentType.MINDFULNESS_BASED],
                'evidence_level': 'high',
                'typical_duration': 16,
                'success_rate': 0.75
            },
            'ptsd': {
                'primary_modalities': [TreatmentType.EMDR, TreatmentType.COGNITIVE_BEHAVIORAL],
                'evidence_level': 'high',
                'typical_duration': 20,
                'success_rate': 0.72
            },
            'relationship_issues': {
                'primary_modalities': [TreatmentType.PSYCHODYNAMIC, TreatmentType.ACCEPTANCE_COMMITMENT],
                'evidence_level': 'moderate',
                'typical_duration': 24,
                'success_rate': 0.70
            },
            'substance_use': {
                'primary_modalities': [TreatmentType.DIALECTICAL_BEHAVIORAL, TreatmentType.MINDFULNESS_BASED],
                'evidence_level': 'high',
                'typical_duration': 26,
                'success_rate': 0.65
            }
        }
    
    def _initialize_activity_library(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize comprehensive activity library"""
        return {
            TreatmentType.COGNITIVE_BEHAVIORAL: [
                {
                    'name': 'Thought Record',
                    'description': 'Track and challenge negative thought patterns',
                    'frequency': 'daily',
                    'duration_minutes': 15,
                    'difficulty': 'moderate',
                    'effectiveness': 0.85,
                    'digital_tool': True
                },
                {
                    'name': 'Behavioral Activation Schedule',
                    'description': 'Plan and track mood-boosting activities',
                    'frequency': 'daily',
                    'duration_minutes': 20,
                    'difficulty': 'easy',
                    'effectiveness': 0.82,
                    'digital_tool': True
                },
                {
                    'name': 'Cognitive Restructuring Exercise',
                    'description': 'Identify and modify cognitive distortions',
                    'frequency': '3x/week',
                    'duration_minutes': 30,
                    'difficulty': 'moderate',
                    'effectiveness': 0.88,
                    'digital_tool': True
                }
            ],
            TreatmentType.MINDFULNESS_BASED: [
                {
                    'name': 'Body Scan Meditation',
                    'description': 'Progressive relaxation through body awareness',
                    'frequency': 'daily',
                    'duration_minutes': 20,
                    'difficulty': 'easy',
                    'effectiveness': 0.80,
                    'digital_tool': True,
                    'guided_audio': True
                },
                {
                    'name': 'Mindful Breathing',
                    'description': 'Focused attention on breath',
                    'frequency': '2x/day',
                    'duration_minutes': 10,
                    'difficulty': 'easy',
                    'effectiveness': 0.78,
                    'digital_tool': True
                },
                {
                    'name': 'Loving-Kindness Meditation',
                    'description': 'Cultivate compassion for self and others',
                    'frequency': '3x/week',
                    'duration_minutes': 25,
                    'difficulty': 'moderate',
                    'effectiveness': 0.76,
                    'digital_tool': True,
                    'guided_audio': True
                }
            ],
            TreatmentType.DIALECTICAL_BEHAVIORAL: [
                {
                    'name': 'Distress Tolerance Skills',
                    'description': 'TIPP technique for crisis management',
                    'frequency': 'as needed',
                    'duration_minutes': 5,
                    'difficulty': 'moderate',
                    'effectiveness': 0.90,
                    'digital_tool': True,
                    'crisis_tool': True
                },
                {
                    'name': 'Emotion Regulation Diary',
                    'description': 'Track emotions and triggers',
                    'frequency': 'daily',
                    'duration_minutes': 10,
                    'difficulty': 'easy',
                    'effectiveness': 0.83,
                    'digital_tool': True
                },
                {
                    'name': 'Interpersonal Effectiveness Practice',
                    'description': 'DEARMAN technique for assertive communication',
                    'frequency': 'weekly',
                    'duration_minutes': 30,
                    'difficulty': 'hard',
                    'effectiveness': 0.85,
                    'digital_tool': True
                }
            ],
            TreatmentType.ACCEPTANCE_COMMITMENT: [
                {
                    'name': 'Values Clarification Exercise',
                    'description': 'Identify and prioritize personal values',
                    'frequency': 'weekly',
                    'duration_minutes': 45,
                    'difficulty': 'moderate',
                    'effectiveness': 0.87,
                    'digital_tool': True
                },
                {
                    'name': 'Defusion Techniques',
                    'description': 'Distance yourself from unhelpful thoughts',
                    'frequency': 'daily',
                    'duration_minutes': 10,
                    'difficulty': 'moderate',
                    'effectiveness': 0.81,
                    'digital_tool': True
                },
                {
                    'name': 'Committed Action Planning',
                    'description': 'Set value-based goals and actions',
                    'frequency': 'weekly',
                    'duration_minutes': 30,
                    'difficulty': 'moderate',
                    'effectiveness': 0.84,
                    'digital_tool': True
                }
            ],
            TreatmentType.SOMATIC: [
                {
                    'name': 'Progressive Muscle Relaxation',
                    'description': 'Systematic tension and release',
                    'frequency': 'daily',
                    'duration_minutes': 20,
                    'difficulty': 'easy',
                    'effectiveness': 0.79,
                    'digital_tool': True,
                    'guided_audio': True
                },
                {
                    'name': 'Grounding Exercises',
                    'description': '5-4-3-2-1 sensory awareness technique',
                    'frequency': 'as needed',
                    'duration_minutes': 5,
                    'difficulty': 'easy',
                    'effectiveness': 0.82,
                    'digital_tool': True
                }
            ],
            TreatmentType.LIFESTYLE: [
                {
                    'name': 'Sleep Hygiene Protocol',
                    'description': 'Optimize sleep environment and habits',
                    'frequency': 'daily',
                    'duration_minutes': 30,
                    'difficulty': 'moderate',
                    'effectiveness': 0.77,
                    'digital_tool': True
                },
                {
                    'name': 'Exercise Planning',
                    'description': 'Structured physical activity schedule',
                    'frequency': '5x/week',
                    'duration_minutes': 30,
                    'difficulty': 'moderate',
                    'effectiveness': 0.81,
                    'digital_tool': True
                },
                {
                    'name': 'Nutrition Tracking',
                    'description': 'Monitor mood-food connections',
                    'frequency': 'daily',
                    'duration_minutes': 10,
                    'difficulty': 'easy',
                    'effectiveness': 0.73,
                    'digital_tool': True
                }
            ]
        }
    
    def generate_personalized_treatment_plan(self, 
                                           diagnosis: Dict[str, Any],
                                           patient_profile: Dict[str, Any],
                                           preferences: Dict[str, Any] = None) -> TreatmentPlan:
        """Generate comprehensive personalized treatment plan using AI consensus"""
        
        # Get AI consensus on treatment approach
        treatment_query = {
            'diagnosis': diagnosis,
            'patient_profile': patient_profile,
            'preferences': preferences or {},
            'query_type': 'treatment_recommendation'
        }
        
        ai_recommendations = self.ai_manager.diagnose_with_ensemble(treatment_query)
        
        # Determine primary condition
        primary_condition = self._extract_primary_condition(diagnosis)
        
        # Get evidence-based recommendations
        evidence_based = self.treatment_database.get(
            primary_condition, 
            self.treatment_database['anxiety']  # Default
        )
        
        # Select treatment modalities
        primary_modality = self._select_primary_modality(
            evidence_based['primary_modalities'],
            patient_profile,
            preferences
        )
        
        secondary_modalities = self._select_secondary_modalities(
            primary_modality,
            patient_profile,
            diagnosis
        )
        
        # Determine intensity
        intensity = self._determine_treatment_intensity(
            diagnosis,
            patient_profile
        )
        
        # Generate activity plan
        activities = self._generate_activity_plan(
            primary_modality,
            secondary_modalities,
            intensity,
            patient_profile
        )
        
        # Set treatment goals
        goals = self._generate_treatment_goals(
            diagnosis,
            patient_profile,
            evidence_based['typical_duration']
        )
        
        # Create monitoring plan
        monitoring_plan = self._create_monitoring_plan(
            diagnosis,
            intensity
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_plan_confidence(
            ai_recommendations,
            evidence_based['evidence_level'],
            patient_profile
        )
        
        return TreatmentPlan(
            primary_modality=primary_modality,
            secondary_modalities=secondary_modalities,
            intensity=intensity,
            duration_weeks=evidence_based['typical_duration'],
            activities=activities,
            goals=goals,
            monitoring_plan=monitoring_plan,
            confidence_score=confidence_score,
            ai_consensus=ai_recommendations
        )
    
    def _extract_primary_condition(self, diagnosis: Dict[str, Any]) -> str:
        """Extract primary condition from diagnosis"""
        primary_diagnosis = diagnosis.get('primary_diagnosis', '').lower()
        
        condition_map = {
            'anxiety': 'anxiety',
            'depression': 'depression',
            'ptsd': 'ptsd',
            'trauma': 'ptsd',
            'relationship': 'relationship_issues',
            'couples': 'relationship_issues',
            'substance': 'substance_use',
            'addiction': 'substance_use'
        }
        
        for keyword, condition in condition_map.items():
            if keyword in primary_diagnosis:
                return condition
        
        return 'anxiety'  # Default
    
    def _select_primary_modality(self, 
                                recommended_modalities: List[TreatmentType],
                                patient_profile: Dict[str, Any],
                                preferences: Dict[str, Any]) -> TreatmentType:
        """Select primary treatment modality based on multiple factors"""
        
        # Score each modality
        modality_scores = {}
        
        for modality in recommended_modalities:
            score = 1.0  # Base score
            
            # Adjust for patient factors
            if patient_profile.get('age', 30) < 25 and modality == TreatmentType.COGNITIVE_BEHAVIORAL:
                score *= 1.2  # CBT works well for younger patients
            
            if patient_profile.get('previous_therapy_success') == modality.value:
                score *= 1.5  # Previous success increases likelihood
            
            # Adjust for preferences
            if preferences:
                if modality.value in preferences.get('preferred_modalities', []):
                    score *= 1.3
                if modality.value in preferences.get('avoided_modalities', []):
                    score *= 0.5
            
            modality_scores[modality] = score
        
        # Select highest scoring modality
        return max(modality_scores.items(), key=lambda x: x[1])[0]
    
    def _select_secondary_modalities(self,
                                   primary: TreatmentType,
                                   patient_profile: Dict[str, Any],
                                   diagnosis: Dict[str, Any]) -> List[TreatmentType]:
        """Select complementary treatment modalities"""
        secondary = []
        
        # Always include lifestyle modifications
        secondary.append(TreatmentType.LIFESTYLE)
        
        # Add mindfulness if stress is high
        if patient_profile.get('stress_level', 5) > 7:
            secondary.append(TreatmentType.MINDFULNESS_BASED)
        
        # Add somatic if trauma is present
        if 'trauma' in diagnosis.get('primary_diagnosis', '').lower():
            secondary.append(TreatmentType.SOMATIC)
        
        # Ensure no duplicates with primary
        return [m for m in secondary if m != primary]
    
    def _determine_treatment_intensity(self,
                                     diagnosis: Dict[str, Any],
                                     patient_profile: Dict[str, Any]) -> TreatmentIntensity:
        """Determine appropriate treatment intensity"""
        
        # Check crisis indicators
        risk_factors = diagnosis.get('risk_factors', [])
        if any('suicidal' in str(rf).lower() or 'crisis' in str(rf).lower() for rf in risk_factors):
            return TreatmentIntensity.CRISIS
        
        # Check symptom severity
        severity = patient_profile.get('symptom_severity', 5)
        if severity >= 8:
            return TreatmentIntensity.INTENSIVE
        elif severity >= 6:
            return TreatmentIntensity.WEEKLY_SESSIONS
        elif severity >= 4:
            return TreatmentIntensity.BIWEEKLY_SESSIONS
        else:
            return TreatmentIntensity.SELF_GUIDED
    
    def _generate_activity_plan(self,
                               primary: TreatmentType,
                               secondary: List[TreatmentType],
                               intensity: TreatmentIntensity,
                               patient_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized activity plan"""
        activities = []
        
        # Get primary modality activities
        primary_activities = self.activity_library.get(primary, [])
        
        # Filter by patient capability
        max_difficulty = patient_profile.get('therapy_experience', 'none')
        difficulty_map = {
            'none': 'easy',
            'some': 'moderate',
            'extensive': 'hard'
        }
        max_diff = difficulty_map.get(max_difficulty, 'moderate')
        
        # Select appropriate activities
        for activity in primary_activities:
            if self._compare_difficulty(activity['difficulty'], max_diff) <= 0:
                activities.append({
                    **activity,
                    'modality': primary.value,
                    'priority': 'high'
                })
        
        # Add secondary modality activities
        for modality in secondary:
            modality_activities = self.activity_library.get(modality, [])
            for activity in modality_activities[:2]:  # Limit to 2 per secondary
                if self._compare_difficulty(activity['difficulty'], max_diff) <= 0:
                    activities.append({
                        **activity,
                        'modality': modality.value,
                        'priority': 'medium'
                    })
        
        # Adjust frequency based on intensity
        if intensity == TreatmentIntensity.SELF_GUIDED:
            # Reduce frequency for self-guided
            for activity in activities:
                if activity['frequency'] == 'daily':
                    activity['frequency'] = '3x/week'
                elif activity['frequency'] == '2x/day':
                    activity['frequency'] = 'daily'
        
        return activities
    
    def _compare_difficulty(self, diff1: str, diff2: str) -> int:
        """Compare difficulty levels"""
        levels = {'easy': 0, 'moderate': 1, 'hard': 2}
        return levels.get(diff1, 1) - levels.get(diff2, 1)
    
    def _generate_treatment_goals(self,
                                diagnosis: Dict[str, Any],
                                patient_profile: Dict[str, Any],
                                duration_weeks: int) -> List[Dict[str, Any]]:
        """Generate SMART treatment goals"""
        goals = []
        
        # Primary symptom reduction goal
        primary_condition = diagnosis.get('primary_diagnosis', 'symptoms')
        goals.append({
            'type': 'symptom_reduction',
            'description': f'Reduce {primary_condition} symptoms by 50%',
            'target_date': (datetime.utcnow() + timedelta(weeks=duration_weeks)).isoformat(),
            'measurement': 'Weekly symptom tracking scores',
            'milestone_1': f'25% reduction by week {duration_weeks//2}',
            'milestone_2': f'40% reduction by week {int(duration_weeks*0.75)}'
        })
        
        # Functional improvement goal
        goals.append({
            'type': 'functional_improvement',
            'description': 'Improve daily functioning and quality of life',
            'target_date': (datetime.utcnow() + timedelta(weeks=duration_weeks)).isoformat(),
            'measurement': 'Functional assessment scores',
            'milestone_1': 'Resume 2 previously avoided activities',
            'milestone_2': 'Maintain consistent daily routine'
        })
        
        # Skill development goal
        goals.append({
            'type': 'skill_development',
            'description': 'Master core therapeutic techniques',
            'target_date': (datetime.utcnow() + timedelta(weeks=duration_weeks//2)).isoformat(),
            'measurement': 'Skill practice logs and self-ratings',
            'milestone_1': 'Complete initial skill training modules',
            'milestone_2': 'Apply skills independently in daily life'
        })
        
        # Relapse prevention goal (if applicable)
        if duration_weeks > 12:
            goals.append({
                'type': 'relapse_prevention',
                'description': 'Develop robust relapse prevention plan',
                'target_date': (datetime.utcnow() + timedelta(weeks=duration_weeks)).isoformat(),
                'measurement': 'Completed prevention plan and practice logs',
                'milestone_1': 'Identify triggers and early warning signs',
                'milestone_2': 'Practice prevention strategies successfully'
            })
        
        return goals
    
    def _create_monitoring_plan(self,
                              diagnosis: Dict[str, Any],
                              intensity: TreatmentIntensity) -> Dict[str, Any]:
        """Create comprehensive monitoring plan"""
        
        # Base monitoring frequency
        frequency_map = {
            TreatmentIntensity.CRISIS: 'daily',
            TreatmentIntensity.INTENSIVE: 'every 3 days',
            TreatmentIntensity.WEEKLY_SESSIONS: 'weekly',
            TreatmentIntensity.BIWEEKLY_SESSIONS: 'biweekly',
            TreatmentIntensity.SELF_GUIDED: 'weekly'
        }
        
        monitoring_plan = {
            'symptom_tracking': {
                'frequency': frequency_map[intensity],
                'methods': ['digital mood diary', 'standardized assessments'],
                'alerts': {
                    'severe_symptoms': 'Immediate notification',
                    'worsening_trend': 'Alert after 3 consecutive increases',
                    'missed_tracking': 'Reminder after 2 missed entries'
                }
            },
            'progress_reviews': {
                'frequency': 'monthly',
                'components': ['symptom scores', 'goal progress', 'activity completion'],
                'adjustment_triggers': ['<25% improvement after 4 weeks', 'patient request']
            },
            'safety_monitoring': {
                'risk_assessment': 'At each contact',
                'crisis_protocol': 'Activated if risk indicators present',
                'emergency_contacts': 'Updated and verified monthly'
            },
            'engagement_tracking': {
                'activity_completion': 'Daily automatic tracking',
                'session_attendance': 'Per session',
                'homework_compliance': 'Weekly review'
            }
        }
        
        return monitoring_plan
    
    def _calculate_plan_confidence(self,
                                 ai_recommendations: Dict[str, Any],
                                 evidence_level: str,
                                 patient_profile: Dict[str, Any]) -> float:
        """Calculate confidence in treatment plan"""
        
        # Start with AI consensus confidence
        base_confidence = ai_recommendations.get('overall_confidence', 0.7)
        
        # Adjust for evidence level
        evidence_multipliers = {
            'high': 1.1,
            'moderate': 1.0,
            'low': 0.9
        }
        base_confidence *= evidence_multipliers.get(evidence_level, 1.0)
        
        # Adjust for patient factors
        if patient_profile.get('previous_therapy_success'):
            base_confidence *= 1.1
        
        if patient_profile.get('motivation_level', 5) > 7:
            base_confidence *= 1.05
        
        # Cap confidence
        return min(base_confidence, 0.95)
    
    def adapt_treatment_plan(self,
                           current_plan: TreatmentPlan,
                           progress_data: Dict[str, Any],
                           patient_feedback: Dict[str, Any]) -> TreatmentPlan:
        """Adapt treatment plan based on progress and feedback"""
        
        # Analyze progress
        improvement_rate = progress_data.get('symptom_improvement', 0)
        engagement_rate = progress_data.get('activity_completion_rate', 0)
        
        # Create modified plan
        new_plan = current_plan
        
        # Adjust intensity if needed
        if improvement_rate < 0.25 and current_plan.duration_weeks > 4:
            # Not improving enough - increase intensity
            if current_plan.intensity == TreatmentIntensity.SELF_GUIDED:
                new_plan.intensity = TreatmentIntensity.BIWEEKLY_SESSIONS
            elif current_plan.intensity == TreatmentIntensity.BIWEEKLY_SESSIONS:
                new_plan.intensity = TreatmentIntensity.WEEKLY_SESSIONS
        
        # Adjust activities based on engagement
        if engagement_rate < 0.5:
            # Low engagement - simplify activities
            new_plan.activities = [a for a in new_plan.activities if a['difficulty'] != 'hard']
            
            # Add more engaging activities
            for activity in new_plan.activities:
                if activity.get('digital_tool'):
                    activity['gamification'] = True
                    activity['reminder_frequency'] = 'daily'
        
        # Update based on patient feedback
        if patient_feedback.get('too_time_consuming'):
            # Reduce activity duration
            for activity in new_plan.activities:
                activity['duration_minutes'] = int(activity['duration_minutes'] * 0.75)
        
        if patient_feedback.get('preferred_activities'):
            # Prioritize preferred activities
            preferred = patient_feedback['preferred_activities']
            for activity in new_plan.activities:
                if activity['name'] in preferred:
                    activity['priority'] = 'high'
        
        return new_plan
    
    def get_crisis_intervention_plan(self, risk_level: str) -> Dict[str, Any]:
        """Get immediate crisis intervention plan"""
        
        crisis_plans = {
            'high': {
                'immediate_actions': [
                    'Contact crisis support immediately',
                    'Ensure safety - remove means',
                    'Do not leave person alone',
                    'Call emergency services if imminent danger'
                ],
                'coping_strategies': [
                    'TIPP technique (Temperature, Intense exercise, Paced breathing, Paired muscle relaxation)',
                    'Distraction with intense sensations',
                    'Contact support person from safety plan'
                ],
                'professional_contact': 'Immediate - within 1 hour',
                'follow_up': 'Daily until crisis resolves'
            },
            'moderate': {
                'immediate_actions': [
                    'Implement safety plan',
                    'Contact therapist within 24 hours',
                    'Increase support check-ins'
                ],
                'coping_strategies': [
                    'Grounding exercises (5-4-3-2-1)',
                    'Safe place visualization',
                    'Call warm line or text crisis line'
                ],
                'professional_contact': 'Within 24 hours',
                'follow_up': 'Every 2-3 days'
            },
            'low': {
                'immediate_actions': [
                    'Review and update safety plan',
                    'Schedule additional session if needed',
                    'Increase self-monitoring'
                ],
                'coping_strategies': [
                    'Regular coping skills practice',
                    'Maintain routine',
                    'Engage support network'
                ],
                'professional_contact': 'Next scheduled session',
                'follow_up': 'Weekly'
            }
        }
        
        return crisis_plans.get(risk_level, crisis_plans['moderate'])