"""
🎭 Real-time Emotion Detection API for Stage 2+ MindMend Platform
===============================================================
Advanced facial emotion recognition during therapy sessions
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime, timezone
import json
import base64
import io
import numpy as np
from PIL import Image
import cv2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

emotion_bp = Blueprint('emotion', __name__, url_prefix='/api/emotion')

class EmotionDetector:
    """Advanced real-time emotion detection for therapy enhancement"""
    
    def __init__(self):
        self.emotion_categories = {
            'happy': {'weight': 1.0, 'therapy_approach': 'positive_reinforcement'},
            'sad': {'weight': -0.8, 'therapy_approach': 'supportive_exploration'},
            'angry': {'weight': -0.9, 'therapy_approach': 'de_escalation'},
            'fear': {'weight': -0.7, 'therapy_approach': 'grounding_techniques'},
            'surprise': {'weight': 0.2, 'therapy_approach': 'engagement'},
            'disgust': {'weight': -0.6, 'therapy_approach': 'cognitive_reframing'},
            'neutral': {'weight': 0.0, 'therapy_approach': 'standard_approach'}
        }
        
        # Initialize mock AI models (in production, use actual models)
        self.confidence_threshold = 0.6
        self.emotion_history = []
        self.max_history = 100
    
    def analyze_facial_emotion(self, image_data, context=None):
        """Analyze facial emotions from image data"""
        try:
            # Decode base64 image
            if isinstance(image_data, str):
                # Remove data URL prefix if present
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Convert to CV2 format for processing
                image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Perform emotion detection (mock implementation)
                emotions = self._mock_emotion_detection(image_cv, context)
                
                # Add to history
                emotion_record = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'emotions': emotions,
                    'dominant_emotion': emotions[0] if emotions else None,
                    'context': context
                }
                
                self._add_to_history(emotion_record)
                
                return {
                    'success': True,
                    'emotions': emotions,
                    'dominant_emotion': emotions[0] if emotions else None,
                    'therapy_recommendations': self._get_therapy_recommendations(emotions),
                    'emotional_state_analysis': self._analyze_emotional_state(emotions),
                    'timestamp': emotion_record['timestamp']
                }
                
            else:
                return {'success': False, 'error': 'Invalid image data format'}
                
        except Exception as e:
            logger.error(f"Error analyzing facial emotion: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_emotions': [{'emotion': 'neutral', 'confidence': 0.5}]
            }
    
    def _mock_emotion_detection(self, image_cv, context):
        """Mock emotion detection (replace with actual AI model)"""
        # In production, use actual facial recognition models like:
        # - OpenCV Haar Cascades + CNN
        # - TensorFlow/PyTorch emotion classification models
        # - Azure Cognitive Services Face API
        # - AWS Rekognition
        
        # Mock emotions based on session context
        if context and 'session_type' in context:
            session_type = context['session_type']
            
            if session_type == 'crisis':
                return [
                    {'emotion': 'sad', 'confidence': 0.75},
                    {'emotion': 'fear', 'confidence': 0.65},
                    {'emotion': 'neutral', 'confidence': 0.3}
                ]
            elif session_type == 'couples':
                return [
                    {'emotion': 'angry', 'confidence': 0.45},
                    {'emotion': 'sad', 'confidence': 0.35},
                    {'emotion': 'neutral', 'confidence': 0.6}
                ]
            elif 'progress' in context.get('user_message', '').lower():
                return [
                    {'emotion': 'happy', 'confidence': 0.8},
                    {'emotion': 'surprise', 'confidence': 0.4},
                    {'emotion': 'neutral', 'confidence': 0.3}
                ]
        
        # Default mock emotions
        import random
        emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']
        selected_emotions = random.sample(emotions, 3)
        
        return [
            {'emotion': selected_emotions[0], 'confidence': round(random.uniform(0.6, 0.95), 2)},
            {'emotion': selected_emotions[1], 'confidence': round(random.uniform(0.3, 0.7), 2)},
            {'emotion': selected_emotions[2], 'confidence': round(random.uniform(0.1, 0.5), 2)}
        ]
    
    def _add_to_history(self, record):
        """Add emotion record to history"""
        self.emotion_history.append(record)
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)
    
    def _get_therapy_recommendations(self, emotions):
        """Get therapy recommendations based on detected emotions"""
        if not emotions:
            return ['Continue with standard therapy approach']
        
        dominant_emotion = emotions[0]['emotion']
        confidence = emotions[0]['confidence']
        
        recommendations = []
        
        if confidence > 0.7:
            emotion_config = self.emotion_categories.get(dominant_emotion, {})
            approach = emotion_config.get('therapy_approach', 'standard_approach')
            
            if approach == 'positive_reinforcement':
                recommendations.extend([
                    'Leverage positive emotional state for skill building',
                    'Explore what contributed to positive feelings',
                    'Reinforce successful coping strategies'
                ])
            elif approach == 'supportive_exploration':
                recommendations.extend([
                    'Provide empathetic validation',
                    'Explore underlying causes of sadness',
                    'Introduce gentle coping strategies'
                ])
            elif approach == 'de_escalation':
                recommendations.extend([
                    'Use calm, steady tone',
                    'Implement anger management techniques',
                    'Focus on grounding and breathing exercises'
                ])
            elif approach == 'grounding_techniques':
                recommendations.extend([
                    'Implement 5-4-3-2-1 grounding technique',
                    'Focus on present moment awareness',
                    'Use calming visualization exercises'
                ])
            elif approach == 'engagement':
                recommendations.extend([
                    'Capitalize on client engagement',
                    'Introduce new therapeutic concepts',
                    'Encourage active participation'
                ])
            elif approach == 'cognitive_reframing':
                recommendations.extend([
                    'Challenge negative thought patterns',
                    'Explore alternative perspectives',
                    'Use cognitive behavioral techniques'
                ])
        
        # Add general recommendations based on emotion mix
        emotion_scores = {e['emotion']: e['confidence'] for e in emotions}
        
        if emotion_scores.get('sad', 0) + emotion_scores.get('fear', 0) > 1.0:
            recommendations.append('Consider increased session frequency')
        
        if emotion_scores.get('angry', 0) > 0.6:
            recommendations.append('Monitor for potential escalation')
        
        return recommendations if recommendations else ['Continue with current therapeutic approach']
    
    def _analyze_emotional_state(self, emotions):
        """Analyze overall emotional state"""
        if not emotions:
            return {
                'overall_state': 'neutral',
                'emotional_intensity': 0.5,
                'stability': 'stable',
                'complexity': 'simple'
            }
        
        # Calculate emotional valence (positive vs negative)
        total_weight = 0
        total_confidence = 0
        
        for emotion in emotions:
            emotion_name = emotion['emotion']
            confidence = emotion['confidence']
            weight = self.emotion_categories.get(emotion_name, {}).get('weight', 0)
            
            total_weight += weight * confidence
            total_confidence += confidence
        
        if total_confidence > 0:
            valence = total_weight / total_confidence
        else:
            valence = 0
        
        # Determine overall state
        if valence > 0.3:
            overall_state = 'positive'
        elif valence < -0.3:
            overall_state = 'negative'
        else:
            overall_state = 'neutral'
        
        # Calculate emotional intensity
        max_confidence = max([e['confidence'] for e in emotions])
        emotional_intensity = max_confidence
        
        # Determine complexity (how many emotions are present)
        significant_emotions = [e for e in emotions if e['confidence'] > 0.4]
        complexity = 'complex' if len(significant_emotions) > 2 else 'simple'
        
        return {
            'overall_state': overall_state,
            'emotional_intensity': round(emotional_intensity, 2),
            'stability': self._assess_stability(),
            'complexity': complexity,
            'valence': round(valence, 2)
        }
    
    def _assess_stability(self):
        """Assess emotional stability based on recent history"""
        if len(self.emotion_history) < 3:
            return 'insufficient_data'
        
        recent_emotions = self.emotion_history[-5:]  # Last 5 records
        dominant_emotions = [record['dominant_emotion']['emotion'] for record in recent_emotions if record['dominant_emotion']]
        
        if len(set(dominant_emotions)) <= 2:
            return 'stable'
        elif len(set(dominant_emotions)) <= 3:
            return 'moderate'
        else:
            return 'variable'
    
    def get_emotion_trends(self, time_window_minutes=30):
        """Get emotion trends over specified time window"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
            
            recent_records = []
            for record in self.emotion_history:
                record_time = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                if record_time > cutoff_time:
                    recent_records.append(record)
            
            if not recent_records:
                return {'trends': [], 'summary': 'Insufficient data'}
            
            # Analyze trends
            emotion_timeline = []
            for record in recent_records:
                if record['dominant_emotion']:
                    emotion_timeline.append({
                        'timestamp': record['timestamp'],
                        'emotion': record['dominant_emotion']['emotion'],
                        'confidence': record['dominant_emotion']['confidence']
                    })
            
            # Calculate emotion distribution
            emotion_counts = {}
            for point in emotion_timeline:
                emotion = point['emotion']
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            # Generate trend summary
            most_frequent = max(emotion_counts.items(), key=lambda x: x[1]) if emotion_counts else ('neutral', 0)
            
            return {
                'trends': emotion_timeline,
                'distribution': emotion_counts,
                'most_frequent_emotion': most_frequent[0],
                'total_detections': len(emotion_timeline),
                'time_window': time_window_minutes,
                'summary': f"Most frequent emotion: {most_frequent[0]} ({most_frequent[1]} detections)"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing emotion trends: {e}")
            return {'error': str(e)}

# Initialize emotion detector
emotion_detector = EmotionDetector()

@emotion_bp.route('/analyze', methods=['POST'])
def analyze_emotion():
    """Analyze emotion from facial image"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        image_data = data.get('image')
        if not image_data:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
        
        # Context for better analysis
        context = {
            'session_type': data.get('session_type', 'individual'),
            'user_message': data.get('user_message', ''),
            'session_id': session.get('current_session_id'),
            'user_id': user_id
        }
        
        # Perform emotion analysis
        result = emotion_detector.analyze_facial_emotion(image_data, context)
        
        if result['success']:
            logger.info(f"🎭 Emotion analysis completed for user {user_id}: {result['dominant_emotion']['emotion'] if result['dominant_emotion'] else 'None'}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error in emotion analysis: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@emotion_bp.route('/trends', methods=['GET'])
def get_emotion_trends():
    """Get emotion trends for current session"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        time_window = request.args.get('time_window', 30, type=int)
        trends = emotion_detector.get_emotion_trends(time_window)
        
        return jsonify({
            'success': True,
            'trends': trends
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting emotion trends: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@emotion_bp.route('/therapy-adjustment', methods=['POST'])
def get_therapy_adjustment():
    """Get therapy approach adjustment based on current emotional state"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Get recent emotion history
        recent_emotions = emotion_detector.emotion_history[-5:] if emotion_detector.emotion_history else []
        
        if not recent_emotions:
            return jsonify({
                'success': False,
                'error': 'No recent emotion data available'
            })
        
        # Analyze current emotional pattern
        latest_record = recent_emotions[-1]
        emotional_state = latest_record.get('emotional_state_analysis', {})
        
        # Generate therapy adjustments
        adjustments = {
            'pace_adjustment': 'standard',
            'technique_recommendations': [],
            'environmental_suggestions': [],
            'session_modifications': []
        }
        
        if emotional_state.get('overall_state') == 'negative':
            adjustments['pace_adjustment'] = 'slower'
            adjustments['technique_recommendations'].extend([
                'mindfulness_breathing',
                'grounding_exercises',
                'positive_affirmations'
            ])
            adjustments['environmental_suggestions'].extend([
                'softer_lighting',
                'calming_background_music',
                'comfortable_temperature'
            ])
        
        elif emotional_state.get('overall_state') == 'positive':
            adjustments['pace_adjustment'] = 'standard_or_faster'
            adjustments['technique_recommendations'].extend([
                'skill_building',
                'goal_setting',
                'strength_exploration'
            ])
        
        if emotional_state.get('stability') == 'variable':
            adjustments['session_modifications'].extend([
                'frequent_check_ins',
                'shorter_segments',
                'flexibility_in_approach'
            ])
        
        return jsonify({
            'success': True,
            'adjustments': adjustments,
            'emotional_state': emotional_state,
            'based_on_emotions': len(recent_emotions)
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting therapy adjustment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@emotion_bp.route('/status', methods=['GET'])
def get_emotion_status():
    """Get current emotion detection status"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        status = {
            'active': len(emotion_detector.emotion_history) > 0,
            'recent_detections': len(emotion_detector.emotion_history),
            'last_detection': emotion_detector.emotion_history[-1]['timestamp'] if emotion_detector.emotion_history else None,
            'dominant_recent_emotion': emotion_detector.emotion_history[-1]['dominant_emotion'] if emotion_detector.emotion_history else None
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting emotion status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@emotion_bp.route('/clear-history', methods=['POST'])
def clear_emotion_history():
    """Clear emotion detection history for new session"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        emotion_detector.emotion_history = []
        
        logger.info(f"🧹 Emotion history cleared for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Emotion history cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Error clearing emotion history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500