"""
Role-Based Security System for Mind Mend
=======================================
Implements different security classes for Admin, Management, and Counselors
"""

from functools import wraps
from flask import session, redirect, url_for, abort, request
import hashlib
import secrets
from datetime import datetime, timedelta

class SecurityRoles:
    # Define role hierarchy and permissions
    ROLES = {
        'super_admin': {
            'level': 100,
            'permissions': [
                'view_all_data', 'edit_all_data', 'delete_all_data',
                'manage_api_keys', 'manage_platform_settings', 'manage_users',
                'view_financial_data', 'manage_counselors', 'system_configuration',
                'deploy_updates', 'access_logs', 'manage_security', 'fraud_detection'
            ],
            'session_timeout': 30,  # minutes
            'require_2fa': True,
            'ip_whitelist': True
        },
        'admin': {
            'level': 90,
            'permissions': [
                'view_all_data', 'edit_most_data', 'manage_users',
                'view_financial_data', 'manage_counselors', 'access_logs',
                'fraud_detection', 'generate_reports'
            ],
            'session_timeout': 60,
            'require_2fa': True,
            'ip_whitelist': False
        },
        'manager': {
            'level': 70,
            'permissions': [
                'view_user_data', 'edit_user_data', 'manage_counselors',
                'view_reports', 'manage_appointments', 'view_analytics',
                'handle_support_tickets'
            ],
            'session_timeout': 120,
            'require_2fa': False,
            'ip_whitelist': False
        },
        'counselor': {
            'level': 50,
            'permissions': [
                'view_assigned_patients', 'edit_patient_notes', 'conduct_sessions',
                'view_patient_history', 'create_treatment_plans', 'access_resources',
                'submit_reports'
            ],
            'session_timeout': 240,
            'require_2fa': False,
            'ip_whitelist': False
        },
        'patient': {
            'level': 10,
            'permissions': [
                'view_own_data', 'book_appointments', 'access_sessions',
                'view_progress', 'update_profile', 'access_resources'
            ],
            'session_timeout': 480,
            'require_2fa': False,
            'ip_whitelist': False
        }
    }
    
    # Audit log for security events
    security_audit_log = []
    
    @classmethod
    def check_permission(cls, user_role, permission):
        """Check if a role has a specific permission"""
        if user_role not in cls.ROLES:
            return False
        return permission in cls.ROLES[user_role]['permissions']
    
    @classmethod
    def get_role_level(cls, user_role):
        """Get the security level of a role"""
        return cls.ROLES.get(user_role, {}).get('level', 0)
    
    @classmethod
    def requires_role(cls, minimum_role):
        """Decorator to require a minimum role for access"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_role = session.get('user_role', 'patient')
                if cls.get_role_level(user_role) < cls.get_role_level(minimum_role):
                    cls.log_security_event('access_denied', {
                        'user': session.get('user_email', 'anonymous'),
                        'required_role': minimum_role,
                        'user_role': user_role,
                        'endpoint': request.endpoint
                    })
                    abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @classmethod
    def requires_permission(cls, permission):
        """Decorator to require a specific permission"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user_role = session.get('user_role', 'patient')
                if not cls.check_permission(user_role, permission):
                    cls.log_security_event('permission_denied', {
                        'user': session.get('user_email', 'anonymous'),
                        'required_permission': permission,
                        'user_role': user_role,
                        'endpoint': request.endpoint
                    })
                    abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @classmethod
    def check_session_timeout(cls, user_role):
        """Check if session has timed out based on role"""
        last_activity = session.get('last_activity')
        if not last_activity:
            return True
            
        timeout_minutes = cls.ROLES.get(user_role, {}).get('session_timeout', 60)
        timeout_delta = timedelta(minutes=timeout_minutes)
        
        if datetime.utcnow() - datetime.fromisoformat(last_activity) > timeout_delta:
            cls.log_security_event('session_timeout', {
                'user': session.get('user_email', 'anonymous'),
                'role': user_role
            })
            return True
            
        return False
    
    @classmethod
    def verify_2fa_requirement(cls, user_role):
        """Check if 2FA is required for role"""
        return cls.ROLES.get(user_role, {}).get('require_2fa', False)
    
    @classmethod
    def verify_ip_whitelist(cls, user_role, ip_address):
        """Check if IP whitelisting is required and valid"""
        if not cls.ROLES.get(user_role, {}).get('ip_whitelist', False):
            return True
            
        # In production, this would check against actual whitelist
        allowed_ips = session.get('allowed_ips', [])
        return ip_address in allowed_ips
    
    @classmethod
    def generate_secure_token(cls, length=32):
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)
    
    @classmethod
    def hash_sensitive_data(cls, data):
        """Hash sensitive data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @classmethod
    def log_security_event(cls, event_type, details):
        """Log security events for audit trail"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details,
            'ip_address': request.remote_addr if request else 'system',
            'user_agent': request.headers.get('User-Agent', 'system') if request else 'system'
        }
        cls.security_audit_log.append(event)
        
        # In production, this would be stored in database
        # For now, keep last 1000 events in memory
        if len(cls.security_audit_log) > 1000:
            cls.security_audit_log = cls.security_audit_log[-1000:]
    
    @classmethod
    def get_security_audit_log(cls, filters=None):
        """Get security audit log with optional filters"""
        if not filters:
            return cls.security_audit_log
            
        filtered_log = []
        for event in cls.security_audit_log:
            match = True
            if 'event_type' in filters and event['event_type'] != filters['event_type']:
                match = False
            if 'user' in filters and event['details'].get('user') != filters['user']:
                match = False
            if 'date_from' in filters:
                event_date = datetime.fromisoformat(event['timestamp'])
                if event_date < filters['date_from']:
                    match = False
            if 'date_to' in filters:
                event_date = datetime.fromisoformat(event['timestamp'])
                if event_date > filters['date_to']:
                    match = False
                    
            if match:
                filtered_log.append(event)
                
        return filtered_log
    
    @classmethod
    def enforce_password_policy(cls, password, role):
        """Enforce password policy based on role"""
        min_length = {
            'super_admin': 16,
            'admin': 12,
            'manager': 10,
            'counselor': 8,
            'patient': 8
        }
        
        required_length = min_length.get(role, 8)
        
        if len(password) < required_length:
            return False, f"Password must be at least {required_length} characters"
            
        # Check complexity for admin roles
        if role in ['super_admin', 'admin']:
            if not any(c.isupper() for c in password):
                return False, "Password must contain uppercase letters"
            if not any(c.islower() for c in password):
                return False, "Password must contain lowercase letters"
            if not any(c.isdigit() for c in password):
                return False, "Password must contain numbers"
            if not any(c in '!@#$%^&*()_+-=' for c in password):
                return False, "Password must contain special characters"
                
        return True, "Password meets requirements"
    
    @classmethod
    def get_role_dashboard_url(cls, role):
        """Get the appropriate dashboard URL for each role"""
        dashboards = {
            'super_admin': '/admin/dashboard',
            'admin': '/admin/dashboard',
            'manager': '/manager/dashboard',
            'counselor': '/counselor/dashboard',
            'patient': '/dashboard'
        }
        return dashboards.get(role, '/dashboard')