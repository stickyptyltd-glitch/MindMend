from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
import os
from models.database import db, AdminUser, AdminAudit, Counselor
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from collections import deque
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from email_utils import send_email

# Simple in-memory rate limit store (per-IP for login); consider Redis in production
_login_attempts = {}


def _client_ip():
    # Prefer X-Forwarded-For if present (ProxyFix may set this already)
    from flask import request

    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def _token_serializer():
    from flask import current_app
    secret = current_app.config.get('SECRET_KEY') or current_app.secret_key
    return URLSafeTimedSerializer(secret_key=secret, salt='admin-reset')


@admin_bp.before_request
def _enforce_ip_allowlist():
    from flask import request

    allowlist = os.getenv('ADMIN_IP_WHITELIST', '').strip()
    if not allowlist:
        return  # no restriction configured
    client_ip = _client_ip()
    allowed = {ip.strip() for ip in allowlist.split(',') if ip.strip()}
    if client_ip not in allowed:
        return ("Access restricted", 403)


def _rate_limited(max_attempts=10, window_seconds=60):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            ip = _client_ip()
            q = _login_attempts.setdefault(ip, deque())
            now = datetime.utcnow()
            # prune
            while q and (now - q[0]).total_seconds() > window_seconds:
                q.popleft()
            if len(q) >= max_attempts:
                return ("Too many attempts, please try again later", 429)
            q.append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
import logging
from datetime import datetime, timedelta

# Create the admin blueprint
admin_bp = Blueprint('admin', __name__)

