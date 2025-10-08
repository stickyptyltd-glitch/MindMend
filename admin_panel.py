from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
import os
from models.database import db, AdminUser, AdminAudit, Counselor
from models.subscription import NewsletterSubscription
from datetime import datetime, timedelta
from admin_security import require_admin_auth


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@require_admin_auth
def dashboard():
    """Main admin dashboard"""
    dashboard_data = {
        'system_stats': {
            'total_users': 1247,
            'active_sessions': 45,
            'total_counselors': 23,
            'revenue_this_month': 45600,
            'platform_uptime': '99.9%'
        },
        'recent_activities': [
            {
                'action': 'User Registration',
                'details': 'New user signed up',
                'timestamp': datetime.utcnow() - timedelta(minutes=15),
                'type': 'user'
            },
            {
                'action': 'Payment Processed',
                'details': 'Premium subscription - $99 AUD',
                'timestamp': datetime.utcnow() - timedelta(hours=2),
                'type': 'payment'
            }
        ]
    }

    return render_template('admin/dashboard.html', data=dashboard_data)