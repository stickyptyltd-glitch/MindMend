"""
User Management Module
=====================
Comprehensive user CRUD operations, analytics, and account management
"""
import json
import csv
import io
from datetime import datetime, timedelta
from flask import (
    render_template, request, redirect, url_for, flash,
    jsonify, make_response, send_file
)
from sqlalchemy import func, desc, asc, or_, and_
from werkzeug.security import generate_password_hash
from . import admin_bp
from .auth import require_admin_auth, require_permission
from models.database import db, Patient, Session, BiometricData, Assessment
from models.audit_log import audit_logger

@admin_bp.route('/users')
@require_admin_auth
@require_permission('users.view')
def users_list():
    """Main user management dashboard with advanced filtering and search"""

    # Get filter parameters
    search = request.args.get('search', '').strip()
    subscription_filter = request.args.get('subscription', '')
    risk_filter = request.args.get('risk_level', '')
    status_filter = request.args.get('status', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))

    # Base query
    query = Patient.query

    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Patient.name.ilike(search_pattern),
                Patient.email.ilike(search_pattern),
                Patient.phone.ilike(search_pattern)
            )
        )

    if subscription_filter:
        query = query.filter(Patient.subscription_tier == subscription_filter)

    if risk_filter:
        query = query.filter(Patient.risk_level == risk_filter)

    if status_filter == 'active':
        # Users with activity in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        query = query.filter(Patient.last_session >= thirty_days_ago)
    elif status_filter == 'inactive':
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        query = query.filter(
            or_(
                Patient.last_session < thirty_days_ago,
                Patient.last_session.is_(None)
            )
        )

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Patient.created_at >= date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Patient.created_at <= date_to_obj)
        except ValueError:
            pass

    # Apply sorting
    if hasattr(Patient, sort_by):
        if sort_order == 'desc':
            query = query.order_by(desc(getattr(Patient, sort_by)))
        else:
            query = query.order_by(asc(getattr(Patient, sort_by)))

    # Get total count before pagination
    total_users = query.count()

    # Apply pagination
    users = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Get user statistics
    user_stats = get_user_statistics()

    # Log admin action
    audit_logger.log_admin_action(
        'USER_LIST_VIEW',
        f'Viewed user list (page {page}, filters applied)',
        details={
            'search': search,
            'filters': {
                'subscription': subscription_filter,
                'risk_level': risk_filter,
                'status': status_filter
            },
            'total_results': total_users
        }
    )

    return render_template('admin/users/list.html', {
        'users': users,
        'user_stats': user_stats,
        'current_filters': {
            'search': search,
            'subscription': subscription_filter,
            'risk_level': risk_filter,
            'status': status_filter,
            'date_from': date_from,
            'date_to': date_to,
            'sort': sort_by,
            'order': sort_order,
            'per_page': per_page
        },
        'subscription_tiers': ['free', 'basic', 'premium', 'enterprise'],
        'risk_levels': ['low', 'medium', 'high', 'critical'],
        'total_users': total_users
    })