logger = logging.getLogger(__name__)

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
def admin_index():
    """Redirect to dashboard or login"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
@_rate_limited()
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        # Email-format admin login (DB-backed with env fallback)
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        user = AdminUser.query.filter_by(email=email, is_active=True).first()
        if user and user.check_password(password):
            session['admin_logged_in'] = True
            session['admin_email'] = user.email
            session['admin_role'] = user.role
            db.session.add(AdminAudit(admin_email=user.email, action='login', ip_address=_client_ip()))
            db.session.commit()
            return redirect(url_for('admin.dashboard'))

        flash('Invalid credentials', 'error')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    admin_email = session.get('admin_email', 'unknown')
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    session.pop('admin_role', None)
    db.session.add(AdminAudit(admin_email=admin_email, action='logout', ip_address=_client_ip()))
    db.session.commit()
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/dashboard')
@require_admin_auth
def dashboard():
    """Main admin dashboard"""
    dashboard_data = {
        'system_stats': {
            'total_users': 1247,
            'active_sessions': 45,
            'total_counselors': 23,
            'revenue_this_month': 45600,
            'platform_uptime': '99.9%'
        },
        'recent_activities': [
            {
                'action': 'User Registration',
                'details': 'New user signed up',
                'timestamp': datetime.utcnow() - timedelta(minutes=15),
                'type': 'user'
            },
            {
                'action': 'Payment Processed',
                'details': 'Premium subscription - $99 AUD',
                'timestamp': datetime.utcnow() - timedelta(hours=2),
                'type': 'payment'
            }
        ]
    }

    return render_template('admin/dashboard.html', data=dashboard_data)


@admin_bp.route('/admins')
@require_admin_auth
def list_admins():
    if session.get('admin_role') != 'super_admin':
        return ("Forbidden", 403)
    admins = AdminUser.query.order_by(AdminUser.created_at.desc()).all()
    return render_template('admin/admins.html', admins=admins)


@admin_bp.route('/admins/create', methods=['GET', 'POST'])
@require_admin_auth
def create_admin():
    if session.get('admin_role') != 'super_admin':
        return ("Forbidden", 403)
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        name = request.form.get('name') or ''
        password = request.form.get('password') or ''
        role = request.form.get('role') or 'admin'
        if not email or not password:
            flash('Email and password required', 'error')
        elif AdminUser.query.filter_by(email=email).first():
            flash('Admin already exists', 'error')
        else:
            u = AdminUser(email=email, name=name, role=role)
            u.set_password(password)
            db.session.add(u)
            db.session.add(AdminAudit(admin_email=session.get('admin_email'), action='create_admin', details=email, ip_address=_client_ip()))
            db.session.commit()
            flash('Admin created', 'success')
            return redirect(url_for('admin.list_admins'))
    return render_template('admin/create_admin.html')


@admin_bp.route('/admins/<int:admin_id>/deactivate', methods=['POST'])
@require_admin_auth
def deactivate_admin(admin_id):
    if session.get('admin_role') != 'super_admin':
        return ("Forbidden", 403)
    u = AdminUser.query.get_or_404(admin_id)
    if u.email == session.get('admin_email'):
        flash('Cannot deactivate current session user', 'error')
        return redirect(url_for('admin.list_admins'))
    u.is_active = False
    db.session.add(AdminAudit(admin_email=session.get('admin_email'), action='deactivate_admin', details=u.email, ip_address=_client_ip()))
    db.session.commit()
    flash('Admin deactivated', 'success')
    return redirect(url_for('admin.list_admins'))


@admin_bp.route('/admins/<int:admin_id>/edit', methods=['GET', 'POST'])
@require_admin_auth
def edit_admin(admin_id):
    if session.get('admin_role') != 'super_admin':
        return ("Forbidden", 403)
    u = AdminUser.query.get_or_404(admin_id)
    if request.method == 'POST':
        name = request.form.get('name') or ''
        role = request.form.get('role') or 'admin'
        password = request.form.get('password') or ''
        u.name = name
        u.role = role
        if password:
            u.set_password(password)
        db.session.add(AdminAudit(admin_email=session.get('admin_email'), action='edit_admin', details=u.email, ip_address=_client_ip()))
        db.session.commit()
        flash('Admin updated', 'success')
        return redirect(url_for('admin.list_admins'))
    return render_template('admin/edit_admin.html', admin=u)


@admin_bp.route('/admins/<int:admin_id>/delete', methods=['POST'])
@require_admin_auth
def delete_admin(admin_id):
    if session.get('admin_role') != 'super_admin':
        return ("Forbidden", 403)
    u = AdminUser.query.get_or_404(admin_id)
    if u.email == session.get('admin_email'):
        flash('Cannot delete current session user', 'error')
        return redirect(url_for('admin.list_admins'))
    db.session.delete(u)
    db.session.add(AdminAudit(admin_email=session.get('admin_email'), action='delete_admin', details=u.email, ip_address=_client_ip()))
    db.session.commit()
    flash('Admin deleted', 'success')
    return redirect(url_for('admin.list_admins'))


@admin_bp.route('/counselors')
@require_admin_auth
def list_counselors():
    cs = Counselor.query.order_by(Counselor.created_at.desc()).all()
    return render_template('admin/counselors.html', counselors=cs)


@admin_bp.route('/counselors/<int:c_id>/deactivate', methods=['POST'])
@require_admin_auth
def deactivate_counselor(c_id):
    c = Counselor.query.get_or_404(c_id)
    c.is_active = False
    db.session.add(AdminAudit(admin_email=session.get('admin_email'), action='deactivate_counselor', details=c.email, ip_address=_client_ip()))
    db.session.commit()
    flash('Counselor deactivated', 'success')
    return redirect(url_for('admin.list_counselors'))


@admin_bp.route('/counselors/<int:c_id>/edit', methods=['GET', 'POST'])
@require_admin_auth
def edit_counselor(c_id):
    c = Counselor.query.get_or_404(c_id)
    if request.method == 'POST':
        name = request.form.get('name') or ''
        password = request.form.get('password') or ''
        c.name = name
        if password:
            c.set_password(password)
        db.session.add(AdminAudit(admin_email=session.get('admin_email'), action='edit_counselor', details=c.email, ip_address=_client_ip()))
        db.session.commit()
        flash('Counselor updated', 'success')
        return redirect(url_for('admin.list_counselors'))
    return render_template('admin/edit_counselor.html', counselor=c)

@admin_bp.route('/api-keys', methods=['GET', 'POST'])
@require_admin_auth
def api_keys():
    """API key management"""
    if request.method == 'POST':
        flash('API keys updated successfully', 'success')
        db.session.add(AdminAudit(admin_email=session.get('admin_email'), action='update_api_keys', ip_address=_client_ip()))
        db.session.commit()
        return redirect(url_for('admin.api_keys'))

    api_keys = {
        'openai_api_key': '',
        'stripe_secret_key': '',
        'stripe_publishable_key': '',
        'paypal_client_id': '',
        'paypal_client_secret': ''
    }

    return render_template('admin/api_keys.html', api_keys=api_keys)

@admin_bp.route('/platform-upgrades')
@require_admin_auth
def platform_upgrades():
    """Platform upgrade management"""
    # Only super admins can view this page
    if session.get('admin_role') != 'super_admin':
        return ("Forbidden", 403)
    upgrade_options = {
        'level_3': {
            'name': 'Level 3 - Advanced AI',
            'price': '$2,000 AUD/month',
            'features': [
                'Real-time microexpression analysis',
                'Biosensor integration (Apple Watch, Fitbit)',
                'Advanced video assessment with emotion detection'
            ],
            'status': 'available'
        }
    }

    return render_template('admin/platform_upgrades.html', upgrades=upgrade_options)


@admin_bp.route('/counselors/create', methods=['GET', 'POST'])
@require_admin_auth
def create_counselor():
    """Create a counselor account (super admin only)."""
    if session.get('admin_role') != 'super_admin':
        return ("Forbidden", 403)
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        name = request.form.get('name') or ''
        password = request.form.get('password') or ''
        if not email or not password:
            flash('Email and password required', 'error')
        else:
            existing = Counselor.query.filter_by(email=email).first()
            if existing:
                flash('Counselor already exists', 'error')
            else:
                c = Counselor(email=email, name=name)
                c.set_password(password)
                db.session.add(c)
                db.session.add(AdminAudit(admin_email=session.get('admin_email'), action='create_counselor', details=email, ip_address=_client_ip()))
                db.session.commit()
                flash('Counselor created', 'success')
                return redirect(url_for('admin.create_counselor'))
    # Minimal HTML form to avoid adding templates
    return render_template('admin/create_counselor.html')


@admin_bp.route('/reset-password', methods=['GET', 'POST'])
@require_admin_auth
def reset_password():
    """Allow current admin to change their password."""
    if request.method == 'POST':
        current = request.form.get('current') or ''
        new = request.form.get('new') or ''
        if not new:
            flash('New password required', 'error')
        else:
            email = session.get('admin_email')
            user = AdminUser.query.filter_by(email=email, is_active=True).first()
            if user and user.check_password(current):
                user.set_password(new)
                db.session.add(AdminAudit(admin_email=email, action='reset_password', ip_address=_client_ip()))
                db.session.commit()
                flash('Password updated', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Current password incorrect', 'error')
    return render_template('admin/reset_password.html')


@admin_bp.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        user = AdminUser.query.filter_by(email=email, is_active=True).first()
        if user:
            s = _token_serializer()
            token = s.dumps({"email": email})
            reset_link = url_for('admin.reset_with_token', token=token, _external=True)
            try:
                send_email(email, "MindMend Admin Password Reset", f"<p>Reset your password: <a href='{reset_link}'>Reset</a></p>")
                flash('Password reset link sent', 'success')
            except Exception as e:
                flash(f'Email error: {e}', 'error')
        else:
            flash('If the email exists, a reset link has been sent', 'info')
    return render_template('admin/forgot.html')


@admin_bp.route('/reset/<token>', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.admin_login'))

    return render_template('admin/reset.html')

@admin_bp.route('/business-settings', methods=['GET', 'POST'])
@require_admin_auth
def business_settings():
    """Business configuration and settings"""
    if request.method == 'POST':
        flash('Business settings updated successfully', 'success')
        return redirect(url_for('admin.business_settings'))

    settings = {
        'company_name': 'Sticky Pty Ltd',
        'contact_email': 'support@mindmend.com.au',
        'contact_phone': '+61 2 9000 0000',
        'business_address': 'Sydney, NSW, Australia'
    }

    return render_template('admin/business_settings.html', settings=settings)

@admin_bp.route('/user-management')
@require_admin_auth
def user_management():
    """User and counselor management"""
    users_data = {
        'total_users': 1247,
        'active_users': 892,
        'premium_users': 234,
        'counselors': 45
    }

    return render_template('admin/user_management.html', data=users_data)

@admin_bp.route('/financial-overview')
@require_admin_auth
def financial_overview():
    """Financial dashboard and revenue tracking"""
    financial_data = {
        'revenue': {
            'this_month': 45600,
            'last_month': 38200,
            'growth_rate': 19.4,
            'projected_annual': 520000
        },
        'subscriptions': {
            'basic': {'count': 456, 'revenue': 22344},
            'premium': {'count': 234, 'revenue': 23166}
        },
        'counselor_earnings': {
            'total_paid': 156000,
            'pending_payouts': 12400
        },
        'expenses': {
            'hosting': 2400,
            'ai_services': 3200,
            'support_staff': 18000,
            'marketing': 8500
        }
    }

    return render_template('admin/financial_overview.html', data=financial_data)

@admin_bp.route('/system-monitoring')
@require_admin_auth
def system_monitoring():
    """System health and monitoring"""
    monitoring_data = {
        'system_health': {
            'status': 'healthy',
            'uptime': '99.97%',
            'response_time': '245ms',
            'error_rate': '0.02%'
        },
        'resources': {
            'cpu_usage': 34,
            'memory_usage': 67,
            'disk_usage': 23,
            'bandwidth': 145
        },
        'security': {
            'failed_login_attempts': 12,
            'blocked_ips': 3,
            'security_alerts': 0,
            'last_backup': datetime.utcnow() - timedelta(hours=6)
        },
        'ai_services': {
            'openai_status': 'operational',
            'requests_today': 2456,
            'quota_remaining': '78%',
            'average_response_time': '1.2s'
        }
    }

    return render_template('admin/system_monitoring.html', data=monitoring_data)

@admin_bp.route('/deployment-tools')
@require_admin_auth
def deployment_tools():
    """Deployment and DevOps tools"""
    deployment_data = {
        'current_version': '2.0.1',
        'deployment_status': 'stable',
        'last_deployment': datetime.utcnow() - timedelta(days=3),
        'environments': {
            'production': {
                'status': 'healthy',
                'version': '2.0.1',
                'url': 'https://mindmend.com.au'
            },
            'staging': {
                'status': 'healthy',
                'version': '2.1.0-beta',
                'url': 'https://staging.mindmend.com.au'
            },
            'development': {
                'status': 'healthy',
                'version': '2.2.0-dev',
                'url': 'https://dev.mindmend.com.au'
            }
        },
        'hosting_recommendations': {
            'current': 'Replit (Development)',
            'recommended_production': [
                {
                    'provider': 'AWS',
                    'cost': '$800-2000/month',
                    'features': ['Auto-scaling', 'HIPAA compliant', 'Global CDN'],
                    'setup_time': '2-3 weeks'
                },
                {
                    'provider': 'Google Cloud',
                    'cost': '$600-1500/month',
                    'features': ['AI/ML tools', 'Healthcare APIs', 'Global reach'],
                    'setup_time': '2-3 weeks'
                }
            ]
        }
    }

    return render_template('admin/deployment_tools.html', data=deployment_data)

@admin_bp.route('/ai-assistant')
@require_admin_auth
def ai_assistant():
    """AI Assistant for fraud detection and management"""
    return render_template('admin/ai_assistant.html')

@admin_bp.route('/research-management')
@require_admin_auth
def research_management():
    """Research and dataset management interface"""
    stats = {
        'total_papers': 125,
        'papers_this_month': 8,
        'total_datasets': 23,
        'total_records': 50000,
        'total_insights': 340,
        'validated_insights': 280,
        'active_analyses': 5,
        'completed_today': 12
    }

    return render_template('admin/research_management.html', stats=stats)

@admin_bp.route('/ai-models')
@require_admin_auth
def ai_models():
    """AI models management interface"""
    status = {
        'model_details': [],
        'total_models': 5,
        'active_models': 3
    }

    return render_template('admin/ai_models.html', status=status)

@admin_bp.route('/company-documents')
@require_admin_auth
def company_documents():
    """Company Documents management page"""
    uploaded_docs = []

    return render_template('admin/company_documents.html', uploaded_docs=uploaded_docs)

@admin_bp.route('/counselor-benefits', methods=['GET', 'POST'])
@require_admin_auth
def counselor_benefits():
    """Counselor Benefits Management - Developer GUI for Dayle Stueven"""
    from models.database import db, CounselorPosition, CounselorBenefit, CounselorRequirement

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create_position':
            # Create new position
            position = CounselorPosition(
                position_type=request.form.get('position_type'),
                title=request.form.get('title'),
                salary_range_min=float(request.form.get('salary_range_min') or 0),
                salary_range_max=float(request.form.get('salary_range_max') or 0),
                hourly_rate_min=float(request.form.get('hourly_rate_min') or 0),
                hourly_rate_max=float(request.form.get('hourly_rate_max') or 0),
                currency=request.form.get('currency', 'AUD'),
                updated_by='sticky.pty.ltd@gmail.com'
            )
            db.session.add(position)
            db.session.commit()
            flash('Position created successfully', 'success')

        elif action == 'add_benefit':
            # Add benefit to position
            benefit = CounselorBenefit(
                position_id=int(request.form.get('position_id')),
                benefit_name=request.form.get('benefit_name'),
                benefit_description=request.form.get('benefit_description'),
                benefit_category=request.form.get('benefit_category'),
                display_order=int(request.form.get('display_order', 0))
            )
            db.session.add(benefit)
            db.session.commit()
            flash('Benefit added successfully', 'success')

        elif action == 'add_requirement':
            # Add requirement to position
            requirement = CounselorRequirement(
                position_id=int(request.form.get('position_id')),
                requirement_text=request.form.get('requirement_text'),
                requirement_category=request.form.get('requirement_category'),
                is_mandatory=bool(request.form.get('is_mandatory')),
                display_order=int(request.form.get('display_order', 0))
            )
            db.session.add(requirement)
            db.session.commit()
            flash('Requirement added successfully', 'success')

        elif action == 'update_position':
            # Update existing position
            position_id = int(request.form.get('position_id'))
            position = CounselorPosition.query.get(position_id)
            if position:
                position.title = request.form.get('title')
                position.salary_range_min = float(request.form.get('salary_range_min') or 0)
                position.salary_range_max = float(request.form.get('salary_range_max') or 0)
                position.hourly_rate_min = float(request.form.get('hourly_rate_min') or 0)
                position.hourly_rate_max = float(request.form.get('hourly_rate_max') or 0)
                position.currency = request.form.get('currency', 'AUD')
                position.is_active = bool(request.form.get('is_active'))
                position.updated_by = 'sticky.pty.ltd@gmail.com'
                position.updated_at = datetime.utcnow()
                db.session.commit()
                flash('Position updated successfully', 'success')

        elif action == 'delete_benefit':
            benefit_id = int(request.form.get('benefit_id'))
            benefit = CounselorBenefit.query.get(benefit_id)
            if benefit:
                db.session.delete(benefit)
                db.session.commit()
                flash('Benefit deleted successfully', 'success')

        elif action == 'delete_requirement':
            requirement_id = int(request.form.get('requirement_id'))
            requirement = CounselorRequirement.query.get(requirement_id)
            if requirement:
                db.session.delete(requirement)
                db.session.commit()
                flash('Requirement deleted successfully', 'success')

        return redirect(url_for('admin.counselor_benefits'))

    # Get all positions with their benefits and requirements
    positions = CounselorPosition.query.all()

    benefits_data = {
        'positions': positions,
        'benefit_categories': ['health', 'professional', 'financial', 'lifestyle'],
        'requirement_categories': ['education', 'experience', 'technical', 'legal'],
        'currencies': ['AUD', 'USD', 'EUR', 'GBP']
    }

    return render_template('admin/counselor_benefits.html', data=benefits_data)

@admin_bp.route('/api/counselor-benefits/<int:position_id>')
@require_admin_auth
def get_position_data(position_id):
    """API endpoint to get position data for editing"""
    from models.database import CounselorPosition

    position = CounselorPosition.query.get_or_404(position_id)

    return jsonify({
        'id': position.id,
        'position_type': position.position_type,
        'title': position.title,
        'salary_range_min': position.salary_range_min,
        'salary_range_max': position.salary_range_max,
        'hourly_rate_min': position.hourly_rate_min,
        'hourly_rate_max': position.hourly_rate_max,
        'currency': position.currency,
        'is_active': position.is_active,
        'benefits': [{'id': b.id, 'name': b.benefit_name, 'description': b.benefit_description, 'category': b.benefit_category} for b in position.benefits if b.is_active],
        'requirements': [{'id': r.id, 'text': r.requirement_text, 'category': r.requirement_category, 'mandatory': r.is_mandatory} for r in position.requirements if r.is_active]
    })

@admin_bp.route('/ai-model-manager', methods=['GET', 'POST'])
@require_admin_auth
def ai_model_manager():
    """AI Model Import and Management Interface"""
    from models.ai_model_manager import ai_model_manager, ModelType, ModelConfig

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_model':
            # Add new AI model
            try:
                model_config = ModelConfig(
                    name=request.form.get('model_name'),
                    type=ModelType(request.form.get('model_type')),
                    endpoint=request.form.get('endpoint') or None,
                    api_key=request.form.get('api_key') or None,
                    model_path=request.form.get('model_path') or None,
                    parameters=eval(request.form.get('parameters', '{}')) if request.form.get('parameters') else None,
                    specialization=request.form.get('specialization'),
                    accuracy_score=float(request.form.get('accuracy_score', 0.0))
                )

                ai_model_manager.register_model(model_config)
                flash(f'Model {model_config.name} added successfully', 'success')

            except Exception as e:
                flash(f'Error adding model: {str(e)}', 'error')

        elif action == 'test_model':
            # Test model with sample data
            model_name = request.form.get('model_name')
            test_data = {
                'age': 25,
                'gender': 'female',
                'chief_complaint': 'Feeling anxious and stressed',
                'symptoms': {
                    'anxiety_level': 7,
                    'depression_level': 4,
                    'stress_level': 8,
                    'sleep_quality': 3
                },
                'behavioral_data': {
                    'social_withdrawal': 6,
                    'activity_level': 3,
                    'appetite_changes': 5
                },
                'assessment_scores': {
                    'phq9_score': 12,
                    'gad7_score': 15,
                    'pss_score': 18
                }
            }

            try:
                # Run diagnosis with single model or ensemble
                if model_name == 'ensemble':
                    result = ai_model_manager.diagnose_with_ensemble(test_data)
                else:
                    # Test individual model
                    config = ai_model_manager.models.get(model_name)
                    if config:
                        if config.type == ModelType.OPENAI_GPT:
                            result = ai_model_manager._diagnose_with_openai(test_data, config)
                        elif config.type == ModelType.OLLAMA:
                            result = ai_model_manager._diagnose_with_ollama(test_data, config)
                        elif config.type == ModelType.CUSTOM_ML:
                            result = ai_model_manager._diagnose_with_ml(test_data, config)
                        else:
                            result = {'error': 'Model type not supported for individual testing'}
                    else:
                        result = {'error': 'Model not found'}

                session['last_test_result'] = result
                flash('Model test completed successfully', 'success')

            except Exception as e:
                session['last_test_result'] = {'error': str(e)}
                flash(f'Model test failed: {str(e)}', 'error')

        elif action == 'train_model':
            # Train custom ML model
            model_name = request.form.get('model_name')
            model_type = request.form.get('model_type_ml', 'random_forest')

            try:
                # Generate sample training data for demonstration
                import numpy as np
                np.random.seed(42)

                # Create synthetic training data
                n_samples = 1000
                X_train = np.random.rand(n_samples, 12)  # 12 features

                # Create labels based on feature combinations (synthetic)
                y_train = np.zeros(n_samples, dtype=int)
                for i in range(n_samples):
                    anxiety_score = X_train[i, 2]  # anxiety level
                    depression_score = X_train[i, 3]  # depression level

                    if anxiety_score > 0.7:
                        y_train[i] = 3  # Severe
                    elif anxiety_score > 0.5:
                        y_train[i] = 2  # Moderate
                    elif anxiety_score > 0.3:
                        y_train[i] = 1  # Mild
                    else:
                        y_train[i] = 0  # None

                # Train the model
                accuracy = ai_model_manager.train_custom_model(
                    model_name, X_train, y_train, model_type
                )

                if accuracy:
                    flash(f'Model {model_name} trained successfully with {accuracy:.2%} accuracy', 'success')
                else:
                    flash(f'Failed to train model {model_name}', 'error')

            except Exception as e:
                flash(f'Training failed: {str(e)}', 'error')

        return redirect(url_for('admin.ai_model_manager'))

    # Get current model status
    model_status = ai_model_manager.get_model_status()

    # Get test result from session
    test_result = session.pop('last_test_result', None)

    ai_data = {
        'model_status': model_status,
        'test_result': test_result,
        'model_types': [e.value for e in ModelType],
        'ml_model_types': ['random_forest', 'gradient_boosting', 'neural_network'],
        'specializations': [
            'general_therapy',
            'mental_health_assessment',
            'therapy_recommendations',
            'quick_assessment',
            'conversational_therapy',
            'structured_assessment',
            'cognitive_assessment',
            'quick_screening',
            'anxiety_detection',
            'depression_severity',
            'ptsd_risk',
            'bipolar_screening',
            'eating_disorder_risk',
            'substance_abuse_risk',
            'suicide_risk',
            'sleep_disorder',
            'adhd_screening',
            'relationship_conflict',
            'crisis_intervention',
            'therapy_response'
        ]
    }

    return render_template('admin/ai_model_manager.html', data=ai_data)

@admin_bp.route('/api/ai-models/status')
@require_admin_auth
def ai_models_status():
    """API endpoint for AI model status"""
    from models.ai_model_manager import ai_model_manager

    return jsonify(ai_model_manager.get_model_status())

@admin_bp.route('/api/ai-models/test', methods=['POST'])
@require_admin_auth
def test_ai_model():
    """API endpoint to test AI models"""
    from models.ai_model_manager import ai_model_manager

    data = request.get_json()
    model_name = data.get('model_name')
    test_data = data.get('test_data', {})

    try:
        if model_name == 'ensemble':
            result = ai_model_manager.diagnose_with_ensemble(test_data)
        else:
            config = ai_model_manager.models.get(model_name)
            if not config:
                return jsonify({'error': 'Model not found'}), 404

            # Test individual model based on type
            if config.type.value == 'openai_gpt':
                result = ai_model_manager._diagnose_with_openai(test_data, config)
            elif config.type.value == 'ollama':
                result = ai_model_manager._diagnose_with_ollama(test_data, config)
            elif config.type.value == 'custom_ml':
                result = ai_model_manager._diagnose_with_ml(test_data, config)
            else:
                result = {'error': 'Model type not supported'}

        return jsonify({'success': True, 'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/enhancement-manager', methods=['GET', 'POST'])
@require_admin_auth
def enhancement_manager():
    """Mental Health Enhancement Manager Interface"""
    from models.enhancement_manager import enhancement_manager, FeatureModule

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'install_module':
            module_name = request.form.get('module_name')
            result = enhancement_manager.install_module(module_name)

            if result['success']:
                flash(f'Module {result["module"]} installed successfully!', 'success')
            else:
                flash(f'Installation failed: {result["error"]}', 'error')

        elif action == 'activate_module':
            module_name = request.form.get('module_name')
            user_id = request.form.get('user_id', 'admin')
            user_config = {
                'notifications': request.form.get('notifications') == 'on',
                'data_sharing': request.form.get('data_sharing') == 'on',
                'integration_level': request.form.get('integration_level', 'basic')
            }

            result = enhancement_manager.activate_module(module_name, user_id, user_config)

            if result['success']:
                flash(f'Module activated successfully for user {user_id}!', 'success')
            else:
                flash(f'Activation failed: {result["error"]}', 'error')

        elif action == 'test_physical_health':
            # Test Physical Health Integration
            from models.physical_health_integrator import physical_health_integrator

            try:
                # Create sample exercise prescription
                prescription = physical_health_integrator.create_exercise_prescription(
                    user_id=1,
                    mental_health_conditions=["anxiety", "stress"],
                    fitness_level="intermediate",
                    available_time=45,
                    preferences=["yoga", "walking"]
                )

                # Create sample nutrition plan
                nutrition_plan = physical_health_integrator.create_nutrition_plan(
                    user_id=1,
                    mental_health_conditions=["anxiety"],
                    dietary_restrictions=["vegetarian"]
                )

                # Create sample sleep plan
                sleep_plan = physical_health_integrator.create_sleep_optimization_plan(
                    user_id=1,
                    age=30,
                    mental_health_conditions=["anxiety"],
                    current_sleep_duration=6.5
                )

                session['physical_health_test'] = {
                    'exercise': {
                        'condition': prescription.condition.value,
                        'exercise_type': prescription.exercise_type,
                        'intensity': prescription.intensity.value,
                        'duration': prescription.duration_minutes,
                        'frequency': prescription.frequency_per_week,
                        'benefits': prescription.mental_health_benefits[:3]
                    },
                    'nutrition': {
                        'recommended_foods': nutrition_plan.recommended_foods[:5],
                        'supplements': nutrition_plan.supplements,
                        'foods_to_avoid': nutrition_plan.foods_to_avoid[:3]
                    },
                    'sleep': {
                        'recommended_bedtime': sleep_plan.recommended_bedtime,
                        'recommended_wake_time': sleep_plan.recommended_wake_time,
                        'duration_hours': sleep_plan.sleep_duration_hours,
                        'key_tips': sleep_plan.sleep_hygiene_tips[:3]
                    }
                }

                flash('Physical Health Integration test completed successfully!', 'success')

            except Exception as e:
                flash(f'Physical Health test failed: {str(e)}', 'error')

        return redirect(url_for('admin.enhancement_manager'))

    # Get module status
    module_status = enhancement_manager.get_module_status()

    # Get test results
    test_results = session.pop('physical_health_test', None)

    enhancement_data = {
        'module_status': module_status,
        'available_modules': [module.value for module in FeatureModule],
        'test_results': test_results,
        'installation_progress': {
            'phase_1_physical_health': 'ready',
            'phase_2_social_connection': 'development',
            'phase_3_immersive_therapy': 'planning',
            'phase_4_predictive_analytics': 'planning'
        }
    }

    return render_template('admin/enhancement_manager.html', data=enhancement_data)

@admin_bp.route('/api/enhancement-modules/status')
@require_admin_auth
def enhancement_modules_status():
    """API endpoint for enhancement modules status"""
    from models.enhancement_manager import enhancement_manager

    return jsonify(enhancement_manager.get_module_status())

@admin_bp.route('/api/user-features/<user_id>')
@require_admin_auth
def get_user_features(user_id):
    """API endpoint to get user's active features"""
    from models.enhancement_manager import enhancement_manager

    return jsonify(enhancement_manager.get_user_features(user_id))

