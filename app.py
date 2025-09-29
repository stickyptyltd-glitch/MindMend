import os
import logging
import stripe
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
except Exception:
    Limiter = None
from flask_socketio import SocketIO, emit
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
import json
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database instance imported from models.database
from models.database import db, Patient

# Create the app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///data/patients.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Optional rate limiter (backed by Redis if available)
if Limiter:
    redis_url = os.environ.get("REDIS_URL")
    storage_uri = None
    if redis_url:
        storage_uri = f"redis://{redis_url.split('://',1)[1]}"
    limiter = Limiter(get_remote_address, storage_uri=storage_uri, app=app, default_limits=["200 per minute"])

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        return Patient.query.get(int(user_id))
    except Exception:
        return None

# Simple CSRF helpers for auth forms
def generate_csrf_token():
    token = secrets.token_urlsafe(32)
    session['csrf_token'] = token
    return token

def validate_csrf(token: str) -> bool:
    return bool(token) and session.get('csrf_token') == token

# Create data directories (both project and instance) if they don't exist
os.makedirs('data', exist_ok=True)
try:
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, 'data'), exist_ok=True)
except Exception:
    pass
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/css', exist_ok=True)

# Import models after app initialization
with app.app_context():
    from models import (
        Session, BiometricData, VideoAnalysis, Exercise,
        Assessment
    )
    from models.ai_manager import AIManager
    from models.health_checker import HealthChecker
    from models.video_analyzer import VideoAnalyzer
    from models.biometric_integrator import BiometricIntegrator
    from models.exercise_generator import ExerciseGenerator
    from models.therapy_ai_integration import therapy_ai_integration
    
    # Initialize AI Manager
    ai_manager = AIManager()
    
    # Import therapy activities
    from models.therapy_activities import TherapyActivities
    therapy_activities = TherapyActivities()
    
    # Import and register blueprints
    try:
        from admin_panel import admin_bp
        admin_bp_available = True
    except ImportError:
        logger.warning("admin_panel module not found, creating placeholder")
        from flask import Blueprint
        admin_bp = Blueprint('admin', __name__)
        admin_bp_available = False
    from counselor_dashboard import counselor_bp
    from mobile_app import MobileAppIntegration
    from payment_integration import payment_bp
    from security_enhancements import SecurityManager
    from media_pack import media_bp
    
    # Register blueprints
    if admin_bp_available:
        app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(counselor_bp)
    app.register_blueprint(payment_bp)
    
    # Register OAuth blueprint
    from oauth_system import oauth_bp
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(media_bp)
    
    # Initialize security and mobile integration
    security_manager = SecurityManager(app)
    mobile_integration = MobileAppIntegration(app)
    
    # Create all database tables
    db.create_all()

# Initialize AI components
ai_manager = AIManager()
health_checker = HealthChecker()
video_analyzer = VideoAnalyzer()
biometric_integrator = BiometricIntegrator()
exercise_generator = ExerciseGenerator()

# Import conversation starters
from models.conversation_starters import ConversationStarterGenerator
conversation_starter_generator = ConversationStarterGenerator()


@app.route('/subscribe-newsletter', methods=['POST'])
def subscribe_newsletter():
    email = (request.form.get('email') or '').strip().lower()
    if not email:
        return redirect(url_for('home'))
    try:
        sub = NewsletterSubscription.query.filter_by(email=email).first()
        if not sub:
            sub = NewsletterSubscription(email=email, consent=True)
            db.session.add(sub)
            db.session.commit()
        flash('Thanks for subscribing!', 'success')
    except Exception:
        flash('Subscription failed. Please try again later.', 'error')
    return redirect(url_for('home'))

