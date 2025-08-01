import os
import logging
import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import json
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "pk_test_placeholder")
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

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/css', exist_ok=True)

# Import models after app initialization
with app.app_context():
    from models import (
        Session, BiometricData, VideoAnalysis, Exercise,
        Patient, Assessment, TherapistSession
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
    from admin_panel import admin_bp
    from counselor_dashboard import counselor_bp
    from mobile_app import mobile_bp, MobileAppIntegration
    from payment_integration import payment_bp
    from security_enhancements import SecurityManager
    from media_pack import media_bp
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(counselor_bp)
    app.register_blueprint(payment_bp)
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

@app.route("/")
def home():
    """Home page with therapy type selection"""
    return render_template("index.html")

@app.route("/logos")
def logo_showcase():
    """Display logo options for selection"""
    return render_template("logo_showcase.html")

@app.route("/individual")
def individual_therapy():
    """Individual therapy page"""
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
        except:
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
def session():
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
    except:
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
    except:
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
    except:
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
    except:
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
    except:
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
    except:
        pass
    
    return recommendations

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Health check endpoint
@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
