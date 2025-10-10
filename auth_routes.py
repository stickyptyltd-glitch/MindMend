from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models.database import db, Patient, AdminUser
from admin_security import admin_security, AdminAuditLogger
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from email_utils import send_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
        else:
            existing_user = Patient.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered', 'error')
            else:
                new_user = Patient(
                    name=name,
                    email=email,
                    password_hash=generate_password_hash(password),
                    subscription_tier='free'
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! You can now login.', 'success')
                return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password required', 'error')
        else:
            user = Patient.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('general.user_dashboard'))
            else:
                flash('Invalid email or password', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Secure admin login with 2FA support"""
    if request.method == 'GET':
        return render_template('admin/login.html')

    client_ip = request.headers.get('X-Real-IP', request.remote_addr)

    # Rate limiting check
    if not admin_security.check_rate_limit(client_ip, max_attempts=3, window=900):
        AdminAuditLogger.log_login('unknown', False, client_ip)
        flash('Too many failed attempts. Try again later.', 'error')
        return render_template('admin/login.html'), 429

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        admin_security.record_failed_attempt(client_ip)
        AdminAuditLogger.log_login(username, False, client_ip)
        flash('Username and password are required', 'error')
        return render_template('admin/login.html')

    # Verify admin credentials
    from flask import current_app
    current_app.logger.info(f"Attempting admin login for user: {username}")
    current_app.logger.info(f"Password provided: {password}")
    admin_user = AdminUser.query.filter_by(email=username).first()
    current_app.logger.info(f"Admin user found: {admin_user}")
    if admin_user:
        current_app.logger.info(f"Password hash from DB: {admin_user.password_hash}")

    if not admin_user or not check_password_hash(admin_user.password_hash, password):
        if admin_user:
            current_app.logger.info(f"Password hash check result: {check_password_hash(admin_user.password_hash, password)}")
        admin_security.record_failed_attempt(client_ip)
        AdminAuditLogger.log_login(username, False, client_ip)
        flash('Invalid credentials', 'error')
        return render_template('admin/login.html')

    # Generate admin token
    admin_token = admin_security.generate_admin_token(username)
    session['admin_token'] = admin_token
    session['admin_id'] = username

    # Check if 2FA is enabled
    if username in admin_security.two_factor_secrets:
        session['admin_2fa_pending'] = True
        AdminAuditLogger.log_login(username, True, client_ip)
        return redirect(url_for('auth.admin_2fa_verify'))

    # Complete login
    session['admin_authenticated'] = True
    AdminAuditLogger.log_login(username, True, client_ip)
    flash('Successfully logged in', 'success')

    next_page = request.args.get('next')
    return redirect(next_page or url_for('admin.dashboard'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('general.home'))

@auth_bp.route('/admin/logout')
def admin_logout():
    """Secure admin logout"""
    admin_id = session.get('admin_id')
    if admin_id:
        AdminAuditLogger.log_login(admin_id, True, request.headers.get('X-Real-IP', request.remote_addr))

    # Clear all admin session data
    session.pop('admin_token', None)
    session.pop('admin_id', None)
    session.pop('admin_authenticated', None)
    session.pop('admin_2fa_verified', None)
    session.pop('admin_2fa_pending', None)

    flash('Successfully logged out', 'info')
    return redirect(url_for('auth.admin_login'))

@auth_bp.route('/admin/2fa/setup', methods=['GET', 'POST'])
def admin_2fa_setup():
    """Setup 2FA for admin account"""
    if 'admin_token' not in session:
        return redirect(url_for('auth.admin_login'))

    admin_id = session.get('admin_id')

    if request.method == 'GET':
        # Generate 2FA setup
        setup_data = admin_security.setup_2fa(admin_id)
        return render_template('admin/2fa_setup.html',
                             qr_code=setup_data['qr_code'],
                             manual_key=setup_data['manual_entry_key'])

    # Verify setup
    token = request.form.get('token', '').strip()
    if not token:
        flash('Please enter the 6-digit code from your authenticator app', 'error')
        return render_template('admin/2fa_setup.html')

    if admin_security.verify_2fa(admin_id, token):
        session['admin_2fa_verified'] = True
        session['admin_authenticated'] = True
        AdminAuditLogger.log_system_change('2fa_enabled', {'admin_id': admin_id})
        flash('Two-factor authentication enabled successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    else:
        flash('Invalid code. Please try again.', 'error')
        setup_data = admin_security.setup_2fa(admin_id)
        return render_template('admin/2fa_setup.html',
                             qr_code=setup_data['qr_code'],
                             manual_key=setup_data['manual_entry_key'])

@auth_bp.route('/admin/2fa/verify', methods=['GET', 'POST'])
def admin_2fa_verify():
    """Verify 2FA token"""
    if 'admin_token' not in session or not session.get('admin_2fa_pending'):
        return redirect(url_for('auth.admin_login'))

    admin_id = session.get('admin_id')

    if request.method == 'GET':
        return render_template('admin/2fa_verify.html')

    token = request.form.get('token', '').strip()
    if not token:
        flash('Please enter the 6-digit code', 'error')
        return render_template('admin/2fa_verify.html')

    if admin_security.verify_2fa(admin_id, token):
        session['admin_2fa_verified'] = True
        session['admin_authenticated'] = True
        session.pop('admin_2fa_pending', None)
        AdminAuditLogger.log_login(admin_id, True, request.headers.get('X-Real-IP', request.remote_addr))
        flash('Successfully authenticated', 'success')

        next_page = request.args.get('next')
        return redirect(next_page or url_for('admin.dashboard'))
    else:
        client_ip = request.headers.get('X-Real-IP', request.remote_addr)
        admin_security.record_failed_attempt(client_ip)
        flash('Invalid code. Please try again.', 'error')
        return render_template('admin/2fa_verify.html')

def _token_serializer():
    from flask import current_app
    secret = current_app.config.get('SECRET_KEY') or current_app.secret_key
    return URLSafeTimedSerializer(secret_key=secret, salt='admin-reset')

@auth_bp.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        user = AdminUser.query.filter_by(email=email, is_active=True).first()
        if user:
            s = _token_serializer()
            token = s.dumps({"email": email})
            reset_link = url_for('auth.reset_with_token', token=token, _external=True)
            try:
                send_email(email, "MindMend Admin Password Reset", f"<p>Reset your password: <a href='{reset_link}'>Reset</a></p>")
                flash('Password reset link sent', 'success')
            except Exception as e:
                flash(f'Email error: {e}', 'error')
        else:
            flash('If the email exists, a reset link has been sent', 'info')
    return render_template('admin/forgot.html')


@auth_bp.route('/admin/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    s = _token_serializer()
    try:
        data = s.loads(token, max_age=3600)
        email = data.get('email')
    except (BadSignature, SignatureExpired):
        return ("Invalid or expired token", 400)

    if request.method == 'POST':
        new = request.form.get('new') or ''
        if not new:
            return ("New password required", 400)
        user = AdminUser.query.filter_by(email=email, is_active=True).first()
        if not user:
            return ("User not found", 404)
        user.set_password(new)
        db.session.add(AdminAudit(admin_email=email, action='reset_password_via_token', ip_address=_client_ip()))
        db.session.commit()
        flash('Password updated. Please login.', 'success')
        return redirect(url_for('auth.admin_login'))

    return render_template('admin/reset.html')