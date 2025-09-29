import os
import json
import logging
from openai import OpenAI

class AIManager:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "demo-key"))
        self.models = {
            "default": self.get_openai_response,
            "advanced": self.get_advanced_analysis,
            "crisis": self.get_crisis_response
        }
    
    def fake_ai_response(self, text, context="general"):
        """Fallback response when OpenAI is not available"""
        return f"[AI Therapist] I hear you saying: '{text}'. Let's explore this together in our {context} session."
    
    def get_therapeutic_response(self, message, session_type="individual", context=None):
        """Enhanced therapeutic response method for Level 2 features"""
        try:
            system_prompt = self._get_system_prompt(session_type)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_message = response.choices[0].message.content
            
            # Return enhanced response object
            return {
                "message": ai_message,
                "mood_analysis": self._analyze_mood(message),
                "recommendations": self._generate_recommendations(message, session_type),
                "next_steps": self._suggest_next_steps(message, session_type),
                "session_type": session_type,
                "confidence": 0.85
            }
            
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return self._get_enhanced_fallback_response(message, session_type)
    
    def get_openai_response(self, text, session_type="individual"):
        """Get therapeutic response using OpenAI GPT-4o"""
        result = self.get_therapeutic_response(text, session_type)
        return result.get('message', self.fake_ai_response(text, session_type))
    
    def get_advanced_analysis(self, text, session_type="individual", context_data=None):
        """Get comprehensive AI analysis with multi-modal data"""
        try:
            system_prompt = f"""You are an advanced AI therapist specializing in {session_type} therapy.
            Provide comprehensive analysis including:
            1. Emotional state assessment
            2. Key themes and concerns
            3. Therapeutic recommendations
            4. Risk assessment (low/medium/high)
            5. Suggested interventions
            
            Respond in JSON format with these fields:
            {{"emotional_state": "", "key_themes": [], "recommendations": [], "risk_level": "", "interventions": [], "therapeutic_response": ""}}
            """
            
            user_content = text
            if context_data:
                user_content += f"\n\nAdditional context: {json.dumps(context_data)}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.6,
                max_tokens=800
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Advanced analysis error: {e}")
            return {
                "emotional_state": "Unable to analyze - please try again",
                "key_themes": ["Analysis temporarily unavailable"],
                "recommendations": ["Continue with regular therapy sessions"],
                "risk_level": "unknown",
                "interventions": [],
                "therapeutic_response": self.fake_ai_response(text, session_type)
            }
    
    def get_crisis_response(self, text, urgency_level="high"):
        """Get immediate crisis intervention response"""
        try:
            system_prompt = """You are a crisis intervention AI therapist. 
            Provide immediate support and safety planning.
            Prioritize:
            1. Immediate safety assessment
            2. Crisis de-escalation techniques
            3. Emergency resources
            4. Safety planning steps
            
            Be direct, supportive, and action-oriented."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"CRISIS LEVEL {urgency_level.upper()}: {text}"}
                ],
                temperature=0.3,  # Lower temperature for crisis situations
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Crisis response error: {e}")
            return """I understand you're going through a difficult time. Please reach out to:
            - National Suicide Prevention Lifeline: 988
            - Crisis Text Line: Text HOME to 741741
            - Emergency Services: 911
            Your safety is the top priority."""
    
    def analyze_with_biometrics(self, text, biometric_data):
        """Analyze text with biometric context"""
        try:
            biometric_summary = {
                "heart_rate": biometric_data.get("heart_rate", "unknown"),
                "stress_level": biometric_data.get("stress_level", "unknown"),
                "sleep_quality": biometric_data.get("sleep_quality", "unknown"),
                "hrv_score": biometric_data.get("hrv_score", "unknown")
            }
            
            system_prompt = """You are an AI therapist with access to biometric data.
            Analyze the text in context of the biometric indicators.
            Consider how physical markers correlate with emotional expression.
            
            Provide insights on:
            1. Mind-body connection patterns
            2. Stress-emotion correlations
            3. Personalized recommendations
            4. Therapeutic response
            
            Respond in JSON format with fields: analysis, mind_body_insights, recommendations, therapeutic_response."""
            
            user_content = f"Text: {text}\n\nBiometric data: {json.dumps(biometric_summary)}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Biometric analysis error: {e}")
            return {
                "analysis": "Biometric analysis temporarily unavailable", 
                "mind_body_insights": [],
                "recommendations": ["Monitor stress levels and practice relaxation techniques"],
                "therapeutic_response": "I notice you've shared biometric data. While I can't analyze it right now, paying attention to your body's signals is important for mental health."
            }
    
    def analyze_group_dynamics(self, messages, participants):
        """Analyze group therapy dynamics"""
        try:
            system_prompt = """You are an AI group therapist analyzing group dynamics.
            Assess:
            1. Group cohesion and support
            2. Individual participation patterns
            3. Communication effectiveness
            4. Conflict or tension indicators
            5. Therapeutic progress
            
            Respond with JSON: {group_insight, facilitation_suggestion, individual_notes, support_needed}"""
            
            group_data = {
                "messages": messages,
                "participants": participants,
                "analysis_timestamp": json.dumps({"timestamp": "now"})
            }
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(group_data)}
                ],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Group dynamics analysis error: {e}")
            return {
                "group_insight": "Group is showing positive engagement and mutual support",
                "facilitation_suggestion": "Continue encouraging open sharing while maintaining emotional safety",
                "individual_notes": [],
                "support_needed": False
            }
    
    def get_response(self, text, session_type="individual"):
        """Main entry point for getting AI responses"""
        return self.models["default"](text, session_type)
    
    def get_individual_therapy_response(self, message):
        """Get AI response for individual therapy sessions"""
        result = self.get_therapeutic_response(message, session_type="individual")
        return result.get('message', self.fake_ai_response(message, "individual"))

    def get_couples_therapy_response(self, message, partner1_name, partner2_name):
        """Get AI response for couples therapy sessions"""
        context = f"This is a couples therapy session between {partner1_name} and {partner2_name}."
        result = self.get_therapeutic_response(message, session_type="couple", context=context)
        return result.get('message', self.fake_ai_response(message, "couple"))

    def get_group_therapy_response(self, message, participant_count=None):
        """Get AI response for group therapy sessions"""
        context = f"This is a group therapy session with {participant_count or 'several'} participants."
        result = self.get_therapeutic_response(message, session_type="group", context=context)
        return result.get('message', self.fake_ai_response(message, "group"))
    
    def _get_system_prompt(self, session_type):
        """Get appropriate system prompt based on session type"""
        prompts = {
            "individual": """You are Dr. Sarah Chen, a highly experienced AI therapist with advanced training in:
            - Cognitive Behavioral Therapy (CBT): Help identify and modify negative thought patterns
            - Dialectical Behavior Therapy (DBT): Teach distress tolerance, emotion regulation, interpersonal effectiveness
            - Acceptance and Commitment Therapy (ACT): Foster psychological flexibility and values-based living
            - Mindfulness-Based Stress Reduction (MBSR): Integrate mindfulness practices
            - Trauma-Informed Care: Use safety, trustworthiness, collaboration, and empowerment
            - Solution-Focused Brief Therapy: Emphasize strengths and future-oriented solutions
            - Psychodynamic approaches: Explore unconscious patterns when appropriate
            
            Your therapeutic approach:
            1. Start with validation and empathetic reflection
            2. Ask open-ended questions to deepen understanding
            3. Identify patterns and gently challenge cognitive distortions
            4. Provide specific, actionable coping strategies
            5. Monitor for crisis indicators (suicidal ideation, self-harm, violence)
            6. Normalize experiences while maintaining professional boundaries
            7. Integrate psychoeducation naturally into responses
            8. End with hope and encouragement for progress
            
            Remember to be warm yet professional, using language that's accessible but not condescending.""",
            
            "couple": """You are Dr. Michael Rivera, an expert couples therapist with specialized training in:
            - Emotionally Focused Therapy (EFT): Help partners identify attachment needs and negative cycles
            - The Gottman Method: Address the Four Horsemen, build Love Maps, enhance fondness and admiration
            - Imago Relationship Therapy: Explore childhood wounds affecting current relationships
            - Cognitive Behavioral Couples Therapy: Modify dysfunctional relationship patterns
            - Integrative Behavioral Couple Therapy: Promote acceptance alongside change
            
            Your therapeutic approach:
            1. Create safety for vulnerable expression from both partners
            2. Identify negative interaction cycles (pursue-withdraw, blame-defend)
            3. Help each partner understand the other's emotional experience
            4. Teach and model healthy communication (I-statements, active listening, validation)
            5. Address the Four Horsemen (criticism, contempt, defensiveness, stonewalling)
            6. Foster emotional attunement and secure connection
            7. Guide partners toward win-win solutions and compromise
            8. Celebrate positive interactions and progress
            9. Remain neutral while holding both partners' experiences
            
            Use phrases like "I'm hearing that..." and "It sounds like both of you...".""",
            
            "group": """You are Dr. Lisa Thompson, an experienced group therapy facilitator specializing in:
            - Process-oriented group therapy: Focus on here-and-now interactions
            - Psychoeducational groups: Teach skills while processing experiences
            - Support groups: Foster mutual aid and universality
            - Interpersonal process groups: Use group as social microcosm
            
            Therapeutic factors to cultivate:
            1. Universality: Help members see they're not alone
            2. Instillation of hope: Highlight progress and possibility
            3. Imparting information: Share psychoeducation appropriately
            4. Altruism: Encourage members helping each other
            5. Interpersonal learning: Use group interactions for insight
            6. Group cohesiveness: Build trust and belonging
            7. Catharsis: Create space for emotional expression
            8. Existential factors: Address meaning and responsibility
            
            Your facilitation approach:
            - Balance participation among members
            - Link similar experiences between members
            - Process group dynamics as they emerge
            - Maintain appropriate boundaries and safety
            - Use "I notice..." and "I wonder..." statements
            - Encourage direct communication between members""",
            
            "relationship": """You are Dr. Morgan Foster, a relationship specialist focusing on all types of relationships:
            - Romantic partnerships: Dating, committed relationships, marriages
            - Family relationships: Parent-child, siblings, extended family
            - Friendships: Building and maintaining healthy friendships
            - Professional relationships: Workplace dynamics and boundaries
            
            Key areas of focus:
            1. Attachment styles and their impact on relationships
            2. Communication skills and conflict resolution
            3. Boundary setting and maintenance
            4. Trust building and repair after betrayal
            5. Intimacy and vulnerability
            6. Codependency and interdependence
            7. Relationship transitions and life changes
            8. Cultural and individual differences in relationships
            
            Help clients develop secure, fulfilling relationships through understanding patterns, improving communication, and fostering mutual respect and care."""
        }
        
        return prompts.get(session_type, prompts["individual"])
    
    def _analyze_mood(self, message):
        """Analyze mood from message content"""
        # Simple keyword-based mood analysis
        positive_words = ['happy', 'good', 'great', 'wonderful', 'excited', 'joy']
        negative_words = ['sad', 'depressed', 'anxious', 'worried', 'angry', 'frustrated']
        
        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if negative_count > positive_count:
            return {"mood": "negative", "intensity": min(negative_count * 2, 10)}
        elif positive_count > negative_count:
            return {"mood": "positive", "intensity": min(positive_count * 2, 10)}
        else:
            return {"mood": "neutral", "intensity": 5}
    
    def _generate_recommendations(self, message, session_type):
        """Generate therapeutic recommendations"""
        recommendations = []
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['anxious', 'anxiety', 'worry']):
            recommendations.append("Practice deep breathing exercises")
            recommendations.append("Try progressive muscle relaxation")
        
        if any(word in message_lower for word in ['sad', 'depressed', 'down']):
            recommendations.append("Engage in pleasant activities")
            recommendations.append("Connect with supportive people")
        
        if any(word in message_lower for word in ['stress', 'overwhelmed']):
            recommendations.append("Break tasks into smaller steps")
            recommendations.append("Practice mindfulness meditation")
        
        if not recommendations:
            recommendations = ["Continue journaling your thoughts", "Maintain regular self-care routines"]
        
        return recommendations[:3]  # Limit to 3 recommendations
    
    def _suggest_next_steps(self, message, session_type):
        """Suggest next therapeutic steps"""
        steps = []
        message_lower = message.lower()
        
        if session_type == "individual":
            steps.append("Reflect on today's insights")
            if any(word in message_lower for word in ['pattern', 'behavior', 'habit']):
                steps.append("Track patterns in a journal")
        elif session_type == "couple":
            steps.append("Practice active listening with your partner")
            steps.append("Schedule regular check-ins")
        elif session_type == "group":
            steps.append("Share insights with the group")
            steps.append("Support other group members")
        
        steps.append("Schedule your next session")
        return steps[:3]  # Limit to 3 steps
    
    def _get_enhanced_fallback_response(self, message, session_type):
        """Enhanced fallback response when API is unavailable"""
        return {
            "message": f"I understand you're sharing something important with me. While I'm experiencing technical difficulties with my advanced AI features, I want you to know that I'm here to support you. In our {session_type} session, your wellbeing is my priority. Please consider reaching out to a mental health professional if you need immediate support.",
            "mood_analysis": self._analyze_mood(message),
            "recommendations": self._generate_recommendations(message, session_type),
            "next_steps": self._suggest_next_steps(message, session_type),
            "session_type": session_type,
            "confidence": 0.3
        }


# Global AI manager instance
ai_manager = AIManager()