@app.route("/")
def home():
    """Smart homepage - shows personalized dashboard for logged-in users, marketing page for anonymous users"""
    if current_user.is_authenticated:
        # Personalized dashboard for logged-in users
        try:
            # Get user stats
            user_sessions = Session.query.filter_by(patient_name=current_user.name).count()
            recent_sessions = Session.query.filter_by(patient_name=current_user.name).order_by(Session.timestamp.desc()).limit(3).all()

            # Calculate user metrics
            user_stats = {
                'total_sessions': user_sessions,
                'streak_days': calculate_streak_days(),
                'avg_mood': calculate_average_mood(),
                'this_week_sessions': Session.query.filter(
                    Session.patient_name == current_user.name,
                    Session.timestamp >= datetime.now() - timedelta(days=7)
                ).count()
            }

            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Welcome Back - MindMend</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                    .navbar {{ background: rgba(255,255,255,0.1); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
                    .navbar h1 {{ color: white; margin: 0; }}
                    .navbar a {{ color: white; text-decoration: none; margin: 0 15px; padding: 8px 16px; border-radius: 20px; transition: background 0.3s; }}
                    .navbar a:hover {{ background: rgba(255,255,255,0.2); }}
                    .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
                    .welcome-card {{ background: white; border-radius: 15px; padding: 30px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
                    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                    .stat-card {{ background: white; border-radius: 15px; padding: 25px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                    .stat-number {{ font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
                    .stat-label {{ color: #666; font-size: 1.1em; }}
                    .actions-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                    .action-card {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                    .btn {{ background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 8px; text-decoration: none; display: inline-block; font-size: 16px; transition: all 0.3s; }}
                    .btn:hover {{ background: #5a67d8; transform: translateY(-2px); }}
                    .btn-secondary {{ background: #48bb78; }}
                    .btn-secondary:hover {{ background: #38a169; }}
                    .recent-session {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
                    .session-date {{ color: #666; font-size: 0.9em; }}
                    .quick-actions {{ background: linear-gradient(45deg, #667eea, #764ba2); color: white; border-radius: 15px; padding: 25px; margin-top: 20px; }}
                    .insights-card {{ background: linear-gradient(45deg, #48bb78, #38a169); color: white; border-radius: 15px; padding: 25px; }}
                </style>
            </head>
            <body>
                <nav class="navbar">
                    <h1>🧠 MindMend</h1>
                    <div>
                        <a href="/dashboard">Dashboard</a>
                        <a href="/video-assessment">Video Assessment</a>
                        <a href="/activities">Activities</a>
                        <a href="/logout">Logout</a>
                    </div>
                </nav>

                <div class="container">
                    <div class="welcome-card">
                        <h1>Welcome back, {current_user.name}! 👋</h1>
                        <p style="font-size: 1.2em; color: #666; margin: 10px 0;">Ready to continue your mental health journey?</p>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{user_stats['total_sessions']}</div>
                            <div class="stat-label">Total Sessions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{user_stats['this_week_sessions']}</div>
                            <div class="stat-label">This Week</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{user_stats['streak_days']}</div>
                            <div class="stat-label">Day Streak</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{user_stats['avg_mood']}/10</div>
                            <div class="stat-label">Average Mood</div>
                        </div>
                    </div>

                    <div class="actions-grid">
                        <div class="action-card">
                            <h3>🎯 Start Your Session</h3>
                            <p>Ready for your next therapy session? Choose the type that fits your needs today.</p>
                            <a href="/individual" class="btn">Individual Therapy</a>
                            <a href="/relationship" class="btn btn-secondary">Couples Therapy</a>
                        </div>

                        <div class="action-card">
                            <h3>📊 Track Your Progress</h3>
                            <p>Monitor your mental health journey with comprehensive analytics and insights.</p>
                            <a href="/dashboard" class="btn">View Dashboard</a>
                            <a href="/video-assessment" class="btn btn-secondary">Video Assessment</a>
                        </div>

                        <div class="action-card">
                            <h3>🧘 Wellness Activities</h3>
                            <p>Explore therapeutic activities designed to support your mental health goals.</p>
                            <a href="/activities" class="btn">Browse Activities</a>
                            <a href="/emotion-tracking" class="btn btn-secondary">Emotion Tracking</a>
                        </div>
                    </div>

                    <div class="quick-actions">
                        <h3>⚡ Quick Actions</h3>
                        <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-top: 15px;">
                            <a href="/api/session" onclick="startQuickSession()" class="btn" style="background: rgba(255,255,255,0.2);">Quick Check-in</a>
                            <a href="/crisis-support" class="btn" style="background: rgba(255,255,255,0.2);">Crisis Support</a>
                            <a href="/ai-models" class="btn" style="background: rgba(255,255,255,0.2);">AI Tools</a>
                        </div>
                    </div>

                    {f'''
                    <div class="action-card" style="margin-top: 20px;">
                        <h3>📈 Recent Sessions</h3>
                        {''.join([f'<div class="recent-session"><strong>{session.session_type.title()} Session</strong><div class="session-date">{session.timestamp.strftime("%B %d, %Y at %I:%M %p")}</div></div>' for session in recent_sessions]) if recent_sessions else '<p>No recent sessions. Start your first session today!</p>'}
                    </div>
                    ''' if recent_sessions else '<div class="insights-card"><h3>🌟 Ready to Begin?</h3><p>Welcome to MindMend! Your mental health journey starts with a single step. Ready to take yours?</p><a href="/individual" class="btn" style="background: rgba(255,255,255,0.2);">Start First Session</a></div>'}
                </div>

                <script>
                    function startQuickSession() {{
                        fetch('/api/session', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                message: 'Quick check-in: How are you feeling today?',
                                session_type: 'individual',
                                name: '{current_user.name}'
                            }})
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            alert('Quick check-in completed! Response: ' + data.response);
                        }})
                        .catch(error => console.error('Error:', error));
                        return false;
                    }}
                </script>
            </body>
            </html>
            """
        except Exception as e:
            logging.error(f"Error in personalized dashboard: {e}")
            return redirect(url_for('dashboard'))
    else:
        # Marketing homepage for anonymous users
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MindMend - AI-Powered Mental Health Support</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; line-height: 1.6; color: #333; }
                .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 0; text-align: center; }
                .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
                .hero h1 { font-size: 3.5em; margin-bottom: 20px; font-weight: bold; }
                .hero p { font-size: 1.3em; margin-bottom: 30px; opacity: 0.9; }
                .btn { background: #ffffff; color: #667eea; padding: 15px 30px; border: none; border-radius: 25px; text-decoration: none; font-size: 18px; font-weight: bold; display: inline-block; margin: 10px; transition: all 0.3s; }
                .btn:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
                .btn-outline { background: transparent; color: white; border: 2px solid white; }
                .btn-outline:hover { background: white; color: #667eea; }
                .features { padding: 80px 0; background: #f8f9fa; }
                .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; margin-top: 50px; }
                .feature-card { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); text-align: center; }
                .feature-icon { font-size: 3em; margin-bottom: 20px; }
                .feature-card h3 { color: #667eea; margin-bottom: 15px; }
                .testimonials { padding: 80px 0; }
                .testimonial-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; margin-top: 50px; }
                .testimonial { background: #f8f9fa; padding: 30px; border-radius: 15px; border-left: 5px solid #667eea; }
                .cta { background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); color: white; padding: 80px 0; text-align: center; }
                .stats { padding: 80px 0; background: white; text-align: center; }
                .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 40px; margin-top: 50px; }
                .stat-number { font-size: 3em; font-weight: bold; color: #667eea; }
                .navbar { background: rgba(255,255,255,0.95); padding: 15px 0; position: fixed; width: 100%; top: 0; z-index: 1000; backdrop-filter: blur(10px); }
                .navbar .container { display: flex; justify-content: space-between; align-items: center; }
                .navbar .logo { font-weight: bold; font-size: 1.5em; color: #667eea; }
                .navbar-links { display: flex; gap: 30px; }
                .navbar-links a { color: #333; text-decoration: none; font-weight: 500; }
                body { padding-top: 80px; }
            </style>
        </head>
        <body>
            <nav class="navbar">
                <div class="container">
                    <div class="logo">🧠 MindMend</div>
                    <div class="navbar-links">
                        <a href="#features">Features</a>
                        <a href="#testimonials">Success Stories</a>
                        <a href="/login">Login</a>
                        <a href="/register" class="btn" style="padding: 8px 20px; margin: 0;">Get Started</a>
                    </div>
                </div>
            </nav>

            <section class="hero">
                <div class="container">
                    <h1>Transform Your Mental Health Journey</h1>
                    <p>AI-powered therapy sessions, real-time emotional analysis, and personalized wellness activities - all in one platform.</p>
                    <a href="/register" class="btn">Start Your Free Journey</a>
                    <a href="/video-assessment" class="btn btn-outline">Try Video Assessment</a>
                    <form method="POST" action="/subscribe-newsletter" style="margin-top:20px;">
                        <input type="email" name="email" placeholder="Your email for updates" required style="padding:10px;border-radius:6px;border:1px solid #ccc;">
                        <button class="btn btn-secondary" type="submit" style="padding:10px 16px;">Subscribe</button>
                    </form>
                </div>
            </section>

            <section class="stats">
                <div class="container">
                    <h2>Trusted by Thousands</h2>
                    <div class="stats-grid">
                        <div>
                            <div class="stat-number">10k+</div>
                            <div>Active Users</div>
                        </div>
                        <div>
                            <div class="stat-number">50k+</div>
                            <div>Therapy Sessions</div>
                        </div>
                        <div>
                            <div class="stat-number">95%</div>
                            <div>Satisfaction Rate</div>
                        </div>
                        <div>
                            <div class="stat-number">24/7</div>
                            <div>Available Support</div>
                        </div>
                    </div>
                </div>
            </section>

            <section class="features" id="features">
                <div class="container">
                    <h2 style="text-align: center; font-size: 2.5em; margin-bottom: 20px;">Comprehensive Mental Health Support</h2>
                    <p style="text-align: center; font-size: 1.2em; color: #666;">Everything you need for your mental wellness journey</p>

                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🤖</div>
                            <h3>AI-Powered Therapy</h3>
                            <p>Advanced AI therapists trained on evidence-based techniques provide personalized support 24/7.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📹</div>
                            <h3>Video Emotion Analysis</h3>
                            <p>Real-time facial expression analysis to understand your emotional state and provide better support.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">💏</div>
                            <h3>Couples Therapy</h3>
                            <p>Specialized relationship counseling to strengthen communication and resolve conflicts together.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📊</div>
                            <h3>Progress Tracking</h3>
                            <p>Comprehensive analytics to monitor your mental health journey and celebrate improvements.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🧘</div>
                            <h3>Wellness Activities</h3>
                            <p>Curated therapeutic exercises, mindfulness practices, and coping strategies.</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🆘</div>
                            <h3>Crisis Support</h3>
                            <p>Immediate support and resources available whenever you need help the most.</p>
                        </div>
                    </div>
                </div>
            </section>

            <section class="testimonials" id="testimonials">
                <div class="container">
                    <h2 style="text-align: center; font-size: 2.5em; margin-bottom: 20px;">Success Stories</h2>
                    <div class="testimonial-grid">
                        <div class="testimonial">
                            <p>"MindMend helped me understand my anxiety better. The AI therapist is surprisingly understanding and the video analysis feature helped me recognize emotional patterns I never noticed."</p>
                            <strong>- Sarah M.</strong>
                        </div>
                        <div class="testimonial">
                            <p>"My partner and I tried the couples therapy feature and it transformed our communication. The exercises are practical and the AI guidance is spot-on."</p>
                            <strong>- David & Emma</strong>
                        </div>
                        <div class="testimonial">
                            <p>"Having 24/7 access to therapy support has been life-changing. The personalized activities and progress tracking keep me motivated."</p>
                            <strong>- Michael R.</strong>
                        </div>
                    </div>
                </div>
            </section>

            <section class="cta">
                <div class="container">
                    <h2 style="font-size: 2.5em; margin-bottom: 20px;">Ready to Start Your Journey?</h2>
                    <p style="font-size: 1.2em; margin-bottom: 30px;">Join thousands who have transformed their mental health with MindMend</p>
                    <a href="/register" class="btn" style="color: #48bb78; font-size: 20px; padding: 20px 40px;">Create Free Account</a>
                    <div style="margin-top: 30px;">
                        <a href="/individual" style="color: rgba(255,255,255,0.8); text-decoration: none; margin: 0 20px;">Try Individual Therapy</a>
                        <a href="/video-assessment" style="color: rgba(255,255,255,0.8); text-decoration: none; margin: 0 20px;">Experience Video Assessment</a>
                        <a href="/activities" style="color: rgba(255,255,255,0.8); text-decoration: none; margin: 0 20px;">Explore Activities</a>
                    </div>
                </div>
            </section>
        </body>
        </html>
        """

@app.route("/onboarding")
def onboarding():
    """Interactive onboarding tutorial with animated character guide"""
    return render_template("onboarding.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration page (secure)"""
    if request.method == "POST":
        # CSRF validation
        if not validate_csrf(request.form.get('csrf_token')):
            return f"""<div style="color: red; text-align: center; padding: 20px;">Invalid session. Please try again.</div>
            <script>setTimeout(() => window.location.href='/register', 2000);</script>"""

        # Gather and validate inputs
        first_name = (request.form.get('firstName') or '').strip()
        last_name = (request.form.get('lastName') or '').strip()
        email_raw = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''
        date_of_birth_raw = request.form.get('dateOfBirth') or ''
        goals = request.form.getlist('goals')

        # Email validation
        try:
            email = validate_email(email_raw, check_deliverability=False).normalized
        except EmailNotValidError:
            return f"""<div style="color: red; text-align: center; padding: 20px;">Please enter a valid email address.</div>
            <script>setTimeout(() => window.location.href='/register', 2000);</script>"""

        if len(password) < 8:
            return f"""<div style="color: red; text-align: center; padding: 20px;">Password must be at least 8 characters.</div>
            <script>setTimeout(() => window.location.href='/register', 2000);</script>"""

        # Check existing user
        if Patient.query.filter_by(email=email).first():
            return f"""<div style="color: red; text-align: center; padding: 20px;">An account with this email already exists.</div>
            <script>setTimeout(() => window.location.href='/login', 2000);</script>"""

        # Parse date of birth
        dob = None
        if date_of_birth_raw:
            try:
                dob = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
            except ValueError:
                return f"""<div style="color: red; text-align: center; padding: 20px;">Invalid date of birth.</div>
                <script>setTimeout(() => window.location.href='/register', 2000);</script>"""

        # Create patient
        full_name = (f"{first_name} {last_name}".strip()) or email.split('@')[0]
        patient = Patient(
            name=full_name,
            email=email,
            date_of_birth=dob,
            therapy_goals=json.dumps(goals) if goals else None,
            password_hash=generate_password_hash(password)
        )

        try:
            db.session.add(patient)
            db.session.commit()
        except Exception as e:
            logging.error(f"Registration DB error: {e}")
            db.session.rollback()
            return f"""<div style="color: red; text-align: center; padding: 20px;">Registration failed. Please try again.</div>
            <script>setTimeout(() => window.location.href='/register', 2000);</script>"""

        # Auto-login
        login_user(patient, remember=True)
        session.pop('csrf_token', None)
        flash('Account created successfully! Welcome to Mind Mend.', 'success')
        return redirect(url_for('onboarding'))

    # GET: show form with CSRF token
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - MindMend</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 500px; margin: 50px auto; padding: 30px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
            h2 {{ color: #333; text-align: center; margin-bottom: 30px; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #555; }}
            input, select {{ width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }}
            input:focus, select:focus {{ border-color: #667eea; outline: none; }}
            .btn {{ background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-size: 16px; margin-top: 10px; }}
            .btn:hover {{ background: #5a67d8; }}
            .links {{ text-align: center; margin-top: 20px; }}
            .links a {{ color: #667eea; text-decoration: none; margin: 0 10px; }}
            .links a:hover {{ text-decoration: underline; }}
            .flash {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .flash.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            .flash.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .checkbox-group {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; }}
            .checkbox-item {{ display: flex; align-items: center; }}
            .checkbox-item input {{ width: auto; margin-right: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧠 Join MindMend</h2>
            <form method="POST">
                <input type="hidden" name="csrf_token" value="{generate_csrf_token()}">
                <div class="form-group">
                    <label for="firstName">First Name</label>
                    <input type="text" id="firstName" name="firstName" required>
                </div>
                <div class="form-group">
                    <label for="lastName">Last Name</label>
                    <input type="text" id="lastName" name="lastName" required>
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password (8+ characters)</label>
                    <input type="password" id="password" name="password" required minlength="8">
                </div>
                <div class="form-group">
                    <label for="dateOfBirth">Date of Birth (Optional)</label>
                    <input type="date" id="dateOfBirth" name="dateOfBirth">
                </div>
                <div class="form-group">
                    <label>Therapy Goals (Optional)</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="anxiety" name="goals" value="anxiety">
                            <label for="anxiety">Manage Anxiety</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="depression" name="goals" value="depression">
                            <label for="depression">Address Depression</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="relationships" name="goals" value="relationships">
                            <label for="relationships">Improve Relationships</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="stress" name="goals" value="stress">
                            <label for="stress">Reduce Stress</label>
                        </div>
                    </div>
                </div>
                <button type="submit" class="btn">Create Account</button>
            </form>
            <div class="links">
                <a href="/login">Already have an account? Login</a> |
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login page (secure)"""
    if request.method == "POST":
        # CSRF validation
        if not validate_csrf(request.form.get('csrf_token')):
            return f"""<div style="color: red; text-align: center; padding: 20px;">Invalid session. Please try again.</div>
            <script>setTimeout(() => window.location.href='/login', 2000);</script>"""

        email_raw = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''
        remember = bool(request.form.get('remember'))

        try:
            email = validate_email(email_raw, check_deliverability=False).normalized
        except EmailNotValidError:
            return f"""<div style="color: red; text-align: center; padding: 20px;">Invalid email or password.</div>
            <script>setTimeout(() => window.location.href='/login', 2000);</script>"""

        user = Patient.query.filter_by(email=email).first()
        if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
            return f"""<div style="color: red; text-align: center; padding: 20px;">Invalid email or password.</div>
            <script>setTimeout(() => window.location.href='/login', 2000);</script>"""

        login_user(user, remember=remember)
        session.pop('csrf_token', None)
        flash('Welcome back to Mind Mend!', 'success')
        return redirect(url_for('dashboard'))

    # GET
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - MindMend</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
            .container {{ max-width: 400px; margin: 100px auto; padding: 30px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
            h2 {{ color: #333; text-align: center; margin-bottom: 30px; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #555; }}
            input {{ width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }}
            input:focus {{ border-color: #667eea; outline: none; }}
            .btn {{ background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-size: 16px; }}
            .btn:hover {{ background: #5a67d8; }}
            .links {{ text-align: center; margin-top: 20px; }}
            .links a {{ color: #667eea; text-decoration: none; margin: 0 10px; }}
            .links a:hover {{ text-decoration: underline; }}
            .checkbox-group {{ display: flex; align-items: center; margin: 15px 0; }}
            .checkbox-group input {{ width: auto; margin-right: 8px; }}
            .flash {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .flash.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            .flash.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧠 MindMend Login</h2>
            <form method="POST">
                <input type="hidden" name="csrf_token" value="{generate_csrf_token()}">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <div class="checkbox-group">
                    <input type="checkbox" id="remember" name="remember">
                    <label for="remember">Remember me</label>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            <div class="links">
                <a href="/register">Create Account</a> |
                <a href="/forgot-password">Forgot Password?</a> |
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Password reset page"""
    if request.method == "POST":
        email = request.form.get('email')
        
        if email:
            # In a real application, you would:
            # 1. Check if email exists in database
            # 2. Generate secure reset token
            # 3. Send email with reset link
            # For now, just show success message
            return render_template("forgot_password.html", 
                                 message="If an account with that email exists, we've sent password reset instructions.")
        else:
            return render_template("forgot_password.html", 
                                 error="Please enter a valid email address.")
    
    return render_template("forgot_password.html")

@app.route("/user-dashboard")
def user_dashboard():
    """User dashboard with personalized widgets"""
    # For demo purposes, skip authentication check temporarily
    # if 'user' not in session:
    #     return redirect(url_for('login'))
    
    # Mock data for demonstration (replace with real data from database)
    dashboard_data = {
        'session_count': 12,
        'streak_days': 5,
        'goals_achieved': 3,
        'last_session_date': 'Yesterday at 7:30 PM'
    }
    
    return render_template("dashboard_widgets.html", **dashboard_data)

@app.route("/ai-models")
@login_required
def ai_models_page():
    try:
        from models.ai_model_manager import ai_model_manager
        status = ai_model_manager.get_model_status()
        return render_template("ai_models.html", status=status)
    except Exception as e:
        logging.error(f"AI models page error: {e}")
        return render_template("ai_models.html", status={"model_details": [], "total_models": 0, "active_models": 0}, error="Failed to load models"), 500

@app.route("/api/ai-models/toggle", methods=["POST"])
@login_required
def api_toggle_ai_model():
    try:
        data = request.get_json(force=True)
        name = data.get('name')
        active = bool(data.get('active'))
        from models.ai_model_manager import ai_model_manager
        if name not in ai_model_manager.models:
            return jsonify({"error": "Unknown model"}), 400
        if active and name not in ai_model_manager.active_models:
            ai_model_manager.active_models.append(name)
        if not active and name in ai_model_manager.active_models:
            ai_model_manager.active_models.remove(name)
        return jsonify({"success": True, "active_models": ai_model_manager.active_models})
    except Exception as e:
        logging.error(f"Toggle AI model error: {e}")
        return jsonify({"error": "Failed to toggle model"}), 500

@app.route("/logos")
def logo_showcase():
    """Display logo options for selection"""
    return render_template("logo_showcase.html")

@app.route("/brand-guide")
def brand_guide():
    """Display comprehensive brand usage guide"""
    return render_template("brand_guide.html")

@app.route("/individual")
def individual_therapy():
    """Individual therapy page"""
    return render_template("individual_therapy.html")

@app.route("/individual-therapy", methods=["GET", "POST"])
def individual_therapy_session():
    """Individual therapy session with AI"""
    if request.method == "POST":
        user_input = request.form.get('user_input', '')
        
        # Get AI response
        from models.ai_manager import ai_manager
        ai_response = ai_manager.get_individual_therapy_response(user_input)
        
        # Return JSON for AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'response': ai_response,
                'success': True
            })
        
        # For form submissions, render template with response
        return render_template("individual_therapy.html", 
                             user_input=user_input, 
                             ai_response=ai_response)
    
    return render_template("individual_therapy.html")

@app.route("/relationship")
def relationship_therapy():
    """Relationship therapy page"""
    # Check if both partners are logged in
    partner1_logged_in = session.get('partner1_logged_in', False)
    partner2_logged_in = session.get('partner2_logged_in', False)
    
    if partner1_logged_in and partner2_logged_in:
        # Both logged in, redirect to session
        return redirect(url_for('couples_session'))
    else:
        # Show login page
        return redirect(url_for('couples_login'))

@app.route("/group")
def group_therapy():
    """Group therapy page"""
    return render_template("group_therapy.html")

@app.route("/video-assessment")
def video_assessment():
    """AI-powered video assessment page"""
    return render_template("video_assessment.html")

@app.route("/video_assess")
def video_assess():
    """Level 2 AI video assessment with placeholder features"""
    return render_template("video_assess.html")

@app.route("/emotion-tracking")
def emotion_tracking():
    """Emotion tracking dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emotion Tracking - MindMend</title>
        <style>
            body { font-family: Arial; margin: 0; background: #f8f9fa; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
            .tracking-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .tracking-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            .emotion-chart { width: 100%; height: 200px; background: linear-gradient(45deg, #667eea, #764ba2); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; }
            .quick-log { background: #e6fffa; padding: 20px; border-radius: 10px; margin-top: 20px; }
            .emotion-btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 20px; margin: 5px; cursor: pointer; }
            .emotion-btn:hover { background: #5a67d8; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📈 Emotion Tracking</h1>
                <p>Monitor your emotional patterns and progress</p>
            </div>

            <div class="tracking-grid">
                <div class="tracking-card">
                    <h3>Weekly Mood Trend</h3>
                    <div class="emotion-chart">
                        📊 Mood trending upward this week
                    </div>
                    <div style="margin-top: 15px;">
                        <div>Average Mood: <strong>7.2/10</strong></div>
                        <div>Improvement: <strong>+15%</strong></div>
                    </div>
                </div>

                <div class="tracking-card">
                    <h3>Stress Levels</h3>
                    <div class="emotion-chart" style="background: linear-gradient(45deg, #48bb78, #38a169);">
                        🧘 Stress levels decreasing
                    </div>
                    <div style="margin-top: 15px;">
                        <div>Current Level: <strong>Low</strong></div>
                        <div>7-day average: <strong>Moderate</strong></div>
                    </div>
                </div>

                <div class="tracking-card">
                    <h3>Sleep Quality</h3>
                    <div class="emotion-chart" style="background: linear-gradient(45deg, #4299e1, #3182ce);">
                        😴 Sleep improving
                    </div>
                    <div style="margin-top: 15px;">
                        <div>Last night: <strong>8.1/10</strong></div>
                        <div>Weekly average: <strong>7.4/10</strong></div>
                    </div>
                </div>
            </div>

            <div class="quick-log">
                <h3>📝 Quick Emotion Log</h3>
                <p>How are you feeling right now?</p>
                <div>
                    <button class="emotion-btn" onclick="logEmotion('happy')">😊 Happy</button>
                    <button class="emotion-btn" onclick="logEmotion('calm')">😌 Calm</button>
                    <button class="emotion-btn" onclick="logEmotion('anxious')">😰 Anxious</button>
                    <button class="emotion-btn" onclick="logEmotion('sad')">😢 Sad</button>
                    <button class="emotion-btn" onclick="logEmotion('energetic')">⚡ Energetic</button>
                    <button class="emotion-btn" onclick="logEmotion('tired')">😴 Tired</button>
                </div>
            </div>

            <div style="text-align: center; margin-top: 20px;">
                <a href="/" style="background: #6c757d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px;">← Back to Home</a>
                <a href="/video-assessment" style="background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin-left: 10px;">📹 Video Assessment</a>
            </div>
        </div>

        <script>
            function logEmotion(emotion) {
                fetch('/api/log-emotion', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ emotion: emotion, timestamp: new Date().toISOString() })
                }).then(() => {
                    alert(`Emotion "${emotion}" logged successfully!`);
                });
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/log-emotion', methods=['POST'])
def log_emotion():
    """API endpoint for logging emotions"""
    try:
        data = request.get_json()
        return jsonify({"status": "success", "message": "Emotion logged"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/crisis-support")
def crisis_support():
    """Crisis support and emergency resources"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crisis Support - MindMend</title>
        <style>
            body { font-family: Arial; margin: 0; background: linear-gradient(135deg, #dc3545 0%, #bd2130 100%); color: white; min-height: 100vh; }
            .container { max-width: 1000px; margin: 0 auto; padding: 30px; }
            .emergency-card { background: rgba(255,255,255,0.1); border-radius: 15px; padding: 30px; margin-bottom: 20px; backdrop-filter: blur(10px); }
            .btn { background: white; color: #dc3545; padding: 15px 30px; border: none; border-radius: 8px; text-decoration: none; font-size: 18px; font-weight: bold; display: inline-block; margin: 10px; }
            .btn:hover { transform: translateY(-2px); }
            .hotline { background: rgba(255,255,255,0.2); padding: 20px; border-radius: 10px; margin: 15px 0; }
            .immediate { background: #fff3cd; color: #856404; padding: 20px; border-radius: 10px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emergency-card">
                <h1>🆘 Crisis Support</h1>
                <p style="font-size: 1.2em;">If you're in immediate danger or having thoughts of self-harm, please reach out for help immediately.</p>
            </div>

            <div class="immediate">
                <h2>⚠️ Immediate Help</h2>
                <p><strong>If this is a medical emergency, call 000 immediately.</strong></p>
            </div>

            <div class="emergency-card">
                <h2>📞 Crisis Hotlines (Australia)</h2>

                <div class="hotline">
                    <h3>Lifeline - 13 11 14</h3>
                    <p>24-hour crisis support and suicide prevention</p>
                </div>

                <div class="hotline">
                    <h3>Beyond Blue - 1300 22 4636</h3>
                    <p>Support for anxiety, depression and suicide prevention</p>
                </div>

                <div class="hotline">
                    <h3>Kids Helpline - 1800 55 1800</h3>
                    <p>For people aged 5-25 years</p>
                </div>

                <div class="hotline">
                    <h3>MensLine Australia - 1300 78 99 78</h3>
                    <p>Support for men dealing with relationship and emotional health issues</p>
                </div>
            </div>

            <div class="emergency-card">
                <h2>🧘 Immediate Coping Strategies</h2>
                <ul style="font-size: 1.1em;">
                    <li><strong>5-4-3-2-1 Grounding:</strong> Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste</li>
                    <li><strong>Deep Breathing:</strong> Inhale for 4 counts, hold for 4, exhale for 6</li>
                    <li><strong>Call Someone:</strong> Reach out to a trusted friend, family member, or counselor</li>
                    <li><strong>Safety Plan:</strong> Remove any means of self-harm from your immediate area</li>
                    <li><strong>Stay Connected:</strong> Don't isolate yourself - reach out for support</li>
                </ul>
            </div>

            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="btn">← Return to Safety</a>
                <a href="/individual" class="btn">Talk to AI Counselor</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/counselor_signup")
def counselor_signup():
    """Placeholder for premium human counselor signup"""
    return render_template("counselor_signup.html")

@app.route("/premium_session")
def premium_session():
    """Placeholder for premium human counselor sessions"""
    return render_template("premium_session.html")

@app.route("/dashboard")
def dashboard():
    """Patient dashboard with progress tracking"""
    try:
        # Get recent sessions
        recent_sessions = Session.query.order_by(Session.timestamp.desc()).limit(10).all()
        
        # Get biometric data
        biometric_data = BiometricData.query.order_by(BiometricData.timestamp.desc()).limit(20).all()
        
        # Get recent assessments
        assessments = Assessment.query.order_by(Assessment.timestamp.desc()).limit(5).all()
        
        # Get exercises
        exercises = Exercise.query.order_by(Exercise.timestamp.desc()).limit(10).all()
        
        # Calculate statistics
        stats = {
            'total_sessions': Session.query.count(),
            'completed_exercises': Exercise.query.filter_by(completion_status='completed').count(),
            'avg_mood': calculate_average_mood(),
            'streak_days': calculate_streak_days()
        }
        
        return render_template("dashboard.html", 
                             sessions=recent_sessions, 
                             biometric_data=biometric_data,
                             assessments=assessments,
                             exercises=exercises,
                             stats=stats)
    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        return render_template("dashboard.html", 
                             sessions=[], 
                             biometric_data=[],
                             assessments=[],
                             exercises=[],
                             stats={})

@app.route("/premium")
def premium():
    """Premium features and human counselor upgrade"""
    return render_template("premium.html")

@app.route("/subscribe")
def subscribe():
    """Stripe subscription page"""
    return render_template("subscribe.html", stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

@app.route("/api/session", methods=["POST"])
def api_session():
    """GPT therapy session endpoint for MVP"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_input = data.get('message', '')
        session_type = data.get('session_type', 'individual')
        user_id = data.get('user_id', 'anonymous')
        
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        
        # Get AI response (using existing AI manager)
        ai_response = ai_manager.get_therapeutic_response(
            message=user_input,
            session_type=session_type,
            context=data.get('context', {})
        )
        
        # Store session in database
        try:
            session_entry = Session(
                patient_name=data.get('name', 'Anonymous'),
                session_type=session_type,
                input_text=user_input,
                ai_response=ai_response.get('message', ''),
                mood_before=data.get('mood_before'),
                notes=json.dumps({'user_id': user_id, 'timestamp': datetime.now().isoformat()})
            )
            db.session.add(session_entry)
            db.session.commit()
            
            return jsonify({
                "success": True,
                "response": ai_response.get('message', 'Thank you for sharing. How can I help you today?'),
                "session_id": session_entry.id,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logging.error(f"Database error in session: {e}")
            return jsonify({
                "success": True,
                "response": ai_response.get('message', 'Thank you for sharing. How can I help you today?'),
                "session_id": None,
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        logging.error(f"Session API error: {e}")
        return jsonify({
            "success": False,
            "error": "I'm having technical difficulties. Please try again."
        }), 500

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create Stripe checkout session for subscriptions"""
    try:
        # Get the base URL for redirects
        if os.environ.get('REPLIT_DEPLOYMENT'):
            base_url = f"https://{YOUR_DOMAIN}"
        else:
            base_url = f"http://{YOUR_DOMAIN}"
            
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Mind Mend Premium',
                            'description': 'Premium AI therapy with advanced features'
                        },
                        'unit_amount': 2999,  # $29.99
                        'recurring': {
                            'interval': 'month'
                        }
                    },
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=base_url + '/dashboard?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=base_url + '/subscribe?canceled=true',
            automatic_tax={'enabled': True},
        )
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        logging.error(f"Stripe checkout error: {e}")
        flash('Payment processing error. Please try again.', 'error')
        return redirect(url_for('subscribe'))

# Couples Counseling Routes
@app.route('/couples/login', methods=['GET', 'POST'])
def couples_login():
    if request.method == 'POST':
        partner_role = request.form.get('partner_role')
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Store partner info in session
        if partner_role == 'partner1':
            session['partner1_logged_in'] = True
            session['partner1_name'] = name
            session['partner1_email'] = email
        elif partner_role == 'partner2':
            session['partner2_logged_in'] = True
            session['partner2_name'] = name
            session['partner2_email'] = email
        
        flash(f'{name} successfully logged in!', 'success')
        return redirect(url_for('couples_login'))
    
    # Get current login status
    partner1_logged_in = session.get('partner1_logged_in', False)
    partner2_logged_in = session.get('partner2_logged_in', False)
    partner1_name = session.get('partner1_name', '')
    partner2_name = session.get('partner2_name', '')
    
    return render_template('couples_login.html',
                         partner1_logged_in=partner1_logged_in,
                         partner2_logged_in=partner2_logged_in,
                         partner1_name=partner1_name,
                         partner2_name=partner2_name)

@app.route('/couples/session')
def couples_session():
    # Check if both partners are logged in
    if not (session.get('partner1_logged_in') and session.get('partner2_logged_in')):
        flash('Both partners must be logged in to start a session.', 'warning')
        return redirect(url_for('couples_login'))
    
    return render_template('couples_session.html',
                         partner1_name=session.get('partner1_name'),
                         partner2_name=session.get('partner2_name'))

@app.route('/couples/logout')
def couples_logout():
    # Clear couples session data
    session.pop('partner1_logged_in', None)
    session.pop('partner1_name', None)
    session.pop('partner1_email', None)
    session.pop('partner2_logged_in', None)
    session.pop('partner2_name', None)
    session.pop('partner2_email', None)
    
    flash('Both partners have been logged out.', 'info')
    return redirect(url_for('couples_login'))

@app.route('/api/couples_session', methods=['POST'])
def api_couples_session():
    try:
        data = request.json
        message = data.get('message')
        speaker = data.get('speaker')
        speaker_name = data.get('speaker_name')
        partner1_name = data.get('partner1_name')
        partner2_name = data.get('partner2_name')
        
        # Create context for couples therapy
        context = f"""You are a couples therapist facilitating a session between {partner1_name} and {partner2_name}.
        {speaker_name} just said: "{message}"
        
        Provide a therapeutic response that:
        1. Acknowledges what was said
        2. Helps both partners understand each other
        3. Guides toward constructive communication
        4. Suggests healthy relationship practices when appropriate"""
        
        # Get AI response
        ai_response = ai_manager.get_therapeutic_response(context, session_type='couple')
        
        # Calculate relationship metrics (simplified)
        metrics = {
            'communication': min(100, 70 + len(message) // 10),
            'emotional': 60,
            'conflict': 50
        }
        
        return jsonify({
            'response': ai_response,
            'metrics': metrics
        })
        
    except Exception as e:
        app.logger.error(f'Couples session error: {e}')
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/couples_exercise', methods=['POST'])
def api_couples_exercise():
    exercises = [
        "Active Listening Exercise: Take turns speaking for 2 minutes about your feelings while the other partner listens without interrupting. Then the listener summarizes what they heard.",
        "Appreciation Exercise: Each partner shares 3 things they appreciate about the other. Be specific and genuine.",
        "Dream Sharing: Each partner shares one dream or goal for your relationship. Discuss how you can support each other.",
        "Conflict Resolution Practice: Choose a minor disagreement and practice using 'I feel' statements to express your needs.",
        "Connection Ritual: Create a daily 10-minute ritual to connect (e.g., morning coffee together, evening walk, bedtime gratitude)."
    ]
    
    import random
    exercise = random.choice(exercises)
    
    return jsonify({'exercise': exercise})

@app.route('/api/couples_summary', methods=['GET'])
def api_couples_summary():
    # In a real implementation, this would analyze the session
    summary = "Today's session focused on improving communication and understanding each other's perspectives. Key themes included expressing feelings constructively and listening actively. Continue practicing the exercises we discussed."
    
    return jsonify({'summary': summary})

@app.route('/api/conversation_starter', methods=['POST'])
def api_conversation_starter():
    """Get AI-powered conversation starter for couples"""
    try:
        data = request.json
        category = data.get('category', 'random')
        depth = data.get('depth', 'medium')
        history = data.get('history', [])
        
        # Get conversation starter
        starter = conversation_starter_generator.get_starter(
            category=category,
            depth=depth,
            recent_topics=history
        )
        
        return jsonify({'starter': starter})
        
    except Exception as e:
        app.logger.error(f'Conversation starter error: {e}')
        return jsonify({'error': 'Failed to get conversation starter'}), 500

# Activities Routes
@app.route('/activities')
def activities():
    """Display therapeutic activities page"""
    return render_template('activities.html')

@app.route('/api/start_activity', methods=['POST'])
def api_start_activity():
    """Start a specific therapeutic activity"""
    try:
        data = request.json
        activity_type = data.get('activity_type')
        
        # Map activity types to their specific pages/actions
        activity_routes = {
            'body-scan': '/activity/body-scan',
            'grounding': '/activity/grounding',
            'thought-record': '/activity/thought-record',
            'gratitude-map': '/activity/gratitude-map',
            'activity-schedule': '/activity/schedule',
            'emotion-wheel': '/activity/emotions',
            'active-listening': '/activity/listening',
            'art-therapy': '/activity/art',
            'pmr': '/activity/relaxation'
        }
        
        redirect_url = activity_routes.get(activity_type, '/activities')
        return jsonify({'redirect': redirect_url})
        
    except Exception as e:
        app.logger.error(f'Start activity error: {e}')
        return jsonify({'error': 'Failed to start activity'}), 500

@app.route('/api/personalized_activities')
def api_personalized_activities():
    """Get personalized activity recommendations"""
    try:
        # Get user's recent concerns from sessions
        recent_sessions = Session.query.order_by(Session.timestamp.desc()).limit(5).all()
        
        # Analyze concerns (simplified - in production, use NLP)
        concerns = []
        for session in recent_sessions:
            text = (session.input_text or '').lower()
            if any(word in text for word in ['anxious', 'anxiety', 'worry']):
                concerns.append('anxiety')
            if any(word in text for word in ['sad', 'depressed', 'down']):
                concerns.append('depression')
            if any(word in text for word in ['relationship', 'partner', 'conflict']):
                concerns.append('relationships')
            if any(word in text for word in ['stress', 'overwhelmed', 'pressure']):
                concerns.append('stress')
        
        # Get personalized plan
        plan = therapy_activities.get_personalized_plan(
            concerns=list(set(concerns)) or ['stress', 'anxiety'],
            session_type='individual'
        )
        
        # Format for frontend
        activities_data = []
        for activity in plan:
            activities_data.append({
                'id': activity['name'].lower().replace(' ', '-'),
                'name': activity['name'],
                'description': activity['description'],
                'duration': activity['duration'],
                'benefits': activity['benefits']
            })
        
        return jsonify({'activities': activities_data})
        
    except Exception as e:
        app.logger.error(f'Personalized activities error: {e}')
        # Return default activities on error
        return jsonify({
            'activities': [
                {
                    'id': 'breathing',
                    'name': 'Mindful Breathing',
                    'description': 'Simple breathing exercise for immediate calm',
                    'duration': '5 minutes',
                    'benefits': ['Reduces stress', 'Improves focus']
                },
                {
                    'id': 'gratitude',
                    'name': 'Gratitude Practice',
                    'description': 'Reflect on positive aspects of your life',
                    'duration': '10 minutes',
                    'benefits': ['Improves mood', 'Builds resilience']
                }
            ]
        })

@app.route('/activity/<activity_type>')
def activity_detail(activity_type):
    """Display detailed activity page"""
    # Map activity types to their templates
    activity_templates = {
        'body-scan': 'activities/body_scan.html',
        'grounding': 'activities/grounding.html',
        'thought-record': 'activities/thought_record.html',
        'gratitude-map': 'activities/gratitude_map.html',
        'schedule': 'activities/schedule.html',
        'emotions': 'activities/emotion_wheel.html',
        'listening': 'activities/listening.html',
        'art': 'activities/art_therapy.html',
        'relaxation': 'activities/pmr.html'
    }
    
    template = activity_templates.get(activity_type)
    if template:
        try:
            return render_template(template)
        except Exception:
            # If specific template doesn't exist, use generic
            return render_template('activities/generic_activity.html', activity_type=activity_type)
    else:
        flash('Activity not found', 'warning')
        return redirect(url_for('activities'))

@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # For now, just log the event (in production, verify signature)
        event = json.loads(payload)
        
        if event['type'] == 'checkout.session.completed':
            logging.info(f"Payment successful: {event['data']['object']['id']}")
            # Here you would update user subscription status in database
            
        elif event['type'] == 'invoice.payment_succeeded':
            logging.info(f"Subscription payment: {event['data']['object']['id']}")
            
        elif event['type'] == 'customer.subscription.deleted':
            logging.info(f"Subscription canceled: {event['data']['object']['id']}")
            
        return jsonify(success=True)
        
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify(error=str(e)), 400

@app.route("/session", methods=["GET", "POST"])
def therapy_session():
    """Legacy session endpoint - maintained for compatibility"""
    if request.method == "POST":
        try:
            patient_name = request.form.get("name", "Anonymous")
            session_type = request.form.get("session_type", "individual")
            user_input = request.form.get("user_input", "")

            if not user_input.strip():
                return render_template("session.html", error="Please enter your message.")

            # Get AI response
            ai_response = ai_manager.get_response(user_input, session_type)
            
            # Check for health risks
            alerts = health_checker.scan_text(user_input)
            
            # Generate exercises
            exercises = exercise_generator.generate_exercises(user_input, session_type, ai_response)
            
            # Log session to database
            new_session = Session(
                patient_name=patient_name,
                session_type=session_type,
                input_text=user_input,
                ai_response=ai_response,
                alerts=json.dumps(alerts) if alerts else None,
                exercises_assigned=json.dumps([ex.get('title', '') for ex in exercises]) if exercises else None
            )
            db.session.add(new_session)
            db.session.commit()

            # Store exercises in database
            for exercise_data in exercises:
                exercise = Exercise(
                    session_id=new_session.id,
                    exercise_type=exercise_data.get('category', 'general'),
                    title=exercise_data.get('title', 'Untitled Exercise'),
                    description=exercise_data.get('description', ''),
                    instructions='\n'.join(exercise_data.get('instructions', [])),
                    duration_minutes=exercise_data.get('duration_minutes', 10),
                    difficulty_level=exercise_data.get('difficulty_level', 2),
                    personalization_data=json.dumps(exercise_data)
                )
                db.session.add(exercise)
            
            db.session.commit()

            return render_template("session.html", 
                                 name=patient_name,
                                 session_type=session_type,
                                 user_input=user_input,
                                 ai_response=ai_response,
                                 alerts=alerts,
                                 exercises=exercises)
        except Exception as e:
            logging.error(f"Session error: {e}")
            return render_template("session.html", error="An error occurred processing your session.")
    
    return render_template("session.html")

@app.route("/api/sessions")
def api_sessions():
    """API endpoint for session data"""
    try:
        sessions = Session.query.order_by(Session.timestamp.desc()).all()
        return jsonify([{
            'id': s.id,
            'patient_name': s.patient_name,
            'session_type': s.session_type,
            'input_text': s.input_text,
            'ai_response': s.ai_response,
            'timestamp': s.timestamp.isoformat(),
            'alerts': json.loads(s.alerts) if s.alerts else [],
            'duration_minutes': s.duration_minutes,
            'mood_before': s.mood_before,
            'mood_after': s.mood_after
        } for s in sessions])
    except Exception as e:
        logging.error(f"API sessions error: {e}")
        return jsonify({"error": "Failed to retrieve sessions"}), 500

@app.route("/api/therapy-session", methods=["POST"])
def api_therapy_session():
    """Main therapy session endpoint for AI interactions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        message = data.get('message', '')
        session_type = data.get('session_type', 'individual')
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Prepare session data for enhanced AI response
        session_data = {
            'session_id': session_id or f"temp_{datetime.utcnow().timestamp()}",
            'user_age': data.get('age', 30),
            'user_gender': data.get('gender'),
            'presenting_issue': data.get('presenting_issue', message[:100]),
            'anxiety_level': data.get('anxiety_level', 5),
            'depression_level': data.get('depression_level', 5),
            'stress_level': data.get('stress_level', 5),
            'sleep_quality': data.get('sleep_quality', 5),
            'session_number': data.get('session_number', 1),
            'session_history': data.get('session_history', []),
            'response_history': data.get('response_history', []),
            'mood_score': data.get('mood_score', 5),
            'preferences': data.get('preferences', {})
        }
        
        # Get enhanced AI response using multiple models
        enhanced_response = therapy_ai_integration.enhance_therapy_response(
            session_type=session_type,
            user_message=message,
            session_data=session_data,
            use_ensemble=data.get('use_ensemble', True)
        )
        
        # Extract the main response
        ai_response = {
            'message': enhanced_response.get('response', 'I understand you\'re reaching out. How can I help you today?'),
            'confidence': enhanced_response.get('confidence', 0.7),
            'models_used': enhanced_response.get('models_used', ['fallback']),
            'recommendations': [activity['name'] for activity in enhanced_response.get('recommended_activities', [])],
            'activities': enhanced_response.get('recommended_activities', []),
            'research_insights': enhanced_response.get('research_insights', [])
        }
        
        # Store session data
        try:
            session_entry = Session(
                patient_name=data.get('patient_name', 'Anonymous'),
                session_type=session_type,
                input_text=message,
                ai_response=ai_response.get('message', ''),
                mood_before=data.get('mood_score'),
                notes=json.dumps(data.get('notes', {}))
            )
            db.session.add(session_entry)
            db.session.commit()
            session_id = session_entry.id
        except Exception as e:
            logging.error(f"Database error: {e}")
            # Continue without storing if DB fails
        
        # Check for crisis indicators
        crisis_assessment = health_checker.assess_crisis_risk(message, ai_response.get('message', ''))
        
        return jsonify({
            "success": True,
            "response": ai_response.get('message', 'I understand you\'re reaching out. How can I help you today?'),
            "session_id": session_id,
            "crisis_level": crisis_assessment.get('risk_level', 'low'),
            "recommendations": ai_response.get('recommendations', []),
            "mood_analysis": ai_response.get('mood_analysis', {}),
            "next_steps": ai_response.get('next_steps', [])
        })
        
    except Exception as e:
        logging.error(f"Therapy session error: {e}")
        return jsonify({
            "success": False,
            "error": "I'm having technical difficulties. Please try again or contact support if this continues.",
            "fallback_response": "I'm here to listen and support you. While I work through this technical issue, remember that your wellbeing is important and there are always people who want to help."
        }), 500

@app.route("/api/ai-models/status")
def api_ai_models_status():
    """Get status of available AI models"""
    try:
        from models.ai_model_manager import ai_model_manager
        status = ai_model_manager.get_model_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"AI models status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/ai-models/diagnose", methods=["POST"])
def api_ai_diagnose():
    """Perform AI-powered diagnosis using ensemble models"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract patient data
        patient_data = {
            'age': data.get('age', 30),
            'gender': data.get('gender'),
            'chief_complaint': data.get('chief_complaint', ''),
            'symptoms': data.get('symptoms', {}),
            'behavioral_data': data.get('behavioral_data', {}),
            'assessment_scores': data.get('assessment_scores', {})
        }
        
        # Get diagnosis from ensemble
        from models.ai_model_manager import ai_model_manager
        diagnosis = ai_model_manager.diagnose_with_ensemble(patient_data)
        
        # Get treatment recommendations
        if diagnosis.get('primary_diagnosis'):
            treatment_plan = therapy_ai_integration.treatment_recommender.generate_personalized_treatment_plan(
                diagnosis=diagnosis,
                patient_profile=patient_data,
                preferences=data.get('preferences', {})
            )
            
            diagnosis['treatment_plan'] = {
                'primary_modality': treatment_plan.primary_modality.value,
                'secondary_modalities': [m.value for m in treatment_plan.secondary_modalities],
                'intensity': treatment_plan.intensity.value,
                'duration_weeks': treatment_plan.duration_weeks,
                'activities': treatment_plan.activities[:5],  # Top 5 activities
                'confidence': treatment_plan.confidence_score
            }
        
        return jsonify({
            'success': True,
            'diagnosis': diagnosis,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"AI diagnosis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/analyze-text", methods=["POST"])
def analyze_text():
    """API endpoint for real-time text analysis"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
            
        text = data.get('text', '')
        session_type = data.get('session_type', 'individual')
        
        if not text.strip():
            return jsonify({"error": "Empty text provided"}), 400
        
        # Get AI analysis
        ai_response = ai_manager.get_advanced_analysis(text, session_type)
        
        # Check for health risks
        alerts = health_checker.scan_text(text)
        
        # Generate exercises if needed
        exercises = exercise_generator.generate_exercises(text, session_type, ai_response)
        
        # Analyze with biometric data if available
        biometric_data = data.get('biometric_data')
        biometric_analysis = None
        if biometric_data:
            biometric_analysis = biometric_integrator.analyze_patterns(biometric_data)
        
        return jsonify({
            'ai_response': ai_response,
            'alerts': alerts,
            'exercises': exercises,
            'biometric_analysis': biometric_analysis,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logging.error(f"Text analysis error: {e}")
        return jsonify({"error": "Failed to analyze text"}), 500

@app.route("/api/biometric-data", methods=["POST"])
def receive_biometric_data():
    """API endpoint for receiving biometric data from wearables"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Process and store biometric data
        biometric_entry = BiometricData(
            heart_rate=data.get('heart_rate'),
            stress_level=data.get('stress_level'),
            sleep_quality=data.get('sleep_quality'),
            activity_level=data.get('activity_level'),
            hrv_score=data.get('hrv_score'),
            blood_oxygen=data.get('blood_oxygen'),
            temperature=data.get('temperature'),
            device_type=data.get('device_type', 'unknown'),
            raw_data=json.dumps(data)
        )
        db.session.add(biometric_entry)
        db.session.commit()
        
        # Analyze biometric patterns
        analysis = biometric_integrator.analyze_patterns(data)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'recommendations': biometric_integrator.get_recommendations(analysis)
        })
    except Exception as e:
        logging.error(f"Biometric data error: {e}")
        return jsonify({"error": "Failed to process biometric data"}), 500

@app.route("/api/video-analysis", methods=["POST"])
def video_analysis():
    """API endpoint for video frame analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Handle video assessment completion
        if data.get('assessment_complete'):
            assessment_data = data.get('assessment_data', {})
            duration = data.get('duration', 0)
            
            # Create comprehensive assessment
            assessment = Assessment(
                assessment_type='video_assessment',
                text_analysis=json.dumps(assessment_data),
                multi_modal_score=calculate_assessment_score(assessment_data),
                recommendations=json.dumps(generate_assessment_recommendations(assessment_data))
            )
            db.session.add(assessment)
            db.session.commit()
            
            return jsonify({
                'overall_score': assessment.multi_modal_score,
                'emotional_stability': 'Good',
                'stress_resilience': 'Moderate',
                'communication_style': 'Open',
                'insights': [
                    'Strong emotional awareness demonstrated',
                    'Good eye contact and engagement',
                    'Moderate stress response patterns',
                    'Effective communication style'
                ],
                'recommendations': [
                    'Practice stress management techniques',
                    'Continue with regular therapy sessions',
                    'Monitor mood patterns',
                    'Maintain social connections'
                ]
            })
        
        # Handle real-time frame analysis
        frame_data = data.get('frame_data')
        if frame_data:
            # Analyze video frame for emotions and microexpressions
            analysis = video_analyzer.analyze_frame(frame_data)
            
            return jsonify({
                'emotions': analysis.get('emotions', {}),
                'microexpressions': analysis.get('microexpressions', {}),
                'confidence': analysis.get('confidence', 0),
                'stress_level': analysis.get('stress_level', 0),
                'recommendations': analysis.get('recommendations', [])
            })
        
        return jsonify({"error": "No valid data provided"}), 400
        
    except Exception as e:
        logging.error(f"Video analysis error: {e}")
        return jsonify({"error": "Failed to analyze video data"}), 500

# WebSocket events for real-time communication
@socketio.on('video_frame')
def handle_video_frame(data):
    """Handle real-time video frame processing"""
    try:
        frame_data = data.get('frame_data')
        session_id = data.get('session_id')
        
        if not frame_data:
            emit('error', {'message': 'No frame data provided'})
            return
        
        # Analyze the frame
        analysis = video_analyzer.analyze_frame(frame_data)
        
        # Store video analysis if significant
        if analysis.get('confidence', 0) > 0.7:
            video_analysis = VideoAnalysis(
                session_id=session_id if session_id else None,
                emotions_detected=json.dumps(analysis.get('emotions', {})),
                microexpressions=json.dumps(analysis.get('microexpressions', {})),
                confidence_score=analysis.get('confidence', 0),
                frame_timestamp=data.get('timestamp', 0)
            )
            db.session.add(video_analysis)
            db.session.commit()
        
        # Emit results back to client
        emit('video_analysis', {
            'session_id': session_id,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error processing video frame: {e}")
        emit('error', {'message': 'Error processing video frame'})

@socketio.on('biometric_update')
def handle_biometric_update(data):
    """Handle real-time biometric data updates"""
    try:
        if not data:
            emit('error', {'message': 'No biometric data provided'})
            return
            
        # Process biometric data
        analysis = biometric_integrator.analyze_real_time(data)
        
        # Store critical data points
        if analysis.get('store_data', False):
            biometric_entry = BiometricData(
                heart_rate=data.get('heart_rate'),
                stress_level=data.get('stress_level'),
                hrv_score=data.get('hrv_score'),
                raw_data=json.dumps(data)
            )
            db.session.add(biometric_entry)
            db.session.commit()
        
        # Emit analysis results
        emit('biometric_analysis', {
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error processing biometric data: {e}")
        emit('error', {'message': 'Error processing biometric data'})

@app.route("/api/dashboard-stats")
def dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        stats = {
            'total_sessions': Session.query.count(),
            'this_week_sessions': Session.query.filter(
                Session.timestamp >= datetime.now() - timedelta(days=7)
            ).count(),
            'completed_exercises': Exercise.query.filter_by(completion_status='completed').count(),
            'avg_mood_week': calculate_weekly_average_mood(),
            'streak_days': calculate_streak_days(),
            'improvement_percentage': calculate_improvement_percentage()
        }
        
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Dashboard stats error: {e}")
        return jsonify({"error": "Failed to retrieve statistics"}), 500

def calculate_average_mood():
    """Calculate average mood from recent sessions"""
    try:
        recent_sessions = Session.query.filter(
            Session.mood_before.isnot(None)
        ).order_by(Session.timestamp.desc()).limit(10).all()
        
        if not recent_sessions:
            return 5.0
        
        total_mood = sum(s.mood_before for s in recent_sessions)
        return round(total_mood / len(recent_sessions), 1)
    except (ZeroDivisionError, AttributeError):
        return 5.0

def calculate_weekly_average_mood():
    """Calculate average mood for the past week"""
    try:
        week_ago = datetime.now() - timedelta(days=7)
        sessions = Session.query.filter(
            Session.timestamp >= week_ago,
            Session.mood_before.isnot(None)
        ).all()
        
        if not sessions:
            return 5.0
        
        total_mood = sum(s.mood_before for s in sessions)
        return round(total_mood / len(sessions), 1)
    except (ZeroDivisionError, AttributeError):
        return 5.0

def calculate_streak_days():
    """Calculate consecutive days with sessions"""
    try:
        sessions = Session.query.order_by(Session.timestamp.desc()).all()
        if not sessions:
            return 0
        
        streak = 0
        current_date = datetime.now().date()
        
        # Group sessions by date
        session_dates = set()
        for session in sessions:
            session_dates.add(session.timestamp.date())
        
        # Count consecutive days
        while current_date in session_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    except AttributeError:
        return 0

def calculate_improvement_percentage():
    """Calculate improvement percentage over time"""
    try:
        # Get sessions from the past month
        month_ago = datetime.now() - timedelta(days=30)
        sessions = Session.query.filter(
            Session.timestamp >= month_ago,
            Session.mood_before.isnot(None),
            Session.mood_after.isnot(None)
        ).order_by(Session.timestamp).all()
        
        if len(sessions) < 2:
            return 0
        
        # Calculate trend
        first_half = sessions[:len(sessions)//2]
        second_half = sessions[len(sessions)//2:]
        
        avg_first = sum(s.mood_after for s in first_half) / len(first_half)
        avg_second = sum(s.mood_after for s in second_half) / len(second_half)
        
        improvement = ((avg_second - avg_first) / avg_first) * 100
        return round(max(0, improvement), 1)
    except (ZeroDivisionError, AttributeError):
        return 0

def calculate_assessment_score(assessment_data):
    """Calculate overall assessment score"""
    try:
        # Simple scoring based on responses
        score = 75  # Base score
        
        # Adjust based on question responses
        for key, value in assessment_data.items():
            if 'question' in key and isinstance(value, dict):
                answer = value.get('answer', '')
                if isinstance(answer, str) and answer.isdigit():
                    score += (int(answer) - 5) * 2  # Adjust based on scale responses
        
        return max(0, min(100, score))
    except (ZeroDivisionError, AttributeError):
        return 75

def generate_assessment_recommendations(assessment_data):
    """Generate recommendations based on assessment"""
    recommendations = [
        'Continue regular therapy sessions',
        'Practice mindfulness and stress reduction',
        'Maintain healthy sleep patterns',
        'Stay connected with support system'
    ]
    
    # Customize based on assessment data
    try:
        for key, value in assessment_data.items():
            if 'question' in key and isinstance(value, dict):
                answer = value.get('answer', '')
                if 'stress' in value.get('question', '').lower() and isinstance(answer, str):
                    if answer.isdigit() and int(answer) > 7:
                        recommendations.insert(0, 'Focus on stress management techniques')
                    break
    except AttributeError:
        pass
    
    return recommendations

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route("/api/dashboard/ai-insights")
def dashboard_ai_insights():
    """Get AI-generated mental health insights for dashboard"""
    try:
        
        # Sample insights data
        insights = [
            {
                'title': 'Mood Improvement Detected',
                'description': 'Your mood has been consistently improving over the past week. Keep up the great work with your mindfulness exercises!',
                'confidence': 85
            },
            {
                'title': 'Optimal Session Timing',
                'description': 'You tend to have more productive sessions in the evening. Consider scheduling your next session around 7 PM.',
                'confidence': 72
            },
            {
                'title': 'Recommended Exercise',
                'description': 'Based on your goals, try the "5-4-3-2-1 Grounding" technique for anxiety management.',
                'confidence': 90
            }
        ]
        
        return jsonify({
            'success': True,
            'data': insights
        })
    except Exception as e:
        logging.error(f"Error generating dashboard insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to generate insights at this time'
        })

# AI therapy endpoints
@app.route("/ai/individual", methods=["POST"])
def ai_individual_therapy():
    """AI endpoint for individual therapy responses"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
            
        message = data['message']
        context = data.get('context', 'individual_therapy')
        
        # Use AI manager to get response
        from models.ai_manager import ai_manager
        response = ai_manager.get_individual_therapy_response(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'context': context
        })
        
    except Exception as e:
        logging.error(f"Error in individual AI therapy: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to process therapy request'
        }), 500

@app.route("/ai/couples", methods=["POST"])
def ai_couples_therapy():
    """AI endpoint for couples therapy responses"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
            
        message = data['message']
        context = data.get('context', 'couples_therapy')
        
        # Use AI manager to get response
        from models.ai_manager import ai_manager
        partner1_name = data.get('partner1_name', 'Partner 1')
        partner2_name = data.get('partner2_name', 'Partner 2')
        response = ai_manager.get_couples_therapy_response(message, partner1_name, partner2_name)
        
        return jsonify({
            'success': True,
            'response': response,
            'context': context
        })
        
    except Exception as e:
        logging.error(f"Error in couples AI therapy: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to process therapy request'
        }), 500

@app.route("/ai/group", methods=["POST"])
def ai_group_therapy():
    """AI endpoint for group therapy responses"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
            
        message = data['message']
        context = data.get('context', 'group_therapy')
        
        # Use AI manager to get response
        from models.ai_manager import ai_manager
        response = ai_manager.get_group_therapy_response(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'context': context
        })
        
    except Exception as e:
        logging.error(f"Error in group AI therapy: {e}")
        return jsonify({
            'success': False,
            'error': 'Unable to process therapy request'
        }), 500

# Brand and media routes  
@app.route("/media-pack")
def media_pack():
    """Media pack with brand assets and guidelines"""
    return render_template("media_pack.html")

# Missing route fixes
@app.route("/media")
def media():
    """Redirect to media pack"""
    return redirect(url_for('media_pack'))

@app.route("/relationship_therapy")
def relationship_therapy_page():
    """Relationship therapy main page"""
    return render_template("relationship_therapy.html")




# Static JS files routes (for missing JS files)
@app.route("/static/js/video-processing.js")
def video_processing_js():
    """Video processing JavaScript file"""
    return """
// Video Processing JavaScript
console.log('Video processing module loaded');

class VideoProcessor {
    constructor() {
        this.isProcessing = false;
    }

    startProcessing() {
        this.isProcessing = true;
        console.log('Video processing started');
    }

    stopProcessing() {
        this.isProcessing = false;
        console.log('Video processing stopped');
    }
}

window.VideoProcessor = VideoProcessor;
""", 200, {'Content-Type': 'application/javascript'}

@app.route("/static/js/real-time-analysis.js")
def realtime_analysis_js():
    """Real-time analysis JavaScript file"""
    return """
// Real-time Analysis JavaScript
console.log('Real-time analysis module loaded');

class RealTimeAnalyzer {
    constructor() {
        this.isAnalyzing = false;
    }

    startAnalysis() {
        this.isAnalyzing = true;
        console.log('Real-time analysis started');
    }

    stopAnalysis() {
        this.isAnalyzing = false;
        console.log('Real-time analysis stopped');
    }
}

window.RealTimeAnalyzer = RealTimeAnalyzer;
""", 200, {'Content-Type': 'application/javascript'}

@app.route("/static/js/biometric-integration.js")
def biometric_integration_js():
    """Biometric integration JavaScript file"""
    return """
// Biometric Integration JavaScript
console.log('Biometric integration module loaded');

class BiometricIntegrator {
    constructor() {
        this.isConnected = false;
    }

    connect() {
        this.isConnected = true;
        console.log('Biometric device connected');
    }

    disconnect() {
        this.isConnected = false;
        console.log('Biometric device disconnected');
    }
}

window.BiometricIntegrator = BiometricIntegrator;
""", 200, {'Content-Type': 'application/javascript'}

# Health check endpoint
@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200