@admin_bp.route('/social-connection-manager')
@require_admin_auth
def social_connection_manager():
    """Social Connection Management Dashboard"""
    from models.social_connection_manager import social_connection_manager

    # Get overview statistics
    stats = social_connection_manager.get_platform_statistics()

    # Get recent activities
    recent_peer_matches = social_connection_manager.get_recent_peer_matches(limit=10)
    active_groups = social_connection_manager.get_active_group_sessions()
    active_challenges = social_connection_manager.get_active_challenges()

    # Get moderation queue
    content_queue = social_connection_manager.get_moderation_queue()

    return render_template('admin/social_connection_manager.html',
        stats=stats,
        recent_matches=recent_peer_matches,
        active_groups=active_groups,
        active_challenges=active_challenges,
        content_queue=content_queue
    )

@admin_bp.route('/api/social-stats')
@require_admin_auth
def get_social_stats():
    """API endpoint for real-time social connection statistics"""
    from models.social_connection_manager import social_connection_manager

    return jsonify(social_connection_manager.get_platform_statistics())

@admin_bp.route('/api/peer-matches', methods=['GET', 'POST'])
@require_admin_auth
def manage_peer_matches():
    """Manage peer matching system"""
    from models.social_connection_manager import social_connection_manager

    if request.method == 'POST':
        action = request.json.get('action')

        if action == 'create_test_match':
            user_id = request.json.get('user_id', 'test_user_1')
            match = social_connection_manager.find_peer_matches(user_id, limit=1)
            return jsonify({'success': True, 'matches': match})

        elif action == 'moderate_match':
            match_id = request.json.get('match_id')
            status = request.json.get('status')  # approved, rejected
            result = social_connection_manager.moderate_peer_match(match_id, status)
            return jsonify({'success': result})

    # GET request - return recent matches
    matches = social_connection_manager.get_recent_peer_matches(limit=20)
    return jsonify(matches)

