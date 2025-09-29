"""
Payment Security Module for MindMend
===================================
Enhanced security features for payment processing and fraud prevention
"""

import hashlib
import hmac
import secrets
import time
import json
import logging
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify, current_app, session
from flask_login import current_user
from cryptography.fernet import Fernet
from models.database import db, User, Payment, Subscription
import stripe

logger = logging.getLogger(__name__)

class PaymentSecurityManager:
    """Comprehensive payment security management"""
    
    def __init__(self, app=None):
        self.app = app
        self.fernet_key = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security manager with Flask app"""
        self.app = app
        # Generate or load encryption key
        self.fernet_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.fernet_key)
        
    def _get_or_create_encryption_key(self):
        """Get or create encryption key for payment data"""
        key = current_app.config.get('PAYMENT_ENCRYPTION_KEY')
        if not key:
            # Generate new key - in production, store this securely
            key = Fernet.generate_key()
            current_app.config['PAYMENT_ENCRYPTION_KEY'] = key
            logger.warning("Generated new encryption key - store securely in production")
        return key
    
    def encrypt_payment_data(self, data):
        """Encrypt sensitive payment data"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            elif not isinstance(data, (str, bytes)):
                data = str(data)
            
            if isinstance(data, str):
                data = data.encode()
            
            encrypted = self.cipher.encrypt(data)
            return encrypted.decode() if isinstance(encrypted, bytes) else encrypted
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt_payment_data(self, encrypted_data):
        """Decrypt payment data"""
        try:
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode()
            
            decrypted = self.cipher.decrypt(encrypted_data)
            return decrypted.decode() if isinstance(decrypted, bytes) else decrypted
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def verify_stripe_webhook(self, payload, signature):
        """Verify Stripe webhook signature"""
        try:
            endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
            if not endpoint_secret:
                logger.error("Stripe webhook secret not configured")
                return False
            
            stripe.Webhook.construct_event(
                payload, signature, endpoint_secret
            )
            return True
        except stripe.error.SignatureVerificationError:
            logger.warning("Invalid Stripe webhook signature")
            return False
        except Exception as e:
            logger.error(f"Webhook verification error: {e}")
            return False
    
    def generate_payment_token(self, user_id, amount, currency='USD'):
        """Generate secure payment token"""
        timestamp = int(time.time())
        token_data = {
            'user_id': user_id,
            'amount': amount,
            'currency': currency,
            'timestamp': timestamp,
            'expires': timestamp + 3600,  # 1 hour
            'nonce': secrets.token_hex(16)
        }
        
        # Create signature
        token_string = json.dumps(token_data, sort_keys=True)
        signature = self._create_signature(token_string)
        
        return {
            'token': self.encrypt_payment_data(token_data),
            'signature': signature
        }
    
    def verify_payment_token(self, token, signature):
        """Verify payment token validity"""
        try:
            # Decrypt token
            token_data = json.loads(self.decrypt_payment_data(token))
            
            # Verify signature
            token_string = json.dumps(token_data, sort_keys=True)
            if not self._verify_signature(token_string, signature):
                return None
            
            # Check expiration
            if token_data['expires'] < int(time.time()):
                logger.warning("Payment token expired")
                return None
            
            return token_data
            
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def _create_signature(self, data):
        """Create HMAC signature for data"""
        secret = current_app.config.get('SECRET_KEY', '').encode()
        if isinstance(data, str):
            data = data.encode()
        return hmac.new(secret, data, hashlib.sha256).hexdigest()
    
    def _verify_signature(self, data, signature):
        """Verify HMAC signature"""
        expected = self._create_signature(data)
        return hmac.compare_digest(expected, signature)