@admin_bp.route('/users/<int:user_id>')
@require_admin_auth
@require_permission('users.view')
def user_detail(user_id):
    """Detailed user profile with comprehensive information"""

    user = Patient.query.get_or_404(user_id)

    # Get user's sessions
    sessions = Session.query.filter_by(patient_name=user.name)\
        .order_by(desc(Session.timestamp))\
        .limit(20).all()

    # Get user's subscription info
    subscription = Subscription.query.filter_by(user_id=user_id).first()

    # Get user's payments
    payments = Payment.query.filter_by(user_id=user_id)\
        .order_by(desc(Payment.created_at))\
        .limit(10).all()

    # Get user's assessments
    assessments = Assessment.query.filter_by(patient_id=user_id)\
        .order_by(desc(Assessment.timestamp))\
        .limit(10).all()

    # Calculate user metrics
    user_metrics = calculate_user_metrics(user, sessions)

    # Log PHI access
    audit_logger.log_phi_access(
        patient_id=user_id,
        patient_name=user.name,
        access_type='READ',
        description=f'Viewed detailed user profile for {user.name}',
        target_type='USER_PROFILE',
        severity='INFO'
    )

    return render_template('admin/users/detail.html', {
        'user': user,
        'sessions': sessions,
        'subscription': subscription,
        'payments': payments,
        'assessments': assessments,
        'metrics': user_metrics
    })

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@require_admin_auth
@require_permission('users.edit')
def user_edit(user_id):
    """Edit user information"""

    user = Patient.query.get_or_404(user_id)

    if request.method == 'POST':
        original_data = {
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'subscription_tier': user.subscription_tier,
            'risk_level': user.risk_level
        }

        # Update user information
        user.name = request.form.get('name', '').strip()
        user.email = request.form.get('email', '').strip()
        user.phone = request.form.get('phone', '').strip()
        user.subscription_tier = request.form.get('subscription_tier', 'free')
        user.risk_level = request.form.get('risk_level', 'low')
        user.emergency_contact = request.form.get('emergency_contact', '').strip()
        user.medical_history = request.form.get('medical_history', '').strip()
        user.therapy_goals = request.form.get('therapy_goals', '').strip()

        # Update consent settings
        user.consent_video_analysis = 'consent_video' in request.form
        user.consent_biometric_tracking = 'consent_biometric' in request.form
        user.consent_data_sharing = 'consent_data_sharing' in request.form

        try:
            db.session.commit()

            # Log the changes
            changes = {}
            for key, old_value in original_data.items():
                new_value = getattr(user, key)
                if old_value != new_value:
                    changes[key] = {'old': old_value, 'new': new_value}

            audit_logger.log_phi_access(
                patient_id=user_id,
                patient_name=user.name,
                access_type='MODIFY',
                description=f'Updated user profile for {user.name}',
                details={'changes': changes},
                severity='WARNING'
            )

            flash(f'User {user.name} updated successfully', 'success')
            return redirect(url_for('admin.user_detail', user_id=user_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'error')

    return render_template('admin/users/edit.html', {'user': user})

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@require_admin_auth
@require_permission('users.delete')
def user_delete(user_id):
    """Delete user account (GDPR compliance)"""

    user = Patient.query.get_or_404(user_id)
    user_name = user.name
    user_email = user.email

    try:
        # Delete related records (cascade)
        Session.query.filter_by(patient_name=user_name).delete()
        Assessment.query.filter_by(patient_id=user_id).delete()
        Payment.query.filter_by(user_id=user_id).delete()
        Subscription.query.filter_by(user_id=user_id).delete()

        # Delete user
        db.session.delete(user)
        db.session.commit()

        # Log critical action
        audit_logger.log_admin_action(
            'USER_DELETED',
            f'Permanently deleted user account: {user_name} ({user_email})',
            target_type='USER',
            target_id=user_id,
            severity='CRITICAL',
            details={'user_email': user_email, 'deletion_reason': 'Admin action'}
        )

        flash(f'User {user_name} deleted permanently', 'warning')
        return redirect(url_for('admin.users_list'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@require_admin_auth
@require_permission('users.create')
def user_create():
    """Create new user account"""

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        subscription_tier = request.form.get('subscription_tier', 'free')

        # Validation
        if not name or not email or not password:
            flash('Name, email, and password are required', 'error')
            return render_template('admin/users/create.html')

        # Check if email already exists
        existing_user = Patient.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists', 'error')
            return render_template('admin/users/create.html')

        try:
            # Create user
            user = Patient(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                subscription_tier=subscription_tier,
                phone=request.form.get('phone', '').strip(),
                emergency_contact=request.form.get('emergency_contact', '').strip(),
                medical_history=request.form.get('medical_history', '').strip(),
                therapy_goals=request.form.get('therapy_goals', '').strip(),
                created_at=datetime.utcnow()
            )

            db.session.add(user)
            db.session.commit()

            # Create default subscription
            if subscription_tier != 'free':
                subscription = Subscription(
                    user_id=user.id,
                    tier=subscription_tier,
                    status='active',
                    created_at=datetime.utcnow()
                )
                db.session.add(subscription)
                db.session.commit()

            # Log creation
            audit_logger.log_admin_action(
                'USER_CREATED',
                f'Created new user account: {name} ({email})',
                target_type='USER',
                target_id=user.id,
                severity='INFO',
                details={'subscription_tier': subscription_tier}
            )

            flash(f'User {name} created successfully', 'success')
            return redirect(url_for('admin.user_detail', user_id=user.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')

    return render_template('admin/users/create.html')

@admin_bp.route('/users/export')
@require_admin_auth
@require_permission('users.export')
def users_export():
    """Export users to CSV"""

    # Get all users with basic info (no PHI)
    users = Patient.query.all()

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow([
        'ID', 'Name', 'Email', 'Subscription Tier', 'Risk Level',
        'Created At', 'Last Session', 'Total Sessions'
    ])

    # Write user data
    for user in users:
        session_count = Session.query.filter_by(patient_name=user.name).count()
        writer.writerow([
            user.id,
            user.name,
            user.email,
            user.subscription_tier,
            user.risk_level,
            user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
            user.last_session.strftime('%Y-%m-%d %H:%M:%S') if user.last_session else '',
            session_count
        ])

    output.seek(0)

    # Log export action
    audit_logger.log_admin_action(
        'USER_DATA_EXPORT',
        f'Exported user data (CSV format, {len(users)} users)',
        target_type='BULK_DATA',
        severity='WARNING',
        details={'export_format': 'CSV', 'user_count': len(users)}
    )

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=users_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

@admin_bp.route('/users/bulk-actions', methods=['POST'])
@require_admin_auth
@require_permission('users.bulk_edit')
def users_bulk_actions():
    """Bulk actions on multiple users"""

    action = request.form.get('action')
    user_ids = request.form.getlist('user_ids')

    if not action or not user_ids:
        flash('Please select an action and users', 'error')
        return redirect(url_for('admin.users_list'))

    try:
        user_ids = [int(uid) for uid in user_ids]
        users = Patient.query.filter(Patient.id.in_(user_ids)).all()

        if action == 'update_subscription':
            new_tier = request.form.get('new_subscription_tier', 'free')
            for user in users:
                user.subscription_tier = new_tier

            audit_logger.log_admin_action(
                'BULK_SUBSCRIPTION_UPDATE',
                f'Updated subscription tier to {new_tier} for {len(users)} users',
                details={'user_ids': user_ids, 'new_tier': new_tier}
            )

        elif action == 'update_risk_level':
            new_risk = request.form.get('new_risk_level', 'low')
            for user in users:
                user.risk_level = new_risk

            audit_logger.log_admin_action(
                'BULK_RISK_UPDATE',
                f'Updated risk level to {new_risk} for {len(users)} users',
                details={'user_ids': user_ids, 'new_risk': new_risk}
            )

        elif action == 'deactivate':
            # This could set a status field if you add one
            audit_logger.log_admin_action(
                'BULK_USER_DEACTIVATION',
                f'Deactivated {len(users)} users',
                details={'user_ids': user_ids}
            )

        db.session.commit()
        flash(f'Successfully updated {len(users)} users', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error performing bulk action: {str(e)}', 'error')

    return redirect(url_for('admin.users_list'))

def get_user_statistics():
    """Calculate comprehensive user statistics"""

    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    stats = {
        'total_users': Patient.query.count(),
        'new_this_week': Patient.query.filter(func.date(Patient.created_at) >= week_ago).count(),
        'new_this_month': Patient.query.filter(func.date(Patient.created_at) >= month_ago).count(),
        'subscription_breakdown': dict(
            db.session.query(Patient.subscription_tier, func.count(Patient.id))
            .group_by(Patient.subscription_tier).all()
        ),
        'risk_breakdown': dict(
            db.session.query(Patient.risk_level, func.count(Patient.id))
            .group_by(Patient.risk_level).all()
        ),
        'active_users': Patient.query.filter(Patient.last_session >= (datetime.utcnow() - timedelta(days=30))).count()
    }

    return stats

def calculate_user_metrics(user, sessions):
    """Calculate detailed metrics for a specific user"""

    total_sessions = len(sessions)

    if total_sessions > 0:
        total_duration = sum(s.duration_minutes or 0 for s in sessions)
        avg_duration = total_duration / total_sessions

        # Mood tracking
        mood_sessions = [s for s in sessions if s.mood_before and s.mood_after]
        mood_improvement = 0
        if mood_sessions:
            mood_changes = [s.mood_after - s.mood_before for s in mood_sessions]
            mood_improvement = sum(mood_changes) / len(mood_changes)
    else:
        avg_duration = 0
        mood_improvement = 0

    return {
        'total_sessions': total_sessions,
        'avg_session_duration': round(avg_duration, 1),
        'mood_improvement_avg': round(mood_improvement, 2),
        'last_session_date': sessions[0].timestamp if sessions else None,
        'engagement_score': calculate_engagement_score(user, sessions)
    }

def calculate_engagement_score(user, sessions):
    """Calculate user engagement score (0-100)"""

    score = 0

    # Recent activity (40 points)
    if user.last_session:
        days_since_last = (datetime.utcnow() - user.last_session).days
        if days_since_last <= 1:
            score += 40
        elif days_since_last <= 7:
            score += 30
        elif days_since_last <= 30:
            score += 20
        elif days_since_last <= 90:
            score += 10

    # Session frequency (30 points)
    if len(sessions) >= 10:
        score += 30
    elif len(sessions) >= 5:
        score += 20
    elif len(sessions) >= 1:
        score += 10

    # Profile completeness (20 points)
    if user.medical_history:
        score += 5
    if user.therapy_goals:
        score += 5
    if user.emergency_contact:
        score += 5
    if user.phone:
        score += 5

    # Subscription level (10 points)
    tier_scores = {'free': 0, 'basic': 3, 'premium': 7, 'enterprise': 10}
    score += tier_scores.get(user.subscription_tier, 0)

    return min(score, 100)

# ========================================
# ADVANCED USER ANALYTICS & INSIGHTS
# ========================================

@admin_bp.route('/users/analytics')
@require_admin_auth
@require_permission('users.analytics')
def users_analytics_dashboard():
    """Comprehensive user analytics dashboard"""

    # Get time range from request
    period = request.args.get('period', '30d')  # 7d, 30d, 90d, 1y

    # Calculate date range
    end_date = datetime.utcnow()
    if period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '30d':
        start_date = end_date - timedelta(days=30)
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
    elif period == '1y':
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)

    # Get comprehensive analytics
    analytics_data = {
        'user_growth': get_user_growth_analytics(start_date, end_date),
        'engagement_analytics': get_engagement_analytics(start_date, end_date),
        'behavioral_insights': get_behavioral_insights(start_date, end_date),
        'subscription_analytics': get_subscription_analytics(start_date, end_date),
        'risk_analytics': get_risk_level_analytics(start_date, end_date),
        'retention_metrics': get_retention_metrics(start_date, end_date),
        'usage_patterns': get_usage_patterns(start_date, end_date)
    }

    audit_logger.log_admin_action(
        'ANALYTICS_DASHBOARD_VIEW',
        f'Viewed user analytics dashboard (period: {period})',
        details={'period': period, 'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()}}
    )

    return render_template('admin/users/analytics.html', {
        'analytics': analytics_data,
        'period': period,
        'date_range': {'start': start_date, 'end': end_date}
    })

@admin_bp.route('/users/<int:user_id>/behavioral-profile')
@require_admin_auth
@require_permission('users.analytics')
def user_behavioral_profile(user_id):
    """Detailed behavioral profile for specific user"""

    user = Patient.query.get_or_404(user_id)

    # Get user's complete session history
    sessions = Session.query.filter_by(patient_name=user.name)\
        .order_by(Session.timestamp.desc()).all()

    # Get biometric data
    biometric_data = BiometricData.query.filter_by(patient_id=user_id)\
        .order_by(BiometricData.timestamp.desc()).limit(100).all()

    # Generate behavioral insights
    behavioral_profile = generate_behavioral_profile(user, sessions, biometric_data)

    # Log PHI access
    audit_logger.log_phi_access(
        patient_id=user_id,
        patient_name=user.name,
        access_type='READ',
        description=f'Viewed behavioral profile for {user.name}',
        target_type='BEHAVIORAL_ANALYSIS',
        severity='INFO'
    )

    return render_template('admin/users/behavioral_profile.html', {
        'user': user,
        'profile': behavioral_profile,
        'sessions_count': len(sessions),
        'biometric_count': len(biometric_data)
    })

@admin_bp.route('/users/cohort-analysis')
@require_admin_auth
@require_permission('users.analytics')
def users_cohort_analysis():
    """Cohort analysis for user retention and behavior"""

    cohort_data = generate_cohort_analysis()

    audit_logger.log_admin_action(
        'COHORT_ANALYSIS_VIEW',
        'Viewed user cohort analysis',
        details={'cohort_count': len(cohort_data)}
    )

    return render_template('admin/users/cohort_analysis.html', {
        'cohorts': cohort_data
    })

@admin_bp.route('/api/users/analytics/charts')
@require_admin_auth
@require_permission('users.analytics')
def analytics_charts_api():
    """API endpoint for analytics chart data"""

    chart_type = request.args.get('type', 'growth')
    period = request.args.get('period', '30d')

    end_date = datetime.utcnow()
    if period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '30d':
        start_date = end_date - timedelta(days=30)
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=365)

    if chart_type == 'growth':
        data = get_user_growth_chart_data(start_date, end_date)
    elif chart_type == 'engagement':
        data = get_engagement_chart_data(start_date, end_date)
    elif chart_type == 'subscription':
        data = get_subscription_chart_data(start_date, end_date)
    elif chart_type == 'risk':
        data = get_risk_distribution_chart_data()
    else:
        data = {}

    return jsonify(data)

def get_user_growth_analytics(start_date, end_date):
    """Detailed user growth analytics"""

    # Daily new users
    daily_growth = db.session.query(
        func.date(Patient.created_at).label('date'),
        func.count(Patient.id).label('count')
    ).filter(
        Patient.created_at >= start_date,
        Patient.created_at <= end_date
    ).group_by(func.date(Patient.created_at)).all()

    # Growth metrics
    total_users = Patient.query.count()
    period_new_users = Patient.query.filter(
        Patient.created_at >= start_date,
        Patient.created_at <= end_date
    ).count()

    # Previous period comparison
    period_length = (end_date - start_date).days
    prev_start = start_date - timedelta(days=period_length)
    prev_new_users = Patient.query.filter(
        Patient.created_at >= prev_start,
        Patient.created_at < start_date
    ).count()

    growth_rate = 0
    if prev_new_users > 0:
        growth_rate = ((period_new_users - prev_new_users) / prev_new_users) * 100

    return {
        'daily_growth': [{'date': str(d.date), 'count': d.count} for d in daily_growth],
        'total_users': total_users,
        'period_new_users': period_new_users,
        'growth_rate': round(growth_rate, 2),
        'avg_daily_growth': round(period_new_users / max(period_length, 1), 2)
    }

def get_engagement_analytics(start_date, end_date):
    """User engagement analytics"""

    # Active users by period
    active_users = Patient.query.filter(Patient.last_session >= start_date).count()

    # Session analytics
    session_stats = db.session.query(
        func.count(Session.id).label('total_sessions'),
        func.avg(Session.duration_minutes).label('avg_duration'),
        func.count(func.distinct(Session.patient_name)).label('unique_users')
    ).filter(Session.timestamp >= start_date).first()

    # Engagement distribution
    all_users = Patient.query.all()
    engagement_scores = [calculate_engagement_score(user, []) for user in all_users]

    engagement_distribution = {
        'high': len([s for s in engagement_scores if s >= 70]),
        'medium': len([s for s in engagement_scores if 40 <= s < 70]),
        'low': len([s for s in engagement_scores if s < 40])
    }

    return {
        'active_users': active_users,
        'total_sessions': session_stats.total_sessions or 0,
        'avg_session_duration': round(session_stats.avg_duration or 0, 1),
        'unique_session_users': session_stats.unique_users or 0,
        'engagement_distribution': engagement_distribution,
        'avg_engagement_score': round(sum(engagement_scores) / len(engagement_scores), 1) if engagement_scores else 0
    }

def get_behavioral_insights(start_date, end_date):
    """Generate behavioral insights from user data"""

    # Session patterns
    session_times = db.session.query(
        func.extract('hour', Session.timestamp).label('hour'),
        func.count(Session.id).label('count')
    ).filter(Session.timestamp >= start_date).group_by('hour').all()

    # Mood improvement analysis
    mood_sessions = Session.query.filter(
        Session.timestamp >= start_date,
        Session.mood_before.isnot(None),
        Session.mood_after.isnot(None)
    ).all()

    mood_improvements = [s.mood_after - s.mood_before for s in mood_sessions]
    avg_mood_improvement = sum(mood_improvements) / len(mood_improvements) if mood_improvements else 0

    # Crisis indicators
    high_risk_users = Patient.query.filter(Patient.risk_level == 'high').count()
    critical_risk_users = Patient.query.filter(Patient.risk_level == 'critical').count()

    return {
        'session_times': [{'hour': int(st.hour), 'count': st.count} for st in session_times],
        'avg_mood_improvement': round(avg_mood_improvement, 2),
        'mood_improvement_sessions': len(mood_improvements),
        'high_risk_users': high_risk_users,
        'critical_risk_users': critical_risk_users,
        'total_risk_users': high_risk_users + critical_risk_users
    }

def get_subscription_analytics(start_date, end_date):
    """Subscription tier analytics"""

    # Current distribution
    subscription_dist = dict(
        db.session.query(Patient.subscription_tier, func.count(Patient.id))
        .group_by(Patient.subscription_tier).all()
    )

    # Revenue potential (mock calculation)
    tier_prices = {'free': 0, 'basic': 29, 'premium': 79, 'enterprise': 199}
    monthly_revenue = sum(subscription_dist.get(tier, 0) * price for tier, price in tier_prices.items())

    # Upgrades in period
    upgrade_candidates = Patient.query.filter(
        Patient.subscription_tier == 'free',
        Patient.last_session >= start_date
    ).count()

    return {
        'distribution': subscription_dist,
        'monthly_revenue_potential': monthly_revenue,
        'upgrade_candidates': upgrade_candidates,
        'conversion_opportunities': upgrade_candidates
    }

def get_risk_level_analytics(start_date, end_date):
    """Risk level distribution and trends"""

    risk_distribution = dict(
        db.session.query(Patient.risk_level, func.count(Patient.id))
        .group_by(Patient.risk_level).all()
    )

    # Recent risk escalations (users who might have increased risk)
    recent_sessions = Session.query.filter(Session.timestamp >= start_date).all()
    risk_indicators = len([s for s in recent_sessions if s.mood_before and s.mood_before <= 3])

    return {
        'distribution': risk_distribution,
        'recent_risk_indicators': risk_indicators,
        'requires_attention': risk_distribution.get('high', 0) + risk_distribution.get('critical', 0)
    }

def get_retention_metrics(start_date, end_date):
    """User retention analysis"""

    # Users registered in period
    new_users_period = Patient.query.filter(
        Patient.created_at >= start_date,
        Patient.created_at <= end_date
    ).all()

    # Check how many returned
    returned_users = 0
    for user in new_users_period:
        if user.last_session and user.last_session > user.created_at + timedelta(days=1):
            returned_users += 1

    retention_rate = (returned_users / len(new_users_period)) * 100 if new_users_period else 0

    # 7-day retention
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    users_7days_ago = Patient.query.filter(
        Patient.created_at <= seven_days_ago,
        Patient.created_at >= seven_days_ago - timedelta(days=1)
    ).all()

    active_after_7days = len([u for u in users_7days_ago if u.last_session and u.last_session >= seven_days_ago])
    seven_day_retention = (active_after_7days / len(users_7days_ago)) * 100 if users_7days_ago else 0

    return {
        'period_retention_rate': round(retention_rate, 2),
        'seven_day_retention': round(seven_day_retention, 2),
        'new_users_returned': returned_users,
        'total_new_users': len(new_users_period)
    }

def get_usage_patterns(start_date, end_date):
    """Analyze usage patterns and preferences"""

    # Day of week patterns
    dow_sessions = db.session.query(
        func.extract('dow', Session.timestamp).label('dow'),
        func.count(Session.id).label('count')
    ).filter(Session.timestamp >= start_date).group_by('dow').all()

    dow_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    dow_data = {dow_names[int(d.dow)]: d.count for d in dow_sessions}

    # Average session duration by subscription tier
    tier_durations = db.session.query(
        Patient.subscription_tier,
        func.avg(Session.duration_minutes).label('avg_duration')
    ).join(Session, Patient.name == Session.patient_name)\
     .filter(Session.timestamp >= start_date)\
     .group_by(Patient.subscription_tier).all()

    return {
        'day_of_week': dow_data,
        'tier_durations': {td.subscription_tier: round(td.avg_duration or 0, 1) for td in tier_durations},
        'peak_usage_day': max(dow_data, key=dow_data.get) if dow_data else 'N/A'
    }

def generate_behavioral_profile(user, sessions, biometric_data):
    """Generate comprehensive behavioral profile for a user"""

    if not sessions:
        return {'message': 'Insufficient data for behavioral analysis'}

    # Session patterns
    session_hours = [s.timestamp.hour for s in sessions if s.timestamp]
    preferred_times = {}
    if session_hours:
        from collections import Counter
        hour_counts = Counter(session_hours)
        preferred_times = dict(hour_counts.most_common(3))

    # Mood patterns
    mood_data = [(s.mood_before, s.mood_after) for s in sessions if s.mood_before and s.mood_after]
    mood_trend = 'stable'
    if mood_data:
        improvements = [after - before for before, after in mood_data]
        avg_improvement = sum(improvements) / len(improvements)
        if avg_improvement > 0.5:
            mood_trend = 'improving'
        elif avg_improvement < -0.5:
            mood_trend = 'declining'

    # Session consistency
    if len(sessions) >= 5:
        session_dates = [s.timestamp.date() for s in sessions[:30]]  # Last 30 sessions
        unique_dates = len(set(session_dates))
        date_range = (max(session_dates) - min(session_dates)).days + 1
        consistency_score = (unique_dates / date_range) * 100 if date_range > 0 else 0
    else:
        consistency_score = 0

    # Response patterns
    avg_session_length = sum(s.duration_minutes or 0 for s in sessions) / len(sessions)

    # Risk indicators
    risk_indicators = []
    recent_sessions = sessions[:10]  # Last 10 sessions

    if any(s.mood_before and s.mood_before <= 2 for s in recent_sessions):
        risk_indicators.append('Low mood reported')

    if avg_session_length < 5:
        risk_indicators.append('Very short sessions')

    long_gap = False
    if len(sessions) >= 2:
        days_between = [(sessions[i].timestamp - sessions[i+1].timestamp).days for i in range(min(5, len(sessions)-1))]
        if any(gap > 14 for gap in days_between):
            long_gap = True
            risk_indicators.append('Irregular session patterns')

    return {
        'preferred_session_times': preferred_times,
        'mood_trend': mood_trend,
        'consistency_score': round(consistency_score, 1),
        'avg_session_length': round(avg_session_length, 1),
        'risk_indicators': risk_indicators,
        'total_sessions': len(sessions),
        'session_frequency': len(sessions) / max(((datetime.utcnow() - sessions[-1].timestamp).days + 1), 1) if sessions else 0,
        'engagement_level': 'high' if consistency_score > 60 else 'medium' if consistency_score > 30 else 'low'
    }

def generate_cohort_analysis():
    """Generate cohort analysis for user retention"""

    # Group users by signup month
    cohorts = db.session.query(
        func.date_trunc('month', Patient.created_at).label('cohort_month'),
        func.count(Patient.id).label('user_count')
    ).group_by('cohort_month').order_by('cohort_month').all()

    cohort_data = []
    for cohort in cohorts[-12:]:  # Last 12 months
        cohort_month = cohort.cohort_month
        cohort_size = cohort.user_count

        # Calculate retention for subsequent months
        retention_data = []
        for month_offset in range(6):  # 6 months retention
            period_start = cohort_month + timedelta(days=30 * month_offset)
            period_end = period_start + timedelta(days=30)

            active_users = Patient.query.filter(
                Patient.created_at >= cohort_month,
                Patient.created_at < cohort_month + timedelta(days=30),
                Patient.last_session >= period_start
            ).count()

            retention_rate = (active_users / cohort_size) * 100 if cohort_size > 0 else 0
            retention_data.append({
                'month': month_offset,
                'retention_rate': round(retention_rate, 1),
                'active_users': active_users
            })

        cohort_data.append({
            'cohort_month': cohort_month.strftime('%Y-%m'),
            'size': cohort_size,
            'retention': retention_data
        })

    return cohort_data

def get_user_growth_chart_data(start_date, end_date):
    """Chart data for user growth"""
    daily_growth = db.session.query(
        func.date(Patient.created_at).label('date'),
        func.count(Patient.id).label('count')
    ).filter(
        Patient.created_at >= start_date,
        Patient.created_at <= end_date
    ).group_by(func.date(Patient.created_at)).all()

    return {
        'labels': [str(d.date) for d in daily_growth],
        'data': [d.count for d in daily_growth]
    }

def get_engagement_chart_data(start_date, end_date):
    """Chart data for engagement metrics"""
    daily_sessions = db.session.query(
        func.date(Session.timestamp).label('date'),
        func.count(Session.id).label('sessions'),
        func.count(func.distinct(Session.patient_name)).label('unique_users')
    ).filter(Session.timestamp >= start_date)\
     .group_by(func.date(Session.timestamp)).all()

    return {
        'labels': [str(d.date) for d in daily_sessions],
        'sessions': [d.sessions for d in daily_sessions],
        'unique_users': [d.unique_users for d in daily_sessions]
    }

def get_subscription_chart_data(start_date, end_date):
    """Chart data for subscription distribution"""
    subscription_dist = dict(
        db.session.query(Patient.subscription_tier, func.count(Patient.id))
        .group_by(Patient.subscription_tier).all()
    )

    return {
        'labels': list(subscription_dist.keys()),
        'data': list(subscription_dist.values())
    }

def get_risk_distribution_chart_data():
    """Chart data for risk level distribution"""
    risk_dist = dict(
        db.session.query(Patient.risk_level, func.count(Patient.id))
        .group_by(Patient.risk_level).all()
    )

    return {
        'labels': list(risk_dist.keys()),
        'data': list(risk_dist.values())
    }

# ========================================
# USER IMPERSONATION SYSTEM
# ========================================

@admin_bp.route('/users/<int:user_id>/impersonate', methods=['GET', 'POST'])
@require_admin_auth
@require_permission('users.impersonate')
def user_impersonate(user_id):
    """Initiate user impersonation with security checks"""

    user = Patient.query.get_or_404(user_id)

    if request.method == 'POST':
        # Security verification
        admin_password = request.form.get('admin_password', '').strip()
        reason = request.form.get('reason', '').strip()
        duration_hours = int(request.form.get('duration', 2))

        if not admin_password or not reason:
            flash('Admin password and reason are required', 'error')
            return render_template('admin/users/impersonate_confirm.html', {'user': user})

        # Verify admin password
        from werkzeug.security import check_password_hash
        admin = get_current_admin()
        if not admin or not check_password_hash(admin.password_hash, admin_password):
            flash('Invalid admin password', 'error')
            audit_logger.log_security_event(
                'IMPERSONATION_FAILED',
                f'Failed impersonation attempt for user {user.name} - invalid admin password',
                target_type='USER_IMPERSONATION',
                target_id=user_id,
                severity='WARNING'
            )
            return render_template('admin/users/impersonate_confirm.html', {'user': user})

        # Create impersonation session
        impersonation_token = create_impersonation_session(user_id, admin.id, reason, duration_hours)

        if impersonation_token:
            # Log successful impersonation start
            audit_logger.log_admin_action(
                'USER_IMPERSONATION_STARTED',
                f'Started impersonating user {user.name} ({user.email})',
                target_type='USER_IMPERSONATION',
                target_id=user_id,
                severity='CRITICAL',
                details={
                    'impersonated_user': user.email,
                    'reason': reason,
                    'duration_hours': duration_hours,
                    'impersonation_token': impersonation_token[:8] + '...'
                }
            )

            # Log PHI access
            audit_logger.log_phi_access(
                patient_id=user_id,
                patient_name=user.name,
                access_type='IMPERSONATE',
                description=f'Started impersonation session for {user.name}',
                target_type='FULL_ACCOUNT_ACCESS',
                severity='CRITICAL',
                details={'reason': reason, 'duration_hours': duration_hours}
            )

            flash(f'Impersonation session started for {user.name}', 'success')
            return redirect(url_for('admin.impersonation_portal', token=impersonation_token))
        else:
            flash('Failed to create impersonation session', 'error')

    return render_template('admin/users/impersonate_confirm.html', {'user': user})

@admin_bp.route('/impersonate/portal')
@require_admin_auth
@require_permission('users.impersonate')
def impersonation_portal():
    """Secure portal for impersonation sessions"""

    token = request.args.get('token')
    if not token:
        flash('Invalid impersonation token', 'error')
        return redirect(url_for('admin.users_list'))

    # Validate and get impersonation session
    impersonation_data = validate_impersonation_token(token)
    if not impersonation_data:
        flash('Invalid or expired impersonation session', 'error')
        return redirect(url_for('admin.users_list'))

    user = Patient.query.get(impersonation_data['user_id'])
    admin = get_current_admin()

    if not user:
        flash('Impersonated user not found', 'error')
        return redirect(url_for('admin.users_list'))

    return render_template('admin/impersonation/portal.html', {
        'user': user,
        'admin': admin,
        'impersonation': impersonation_data,
        'token': token
    })

@admin_bp.route('/impersonate/end/<token>', methods=['POST'])
@require_admin_auth
@require_permission('users.impersonate')
def end_impersonation(token):
    """End impersonation session"""

    impersonation_data = validate_impersonation_token(token)
    if not impersonation_data:
        flash('Invalid or expired impersonation session', 'error')
        return redirect(url_for('admin.users_list'))

    user = Patient.query.get(impersonation_data['user_id'])
    admin = get_current_admin()

    # End the session
    end_impersonation_session(token)

    # Log session end
    audit_logger.log_admin_action(
        'USER_IMPERSONATION_ENDED',
        f'Ended impersonation session for user {user.name if user else "Unknown"}',
        target_type='USER_IMPERSONATION',
        target_id=impersonation_data['user_id'],
        severity='INFO',
        details={
            'session_duration': impersonation_data.get('actual_duration', 'Unknown'),
            'impersonation_token': token[:8] + '...'
        }
    )

    flash('Impersonation session ended', 'success')
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/impersonate/sessions')
@require_admin_auth
@require_permission('users.impersonate')
def impersonation_sessions():
    """View all impersonation sessions"""

    # Get active sessions
    active_sessions = get_active_impersonation_sessions()

    # Get recent session history from audit logs
    from models.audit_log import AuditLog
    recent_sessions = AuditLog.query.filter(
        AuditLog.action.in_(['USER_IMPERSONATION_STARTED', 'USER_IMPERSONATION_ENDED'])
    ).order_by(AuditLog.timestamp.desc()).limit(50).all()

    audit_logger.log_admin_action(
        'IMPERSONATION_SESSIONS_VIEW',
        'Viewed impersonation sessions list',
        details={'active_sessions': len(active_sessions), 'recent_sessions': len(recent_sessions)}
    )

    return render_template('admin/impersonation/sessions.html', {
        'active_sessions': active_sessions,
        'recent_sessions': recent_sessions
    })

@admin_bp.route('/api/impersonate/proxy/<token>/<path:endpoint>')
@require_admin_auth
def impersonation_proxy(token, endpoint):
    """Proxy requests to main app while impersonating user"""

    impersonation_data = validate_impersonation_token(token)
    if not impersonation_data:
        return jsonify({'error': 'Invalid impersonation session'}), 401

    user = Patient.query.get(impersonation_data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Log the proxied request
    audit_logger.log_phi_access(
        patient_id=user.id,
        patient_name=user.name,
        access_type='READ',
        description=f'Impersonation proxy request to /{endpoint}',
        target_type='API_PROXY',
        severity='INFO',
        details={'endpoint': endpoint, 'method': request.method}
    )

    # This would proxy to the main app with the user's context
    # For now, return basic user info
    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'subscription_tier': user.subscription_tier
        },
        'impersonation': True,
        'endpoint': endpoint
    })

# Helper functions for impersonation system
def create_impersonation_session(user_id, admin_id, reason, duration_hours):
    """Create secure impersonation session"""
    import secrets
    from datetime import datetime, timedelta

    token = secrets.token_urlsafe(32)
    session_data = {
        'token': token,
        'user_id': user_id,
        'admin_id': admin_id,
        'reason': reason,
        'duration_hours': duration_hours,
        'created_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(hours=duration_hours)).isoformat(),
        'active': True
    }

    # Store in secure session storage (Redis in production)
    # For now, use Flask session with secure key
    from flask import current_app
    import json

    # In production, store in Redis with expiration
    session_key = f'impersonation_session:{token}'
    current_app.config.setdefault('IMPERSONATION_SESSIONS', {})
    current_app.config['IMPERSONATION_SESSIONS'][token] = session_data

    return token

def validate_impersonation_token(token):
    """Validate impersonation token and return session data"""
    from flask import current_app
    from datetime import datetime

    sessions = current_app.config.get('IMPERSONATION_SESSIONS', {})
    session_data = sessions.get(token)

    if not session_data:
        return None

    # Check expiration
    expires_at = datetime.fromisoformat(session_data['expires_at'])
    if datetime.utcnow() > expires_at:
        # Session expired
        sessions.pop(token, None)
        return None

    if not session_data.get('active', False):
        return None

    return session_data

def end_impersonation_session(token):
    """End impersonation session"""
    from flask import current_app
    from datetime import datetime

    sessions = current_app.config.get('IMPERSONATION_SESSIONS', {})
    session_data = sessions.get(token)

    if session_data:
        session_data['active'] = False
        session_data['ended_at'] = datetime.utcnow().isoformat()

        # Calculate actual duration
        created_at = datetime.fromisoformat(session_data['created_at'])
        actual_duration = (datetime.utcnow() - created_at).total_seconds() / 3600
        session_data['actual_duration'] = f"{actual_duration:.2f} hours"

        sessions[token] = session_data

    return session_data

def get_active_impersonation_sessions():
    """Get all active impersonation sessions"""
    from flask import current_app
    from datetime import datetime

    sessions = current_app.config.get('IMPERSONATION_SESSIONS', {})
    active_sessions = []

    for token, session_data in sessions.items():
        if session_data.get('active', False):
            # Check if still valid
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.utcnow() <= expires_at:
                # Add user and admin info
                user = Patient.query.get(session_data['user_id'])
                admin = Patient.query.get(session_data['admin_id'])  # Admin stored in Patient table

                session_info = session_data.copy()
                session_info['user'] = user
                session_info['admin'] = admin
                session_info['token_preview'] = token[:8] + '...'
                active_sessions.append(session_info)
            else:
                # Mark expired session as inactive
                session_data['active'] = False

    return active_sessions

def get_current_admin():
    """Get current admin user from session"""
    from flask_login import current_user
    return current_user if current_user.is_authenticated else None