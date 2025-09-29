"""
AI-powered conversation starters for couples therapy
Provides contextual conversation prompts based on relationship stage, issues, and therapy goals
"""

import random
from datetime import datetime
from typing import List, Dict

class ConversationStarterGenerator:
    def __init__(self):
        self.starters = {
            'connection': [
                {
                    'prompt': "What first attracted you to your partner?",
                    'follow_up': "How has that attraction evolved over time?",
                    'category': 'appreciation',
                    'depth': 'light'
                },
                {
                    'prompt': "Describe a moment when you felt most connected to your partner.",
                    'follow_up': "What made that moment special?",
                    'category': 'intimacy',
                    'depth': 'medium'
                },
                {
                    'prompt': "What's one thing your partner does that makes you feel loved?",
                    'follow_up': "How often do you experience this?",
                    'category': 'love_languages',
                    'depth': 'light'
                },
                {
                    'prompt': "Share a dream or goal you haven't discussed with your partner yet.",
                    'follow_up': "What's holding you back from sharing this?",
                    'category': 'vulnerability',
                    'depth': 'deep'
                },
                {
                    'prompt': "What adventure would you like to experience together?",
                    'follow_up': "What's the first step to making this happen?",
                    'category': 'future_planning',
                    'depth': 'medium'
                }
            ],
            'communication': [
                {
                    'prompt': "How do you prefer to receive feedback from your partner?",
                    'follow_up': "Can you give an example of feedback that was helpful?",
                    'category': 'communication_style',
                    'depth': 'medium'
                },
                {
                    'prompt': "What's one thing you wish your partner understood better about you?",
                    'follow_up': "How could you help them understand this?",
                    'category': 'understanding',
                    'depth': 'medium'
                },
                {
                    'prompt': "Describe your ideal way to resolve disagreements.",
                    'follow_up': "What makes this approach work for you?",
                    'category': 'conflict_resolution',
                    'depth': 'medium'
                },
                {
                    'prompt': "What topics do you find hardest to discuss with your partner?",
                    'follow_up': "What would make these conversations easier?",
                    'category': 'difficult_topics',
                    'depth': 'deep'
                },
                {
                    'prompt': "How do you show your partner you're listening?",
                    'follow_up': "How do you know when they're really listening to you?",
                    'category': 'active_listening',
                    'depth': 'light'
                }
            ],
            'conflict_resolution': [
                {
                    'prompt': "What's a recent disagreement you resolved well together?",
                    'follow_up': "What made the resolution successful?",
                    'category': 'success_stories',
                    'depth': 'medium'
                },
                {
                    'prompt': "How do you typically react when you're upset with your partner?",
                    'follow_up': "Is this reaction helpful or harmful?",
                    'category': 'self_awareness',
                    'depth': 'deep'
                },
                {
                    'prompt': "What's one recurring conflict in your relationship?",
                    'follow_up': "What might be the deeper need behind this conflict?",
                    'category': 'patterns',
                    'depth': 'deep'
                },
                {
                    'prompt': "How do you repair hurt feelings after an argument?",
                    'follow_up': "What helps you forgive and move forward?",
                    'category': 'repair',
                    'depth': 'medium'
                },
                {
                    'prompt': "What boundaries do you need in your relationship?",
                    'follow_up': "How can you communicate these respectfully?",
                    'category': 'boundaries',
                    'depth': 'deep'
                }
            ],
            'intimacy': [
                {
                    'prompt': "What makes you feel emotionally safe with your partner?",
                    'follow_up': "How can you create more of this safety?",
                    'category': 'emotional_safety',
                    'depth': 'deep'
                },
                {
                    'prompt': "How do you like to show affection?",
                    'follow_up': "How does your partner prefer to receive affection?",
                    'category': 'affection',
                    'depth': 'light'
                },
                {
                    'prompt': "What's your favorite way to spend quality time together?",
                    'follow_up': "When did you last do this activity?",
                    'category': 'quality_time',
                    'depth': 'light'
                },
                {
                    'prompt': "What does intimacy mean to you beyond physical connection?",
                    'follow_up': "How can you deepen this type of intimacy?",
                    'category': 'emotional_intimacy',
                    'depth': 'deep'
                },
                {
                    'prompt': "What fears do you have about being vulnerable?",
                    'follow_up': "What would help you feel safer being vulnerable?",
                    'category': 'vulnerability',
                    'depth': 'deep'
                }
            ],
            'growth': [
                {
                    'prompt': "How have you grown as a person since being with your partner?",
                    'follow_up': "How has your partner contributed to this growth?",
                    'category': 'personal_growth',
                    'depth': 'medium'
                },
                {
                    'prompt': "What's one thing you'd like to change about yourself for the relationship?",
                    'follow_up': "What support do you need to make this change?",
                    'category': 'self_improvement',
                    'depth': 'deep'
                },
                {
                    'prompt': "What shared goals do you have for the next year?",
                    'follow_up': "What's the first step toward these goals?",
                    'category': 'future_planning',
                    'depth': 'medium'
                },
                {
                    'prompt': "How do you support each other's individual dreams?",
                    'follow_up': "Where could you offer more support?",
                    'category': 'support',
                    'depth': 'medium'
                },
                {
                    'prompt': "What relationship skills would you like to develop?",
                    'follow_up': "How can you practice these together?",
                    'category': 'skill_building',
                    'depth': 'medium'
                }
            ],
            'appreciation': [
                {
                    'prompt': "What's something your partner did recently that you appreciated?",
                    'follow_up': "Did you express this appreciation? How?",
                    'category': 'gratitude',
                    'depth': 'light'
                },
                {
                    'prompt': "What qualities in your partner do you most admire?",
                    'follow_up': "How do these qualities complement yours?",
                    'category': 'admiration',
                    'depth': 'light'
                },
                {
                    'prompt': "Describe a time your partner was there for you when you needed them.",
                    'follow_up': "How did their support impact you?",
                    'category': 'support',
                    'depth': 'medium'
                },
                {
                    'prompt': "What small gestures from your partner mean the most to you?",
                    'follow_up': "How often do you notice these gestures?",
                    'category': 'small_things',
                    'depth': 'light'
                },
                {
                    'prompt': "How has your partner made you a better person?",
                    'follow_up': "Have you told them this?",
                    'category': 'impact',
                    'depth': 'medium'
                }
            ],
            'fun': [
                {
                    'prompt': "What's the funniest memory you share together?",
                    'follow_up': "What made this moment so memorable?",
                    'category': 'humor',
                    'depth': 'light'
                },
                {
                    'prompt': "If you could plan the perfect date, what would it be?",
                    'follow_up': "What elements would make it special for both of you?",
                    'category': 'romance',
                    'depth': 'light'
                },
                {
                    'prompt': "What's a new activity you'd both like to try?",
                    'follow_up': "What's stopping you from trying it?",
                    'category': 'adventure',
                    'depth': 'light'
                },
                {
                    'prompt': "What inside jokes do you share?",
                    'follow_up': "How did these jokes start?",
                    'category': 'humor',
                    'depth': 'light'
                },
                {
                    'prompt': "If you could travel anywhere together, where would it be?",
                    'follow_up': "What would you do there?",
                    'category': 'dreams',
                    'depth': 'light'
                }
            ]
        }
        
        # Contextual modifiers based on relationship stage
        self.stage_modifiers = {
            'new': ['getting to know', 'discovering', 'exploring'],
            'established': ['deepening', 'maintaining', 'strengthening'],
            'struggling': ['rebuilding', 'reconnecting', 'healing'],
            'growing': ['evolving', 'transforming', 'advancing']
        }
        
    def get_starter(self, category: str = 'random', depth: str = 'medium', 
                   relationship_stage: str = 'established', 
                   recent_topics: List[str] = []) -> Dict:
        """
        Get a conversation starter based on parameters
        
        Args:
            category: Type of conversation (connection, communication, etc.)
            depth: Conversation depth (light, medium, deep)
            relationship_stage: Current stage of relationship
            recent_topics: Recently discussed topics to avoid repetition
            
        Returns:
            Dictionary with starter prompt and metadata
        """
        if category == 'random':
            category = random.choice(list(self.starters.keys()))
            
        if category not in self.starters:
            category = 'connection'  # Default fallback
            
        # Filter by depth if specified
        available_starters = [s for s in self.starters[category] 
                            if depth == 'any' or s['depth'] == depth]
        
        if not available_starters:
            available_starters = self.starters[category]
            
        # Avoid recent topics if provided
        if recent_topics:
            filtered = [s for s in available_starters 
                       if s['category'] not in recent_topics]
            if filtered:
                available_starters = filtered
                
        starter = random.choice(available_starters)
        
        # Add contextual elements based on relationship stage
        if relationship_stage in self.stage_modifiers:
            modifier = random.choice(self.stage_modifiers[relationship_stage])
            starter['context'] = f"Focus on {modifier} your relationship"
            
        starter['timestamp'] = datetime.now().isoformat()
        starter['main_category'] = category
        
        return starter
        
    def get_themed_sequence(self, theme: str, count: int = 5) -> List[Dict]:
        """
        Get a sequence of related conversation starters
        
        Args:
            theme: Overall theme for the sequence
            count: Number of starters to return
            
        Returns:
            List of conversation starters
        """
        if theme not in self.starters:
            theme = 'connection'
            
        sequence = []
        used_categories = []
        
        for i in range(min(count, len(self.starters[theme]))):
            available = [s for s in self.starters[theme] 
                        if s['category'] not in used_categories]
            if not available:
                available = self.starters[theme]
                used_categories = []
                
            starter = random.choice(available)
            starter['sequence_number'] = str(i + 1)
            starter['theme'] = theme
            sequence.append(starter.copy())
            used_categories.append(starter['category'])
            
        return sequence
        
    def get_ice_breaker(self) -> Dict:
        """Get a light, fun conversation starter for beginning sessions"""
        fun_categories = ['fun', 'appreciation']
        category = random.choice(fun_categories)
        light_starters = [s for s in self.starters[category] if s['depth'] == 'light']
        
        if light_starters:
            return random.choice(light_starters)
        else:
            return random.choice(self.starters[category])
            
    def get_deeper_prompt(self, current_topic: str) -> Dict:
        """Get a deeper follow-up prompt based on current discussion"""
        # Find starters related to current topic
        related_starters = []
        
        for category, starters in self.starters.items():
            for starter in starters:
                if (starter['depth'] in ['medium', 'deep'] and 
                    any(word in starter['prompt'].lower() for word in current_topic.lower().split())):
                    related_starters.append(starter)
                    
        if related_starters:
            return random.choice(related_starters)
        else:
            # Return a deep starter from any category
            deep_starters = []
            for starters in self.starters.values():
                deep_starters.extend([s for s in starters if s['depth'] == 'deep'])
            return random.choice(deep_starters)
            
    def get_categories(self) -> List[str]:
        """Get all available conversation categories"""
        return list(self.starters.keys())
        
    def get_by_issue(self, issue: str) -> Dict:
        """Get conversation starter based on specific relationship issue"""
        issue_mapping = {
            'trust': 'communication',
            'distance': 'connection',
            'arguing': 'conflict_resolution',
            'boredom': 'fun',
            'passion': 'intimacy',
            'support': 'appreciation',
            'future': 'growth'
        }
        
        category = issue_mapping.get(issue.lower(), 'connection')
        return self.get_starter(category=category)