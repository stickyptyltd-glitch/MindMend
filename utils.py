
from datetime import datetime, timedelta
from models.database import Session
from functools import wraps
from flask import current_app, render_template, session
import json
from pathlib import Path
import secrets

def generate_csrf_token():
    token = secrets.token_urlsafe(32)
    session['csrf_token'] = token
    return token

def validate_csrf(token: str) -> bool:
    return bool(token) and session.get('csrf_token') == token

def check_coming_soon(feature):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            settings_file = Path(current_app.instance_path) / 'coming_soon.json'
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    if settings.get(feature, False):
                        return render_template('coming_soon.html')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