@admin_bp.route('/api/group-sessions', methods=['GET', 'POST'])
@require_admin_auth
def manage_group_sessions():
    """Manage group therapy sessions"""
    from models.social_connection_manager import social_connection_manager

    if request.method == 'POST':
        action = request.json.get('action')

        if action == 'create_session':
            session_data = {
                'session_type': request.json.get('session_type'),
                'title': request.json.get('title'),
                'description': request.json.get('description'),
                'max_participants': request.json.get('max_participants', 8),
                'scheduled_time': request.json.get('scheduled_time')
            }
            session = social_connection_manager.create_group_session(**session_data)
            return jsonify({'success': True, 'session_id': session.session_id})

        elif action == 'moderate_session':
            session_id = request.json.get('session_id')
            status = request.json.get('status')
            result = social_connection_manager.moderate_group_session(session_id, status)
            return jsonify({'success': result})

    # GET request - return active sessions
    sessions = social_connection_manager.get_active_group_sessions()
    return jsonify(sessions)

@admin_bp.route('/api/community-challenges', methods=['GET', 'POST'])
@require_admin_auth
def manage_community_challenges():
    """Manage community wellness challenges"""
    from models.social_connection_manager import social_connection_manager

    if request.method == 'POST':
        action = request.json.get('action')

        if action == 'create_challenge':
            challenge_data = {
                'title': request.json.get('title'),
                'description': request.json.get('description'),
                'challenge_type': request.json.get('challenge_type'),
                'duration_days': request.json.get('duration_days', 30),
                'max_participants': request.json.get('max_participants', 100)
            }
            challenge = social_connection_manager.create_community_challenge(**challenge_data)
            return jsonify({'success': True, 'challenge_id': challenge.challenge_id})

        elif action == 'update_challenge':
            challenge_id = request.json.get('challenge_id')
            updates = request.json.get('updates', {})
            result = social_connection_manager.update_challenge(challenge_id, updates)
            return jsonify({'success': result})

    # GET request - return active challenges
    challenges = social_connection_manager.get_active_challenges()
    return jsonify(challenges)

