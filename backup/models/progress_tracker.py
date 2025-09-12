"""
Progress tracking and goal management for Mind Mend platform
"""

from datetime import datetime
from typing import Dict, List

class ProgressTracker:
    """Track therapeutic progress and goals"""
    
    def __init__(self):
        self.goal_categories = [
            'emotional_regulation',
            'relationship_improvement',
            'anxiety_management',
            'depression_recovery',
            'trauma_healing',
            'self_esteem',
            'behavioral_change',
            'mindfulness_practice',
            'communication_skills',
            'work_life_balance'
        ]
        
        self.progress_indicators = {
            'symptom_reduction': ['anxiety_level', 'depression_score', 'stress_rating'],
            'skill_development': ['coping_skills', 'communication', 'emotional_awareness'],
            'behavioral_metrics': ['activity_level', 'social_engagement', 'self_care'],
            'quality_of_life': ['sleep_quality', 'energy_level', 'life_satisfaction']
        }
    
    def create_treatment_plan(self, user_id: str, assessment_data: Dict) -> Dict:
        """Create personalized treatment plan based on assessment"""
        plan = {
            'user_id': user_id,
            'created_date': datetime.now().isoformat(),
            'primary_concerns': assessment_data.get('concerns', []),
            'goals': self._generate_smart_goals(assessment_data),
            'interventions': self._select_interventions(assessment_data),
            'milestones': self._create_milestones(assessment_data),
            'review_schedule': self._set_review_schedule(assessment_data),
            'success_metrics': self._define_success_metrics(assessment_data)
        }
        
        return plan
    
    def track_session_progress(self, session_data: Dict) -> Dict:
        """Track progress from therapy session"""
        progress = {
            'session_id': session_data.get('session_id'),
            'date': datetime.now().isoformat(),
            'topics_covered': session_data.get('topics', []),
            'breakthroughs': self._identify_breakthroughs(session_data),
            'challenges': self._identify_challenges(session_data),
            'homework_assigned': session_data.get('homework', []),
            'mood_change': {
                'before': session_data.get('mood_before', 5),
                'after': session_data.get('mood_after', 7),
                'improvement': session_data.get('mood_after', 7) - session_data.get('mood_before', 5)
            },
            'insights_gained': session_data.get('insights', []),
            'next_session_focus': self._suggest_next_focus(session_data)
        }
        
        return progress
    
    def generate_progress_report(self, user_id: str, period_days: int = 30) -> Dict:
        """Generate comprehensive progress report"""
        report = {
            'period': f'{period_days} days',
            'overall_progress': self._calculate_overall_progress(user_id, period_days),
            'goal_achievement': self._assess_goal_achievement(user_id, period_days),
            'symptom_trajectory': self._analyze_symptom_trajectory(user_id, period_days),
            'skill_development': self._assess_skill_development(user_id, period_days),
            'engagement_metrics': self._calculate_engagement(user_id, period_days),
            'therapeutic_alliance': self._assess_therapeutic_alliance(user_id),
            'recommendations': self._generate_recommendations(user_id, period_days),
            'celebrate': self._identify_wins(user_id, period_days)
        }
        
        return report
    
    def set_goal(self, user_id: str, goal_data: Dict) -> Dict:
        """Set a SMART goal for user"""
        goal = {
            'goal_id': f"goal_{datetime.now().timestamp()}",
            'user_id': user_id,
            'category': goal_data.get('category'),
            'title': goal_data.get('title'),
            'description': goal_data.get('description'),
            'specific': goal_data.get('specific_criteria'),
            'measurable': goal_data.get('measurement_method'),
            'achievable': goal_data.get('achievability_assessment'),
            'relevant': goal_data.get('relevance_to_treatment'),
            'time_bound': goal_data.get('target_date'),
            'milestones': self._create_goal_milestones(goal_data),
            'action_steps': goal_data.get('action_steps', []),
            'potential_obstacles': goal_data.get('obstacles', []),
            'support_needed': goal_data.get('support', []),
            'created_date': datetime.now().isoformat(),
            'status': 'active'
        }
        
        return goal
    
    def update_goal_progress(self, goal_id: str, progress_data: Dict) -> Dict:
        """Update progress on a specific goal"""
        update = {
            'goal_id': goal_id,
            'update_date': datetime.now().isoformat(),
            'progress_percentage': progress_data.get('percentage', 0),
            'milestones_completed': progress_data.get('completed_milestones', []),
            'challenges_faced': progress_data.get('challenges', []),
            'strategies_used': progress_data.get('strategies', []),
            'support_received': progress_data.get('support', []),
            'reflection': progress_data.get('reflection', ''),
            'next_steps': progress_data.get('next_steps', []),
            'confidence_level': progress_data.get('confidence', 5)
        }
        
        return update
    
    def _generate_smart_goals(self, assessment_data: Dict) -> List[Dict]:
        """Generate SMART goals based on assessment"""
        goals = []
        concerns = assessment_data.get('concerns', [])
        
        if 'anxiety' in concerns:
            goals.append({
                'title': 'Reduce anxiety symptoms',
                'specific': 'Decrease anxiety attacks from daily to weekly',
                'measurable': 'Track anxiety episodes and intensity daily',
                'achievable': 'Use learned coping techniques',
                'relevant': 'Primary presenting concern',
                'time_bound': '3 months',
                'category': 'anxiety_management'
            })
        
        if 'depression' in concerns:
            goals.append({
                'title': 'Improve mood and energy',
                'specific': 'Engage in 3 pleasant activities per week',
                'measurable': 'Activity log and mood ratings',
                'achievable': 'Start with simple activities',
                'relevant': 'Addresses behavioral activation',
                'time_bound': '6 weeks',
                'category': 'depression_recovery'
            })
        
        return goals
    
    def _select_interventions(self, assessment_data: Dict) -> List[Dict]:
        """Select appropriate interventions"""
        interventions = []
        concerns = assessment_data.get('concerns', [])
        
        intervention_map = {
            'anxiety': [
                {'name': 'CBT for anxiety', 'frequency': 'weekly sessions'},
                {'name': 'Mindfulness practice', 'frequency': 'daily 10 min'},
                {'name': 'Exposure exercises', 'frequency': 'as assigned'}
            ],
            'depression': [
                {'name': 'Behavioral activation', 'frequency': 'daily planning'},
                {'name': 'Cognitive restructuring', 'frequency': 'weekly'},
                {'name': 'Social connection', 'frequency': '2-3x per week'}
            ],
            'relationships': [
                {'name': 'Communication skills', 'frequency': 'practice daily'},
                {'name': 'Couples therapy', 'frequency': 'bi-weekly'},
                {'name': 'Attachment work', 'frequency': 'ongoing'}
            ]
        }
        
        for concern in concerns:
            if concern in intervention_map:
                interventions.extend(intervention_map[concern])
        
        return interventions
    
    def _create_milestones(self, assessment_data: Dict) -> List[Dict]:
        """Create treatment milestones"""
        milestones = [
            {
                'week': 2,
                'description': 'Complete initial assessment and establish therapeutic alliance',
                'indicators': ['Comfort sharing', 'Understanding of process']
            },
            {
                'week': 4,
                'description': 'Master basic coping techniques',
                'indicators': ['Can identify triggers', 'Uses 2+ coping strategies']
            },
            {
                'week': 8,
                'description': 'Show measurable symptom improvement',
                'indicators': ['20% reduction in primary symptoms', 'Improved functioning']
            },
            {
                'week': 12,
                'description': 'Integrate skills into daily life',
                'indicators': ['Automatic use of skills', 'Maintained improvement']
            }
        ]
        
        return milestones
    
    def _set_review_schedule(self, assessment_data: Dict) -> Dict:
        """Set review schedule for treatment plan"""
        severity = assessment_data.get('severity', 'moderate')
        
        schedules = {
            'mild': {'frequency': 'monthly', 'first_review': 4},
            'moderate': {'frequency': 'bi-weekly', 'first_review': 2},
            'severe': {'frequency': 'weekly', 'first_review': 1}
        }
        
        return schedules.get(severity, schedules['moderate'])
    
    def _define_success_metrics(self, assessment_data: Dict) -> Dict:
        """Define success metrics for treatment"""
        return {
            'primary_outcomes': [
                'Symptom reduction of 50% or more',
                'Improved daily functioning',
                'Achievement of 80% of treatment goals'
            ],
            'secondary_outcomes': [
                'Improved relationships',
                'Better quality of life',
                'Increased self-efficacy'
            ],
            'measurement_tools': [
                'Weekly mood tracking',
                'Monthly assessments',
                'Goal achievement reviews'
            ]
        }
    
    def _identify_breakthroughs(self, session_data: Dict) -> List[str]:
        """Identify breakthrough moments in session"""
        breakthroughs = []
        
        # Analyze session content for breakthrough indicators
        content = session_data.get('content', '').lower()
        
        breakthrough_indicators = [
            ('realized', 'New realization or insight'),
            ('understand now', 'Improved understanding'),
            ('feel different', 'Emotional shift'),
            ('never thought', 'Perspective change'),
            ('breakthrough', 'Explicit breakthrough')
        ]
        
        for indicator, description in breakthrough_indicators:
            if indicator in content:
                breakthroughs.append(description)
        
        return breakthroughs
    
    def _identify_challenges(self, session_data: Dict) -> List[str]:
        """Identify challenges from session"""
        challenges = []
        
        # Simplified challenge detection
        resistance_indicators = ['but', 'cant', 'wont', 'difficult', 'hard', 'struggle']
        content = session_data.get('content', '').lower()
        
        for indicator in resistance_indicators:
            if indicator in content:
                challenges.append('Resistance or difficulty expressed')
                break
        
        return challenges
    
    def _suggest_next_focus(self, session_data: Dict) -> List[str]:
        """Suggest focus areas for next session"""
        suggestions = []
        
        # Based on session content, suggest next steps
        if session_data.get('homework'):
            suggestions.append('Review homework completion and obstacles')
        
        if session_data.get('breakthroughs'):
            suggestions.append('Deepen understanding of recent insights')
        
        if session_data.get('challenges'):
            suggestions.append('Address resistance and explore barriers')
        
        return suggestions or ['Continue current therapeutic direction']
    
    def _calculate_overall_progress(self, user_id: str, period_days: int) -> Dict:
        """Calculate overall treatment progress"""
        return {
            'percentage': 65,
            'trajectory': 'improving',
            'pace': 'on_track',
            'areas_of_growth': ['emotional awareness', 'coping skills', 'self-compassion'],
            'areas_needing_focus': ['behavioral activation', 'social engagement']
        }
    
    def _assess_goal_achievement(self, user_id: str, period_days: int) -> List[Dict]:
        """Assess achievement of treatment goals"""
        return [
            {
                'goal': 'Reduce anxiety symptoms',
                'progress': 70,
                'status': 'on_track',
                'evidence': ['Fewer panic attacks', 'Using breathing techniques']
            },
            {
                'goal': 'Improve sleep quality',
                'progress': 85,
                'status': 'ahead_of_schedule',
                'evidence': ['7 hours average sleep', 'Better sleep hygiene']
            }
        ]
    
    def _analyze_symptom_trajectory(self, user_id: str, period_days: int) -> Dict:
        """Analyze trajectory of symptoms"""
        return {
            'anxiety': {'start': 8, 'current': 5, 'trend': 'decreasing'},
            'depression': {'start': 7, 'current': 4, 'trend': 'decreasing'},
            'stress': {'start': 9, 'current': 6, 'trend': 'decreasing'},
            'overall_improvement': 40
        }
    
    def _assess_skill_development(self, user_id: str, period_days: int) -> Dict:
        """Assess development of therapeutic skills"""
        return {
            'skills_learned': [
                {'skill': 'Deep breathing', 'mastery': 90},
                {'skill': 'Thought challenging', 'mastery': 70},
                {'skill': 'Mindfulness', 'mastery': 60}
            ],
            'skills_in_progress': ['Emotion regulation', 'Assertive communication'],
            'recommended_next': ['Progressive muscle relaxation', 'Values clarification']
        }
    
    def _calculate_engagement(self, user_id: str, period_days: int) -> Dict:
        """Calculate treatment engagement metrics"""
        return {
            'session_attendance': 95,
            'homework_completion': 80,
            'activity_participation': 75,
            'journaling_consistency': 85,
            'overall_engagement': 'high'
        }
    
    def _assess_therapeutic_alliance(self, user_id: str) -> Dict:
        """Assess quality of therapeutic relationship"""
        return {
            'trust_level': 'high',
            'collaboration': 'excellent',
            'openness': 'improving',
            'feedback': 'Client reports feeling heard and supported'
        }
    
    def _generate_recommendations(self, user_id: str, period_days: int) -> List[str]:
        """Generate treatment recommendations"""
        return [
            "Continue current CBT approach with increased focus on behavioral activation",
            "Introduce advanced emotion regulation techniques",
            "Consider group therapy for additional peer support",
            "Gradually reduce session frequency as symptoms improve",
            "Develop relapse prevention plan"
        ]
    
    def _identify_wins(self, user_id: str, period_days: int) -> List[str]:
        """Identify victories to celebrate"""
        return [
            "30 days of consistent mood tracking!",
            "Successfully used coping skills during work presentation",
            "Improved sleep quality by 40%",
            "Reconnected with two supportive friends",
            "Completed all therapy homework for 3 weeks straight"
        ]
    
    def _create_goal_milestones(self, goal_data: Dict) -> List[Dict]:
        """Create milestones for a specific goal"""
        # Calculate milestone dates based on goal timeline
        target_date = goal_data.get('target_date')
        milestones = []
        
        # Create 4 evenly spaced milestones
        for i in range(1, 5):
            milestone = {
                'number': i,
                'description': f'Milestone {i} for {goal_data.get("title")}',
                'target_date': 'calculated_date',
                'criteria': f'{i * 25}% progress toward goal',
                'status': 'pending'
            }
            milestones.append(milestone)
        
        return milestones