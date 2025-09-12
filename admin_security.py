"""
Enhanced Admin Panel Security Module
====================================
Advanced security measures for MindMend admin panel access
"""

import os
import hmac
import hashlib
import time
import ipaddress
from datetime import datetime, timedelta
from functools import wraps
from flask import request, session, jsonify, abort, flash, redirect, url_for
import pyotp
import qrcode
import io
import base64
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class AdminSecurity:
    def __init__(self, app=None):
        self.app = app
        self.admin_sessions = {}
        self.failed_attempts = {}
        self.ip_whitelist = set()
        self.two_factor_secrets = {}
        
        # Load IP whitelist from environment
        whitelist_ips = os.environ.get('ADMIN_IP_WHITELIST', '').split(',')
        for ip in whitelist_ips:
            if ip.strip():
                try:
                    self.ip_whitelist.add(ipaddress.ip_network(ip.strip(), strict=False))
                except:
                    logger.warning(f"Invalid IP in whitelist: {ip}")
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.admin_secret = app.config.get('ADMIN_SECRET_KEY', os.urandom(32))
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def generate_admin_token(self, admin_id: str) -> str:
        """Generate secure admin session token"""
        timestamp = str(int(time.time()))
        data = f"{admin_id}:{timestamp}"
        signature = hmac.new(
            self.admin_secret.encode() if isinstance(self.admin_secret, str) else self.admin_secret,
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{data}:{signature}"
    
    def verify_admin_token(self, token: str) -> dict:
        """Verify admin session token"""
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return None
            
            admin_id, timestamp, signature = parts
            data = f"{admin_id}:{timestamp}"
            
            expected_signature = hmac.new(
                self.admin_secret.encode() if isinstance(self.admin_secret, str) else self.admin_secret,
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            # Check if token is expired (24 hour limit)
            if int(time.time()) - int(timestamp) > 86400:
                return None
            
            return {
                'admin_id': admin_id,
                'timestamp': int(timestamp),
                'valid': True
            }
        except:
            return None
    
    def is_ip_whitelisted(self, ip_address: str) -> bool:
        """Check if IP is in whitelist"""
        if not self.ip_whitelist:
            return True  # No whitelist configured, allow all
        
        try:
            ip = ipaddress.ip_address(ip_address)
            for network in self.ip_whitelist:
                if ip in network:
                    return True
            return False
        except:
            return False
    
    def check_rate_limit(self, identifier: str, max_attempts: int = 5, window: int = 900) -> bool:
        """Check if identifier is rate limited"""
        now = time.time()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Clean old attempts
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier]
            if now - attempt < window
        ]
        
        return len(self.failed_attempts[identifier]) < max_attempts
    
    def record_failed_attempt(self, identifier: str):
        """Record a failed authentication attempt"""
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        self.failed_attempts[identifier].append(time.time())
        logger.warning(f"Failed admin authentication attempt from {identifier}")
    
    def setup_2fa(self, admin_id: str) -> dict:
        """Setup two-factor authentication for admin"""
        secret = pyotp.random_base32()
        self.two_factor_secrets[admin_id] = secret
        
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=f"MindMend Admin ({admin_id})",
            issuer_name="MindMend"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return {
            'secret': secret,
            'qr_code': qr_code_base64,
            'manual_entry_key': secret
        }
    
    def verify_2fa(self, admin_id: str, token: str) -> bool:
        """Verify 2FA token"""
        if admin_id not in self.two_factor_secrets:
            return False
        
        secret = self.two_factor_secrets[admin_id]
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Initialize security manager
admin_security = AdminSecurity()

def require_admin_auth(f):
    """Decorator to require admin authentication with enhanced security"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if request is from admin subdomain
        if not request.headers.get('X-Admin-Request'):
            if not request.host.startswith('admin.'):
                abort(403)
        
        # IP whitelist check
        client_ip = request.headers.get('X-Real-IP', request.remote_addr)
        if not admin_security.is_ip_whitelisted(client_ip):
            logger.warning(f"Admin access denied for IP: {client_ip}")
            abort(403)
        
        # Rate limiting check
        if not admin_security.check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for admin access from IP: {client_ip}")
            abort(429)
        
        # Check admin session
        admin_token = session.get('admin_token')
        if not admin_token:
            admin_security.record_failed_attempt(client_ip)
            flash('Admin authentication required', 'error')
            return redirect(url_for('admin_auth_required'))
        
        # Verify token
        token_data = admin_security.verify_admin_token(admin_token)
        if not token_data:
            admin_security.record_failed_attempt(client_ip)
            session.pop('admin_token', None)
            flash('Invalid or expired admin session', 'error')
            return redirect(url_for('admin_auth_required'))
        
        # Check 2FA if enabled
        if token_data['admin_id'] in admin_security.two_factor_secrets:
            if not session.get('admin_2fa_verified'):
                return redirect(url_for('admin_2fa_verify'))
        
        # Store admin info for request
        request.admin_id = token_data['admin_id']
        request.admin_authenticated = True
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_super_admin(f):
    """Decorator for super admin only functions"""
    @require_admin_auth
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is super admin (you can customize this logic)
        if request.admin_id != os.environ.get('SUPER_ADMIN_ID', 'super_admin'):
            logger.warning(f"Super admin access denied for user: {request.admin_id}")
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function

def log_admin_action(action: str, details: dict = None):
    """Log admin actions for audit trail"""
    admin_id = getattr(request, 'admin_id', 'unknown')
    client_ip = request.headers.get('X-Real-IP', request.remote_addr)
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'admin_id': admin_id,
        'ip_address': client_ip,
        'action': action,
        'user_agent': request.headers.get('User-Agent', ''),
        'details': details or {}
    }
    
    logger.info(f"Admin action: {log_entry}")
    
    # You can also store this in database for persistent audit trail
    # audit_log.create_log_entry(log_entry)

class AdminAuditLogger:
    """Audit logger for admin actions"""
    
    @staticmethod
    def log_login(admin_id: str, success: bool, ip_address: str):
        """Log admin login attempts"""
        log_admin_action('admin_login', {
            'admin_id': admin_id,
            'success': success,
            'ip_address': ip_address
        })
    
    @staticmethod
    def log_user_action(action: str, target_user_id: str, details: dict = None):
        """Log actions performed on users"""
        log_admin_action('user_management', {
            'action': action,
            'target_user_id': target_user_id,
            'details': details
        })
    
    @staticmethod
    def log_system_change(change_type: str, details: dict = None):
        """Log system configuration changes"""
        log_admin_action('system_change', {
            'change_type': change_type,
            'details': details
        })
    
    @staticmethod
    def log_data_access(data_type: str, record_count: int = None):
        """Log data access events"""
        log_admin_action('data_access', {
            'data_type': data_type,
            'record_count': record_count
        })