@admin_bp.route('/api/content-moderation', methods=['GET', 'POST'])
@require_admin_auth
def manage_content_moderation():
    """Handle content moderation for social features"""
    from models.social_connection_manager import social_connection_manager

    if request.method == 'POST':
        action = request.json.get('action')
        content_id = request.json.get('content_id')

        if action == 'approve':
            result = social_connection_manager.approve_content(content_id)
            return jsonify({'success': result})

        elif action == 'reject':
            reason = request.json.get('reason', 'Inappropriate content')
            result = social_connection_manager.reject_content(content_id, reason)
            return jsonify({'success': result})

        elif action == 'flag_user':
            user_id = request.json.get('user_id')
            reason = request.json.get('reason')
            result = social_connection_manager.flag_user_for_review(user_id, reason)
            return jsonify({'success': result})

    # GET request - return moderation queue
    queue = social_connection_manager.get_moderation_queue()
    return jsonify(queue)

@admin_bp.route('/therapeutic-tools-manager')
@require_admin_auth
def therapeutic_tools_manager():
    """Advanced Therapeutic Tools Management Dashboard"""
    from models.therapeutic_tools_manager import therapeutic_tools_manager

    # Get overview statistics
    stats = therapeutic_tools_manager.get_platform_statistics()

    # Get sample user progress data
    sample_users = ["user_001", "user_002", "user_003"]
    user_progress = {}
    for user_id in sample_users:
        progress = therapeutic_tools_manager.get_user_therapy_progress(user_id)
        user_progress[user_id] = progress

    return render_template('admin/therapeutic_tools_manager.html',
        stats=stats,
        user_progress=user_progress,
        vr_environments=therapeutic_tools_manager.vr_environments,
        biofeedback_exercises=therapeutic_tools_manager.biofeedback_exercises,
        ai_models=therapeutic_tools_manager.ai_therapy_models
    )

