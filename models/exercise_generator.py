import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional
import os
from openai import OpenAI

class ExerciseGenerator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-openai-api-key"))
        
        # Exercise categories and templates
        self.exercise_categories = {
            "breathing": {
                "name": "Breathing Exercises",
                "benefits": ["stress reduction", "anxiety management", "emotional regulation"],
                "duration_range": (3, 10),
                "difficulty_levels": [1, 2, 3]
            },
            "mindfulness": {
                "name": "Mindfulness Practices",
                "benefits": ["present moment awareness", "emotional balance", "stress relief"],
                "duration_range": (5, 20),
                "difficulty_levels": [1, 2, 3, 4]
            },
            "cognitive": {
                "name": "Cognitive Exercises",
                "benefits": ["thought restructuring", "problem solving", "perspective taking"],
                "duration_range": (10, 30),
                "difficulty_levels": [2, 3, 4, 5]
            },
            "movement": {
                "name": "Movement Therapy",
                "benefits": ["physical tension release", "mood improvement", "energy boost"],
                "duration_range": (5, 15),
                "difficulty_levels": [1, 2, 3, 4]
            },
            "creative": {
                "name": "Creative Expression",
                "benefits": ["emotional processing", "self-discovery", "stress relief"],
                "duration_range": (15, 45),
                "difficulty_levels": [1, 2, 3, 4, 5]
            },
            "social": {
                "name": "Social Connection",
                "benefits": ["relationship building", "communication skills", "support system"],
                "duration_range": (10, 30),
                "difficulty_levels": [2, 3, 4]
            },
            "grounding": {
                "name": "Grounding Techniques",
                "benefits": ["anxiety reduction", "panic management", "present moment focus"],
                "duration_range": (2, 8),
                "difficulty_levels": [1, 2]
            }
        }
        
        # Pre-built exercise templates
        self.exercise_templates = {
            "breathing": [
                {
                    "title": "4-7-8 Breathing",
                    "description": "A calming breathing technique for anxiety and stress relief",
                    "instructions": [
                        "Sit comfortably with your back straight",
                        "Exhale completely through your mouth",
                        "Inhale through nose for 4 counts",
                        "Hold breath for 7 counts",
                        "Exhale through mouth for 8 counts",
                        "Repeat 3-4 cycles"
                    ],
                    "duration_minutes": 5,
                    "difficulty_level": 1
                },
                {
                    "title": "Box Breathing",
                    "description": "Equal count breathing for focus and calm",
                    "instructions": [
                        "Inhale for 4 counts",
                        "Hold for 4 counts",
                        "Exhale for 4 counts",
                        "Hold empty for 4 counts",
                        "Repeat for 5-10 cycles"
                    ],
                    "duration_minutes": 6,
                    "difficulty_level": 2
                }
            ],
            "mindfulness": [
                {
                    "title": "5-4-3-2-1 Grounding",
                    "description": "Sensory grounding technique for anxiety and panic",
                    "instructions": [
                        "Notice 5 things you can see",
                        "Notice 4 things you can touch",
                        "Notice 3 things you can hear",
                        "Notice 2 things you can smell",
                        "Notice 1 thing you can taste",
                        "Take three deep breaths"
                    ],
                    "duration_minutes": 5,
                    "difficulty_level": 1
                },
                {
                    "title": "Body Scan Meditation",
                    "description": "Progressive awareness of physical sensations",
                    "instructions": [
                        "Lie down comfortably",
                        "Start at the top of your head",
                        "Slowly scan down through your body",
                        "Notice sensations without judgment",
                        "Breathe into areas of tension",
                        "Complete the scan at your toes"
                    ],
                    "duration_minutes": 15,
                    "difficulty_level": 2
                }
            ],
            "cognitive": [
                {
                    "title": "Thought Record",
                    "description": "Identify and challenge negative thought patterns",
                    "instructions": [
                        "Write down the triggering situation",
                        "Identify the negative thought",
                        "Rate the intensity (1-10)",
                        "List evidence for and against the thought",
                        "Create a balanced alternative thought",
                        "Re-rate the intensity"
                    ],
                    "duration_minutes": 20,
                    "difficulty_level": 3
                }
            ]
        }
    
    def generate_exercises(self, session_data: str, session_type: str, ai_analysis: Dict = None) -> List[Dict]:
        """Generate personalized exercises based on session data and AI analysis"""
        try:
            # Analyze session needs
            exercise_needs = self._analyze_exercise_needs(session_data, session_type, ai_analysis)
            
            # Generate AI-powered exercises
            ai_exercises = self._generate_ai_exercises(exercise_needs, session_type)
            
            # Select template exercises
            template_exercises = self._select_template_exercises(exercise_needs)
            
            # Combine and prioritize
            all_exercises = ai_exercises + template_exercises
            
            # Personalize based on session data
            personalized_exercises = self._personalize_exercises(all_exercises, session_data, ai_analysis)
            
            return personalized_exercises[:5]  # Return top 5 exercises
            
        except Exception as e:
            logging.error(f"Exercise generation error: {e}")
            return self._get_fallback_exercises(session_type)
    
    def _analyze_exercise_needs(self, session_data: str, session_type: str, ai_analysis: Dict = None) -> Dict:
        """Analyze what types of exercises would be most beneficial"""
        needs = {
            "primary_needs": [],
            "secondary_needs": [],
            "stress_level": "moderate",
            "emotional_state": "neutral",
            "preferred_categories": [],
            "avoid_categories": []
        }
        
        # Analyze session text
        session_lower = session_data.lower()
        
        # Identify primary needs based on keywords
        if any(word in session_lower for word in ["anxious", "worried", "panic", "nervous"]):
            needs["primary_needs"].extend(["breathing", "grounding", "mindfulness"])
            needs["stress_level"] = "high"
        
        if any(word in session_lower for word in ["sad", "depressed", "down", "hopeless"]):
            needs["primary_needs"].extend(["movement", "creative", "cognitive"])
            needs["emotional_state"] = "low"
        
        if any(word in session_lower for word in ["angry", "frustrated", "mad", "furious"]):
            needs["primary_needs"].extend(["breathing", "movement", "cognitive"])
            needs["emotional_state"] = "activated"
        
        if any(word in session_lower for word in ["overwhelmed", "stressed", "pressure"]):
            needs["primary_needs"].extend(["mindfulness", "breathing", "grounding"])
            needs["stress_level"] = "high"
        
        # Session type specific needs
        if session_type in ["couple", "relationship"]:
            needs["secondary_needs"].append("social")
        elif session_type == "group":
            needs["secondary_needs"].extend(["social", "creative"])
        
        # AI analysis integration
        if ai_analysis:
            if isinstance(ai_analysis, dict):
                emotional_state = ai_analysis.get("emotional_state", "").lower()
                if "anxiety" in emotional_state:
                    needs["primary_needs"].append("breathing")
                if "depression" in emotional_state:
                    needs["primary_needs"].append("movement")
                
                risk_level = ai_analysis.get("risk_level", "low")
                if risk_level in ["high", "critical"]:
                    needs["primary_needs"] = ["grounding", "breathing"]
                    needs["avoid_categories"] = ["cognitive"]  # Avoid complex thinking when in crisis
        
        return needs
    
    def _generate_ai_exercises(self, exercise_needs: Dict, session_type: str) -> List[Dict]:
        """Generate custom exercises using AI based on specific needs"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            
            prompt = f"""Create personalized therapeutic exercises for a {session_type} therapy session.
            
            Exercise needs: {json.dumps(exercise_needs)}
            
            Generate 2 exercises in JSON format as an array with this structure:
            [{{
                "title": "Exercise Name",
                "description": "Brief description of the exercise",
                "category": "breathing/mindfulness/cognitive/movement/creative/social/grounding",
                "instructions": ["step 1", "step 2", "step 3"],
                "duration_minutes": 5,
                "difficulty_level": 2,
                "benefits": ["benefit 1", "benefit 2"],
                "personalization_notes": "How this addresses specific needs"
            }}]
            
            Focus on evidence-based techniques that address the identified needs."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a therapeutic exercise specialist. Create personalized, evidence-based exercises. Always respond with valid JSON array format."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Handle different response formats
            if isinstance(result, dict) and "exercises" in result:
                exercises = result["exercises"]
            elif isinstance(result, list):
                exercises = result
            else:
                exercises = [result] if isinstance(result, dict) else []
            
            # Add metadata
            for exercise in exercises:
                exercise["source"] = "ai_generated"
                exercise["timestamp"] = datetime.now().isoformat()
            
            return exercises
            
        except Exception as e:
            logging.error(f"AI exercise generation error: {e}")
            return []
    
    def _select_template_exercises(self, exercise_needs: Dict) -> List[Dict]:
        """Select appropriate template exercises based on needs"""
        selected_exercises = []
        primary_needs = exercise_needs.get("primary_needs", [])
        
        for category in primary_needs:
            if category in self.exercise_templates:
                templates = self.exercise_templates[category]
                for template in templates:
                    exercise = template.copy()
                    exercise["category"] = category
                    exercise["source"] = "template"
                    exercise["benefits"] = self.exercise_categories[category]["benefits"]
                    selected_exercises.append(exercise)
        
        return selected_exercises
    
    def _personalize_exercises(self, exercises: List[Dict], session_data: str, ai_analysis: Dict = None) -> List[Dict]:
        """Personalize exercises based on session context"""
        personalized = []
        
        for exercise in exercises:
            personalized_exercise = exercise.copy()
            
            # Adjust difficulty based on stress level
            if ai_analysis and isinstance(ai_analysis, dict):
                risk_level = ai_analysis.get("risk_level", "low")
                if risk_level in ["high", "critical"]:
                    personalized_exercise["difficulty_level"] = min(personalized_exercise.get("difficulty_level", 3), 2)
                    personalized_exercise["duration_minutes"] = min(personalized_exercise.get("duration_minutes", 10), 5)
            
            # Add session-specific notes
            session_lower = session_data.lower()
            personalization_notes = []
            
            if "time" in session_lower and "no time" in session_lower:
                personalized_exercise["duration_minutes"] = min(personalized_exercise.get("duration_minutes", 10), 5)
                personalization_notes.append("Shortened for time constraints")
            
            if any(word in session_lower for word in ["beginner", "new", "never done"]):
                personalized_exercise["difficulty_level"] = 1
                personalization_notes.append("Adapted for beginners")
            
            if personalization_notes:
                existing_notes = personalized_exercise.get("personalization_notes", "")
                personalized_exercise["personalization_notes"] = existing_notes + " " + ". ".join(personalization_notes)
            
            # Calculate priority score
            personalized_exercise["priority_score"] = self._calculate_priority_score(personalized_exercise, session_data, ai_analysis)
            
            personalized.append(personalized_exercise)
        
        # Sort by priority score
        personalized.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return personalized
    
    def _calculate_priority_score(self, exercise: Dict, session_data: str, ai_analysis: Dict = None) -> float:
        """Calculate priority score for exercise ranking"""
        score = 0.0
        
        # Base score by category
        category_scores = {
            "breathing": 0.8,
            "grounding": 0.9,
            "mindfulness": 0.7,
            "cognitive": 0.6,
            "movement": 0.5,
            "creative": 0.4,
            "social": 0.3
        }
        
        score += category_scores.get(exercise.get("category", ""), 0.5)
        
        # Adjust for session content relevance
        session_lower = session_data.lower()
        
        if exercise.get("category") == "breathing" and any(word in session_lower for word in ["anxious", "panic", "nervous"]):
            score += 0.3
        
        if exercise.get("category") == "cognitive" and any(word in session_lower for word in ["thinking", "thoughts", "worry"]):
            score += 0.2
        
        if exercise.get("category") == "movement" and any(word in session_lower for word in ["tired", "sluggish", "low energy"]):
            score += 0.2
        
        # Adjust for AI analysis
        if ai_analysis and isinstance(ai_analysis, dict):
            risk_level = ai_analysis.get("risk_level", "low")
            if risk_level in ["high", "critical"] and exercise.get("category") in ["breathing", "grounding"]:
                score += 0.4
        
        # Prefer shorter exercises for high stress
        duration = exercise.get("duration_minutes", 10)
        if duration <= 5:
            score += 0.1
        elif duration >= 20:
            score -= 0.1
        
        # Prefer easier exercises for crisis situations
        difficulty = exercise.get("difficulty_level", 3)
        if difficulty <= 2:
            score += 0.1
        elif difficulty >= 4:
            score -= 0.1
        
        return score
    
    def _get_fallback_exercises(self, session_type: str) -> List[Dict]:
        """Get fallback exercises when AI generation fails"""
        fallback_exercises = [
            {
                "title": "Deep Breathing",
                "description": "Simple breathing exercise for immediate calm",
                "category": "breathing",
                "instructions": [
                    "Sit comfortably",
                    "Breathe in slowly for 4 counts",
                    "Hold for 2 counts",
                    "Breathe out slowly for 6 counts",
                    "Repeat 5 times"
                ],
                "duration_minutes": 3,
                "difficulty_level": 1,
                "benefits": ["stress reduction", "immediate calm"],
                "source": "fallback"
            },
            {
                "title": "Present Moment Awareness",
                "description": "Simple mindfulness exercise",
                "category": "mindfulness",
                "instructions": [
                    "Notice where you are right now",
                    "Feel your feet on the ground",
                    "Notice three things you can see",
                    "Take three conscious breaths",
                    "Set an intention for the next hour"
                ],
                "duration_minutes": 2,
                "difficulty_level": 1,
                "benefits": ["grounding", "present moment focus"],
                "source": "fallback"
            }
        ]
        
        return fallback_exercises
