
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.database import db, Session
from models.therapy_activities import TherapyActivities
import logging

activities_bp = Blueprint('activities', __name__)

therapy_activities = TherapyActivities()

# Activities Routes
@activities_bp.route('/activities')
def activities():
    """Display therapeutic activities page"""
    return render_template('activities.html')

@activities_bp.route('/api/start_activity', methods=['POST'])
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
        logging.error(f'Start activity error: {e}')
        return jsonify({'error': 'Failed to start activity'}), 500

@activities_bp.route('/api/personalized_activities')
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
        logging.error(f'Personalized activities error: {e}')
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

@activities_bp.route('/activity/<activity_type>')
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
        return redirect(url_for('activities.activities'))
