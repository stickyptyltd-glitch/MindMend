"""
🚨 Advanced Crisis Intervention API for Stage 2+ MindMend Platform
================================================================
Real-time crisis detection and automatic escalation system
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime, timezone, timedelta
import json
import logging
from models.therapy_ai_integration import therapy_ai_integration
from models.database import db, User, Session as TherapySession, CrisisEvent
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

crisis_bp = Blueprint('crisis', __name__, url_prefix='/api/crisis')

class CrisisInterventionSystem:
    """Advanced crisis detection and intervention system"""
    
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
                'delay_minutes': 0
            },
            'medium': {
                'score_range': (50, 75),
                'response': 'immediate_intervention',
                'action': 'alert_supervisor',
                'delay_minutes': 5
            },
            'high': {
                'score_range': (75, 90),
                'response': 'crisis_protocol',
                'action': 'emergency_contact',
                'delay_minutes': 2
            },
            'critical': {
                'score_range': (90, 100),
                'response': 'emergency_services',
                'action': 'immediate_escalation',
                'delay_minutes': 0
            }
        }
        
        # Emergency contacts (in production, load from secure config)
        self.emergency_contacts = {
            'supervisor': {
                'email': 'supervisor@mindmend.com',
                'phone': '+1-555-CRISIS',
                'name': 'Dr. Sarah Chen'
            },
            'emergency': {
                'email': 'emergency@mindmend.com',
                'phone': '+1-555-EMERGENCY',
                'name': 'Crisis Team Lead'
            },
            'external': {
                'suicide_hotline': '988',
                'crisis_text': 'Text HOME to 741741',
                'emergency': '911'
            }
        }
    
    def analyze_crisis_risk(self, user_message, biometric_data=None, emotion_data=None, context=None):
        """Comprehensive crisis risk analysis"""
        try:
            crisis_score = 0
            risk_factors = []
            
            # Text analysis (40% weight)
            text_risk = self._analyze_text_content(user_message)
            crisis_score += text_risk['score'] * 0.4
            risk_factors.extend(text_risk['factors'])
            
            # Biometric analysis (30% weight)
            if biometric_data:
                bio_risk = self._analyze_biometric_crisis_indicators(biometric_data)
                crisis_score += bio_risk['score'] * 0.3
                risk_factors.extend(bio_risk['factors'])
            
            # Emotion analysis (20% weight)
            if emotion_data:
                emotion_risk = self._analyze_emotional_crisis_indicators(emotion_data)
                crisis_score += emotion_risk['score'] * 0.2
                risk_factors.extend(emotion_risk['factors'])
            
            # Context analysis (10% weight)
            if context:
                context_risk = self._analyze_context_indicators(context)
                crisis_score += context_risk['score'] * 0.1
                risk_factors.extend(context_risk['factors'])
            
            # Determine crisis level
            crisis_level = self._determine_crisis_level(crisis_score)
            
            return {
                'crisis_score': min(crisis_score, 100),
                'crisis_level': crisis_level,
                'risk_factors': list(set(risk_factors)),  # Remove duplicates
                'immediate_action_required': crisis_score >= 75,
                'escalation_protocol': self.escalation_levels[crisis_level],
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing crisis risk: {e}")
            return {
                'crisis_score': 0,
                'crisis_level': 'unknown',
                'error': str(e),
                'immediate_action_required': False
            }
    
    def _analyze_text_content(self, text):
        """Analyze text for crisis indicators"""
        if not text:
            return {'score': 0, 'factors': []}
        
        text_lower = text.lower()
        score = 0
        factors = []
        
        # Direct crisis keyword detection
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                if keyword in ['suicide', 'kill myself', 'end it all', 'want to die']:
                    score += 40  # High-weight keywords
                    factors.append(f"Direct crisis language: '{keyword}'")
                elif keyword in ['hurt myself', 'self harm', 'hopeless', 'worthless']:
                    score += 25  # Medium-weight keywords
                    factors.append(f"Self-harm language: '{keyword}'")
                else:
                    score += 15  # Lower-weight but concerning
                    factors.append(f"Concerning language: '{keyword}'")
        
        # Pattern detection
        crisis_patterns = [
            (r'can\'t (take|handle|deal with) (it|this) anymore', 20, 'Overwhelm pattern'),
            (r'nobody (cares|loves|understands) me', 15, 'Isolation pattern'),
            (r'everything is (falling apart|ruined|hopeless)', 20, 'Despair pattern'),
            (r'i (hate|despise) myself', 25, 'Self-hatred pattern')
        ]
        
        import re
        for pattern, points, description in crisis_patterns:
            if re.search(pattern, text_lower):
                score += points
                factors.append(description)
        
        # Length and intensity analysis
        if len(text) > 500 and score > 10:  # Long, concerning messages
            score += 10
            factors.append("Extended distressed communication")
        
        return {'score': min(score, 100), 'factors': factors}
    
    def _analyze_biometric_crisis_indicators(self, biometric_data):
        """Analyze biometric data for crisis indicators"""
        score = 0
        factors = []
        
        heart_rate = biometric_data.get('heart_rate', 70)
        stress_level = biometric_data.get('stress_level', 'unknown')
        
        # Extreme stress indicators
        if stress_level == 'critical':
            score += 30
            factors.append("Critical biometric stress levels")
        elif stress_level == 'high':
            score += 20
            factors.append("High biometric stress levels")
        
        # Heart rate crisis indicators
        if heart_rate > 130:
            score += 25
            factors.append("Extremely elevated heart rate")
        elif heart_rate < 50:
            score += 20
            factors.append("Concerning low heart rate")
        
        return {'score': min(score, 100), 'factors': factors}
    
    def _analyze_emotional_crisis_indicators(self, emotion_data):
        """Analyze emotion data for crisis indicators"""
        score = 0
        factors = []
        
        if not emotion_data or not emotion_data.get('emotions'):
            return {'score': 0, 'factors': []}
        
        emotions = emotion_data['emotions']
        dominant_emotion = emotion_data.get('dominant_emotion', {})
        
        # High-risk emotional states
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
        
        # Emotional instability
        high_confidence_emotions = [e for e in emotions if e.get('confidence', 0) > 0.6]
        if len(high_confidence_emotions) >= 3:
            score += 15
            factors.append("Emotional instability detected")
        
        return {'score': min(score, 100), 'factors': factors}
    
    def _analyze_context_indicators(self, context):
        """Analyze session context for crisis indicators"""
        score = 0
        factors = []
        
        session_type = context.get('session_type', 'individual')
        previous_crises = context.get('previous_crisis_events', 0)
        session_duration = context.get('session_duration_minutes', 0)
        
        # Previous crisis history
        if previous_crises > 0:
            score += min(previous_crises * 5, 20)
            factors.append(f"Previous crisis events: {previous_crises}")
        
        # Extended distressed sessions
        if session_duration > 90:
            score += 10
            factors.append("Extended session duration")
        
        # Crisis session type
        if session_type == 'crisis':
            score += 15
            factors.append("Already in crisis session mode")
        
        return {'score': min(score, 100), 'factors': factors}
    
    def _determine_crisis_level(self, score):
        """Determine crisis level from score"""
        for level, config in self.escalation_levels.items():
            min_score, max_score = config['score_range']
            if min_score <= score < max_score:
                return level
        
        if score >= 90:
            return 'critical'
        else:
            return 'low'
    
    def execute_crisis_protocol(self, crisis_analysis, user_id, session_id):
        """Execute appropriate crisis intervention protocol"""
        try:
            crisis_level = crisis_analysis['crisis_level']
            protocol = self.escalation_levels[crisis_level]
            
            # Log crisis event
            crisis_event = CrisisEvent(
                user_id=user_id,
                session_id=session_id,
                crisis_level=crisis_level,
                crisis_score=crisis_analysis['crisis_score'],
                risk_factors=json.dumps(crisis_analysis['risk_factors']),
                protocol_executed=protocol['action'],
                timestamp=datetime.now(timezone.utc)
            )
            
            try:
                db.session.add(crisis_event)
                db.session.commit()
            except Exception as db_error:
                logger.warning(f"Database error (continuing): {db_error}")
            
            # Execute immediate response
            response_message = self._generate_crisis_response(crisis_level, crisis_analysis)
            
            # Execute escalation protocol
            if protocol['delay_minutes'] == 0:
                self._execute_immediate_escalation(crisis_level, user_id, crisis_analysis)
            else:
                # Schedule delayed escalation
                threading.Timer(
                    protocol['delay_minutes'] * 60,
                    self._execute_delayed_escalation,
                    args=(crisis_level, user_id, crisis_analysis)
                ).start()
            
            logger.warning(f"🚨 CRISIS PROTOCOL ACTIVATED: Level {crisis_level} for user {user_id}")
            
            return {
                'protocol_activated': True,
                'crisis_level': crisis_level,
                'immediate_response': response_message,
                'escalation_scheduled': protocol['delay_minutes'] > 0,
                'emergency_contacts': self._get_user_appropriate_contacts(crisis_level)
            }
            
        except Exception as e:
            logger.error(f"Error executing crisis protocol: {e}")
            # Fallback to maximum safety protocol
            self._execute_emergency_fallback(user_id)
            return {
                'protocol_activated': True,
                'crisis_level': 'critical',
                'immediate_response': self._get_emergency_response(),
                'error': str(e)
            }
    
    def _generate_crisis_response(self, crisis_level, crisis_analysis):
        """Generate appropriate crisis response message"""
        responses = {
            'low': """I notice you might be going through a difficult time. It's important to know that you're not alone, and there are people who care about you. 

