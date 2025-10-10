"""
Admin Authentication & Security Module
=====================================
Handles admin login, MFA, session management, and security features
"""
import os
import logging
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    request, render_template, redirect, url_for, session,
    flash, jsonify, current_app, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from . import admin_bp
from models.database import db, Patient
from models.audit_log import audit_logger

# Configure logging for security events
security_logger = logging.getLogger('admin_security')
security_logger.setLevel(logging.INFO)

# Admin roles and permissions
ADMIN_ROLES = {
    'super_admin': {
        'name': 'Super Administrator',
        'permissions': ['*'],  # All permissions
        'level': 100
    },
    'finance_admin': {
        'name': 'Finance Administrator',
        'permissions': [
            'finance.view', 'finance.edit', 'users.view',
            'subscriptions.view', 'subscriptions.edit', 'subscriptions.create',
            'subscriptions.cancel', 'subscriptions.analytics', 'subscriptions.export',
            'payments.process'
        ],
        'level': 80
    },
    'ai_admin': {
        'name': 'AI Administrator',
        'permissions': [
            'ai.models.manage', 'ai.training.manage', 'ai.testing.manage',
            'users.view', 'analytics.view'
        ],
        'level': 70
    },
    'support_admin': {
        'name': 'Support Administrator',
        'permissions': [
            'users.view', 'users.edit', 'users.analytics', 'users.impersonate',
            'support.manage', 'analytics.view', 'content.manage'
        ],
        'level': 60
    },
    'content_admin': {
        'name': 'Content Administrator',
        'permissions': [
            'content.manage', 'marketing.manage', 'email.manage',
            'analytics.view'
        ],
        'level': 50
    }
}

