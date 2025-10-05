
from flask import Blueprint, request, jsonify, session
from datetime import datetime, timezone
import logging
import re

crisis_bp = Blueprint('crisis', __name__, url_prefix='/api/crisis')

class CrisisInterventionSystem:
    def __init__(self):
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'not worth living', 'better off dead',
            'hurt myself', 'self harm', 'cut myself', 'overdose', 'can\'t go on',
            'hopeless', 'worthless', 'want to die', 'ending my life', 'no point',
            'harm others', 'kill someone', 'violence', 'rage', 'destroy everything'
        ]
        self.escalation_levels = {
            'low': {
                'score_range': (30, 50),
                'response': 'supportive_resources',
                'action': 'monitor_closely',
            },
            'medium': {
                'score_range': (50, 75),
                'response': 'immediate_intervention',
                'action': 'alert_supervisor',
            },
            'high': {
                'score_range': (75, 90),
                'response': 'crisis_protocol',
                'action': 'emergency_contact',
            },
            'critical': {
                'score_range': (90, 100),
                'response': 'emergency_services',
                'action': 'immediate_escalation',
            }
        }

    def analyze_crisis_risk(self, user_message, biometric_data=None, emotion_data=None, context=None):
        try:
            crisis_score = 0
            risk_factors = []
            text_risk = self._analyze_text_content(user_message)
            crisis_score += text_risk['score'] * 0.4
            risk_factors.extend(text_risk['factors'])
            if biometric_data:
                bio_risk = self._analyze_biometric_crisis_indicators(biometric_data)
                crisis_score += bio_risk['score'] * 0.3
                risk_factors.extend(bio_risk['factors'])
            if emotion_data:
                emotion_risk = self._analyze_emotional_crisis_indicators(emotion_data)
                crisis_score += emotion_risk['score'] * 0.2
                risk_factors.extend(emotion_risk['factors'])
            if context:
                context_risk = self._analyze_context_indicators(context)
                crisis_score += context_risk['score'] * 0.1
                risk_factors.extend(context_risk['factors'])
            crisis_level = self._determine_crisis_level(crisis_score)
            return {
                'crisis_score': min(crisis_score, 100),
                'crisis_level': crisis_level,
                'risk_factors': list(set(risk_factors)),
                'immediate_action_required': crisis_score >= 75,
                'escalation_protocol': self.escalation_levels[crisis_level],
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                'crisis_score': 0,
                'crisis_level': 'unknown',
                'error': str(e),
                'immediate_action_required': False
            }

    def _analyze_text_content(self, text):
        if not text:
            return {'score': 0, 'factors': []}
        text_lower = text.lower()
        score = 0
        factors = []
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                if keyword in ['suicide', 'kill myself', 'end it all', 'want to die']:
                    score += 40
                    factors.append(f"Direct crisis language: '{keyword}'")
                elif keyword in ['hurt myself', 'self harm', 'hopeless', 'worthless']:
                    score += 25
                    factors.append(f"Self-harm language: '{keyword}'")
                else:
                    score += 15
                    factors.append(f"Concerning language: '{keyword}'")
        crisis_patterns = [
            (r'can\'t (take|handle|deal with) (it|this) anymore', 20, 'Overwhelm pattern'),
            (r'nobody (cares|loves|understands) me', 15, 'Isolation pattern'),
            (r'everything is (falling apart|ruined|hopeless)', 20, 'Despair pattern'),
            (r'i (hate|despise) myself', 25, 'Self-hatred pattern')
        ]
        for pattern, points, description in crisis_patterns:
            if re.search(pattern, text_lower):
                score += points
                factors.append(description)
        if len(text) > 500 and score > 10:
            score += 10
            factors.append("Extended distressed communication")
        return {'score': min(score, 100), 'factors': factors}

    def _analyze_biometric_crisis_indicators(self, biometric_data):
        score = 0
        factors = []
        heart_rate = biometric_data.get('heart_rate', 70)
        stress_level = biometric_data.get('stress_level', 'unknown')
        if stress_level == 'critical':
            score += 30
            factors.append("Critical biometric stress levels")
        elif stress_level == 'high':
            score += 20
            factors.append("High biometric stress levels")
        if heart_rate > 130:
            score += 25
            factors.append("Extremely elevated heart rate")
        elif heart_rate < 50:
            score += 20
            factors.append("Concerning low heart rate")
        return {'score': min(score, 100), 'factors': factors}

    def _analyze_emotional_crisis_indicators(self, emotion_data):
        score = 0
        factors = []
        if not emotion_data or not emotion_data.get('emotions'):
            return {'score': 0, 'factors': []}
        emotions = emotion_data['emotions']
        for emotion in emotions:
            emotion_name = emotion.get('emotion', '')
            confidence = emotion.get('confidence', 0)
            if emotion_name == 'sad' and confidence > 0.8:
                score += 25
                factors.append("Extreme sadness detected")
            elif emotion_name == 'angry' and confidence > 0.8:
                score += 30
                factors.append("Extreme anger detected")
            elif emotion_name == 'fear' and confidence > 0.7:
                score += 20
                factors.append("High fear levels detected")
        high_confidence_emotions = [e for e in emotions if e.get('confidence', 0) > 0.6]
        if len(high_confidence_emotions) >= 3:
            score += 15
            factors.append("Emotional instability detected")
        return {'score': min(score, 100), 'factors': factors}

    def _analyze_context_indicators(self, context):
        score = 0
        factors = []
        session_type = context.get('session_type', 'individual')
        previous_crises = context.get('previous_crisis_events', 0)
        session_duration = context.get('session_duration_minutes', 0)
        if previous_crises > 0:
            score += min(previous_crises * 5, 20)
            factors.append(f"Previous crisis events: {previous_crises}")
        if session_duration > 90:
            score += 10
            factors.append("Extended session duration")
        if session_type == 'crisis':
            score += 15
            factors.append("Already in crisis session mode")
        return {'score': min(score, 100), 'factors': factors}

    def _determine_crisis_level(self, score):
        for level, config in self.escalation_levels.items():
            min_score, max_score = config['score_range']
            if min_score <= score < max_score:
                return level
        if score >= 90:
            return 'critical'
        else:
            return 'low'

crisis_system = CrisisInterventionSystem()

from flask_login import login_required

@crisis_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_crisis():
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        user_message = data.get('user_message', '')
        biometric_data = data.get('biometric_data') or session.get('latest_biometric_analysis')
        emotion_data = data.get('emotion_data') or session.get('latest_emotion_analysis')
        context = {
            'session_type': data.get('session_type', 'individual'),
            'session_duration_minutes': data.get('session_duration', 0),
            'previous_crisis_events': 0,
            'user_id': user_id
        }
        crisis_analysis = crisis_system.analyze_crisis_risk(
            user_message, biometric_data, emotion_data, context
        )
        session['latest_crisis_analysis'] = crisis_analysis
        return jsonify({
            'success': True,
            'analysis': crisis_analysis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@crisis_bp.route('/status', methods=['GET'])
@login_required
def get_crisis_status():
    try:
        latest_analysis = session.get('latest_crisis_analysis')
        status = {
            'monitoring_active': True,
            'latest_analysis': latest_analysis,
        }
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
