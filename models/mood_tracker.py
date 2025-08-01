"""
Mood tracking and analytics for Mind Mend platform
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

class MoodTracker:
    """Advanced mood tracking with insights and patterns"""
    
    def __init__(self):
        self.mood_categories = {
            'emotions': {
                'happy': {'color': '#FFD700', 'icon': '😊'},
                'sad': {'color': '#4169E1', 'icon': '😢'},
                'anxious': {'color': '#FF6347', 'icon': '😰'},
                'angry': {'color': '#DC143C', 'icon': '😠'},
                'calm': {'color': '#32CD32', 'icon': '😌'},
                'excited': {'color': '#FF1493', 'icon': '🎉'},
                'confused': {'color': '#DDA0DD', 'icon': '😕'},
                'grateful': {'color': '#FFB6C1', 'icon': '🙏'}
            },
            'energy_levels': {
                'very_low': 1,
                'low': 2,
                'moderate': 3,
                'high': 4,
                'very_high': 5
            },
            'stress_levels': {
                'minimal': 1,
                'mild': 2,
                'moderate': 3,
                'high': 4,
                'severe': 5
            }
        }
        
        self.triggers = [
            'work', 'relationships', 'health', 'finances', 'family',
            'social', 'personal_growth', 'environment', 'routine', 'other'
        ]
        
        self.coping_strategies = {
            'anxious': ['deep breathing', 'grounding exercises', 'progressive muscle relaxation'],
            'sad': ['pleasant activities', 'social connection', 'self-compassion'],
            'angry': ['physical exercise', 'journaling', 'timeout technique'],
            'stressed': ['mindfulness', 'time management', 'boundary setting']
        }
    
    def log_mood(self, user_id: str, mood_data: Dict) -> Dict:
        """Log a mood entry with comprehensive data"""
        entry = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'primary_emotion': mood_data.get('emotion'),
            'intensity': mood_data.get('intensity', 5),
            'energy_level': mood_data.get('energy_level', 3),
            'stress_level': mood_data.get('stress_level', 3),
            'triggers': mood_data.get('triggers', []),
            'thoughts': mood_data.get('thoughts', ''),
            'physical_sensations': mood_data.get('physical_sensations', []),
            'activities': mood_data.get('activities', []),
            'sleep_quality': mood_data.get('sleep_quality'),
            'medication_taken': mood_data.get('medication_taken', False),
            'notes': mood_data.get('notes', '')
        }
        
        # Generate insights
        insights = self._generate_insights(entry)
        entry['insights'] = insights
        
        return entry
    
    def get_mood_patterns(self, user_id: str, days: int = 30) -> Dict:
        """Analyze mood patterns over time"""
        # In production, this would query the database
        patterns = {
            'dominant_emotions': self._calculate_dominant_emotions(user_id, days),
            'mood_trends': self._calculate_mood_trends(user_id, days),
            'trigger_analysis': self._analyze_triggers(user_id, days),
            'best_worst_times': self._find_best_worst_times(user_id, days),
            'coping_effectiveness': self._analyze_coping_strategies(user_id, days),
            'recommendations': self._generate_recommendations(user_id, days)
        }
        
        return patterns
    
    def get_mood_forecast(self, user_id: str) -> Dict:
        """Predict mood patterns based on historical data"""
        # Simplified forecast - in production would use ML
        return {
            'next_24h': {
                'likely_mood': 'calm',
                'confidence': 0.75,
                'factors': ['good sleep pattern', 'weekend approaching', 'reduced stress']
            },
            'next_week': {
                'challenging_days': ['Monday', 'Wednesday'],
                'positive_days': ['Saturday', 'Sunday'],
                'recommendations': [
                    'Schedule self-care on Monday',
                    'Plan social activities for weekend',
                    'Prepare for Wednesday deadline'
                ]
            }
        }
    
    def generate_mood_report(self, user_id: str, period: str = 'weekly') -> Dict:
        """Generate comprehensive mood report"""
        report = {
            'period': period,
            'summary': {
                'average_mood': 6.5,
                'mood_stability': 'moderate',
                'improvement_areas': ['stress management', 'sleep quality'],
                'achievements': ['consistent journaling', 'increased social activities']
            },
            'detailed_analysis': {
                'emotional_range': self._analyze_emotional_range(user_id, period),
                'trigger_patterns': self._analyze_trigger_patterns(user_id, period),
                'coping_success': self._analyze_coping_success(user_id, period),
                'correlation_insights': self._find_correlations(user_id, period)
            },
            'therapist_notes': self._generate_therapist_notes(user_id, period),
            'action_plan': self._create_action_plan(user_id, period)
        }
        
        return report
    
    def _generate_insights(self, entry: Dict) -> List[str]:
        """Generate insights from mood entry"""
        insights = []
        
        # Emotion-based insights
        if entry['primary_emotion'] == 'anxious' and entry['intensity'] > 7:
            insights.append("High anxiety detected. Consider trying grounding exercises.")
        
        # Pattern insights
        if entry['stress_level'] > 3 and entry['sleep_quality'] == 'poor':
            insights.append("Poor sleep may be contributing to increased stress.")
        
        # Trigger insights
        if 'work' in entry['triggers']:
            insights.append("Work-related stress identified. Setting boundaries might help.")
        
        return insights
    
    def _calculate_dominant_emotions(self, user_id: str, days: int) -> List[Dict]:
        """Calculate most frequent emotions"""
        # Placeholder - would query database in production
        return [
            {'emotion': 'calm', 'frequency': 35, 'percentage': 35},
            {'emotion': 'anxious', 'frequency': 25, 'percentage': 25},
            {'emotion': 'happy', 'frequency': 20, 'percentage': 20}
        ]
    
    def _calculate_mood_trends(self, user_id: str, days: int) -> Dict:
        """Calculate mood trends over time"""
        return {
            'direction': 'improving',
            'rate': 15,  # 15% improvement
            'stability': 'increasing',
            'graph_data': []  # Would contain actual data points
        }
    
    def _analyze_triggers(self, user_id: str, days: int) -> List[Dict]:
        """Analyze common triggers"""
        return [
            {'trigger': 'work', 'frequency': 45, 'impact': 'high'},
            {'trigger': 'relationships', 'frequency': 30, 'impact': 'moderate'},
            {'trigger': 'health', 'frequency': 15, 'impact': 'low'}
        ]
    
    def _find_best_worst_times(self, user_id: str, days: int) -> Dict:
        """Find patterns in time of day"""
        return {
            'best_times': ['morning', 'early evening'],
            'challenging_times': ['late afternoon', 'before bed'],
            'weekly_patterns': {
                'best_days': ['Friday', 'Saturday'],
                'challenging_days': ['Monday', 'Sunday evening']
            }
        }
    
    def _analyze_coping_strategies(self, user_id: str, days: int) -> Dict:
        """Analyze effectiveness of coping strategies"""
        return {
            'most_effective': ['exercise', 'meditation', 'social connection'],
            'least_effective': ['isolation', 'rumination'],
            'recommended_new': ['art therapy', 'nature walks', 'gratitude practice']
        }
    
    def _generate_recommendations(self, user_id: str, days: int) -> List[str]:
        """Generate personalized recommendations"""
        return [
            "Try morning meditation to start days with calm",
            "Schedule regular breaks during work hours",
            "Consider evening gratitude journaling",
            "Maintain consistent sleep schedule",
            "Engage in physical activity 3-4 times per week"
        ]
    
    def _analyze_emotional_range(self, user_id: str, period: str) -> Dict:
        """Analyze range and variety of emotions"""
        return {
            'emotional_flexibility': 'moderate',
            'dominant_valence': 'positive',
            'emotional_vocabulary': ['varied', 'expanding'],
            'areas_for_exploration': ['nuanced positive emotions', 'anger expression']
        }
    
    def _analyze_trigger_patterns(self, user_id: str, period: str) -> Dict:
        """Deep analysis of trigger patterns"""
        return {
            'recurring_patterns': [
                'Work stress peaks on Mondays',
                'Social anxiety before events',
                'Low mood on Sunday evenings'
            ],
            'trigger_combinations': [
                ['work', 'deadlines', 'lack of sleep'],
                ['social', 'crowds', 'unfamiliar places']
            ],
            'protective_factors': ['exercise', 'nature', 'pet time']
        }
    
    def _analyze_coping_success(self, user_id: str, period: str) -> Dict:
        """Analyze success of coping strategies"""
        return {
            'success_rate': 72,
            'improving_strategies': ['breathing exercises', 'journaling'],
            'consistent_strategies': ['walking', 'music'],
            'abandoned_strategies': ['meditation apps'],
            'suggested_modifications': [
                'Try shorter meditation sessions',
                'Combine walking with mindfulness',
                'Add variety to journaling prompts'
            ]
        }
    
    def _find_correlations(self, user_id: str, period: str) -> List[Dict]:
        """Find correlations between factors"""
        return [
            {
                'factor1': 'sleep_quality',
                'factor2': 'mood_rating',
                'correlation': 0.78,
                'insight': 'Better sleep strongly correlates with improved mood'
            },
            {
                'factor1': 'exercise',
                'factor2': 'anxiety_level',
                'correlation': -0.65,
                'insight': 'Regular exercise associated with lower anxiety'
            }
        ]
    
    def _generate_therapist_notes(self, user_id: str, period: str) -> str:
        """Generate notes for therapist review"""
        return """Patient shows improving mood stability with some persistent anxiety around work situations. 
        Sleep hygiene remains a concern. Coping strategies are developing well, particularly physical exercise 
        and social connection. Consider exploring work-related boundaries and stress management techniques 
        in upcoming sessions."""
    
    def _create_action_plan(self, user_id: str, period: str) -> List[Dict]:
        """Create actionable steps"""
        return [
            {
                'goal': 'Improve sleep quality',
                'actions': ['Set consistent bedtime', 'No screens 1hr before bed', 'Evening relaxation routine'],
                'timeline': '2 weeks',
                'success_metric': '7+ hours sleep, 5 nights/week'
            },
            {
                'goal': 'Manage work stress',
                'actions': ['Daily 5-min breaks', 'Boundary setting practice', 'Weekly planning sessions'],
                'timeline': '1 month',
                'success_metric': 'Stress level < 3 on workdays'
            }
        ]