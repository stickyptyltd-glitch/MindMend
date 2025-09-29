"""
Security Enhancements for Mind Mend
==================================
HIPAA compliance, fraud protection, and security features
"""

from flask import request, session, abort
from functools import wraps
import hashlib
import hmac
import time
import logging
import re
from datetime import datetime, timedelta
import json
import os

class SecurityManager:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
        
        # Security configuration
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 minutes
        self.session_timeout = 3600  # 1 hour
        self.failed_attempts = {}
        self.blocked_ips = set()
        
        # HIPAA compliance settings
        self.audit_log = []
        self.data_retention_days = 2555  # 7 years
        self.encryption_key = os.environ.get('ENCRYPTION_KEY', 'dev-key')
        
    def init_app(self, app):
        """Initialize security with Flask app"""
        app.before_request(self.before_request_security)
        app.after_request(self.after_request_security)
        
        # Set secure headers
        @app.after_request
        def set_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://js.stripe.com https://www.paypal.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self' https://api.stripe.com https://api.paypal.com; "
                "frame-src https://js.stripe.com https://www.paypal.com;"
            )
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response.headers['Permissions-Policy'] = (
                "camera=(), microphone=(), geolocation=(), "
                "payment=(), usb=(), serial=(), bluetooth=()"
            )
            return response
    
    def before_request_security(self):
        """Run security checks before each request"""
        # Check if IP is blocked
        client_ip = self.get_client_ip()
        if client_ip in self.blocked_ips:
            self.log_security_event('blocked_ip_attempt', {
                'ip': client_ip,
                'user_agent': request.headers.get('User-Agent', ''),
                'timestamp': datetime.utcnow().isoformat()
            })
            abort(403)
        
        # Rate limiting check
        if self.is_rate_limited(client_ip):
            abort(429)
        
        # Session timeout check
        if 'last_activity' in session:
            last_activity = datetime.fromisoformat(session['last_activity'])
            if datetime.utcnow() - last_activity > timedelta(seconds=self.session_timeout):
                session.clear()
                self.log_security_event('session_timeout', {
                    'ip': client_ip,
                    'last_activity': session.get('last_activity')
                })
        
        session['last_activity'] = datetime.utcnow().isoformat()
    
    def after_request_security(self, response):
        """Run security checks after each request"""
        # Log sensitive operations
        if request.endpoint and any(sensitive in request.endpoint for sensitive in 
                                  ['payment', 'session', 'counselor', 'dashboard']):
            self.log_audit_event(request.endpoint, {
                'method': request.method,
                'ip': self.get_client_ip(),
                'user': session.get('user_id', 'anonymous'),
                'timestamp': datetime.utcnow().isoformat(),
                'status_code': response.status_code
            })
        
        return response
    
    def get_client_ip(self):
        """Get real client IP address"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def is_rate_limited(self, ip):
        """Check if IP is rate limited"""
        current_time = time.time()
        window = 60  # 1 minute window
        max_requests = 100  # Max requests per minute
        
        # Clean old entries
        if ip in self.failed_attempts:
            self.failed_attempts[ip] = [
                timestamp for timestamp in self.failed_attempts[ip]
                if current_time - timestamp < window
            ]
        
        # Check if over limit
        if ip in self.failed_attempts and len(self.failed_attempts[ip]) >= max_requests:
            return True
        
        # Add current request
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
        self.failed_attempts[ip].append(current_time)
        
        return False
    
    def log_security_event(self, event_type, data):
        """Log security events"""
        security_event = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data,
            'severity': self.get_event_severity(event_type)
        }
        
        logging.warning(f"Security Event: {json.dumps(security_event)}")
        
        # Store in audit log
        self.audit_log.append(security_event)
        
        # Alert on high severity events
        if security_event['severity'] == 'high':
            self.send_security_alert(security_event)
    
    def log_audit_event(self, action, data):
        """Log HIPAA audit events"""
        audit_event = {
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data,
            'hipaa_relevant': self.is_hipaa_relevant(action)
        }
        
        logging.info(f"Audit Log: {json.dumps(audit_event)}")
        self.audit_log.append(audit_event)
    
    def get_event_severity(self, event_type):
        """Determine event severity"""
        high_severity = [
            'blocked_ip_attempt', 'multiple_failed_logins', 
            'unauthorized_access', 'data_breach_attempt'
        ]
        medium_severity = [
            'failed_login', 'session_timeout', 'invalid_token'
        ]
        
        if event_type in high_severity:
            return 'high'
        elif event_type in medium_severity:
            return 'medium'
        else:
            return 'low'
    
    def is_hipaa_relevant(self, action):
        """Check if action is HIPAA relevant"""
        hipaa_actions = [
            'session', 'counselor', 'payment', 'dashboard',
            'health_data', 'client_info', 'medical_record'
        ]
        return any(hipaa_action in action.lower() for hipaa_action in hipaa_actions)
    
    def send_security_alert(self, event):
        """Send security alert to administrators"""
        # In production, integrate with alerting system (email, Slack, PagerDuty)
        logging.critical(f"HIGH SEVERITY SECURITY ALERT: {json.dumps(event)}")
    
    def validate_phone_number(self, phone, country_code='AU'):
        """Validate phone number format by country"""
        patterns = {
            'AU': r'^(\+61|61|0)[2-9]\d{8}$',  # Australian format
            'US': r'^(\+1|1)?[2-9]\d{2}[2-9]\d{2}\d{4}$',  # US format
            'UK': r'^(\+44|44|0)[1-9]\d{8,9}$',  # UK format
            'CA': r'^(\+1|1)?[2-9]\d{2}[2-9]\d{2}\d{4}$'  # Canadian format
        }
        
        pattern = patterns.get(country_code, patterns['AU'])
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))
    
    def format_phone_number(self, phone, country_code='AU'):
        """Format phone number by country"""
        # Remove all non-digit characters except +
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        if country_code == 'AU':
            # Australian format: +61 2 xxxx xxxx or 0x xxxx xxxx
            if clean_phone.startswith('+61'):
                return f"+61 {clean_phone[3:4]} {clean_phone[4:8]} {clean_phone[8:]}"
            elif clean_phone.startswith('61'):
                return f"+61 {clean_phone[2:3]} {clean_phone[3:7]} {clean_phone[7:]}"
            elif clean_phone.startswith('0'):
                return f"{clean_phone[0]} {clean_phone[1:2]} {clean_phone[2:6]} {clean_phone[6:]}"
        
        return phone  # Return original if can't format
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data for HIPAA compliance"""
        if isinstance(data, str):
            data = data.encode()
        
        # In production, use proper encryption library like cryptography
        # This is a simplified example
        key = self.encryption_key.encode()
        encrypted = hmac.new(key, data, hashlib.sha256).hexdigest()
        return encrypted
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data"""
        # In production, implement proper decryption
        # This is a placeholder for the decryption logic
        return "[ENCRYPTED_DATA]"
    
    def validate_australian_business_number(self, abn):
        """Validate Australian Business Number (ABN)"""
        if not abn or len(abn) != 11:
            return False
        
        try:
            # ABN validation algorithm
            weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
            abn_digits = [int(d) for d in abn]
            abn_digits[0] -= 1  # Subtract 1 from first digit
            
            total = sum(digit * weight for digit, weight in zip(abn_digits, weights))
            return total % 89 == 0
        except (ValueError, IndexError):
            return False

# Decorators for security

def require_https(f):
    """Require HTTPS for sensitive endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not request.headers.get('X-Forwarded-Proto') == 'https':
            if os.environ.get('FLASK_ENV') == 'production':
                return redirect(request.url.replace('http://', 'https://'))
        return f(*args, **kwargs)
    return decorated_function