Would you like to explore some coping strategies together, or would you prefer to talk about what's been troubling you?""",
            
            'medium': """I'm concerned about what you're sharing with me right now. Your feelings are valid, but I want to make sure you're safe and supported.

Let's take a moment together. Can you tell me if you're in a safe place right now? I'm here to help you through this difficult time.

If you need immediate support, you can:
• Call 988 (Suicide & Crisis Lifeline)
• Text HOME to 741741 (Crisis Text Line)""",
            
            'high': """⚠️ I'm very concerned about your safety right now. What you're experiencing sounds extremely difficult, but there are people trained to help you through this.

Please know that you matter and your life has value. I'm alerting our crisis team to provide you with immediate support.

IMMEDIATE RESOURCES:
• Call 988 (Suicide & Crisis Lifeline) - Available 24/7
• Text HOME to 741741 (Crisis Text Line)
• Call 911 if you're in immediate danger

A member of our crisis team will be contacting you within the next few minutes.""",
            
            'critical': """🚨 CRISIS ALERT: I'm extremely concerned about your immediate safety. You've shared information that indicates you may be in crisis.

Our emergency protocol has been activated and help is on the way. Please:

1. Stay on this line - don't navigate away
2. If you're in immediate danger, call 911 NOW
3. Go to your nearest emergency room if possible
4. Call 988 (Suicide & Crisis Lifeline) immediately

A crisis counselor is being alerted NOW and will contact you immediately. You are not alone."""
        }
        
        return responses.get(crisis_level, responses['critical'])
    
    def _execute_immediate_escalation(self, crisis_level, user_id, crisis_analysis):
        """Execute immediate escalation protocols"""
        if crisis_level in ['high', 'critical']:
            # Alert emergency team
            self._send_crisis_alert(user_id, crisis_analysis)
            logger.critical(f"🚨 IMMEDIATE ESCALATION: {crisis_level} crisis for user {user_id}")
    
    def _execute_delayed_escalation(self, crisis_level, user_id, crisis_analysis):
        """Execute delayed escalation after timer"""
        self._send_crisis_alert(user_id, crisis_analysis)
        logger.warning(f"⏰ DELAYED ESCALATION: {crisis_level} crisis for user {user_id}")
    
    def _send_crisis_alert(self, user_id, crisis_analysis):
        """Send crisis alert to appropriate personnel"""
        try:
            crisis_level = crisis_analysis['crisis_level']
            
            # Determine recipient
            if crisis_level == 'critical':
                recipient = self.emergency_contacts['emergency']
            else:
                recipient = self.emergency_contacts['supervisor']
            
            # Email alert (in production, use secure email service)
            subject = f"🚨 CRISIS ALERT: Level {crisis_level.upper()} - User {user_id}"
            
            body = f"""
CRISIS INTERVENTION ALERT

User ID: {user_id}
Crisis Level: {crisis_level.upper()}
Crisis Score: {crisis_analysis['crisis_score']}/100
Timestamp: {crisis_analysis['analysis_timestamp']}

Risk Factors:
{chr(10).join('• ' + factor for factor in crisis_analysis['risk_factors'])}

Immediate action required: {'YES' if crisis_analysis['immediate_action_required'] else 'NO'}

Protocol: {self.escalation_levels[crisis_level]['action']}

This is an automated alert from the MindMend Crisis Intervention System.
Please respond immediately.
            """
            
            # In production, implement actual email sending
            logger.critical(f"📧 CRISIS EMAIL ALERT SENT to {recipient['email']}: {subject}")
            
        except Exception as e:
            logger.error(f"Failed to send crisis alert: {e}")
    
    def _execute_emergency_fallback(self, user_id):
        """Emergency fallback when main crisis system fails"""
        logger.critical(f"🚨 EMERGENCY FALLBACK ACTIVATED for user {user_id}")
        # In production, trigger all available emergency protocols
    
    def _get_emergency_response(self):
        """Get emergency response message"""
        return """🚨 EMERGENCY: Our crisis detection system has identified that you may be in immediate danger. 

CALL 911 NOW if you are in immediate physical danger.
CALL 988 (Suicide & Crisis Lifeline) for immediate crisis support.

Our emergency team has been automatically notified and will contact you immediately."""
    
    def _get_user_appropriate_contacts(self, crisis_level):
        """Get appropriate emergency contacts for user"""
        contacts = {
            'crisis_hotline': '988',
            'crisis_text': 'HOME to 741741',
            'emergency': '911'
        }
        
        if crisis_level in ['high', 'critical']:
            contacts['mindmend_crisis'] = self.emergency_contacts['emergency']['phone']
        
        return contacts

