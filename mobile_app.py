"""
Mobile App Integration for Mind Mend
===================================
iOS and Android compatibility layer
"""

from flask import Blueprint, jsonify, request, render_template
import jwt
from datetime import datetime, timedelta
import os

mobile_bp = Blueprint('mobile', __name__, url_prefix='/mobile')

class MobileAppIntegration:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        app.register_blueprint(mobile_bp)
        
        # Mobile-specific configuration
        mobile_jwt_secret = os.environ.get('MOBILE_JWT_SECRET')
        if not mobile_jwt_secret:
            raise ValueError("MOBILE_JWT_SECRET environment variable is required")
        app.config['MOBILE_JWT_SECRET'] = mobile_jwt_secret
        app.config['MOBILE_TOKEN_EXPIRY'] = 24 * 7  # 7 days

@mobile_bp.route('/api/health')
def health_check():
    """Health check endpoint for mobile apps"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'features': {
            'ai_therapy': True,
            'video_assessment': True,
            'human_counselors': True,
            'payments': True,
            'biometric_sync': True
        }
    })

@mobile_bp.route('/api/auth/mobile-login', methods=['POST'])
def mobile_login():
    """Mobile-specific authentication endpoint"""
    data = request.get_json()
    
    # Validate mobile credentials
    device_id = data.get('device_id')
    device_type = data.get('device_type')  # 'ios' or 'android'
    fcm_token = data.get('fcm_token')  # For push notifications
    
    if not device_id or not device_type:
        return jsonify({'error': 'Missing device information'}), 400
    
    # Generate mobile JWT token
    token_payload = {
        'device_id': device_id,
        'device_type': device_type,
        'fcm_token': fcm_token,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    
    mobile_jwt_secret = os.environ.get('MOBILE_JWT_SECRET')
    if not mobile_jwt_secret:
        return jsonify({'error': 'Server configuration error'}), 500
    
    token = jwt.encode(
        token_payload, 
        mobile_jwt_secret, 
        algorithm='HS256'
    )
    
    return jsonify({
        'token': token,
        'expires_in': 7 * 24 * 3600,  # 7 days in seconds
        'user_profile': {
            'device_registered': True,
            'push_enabled': bool(fcm_token),
            'app_version': '2.0.0'
        }
    })

@mobile_bp.route('/api/therapy/mobile-session', methods=['POST'])
def mobile_therapy_session():
    """Mobile-optimized therapy session endpoint"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    try:
        token = auth_header.split(' ')[1]
        mobile_jwt_secret = os.environ.get('MOBILE_JWT_SECRET')
        if not mobile_jwt_secret:
            return jsonify({'error': 'Server configuration error'}), 500
            
        payload = jwt.decode(
            token, 
            mobile_jwt_secret, 
            algorithms=['HS256']
        )
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    message = data.get('message', '')
    session_type = data.get('session_type', 'individual')
    
    # Mobile-optimized response format
    response = {
        'ai_response': f"Mobile therapy response for: {message}",
        'session_id': f"mobile_session_{datetime.utcnow().timestamp()}",
        'confidence': 0.95,
        'recommendations': [
            'Take deep breaths',
            'Practice mindfulness',
            'Schedule follow-up session'
        ],
        'mobile_features': {
            'voice_response_available': True,
            'biometric_sync_ready': True,
            'offline_exercises': [
                'Breathing exercise',
                'Gratitude journal',
                'Progressive muscle relaxation'
            ]
        }
    }
    
    return jsonify(response)

@mobile_bp.route('/api/payments/mobile-checkout', methods=['POST'])
def mobile_payment_checkout():
    """Mobile payment integration"""
    data = request.get_json()
    payment_method = data.get('payment_method')  # 'apple_pay', 'google_pay', 'card'
    amount = data.get('amount')
    currency = data.get('currency', 'AUD')
    
    # Mobile payment response
    return jsonify({
        'checkout_session': {
            'session_id': f"mobile_checkout_{datetime.utcnow().timestamp()}",
            'amount': amount,
            'currency': currency,
            'payment_methods': {
                'apple_pay': payment_method == 'apple_pay',
                'google_pay': payment_method == 'google_pay',
                'card': True
            },
            'success_url': 'mindmend://payment/success',
            'cancel_url': 'mindmend://payment/cancel'
        }
    })

@mobile_bp.route('/api/biometric/sync', methods=['POST'])
def sync_biometric_data():
    """Sync biometric data from mobile devices"""
    data = request.get_json()
    
    biometric_data = {
        'heart_rate': data.get('heart_rate'),
        'steps': data.get('steps'),
        'sleep_hours': data.get('sleep_hours'),
        'stress_level': data.get('stress_level'),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify({
        'sync_status': 'success',
        'data_points_received': len([v for v in biometric_data.values() if v is not None]),
        'next_sync': (datetime.utcnow() + timedelta(hours=1)).isoformat()
    })

@mobile_bp.route('/download/ios')
def ios_download():
    """iOS App Store redirect"""
    return render_template('mobile/ios_download.html', 
                         app_id="au.com.sticky.mindmend")

@mobile_bp.route('/download/android')
def android_download():
    """Google Play Store redirect"""
    return render_template('mobile/android_download.html', 
                         package_name="au.com.sticky.mindmend")

# Progressive Web App (PWA) Support
@mobile_bp.route('/manifest.json')
def pwa_manifest():
    """PWA manifest for mobile web app"""
    return jsonify({
        "name": "Mind Mend - Mental Health Platform",
        "short_name": "Mind Mend",
        "description": "AI-powered mental health therapy platform by Sticky Pty Ltd",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#764ba2",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/static/icons/icon-192x192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/icons/icon-512x512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ],
        "categories": ["health", "medical", "lifestyle"],
        "lang": "en-AU"
    })

@mobile_bp.route('/sw.js')
def service_worker():
    """Service worker for PWA offline functionality"""
    return render_template('mobile/service-worker.js'), 200, {
        'Content-Type': 'application/javascript'
    }