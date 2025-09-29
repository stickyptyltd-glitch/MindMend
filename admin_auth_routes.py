"""
Admin Authentication Routes
==========================
Secure authentication routes for MindMend admin panel
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import os
import time
from admin_security import admin_security, AdminAuditLogger

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

@admin_auth_bp.route('/login', methods=['GET', 'POST'])
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
    admin_credentials = {
        os.environ.get('SUPER_ADMIN_ID', 'super_admin'): os.environ.get('SUPER_ADMIN_PASSWORD_HASH'),
        # Add more admin users here
    }
    
    if username not in admin_credentials:
        admin_security.record_failed_attempt(client_ip)
        AdminAuditLogger.log_login(username, False, client_ip)
        flash('Invalid credentials', 'error')
        return render_template('admin/login.html')
    
    stored_password_hash = admin_credentials[username]
    if not stored_password_hash or not check_password_hash(stored_password_hash, password):
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
        return redirect(url_for('admin_auth.admin_2fa_verify'))
    
    # Complete login
    session['admin_authenticated'] = True
    AdminAuditLogger.log_login(username, True, client_ip)
    flash('Successfully logged in', 'success')
    
    next_page = request.args.get('next')
    return redirect(next_page or url_for('admin.dashboard'))

@admin_auth_bp.route('/2fa/setup', methods=['GET', 'POST'])
def admin_2fa_setup():
    """Setup 2FA for admin account"""
    if 'admin_token' not in session:
        return redirect(url_for('admin_auth.admin_login'))
    
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

@admin_auth_bp.route('/2fa/verify', methods=['GET', 'POST'])
def admin_2fa_verify():
    """Verify 2FA token"""
    if 'admin_token' not in session or not session.get('admin_2fa_pending'):
        return redirect(url_for('admin_auth.admin_login'))
    
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

@admin_auth_bp.route('/logout')
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
    return redirect(url_for('admin_auth.admin_login'))

@admin_auth_bp.route('/auth-required')
def admin_auth_required():
    """Show authentication required page"""
    return render_template('admin/auth_required.html')

@admin_auth_bp.route('/forbidden')
def admin_forbidden():
    """Show access forbidden page"""
    return render_template('admin/forbidden.html'), 403