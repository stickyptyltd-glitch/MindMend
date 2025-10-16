"""
Admin Dashboard Module
=====================
Main dashboard with real-time metrics, alerts, and system overview
"""
import json
from datetime import datetime, timedelta
from flask import render_template, jsonify, request
from flask_socketio import emit
from sqlalchemy import func, desc
from . import admin_bp
from .auth import require_admin_auth, require_permission
from models.database import db, Patient, Session, BiometricData, Payment, Subscription

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@require_admin_auth
def dashboard():
    """Main admin dashboard with comprehensive metrics"""

    # Get current date range
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # User Statistics
    total_users = Patient.query.count()
    new_users_today = Patient.query.filter(
        func.date(Patient.created_at) == today
    ).count()
    new_users_week = Patient.query.filter(
        func.date(Patient.created_at) >= week_ago
    ).count()

    active_users_week = Session.query.filter(
        func.date(Session.timestamp) >= week_ago
    ).distinct(Session.patient_name).count()

    # Revenue Statistics
    total_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'succeeded'
    ).scalar() or 0

    revenue_month = db.session.query(func.sum(Payment.amount)).filter(
        Payment.status == 'succeeded',
        func.date(Payment.created_at) >= month_ago
    ).scalar() or 0

    # Subscription Statistics
    subscription_stats = db.session.query(
        Subscription.tier,
        func.count(Subscription.id).label('count')
    ).filter(Subscription.status == 'active').group_by(Subscription.tier).all()

    subscription_data = {}
    for tier, count in subscription_stats:
        subscription_data[tier] = count

    # Session Statistics
    total_sessions = Session.query.count()
    sessions_today = Session.query.filter(
        func.date(Session.timestamp) == today
    ).count()
    sessions_week = Session.query.filter(
        func.date(Session.timestamp) >= week_ago
    ).count()

    # Average session duration
    avg_duration = db.session.query(
        func.avg(Session.duration_minutes)
    ).scalar() or 0

    # AI Model Performance (mock data for now)
    ai_metrics = {
        'total_requests': sessions_week * 3,  # Approximate
        'avg_response_time': 1.2,
        'success_rate': 98.5,
        'active_models': 22
    }

    # System Health
    system_health = {
        'database': 'healthy',
        'redis': 'healthy',
        'ai_services': 'healthy',
        'payment_gateway': 'healthy'
    }

    # Recent Activity (last 10 sessions)
    recent_sessions = Session.query.order_by(
        desc(Session.timestamp)
    ).limit(10).all()

    # Crisis Alerts (high-risk sessions)
    crisis_sessions = Session.query.filter(
        Session.alerts.isnot(None),
        func.date(Session.timestamp) >= week_ago
    ).limit(5).all()

    # Growth Metrics
    user_growth = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = Patient.query.filter(
            func.date(Patient.created_at) == date
        ).count()
        user_growth.append({
            'date': date.strftime('%Y-%m-%d'),
            'users': count
        })

    # Revenue Growth (last 30 days)
    revenue_growth = []
    for i in range(30):
        date = today - timedelta(days=i)
        daily_revenue = db.session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'succeeded',
            func.date(Payment.created_at) == date
        ).scalar() or 0
        revenue_growth.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })

    dashboard_data = {
        'user_stats': {
            'total_users': total_users,
            'new_today': new_users_today,
            'new_week': new_users_week,
            'active_week': active_users_week,
            'growth_rate': round((new_users_week / max(total_users - new_users_week, 1)) * 100, 1)
        },
        'revenue_stats': {
            'total_revenue': float(total_revenue),
            'revenue_month': float(revenue_month),
            'mrr': float(revenue_month),  # Simplified MRR calculation
            'arpu': float(total_revenue / max(total_users, 1))
        },
        'subscription_stats': subscription_data,
        'session_stats': {
            'total_sessions': total_sessions,
            'sessions_today': sessions_today,
            'sessions_week': sessions_week,
            'avg_duration': round(avg_duration, 1) if avg_duration else 0
        },
        'ai_metrics': ai_metrics,
        'system_health': system_health,
        'recent_sessions': [{
            'id': s.id,
            'patient': s.patient_name,
            'type': s.session_type,
            'timestamp': s.timestamp.strftime('%H:%M'),
            'duration': s.duration_minutes or 0,
            'mood_change': (s.mood_after - s.mood_before) if (s.mood_after and s.mood_before) else None
        } for s in recent_sessions],
        'crisis_alerts': [{
            'id': s.id,
            'patient': s.patient_name,
            'timestamp': s.timestamp.strftime('%m/%d %H:%M'),
            'alert_type': 'High Risk',  # Simplified
            'status': 'Active'
        } for s in crisis_sessions],
        'user_growth': user_growth,
        'revenue_growth': revenue_growth
    }

    return render_template('admin/dashboard_complete.html',
                          stats=dashboard_data['user_stats'],
                          revenue=dashboard_data['revenue_stats'],
                          subscriptions=dashboard_data['subscription_stats'],
                          sessions=dashboard_data['session_stats'],
                          ai_insights=dashboard_data['ai_metrics'],
                          system_status=dashboard_data['system_health'],
                          recent_activity=dashboard_data['recent_sessions'],
                          crisis_alerts=dashboard_data['crisis_alerts'],
                          user_growth=dashboard_data['user_growth'],
                          revenue_growth=dashboard_data['revenue_growth'])