class FraudDetection:
    """Fraud detection and prevention system"""
    
    @staticmethod
    def analyze_payment(user, amount, payment_method=None):
        """Analyze payment for fraud indicators"""
        risk_score = 0
        warnings = []
        
        # Check user payment history
        recent_payments = Payment.query.filter(
            Payment.user_id == user.id,
            Payment.created_at > datetime.now(timezone.utc) - timedelta(hours=24)
        ).all()
        
        # Rapid payment frequency check
        if len(recent_payments) > 5:
            risk_score += 30
            warnings.append("Multiple payments in 24h")
        
        # Amount anomaly detection
        if user.subscription:
            typical_amount = user.subscription.price_per_month or 0
            if amount > typical_amount * 10:
                risk_score += 25
                warnings.append("Unusually large payment amount")
        
        # New user check
        if user.created_at > datetime.now(timezone.utc) - timedelta(days=7):
            if amount > 100:
                risk_score += 15
                warnings.append("Large payment from new user")
        
        # Geographic anomaly (would need IP geolocation in production)
        # IP-based checks would go here
        
        return {
            'risk_score': risk_score,
            'risk_level': 'high' if risk_score > 50 else 'medium' if risk_score > 25 else 'low',
            'warnings': warnings,
            'approved': risk_score < 75
        }
    
    @staticmethod
    def log_fraud_attempt(user_id, details, risk_score):
        """Log potential fraud attempt"""
        logger.warning(f"Fraud alert - User {user_id}: {details} (Risk: {risk_score})")
        
        # In production, would store in fraud detection database
        fraud_log = {
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'details': details,
            'risk_score': risk_score,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None
        }
        
        # Store in database or external fraud detection service
        current_app.logger.critical(f"FRAUD_ALERT: {json.dumps(fraud_log)}")

def require_payment_auth(f):
    """Decorator to require authentication for payment operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user account is locked
        if hasattr(current_user, 'is_locked') and current_user.is_locked:
            return jsonify({'error': 'Account locked'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_payments(max_attempts=5, window=3600):
    """Rate limiting decorator for payment operations"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return f(*args, **kwargs)
            
            # Check rate limit in session or cache
            key = f"payment_attempts_{current_user.id}"
            attempts = session.get(key, [])
            
            # Clean old attempts
            now = time.time()
            attempts = [t for t in attempts if now - t < window]
            
            if len(attempts) >= max_attempts:
                return jsonify({
                    'error': 'Too many payment attempts. Please try again later.',
                    'retry_after': int(window - (now - min(attempts)))
                }), 429
            
            # Record this attempt
            attempts.append(now)
            session[key] = attempts
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class PaymentAuditLogger:
    """Comprehensive payment audit logging"""
    
    @staticmethod
    def log_payment_event(event_type, user_id, details, severity='info'):
        """Log payment-related events"""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details,
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'session_id': session.get('_id') if session else None
        }
        
        log_message = f"PAYMENT_AUDIT: {json.dumps(log_entry)}"
        
        if severity == 'critical':
            logger.critical(log_message)
        elif severity == 'warning':
            logger.warning(log_message)
        elif severity == 'error':
            logger.error(log_message)
        else:
            logger.info(log_message)
    
    @staticmethod
    def log_subscription_change(user, old_tier, new_tier, reason):
        """Log subscription tier changes"""
        PaymentAuditLogger.log_payment_event(
            'subscription_change',
            user.id,
            {
                'old_tier': old_tier,
                'new_tier': new_tier,
                'reason': reason,
                'user_email': user.email
            },
            'info'
        )
    
    @staticmethod
    def log_payment_failure(user_id, amount, error_details):
        """Log payment failures"""
        PaymentAuditLogger.log_payment_event(
            'payment_failure',
            user_id,
            {
                'amount': amount,
                'error': error_details
            },
            'warning'
        )

# PCI DSS Compliance helpers
class PCICompliance:
    """PCI DSS compliance utilities"""
    
    @staticmethod
    def mask_card_number(card_number):
        """Mask credit card number for logging"""
        if not card_number or len(card_number) < 4:
            return "****"
        return f"****-****-****-{card_number[-4:]}"
    
    @staticmethod
    def sanitize_payment_data(data):
        """Remove sensitive payment data for logging"""
        sensitive_fields = [
            'card_number', 'cvv', 'cvc', 'security_code',
            'exp_month', 'exp_year', 'routing_number', 'account_number'
        ]
        
        if isinstance(data, dict):
            sanitized = data.copy()
            for field in sensitive_fields:
                if field in sanitized:
                    sanitized[field] = "REDACTED"
            return sanitized
        return data
    
    @staticmethod
    def validate_payment_environment():
        """Validate PCI compliance environment settings"""
        issues = []
        
        if not current_app.config.get('SECRET_KEY'):
            issues.append("SECRET_KEY not configured")
        
        if not current_app.config.get('STRIPE_SECRET_KEY'):
            issues.append("Stripe secret key not configured")
        
        if current_app.debug:
            issues.append("Debug mode enabled in production")
        
        return issues

# Initialize security manager
payment_security = PaymentSecurityManager()