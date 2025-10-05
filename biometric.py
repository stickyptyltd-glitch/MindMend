
from flask import Blueprint, request, jsonify, session
from datetime import datetime, timezone
import logging

biometric_bp = Blueprint('biometric', __name__, url_prefix='/api/biometric')

class BiometricAnalyzer:
    def analyze_stress_level(self, biometric_data):
        try:
            heart_rate = biometric_data.get('heart_rate', 70)
            hrv = biometric_data.get('hrv', 40)
            blood_oxygen = biometric_data.get('blood_oxygen', 98)
            stress_score = 0
            if heart_rate > 120:
                stress_score += 40
            elif heart_rate > 100:
                stress_score += 30
            elif heart_rate > 80:
                stress_score += 15
            if hrv < 20:
                stress_score += 30
            elif hrv < 30:
                stress_score += 20
            elif hrv < 40:
                stress_score += 10
            if blood_oxygen < 95:
                stress_score += 20
            elif blood_oxygen < 97:
                stress_score += 10
            activity = biometric_data.get('activity_level', 'moderate')
            if activity == 'high':
                stress_score += 5
            elif activity == 'very_high':
                stress_score += 10
            return {
                'stress_score': min(stress_score, 100),
                'stress_level': self._get_stress_category(stress_score),
                'recommendations': self._get_stress_recommendations(stress_score),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                'stress_score': 0,
                'stress_level': 'unknown',
                'error': str(e)
            }
    def _get_stress_category(self, score):
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'moderate'
        elif score >= 20:
            return 'mild'
        else:
            return 'relaxed'
    def _get_stress_recommendations(self, score):
        if score >= 80:
            return [
                "Implement immediate breathing exercises",
                "Consider grounding techniques",
                "Alert therapy coordinator",
                "Schedule follow-up session"
            ]
        elif score >= 60:
            return [
                "Focus on relaxation techniques",
                "Practice mindfulness exercises",
                "Adjust session pacing"
            ]
        elif score >= 40:
            return [
                "Maintain current approach",
                "Monitor stress levels",
                "Include stress management tools"
            ]
        else:
            return [
                "Continue with standard therapy approach",
                "Utilize positive momentum"
            ]

biometric_analyzer = BiometricAnalyzer()

from flask_login import login_required

@biometric_bp.route('/connect', methods=['POST'])
@login_required
def connect_device():
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        device_type = data.get('device_type', 'Unknown')
        device_connection = {
            'user_id': user_id,
            'device_type': device_type,
            'connected_at': datetime.now(timezone.utc).isoformat(),
            'status': 'connected',
            'features': data.get('features', [])
        }
        session['biometric_device'] = device_connection
        return jsonify({
            'success': True,
            'message': f'Successfully connected {device_type}',
            'connection': device_connection
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@biometric_bp.route('/data', methods=['POST'])
@login_required
def receive_biometric_data():
    try:
        data = request.get_json()
        biometric_data = {
            'heart_rate': data.get('heart_rate'),
            'hrv': data.get('hrv'),
            'blood_oxygen': data.get('blood_oxygen'),
            'activity_level': data.get('activity_level'),
            'temperature': data.get('temperature'),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        analysis = biometric_analyzer.analyze_stress_level(biometric_data)
        session['latest_biometric_data'] = biometric_data
        session['latest_biometric_analysis'] = analysis
        return jsonify({
            'success': True,
            'analysis': analysis,
            'recommendations': analysis['recommendations']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@biometric_bp.route('/status', methods=['GET'])
@login_required
def get_biometric_status():
    try:
        device_connection = session.get('biometric_device')
        latest_data = session.get('latest_biometric_data')
        latest_analysis = session.get('latest_biometric_analysis')
        status = {
            'connected': bool(device_connection),
            'device': device_connection,
            'latest_data': latest_data,
            'latest_analysis': latest_analysis,
            'monitoring_active': bool(latest_data and (
                datetime.now(timezone.utc) - datetime.fromisoformat(latest_data['timestamp'])
            ).total_seconds() < 300)
        }
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@biometric_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect_device():
    try:
        session.pop('biometric_device', None)
        session.pop('latest_biometric_data', None)
        session.pop('latest_biometric_analysis', None)
        return jsonify({
            'success': True,
            'message': 'Biometric device disconnected successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
