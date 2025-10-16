"""
Crisis Detection Integration
Integrates universal crisis predictor with Flask routes
"""

import logging
import asyncio
from flask import Blueprint, request, jsonify, session
from flask_login import current_user
from datetime import datetime
from models.universal_crisis_predictor import crisis_predictor, CrisisSeverity
from models.database import Session as TherapySession, Patient, db
import json

logger = logging.getLogger(__name__)

crisis_bp = Blueprint('crisis', __name__)

def get_user_tier():
    """Get current user's subscription tier"""
    if not current_user.is_authenticated:
        return 'free'

    # Map subscription types to tiers
    tier_map = {
        'free': 'free',
        'basic': 'basic',
        'premium': 'premium',
        'enterprise': 'enterprise'
    }

    return tier_map.get(current_user.subscription_type, 'free')

def get_user_context():
    """Get context about current user for better prediction"""
    context = {
        'session_id': session.get('session_id', 'unknown'),
        'timestamp': datetime.now().isoformat()
    }

    if current_user.is_authenticated:
        # Get user history
        recent_sessions = TherapySession.query.filter_by(
            user_id=current_user.id
        ).order_by(TherapySession.created_at.desc()).limit(10).all()

        # Check for recent crises
        recent_crisis = any(
            s.metadata and json.loads(s.metadata).get('crisis_detected', False)
            for s in recent_sessions if s.metadata
        )

        context.update({
            'user_id': current_user.id,
            'session_count': len(recent_sessions),
            'recent_crisis': recent_crisis,
            'user_age': getattr(current_user, 'age', None),
            'days_since_last_crisis': 30  # Default, would calculate in production
        })

    return context

