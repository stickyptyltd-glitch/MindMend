from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
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
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        # Placeholder authentication - replace with proper auth
        username = request.form.get('username')
        password = request.form.get('password')

        # Default admin credentials for testing
        if username == 'admin' and password == 'mindmend123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
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

@admin_bp.route('/api-keys', methods=['GET', 'POST'])
@require_admin_auth
def api_keys():
    """API key management"""
    if request.method == 'POST':
        flash('API keys updated successfully', 'success')
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