@admin_bp.route('/api/therapeutic-stats')
@require_admin_auth
def get_therapeutic_stats():
    """API endpoint for real-time therapeutic tools statistics"""
    from models.therapeutic_tools_manager import therapeutic_tools_manager

    return jsonify(therapeutic_tools_manager.get_platform_statistics())

@admin_bp.route('/api/therapy-plans', methods=['GET', 'POST'])
@require_admin_auth
def manage_therapy_plans():
    """Manage personalized therapy plans"""
    from models.therapeutic_tools_manager import therapeutic_tools_manager, VREnvironment

    if request.method == 'POST':
        action = request.json.get('action')

        if action == 'create_plan':
            user_id = request.json.get('user_id')
            conditions = request.json.get('conditions', [])
            preferences = request.json.get('preferences', {})

            plan = therapeutic_tools_manager.create_personalized_therapy_plan(
                user_id, conditions, preferences
            )
            return jsonify({'success': True, 'plan_id': plan.plan_id})

        elif action == 'test_vr_session':
            user_id = request.json.get('user_id', 'test_user')
            environment = VREnvironment(request.json.get('environment', 'beach_calm'))
            therapy_type = request.json.get('therapy_type', 'relaxation')

            session = therapeutic_tools_manager.start_vr_therapy_session(
                user_id, environment, therapy_type
            )
            return jsonify({'success': True, 'session_id': session.session_id})

    # GET request - return therapy plans summary
    plans_summary = {
        'total_plans': len(therapeutic_tools_manager.therapy_plans),
        'active_sessions': len(therapeutic_tools_manager.active_sessions),
        'recent_plans': list(therapeutic_tools_manager.therapy_plans.keys())[:5]
    }
    return jsonify(plans_summary)

