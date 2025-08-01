import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
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
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

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
    
    # Create all database tables
    db.create_all()

# Initialize AI components
ai_manager = AIManager()
health_checker = HealthChecker()
video_analyzer = VideoAnalyzer()
biometric_integrator = BiometricIntegrator()
exercise_generator = ExerciseGenerator()

@app.route("/")
def home():
    """Home page with therapy type selection"""
    return render_template("index.html")

@app.route("/individual")
def individual_therapy():
    """Individual therapy page"""
    return render_template("individual_therapy.html")

@app.route("/relationship")
def relationship_therapy():
    """Relationship therapy page"""
    return render_template("relationship_therapy.html")

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