def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'counselor_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def audit_log(action):
    """Decorator to log actions for HIPAA compliance"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Log the action
            logging.info(f"HIPAA Audit: {action} by {session.get('user_id', 'anonymous')} at {datetime.utcnow()}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_csrf_token(f):
    """Validate CSRF token for state-changing operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            expected_token = session.get('csrf_token')
            
            if not token or not expected_token or token != expected_token:
                abort(403, 'CSRF token validation failed')
        
        return f(*args, **kwargs)
    return decorated_function

# Fraud protection utilities

class FraudProtection:
    def __init__(self):
        self.suspicious_patterns = []
        self.risk_scores = {}
    
    def analyze_payment_risk(self, payment_data):
        """Analyze payment for fraud risk"""
        risk_score = 0
        risk_factors = []
        
        # Check for suspicious patterns
        if payment_data.get('amount', 0) > 1000:
            risk_score += 10
            risk_factors.append('High amount')
        
        # Check IP geolocation vs billing address
        if self.check_ip_mismatch(payment_data):
            risk_score += 20
            risk_factors.append('IP/Billing mismatch')
        
        # Check for rapid repeated attempts
        if self.check_rapid_attempts(payment_data):
            risk_score += 30
            risk_factors.append('Rapid attempts')
        
        return {
            'risk_score': risk_score,
            'risk_level': 'high' if risk_score > 50 else 'medium' if risk_score > 20 else 'low',
            'risk_factors': risk_factors,
            'recommended_action': 'block' if risk_score > 70 else 'review' if risk_score > 40 else 'approve'
        }
    
    def check_ip_mismatch(self, payment_data):
        """Check if IP and billing address match geographically"""
        # In production, use IP geolocation service
        return False  # Placeholder
    
    def check_rapid_attempts(self, payment_data):
        """Check for rapid payment attempts"""
        # In production, check against recent payment attempts
        return False  # Placeholder

# Copyright and legal protection

class LegalProtection:
    def __init__(self):
        self.company_info = {
            'name': 'Sticky Pty Ltd',
            'abn': '12345678901',  # Replace with actual ABN
            'address': 'Suite 123, Level 45, Sydney CBD, NSW 2000, Australia',
            'phone': '+61 2 9000 0000',
            'email': 'legal@sticky.com.au'
        }
    
    def generate_copyright_notice(self):
        """Generate copyright notice"""
        current_year = datetime.now().year
        return f"© {current_year} {self.company_info['name']}. All rights reserved."
    
    def generate_privacy_policy_summary(self):
        """Generate privacy policy summary"""
        return {
            'data_collection': 'We collect health information to provide therapy services',
            'data_use': 'Data used only for treatment and platform improvement',
            'data_sharing': 'Never shared without consent except as required by law',
            'data_retention': '7 years as per HIPAA requirements',
            'user_rights': 'Access, correct, delete, or export your data',
            'contact': self.company_info['email']
        }
    
    def generate_terms_of_service_key_points(self):
        """Generate key terms of service points"""
        return {
            'service_description': 'AI-powered mental health therapy platform',
            'user_obligations': 'Provide accurate information, follow treatment plans',
            'platform_obligations': 'Provide secure, confidential therapy services',
            'liability_limits': 'Limited to amount paid for services',
            'governing_law': 'Laws of New South Wales, Australia',
            'dispute_resolution': 'Mediation followed by arbitration if needed'
        }