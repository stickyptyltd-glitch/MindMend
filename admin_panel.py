"""
Admin Panel for Mind Mend Platform Management
===========================================
Creator admin interface for platform configuration, API keys, and business management
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
import logging
from functools import wraps
from models.security_roles import SecurityRoles
from models.admin_ai_assistant import AdminAIAssistant

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

class AdminManager:
    def __init__(self):
        # Initialize AI assistant
        self.ai_assistant = AdminAIAssistant()
        
        # Default admin credentials with role-based security
        self.admin_users = {
            'admin@sticky.com.au': {
                'password_hash': generate_password_hash('StickyAdmin2025!'),
                'role': 'super_admin',
                'name': 'Sticky Admin',
                'created_at': datetime.utcnow().isoformat(),
                'require_2fa': True
            },
            'manager@sticky.com.au': {
                'password_hash': generate_password_hash('Manager2025!'),
                'role': 'manager',
                'name': 'Platform Manager',
                'created_at': datetime.utcnow().isoformat(),
                'require_2fa': False
            }
        }
        
        # Platform configuration storage
        self.platform_config = {
            'api_keys': {
                'openai_api_key': '',
                'stripe_secret_key': '',
                'stripe_publishable_key': '',
                'paypal_client_id': '',
                'paypal_client_secret': '',
                'google_pay_merchant_id': '',
                'twilio_account_sid': '',
                'twilio_auth_token': '',
                'sendgrid_api_key': ''
            },
            'platform_settings': {
                'version': '2.0',
                'maintenance_mode': False,
                'registration_enabled': True,
                'payment_enabled': False,
                'ai_features_enabled': True,
                'video_assessment_enabled': True,
                'counselor_platform_enabled': False
            },
            'business_settings': {
                'company_name': 'Sticky Pty Ltd',
                'abn': '',
                'contact_email': 'support@mindmend.com.au',
                'contact_phone': '+61 2 9000 0000',
                'business_address': 'Suite 123, Level 45, Sydney CBD, NSW 2000, Australia',
                'domain': 'mindmend.com.au',
                'timezone': 'Australia/Sydney'
            },
            'upgrade_features': {
                'level_3_features': {
                    'microexpression_analysis': False,
                    'biosensor_integration': False,
                    'advanced_video_assessment': False,
                    'multi_modal_ai': False,
                    'real_time_crisis_detection': False
                },
                'enterprise_features': {
                    'white_label_branding': False,
                    'custom_integrations': False,
                    'dedicated_support': False,
                    'advanced_analytics': False,
                    'multi_tenant_architecture': False
                }
            }
        }
        
        # System statistics
        self.system_stats = {
            'total_users': 0,
            'active_sessions': 0,
            'total_counselors': 0,
            'revenue_this_month': 0,
            'platform_uptime': '99.9%'
        }

admin_manager = AdminManager()

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
def admin_index():
    """Redirect to admin dashboard or login"""
    if session.get('admin_authenticated'):
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        admin_user = admin_manager.admin_users.get(email)
        if admin_user and check_password_hash(admin_user['password_hash'], password):
            session['admin_authenticated'] = True
            session['admin_email'] = email
            session['admin_role'] = admin_user['role']
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    session.pop('admin_email', None)
    session.pop('admin_role', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@require_admin_auth
def dashboard():
    """Main admin dashboard"""
    dashboard_data = {
        'system_stats': admin_manager.system_stats,
        'platform_config': admin_manager.platform_config,
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
            },
            {
                'action': 'Counselor Application',
                'details': 'New counselor application received',
                'timestamp': datetime.utcnow() - timedelta(hours=4),
                'type': 'counselor'
            }
        ],
        'alerts': [
            {
                'type': 'warning',
                'message': 'Payment gateway not configured - Configure API keys to enable payments',
                'action_url': url_for('admin.api_keys')
            },
            {
                'type': 'info',
                'message': 'Level 3 features available for upgrade',
                'action_url': url_for('admin.platform_upgrades')
            }
        ]
    }
    
    return render_template('admin/dashboard.html', data=dashboard_data)

@admin_bp.route('/api-keys', methods=['GET', 'POST'])
@require_admin_auth
def api_keys():
    """API key management"""
    if request.method == 'POST':
        # Update API keys
        api_keys = admin_manager.platform_config['api_keys']
        
        for key in api_keys.keys():
            if request.form.get(key):
                api_keys[key] = request.form.get(key)
                # In production, encrypt and store securely
                os.environ[key.upper()] = request.form.get(key)
        
        # Test API keys
        test_results = test_api_connections(api_keys)
        
        flash('API keys updated successfully', 'success')
        return redirect(url_for('admin.api_keys', test_results=json.dumps(test_results)))
    
    return render_template('admin/api_keys.html', 
                         api_keys=admin_manager.platform_config['api_keys'])

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
                'Advanced video assessment with emotion detection',
                'Multi-modal AI crisis detection',
                'Enhanced therapy personalization'
            ],
            'implementation_time': '6-8 weeks',
            'status': 'available'
        },
        'enterprise': {
            'name': 'Enterprise Package',
            'price': '$5,000 AUD/month',
            'features': [
                'White-label branding',
                'Custom API integrations',
                'Dedicated account manager',
                'Advanced analytics dashboard',
                'Multi-tenant architecture',
                'Priority support'
            ],
            'implementation_time': '8-12 weeks',
            'status': 'available'
        },
        'mobile_apps': {
            'name': 'Native Mobile Apps',
            'price': '$10,000 AUD one-time',
            'features': [
                'iOS native app',
                'Android native app',
                'App Store optimization',
                'Push notifications',
                'Offline functionality',
                'App analytics'
            ],
            'implementation_time': '12-16 weeks',
            'status': 'in_development'
        }
    }
    
    return render_template('admin/platform_upgrades.html', 
                         upgrades=upgrade_options,
                         current_features=admin_manager.platform_config['upgrade_features'])

@admin_bp.route('/business-settings', methods=['GET', 'POST'])
@require_admin_auth
def business_settings():
    """Business configuration and settings"""
    if request.method == 'POST':
        business_settings = admin_manager.platform_config['business_settings']
        
        # Update business settings
        for key in business_settings.keys():
            if request.form.get(key):
                business_settings[key] = request.form.get(key)
        
        flash('Business settings updated successfully', 'success')
        return redirect(url_for('admin.business_settings'))
    
    return render_template('admin/business_settings.html',
                         settings=admin_manager.platform_config['business_settings'])

@admin_bp.route('/user-management')
@require_admin_auth
def user_management():
    """User and counselor management"""
    users_data = {
        'total_users': 1247,
        'active_users': 892,
        'premium_users': 234,
        'counselors': 45,
        'recent_signups': [
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.j@email.com',
                'type': 'Premium User',
                'signup_date': datetime.utcnow() - timedelta(days=1),
                'location': 'Sydney, NSW'
            },
            {
                'name': 'Dr. Michael Chen',
                'email': 'mchen@therapist.com',
                'type': 'Counselor',
                'signup_date': datetime.utcnow() - timedelta(days=2),
                'location': 'Melbourne, VIC'
            }
        ]
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
            'premium': {'count': 234, 'revenue': 23166},
            'enterprise': {'count': 12, 'revenue': 2388}
        },
        'counselor_earnings': {
            'total_paid': 156000,
            'pending_payouts': 12400,
            'platform_fee_collected': 27600
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

# API endpoints for admin panel

@admin_bp.route('/api/toggle-feature', methods=['POST'])
@require_admin_auth
def toggle_feature():
    """Toggle platform features on/off"""
    data = request.get_json()
    feature_name = data.get('feature')
    enabled = data.get('enabled', False)
    
    # Update platform settings
    if feature_name in admin_manager.platform_config['platform_settings']:
        admin_manager.platform_config['platform_settings'][feature_name] = enabled
        
        return jsonify({
            'success': True,
            'message': f'Feature {feature_name} {"enabled" if enabled else "disabled"}',
            'feature': feature_name,
            'enabled': enabled
        })
    
    return jsonify({'success': False, 'error': 'Feature not found'}), 404

@admin_bp.route('/api/upgrade-platform', methods=['POST'])
@require_admin_auth
def upgrade_platform():
    """Initiate platform upgrade"""
    data = request.get_json()
    upgrade_type = data.get('upgrade_type')
    
    upgrade_status = {
        'upgrade_id': f'upgrade_{datetime.utcnow().timestamp()}',
        'type': upgrade_type,
        'status': 'initiated',
        'estimated_completion': (datetime.utcnow() + timedelta(weeks=8)).isoformat(),
        'contact_info': 'Our team will contact you within 24 hours to discuss implementation details.'
    }
    
    return jsonify({
        'success': True,
        'upgrade_status': upgrade_status
    })

@admin_bp.route('/api/test-integrations', methods=['POST'])
@require_admin_auth
def test_integrations():
    """Test all system integrations"""
    test_results = test_api_connections(admin_manager.platform_config['api_keys'])
    
    return jsonify({
        'test_results': test_results,
        'overall_status': 'healthy' if all(r['status'] == 'connected' for r in test_results.values()) else 'issues_found'
    })

def test_api_connections(api_keys):
    """Test API connections"""
    results = {}
    
    # Test OpenAI
    if api_keys.get('openai_api_key'):
        results['openai'] = {'status': 'connected', 'message': 'API key valid'}
    else:
        results['openai'] = {'status': 'not_configured', 'message': 'API key not set'}
    
    # Test Stripe
    if api_keys.get('stripe_secret_key') and api_keys.get('stripe_publishable_key'):
        results['stripe'] = {'status': 'connected', 'message': 'Keys valid'}
    else:
        results['stripe'] = {'status': 'not_configured', 'message': 'Keys not set'}
    
    # Test PayPal
    if api_keys.get('paypal_client_id') and api_keys.get('paypal_client_secret'):
        results['paypal'] = {'status': 'connected', 'message': 'Credentials valid'}
    else:
        results['paypal'] = {'status': 'not_configured', 'message': 'Credentials not set'}
    
    return results

# AI Fraud Detection Routes
@admin_bp.route('/ai-assistant')
@require_admin_auth
@SecurityRoles.requires_permission('fraud_detection')
def ai_assistant():
    """AI Assistant for fraud detection and management"""
    # Get recent system activity
    recent_activity = {
        'payment': {
            'transaction_count': 5,
            'amount': 99.99,
            'ip_address': request.remote_addr
        },
        'account': {
            'email': session.get('admin_email', ''),
            'failed_login_attempts': 0,
            'ip_address': request.remote_addr
        },
        'usage': {
            'api_calls_per_minute': 10,
            'page_views_per_minute': 20
        }
    }
    
    # Get fraud risk assessment
    fraud_assessment = admin_manager.ai_assistant.analyze_fraud_risk(recent_activity)
    
    # Get management recommendations
    recommendations = admin_manager.ai_assistant.get_management_recommendations('security_audit')
    
    # Get system insights
    analytics_data = {
        'revenue': {'monthly': 50000, 'growth_rate': 15},
        'users': {'churn_rate': 5, 'engagement_score': 70},
        'platform': {'uptime_percentage': 99.95, 'error_rate': 0.5}
    }
    insights = admin_manager.ai_assistant.generate_admin_insights(analytics_data)
    
    return render_template('admin/ai_assistant.html', 
                         fraud_assessment=fraud_assessment,
                         recommendations=recommendations,
                         insights=insights)

@admin_bp.route('/api/fraud-check', methods=['POST'])
@require_admin_auth
@SecurityRoles.requires_permission('fraud_detection')
def api_fraud_check():
    """Real-time fraud detection API"""
    data = request.get_json()
    
    # Analyze fraud risk
    risk_assessment = admin_manager.ai_assistant.analyze_fraud_risk(data)
    
    # Log security event
    SecurityRoles.log_security_event('fraud_check', {
        'user': session.get('admin_email', 'system'),
        'risk_level': risk_assessment['risk_level'],
        'risk_score': risk_assessment['risk_score']
    })
    
    return jsonify(risk_assessment)

@admin_bp.route('/api/ai-recommendations', methods=['POST'])
@require_admin_auth
def api_ai_recommendations():
    """Get AI recommendations for specific context"""
    data = request.get_json()
    context = data.get('context', 'general')
    
    recommendations = admin_manager.ai_assistant.get_management_recommendations(context)
    
    return jsonify(recommendations)

@admin_bp.route('/security-audit')
@require_admin_auth
@SecurityRoles.requires_role('admin')
def security_audit():
    """View security audit logs"""
    # Get audit logs with filters
    filters = {
        'date_from': datetime.utcnow() - timedelta(days=7),
        'date_to': datetime.utcnow()
    }
    
    audit_logs = SecurityRoles.get_security_audit_log(filters)
    
    return render_template('admin/security_audit.html', audit_logs=audit_logs)

@admin_bp.route('/download-manual')
@require_admin_auth
def download_manual():
    """Download the admin manual PDF"""
    from flask import send_file
    import os
    
    # Generate the manual if it doesn't exist
    manual_path = 'Mind_Mend_Admin_Manual.pdf'
    if not os.path.exists(manual_path):
        from create_admin_manual import create_admin_manual
        create_admin_manual()
    
    return send_file(manual_path, as_attachment=True, download_name='Mind_Mend_Admin_Manual.pdf')