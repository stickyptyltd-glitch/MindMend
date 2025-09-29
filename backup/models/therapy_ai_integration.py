"""
Integration module for AI-powered therapy sessions
Connects multiple AI models with the therapy system
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import numpy as np
from models.ai_model_manager import ai_model_manager, ModelType
from models.treatment_recommender import TreatmentRecommender
from models.research_manager import research_manager

logger = logging.getLogger(__name__)

class TherapyAIIntegration:
    """Integrates AI models with therapy sessions"""
    
    def __init__(self):
        self.ai_manager = ai_model_manager
        self.treatment_recommender = TreatmentRecommender(ai_model_manager)
        self.research_manager = research_manager
        self.session_contexts = {}
        self.model_performance_tracker = {}
        
    def enhance_therapy_response(self, 
                               session_type: str,
                               user_message: str,
                               session_data: Dict[str, Any],
                               use_ensemble: bool = True) -> Dict[str, Any]:
        """Enhanced therapy response using multiple AI models"""
        
        # Extract patient profile from session
        patient_profile = self._extract_patient_profile(session_data)
        
        # Get initial diagnosis if needed
        if not session_data.get('diagnosis'):
            diagnosis = self.ai_manager.diagnose_with_ensemble(patient_profile)
            session_data['diagnosis'] = diagnosis
        else:
            diagnosis = session_data['diagnosis']
        
        # Get treatment recommendations
        if not session_data.get('treatment_plan'):
            treatment_plan = self.treatment_recommender.generate_personalized_treatment_plan(
                diagnosis,
                patient_profile,
                session_data.get('preferences', {})
            )
            session_data['treatment_plan'] = treatment_plan
        else:
            treatment_plan = session_data['treatment_plan']
        
        # Generate enhanced therapy response
        if use_ensemble:
            response = self._generate_ensemble_response(
                session_type,
                user_message,
                diagnosis,
                treatment_plan,
                session_data
            )
        else:
            response = self._generate_single_model_response(
                session_type,
                user_message,
                diagnosis,
                treatment_plan,
                session_data
            )
        
        # Enhance with research insights
        response = self._enhance_with_research(response, diagnosis)
        
        # Add recommended activities
        response['recommended_activities'] = self._get_session_activities(
            treatment_plan,
            session_data.get('completed_activities', [])
        )
        
        # Update session context
        self._update_session_context(session_data['session_id'], response)
        
        return response
    
    def _extract_patient_profile(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patient profile from session data"""
        return {
            'age': session_data.get('user_age', 30),
            'gender': session_data.get('user_gender', 'not_specified'),
            'chief_complaint': session_data.get('presenting_issue', ''),
            'symptoms': {
                'anxiety_level': session_data.get('anxiety_level', 5),
                'depression_level': session_data.get('depression_level', 5),
                'stress_level': session_data.get('stress_level', 5),
                'sleep_quality': session_data.get('sleep_quality', 5)
            },
            'behavioral_data': {
                'social_withdrawal': session_data.get('social_withdrawal', 0),
                'activity_level': session_data.get('activity_level', 5),
                'appetite_changes': session_data.get('appetite_changes', 0)
            },
            'assessment_scores': {
                'phq9_score': session_data.get('phq9_score', 0),
                'gad7_score': session_data.get('gad7_score', 0),
                'pss_score': session_data.get('perceived_stress_score', 0)
            },
            'session_history': len(session_data.get('session_history', [])),
            'therapy_experience': session_data.get('therapy_experience', 'none'),
            'motivation_level': session_data.get('motivation_level', 7)
        }
    
    def _generate_ensemble_response(self,
                                  session_type: str,
                                  user_message: str,
                                  diagnosis: Dict[str, Any],
                                  treatment_plan: Any,
                                  session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using multiple AI models"""
        
        responses = []
        model_weights = {}
        
        # Prepare context for AI models
        context = {
            'session_type': session_type,
            'user_message': user_message,
            'diagnosis': diagnosis,
            'treatment_modality': treatment_plan.primary_modality.value,
            'session_number': session_data.get('session_number', 1),
            'previous_responses': session_data.get('response_history', [])[-3:]  # Last 3 exchanges
        }
        
        # Get responses from different models
        active_models = self.ai_manager.active_models[:3]  # Use top 3 models
        
        for model_name in active_models:
            try:
                model_config = self.ai_manager.models[model_name]
                
                # Generate prompt based on model specialization
                prompt = self._create_therapy_prompt(context, model_config.specialization)
                
                # Get response based on model type
                if model_config.type == ModelType.OPENAI_GPT:
                    response = self._get_openai_therapy_response(prompt, model_config)
                elif model_config.type == ModelType.OLLAMA:
                    response = self._get_ollama_therapy_response(prompt, model_config)
                else:
                    continue
                
                if response:
                    responses.append(response)
                    model_weights[model_name] = model_config.accuracy_score or 0.8
                    
            except Exception as e:
                logger.error(f"Error getting response from {model_name}: {str(e)}")
        
        # Aggregate responses
        if not responses:
            return self._get_fallback_therapy_response(context)
        
        # Synthesize best response
        final_response = self._synthesize_therapy_responses(responses, model_weights)
        
        return final_response
    
    def _create_therapy_prompt(self, context: Dict[str, Any], specialization: str) -> str:
        """Create specialized therapy prompt"""
        
        base_prompt = f"""
        You are an expert therapist specializing in {context['treatment_modality']} therapy.
        This is session {context['session_number']} with a patient diagnosed with {context['diagnosis']['primary_diagnosis']}.
        
        Session Type: {context['session_type']}
        
        Patient Message: {context['user_message']}
        
        Please provide a therapeutic response that:
        1. Validates the patient's feelings
        2. Uses appropriate {context['treatment_modality']} techniques
        3. Provides practical guidance
        4. Maintains professional boundaries
        5. Shows empathy and understanding
        """
        
        # Add specialization-specific instructions
        if specialization == "mental_health_assessment":
            base_prompt += "\n\nFocus on assessment and understanding the patient's current state."
        elif specialization == "therapy_recommendations":
            base_prompt += "\n\nInclude specific therapeutic exercises or homework."
        elif specialization == "general_therapy":
            base_prompt += "\n\nProvide a balanced response addressing both emotional and practical aspects."
        
        return base_prompt
    
    def _get_openai_therapy_response(self, prompt: str, config: Any) -> Dict[str, Any]:
        """Get therapy response from OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=config.api_key)
            
            response = client.chat.completions.create(
                model=config.name,
                messages=[
                    {"role": "system", "content": "You are a compassionate and professional therapist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            return {
                'text': response.choices[0].message.content,
                'model': config.name,
                'confidence': 0.9
            }
            
        except Exception as e:
            logger.error(f"OpenAI therapy response error: {str(e)}")
            return None
    
    def _get_ollama_therapy_response(self, prompt: str, config: Any) -> Dict[str, Any]:
        """Get therapy response from Ollama"""
        try:
            import requests
            
            response = requests.post(
                config.endpoint,
                json={
                    "model": config.name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'text': result.get('response', ''),
                    'model': config.name,
                    'confidence': 0.85
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Ollama therapy response error: {str(e)}")
            return None
    
    def _synthesize_therapy_responses(self, 
                                    responses: List[Dict[str, Any]], 
                                    weights: Dict[str, float]) -> Dict[str, Any]:
        """Synthesize multiple AI responses into one coherent response"""
        
        # Extract key elements from each response
        validations = []
        techniques = []
        guidance = []
        
        for response in responses:
            text = response['text']
            model = response['model']
            weight = weights.get(model, 0.8)
            
            # Simple extraction (in production, use NLP)
            sections = text.split('\n\n')
            if sections:
                validations.append((sections[0], weight))
                if len(sections) > 1:
                    techniques.append((sections[1], weight))
                if len(sections) > 2:
                    guidance.append((sections[2], weight))
        
        # Select best elements based on weights
        best_validation = max(validations, key=lambda x: x[1])[0] if validations else ""
        best_technique = max(techniques, key=lambda x: x[1])[0] if techniques else ""
        best_guidance = max(guidance, key=lambda x: x[1])[0] if guidance else ""
        
        # Combine into final response
        final_text = f"{best_validation}\n\n{best_technique}\n\n{best_guidance}".strip()
        
        # Calculate aggregate confidence
        total_confidence = sum(r['confidence'] * weights.get(r['model'], 0.8) for r in responses)
        avg_confidence = total_confidence / len(responses) if responses else 0.7
        
        return {
            'response': final_text,
            'confidence': avg_confidence,
            'models_used': [r['model'] for r in responses],
            'synthesis_method': 'weighted_selection',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _enhance_with_research(self, 
                             response: Dict[str, Any], 
                             diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance response with research insights"""
        
        # Get relevant research insights
        condition = diagnosis.get('primary_diagnosis', '').lower()
        
        # Search for relevant research
        research_results = self.research_manager.search_research(
            f"{condition} treatment effectiveness",
            category='treatment'
        )
        
        if research_results:
            # Add research-backed insights
            insights = []
            for paper in research_results[:2]:  # Top 2 relevant papers
                insights.append({
                    'title': paper.get('title', ''),
                    'key_finding': paper.get('abstract', '')[:200] + '...',
                    'relevance_score': paper.get('relevance_score', 0.8)
                })
            
            response['research_insights'] = insights
            response['evidence_based'] = True
        
        # Get early diagnosis indicators if relevant
        if 'early' in condition or 'risk' in diagnosis.get('risk_factors', []):
            indicators = self.research_manager.get_early_diagnosis_indicators(condition)
            if indicators:
                response['early_indicators'] = indicators['indicators'][:3]
        
        return response
    
    def _get_session_activities(self, 
                              treatment_plan: Any,
                              completed_activities: List[str]) -> List[Dict[str, Any]]:
        """Get recommended activities for this session"""
        
        # Filter out completed activities
        available_activities = [
            a for a in treatment_plan.activities 
            if a['name'] not in completed_activities
        ]
        
        # Prioritize by multiple factors
        for activity in available_activities:
            score = 0
            
            # Priority score
            if activity.get('priority') == 'high':
                score += 3
            elif activity.get('priority') == 'medium':
                score += 2
            else:
                score += 1
            
            # Effectiveness score
            score += activity.get('effectiveness', 0.8) * 2
            
            # Difficulty appropriate for stage
            if len(completed_activities) < 3 and activity.get('difficulty') == 'easy':
                score += 1
            elif len(completed_activities) >= 3 and activity.get('difficulty') == 'moderate':
                score += 1
            
            activity['recommendation_score'] = score
        
        # Sort by score and return top 3
        available_activities.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return available_activities[:3]
    
    def _update_session_context(self, session_id: str, response: Dict[str, Any]):
        """Update session context for continuity"""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {
                'created': datetime.utcnow(),
                'exchanges': []
            }
        
        self.session_contexts[session_id]['exchanges'].append({
            'timestamp': datetime.utcnow(),
            'response': response['response'][:200],  # Store summary
            'confidence': response.get('confidence', 0.7),
            'models_used': response.get('models_used', [])
        })
        
        # Keep only last 10 exchanges
        self.session_contexts[session_id]['exchanges'] = \
            self.session_contexts[session_id]['exchanges'][-10:]
    
    def _generate_single_model_response(self,
                                      session_type: str,
                                      user_message: str,
                                      diagnosis: Dict[str, Any],
                                      treatment_plan: Any,
                                      session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using a single model (fallback)"""
        
        # Use primary OpenAI model
        context = {
            'session_type': session_type,
            'user_message': user_message,
            'diagnosis': diagnosis,
            'treatment_modality': treatment_plan.primary_modality.value
        }
        
        prompt = self._create_therapy_prompt(context, "general_therapy")
        
        # Try OpenAI first
        for model_name in self.ai_manager.active_models:
            config = self.ai_manager.models[model_name]
            if config.type == ModelType.OPENAI_GPT:
                response = self._get_openai_therapy_response(prompt, config)
                if response:
                    return {
                        'response': response['text'],
                        'confidence': response['confidence'],
                        'models_used': [model_name],
                        'timestamp': datetime.utcnow().isoformat()
                    }
        
        # Fallback
        return self._get_fallback_therapy_response(context)
    
    def _get_fallback_therapy_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback therapy response"""
        
        responses = {
            'default': "I hear what you're sharing, and I appreciate your openness. Let's explore this together. Can you tell me more about how this has been affecting your daily life?",
            'anxiety': "It sounds like you're experiencing some anxiety. That's completely understandable. Let's work on some grounding techniques that might help you feel more centered.",
            'depression': "Thank you for sharing that with me. Depression can make everything feel overwhelming. Let's focus on small, manageable steps that can help you feel a bit better.",
            'stress': "I can hear the stress in what you're sharing. Stress affects us all differently. Let's identify what's within your control and work on strategies to manage those areas."
        }
        
        # Select appropriate response
        condition = context.get('diagnosis', {}).get('primary_diagnosis', '').lower()
        
        for key, response in responses.items():
            if key in condition:
                selected_response = response
                break
        else:
            selected_response = responses['default']
        
        return {
            'response': selected_response,
            'confidence': 0.6,
            'models_used': ['fallback'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def analyze_session_effectiveness(self, 
                                    session_id: str,
                                    session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the effectiveness of a therapy session"""
        
        # Get session context
        context = self.session_contexts.get(session_id, {})
        
        # Calculate metrics
        metrics = {
            'engagement_score': self._calculate_engagement_score(session_data),
            'therapeutic_alliance': self._assess_therapeutic_alliance(session_data),
            'technique_utilization': self._analyze_technique_usage(context),
            'progress_indicators': self._identify_progress_indicators(session_data),
            'areas_for_improvement': []
        }
        
        # Identify areas for improvement
        if metrics['engagement_score'] < 0.6:
            metrics['areas_for_improvement'].append({
                'area': 'engagement',
                'suggestion': 'Consider more interactive exercises or shorter response times'
            })
        
        if metrics['therapeutic_alliance'] < 0.7:
            metrics['areas_for_improvement'].append({
                'area': 'rapport',
                'suggestion': 'Focus more on validation and empathy in responses'
            })
        
        # Model performance tracking
        if 'models_used' in context:
            for model in context['models_used']:
                if model not in self.model_performance_tracker:
                    self.model_performance_tracker[model] = []
                
                self.model_performance_tracker[model].append({
                    'session_id': session_id,
                    'effectiveness': metrics['engagement_score'],
                    'timestamp': datetime.utcnow()
                })
        
        return metrics
    
    def _calculate_engagement_score(self, session_data: Dict[str, Any]) -> float:
        """Calculate patient engagement score"""
        score = 0.5  # Base score
        
        # Message length and frequency
        messages = session_data.get('messages', [])
        if messages:
            avg_length = np.mean([len(m.get('content', '')) for m in messages])
            if avg_length > 50:
                score += 0.1
            if avg_length > 100:
                score += 0.1
        
        # Response time
        response_times = session_data.get('response_times', [])
        if response_times:
            avg_response_time = np.mean(response_times)
            if avg_response_time < 60:  # Less than 1 minute
                score += 0.1
        
        # Activity completion
        if session_data.get('activities_completed', 0) > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_therapeutic_alliance(self, session_data: Dict[str, Any]) -> float:
        """Assess therapeutic alliance quality"""
        alliance_score = 0.7  # Base score
        
        # Check for positive indicators
        positive_indicators = ['thank', 'helpful', 'understand', 'appreciate', 'better']
        messages = ' '.join([m.get('content', '') for m in session_data.get('messages', [])])
        
        for indicator in positive_indicators:
            if indicator in messages.lower():
                alliance_score += 0.05
        
        # Check for negative indicators
        negative_indicators = ['confused', 'frustrated', "don't understand", 'not helping']
        for indicator in negative_indicators:
            if indicator in messages.lower():
                alliance_score -= 0.1
        
        return max(0, min(alliance_score, 1.0))
    
    def _analyze_technique_usage(self, context: Dict[str, Any]) -> Dict[str, int]:
        """Analyze therapeutic techniques used"""
        techniques = {
            'validation': 0,
            'reframing': 0,
            'skills_teaching': 0,
            'homework_assignment': 0,
            'mindfulness': 0
        }
        
        # Simple keyword analysis (in production, use NLP)
        exchanges = context.get('exchanges', [])
        for exchange in exchanges:
            response_text = exchange.get('response', '').lower()
            
            if any(word in response_text for word in ['understand', 'hear', 'valid']):
                techniques['validation'] += 1
            if any(word in response_text for word in ['another way', 'perspective', 'reframe']):
                techniques['reframing'] += 1
            if any(word in response_text for word in ['practice', 'exercise', 'technique']):
                techniques['skills_teaching'] += 1
            if any(word in response_text for word in ['homework', 'practice this week', 'try']):
                techniques['homework_assignment'] += 1
            if any(word in response_text for word in ['mindful', 'present', 'breathing']):
                techniques['mindfulness'] += 1
        
        return techniques
    
    def _identify_progress_indicators(self, session_data: Dict[str, Any]) -> List[str]:
        """Identify indicators of therapeutic progress"""
        indicators = []
        
        # Mood improvement
        if session_data.get('mood_start') and session_data.get('mood_end'):
            if session_data['mood_end'] > session_data['mood_start']:
                indicators.append('mood_improvement')
        
        # Insight development
        insight_keywords = ['realize', 'understand now', 'makes sense', 'see how']
        messages = ' '.join([m.get('content', '') for m in session_data.get('messages', [])])
        
        if any(keyword in messages.lower() for keyword in insight_keywords):
            indicators.append('insight_development')
        
        # Commitment to change
        commitment_keywords = ['will try', 'going to', 'plan to', 'commit']
        if any(keyword in messages.lower() for keyword in commitment_keywords):
            indicators.append('commitment_to_change')
        
        # Skill application
        if 'practiced' in messages.lower() or 'used the technique' in messages.lower():
            indicators.append('skill_application')
        
        return indicators

# Create singleton instance
therapy_ai_integration = TherapyAIIntegration()