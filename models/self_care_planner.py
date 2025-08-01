"""
Self-care planning and wellness routines for Mind Mend platform
"""

from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
import random

class SelfCarePlanner:
    """Personalized self-care and wellness planning"""
    
    def __init__(self):
        self.self_care_categories = {
            'physical': {
                'activities': [
                    'Take a walk in nature',
                    'Do gentle stretching',
                    'Practice yoga',
                    'Dance to favorite music',
                    'Take a relaxing bath',
                    'Get a massage',
                    'Exercise for 30 minutes',
                    'Prepare a healthy meal'
                ],
                'benefits': ['Reduces tension', 'Improves energy', 'Enhances mood']
            },
            'emotional': {
                'activities': [
                    'Journal about feelings',
                    'Practice self-compassion',
                    'Call a supportive friend',
                    'Watch a comfort movie',
                    'Create art or crafts',
                    'Listen to uplifting music',
                    'Practice gratitude',
                    'Cry if needed'
                ],
                'benefits': ['Processes emotions', 'Builds resilience', 'Improves mood']
            },
            'mental': {
                'activities': [
                    'Read a book',
                    'Do a puzzle',
                    'Learn something new',
                    'Limit social media',
                    'Practice mindfulness',
                    'Organize your space',
                    'Set boundaries',
                    'Take breaks from work'
                ],
                'benefits': ['Reduces stress', 'Improves focus', 'Enhances clarity']
            },
            'social': {
                'activities': [
                    'Connect with loved ones',
                    'Join a support group',
                    'Volunteer for a cause',
                    'Plan a social activity',
                    'Express appreciation',
                    'Ask for help when needed',
                    'Set social boundaries',
                    'Practice active listening'
                ],
                'benefits': ['Reduces isolation', 'Builds support', 'Improves relationships']
            },
            'spiritual': {
                'activities': [
                    'Practice meditation',
                    'Spend time in nature',
                    'Practice prayer or reflection',
                    'Read inspirational texts',
                    'Practice forgiveness',
                    'Connect with values',
                    'Practice acceptance',
                    'Engage in ritual or ceremony'
                ],
                'benefits': ['Increases meaning', 'Provides peace', 'Enhances connection']
            }
        }
        
        self.wellness_dimensions = [
            'sleep_hygiene',
            'nutrition',
            'movement',
            'stress_management',
            'social_connection',
            'purpose_meaning',
            'creativity',
            'environment'
        ]
        
        self.routine_templates = {
            'morning': {
                'energizing': ['stretching', 'meditation', 'healthy breakfast', 'gratitude'],
                'calming': ['gentle wake-up', 'tea ritual', 'journaling', 'slow movement'],
                'productive': ['exercise', 'planning', 'affirmations', 'cold shower']
            },
            'evening': {
                'relaxing': ['warm bath', 'reading', 'gentle music', 'tea'],
                'reflective': ['journaling', 'gratitude', 'meditation', 'planning tomorrow'],
                'social': ['family time', 'phone friend', 'game night', 'shared meal']
            },
            'crisis': {
                'immediate': ['breathing', 'grounding', 'safe space', 'support person'],
                'short_term': ['gentle movement', 'comfort items', 'simple tasks', 'rest'],
                'recovery': ['routine', 'nutrition', 'sleep', 'professional help']
            }
        }
    
    def create_personalized_plan(self, user_data: Dict) -> Dict:
        """Create personalized self-care plan based on user needs"""
        plan = {
            'user_id': user_data.get('user_id'),
            'created_date': datetime.now().isoformat(),
            'primary_focus': self._determine_focus_areas(user_data),
            'daily_practices': self._select_daily_practices(user_data),
            'weekly_activities': self._plan_weekly_activities(user_data),
            'crisis_plan': self._create_crisis_plan(user_data),
            'accountability': self._set_accountability_measures(user_data),
            'resources': self._gather_resources(user_data)
        }
        
        return plan
    
    def generate_daily_routine(self, preferences: Dict) -> Dict:
        """Generate daily self-care routine"""
        routine = {
            'morning': self._create_morning_routine(preferences),
            'midday': self._create_midday_routine(preferences),
            'evening': self._create_evening_routine(preferences),
            'as_needed': self._create_as_needed_activities(preferences),
            'reminders': self._set_routine_reminders(preferences)
        }
        
        return routine
    
    def suggest_self_care_activity(self, current_state: Dict) -> Dict:
        """Suggest immediate self-care activity based on current state"""
        mood = current_state.get('mood', 'neutral')
        energy = current_state.get('energy_level', 'medium')
        time_available = current_state.get('time_minutes', 15)
        
        # Select appropriate activity based on state
        if mood == 'anxious':
            category = 'physical' if energy == 'high' else 'mental'
        elif mood == 'sad':
            category = 'emotional' if energy == 'low' else 'social'
        elif mood == 'stressed':
            category = 'mental' if time_available < 20 else 'physical'
        else:
            category = random.choice(list(self.self_care_categories.keys()))
        
        activities = self.self_care_categories[category]['activities']
        
        # Filter by time
        if time_available < 10:
            quick_activities = [a for a in activities if 'practice' in a.lower() or 'take' in a.lower()]
            activity = random.choice(quick_activities) if quick_activities else activities[0]
        else:
            activity = random.choice(activities)
        
        return {
            'activity': activity,
            'category': category,
            'estimated_time': self._estimate_activity_time(activity),
            'benefits': self.self_care_categories[category]['benefits'],
            'instructions': self._get_activity_instructions(activity),
            'alternatives': self._get_alternative_activities(category, activity)
        }
    
    def create_wellness_challenge(self, duration_days: int = 30) -> Dict:
        """Create a wellness challenge"""
        challenge = {
            'name': f'{duration_days}-Day Wellness Journey',
            'duration': duration_days,
            'daily_challenges': [],
            'weekly_themes': [],
            'rewards': self._set_challenge_rewards(duration_days),
            'tracking_method': 'daily check-ins',
            'community_aspect': 'share progress in group'
        }
        
        # Create daily challenges
        for day in range(1, duration_days + 1):
            daily_challenge = {
                'day': day,
                'primary': self._select_challenge_activity(day),
                'bonus': self._select_bonus_activity(day),
                'reflection_prompt': self._get_reflection_prompt(day)
            }
            challenge['daily_challenges'].append(daily_challenge)
        
        # Set weekly themes
        weeks = (duration_days + 6) // 7
        themes = ['Foundation', 'Growth', 'Integration', 'Mastery']
        for week in range(weeks):
            challenge['weekly_themes'].append({
                'week': week + 1,
                'theme': themes[week % len(themes)],
                'focus': self._get_weekly_focus(week)
            })
        
        return challenge
    
    def track_self_care(self, user_id: str, activity_data: Dict) -> Dict:
        """Track self-care activity completion"""
        tracking = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'activity': activity_data.get('activity'),
            'category': activity_data.get('category'),
            'duration_minutes': activity_data.get('duration'),
            'mood_before': activity_data.get('mood_before'),
            'mood_after': activity_data.get('mood_after'),
            'effectiveness': activity_data.get('effectiveness', 5),
            'would_repeat': activity_data.get('would_repeat', True),
            'notes': activity_data.get('notes', ''),
            'barriers': activity_data.get('barriers', []),
            'streak_count': self._calculate_streak(user_id)
        }
        
        # Generate insights
        tracking['insights'] = self._generate_tracking_insights(tracking)
        
        return tracking
    
    def get_self_care_stats(self, user_id: str, period_days: int = 30) -> Dict:
        """Get self-care statistics and insights"""
        stats = {
            'period': f'{period_days} days',
            'total_activities': 45,  # Placeholder
            'consistency_rate': 75,  # Placeholder
            'favorite_categories': self._get_favorite_categories(user_id),
            'most_effective': self._get_most_effective_activities(user_id),
            'streak_data': self._get_streak_data(user_id),
            'mood_impact': self._analyze_mood_impact(user_id),
            'barriers_identified': self._get_common_barriers(user_id),
            'recommendations': self._generate_recommendations(user_id),
            'achievements': self._get_achievements(user_id)
        }
        
        return stats
    
    def _determine_focus_areas(self, user_data: Dict) -> List[str]:
        """Determine primary self-care focus areas"""
        concerns = user_data.get('concerns', [])
        focus_areas = []
        
        concern_to_focus = {
            'anxiety': ['stress_management', 'physical', 'mental'],
            'depression': ['movement', 'social_connection', 'purpose_meaning'],
            'stress': ['stress_management', 'physical', 'spiritual'],
            'relationships': ['social_connection', 'emotional', 'communication'],
            'trauma': ['spiritual', 'emotional', 'physical']
        }
        
        for concern in concerns:
            if concern in concern_to_focus:
                focus_areas.extend(concern_to_focus[concern])
        
        return list(set(focus_areas))[:3]  # Top 3 unique areas
    
    def _select_daily_practices(self, user_data: Dict) -> List[Dict]:
        """Select daily self-care practices"""
        practices = []
        time_available = user_data.get('daily_time_minutes', 30)
        
        # Morning practice (5-10 min)
        practices.append({
            'time': 'morning',
            'activity': 'mindful breathing or gratitude',
            'duration': 5,
            'purpose': 'start day centered'
        })
        
        # Midday practice (5-10 min)
        if time_available >= 20:
            practices.append({
                'time': 'midday',
                'activity': 'movement break or walk',
                'duration': 10,
                'purpose': 'reset energy'
            })
        
        # Evening practice (10-15 min)
        practices.append({
            'time': 'evening',
            'activity': 'journaling or relaxation',
            'duration': 10,
            'purpose': 'process day and unwind'
        })
        
        return practices
    
    def _plan_weekly_activities(self, user_data: Dict) -> List[Dict]:
        """Plan weekly self-care activities"""
        activities = []
        preferences = user_data.get('preferences', {})
        
        # Add variety throughout the week
        weekly_template = [
            {'day': 'Monday', 'focus': 'physical', 'activity': 'exercise or yoga'},
            {'day': 'Tuesday', 'focus': 'mental', 'activity': 'learning or organizing'},
            {'day': 'Wednesday', 'focus': 'social', 'activity': 'connect with friend'},
            {'day': 'Thursday', 'focus': 'creative', 'activity': 'art or music'},
            {'day': 'Friday', 'focus': 'emotional', 'activity': 'therapy or journaling'},
            {'day': 'Saturday', 'focus': 'spiritual', 'activity': 'nature or meditation'},
            {'day': 'Sunday', 'focus': 'rest', 'activity': 'whatever feels good'}
        ]
        
        for day_plan in weekly_template:
            if day_plan['focus'] in preferences.get('preferred_categories', []):
                activities.append(day_plan)
        
        return activities
    
    def _create_crisis_plan(self, user_data: Dict) -> Dict:
        """Create crisis self-care plan"""
        return {
            'warning_signs': [
                'Feeling overwhelmed',
                'Isolation urges',
                'Sleep disruption',
                'Appetite changes'
            ],
            'immediate_actions': [
                'Use TIPP technique',
                'Call support person',
                'Go to safe space',
                'Use crisis hotline if needed'
            ],
            'comfort_kit': [
                'Soft blanket',
                'Calming music playlist',
                'Photos of loved ones',
                'Favorite tea',
                'Stress ball',
                'Essential oils'
            ],
            'support_contacts': [
                'Therapist',
                'Trusted friend',
                'Family member',
                'Crisis hotline: 988'
            ],
            'recovery_plan': [
                'Gentle routine',
                'Basic self-care',
                'Professional support',
                'Gradual re-engagement'
            ]
        }
    
    def _set_accountability_measures(self, user_data: Dict) -> Dict:
        """Set accountability measures for self-care"""
        return {
            'tracking_method': user_data.get('preferred_tracking', 'app reminders'),
            'check_in_frequency': 'daily',
            'accountability_partner': user_data.get('partner_name'),
            'rewards_system': {
                '7_days': 'Favorite treat',
                '14_days': 'New self-care item',
                '30_days': 'Special celebration'
            },
            'gentle_reminders': True,
            'progress_sharing': user_data.get('share_progress', False)
        }
    
    def _gather_resources(self, user_data: Dict) -> Dict:
        """Gather relevant self-care resources"""
        return {
            'apps': [
                'Insight Timer (meditation)',
                'Calm (sleep stories)',
                'Headspace (mindfulness)'
            ],
            'books': [
                'The Self-Compassion Workbook',
                'The Body Keeps the Score',
                'Radical Acceptance'
            ],
            'websites': [
                'mindmend.com.au/resources',
                'self-compassion.org',
                'mindful.org'
            ],
            'local_resources': [
                'Community wellness center',
                'Parks and nature trails',
                'Support groups'
            ],
            'emergency_resources': [
                'Crisis hotline: 988',
                'Text HOME to 741741',
                'Emergency: 911'
            ]
        }
    
    def _create_morning_routine(self, preferences: Dict) -> List[Dict]:
        """Create morning self-care routine"""
        routine_type = preferences.get('morning_type', 'calming')
        routines = self.routine_templates['morning'].get(routine_type, [])
        
        return [{'time': '7:00 AM', 'activity': activity, 'duration': 10} for activity in routines]
    
    def _create_midday_routine(self, preferences: Dict) -> List[Dict]:
        """Create midday self-care routine"""
        return [
            {'time': '12:00 PM', 'activity': 'mindful lunch', 'duration': 30},
            {'time': '2:00 PM', 'activity': 'stretch break', 'duration': 5}
        ]
    
    def _create_evening_routine(self, preferences: Dict) -> List[Dict]:
        """Create evening self-care routine"""
        routine_type = preferences.get('evening_type', 'relaxing')
        routines = self.routine_templates['evening'].get(routine_type, [])
        
        return [{'time': '8:00 PM', 'activity': activity, 'duration': 15} for activity in routines]
    
    def _create_as_needed_activities(self, preferences: Dict) -> List[Dict]:
        """Create as-needed self-care activities"""
        return [
            {'trigger': 'feeling stressed', 'activity': 'breathing exercise', 'duration': 5},
            {'trigger': 'feeling sad', 'activity': 'call a friend', 'duration': 20},
            {'trigger': 'feeling anxious', 'activity': 'grounding exercise', 'duration': 10}
        ]
    
    def _set_routine_reminders(self, preferences: Dict) -> List[Dict]:
        """Set reminders for routine"""
        return [
            {'time': '7:00 AM', 'message': 'Good morning! Time for your morning routine'},
            {'time': '12:00 PM', 'message': 'Take a mindful lunch break'},
            {'time': '8:00 PM', 'message': 'Evening wind-down time'}
        ]
    
    def _estimate_activity_time(self, activity: str) -> int:
        """Estimate time for activity"""
        quick = ['breathing', 'stretch', 'gratitude', 'affirmation']
        medium = ['walk', 'journal', 'meditation', 'call']
        long = ['exercise', 'bath', 'yoga', 'nature']
        
        activity_lower = activity.lower()
        if any(q in activity_lower for q in quick):
            return 5
        elif any(m in activity_lower for m in medium):
            return 15
        elif any(l in activity_lower for l in long):
            return 30
        return 15
    
    def _get_activity_instructions(self, activity: str) -> str:
        """Get instructions for activity"""
        instructions = {
            'breathing': 'Find comfortable position. Breathe in for 4, hold for 4, out for 6.',
            'meditation': 'Sit comfortably, close eyes, focus on breath or use guided app.',
            'journal': 'Write freely about thoughts and feelings without judgment.',
            'walk': 'Walk at comfortable pace, notice surroundings mindfully.',
            'gratitude': 'List 3 things you appreciate, be specific.'
        }
        
        for key, instruction in instructions.items():
            if key in activity.lower():
                return instruction
        
        return 'Take your time and be present with this activity.'
    
    def _get_alternative_activities(self, category: str, current: str) -> List[str]:
        """Get alternative activities"""
        all_activities = self.self_care_categories.get(category, {}).get('activities', [])
        return [a for a in all_activities if a != current][:3]
    
    def _set_challenge_rewards(self, duration: int) -> List[Dict]:
        """Set challenge rewards"""
        rewards = []
        milestones = [7, 14, 21, 30]
        
        for milestone in milestones:
            if milestone <= duration:
                rewards.append({
                    'day': milestone,
                    'reward': f'{milestone}-day achievement badge',
                    'bonus': 'Special self-care activity unlock'
                })
        
        return rewards
    
    def _select_challenge_activity(self, day: int) -> str:
        """Select daily challenge activity"""
        categories = list(self.self_care_categories.keys())
        category = categories[day % len(categories)]
        activities = self.self_care_categories[category]['activities']
        return random.choice(activities)
    
    def _select_bonus_activity(self, day: int) -> str:
        """Select bonus activity"""
        bonus_activities = [
            'Try something new',
            'Double your usual practice',
            'Share with a friend',
            'Create your own activity'
        ]
        return bonus_activities[day % len(bonus_activities)]
    
    def _get_reflection_prompt(self, day: int) -> str:
        """Get daily reflection prompt"""
        prompts = [
            'What did you notice about yourself today?',
            'How did self-care impact your mood?',
            'What was most challenging and why?',
            'What brought you joy today?',
            'How can you build on today\'s success?'
        ]
        return prompts[day % len(prompts)]
    
    def _get_weekly_focus(self, week: int) -> str:
        """Get weekly focus area"""
        focuses = ['Building habits', 'Deepening practice', 'Overcoming barriers', 'Integration']
        return focuses[week % len(focuses)]
    
    def _calculate_streak(self, user_id: str) -> int:
        """Calculate self-care streak"""
        # Placeholder - would check database in production
        return random.randint(1, 30)
    
    def _generate_tracking_insights(self, tracking: Dict) -> List[str]:
        """Generate insights from tracking"""
        insights = []
        
        if tracking['mood_after'] > tracking['mood_before']:
            insights.append('This activity improved your mood!')
        
        if tracking['effectiveness'] >= 8:
            insights.append('Highly effective - consider making this a regular practice.')
        
        if tracking['streak_count'] > 7:
            insights.append(f'Amazing {tracking["streak_count"]}-day streak!')
        
        return insights
    
    def _get_favorite_categories(self, user_id: str) -> List[str]:
        """Get user's favorite categories"""
        # Placeholder - would analyze user data
        return ['physical', 'emotional', 'mental']
    
    def _get_most_effective_activities(self, user_id: str) -> List[Dict]:
        """Get most effective activities"""
        return [
            {'activity': 'Morning meditation', 'effectiveness': 9.2},
            {'activity': 'Evening walk', 'effectiveness': 8.5},
            {'activity': 'Gratitude journal', 'effectiveness': 8.0}
        ]
    
    def _get_streak_data(self, user_id: str) -> Dict:
        """Get streak data"""
        return {
            'current_streak': 12,
            'longest_streak': 28,
            'total_days': 95,
            'consistency_rate': 82
        }
    
    def _analyze_mood_impact(self, user_id: str) -> Dict:
        """Analyze mood impact of self-care"""
        return {
            'average_mood_lift': 2.3,
            'most_impactful_category': 'physical',
            'correlation_strength': 0.72
        }
    
    def _get_common_barriers(self, user_id: str) -> List[str]:
        """Get common barriers to self-care"""
        return ['lack of time', 'low energy', 'forgetting', 'feeling undeserving']
    
    def _generate_recommendations(self, user_id: str) -> List[str]:
        """Generate self-care recommendations"""
        return [
            'Try morning routine for consistency',
            'Add more social activities',
            'Experiment with creative self-care',
            'Set gentle reminders'
        ]
    
    def _get_achievements(self, user_id: str) -> List[Dict]:
        """Get self-care achievements"""
        return [
            {'name': 'Week Warrior', 'description': '7-day streak', 'date': 'Last week'},
            {'name': 'Variety Victor', 'description': 'Tried all categories', 'date': '2 weeks ago'},
            {'name': 'Mood Master', 'description': 'Consistent mood improvement', 'date': 'This month'}
        ]