@admin_bp.route('/api/dashboard/metrics')
@require_admin_auth
def dashboard_metrics_api():
    """API endpoint for real-time dashboard metrics"""

    # Get quick stats for real-time updates
    current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'active_sessions': Session.query.filter(
            Session.timestamp >= current_hour
        ).count(),
        'new_users_hour': Patient.query.filter(
            Patient.created_at >= current_hour
        ).count(),
        'system_load': {
            'cpu': 45,  # Mock data - replace with actual system metrics
            'memory': 62,
            'database_connections': 15
        },
        'alerts': {
            'critical': 0,
            'warning': 2,
            'info': 5
        }
    }

    return jsonify(metrics)

@admin_bp.route('/api/dashboard/alerts')
@require_admin_auth
def dashboard_alerts_api():
    """API endpoint for system alerts"""

    alerts = [
        {
            'id': 1,
            'type': 'warning',
            'title': 'High Response Time',
            'message': 'AI model response time above 2 seconds',
            'timestamp': datetime.utcnow().isoformat(),
            'resolved': False
        },
        {
            'id': 2,
            'type': 'info',
            'title': 'New User Milestone',
            'message': '1000+ users reached!',
            'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            'resolved': True
        }
    ]

    return jsonify(alerts)

@admin_bp.route('/api/dashboard/user-activity')
@require_admin_auth
def user_activity_api():
    """Real-time user activity feed"""

    # Get recent user activities
    recent_sessions = Session.query.order_by(
        desc(Session.timestamp)
    ).limit(20).all()

    activities = []
    for session in recent_sessions:
        activities.append({
            'id': session.id,
            'type': 'session_started',
            'user': session.patient_name,
            'details': f"Started {session.session_type} session",
            'timestamp': session.timestamp.isoformat(),
            'duration': session.duration_minutes
        })

    return jsonify(activities)

@admin_bp.route('/quick-actions')
@require_admin_auth
def quick_actions():
    """Quick actions panel"""

    actions = [
        {
            'id': 'backup_database',
            'title': 'Backup Database',
            'description': 'Create immediate database backup',
            'icon': 'fas fa-database',
            'color': 'primary',
            'permission': 'system.backup'
        },
        {
            'id': 'send_announcement',
            'title': 'Send Announcement',
            'description': 'Send announcement to all users',
            'icon': 'fas fa-bullhorn',
            'color': 'info',
            'permission': 'marketing.announce'
        },
        {
            'id': 'generate_report',
            'title': 'Generate Report',
            'description': 'Generate comprehensive analytics report',
            'icon': 'fas fa-chart-bar',
            'color': 'success',
            'permission': 'analytics.generate'
        },
        {
            'id': 'restart_services',
            'title': 'Restart Services',
            'description': 'Restart AI and background services',
            'icon': 'fas fa-sync',
            'color': 'warning',
            'permission': 'system.restart'
        }
    ]

    return render_template('admin/quick_actions.html', actions=actions)

@admin_bp.route('/system-status')
@require_admin_auth
@require_permission('system.view')
def system_status():
    """Detailed system status page"""

    status_data = {
        'services': [
            {'name': 'Flask Application', 'status': 'healthy', 'uptime': '5 days', 'cpu': '12%', 'memory': '256MB'},
            {'name': 'PostgreSQL', 'status': 'healthy', 'uptime': '5 days', 'connections': 15, 'size': '2.1GB'},
            {'name': 'Redis Cache', 'status': 'healthy', 'uptime': '5 days', 'memory': '45MB', 'keys': 1250},
            {'name': 'Nginx', 'status': 'healthy', 'uptime': '5 days', 'requests_sec': 45},
            {'name': 'AI Models', 'status': 'healthy', 'models_loaded': 22, 'avg_response': '1.2s'},
        ],
        'performance': {
            'response_time_avg': 245,
            'requests_per_minute': 127,
            'error_rate': 0.02,
            'uptime_percentage': 99.98
        },
        'resources': {
            'cpu_usage': 45,
            'memory_usage': 62,
            'disk_usage': 38,
            'network_io': '125 KB/s'
        }
    }

    return render_template('admin/system_status.html', status=status_data)