@crisis_bp.route('/api/crisis/check', methods=['POST'])
async def check_for_crisis():
    """
    Check text for crisis indicators
    Endpoint for real-time crisis detection
    """
    try:
        data = request.get_json()
        text = data.get('text', '')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Get user tier and context
        user_tier = get_user_tier()
        context = get_user_context()

        # Run crisis detection
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        prediction = loop.run_until_complete(
            crisis_predictor.predict_crisis(
                text=text,
                user_tier=user_tier,
                context=context,
                force_free=(user_tier == 'free')
            )
        )

        # Log to database if crisis detected
        if prediction.is_crisis:
            logger.warning(f"CRISIS DETECTED - User: {context.get('user_id', 'anonymous')}, "
                         f"Severity: {prediction.severity.value}, "
                         f"Confidence: {prediction.confidence:.2%}")

            # Store in session metadata
            if current_user.is_authenticated:
                therapy_session = TherapySession.query.filter_by(
                    user_id=current_user.id
                ).order_by(TherapySession.created_at.desc()).first()

                if therapy_session:
                    metadata = json.loads(therapy_session.metadata or '{}')
                    metadata['crisis_detected'] = True
                    metadata['crisis_severity'] = prediction.severity.value
                    metadata['crisis_confidence'] = prediction.confidence
                    metadata['crisis_timestamp'] = datetime.now().isoformat()
                    therapy_session.metadata = json.dumps(metadata)
                    db.session.commit()

            # Trigger alerts for critical cases
            if prediction.severity == CrisisSeverity.CRITICAL:
                await trigger_crisis_alert(context, prediction)

        # Prepare response
        response = {
            'is_crisis': prediction.is_crisis,
            'severity': prediction.severity.value,
            'confidence': prediction.confidence,
            'risk_factors': prediction.risk_factors,
            'recommended_actions': prediction.recommended_actions,
            'requires_human_review': prediction.requires_human_review,
            'response_time_ms': prediction.latency * 1000
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Crisis check error: {e}")
        return jsonify({'error': 'Crisis check failed'}), 500

@crisis_bp.route('/api/crisis/resources', methods=['GET'])
def get_crisis_resources():
    """Get crisis resources based on location and severity"""

    severity = request.args.get('severity', 'medium')
    country = request.args.get('country', 'US')

    resources = {
        'hotlines': get_crisis_hotlines(country),
        'immediate_help': get_immediate_help_steps(severity),
        'coping_strategies': get_coping_strategies(severity),
        'safety_plan_template': get_safety_plan_template()
    }

    return jsonify(resources), 200

async def trigger_crisis_alert(context: dict, prediction):
    """
    Trigger alerts for critical crisis situations
    """
    alert_data = {
        'user_id': context.get('user_id', 'anonymous'),
        'severity': prediction.severity.value,
        'confidence': prediction.confidence,
        'timestamp': datetime.now().isoformat(),
        'risk_factors': prediction.risk_factors
    }

    # In production, this would:
    # 1. Notify on-call therapist
    # 2. Send SMS/email to emergency contact
    # 3. Log to monitoring system
    # 4. Queue for immediate follow-up

    logger.critical(f"CRISIS ALERT: {json.dumps(alert_data)}")

    # Store alert in database
    if context.get('user_id'):
        # Would create alert record in production
        pass

def get_crisis_hotlines(country='US'):
    """Get crisis hotlines by country"""
    hotlines = {
        'US': [
            {
                'name': '988 Suicide & Crisis Lifeline',
                'number': '988',
                'text': 'Text HOME to 741741',
                'hours': '24/7',
                'description': 'Free, confidential crisis support'
            },
            {
                'name': 'SAMHSA National Helpline',
                'number': '1-800-662-4357',
                'hours': '24/7',
                'description': 'Treatment referral and information'
            }
        ],
        'UK': [
            {
                'name': 'Samaritans',
                'number': '116 123',
                'hours': '24/7',
                'description': 'Emotional support'
            }
        ],
        'AU': [
            {
                'name': 'Lifeline',
                'number': '13 11 14',
                'hours': '24/7',
                'description': 'Crisis support and suicide prevention'
            }
        ],
        'CA': [
            {
                'name': 'Talk Suicide Canada',
                'number': '1-833-456-4566',
                'text': 'Text 45645',
                'hours': '24/7',
                'description': 'Suicide prevention support'
            }
        ]
    }

    return hotlines.get(country, hotlines['US'])

def get_immediate_help_steps(severity):
    """Get immediate help steps based on severity"""
    steps = {
        'critical': [
            'Call emergency services (911/999/112) if in immediate danger',
            'Go to nearest emergency room',
            'Call crisis hotline immediately',
            'Stay with someone you trust',
            'Remove access to means of harm'
        ],
        'high': [
            'Call crisis hotline for immediate support',
            'Contact your therapist or doctor urgently',
            'Reach out to trusted friend or family member',
            'Use your safety plan if you have one',
            'Avoid being alone'
        ],
        'medium': [
            'Schedule urgent appointment with therapist',
            'Practice crisis coping strategies',
            'Connect with support network',
            'Use grounding techniques',
            'Monitor your feelings closely'
        ],
        'low': [
            'Continue regular therapy',
            'Practice self-care activities',
            'Maintain routine',
            'Use coping skills',
            'Check in with support system'
        ]
    }

    return steps.get(severity, steps['medium'])

def get_coping_strategies(severity):
    """Get coping strategies based on severity"""
    return [
        {
            'name': '5-4-3-2-1 Grounding',
            'description': 'Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste',
            'duration': '5 minutes'
        },
        {
            'name': 'Box Breathing',
            'description': 'Breathe in 4, hold 4, out 4, hold 4',
            'duration': '3-5 minutes'
        },
        {
            'name': 'Ice Technique',
            'description': 'Hold ice cube, splash cold water on face',
            'duration': 'Immediate'
        },
        {
            'name': 'TIPP',
            'description': 'Temperature, Intense exercise, Paced breathing, Paired muscle relaxation',
            'duration': '10-15 minutes'
        }
    ]

def get_safety_plan_template():
    """Get safety plan template"""
    return {
        'warning_signs': [
            'Thoughts that concern me',
            'Situations that trigger me',
            'Changes in my mood or behavior'
        ],
        'coping_strategies': [
            'Things I can do alone to feel better',
            'Healthy distractions',
            'Relaxation techniques that work for me'
        ],
        'support_contacts': [
            'Friends I can reach out to',
            'Family members who understand',
            'Professional contacts (therapist, doctor)'
        ],
        'crisis_contacts': [
            'Crisis hotline numbers',
            'Emergency services',
            'Hospital information'
        ],
        'safe_environment': [
            'Remove or secure harmful items',
            'Identify safe spaces',
            'Plan where to go if home unsafe'
        ],
        'reasons_for_living': [
            'People who matter to me',
            'Goals I want to achieve',
            'Things that give me hope'
        ]
    }

# Middleware to check all therapy messages
def check_message_for_crisis(message):
    """
    Middleware function to check all messages for crisis
    Can be integrated into existing chat/session routes
    """
    if not message:
        return None

    # Quick pre-check for efficiency
    crisis_keywords = ['suicide', 'kill', 'die', 'hurt myself', 'end it']
    if not any(keyword in message.lower() for keyword in crisis_keywords):
        return None

    # Full check if keywords found
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    prediction = loop.run_until_complete(
        crisis_predictor.predict_crisis(
            text=message,
            user_tier='free',
            context={},
            force_free=True
        )
    )

    return prediction if prediction.is_crisis else None