
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from models.ai_manager import AIManager
from models.health_checker import HealthChecker
from models.exercise_generator import ExerciseGenerator
from models.biometric_integrator import BiometricIntegrator
import logging
from datetime import datetime

general_bp = Blueprint('general', __name__)

ai_manager = AIManager()
health_checker = HealthChecker()
exercise_generator = ExerciseGenerator()
biometric_integrator = BiometricIntegrator()

@general_bp.route("/onboarding", methods=["GET", "POST"])
def onboarding():
    """Interactive onboarding tutorial with animated character guide"""
    return render_template("onboarding.html")

@general_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Password reset page"""
    if request.method == "POST":
        email = request.form.get('email')
        
        if email:
            return render_template("forgot_password.html", 
                                 message="If an account with that email exists, we've sent password reset instructions.")
        else:
            return render_template("forgot_password.html", 
                                 error="Please enter a valid email address.")
    
    return render_template("forgot_password.html")

@general_bp.route("/user-dashboard")
def user_dashboard():
    """User dashboard with personalized widgets"""
    return render_template("dashboard_widgets.html")

@general_bp.route("/logos")
def logo_showcase():
    """Display logo options for selection"""
    return render_template("logo_showcase.html")

@general_bp.route("/brand-guide")
def brand_guide():
    """Display comprehensive brand usage guide"""
    return render_template("brand_guide.html")

@general_bp.route("/crisis-support")
def crisis_support():
    """Crisis support and emergency resources"""
    return render_template('crisis_support.html')

@general_bp.route("/counselor_signup")
def counselor_signup():
    """Placeholder for premium human counselor signup"""
    return render_template("counselor_signup.html")

@general_bp.route("/premium_session")
def premium_session():
    """Placeholder for premium human counselor sessions"""
    return render_template("premium_session.html")

@general_bp.route("/api/analyze-text", methods=["POST"])
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
        
        ai_response = ai_manager.get_advanced_analysis(text, session_type)
        alerts = health_checker.scan_text(text)
        exercises = exercise_generator.generate_exercises(text, session_type, ai_response)
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

@general_bp.route("/ai/individual", methods=["POST"])
def ai_individual_therapy():
    """AI endpoint for individual therapy responses"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
            
        message = data['message']
        context = data.get('context', 'individual_therapy')
        
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

@general_bp.route("/ai/couples", methods=["POST"])
def ai_couples_therapy():
    """AI endpoint for couples therapy responses"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
            
        message = data['message']
        context = data.get('context', 'couples_therapy')
        
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

@general_bp.route("/ai/group", methods=["POST"])
def ai_group_therapy():
    """AI endpoint for group therapy responses"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
            
        message = data['message']
        context = data.get('context', 'group_therapy')
        
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

@general_bp.route("/media-pack")
def media_pack():
    """Media pack with brand assets and guidelines"""
    return render_template("media_pack.html")

@general_bp.route("/media")
def media():
    """Redirect to media pack"""
    return redirect(url_for('general.media_pack'))

@general_bp.route("/relationship_therapy")
def relationship_therapy_page():
    """Relationship therapy main page"""
    return render_template("relationship_therapy.html")

@general_bp.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