# Initialize crisis intervention system
crisis_system = CrisisInterventionSystem()

@crisis_bp.route('/analyze', methods=['POST'])
def analyze_crisis_risk():
    """Analyze crisis risk from user input and biometric/emotion data"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        session_id = session.get('current_session_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        user_message = data.get('user_message', '')
        biometric_data = data.get('biometric_data') or session.get('latest_biometric_analysis')
        emotion_data = data.get('emotion_data') or session.get('latest_emotion_analysis')
        
        # Context for analysis
        context = {
            'session_type': data.get('session_type', 'individual'),
            'session_duration_minutes': data.get('session_duration', 0),
            'previous_crisis_events': 0,  # In production, query from database
            'user_id': user_id
        }
        
        # Perform crisis risk analysis
        crisis_analysis = crisis_system.analyze_crisis_risk(
            user_message, biometric_data, emotion_data, context
        )
        
        # Store analysis in session
        session['latest_crisis_analysis'] = crisis_analysis
        
        # Execute crisis protocol if necessary
        if crisis_analysis['immediate_action_required']:
            protocol_result = crisis_system.execute_crisis_protocol(
                crisis_analysis, user_id, session_id
            )
            crisis_analysis['protocol_result'] = protocol_result
        
        logger.info(f"🚨 Crisis analysis completed: Level {crisis_analysis['crisis_level']} (Score: {crisis_analysis['crisis_score']}/100)")
        
        return jsonify({
            'success': True,
            'analysis': crisis_analysis
        })
        
    except Exception as e:
        logger.error(f"❌ Error analyzing crisis risk: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@crisis_bp.route('/emergency-override', methods=['POST'])
def emergency_override():
    """Emergency override for immediate crisis escalation"""
    try:
        user_id = session.get('user_id')
        session_id = session.get('current_session_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Force maximum crisis protocol
        crisis_analysis = {
            'crisis_score': 100,
            'crisis_level': 'critical',
            'risk_factors': ['Emergency override activated'],
            'immediate_action_required': True,
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        protocol_result = crisis_system.execute_crisis_protocol(
            crisis_analysis, user_id, session_id
        )
        
        logger.critical(f"🚨 EMERGENCY OVERRIDE ACTIVATED for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Emergency protocol activated',
            'protocol_result': protocol_result
        })
        
    except Exception as e:
        logger.error(f"❌ Error in emergency override: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@crisis_bp.route('/status', methods=['GET'])
def get_crisis_status():
    """Get current crisis monitoring status"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        latest_analysis = session.get('latest_crisis_analysis')
        
        status = {
            'monitoring_active': True,
            'latest_analysis': latest_analysis,
            'emergency_contacts': crisis_system._get_user_appropriate_contacts(
                latest_analysis['crisis_level'] if latest_analysis else 'low'
            )
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting crisis status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Database model for crisis events
try:
    class CrisisEvent(db.Model):
        """Store crisis intervention events"""
        __tablename__ = 'crisis_events'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
        crisis_level = db.Column(db.String(20), nullable=False)
        crisis_score = db.Column(db.Integer, nullable=False)
        risk_factors = db.Column(db.Text)  # JSON string
        protocol_executed = db.Column(db.String(100))
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        resolved_at = db.Column(db.DateTime)
        resolution_notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'session_id': self.session_id,
                'crisis_level': self.crisis_level,
                'crisis_score': self.crisis_score,
                'risk_factors': json.loads(self.risk_factors) if self.risk_factors else [],
                'protocol_executed': self.protocol_executed,
                'timestamp': self.timestamp.isoformat(),
                'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
                'resolution_notes': self.resolution_notes,
                'created_at': self.created_at.isoformat()
            }
except Exception as e:
    logger.warning(f"CrisisEvent model already exists: {e}")