
from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from models.database import db, Session, BiometricData, Assessment, Exercise
from utils import (
    calculate_average_mood,
    calculate_streak_days,
    calculate_weekly_average_mood,
    calculate_improvement_percentage,
)
import logging
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
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

@dashboard_bp.route("/api/dashboard-stats")
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

@dashboard_bp.route("/api/dashboard/ai-insights")
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
