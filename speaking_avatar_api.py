"""
🎙️ Speaking Avatar API for Stage 3 MindMend Platform
==================================================
AI-powered speaking avatar with real-time text-to-speech and visual feedback
"""

from flask import Blueprint, request, jsonify, session, render_template_string
from datetime import datetime, timezone
import json
import base64
import hashlib
import logging
import os
from models.therapy_ai_integration import therapy_ai_integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

avatar_bp = Blueprint('avatar', __name__, url_prefix='/api/avatar')

class SpeakingAvatarSystem:
    """Advanced speaking avatar system for immersive therapy"""
    
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
            'pronunciation_emphasis': True,
            'emotion_modulation': True,
            'background_noise_reduction': True
        }
        
        self.avatar_animations = {
            'idle': {
                'mouth': 'closed_slight_smile',
                'eyes': 'attentive_gaze',
                'head_position': 'centered',
                'breathing': 'subtle_chest_movement'
            },
            'speaking': {
                'mouth': 'synchronized_lip_sync',
                'eyes': 'engaged_eye_contact',
                'head_position': 'slight_forward_lean',
                'gestures': 'supportive_hand_movements'
            },
            'listening': {
                'mouth': 'relaxed_closed',
                'eyes': 'focused_attention',
                'head_position': 'slight_tilt',
                'body_language': 'open_receptive'
            },
            'empathetic_response': {
                'mouth': 'concerned_expression',
                'eyes': 'compassionate_gaze',
                'head_position': 'forward_caring',
                'gestures': 'gentle_supportive'
            },
            'encouraging_response': {
                'mouth': 'warm_smile',
                'eyes': 'bright_encouraging',
                'head_position': 'positive_nod',
                'gestures': 'uplifting_movements'
            }
        }
        
        # Speech synthesis queue for smoother delivery
        self.speech_queue = []
        self.current_speech_id = None
        
    def generate_avatar_response(self, user_message, session_context, avatar_personality='compassionate'):
        """Generate comprehensive avatar response with speech and animation"""
        try:
            # Get AI therapy response
            therapy_response = therapy_ai_integration.get_ai_response(
                session_type=session_context.get('session_type', 'individual'),
                user_message=user_message,
                session_data=session_context
            )
            
            # Analyze response for avatar animation
            animation_type = self._determine_animation_type(therapy_response, user_message)
            
            # Generate speech synthesis data
            speech_data = self._prepare_speech_synthesis(
                text=therapy_response,
                personality=avatar_personality,
                emotion_context=session_context.get('emotion_analysis', {})
            )
            
            # Create avatar visual state
            visual_state = self._generate_visual_state(
                animation_type=animation_type,
                personality=avatar_personality,
                speech_duration=speech_data['estimated_duration']
            )
            
            # Generate lip sync data
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
            
        except Exception as e:
            logger.error(f"Error generating avatar response: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_response': self._get_fallback_response(avatar_personality)
            }
    
    def _determine_animation_type(self, response_text, user_message):
        """Determine appropriate animation based on content analysis"""
        response_lower = response_text.lower()
        user_lower = user_message.lower()
        
        # Crisis or distress indicators
        crisis_keywords = ['crisis', 'emergency', 'hurt', 'harm', 'suicide', 'help me']
        if any(keyword in user_lower for keyword in crisis_keywords):
            return 'empathetic_response'
        
        # Positive/encouraging content
        positive_keywords = ['great', 'wonderful', 'excellent', 'progress', 'achievement', 'success']
        if any(keyword in response_lower for keyword in positive_keywords):
            return 'encouraging_response'
        
        # Questioning/exploring content
        if '?' in response_text:
            return 'listening'
        
        # Default speaking animation
        return 'speaking'
    
    def _prepare_speech_synthesis(self, text, personality, emotion_context):
        """Prepare text-to-speech synthesis parameters"""
        personality_config = self.avatar_personalities.get(personality, self.avatar_personalities['compassionate'])
        
        # Adjust speech parameters based on emotion context
        speech_rate = self.voice_synthesis_settings['speech_rate']
        voice_pitch = self.voice_synthesis_settings['voice_pitch']
        voice_volume = self.voice_synthesis_settings['voice_volume']
        
        if emotion_context:
            dominant_emotion = emotion_context.get('dominant_emotion', {}).get('emotion', 'neutral')
            
            if dominant_emotion == 'sad':
                speech_rate *= 0.85  # Slower for sad emotions
                voice_pitch -= 0.1   # Lower pitch for empathy
            elif dominant_emotion == 'angry':
                speech_rate *= 0.9   # Slightly slower to be calming
                voice_volume *= 0.9  # Softer volume
            elif dominant_emotion == 'happy':
                speech_rate *= 1.1   # Slightly faster for positive energy
                voice_pitch += 0.05  # Slightly higher pitch
        
        # Estimate speech duration (rough calculation: ~150 words per minute average)
        word_count = len(text.split())
        estimated_duration = (word_count / 150) * 60  # seconds
        
        # Break text into manageable chunks for better synthesis
        text_chunks = self._break_text_into_chunks(text)
        
        return {
            'text': text,
            'text_chunks': text_chunks,
            'voice_profile': personality_config['voice_profile'],
            'speech_rate': speech_rate,
            'voice_pitch': voice_pitch,
            'voice_volume': voice_volume,
            'speaking_pace': personality_config['speaking_pace'],
            'estimated_duration': estimated_duration,
            'synthesis_id': hashlib.md5(text.encode()).hexdigest()
        }
    
    def _break_text_into_chunks(self, text, max_chunk_length=100):
        """Break text into smaller chunks for better TTS synthesis"""
        import re
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence exceeds max length, start new chunk
            if len(current_chunk) + len(sentence) > max_chunk_length and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _generate_visual_state(self, animation_type, personality, speech_duration):
        """Generate avatar visual state and animation parameters"""
        personality_config = self.avatar_personalities.get(personality, self.avatar_personalities['compassionate'])
        animation_config = self.avatar_animations.get(animation_type, self.avatar_animations['speaking'])
        
        return {
            'personality_style': personality_config['visual_style'],
            'emotion_expression': personality_config['emotion_expression'],
            'animation_type': animation_type,
            'animation_duration': speech_duration,
            'facial_expression': {
                'mouth': animation_config['mouth'],
                'eyes': animation_config['eyes'],
                'head_position': animation_config['head_position']
            },
            'body_language': animation_config.get('body_language', 'neutral'),
            'gestures': animation_config.get('gestures', 'minimal'),
            'background_setting': self._get_background_setting(personality),
            'lighting_mood': self._get_lighting_mood(animation_type)
        }
    
    def _generate_lip_sync_data(self, text):
        """Generate lip synchronization data for realistic speech animation"""
        # Simplified phoneme mapping for lip sync
        phoneme_mapping = {
            'a': 'open_wide',
            'e': 'open_medium', 
            'i': 'closed_smile',
            'o': 'rounded_open',
            'u': 'rounded_closed',
            'm': 'lips_together',
            'p': 'lips_together',
            'b': 'lips_together',
            'f': 'lower_lip_teeth',
            'v': 'lower_lip_teeth',
            's': 'teeth_together',
            'z': 'teeth_together',
            'th': 'tongue_teeth',
            'l': 'tongue_tip',
            'n': 'tongue_tip',
            't': 'tongue_tip',
            'd': 'tongue_tip'
        }
        
        # Generate simple lip sync timeline
        words = text.split()
        lip_sync_timeline = []
        current_time = 0
        
        for word in words:
            word_duration = len(word) * 0.1  # Rough timing
            
            # Analyze phonemes in word (simplified)
            dominant_mouth_shape = 'neutral'
            for char in word.lower():
                if char in phoneme_mapping:
                    dominant_mouth_shape = phoneme_mapping[char]
                    break
            
            lip_sync_timeline.append({
                'start_time': current_time,
                'end_time': current_time + word_duration,
                'mouth_shape': dominant_mouth_shape,
                'word': word
            })
            
            current_time += word_duration + 0.1  # Brief pause between words
        
        return {
            'timeline': lip_sync_timeline,
            'total_duration': current_time,
            'sync_accuracy': 'simplified'  # In production, use advanced phoneme analysis
        }
    
    def _get_background_setting(self, personality):
        """Get appropriate background setting for personality"""
        settings = {
            'compassionate': 'warm_office_natural_light',
            'professional': 'clinical_office_bright_light',
            'encouraging': 'vibrant_space_energetic',
            'calming': 'zen_garden_soft_lighting'
        }
        return settings.get(personality, 'neutral_office')
    
    def _get_lighting_mood(self, animation_type):
        """Get appropriate lighting mood for animation type"""
        moods = {
            'speaking': 'natural_balanced',
            'listening': 'attentive_focused',
            'empathetic_response': 'warm_supportive',
            'encouraging_response': 'bright_uplifting'
        }
        return moods.get(animation_type, 'natural_balanced')
    
    def _generate_interaction_id(self):
        """Generate unique interaction ID"""
        timestamp = str(int(datetime.now().timestamp() * 1000))
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _get_fallback_response(self, personality):
        """Get fallback response when system fails"""
        fallbacks = {
            'compassionate': "I'm here to listen and support you. Please feel free to share what's on your mind.",
            'professional': "I apologize for the technical difficulty. Let's continue our session. How can I assist you?",
            'encouraging': "Even with a small hiccup, we're making progress! What would you like to explore next?",
            'calming': "Let's take a moment to breathe together. When you're ready, please continue..."
        }
        return fallbacks.get(personality, "I'm here to help. Please let me know how I can support you today.")

