
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from models.database import db, Session, Exercise
from models.ai_manager import AIManager
from models.health_checker import HealthChecker
from models.exercise_generator import ExerciseGenerator
from models.therapy_ai_integration import therapy_ai_integration
import json
from datetime import datetime
import logging

therapy_bp = Blueprint('therapy', __name__)

ai_manager = AIManager()
health_checker = HealthChecker()
exercise_generator = ExerciseGenerator()

@therapy_bp.route("/individual")
def individual_therapy():
    """Individual therapy page"""
    return render_template("individual_therapy.html")

@therapy_bp.route("/individual-therapy", methods=["GET", "POST"])
def individual_therapy_session():
    """Individual therapy session with AI"""
    if request.method == "POST":
        user_input = request.form.get('user_input', '')
        
        # Get AI response
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

@therapy_bp.route("/relationship")
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

@therapy_bp.route("/group")
def group_therapy():
    """Group therapy page"""
    return render_template("group_therapy.html")

@therapy_bp.route("/api/session", methods=["POST"])
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

@therapy_bp.route("/session", methods=["GET", "POST"])
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

@therapy_bp.route("/api/sessions")
def api_sessions():
    """API endpoint for session data"""
    try:
        sessions = Session.query.order_by(Session.timestamp.desc()).all()
        return jsonify([
            {
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
            } for s in sessions
        ])
    except Exception as e:
        logging.error(f"API sessions error: {e}")
        return jsonify({"error": "Failed to retrieve sessions"}), 500

@therapy_bp.route("/api/therapy-session", methods=["POST"])
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