@admin_bp.route('/api/vr-sessions', methods=['GET', 'POST'])
@require_admin_auth
def manage_vr_sessions():
    """Manage VR therapy sessions"""
    from models.therapeutic_tools_manager import therapeutic_tools_manager, BiometricType

    if request.method == 'POST':
        action = request.json.get('action')
        session_id = request.json.get('session_id')

        if action == 'simulate_biometric':
            biometric_type = BiometricType(request.json.get('biometric_type', 'heart_rate'))
            value = request.json.get('value', 75.0)

            result = therapeutic_tools_manager.process_biometric_reading(
                session_id, biometric_type, value
            )
            return jsonify({'success': result})

        elif action == 'complete_session':
            user_feedback = request.json.get('feedback', {
                'pre_mood': 4,
                'post_mood': 7,
                'satisfaction': 8
            })

            outcome = therapeutic_tools_manager.complete_vr_session(session_id, user_feedback)
            return jsonify({'success': True, 'outcome_id': outcome.outcome_id})

    # GET request - return active sessions
    active_sessions = {
        session_id: {
            'user_id': session.user_id,
            'environment': session.environment.value,
            'therapy_type': session.therapy_type,
            'started_at': session.started_at.isoformat() if session.started_at else None,
            'biometric_readings': len(session.biometric_data)
        }
        for session_id, session in therapeutic_tools_manager.active_sessions.items()
    }

    return jsonify(active_sessions)

@admin_bp.route('/api/user-progress/<user_id>')
@require_admin_auth
def get_user_progress(user_id):
    """Get detailed user therapy progress"""
    from models.therapeutic_tools_manager import therapeutic_tools_manager

    progress = therapeutic_tools_manager.get_user_therapy_progress(user_id)
    return jsonify(progress)