def get_client_ip():
    """Get real client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def log_security_event(event_type, details=None, user_id=None):
    """Log security events for audit trail"""
    # Log to audit system
    try:
        audit_logger.log_security_event(
            event_type=event_type,
            description=f"Security event: {event_type}",
            details=details or {},
            admin_user_id=user_id or session.get('admin_user_id')
        )
    except Exception as e:
        # Fallback to file logging
        security_logger.error(f"Audit logging failed for {event_type}: {e}")

    # Also log to application logger
    event_data = {
        'timestamp': datetime.utcnow(),
        'event_type': event_type,
        'user_id': user_id or session.get('admin_user_id'),
        'ip_address': get_client_ip(),
        'user_agent': request.headers.get('User-Agent', ''),
        'details': details or {}
    }

    security_logger.info(f"SECURITY_EVENT: {event_type}", extra=event_data)

def check_ip_whitelist():
    """Check if admin IP is whitelisted"""
    whitelist = os.environ.get('ADMIN_IP_WHITELIST', '').split(',')
    if not whitelist or whitelist == ['']:
        return True  # No whitelist configured

    client_ip = get_client_ip()
    return client_ip in [ip.strip() for ip in whitelist]

def check_rate_limit(key, limit=5, window=300):
    """Simple rate limiting (in production, use Redis)"""
    # For now, we'll implement basic rate limiting in session
    # In production, this should use Redis with sliding window
    now = datetime.utcnow()
    rate_key = f"rate_limit_{key}"

    if rate_key not in session:
        session[rate_key] = {'count': 0, 'window_start': now.timestamp()}

    rate_data = session[rate_key]

    # Reset if window expired
    if now.timestamp() - rate_data['window_start'] > window:
        session[rate_key] = {'count': 1, 'window_start': now.timestamp()}
        return True

    # Check if limit exceeded
    if rate_data['count'] >= limit:
        return False

    # Increment counter
    session[rate_key]['count'] += 1
    return True

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check IP whitelist
        if not check_ip_whitelist():
            log_security_event('UNAUTHORIZED_IP_ACCESS', {
                'ip': get_client_ip(),
                'attempted_route': request.endpoint
            })
            flash('Access denied: IP not whitelisted', 'error')
            return redirect(url_for('admin.login'))

        # Check session
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin.login'))

        # Check session expiry
        if 'admin_session_expiry' in session:
            if datetime.utcnow() > datetime.fromisoformat(session['admin_session_expiry']):
                session.clear()
                flash('Session expired. Please login again.', 'warning')
                return redirect(url_for('admin.login'))

        # Check MFA if enabled
        if session.get('admin_mfa_required') and not session.get('admin_mfa_verified'):
            return redirect(url_for('admin.mfa_verify'))

        # Update last activity
        session['admin_last_activity'] = datetime.utcnow().isoformat()

        return f(*args, **kwargs)
    return decorated_function

def require_permission(permission):
    """Decorator to require specific admin permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First check admin auth
            if not session.get('admin_authenticated'):
                return redirect(url_for('admin.login'))

            # Get user permissions
            user_role = session.get('admin_role', 'support_admin')
            user_permissions = ADMIN_ROLES.get(user_role, {}).get('permissions', [])

            # Check permission (super admin has all permissions)
            if '*' not in user_permissions and permission not in user_permissions:
                log_security_event('PERMISSION_DENIED', {
                    'required_permission': permission,
                    'user_role': user_role,
                    'attempted_route': request.endpoint
                })
                flash(f'Access denied: Missing permission "{permission}"', 'error')
                return redirect(url_for('admin.dashboard'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login with MFA support"""
    if request.method == 'POST':
        # Rate limiting
        client_ip = get_client_ip()
        if not check_rate_limit(f"login_{client_ip}", limit=5, window=900):  # 5 attempts per 15 minutes
            log_security_event('LOGIN_RATE_LIMIT_EXCEEDED', {'ip': client_ip})
            flash('Too many login attempts. Please try again later.', 'error')
            return render_template('admin/login_complete.html')

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Basic validation
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('admin/login_complete.html')

        # Find admin user (using AdminUser model)
        from models.database import AdminUser
        admin_user = AdminUser.query.filter_by(
            email=username,
            is_active=True
        ).first()

        if admin_user and check_password_hash(admin_user.password_hash, password):
            # Successful login
            session['admin_authenticated'] = True
            session['admin_user_id'] = admin_user.id
            session['admin_username'] = admin_user.email
            session['admin_role'] = admin_user.role  # Use the role from AdminUser model
            session['admin_session_expiry'] = (datetime.utcnow() + timedelta(hours=8)).isoformat()

            # Check if MFA is enabled
            mfa_secret = admin_user.oauth_providers  # Reuse this field for MFA secret
            if mfa_secret:
                session['admin_mfa_required'] = True
                session['admin_mfa_verified'] = False
                audit_logger.log_admin_action(
                    'LOGIN_SUCCESS_MFA_REQUIRED',
                    f'Admin {admin_user.email} logged in successfully, MFA required',
                    target_type='USER',
                    target_id=admin_user.id,
                    severity='INFO'
                )
                return redirect(url_for('admin.mfa_verify'))
            else:
                session['admin_mfa_required'] = False
                session['admin_mfa_verified'] = True

            audit_logger.log_admin_action(
                'LOGIN_SUCCESS',
                f'Admin {admin_user.email} logged in successfully',
                target_type='USER',
                target_id=admin_user.id,
                severity='INFO'
            )
            flash(f'Welcome, {admin_user.name}!', 'success')

            # Redirect to originally requested page or dashboard
            next_page = request.form.get('next') or url_for('admin.dashboard')
            return redirect(next_page)
        else:
            # Failed login
            log_security_event('LOGIN_FAILED', {
                'attempted_username': username,
                'ip': client_ip
            })
            flash('Invalid username or password', 'error')

    return render_template('admin/login_complete.html')

@admin_bp.route('/mfa/setup')
@require_admin_auth
def mfa_setup():
    """Set up Multi-Factor Authentication"""
    user_id = session.get('admin_user_id')
    admin_user = Patient.query.get(user_id)

    if not admin_user:
        flash('User not found', 'error')
        return redirect(url_for('admin.dashboard'))

    # Generate MFA secret
    secret = pyotp.random_base32()

    # Generate QR code
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=admin_user.email,
        issuer_name="MindMend Admin"
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for display
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_b64 = base64.b64encode(img_buffer.getvalue()).decode()

    return render_template('admin/mfa_setup.html', {
        'secret': secret,
        'qr_code': img_b64,
        'user_email': admin_user.email
    })

@admin_bp.route('/mfa/verify', methods=['GET', 'POST'])
def mfa_verify():
    """Verify MFA token"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin.login'))

    if request.method == 'POST':
        token = request.form.get('token', '').strip()

        if not token:
            flash('MFA token is required', 'error')
            return render_template('admin/mfa_verify.html')

        user_id = session.get('admin_user_id')
        admin_user = Patient.query.get(user_id)

        if admin_user and admin_user.oauth_providers:  # MFA secret stored here
            totp = pyotp.TOTP(admin_user.oauth_providers)

            if totp.verify(token, valid_window=1):  # Allow 1 step tolerance
                session['admin_mfa_verified'] = True
                log_security_event('MFA_SUCCESS', {'user_id': user_id})
                flash('MFA verification successful', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                log_security_event('MFA_FAILED', {'user_id': user_id})
                flash('Invalid MFA token', 'error')

    return render_template('admin/mfa_verify.html')

@admin_bp.route('/mfa/enable', methods=['POST'])
@require_admin_auth
def mfa_enable():
    """Enable MFA with verified token"""
    user_id = session.get('admin_user_id')
    admin_user = Patient.query.get(user_id)

    secret = request.form.get('secret')
    token = request.form.get('token')

    if not secret or not token:
        flash('Secret and token are required', 'error')
        return redirect(url_for('admin.mfa_setup'))

    # Verify token
    totp = pyotp.TOTP(secret)
    if totp.verify(token, valid_window=1):
        # Save secret to user account
        admin_user.oauth_providers = secret
        db.session.commit()

        log_security_event('MFA_ENABLED', {'user_id': user_id})
        flash('MFA has been enabled successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    else:
        flash('Invalid token. Please try again.', 'error')
        return redirect(url_for('admin.mfa_setup'))

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    user_id = session.get('admin_user_id')
    log_security_event('LOGOUT', {'user_id': user_id})

    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/session/extend', methods=['POST'])
@require_admin_auth
def extend_session():
    """Extend admin session"""
    session['admin_session_expiry'] = (datetime.utcnow() + timedelta(hours=8)).isoformat()
    return jsonify({'success': True, 'message': 'Session extended'})

@admin_bp.route('/security/events')
@require_admin_auth
@require_permission('security.view')
def security_events():
    """View security events and audit log"""
    # This will be implemented when we create the audit log table
    return render_template('admin/security_events.html', events=[])