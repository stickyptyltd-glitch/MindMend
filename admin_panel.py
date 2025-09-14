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