# Initialize avatar system
avatar_system = SpeakingAvatarSystem()

@avatar_bp.route('/speak', methods=['POST'])
def generate_avatar_speech():
    """Generate avatar speech response with visual animation"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
        
        # Get session context
        session_context = {
            'session_type': data.get('session_type', 'individual'),
            'session_id': session.get('current_session_id'),
            'user_id': user_id,
            'biometric_analysis': session.get('latest_biometric_analysis', {}),
            'emotion_analysis': session.get('latest_emotion_analysis', {}),
            'crisis_analysis': session.get('latest_crisis_analysis', {})
        }
        
        # Avatar personality preference
        avatar_personality = data.get('personality', 'compassionate')
        
        # Generate avatar response
        avatar_response = avatar_system.generate_avatar_response(
            user_message=user_message,
            session_context=session_context,
            avatar_personality=avatar_personality
        )
        
        # Store in session for reference
        session['latest_avatar_response'] = avatar_response
        
        logger.info(f"🎙️ Avatar speech generated for user {user_id}: {len(user_message)} chars -> {len(avatar_response.get('response_text', '')) if avatar_response.get('success') else 0} chars")
        
        return jsonify(avatar_response)
        
    except Exception as e:
        logger.error(f"❌ Error generating avatar speech: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@avatar_bp.route('/personality', methods=['POST'])
def set_avatar_personality():
    """Set avatar personality for session"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        personality = data.get('personality', 'compassionate')
        if personality not in avatar_system.avatar_personalities:
            return jsonify({'success': False, 'error': 'Invalid personality type'}), 400
        
        # Store personality preference
        session['avatar_personality'] = personality
        
        # Get personality configuration
        personality_config = avatar_system.avatar_personalities[personality]
        
        logger.info(f"🎭 Avatar personality set to '{personality}' for user {user_id}")
        
        return jsonify({
            'success': True,
            'personality': personality,
            'config': personality_config,
            'greeting': personality_config['greeting']
        })
        
    except Exception as e:
        logger.error(f"❌ Error setting avatar personality: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@avatar_bp.route('/settings', methods=['GET', 'POST'])
def avatar_settings():
    """Get or update avatar voice and visual settings"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        if request.method == 'GET':
            # Return current settings
            current_settings = {
                'personality': session.get('avatar_personality', 'compassionate'),
                'voice_settings': avatar_system.voice_synthesis_settings.copy(),
                'available_personalities': list(avatar_system.avatar_personalities.keys()),
                'available_animations': list(avatar_system.avatar_animations.keys())
            }
            
            return jsonify({
                'success': True,
                'settings': current_settings
            })
        
        else:  # POST - update settings
            data = request.get_json()
            
            # Update voice settings if provided
            if 'voice_settings' in data:
                voice_updates = data['voice_settings']
                for key, value in voice_updates.items():
                    if key in avatar_system.voice_synthesis_settings:
                        avatar_system.voice_synthesis_settings[key] = value
            
            # Update personality if provided
            if 'personality' in data:
                personality = data['personality']
                if personality in avatar_system.avatar_personalities:
                    session['avatar_personality'] = personality
            
            logger.info(f"🔧 Avatar settings updated for user {user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Settings updated successfully',
                'updated_settings': {
                    'personality': session.get('avatar_personality', 'compassionate'),
                    'voice_settings': avatar_system.voice_synthesis_settings
                }
            })
        
    except Exception as e:
        logger.error(f"❌ Error managing avatar settings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@avatar_bp.route('/status', methods=['GET'])
def get_avatar_status():
    """Get current avatar system status"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        latest_response = session.get('latest_avatar_response')
        
        status = {
            'active': True,
            'current_personality': session.get('avatar_personality', 'compassionate'),
            'voice_synthesis_available': True,
            'animation_system_active': True,
            'latest_interaction': latest_response['interaction_id'] if latest_response and latest_response.get('success') else None,
            'speech_queue_length': len(avatar_system.speech_queue),
            'system_capabilities': {
                'text_to_speech': True,
                'lip_synchronization': True,
                'emotion_responsive_animation': True,
                'personality_adaptation': True,
                'real_time_synthesis': True
            }
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting avatar status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@avatar_bp.route('/demo', methods=['GET'])
def avatar_demo_page():
    """Demo page for avatar system"""
    demo_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MindMend Speaking Avatar Demo</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 30px;
                backdrop-filter: blur(10px);
            }
            .avatar-container {
                display: flex;
                gap: 30px;
                align-items: flex-start;
            }
            .avatar-visual {
                flex: 1;
                background: rgba(255,255,255,0.2);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                min-height: 400px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .avatar-face {
                font-size: 120px;
                margin-bottom: 20px;
            }
            .controls {
                flex: 1;
                background: rgba(255,255,255,0.2);
                border-radius: 15px;
                padding: 20px;
            }
            .control-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input, select, textarea, button {
                width: 100%;
                padding: 10px;
                border: none;
                border-radius: 5px;
                margin-bottom: 10px;
                font-size: 14px;
            }
            button {
                background: #4CAF50;
                color: white;
                cursor: pointer;
                font-weight: bold;
            }
            button:hover {
                background: #45a049;
            }
            .personality-btn {
                display: inline-block;
                width: auto;
                margin: 5px;
                padding: 8px 16px;
                background: rgba(255,255,255,0.3);
                border: 2px solid transparent;
            }
            .personality-btn.active {
                border-color: #4CAF50;
                background: rgba(76, 175, 80, 0.3);
            }
            .status {
                background: rgba(0,0,0,0.3);
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                font-family: monospace;
            }
            .speech-text {
                background: rgba(255,255,255,0.9);
                color: #333;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                max-height: 200px;
                overflow-y: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ MindMend Speaking Avatar Demo</h1>
            <p>Experience the advanced AI-powered speaking avatar system with real-time text-to-speech and emotion-responsive animations.</p>
            
            <div class="avatar-container">
                <div class="avatar-visual">
                    <div class="avatar-face" id="avatar-face">😊</div>
                    <h3 id="avatar-status">Ready to speak</h3>
                    <div id="speech-text" class="speech-text" style="display:none;"></div>
                </div>
                
                <div class="controls">
                    <div class="control-group">
                        <label>Avatar Personality:</label>
                        <button class="personality-btn active" onclick="setPersonality('compassionate')">Compassionate</button>
                        <button class="personality-btn" onclick="setPersonality('professional')">Professional</button>
                        <button class="personality-btn" onclick="setPersonality('encouraging')">Encouraging</button>
                        <button class="personality-btn" onclick="setPersonality('calming')">Calming</button>
                    </div>
                    
                    <div class="control-group">
                        <label for="user-message">Your Message:</label>
                        <textarea id="user-message" rows="4" placeholder="Type your message here... The avatar will respond with appropriate speech and animation.">I'm feeling anxious about my upcoming job interview. Can you help me prepare?</textarea>
                    </div>
                    
                    <div class="control-group">
                        <button onclick="generateAvatarSpeech()">🎙️ Generate Avatar Response</button>
                        <button onclick="stopSpeech()">⏹️ Stop Speech</button>
                    </div>
                    
                    <div class="control-group">
                        <label>Voice Settings:</label>
                        <label for="speech-rate">Speech Rate:</label>
                        <input type="range" id="speech-rate" min="0.5" max="2.0" step="0.1" value="1.0" onchange="updateVoiceSettings()">
                        
                        <label for="voice-pitch">Voice Pitch:</label>
                        <input type="range" id="voice-pitch" min="-1.0" max="1.0" step="0.1" value="0.0" onchange="updateVoiceSettings()">
                        
                        <label for="voice-volume">Voice Volume:</label>
                        <input type="range" id="voice-volume" min="0.1" max="1.0" step="0.1" value="0.8" onchange="updateVoiceSettings()">
                    </div>
                </div>
            </div>
            
            <div class="status" id="status">
                System Status: Ready<br>
                Current Personality: Compassionate<br>
                Speech Engine: Active<br>
                Animation System: Ready
            </div>
        </div>

        <script>
            let currentPersonality = 'compassionate';
            let currentSpeech = null;
            
            function setPersonality(personality) {
                currentPersonality = personality;
                
                // Update UI
                document.querySelectorAll('.personality-btn').forEach(btn => btn.classList.remove('active'));
                event.target.classList.add('active');
                
                // Update avatar face based on personality
                const faces = {
                    'compassionate': '😊',
                    'professional': '🧑‍💼', 
                    'encouraging': '😄',
                    'calming': '😌'
                };
                document.getElementById('avatar-face').textContent = faces[personality];
                
                // Send to backend
                fetch('/api/avatar/personality', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({personality: personality})
                }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateStatus(`Personality changed to: ${personality}`);
                        // Show greeting
                        document.getElementById('speech-text').textContent = data.greeting;
                        document.getElementById('speech-text').style.display = 'block';
                        speakText(data.greeting);
                    }
                });
            }
            
            async function generateAvatarSpeech() {
                const message = document.getElementById('user-message').value;
                if (!message.trim()) {
                    alert('Please enter a message');
                    return;
                }
                
                updateStatus('Generating avatar response...');
                document.getElementById('avatar-status').textContent = 'Thinking...';
                document.getElementById('avatar-face').textContent = '🤔';
                
                try {
                    const response = await fetch('/api/avatar/speak', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            message: message,
                            personality: currentPersonality,
                            session_type: 'individual'
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        // Display response text
                        document.getElementById('speech-text').textContent = data.response_text;
                        document.getElementById('speech-text').style.display = 'block';
                        
                        // Update avatar animation
                        updateAvatarAnimation(data.animation_type);
                        
                        // Speak the response
                        await speakText(data.response_text);
                        
                        updateStatus(`Response generated successfully (${data.speech_data.estimated_duration.toFixed(1)}s duration)`);
                    } else {
                        updateStatus(`Error: ${data.error}`);
                        if (data.fallback_response) {
                            document.getElementById('speech-text').textContent = data.fallback_response;
                            document.getElementById('speech-text').style.display = 'block';
                            speakText(data.fallback_response);
                        }
                    }
                } catch (error) {
                    updateStatus(`Error: ${error.message}`);
                }
            }
            
            function updateAvatarAnimation(animationType) {
                const faces = {
                    'speaking': '😊',
                    'listening': '👂',
                    'empathetic_response': '🤗',
                    'encouraging_response': '💪'
                };
                
                document.getElementById('avatar-face').textContent = faces[animationType] || '😊';
                document.getElementById('avatar-status').textContent = animationType.replace('_', ' ');
            }
            
            function speakText(text) {
                return new Promise((resolve) => {
                    if (currentSpeech) {
                        currentSpeech.cancel();
                    }
                    
                    currentSpeech = new SpeechSynthesisUtterance(text);
                    
                    // Apply voice settings
                    currentSpeech.rate = parseFloat(document.getElementById('speech-rate').value);
                    currentSpeech.pitch = parseFloat(document.getElementById('voice-pitch').value);
                    currentSpeech.volume = parseFloat(document.getElementById('voice-volume').value);
                    
                    currentSpeech.onend = () => {
                        document.getElementById('avatar-status').textContent = 'Ready to speak';
                        document.getElementById('avatar-face').textContent = '😊';
                        resolve();
                    };
                    
                    currentSpeech.onerror = (error) => {
                        updateStatus(`Speech error: ${error.error}`);
                        resolve();
                    };
                    
                    document.getElementById('avatar-status').textContent = 'Speaking...';
                    speechSynthesis.speak(currentSpeech);
                });
            }
            
            function stopSpeech() {
                if (currentSpeech) {
                    speechSynthesis.cancel();
                    currentSpeech = null;
                    document.getElementById('avatar-status').textContent = 'Ready to speak';
                    document.getElementById('avatar-face').textContent = '😊';
                    updateStatus('Speech stopped');
                }
            }
            
            function updateVoiceSettings() {
                const rate = document.getElementById('speech-rate').value;
                const pitch = document.getElementById('voice-pitch').value;
                const volume = document.getElementById('voice-volume').value;
                
                fetch('/api/avatar/settings', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        voice_settings: {
                            speech_rate: parseFloat(rate),
                            voice_pitch: parseFloat(pitch),
                            voice_volume: parseFloat(volume)
                        }
                    })
                }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateStatus(`Voice settings updated: Rate=${rate}, Pitch=${pitch}, Volume=${volume}`);
                    }
                });
            }
            
            function updateStatus(message) {
                const statusDiv = document.getElementById('status');
                const timestamp = new Date().toLocaleTimeString();
                statusDiv.innerHTML = `
                    System Status: Active<br>
                    Current Personality: ${currentPersonality}<br>
                    Speech Engine: ${speechSynthesis.speaking ? 'Speaking' : 'Ready'}<br>
                    Last Update: ${timestamp}<br>
                    Message: ${message}
                `;
            }
            
            // Initialize
            updateStatus('Avatar system initialized');
        </script>
    </body>
    </html>
    """
    
    return render_template_string(demo_html)