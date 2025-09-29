"""
Comprehensive therapy activities and exercises for Mind Mend platform
"""

import random
from typing import Dict, List

class TherapyActivities:
    """Enhanced therapy activities generator with diverse exercises"""
    
    def __init__(self):
        self.activities = {
            'mindfulness': [
                {
                    'name': 'Body Scan Meditation',
                    'duration': '15-20 minutes',
                    'description': 'Systematically focus on different parts of your body, noticing sensations without judgment.',
                    'instructions': [
                        'Find a comfortable position lying down or sitting',
                        'Close your eyes and take three deep breaths',
                        'Start with your toes, noticing any sensations',
                        'Slowly move your attention up through your body',
                        'Acknowledge any tension and consciously relax',
                        'End with awareness of your whole body'
                    ],
                    'benefits': ['Reduces stress', 'Improves body awareness', 'Promotes relaxation']
                },
                {
                    'name': '5-4-3-2-1 Grounding Exercise',
                    'duration': '5 minutes',
                    'description': 'Use your senses to ground yourself in the present moment.',
                    'instructions': [
                        'Name 5 things you can see',
                        'Name 4 things you can touch',
                        'Name 3 things you can hear',
                        'Name 2 things you can smell',
                        'Name 1 thing you can taste'
                    ],
                    'benefits': ['Reduces anxiety', 'Helps with panic attacks', 'Increases present moment awareness']
                },
                {
                    'name': 'Mindful Breathing Box',
                    'duration': '10 minutes',
                    'description': 'Square breathing technique for calm and focus.',
                    'instructions': [
                        'Breathe in for 4 counts',
                        'Hold for 4 counts',
                        'Breathe out for 4 counts',
                        'Hold empty for 4 counts',
                        'Repeat for 10 cycles'
                    ],
                    'benefits': ['Calms nervous system', 'Improves focus', 'Reduces stress']
                }
            ],
            'cognitive': [
                {
                    'name': 'Thought Record Journal',
                    'duration': '20 minutes',
                    'description': 'Identify and challenge negative thought patterns.',
                    'instructions': [
                        'Describe the situation that triggered negative thoughts',
                        'Write down your automatic thoughts',
                        'Rate the emotion intensity (0-100)',
                        'List evidence for and against the thought',
                        'Create a balanced, realistic thought',
                        'Re-rate your emotion'
                    ],
                    'benefits': ['Challenges cognitive distortions', 'Improves emotional regulation', 'Builds self-awareness']
                },
                {
                    'name': 'Gratitude Mapping',
                    'duration': '15 minutes',
                    'description': 'Create a visual map of things you appreciate.',
                    'instructions': [
                        'Draw yourself in the center of a page',
                        'Create branches for different life areas',
                        'Add specific things you\'re grateful for',
                        'Use colors to represent different emotions',
                        'Add new items daily'
                    ],
                    'benefits': ['Shifts focus to positive', 'Improves mood', 'Builds resilience']
                },
                {
                    'name': 'Values Clarification Exercise',
                    'duration': '30 minutes',
                    'description': 'Identify and prioritize your core values.',
                    'instructions': [
                        'List 10 values important to you',
                        'Define what each value means to you',
                        'Rank them by importance',
                        'Reflect on how you live these values',
                        'Identify one action for each top value'
                    ],
                    'benefits': ['Improves decision-making', 'Increases life satisfaction', 'Guides goal-setting']
                }
            ],
            'behavioral': [
                {
                    'name': 'Activity Scheduling',
                    'duration': '15 minutes daily',
                    'description': 'Plan enjoyable and meaningful activities.',
                    'instructions': [
                        'List activities that bring joy or accomplishment',
                        'Schedule 1-2 activities per day',
                        'Rate mood before and after each activity',
                        'Track patterns over a week',
                        'Adjust schedule based on what helps most'
                    ],
                    'benefits': ['Combats depression', 'Increases motivation', 'Builds positive routines']
                },
                {
                    'name': 'Exposure Ladder',
                    'duration': 'Variable',
                    'description': 'Gradually face fears in a controlled way.',
                    'instructions': [
                        'Identify your fear or anxiety trigger',
                        'List 10 situations from least to most scary',
                        'Start with the easiest situation',
                        'Stay in the situation until anxiety decreases',
                        'Move up the ladder gradually'
                    ],
                    'benefits': ['Reduces phobias', 'Builds confidence', 'Decreases avoidance']
                },
                {
                    'name': 'Habit Stacking',
                    'duration': '5 minutes planning',
                    'description': 'Build new positive habits onto existing ones.',
                    'instructions': [
                        'Identify a current daily habit',
                        'Choose a new habit to add',
                        'Link them with "After I [current habit], I will [new habit]"',
                        'Start with 2-minute versions',
                        'Gradually increase duration'
                    ],
                    'benefits': ['Creates lasting change', 'Reduces resistance', 'Builds healthy routines']
                }
            ],
            'emotional': [
                {
                    'name': 'Emotion Wheel Check-In',
                    'duration': '10 minutes',
                    'description': 'Identify and name complex emotions.',
                    'instructions': [
                        'Look at an emotion wheel diagram',
                        'Start with basic emotions in the center',
                        'Move outward to more specific feelings',
                        'Journal about what triggered these emotions',
                        'Note physical sensations with each emotion'
                    ],
                    'benefits': ['Improves emotional literacy', 'Enhances self-awareness', 'Facilitates communication']
                },
                {
                    'name': 'Self-Compassion Break',
                    'duration': '5-10 minutes',
                    'description': 'Practice kindness toward yourself during difficulty.',
                    'instructions': [
                        'Acknowledge: "This is a moment of suffering"',
                        'Remember: "Suffering is part of human experience"',
                        'Offer yourself kindness: "May I be kind to myself"',
                        'Place hand on heart for comfort',
                        'Speak to yourself as you would a friend'
                    ],
                    'benefits': ['Reduces self-criticism', 'Increases resilience', 'Improves emotional wellbeing']
                },
                {
                    'name': 'Emotional Freedom Technique (Tapping)',
                    'duration': '15 minutes',
                    'description': 'Use acupressure points while processing emotions.',
                    'instructions': [
                        'Rate your distress level (0-10)',
                        'Create a setup statement acknowledging the issue',
                        'Tap on specific points while repeating phrases',
                        'Work through negative and positive statements',
                        'Re-rate your distress level'
                    ],
                    'benefits': ['Reduces anxiety', 'Processes trauma', 'Calms nervous system']
                }
            ],
            'interpersonal': [
                {
                    'name': 'Active Listening Practice',
                    'duration': '20 minutes',
                    'description': 'Improve communication through focused listening.',
                    'instructions': [
                        'Partner speaks for 5 minutes uninterrupted',
                        'Listener focuses without planning response',
                        'Listener summarizes what they heard',
                        'Speaker confirms or clarifies',
                        'Switch roles and repeat'
                    ],
                    'benefits': ['Improves relationships', 'Reduces conflicts', 'Builds empathy']
                },
                {
                    'name': 'Boundary Setting Exercise',
                    'duration': '30 minutes',
                    'description': 'Define and communicate personal boundaries.',
                    'instructions': [
                        'List areas where you need boundaries',
                        'Define what you will and won\'t accept',
                        'Practice boundary statements',
                        'Identify consequences for violations',
                        'Role-play difficult conversations'
                    ],
                    'benefits': ['Improves self-respect', 'Reduces resentment', 'Enhances relationships']
                },
                {
                    'name': 'Empathy Building Cards',
                    'duration': '15 minutes',
                    'description': 'Practice seeing situations from others\' perspectives.',
                    'instructions': [
                        'Write a conflict on a card',
                        'List your perspective',
                        'Imagine the other person\'s view',
                        'Find three possible explanations for their behavior',
                        'Identify common ground'
                    ],
                    'benefits': ['Reduces judgment', 'Improves understanding', 'Resolves conflicts']
                }
            ],
            'creative': [
                {
                    'name': 'Art Therapy Expression',
                    'duration': '30-45 minutes',
                    'description': 'Express emotions through creative art.',
                    'instructions': [
                        'Choose art materials that appeal to you',
                        'Set intention: express current feelings',
                        'Create without judging the outcome',
                        'Notice colors, shapes, and patterns',
                        'Journal about what emerged'
                    ],
                    'benefits': ['Processes unconscious feelings', 'Reduces stress', 'Enhances self-expression']
                },
                {
                    'name': 'Music Mood Playlist',
                    'duration': '20 minutes',
                    'description': 'Create playlists for emotional regulation.',
                    'instructions': [
                        'Create a playlist for your current mood',
                        'Make another for your desired mood',
                        'Include transitional songs between them',
                        'Listen mindfully to the progression',
                        'Note how music affects your state'
                    ],
                    'benefits': ['Regulates emotions', 'Provides coping tool', 'Increases self-awareness']
                },
                {
                    'name': 'Therapeutic Writing Prompts',
                    'duration': '20 minutes',
                    'description': 'Explore thoughts and feelings through guided writing.',
                    'instructions': [
                        'Choose a prompt that resonates',
                        'Write continuously without editing',
                        'Don\'t worry about grammar or structure',
                        'Write for the full time',
                        'Read back and highlight insights'
                    ],
                    'benefits': ['Clarifies thoughts', 'Processes emotions', 'Gains insights']
                }
            ],
            'somatic': [
                {
                    'name': 'Progressive Muscle Relaxation',
                    'duration': '20 minutes',
                    'description': 'Systematically tense and relax muscle groups.',
                    'instructions': [
                        'Start with your toes, tense for 5 seconds',
                        'Release and notice the relaxation',
                        'Move up through each muscle group',
                        'Include face and scalp',
                        'End with whole body awareness'
                    ],
                    'benefits': ['Reduces physical tension', 'Improves sleep', 'Decreases anxiety']
                },
                {
                    'name': 'Butterfly Hug',
                    'duration': '5-10 minutes',
                    'description': 'Self-soothing technique for emotional regulation.',
                    'instructions': [
                        'Cross arms over chest, hands on shoulders',
                        'Alternate tapping each shoulder',
                        'Maintain slow, rhythmic pace',
                        'Breathe deeply while tapping',
                        'Continue until feeling calmer'
                    ],
                    'benefits': ['Calms nervous system', 'Provides self-comfort', 'Reduces distress']
                },
                {
                    'name': 'Yoga for Emotions',
                    'duration': '30 minutes',
                    'description': 'Use specific poses for emotional release.',
                    'instructions': [
                        'Child\'s pose for safety and comfort',
                        'Warrior poses for confidence',
                        'Heart openers for grief or sadness',
                        'Twists for letting go',
                        'End in relaxation pose'
                    ],
                    'benefits': ['Releases stored emotions', 'Improves mind-body connection', 'Builds resilience']
                }
            ]
        }
        
        self.prompts = {
            'journaling': [
                "What would you do if you knew you couldn't fail?",
                "Describe a time when you felt truly authentic.",
                "What patterns do you notice in your relationships?",
                "If your emotions had colors, what would today look like?",
                "What would your best friend say about your current situation?",
                "Write a letter to your younger self.",
                "What are you avoiding and why?",
                "Describe your ideal day in detail.",
                "What would letting go look like for you?",
                "How has your greatest challenge shaped you?"
            ],
            'reflection': [
                "What did you learn about yourself this week?",
                "How have your values influenced recent decisions?",
                "What masks do you wear and with whom?",
                "When do you feel most like yourself?",
                "What would change if you fully accepted yourself?",
                "How do you define success for yourself?",
                "What beliefs about yourself are you ready to challenge?",
                "What brings you genuine joy versus temporary pleasure?",
                "How do you want to be remembered?",
                "What growth have you noticed in yourself lately?"
            ]
        }
    
    def get_activity(self, category: str, difficulty: str = 'moderate') -> Dict:
        """Get a specific activity from a category"""
        if category in self.activities:
            activities = self.activities[category]
            return random.choice(activities)
        return None
    
    def get_personalized_plan(self, concerns: List[str], session_type: str) -> List[Dict]:
        """Create a personalized activity plan based on concerns"""
        plan = []
        
        # Map concerns to activity categories
        concern_mapping = {
            'anxiety': ['mindfulness', 'somatic', 'cognitive'],
            'depression': ['behavioral', 'creative', 'cognitive'],
            'relationships': ['interpersonal', 'emotional', 'mindfulness'],
            'stress': ['somatic', 'mindfulness', 'creative'],
            'trauma': ['somatic', 'emotional', 'creative'],
            'self-esteem': ['cognitive', 'creative', 'emotional']
        }
        
        for concern in concerns:
            if concern.lower() in concern_mapping:
                categories = concern_mapping[concern.lower()]
                for cat in categories[:2]:  # Pick top 2 categories
                    activity = self.get_activity(cat)
                    if activity and activity not in plan:
                        plan.append(activity)
        
        return plan[:3]  # Return top 3 activities
    
    def get_crisis_activities(self) -> List[Dict]:
        """Get immediate activities for crisis situations"""
        crisis_activities = [
            {
                'name': 'TIPP Technique',
                'duration': 'Immediate',
                'description': 'Rapid distress tolerance for crisis moments.',
                'instructions': [
                    'Temperature: Splash cold water on face',
                    'Intense exercise: Do jumping jacks for 1 minute',
                    'Paced breathing: Breathe out longer than in',
                    'Paired muscle relaxation: Tense and release'
                ],
                'benefits': ['Immediate relief', 'Prevents impulsive actions', 'Calms intense emotions']
            },
            {
                'name': 'Crisis Grounding',
                'duration': '2-5 minutes',
                'description': 'Quick grounding for panic or dissociation.',
                'instructions': [
                    'Plant feet firmly on ground',
                    'Name your location and date',
                    'Touch 3 different textures',
                    'Say 3 affirmations out loud',
                    'Call a support person if needed'
                ],
                'benefits': ['Prevents dissociation', 'Reduces panic', 'Reconnects to present']
            }
        ]
        return crisis_activities
    
    def get_daily_check_in(self) -> Dict:
        """Get a daily mental health check-in activity"""
        return {
            'name': 'Daily Wellness Check-In',
            'duration': '5 minutes',
            'description': 'Quick daily assessment and intention setting.',
            'instructions': [
                'Rate your mood (1-10)',
                'Name your primary emotion',
                'List 3 things you\'re grateful for',
                'Set one intention for the day',
                'Choose one self-care activity'
            ],
            'benefits': ['Tracks patterns', 'Increases awareness', 'Promotes daily wellness']
        }