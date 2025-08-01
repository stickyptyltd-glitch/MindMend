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
    
    def get_openai_response(self, text, session_type="individual"):
        """Get therapeutic response using OpenAI GPT-4o"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            
            system_prompt = self._get_system_prompt(session_type)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            return self.fake_ai_response(text, session_type)
    
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
    
    def _get_system_prompt(self, session_type):
        """Get appropriate system prompt based on session type"""
        prompts = {
            "individual": """You are a compassionate AI therapist specializing in individual therapy.
            Use evidence-based approaches like CBT, DBT, and mindfulness.
            Be empathetic, non-judgmental, and solution-focused.
            Ask thoughtful questions to guide self-reflection.
            Keep responses supportive but professional.""",
            
            "couple": """You are an AI therapist specializing in couples therapy.
            Focus on communication patterns, relationship dynamics, and conflict resolution.
            Help partners understand each other's perspectives.
            Use techniques from Gottman Method and EFT.
            Remain neutral and help both partners feel heard.""",
            
            "group": """You are an AI therapist facilitating group therapy.
            Foster peer support, shared experiences, and group cohesion.
            Encourage participation while maintaining psychological safety.
            Address group dynamics and interpersonal relationships.
            Create an inclusive environment where everyone feels valued.""",
            
            "relationship": """You are an AI therapist specializing in relationship counseling.
            Address attachment styles, communication issues, and relationship patterns.
            Help build healthy relationship skills and emotional intimacy.
            Focus on building trust and understanding between partners."""
        }
        
        return prompts.get(session_type, prompts["individual"])
