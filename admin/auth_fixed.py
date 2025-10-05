"""
Simple Admin Authentication
"""
from flask import request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from . import admin_bp
from models.database import db, Patient

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Simple admin login"""
    if request.method == 'POST':
        # Get credentials from form (handle both email/username fields)
        username = request.form.get('username') or request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Basic validation
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('admin/login_complete.html')

        # Find admin user
        admin_user = Patient.query.filter_by(
            email=username,
            subscription_tier='enterprise'
        ).first()

        if admin_user and check_password_hash(admin_user.password_hash, password):
            # Successful login
            session['admin_authenticated'] = True
            session['admin_logged_in'] = True
            session['admin_user_id'] = admin_user.id
            session['admin_username'] = admin_user.email
            session['admin_email'] = admin_user.email
            session['admin_role'] = 'super_admin'
            session['admin_mfa_verified'] = True

            flash('Login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials. Please check your username and password.', 'error')

    return render_template('admin/login_complete.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.login'))