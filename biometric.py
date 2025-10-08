"""
🔬 Advanced Biometric Integration API for Stage 2+ MindMend Platform
================================================================
Real-time biometric analysis integration for enhanced therapy sessions
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime, timezone
from models.therapy_ai_integration import therapy_ai_integration
from models.database import db, BiometricData
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

biometric_bp = Blueprint('biometric', __name__, url_prefix='/api/biometric')

class BiometricAnalyzer:
    """Advanced biometric data analysis for therapy enhancement"""
    
    def __init__(self):
        self.stress_threshold_high = 80
        self.stress_threshold_medium = 60
        self.heart_rate_zones = {
            'relaxed': (60, 80),
            'elevated': (80, 100),
            'stressed': (100, 120),
            'critical': (120, 180)
        }
    
    def analyze_stress_level(self, biometric_data):
        """Analyze stress level from biometric data"""
        try:
            heart_rate = biometric_data.get('heart_rate', 70)
            hrv = biometric_data.get('hrv', 40)
            blood_oxygen = biometric_data.get('blood_oxygen', 98)
            
            # Calculate stress score (0-100)
            stress_score = 0
            
            # Heart rate analysis (40% weight)
            if heart_rate > 120:
                stress_score += 40
            elif heart_rate > 100:
                stress_score += 30
            elif heart_rate > 80:
                stress_score += 15
            
            # HRV analysis (30% weight) - Lower HRV = Higher stress
            if hrv < 20:
                stress_score += 30
            elif hrv < 30:
                stress_score += 20
            elif hrv < 40:
                stress_score += 10
            
            # Blood oxygen analysis (20% weight)
            if blood_oxygen < 95:
                stress_score += 20
            elif blood_oxygen < 97:
                stress_score += 10
            
            # Activity/movement analysis (10% weight)
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
            logger.error(f"Error analyzing stress level: {e}")
            return {
                'stress_score': 0,
                'stress_level': 'unknown',
                'error': str(e)
            }
    
    def _get_stress_category(self, score):
        """Categorize stress level"""
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
        """Get therapy recommendations based on stress level"""
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
    
    def generate_therapy_insights(self, biometric_data, session_context):
        """Generate AI therapy insights based on biometric data"""
        try:
            stress_analysis = self.analyze_stress_level(biometric_data)
            
            # Enhanced therapy prompt with biometric context
            biometric_context = f"""
            BIOMETRIC ANALYSIS:
            - Stress Level: {stress_analysis['stress_level']} ({stress_analysis['stress_score']}/100)
            - Heart Rate: {biometric_data.get('heart_rate', 'N/A')} BPM
            - Heart Rate Variability: {biometric_data.get('hrv', 'N/A')}
            - Blood Oxygen: {biometric_data.get('blood_oxygen', 'N/A')}%
            - Activity Level: {biometric_data.get('activity_level', 'N/A')}
            
            RECOMMENDATIONS: {', '.join(stress_analysis['recommendations'])}
            
            Please adjust your therapeutic response based on these biometric indicators.
            If stress is high, focus on calming techniques. If relaxed, proceed normally.
            """
            
            # Generate enhanced AI response
            enhanced_response = therapy_ai_integration.enhance_therapy_response(
                session_type=session_context.get('session_type', 'individual'),
                user_message=session_context.get('user_message', ''),
                session_data={
                    **session_context,
                    'biometric_context': biometric_context,
                    'stress_level': stress_analysis['stress_level'],
                    'biometric_recommendations': stress_analysis['recommendations']
                }
            )
            
            return {
                'enhanced_response': enhanced_response,
                'biometric_analysis': stress_analysis,
                'therapy_adjustments': self._get_therapy_adjustments(stress_analysis['stress_level'])
            }
            
        except Exception as e:
            logger.error(f"Error generating therapy insights: {e}")
            return {
                'error': str(e),
                'fallback_response': "I notice we're having some technical difficulties with biometric analysis. Let's continue with our session."
            }
    
    def _get_therapy_adjustments(self, stress_level):
        """Get specific therapy technique adjustments"""
        adjustments = {
            'critical': {
                'pace': 'very_slow',
                'techniques': ['deep_breathing', 'grounding_5_4_3_2_1', 'progressive_relaxation'],
                'duration': 'extended',
                'follow_up': 'immediate'
            },
            'high': {
                'pace': 'slow',
                'techniques': ['mindfulness', 'breathing_exercises', 'body_scan'],
                'duration': 'standard',
                'follow_up': 'same_day'
            },
            'moderate': {
                'pace': 'moderate',
                'techniques': ['cognitive_reframing', 'mindfulness', 'problem_solving'],
                'duration': 'standard',
                'follow_up': 'next_session'
            },
            'mild': {
                'pace': 'standard',
                'techniques': ['standard_therapy', 'skill_building', 'goal_setting'],
                'duration': 'standard',
                'follow_up': 'routine'
            },
            'relaxed': {
                'pace': 'standard',
                'techniques': ['exploration', 'insight_work', 'skill_advancement'],
                'duration': 'full',
                'follow_up': 'routine'
            }
        }
        
        return adjustments.get(stress_level, adjustments['moderate'])

# Initialize analyzer
biometric_analyzer = BiometricAnalyzer()

@biometric_bp.route('/connect', methods=['POST'])
def connect_device():
    """Connect biometric device to therapy session"""
    try:
        data = request.get_json()
        device_type = data.get('device_type')
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Store device connection
        device_connection = {
            'user_id': user_id,
            'device_type': device_type,
            'connected_at': datetime.now(timezone.utc).isoformat(),
            'status': 'connected',
            'features': data.get('features', [])
        }
        
        # In production, store in database
        session['biometric_device'] = device_connection
        
        logger.info(f"✅ Biometric device connected: {device_type} for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully connected {device_type}',
            'connection': device_connection
        })
        
    except Exception as e:
        logger.error(f"❌ Error connecting biometric device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@biometric_bp.route('/data', methods=['POST'])
def receive_biometric_data():
    """Receive real-time biometric data during therapy session"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        session_id = session.get('current_session_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        biometric_data = {
            'heart_rate': data.get('heart_rate'),
            'hrv': data.get('hrv'),
            'blood_oxygen': data.get('blood_oxygen'),
            'activity_level': data.get('activity_level'),
            'temperature': data.get('temperature'),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Analyze stress level
        analysis = biometric_analyzer.analyze_stress_level(biometric_data)
        
        # Store in database (in production)
        try:
            biometric_record = BiometricData(
                user_id=user_id,
                session_id=session_id,
                heart_rate=biometric_data['heart_rate'],
                hrv=biometric_data['hrv'],
                blood_oxygen=biometric_data['blood_oxygen'],
                stress_score=analysis['stress_score'],
                stress_level=analysis['stress_level'],
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(biometric_record)
            db.session.commit()
        except Exception as db_error:
            logger.warning(f"⚠️ Database error (continuing): {db_error}")
        
        # Store in session for immediate use
        session['latest_biometric_data'] = biometric_data
        session['latest_biometric_analysis'] = analysis
        
        logger.info(f"📊 Biometric data received: Stress {analysis['stress_level']} ({analysis['stress_score']}/100)")
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'recommendations': analysis['recommendations']
        })
        
    except Exception as e:
        logger.error(f"❌ Error processing biometric data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@biometric_bp.route('/therapy-insights', methods=['POST'])
def generate_therapy_insights():
    """Generate AI therapy insights based on current biometric data"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Get latest biometric data
        biometric_data = session.get('latest_biometric_data', {})
        if not biometric_data:
            return jsonify({'success': False, 'error': 'No biometric data available'}), 400
        
        # Session context
        session_context = {
            'session_type': data.get('session_type', 'individual'),
            'user_message': data.get('user_message', ''),
            'session_id': session.get('current_session_id'),
            'user_id': user_id
        }
        
        # Generate insights
        insights = biometric_analyzer.generate_therapy_insights(biometric_data, session_context)
        
        logger.info(f"🧠 Generated biometric-enhanced therapy insights for user {user_id}")
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        logger.error(f"❌ Error generating therapy insights: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@biometric_bp.route('/status', methods=['GET'])
def get_biometric_status():
    """Get current biometric monitoring status"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
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
            ).total_seconds() < 300)  # Active if data within 5 minutes
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting biometric status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@biometric_bp.route('/disconnect', methods=['POST'])
def disconnect_device():
    """Disconnect biometric device"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Clear session data
        session.pop('biometric_device', None)
        session.pop('latest_biometric_data', None)
        session.pop('latest_biometric_analysis', None)
        
        logger.info(f"🔌 Biometric device disconnected for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Biometric device disconnected successfully'
        })
        
    except Exception as e:
        logger.error(f"❌ Error disconnecting biometric device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Database model for biometric data storage  
# Note: This model may already be defined in models/database.py
try:
    class BiometricData(db.Model):
        """Store biometric data from therapy sessions"""
        __tablename__ = 'biometric_data'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
        heart_rate = db.Column(db.Integer)
        hrv = db.Column(db.Float)
        blood_oxygen = db.Column(db.Float)
        temperature = db.Column(db.Float)
        stress_score = db.Column(db.Integer)
        stress_level = db.Column(db.String(50))
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'session_id': self.session_id,
                'heart_rate': self.heart_rate,
                                'hrv': self.hrv,
                'blood_oxygen': self.blood_oxygen,
                'temperature': self.temperature,
                'stress_score': self.stress_score,
                'stress_level': self.stress_level,
                'timestamp': self.timestamp.isoformat(),
                'created_at': self.created_at.isoformat()
            }
except Exception as e:
    logger.warning(f"BiometricData model already exists: {e}")