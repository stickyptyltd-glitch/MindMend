
from flask import Blueprint, request, jsonify, session, render_template_string
from datetime import datetime, timezone
import hashlib

avatar_bp = Blueprint('avatar', __name__, url_prefix='/api/avatar')

class SpeakingAvatarSystem:
    def __init__(self):
        self.avatar_personalities = {
            'compassionate': {
                'voice_profile': 'warm_female',
                'speaking_pace': 'moderate',
                'emotion_expression': 'empathetic',
                'visual_style': 'professional_caring',
                'greeting': "Hello, I'm here to support you on your journey. How are you feeling today?"
            },
            'professional': {
                'voice_profile': 'neutral_professional',
                'speaking_pace': 'measured',
                'emotion_expression': 'composed',
                'visual_style': 'clinical_professional',
                'greeting': "Good day. I'm your therapeutic AI assistant. What would you like to focus on in our session?"
            },
            'encouraging': {
                'voice_profile': 'upbeat_encouraging',
                'speaking_pace': 'energetic',
                'emotion_expression': 'motivational',
                'visual_style': 'bright_optimistic',
                'greeting': "Hi there! I'm excited to work with you today. You've taken a positive step by being here!"
            },
            'calming': {
                'voice_profile': 'soft_soothing',
                'speaking_pace': 'slow_gentle',
                'emotion_expression': 'peaceful',
                'visual_style': 'serene_minimal',
                'greeting': "Welcome to this peaceful space. Take a deep breath... I'm here when you're ready to begin."
            }
        }
        self.voice_synthesis_settings = {
            'speech_rate': 1.0,
            'voice_pitch': 0.0,
            'voice_volume': 0.8,
        }

    def generate_avatar_response(self, user_message, session_context, avatar_personality='compassionate'):
        therapy_response = "This is a mock therapy response."
        animation_type = self._determine_animation_type(therapy_response, user_message)
        speech_data = self._prepare_speech_synthesis(
            text=therapy_response,
            personality=avatar_personality,
            emotion_context=session_context.get('emotion_analysis', {})
        )
        visual_state = self._generate_visual_state(
            animation_type=animation_type,
            personality=avatar_personality,
            speech_duration=speech_data['estimated_duration']
        )
        lip_sync_data = self._generate_lip_sync_data(therapy_response)
        return {
            'success': True,
            'response_text': therapy_response,
            'speech_data': speech_data,
            'visual_state': visual_state,
            'lip_sync_data': lip_sync_data,
            'animation_type': animation_type,
            'personality': avatar_personality,
            'interaction_id': self._generate_interaction_id(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def _determine_animation_type(self, response_text, user_message):
        response_lower = response_text.lower()
        user_lower = user_message.lower()
        crisis_keywords = ['crisis', 'emergency', 'hurt', 'harm', 'suicide', 'help me']
        if any(keyword in user_lower for keyword in crisis_keywords):
            return 'empathetic_response'
        positive_keywords = ['great', 'wonderful', 'excellent', 'progress', 'achievement', 'success']
        if any(keyword in response_lower for keyword in positive_keywords):
            return 'encouraging_response'
        if '?' in response_text:
            return 'listening'
        return 'speaking'

    def _prepare_speech_synthesis(self, text, personality, emotion_context):
        personality_config = self.avatar_personalities.get(personality, self.avatar_personalities['compassionate'])
        speech_rate = self.voice_synthesis_settings['speech_rate']
        voice_pitch = self.voice_synthesis_settings['voice_pitch']
        voice_volume = self.voice_synthesis_settings['voice_volume']
        if emotion_context:
            dominant_emotion = emotion_context.get('dominant_emotion', {}).get('emotion', 'neutral')
            if dominant_emotion == 'sad':
                speech_rate *= 0.85
                voice_pitch -= 0.1
            elif dominant_emotion == 'angry':
                speech_rate *= 0.9
                voice_volume *= 0.9
            elif dominant_emotion == 'happy':
                speech_rate *= 1.1
                voice_pitch += 0.05
        word_count = len(text.split())
        estimated_duration = (word_count / 150) * 60
        return {
            'text': text,
            'voice_profile': personality_config['voice_profile'],
            'speech_rate': speech_rate,
            'voice_pitch': voice_pitch,
            'voice_volume': voice_volume,
            'speaking_pace': personality_config['speaking_pace'],
            'estimated_duration': estimated_duration,
            'synthesis_id': hashlib.md5(text.encode()).hexdigest()
        }

    def _generate_visual_state(self, animation_type, personality, speech_duration):
        return {
            'animation_type': animation_type,
            'animation_duration': speech_duration,
        }

    def _generate_lip_sync_data(self, text):
        return {
            'timeline': [],
            'total_duration': 0,
            'sync_accuracy': 'simplified'
        }

    def _generate_interaction_id(self):
        timestamp = str(int(datetime.now().timestamp() * 1000))
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

avatar_system = SpeakingAvatarSystem()

from flask_login import login_required

@avatar_bp.route('/speak', methods=['POST'])
@login_required
def speak():
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
        session_context = {
            'session_type': data.get('session_type', 'individual'),
            'session_id': session.get('current_session_id'),
            'user_id': user_id,
            'biometric_analysis': session.get('latest_biometric_analysis', {}),
            'emotion_analysis': session.get('latest_emotion_analysis', {}),
            'crisis_analysis': session.get('latest_crisis_analysis', {})
        }
        avatar_personality = data.get('personality', 'compassionate')
        avatar_response = avatar_system.generate_avatar_response(
            user_message=user_message,
            session_context=session_context,
            avatar_personality=avatar_personality
        )
        session['latest_avatar_response'] = avatar_response
        return jsonify(avatar_response)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@avatar_bp.route('/personality', methods=['POST'])
@login_required
def set_avatar_personality():
    try:
        data = request.get_json()
        personality = data.get('personality', 'compassionate')
        if personality not in avatar_system.avatar_personalities:
            return jsonify({'success': False, 'error': 'Invalid personality type'}), 400
        session['avatar_personality'] = personality
        personality_config = avatar_system.avatar_personalities[personality]
        return jsonify({
            'success': True,
            'personality': personality,
            'config': personality_config,
            'greeting': personality_config['greeting']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@avatar_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def avatar_settings():
    try:
        if request.method == 'GET':
            current_settings = {
                'personality': session.get('avatar_personality', 'compassionate'),
                'voice_settings': avatar_system.voice_synthesis_settings.copy(),
                'available_personalities': list(avatar_system.avatar_personalities.keys()),
            }
            return jsonify({
                'success': True,
                'settings': current_settings
            })
        else:
            data = request.get_json()
            if 'voice_settings' in data:
                voice_updates = data['voice_settings']
                for key, value in voice_updates.items():
                    if key in avatar_system.voice_synthesis_settings:
                        avatar_system.voice_synthesis_settings[key] = value
            if 'personality' in data:
                personality = data['personality']
                if personality in avatar_system.avatar_personalities:
                    session['avatar_personality'] = personality
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully',
                'updated_settings': {
                    'personality': session.get('avatar_personality', 'compassionate'),
                    'voice_settings': avatar_system.voice_synthesis_settings
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
