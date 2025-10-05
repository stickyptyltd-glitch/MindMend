
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.ai_manager import AIManager
import logging

couples_bp = Blueprint('couples', __name__)

ai_manager = AIManager()

# Couples Counseling Routes
@couples_bp.route('/couples/login', methods=['GET', 'POST'])
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
        return redirect(url_for('couples.couples_login'))
    
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

@couples_bp.route('/couples/session')
def couples_session():
    # Check if both partners are logged in
    if not (session.get('partner1_logged_in') and session.get('partner2_logged_in')):
        flash('Both partners must be logged in to start a session.', 'warning')
        return redirect(url_for('couples.couples_login'))
    
    return render_template('couples_session.html',
                         partner1_name=session.get('partner1_name'),
                         partner2_name=session.get('partner2_name'))

@couples_bp.route('/couples/logout')
def couples_logout():
    # Clear couples session data
    session.pop('partner1_logged_in', None)
    session.pop('partner1_name', None)
    session.pop('partner1_email', None)
    session.pop('partner2_logged_in', None)
    session.pop('partner2_name', None)
    session.pop('partner2_email', None)
    
    flash('Both partners have been logged out.', 'info')
    return redirect(url_for('couples.couples_login'))

@couples_bp.route('/api/couples_session', methods=['POST'])
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
        logging.error(f'Couples session error: {e}')
        return jsonify({'error': 'Failed to process message'}), 500

@couples_bp.route('/api/couples_exercise', methods=['POST'])
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

@couples_bp.route('/api/couples_summary', methods=['GET'])
def api_couples_summary():
    return jsonify({'message': 'Coming soon'})

@couples_bp.route('/api/conversation_starter', methods=['POST'])
def api_conversation_starter():
    """Get AI-powered conversation starter for couples"""
    try:
        data = request.json
        category = data.get('category', 'random')
        depth = data.get('depth', 'medium')
        history = data.get('history', [])
        
        # Get conversation starter
        from models.conversation_starters import ConversationStarterGenerator
        conversation_starter_generator = ConversationStarterGenerator()
        starter = conversation_starter_generator.get_starter(
            category=category,
            depth=depth,
            recent_topics=history
        )
        
        return jsonify({'starter': starter})
        
    except Exception as e:
        logging.error(f'Conversation starter error: {e}')
        return jsonify({'error': 'Failed to get conversation starter'}), 500
