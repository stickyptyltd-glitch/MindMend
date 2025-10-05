
from flask import Blueprint, request, jsonify, session
from datetime import datetime, timezone, timedelta
import logging
import base64
import io
import numpy as np
from PIL import Image
import cv2

emotion_bp = Blueprint('emotion', __name__, url_prefix='/api/emotion')

class EmotionDetector:
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
        self.emotion_history = []
        self.max_history = 100

    def analyze_facial_emotion(self, image_data, context=None):
        try:
            if isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                emotions = self._mock_emotion_detection(image_cv, context)
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
            return {
                'success': False,
                'error': str(e),
                'fallback_emotions': [{'emotion': 'neutral', 'confidence': 0.5}]
            }

    def _mock_emotion_detection(self, image_cv, context):
        import random
        emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']
        selected_emotions = random.sample(emotions, 3)
        return [
            {'emotion': selected_emotions[0], 'confidence': round(random.uniform(0.6, 0.95), 2)},
            {'emotion': selected_emotions[1], 'confidence': round(random.uniform(0.3, 0.7), 2)},
            {'emotion': selected_emotions[2], 'confidence': round(random.uniform(0.1, 0.5), 2)}
        ]

    def _add_to_history(self, record):
        self.emotion_history.append(record)
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)

    def _get_therapy_recommendations(self, emotions):
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
        emotion_scores = {e['emotion']: e['confidence'] for e in emotions}
        if emotion_scores.get('sad', 0) + emotion_scores.get('fear', 0) > 1.0:
            recommendations.append('Consider increased session frequency')
        if emotion_scores.get('angry', 0) > 0.6:
            recommendations.append('Monitor for potential escalation')
        return recommendations if recommendations else ['Continue with current therapeutic approach']

    def _analyze_emotional_state(self, emotions):
        if not emotions:
            return {
                'overall_state': 'neutral',
                'emotional_intensity': 0.5,
                'stability': 'stable',
                'complexity': 'simple'
            }
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
        if valence > 0.3:
            overall_state = 'positive'
        elif valence < -0.3:
            overall_state = 'negative'
        else:
            overall_state = 'neutral'
        max_confidence = max([e['confidence'] for e in emotions])
        emotional_intensity = max_confidence
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
        if len(self.emotion_history) < 3:
            return 'insufficient_data'
        recent_emotions = self.emotion_history[-5:]
        dominant_emotions = [record['dominant_emotion']['emotion'] for record in recent_emotions if record['dominant_emotion']]
        if len(set(dominant_emotions)) <= 2:
            return 'stable'
        elif len(set(dominant_emotions)) <= 3:
            return 'moderate'
        else:
            return 'variable'

emotion_detector = EmotionDetector()

from flask_login import login_required

@emotion_bp.route('/analyze', methods=['POST'])
@login_required
def analyze_emotion():
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        image_data = data.get('image')
        if not image_data:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
        context = {
            'session_type': data.get('session_type', 'individual'),
            'user_message': data.get('user_message', ''),
            'session_id': session.get('current_session_id'),
            'user_id': user_id
        }
        result = emotion_detector.analyze_facial_emotion(image_data, context)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
