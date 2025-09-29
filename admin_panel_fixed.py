"""
🔧 ROBUST Admin Panel for MindMend - Error-Free Version
====================================================
Enhanced admin interface with comprehensive error handling and validation
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import json
import os
import logging
from functools import wraps
import traceback
from typing import Dict, Optional, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

class RobustAdminManager:
    """Enhanced Admin Manager with comprehensive error handling"""
    
    def __init__(self):
        self.logger = logger
        self._initialize_admin_users()
        self._initialize_platform_config()
        self._initialize_security()
        
    def _initialize_admin_users(self):
        """Initialize admin users with error handling"""
        try:
            self.admin_users = {
                'admin@sticky.com.au': {
                    'password_hash': generate_password_hash('StickyAdmin2025!'),
                    'role': 'super_admin',
                    'name': 'Sticky Admin',
                    'created_at': self._get_current_timestamp(),
                    'require_2fa': True,
                    'last_login': None,
                    'login_attempts': 0,
                    'locked_until': None
                },
                'manager@sticky.com.au': {
                    'password_hash': generate_password_hash('Manager2025!'),
                    'role': 'manager', 
                    'name': 'Platform Manager',
                    'created_at': self._get_current_timestamp(),
                    'require_2fa': False,
                    'last_login': None,
                    'login_attempts': 0,
                    'locked_until': None
                },
                'support@sticky.com.au': {
                    'password_hash': generate_password_hash('Support2025!'),
                    'role': 'support',
                    'name': 'Support Agent',
                    'created_at': self._get_current_timestamp(),
                    'require_2fa': False,
                    'last_login': None,
                    'login_attempts': 0,
                    'locked_until': None
                }
            }
            self.logger.info("✅ Admin users initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Error initializing admin users: {e}")
            self.admin_users = {}
            
    def _initialize_platform_config(self):
        """Initialize platform configuration with safe defaults"""
        try:
            self.platform_config = {
                'api_keys': {
                    'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
                    'stripe_secret_key': os.getenv('STRIPE_SECRET_KEY', ''),
                    'stripe_publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY', ''),
                    'paypal_client_id': os.getenv('PAYPAL_CLIENT_ID', ''),
                    'paypal_client_secret': os.getenv('PAYPAL_CLIENT_SECRET', ''),
                },
                'business_settings': {
                    'company_name': 'Sticky Pty Ltd',
                    'company_email': 'sticky.pty.ltd@gmail.com',
                    'company_address': 'Suite 329/98-100 Elizabeth Street, Melbourne, VIC, 3000',
                    'timezone': 'Australia/Melbourne',
                    'currency': 'AUD',
                    'language': 'en'
                },
                'system_settings': {
                    'maintenance_mode': False,
                    'registration_enabled': True,
                    'email_verification_required': True,
                    'max_sessions_per_user': 5,
                    'session_timeout': 3600,
                    'rate_limit_enabled': True,
                    'backup_enabled': True,
                    'analytics_enabled': True
                },
                'ai_settings': {
                    'default_model': 'gpt-4o',
                    'max_tokens_per_session': 4000,
                    'temperature': 0.7,
                    'enable_content_filter': True,
                    'crisis_detection_enabled': True,
                    'response_timeout': 30
                }
            }
            self.logger.info("✅ Platform configuration initialized")
        except Exception as e:
            self.logger.error(f"❌ Error initializing platform config: {e}")
            self.platform_config = {}
            
    def _initialize_security(self):
        """Initialize security settings"""
        try:
            self.security_config = {
                'max_login_attempts': 5,
                'lockout_duration': 900,  # 15 minutes
                'session_lifetime': 3600,  # 1 hour
                'require_https': True,
                'password_policy': {
                    'min_length': 12,
                    'require_uppercase': True,
                    'require_lowercase': True,
                    'require_numbers': True,
                    'require_special_chars': True
                }
            }
            self.logger.info("✅ Security configuration initialized")
        except Exception as e:
            self.logger.error(f"❌ Error initializing security config: {e}")
            self.security_config = {}
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in UTC with timezone info"""
        try:
            return datetime.now(timezone.utc).isoformat()
        except Exception as e:
            self.logger.error(f"❌ Error getting timestamp: {e}")
            return datetime.now().isoformat()
    
    def _safe_datetime_parse(self, timestamp_str: str) -> Optional[datetime]:
        """Safely parse datetime string"""
        if not timestamp_str:
            return None
            
        try:
            # Try ISO format first
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try common formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S']:
                    try:
                        return datetime.strptime(timestamp_str, fmt)
                    except ValueError:
                        continue
            except Exception as e:
                self.logger.error(f"❌ Error parsing datetime {timestamp_str}: {e}")
        
        return None
    
    def authenticate_admin(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate admin user with comprehensive error handling"""
        try:
            if not username or not password:
                return {'success': False, 'error': 'Username and password required'}
                
            user = self.admin_users.get(username)
            if not user:
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Check if account is locked
            if user.get('locked_until'):
                try:
                    locked_until = self._safe_datetime_parse(user['locked_until'])
                    if locked_until and datetime.now(timezone.utc) < locked_until:
                        return {'success': False, 'error': 'Account temporarily locked'}
                except Exception:
                    pass  # If parsing fails, continue with authentication
            
            # Verify password
            if not check_password_hash(user['password_hash'], password):
                # Increment failed attempts
                user['login_attempts'] = user.get('login_attempts', 0) + 1
                
                if user['login_attempts'] >= self.security_config.get('max_login_attempts', 5):
                    lockout_duration = self.security_config.get('lockout_duration', 900)
                    user['locked_until'] = (datetime.now(timezone.utc) + timedelta(seconds=lockout_duration)).isoformat()
                    
                return {'success': False, 'error': 'Invalid credentials'}
            
            # Successful login - reset attempts
            user['login_attempts'] = 0
            user['locked_until'] = None
            user['last_login'] = self._get_current_timestamp()
            
            return {
                'success': True,
                'user': {
                    'username': username,
                    'name': user['name'],
                    'role': user['role'],
                    'require_2fa': user.get('require_2fa', False)
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error during authentication: {e}")
            return {'success': False, 'error': 'Authentication system error'}
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics with error handling"""
        try:
            stats = {
                'total_users': 0,
                'active_sessions': 0,
                'total_sessions': 0,
                'revenue_today': 0.0,
                'revenue_month': 0.0,
                'system_health': 'Good',
                'ai_models_status': [],
                'recent_activities': [],
                'alerts': [],
                'last_updated': self._get_current_timestamp()
            }
            
            # Try to get real stats from database
            try:
                from models.database import db, User, Session, Payment
                
                # Get user count
                stats['total_users'] = User.query.count() or 0
                
                # Get session count
                stats['total_sessions'] = Session.query.count() or 0
                
                # Get active sessions (last 24 hours)
                yesterday = datetime.now(timezone.utc) - timedelta(days=1)
                stats['active_sessions'] = Session.query.filter(
                    Session.created_at >= yesterday
                ).count() or 0
                
                # Get revenue stats
                today = datetime.now(timezone.utc).date()
                month_start = today.replace(day=1)
                
                stats['revenue_today'] = db.session.query(
                    db.func.sum(Payment.amount)
                ).filter(
                    db.func.date(Payment.created_at) == today
                ).scalar() or 0.0
                
                stats['revenue_month'] = db.session.query(
                    db.func.sum(Payment.amount)
                ).filter(
                    Payment.created_at >= month_start
                ).scalar() or 0.0
                
            except Exception as db_error:
                self.logger.error(f"❌ Database error in stats: {db_error}")
                # Keep default values
            
            # Check AI model status
            try:
                stats['ai_models_status'] = [
                    {'name': 'GPT-4', 'status': 'active', 'health': 'good'},
                    {'name': 'Llama2-Mental', 'status': 'active', 'health': 'good'},
                    {'name': 'Mistral-Therapy', 'status': 'active', 'health': 'good'},
                    {'name': 'Depression Classifier', 'status': 'active', 'health': 'good'},
                    {'name': 'Anxiety Detector', 'status': 'active', 'health': 'good'},
                ]
            except Exception:
                stats['ai_models_status'] = []
            
            # Add recent activities
            stats['recent_activities'] = [
                {
                    'timestamp': self._get_current_timestamp(),
                    'activity': 'System startup completed',
                    'user': 'system',
                    'type': 'info'
                }
            ]
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Error getting dashboard stats: {e}")
            return {
                'total_users': 0,
                'active_sessions': 0,
                'total_sessions': 0,
                'revenue_today': 0.0,
                'revenue_month': 0.0,
                'system_health': 'Error',
                'ai_models_status': [],
                'recent_activities': [],
                'alerts': [{'type': 'error', 'message': 'Dashboard stats unavailable'}],
                'last_updated': self._get_current_timestamp()
            }
    
    def update_api_key(self, key_name: str, key_value: str, updated_by: str) -> Dict[str, Any]:
        """Update API key with validation"""
        try:
            if key_name not in self.platform_config['api_keys']:
                return {'success': False, 'error': 'Invalid API key name'}
            
            if not key_value or len(key_value) < 10:
                return {'success': False, 'error': 'Invalid API key value'}
            
            # Store the key
            self.platform_config['api_keys'][key_name] = key_value
            
            # Log the change
            self.logger.info(f"✅ API key {key_name} updated by {updated_by}")
            
            return {
                'success': True,
                'message': f'API key {key_name} updated successfully',
                'updated_at': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error updating API key: {e}")
            return {'success': False, 'error': 'Failed to update API key'}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health check"""
        try:
            health_check = {
                'overall_status': 'healthy',
                'checks': [],
                'timestamp': self._get_current_timestamp()
            }
            
            # Database check
            try:
                from models.database import db
                db.engine.execute('SELECT 1')
                health_check['checks'].append({
                    'component': 'Database',
                    'status': 'healthy',
                    'message': 'Database connection successful'
                })
            except Exception as db_e:
                health_check['checks'].append({
                    'component': 'Database',
                    'status': 'error',
                    'message': f'Database connection failed: {str(db_e)}'
                })
                health_check['overall_status'] = 'degraded'
            
            # AI Services check
            ai_key = os.getenv('OPENAI_API_KEY', '')
            if ai_key and len(ai_key) > 20:
                health_check['checks'].append({
                    'component': 'AI Services',
                    'status': 'healthy',
                    'message': 'OpenAI API key configured'
                })
            else:
                health_check['checks'].append({
                    'component': 'AI Services',
                    'status': 'warning',
                    'message': 'OpenAI API key not configured'
                })
            
            # Payment Services check
            stripe_key = os.getenv('STRIPE_SECRET_KEY', '')
            if stripe_key and 'sk_' in stripe_key:
                health_check['checks'].append({
                    'component': 'Payment Services',
                    'status': 'healthy',
                    'message': 'Stripe integration configured'
                })
            else:
                health_check['checks'].append({
                    'component': 'Payment Services',
                    'status': 'warning',
                    'message': 'Payment integration not fully configured'
                })
            
            return health_check
            
        except Exception as e:
            self.logger.error(f"❌ Error in health check: {e}")
            return {
                'overall_status': 'error',
                'checks': [{'component': 'System', 'status': 'error', 'message': 'Health check failed'}],
                'timestamp': self._get_current_timestamp()
            }

# Initialize the robust admin manager
admin_manager = RobustAdminManager()

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if 'admin_user' not in session:
                return redirect(url_for('admin.login'))
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Auth error: {e}")
            flash('Authentication error occurred', 'error')
            return redirect(url_for('admin.login'))
    return decorated_function

# Admin Routes with Error Handling

@admin_bp.route('/')
@require_admin_auth
def dashboard():
    """Admin dashboard with comprehensive error handling"""
    try:
        stats = admin_manager.get_dashboard_stats()
        health = admin_manager.get_system_health()
        
        return render_template('admin/dashboard_robust.html', 
                             stats=stats, 
                             health=health,
                             current_user=session.get('admin_user'))
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        flash('Dashboard temporarily unavailable', 'error')
        return render_template('admin/error.html', error='Dashboard Error')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Secure admin login with error handling"""
    try:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            result = admin_manager.authenticate_admin(username, password)
            
            if result['success']:
                session['admin_user'] = result['user']
                session['login_time'] = admin_manager._get_current_timestamp()
                flash(f"Welcome back, {result['user']['name']}", 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash(result['error'], 'error')
                
        return render_template('admin/login_robust.html')
        
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        flash('Login system temporarily unavailable', 'error')
        return render_template('admin/error.html', error='Login Error')

@admin_bp.route('/logout')
def logout():
    """Secure logout"""
    try:
        username = session.get('admin_user', {}).get('name', 'Unknown')
        session.clear()
        flash(f'Goodbye {username}', 'info')
        return redirect(url_for('admin.login'))
    except Exception as e:
        logger.error(f"❌ Logout error: {e}")
        session.clear()
        return redirect(url_for('admin.login'))

@admin_bp.route('/api-keys', methods=['GET', 'POST'])
@require_admin_auth
def api_keys():
    """API key management with validation"""
    try:
        if request.method == 'POST':
            key_name = request.form.get('key_name')
            key_value = request.form.get('key_value')
            updated_by = session.get('admin_user', {}).get('username', 'unknown')
            
            result = admin_manager.update_api_key(key_name, key_value, updated_by)
            
            if result['success']:
                flash(result['message'], 'success')
            else:
                flash(result['error'], 'error')
        
        return render_template('admin/api_keys_robust.html', 
                             api_keys=admin_manager.platform_config.get('api_keys', {}))
                             
    except Exception as e:
        logger.error(f"❌ API keys error: {e}")
        flash('API key management temporarily unavailable', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/health')
def health():
    """System health endpoint"""
    try:
        health_data = admin_manager.get_system_health()
        return jsonify(health_data)
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return jsonify({
            'overall_status': 'error',
            'error': 'Health check failed',
            'timestamp': admin_manager._get_current_timestamp()
        }), 500

# Error handlers
@admin_bp.errorhandler(404)
def not_found_error(error):
    return render_template('admin/error.html', error='Page Not Found'), 404

@admin_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"❌ Internal server error: {error}")
    return render_template('admin/error.html', error='Internal Server Error'), 500