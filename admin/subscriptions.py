"""
Subscription Management Module
=============================
Comprehensive subscription, billing, and payment management for admin panel
"""
import json
from datetime import datetime, timedelta
from flask import (
    render_template, request, redirect, url_for, flash,
    jsonify, make_response
)
from sqlalchemy import func, desc, asc, or_, and_
from . import admin_bp
from .auth import require_admin_auth, require_permission
from models.database import db, Patient, Subscription, Payment
from models.audit_log import audit_logger

@admin_bp.route('/subscriptions')
@require_admin_auth
@require_permission('subscriptions.view')
def subscriptions_list():
    """Main subscription management dashboard"""

    # Get filter parameters
    tier_filter = request.args.get('tier', '')
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))

    # Base query with user information
    query = db.session.query(Subscription, Patient).join(Patient, Subscription.user_id == Patient.id)

    # Apply filters
    if tier_filter:
        query = query.filter(Subscription.tier == tier_filter)

    if status_filter:
        query = query.filter(Subscription.status == status_filter)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Patient.name.ilike(search_pattern),
                Patient.email.ilike(search_pattern),
                Subscription.stripe_subscription_id.ilike(search_pattern)
            )
        )

    # Apply sorting
    if hasattr(Subscription, sort_by):
        if sort_order == 'desc':
            query = query.order_by(desc(getattr(Subscription, sort_by)))
        else:
            query = query.order_by(asc(getattr(Subscription, sort_by)))

    # Get total count before pagination
    total_subscriptions = query.count()

    # Apply pagination
    subscriptions = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Get subscription statistics
    subscription_stats = get_subscription_statistics()

    # Log admin action
    audit_logger.log_admin_action(
        'SUBSCRIPTION_LIST_VIEW',
        f'Viewed subscription list (page {page}, {total_subscriptions} total)',
        details={
            'filters': {'tier': tier_filter, 'status': status_filter, 'search': search},
            'total_results': total_subscriptions
        }
    )

    return render_template('admin/subscriptions/list.html',
        subscriptions=subscriptions,
        subscription_stats=subscription_stats,
        current_filters={
            'tier': tier_filter,
            'status': status_filter,
            'search': search,
            'sort': sort_by,
            'order': sort_order,
            'per_page': per_page
        },
        subscription_tiers=['free', 'basic', 'premium', 'enterprise'],
        subscription_statuses=['active', 'canceled', 'past_due', 'unpaid', 'trialing'],
        total_subscriptions=total_subscriptions
    )

@admin_bp.route('/subscriptions/<int:subscription_id>')
@require_admin_auth
@require_permission('subscriptions.view')
def subscription_detail(subscription_id):
    """Detailed subscription view"""

    subscription = Subscription.query.get_or_404(subscription_id)
    user = Patient.query.get(subscription.user_id)

    # Get payment history for this subscription
    payments = Payment.query.filter_by(user_id=subscription.user_id)\
        .order_by(desc(Payment.created_at)).limit(20).all()

    # Calculate subscription metrics
    subscription_metrics = calculate_subscription_metrics(subscription, payments)

    # Get subscription timeline
    timeline = get_subscription_timeline(subscription)

    # Log access
    audit_logger.log_admin_action(
        'SUBSCRIPTION_DETAIL_VIEW',
        f'Viewed subscription details for {user.name if user else "Unknown"} (ID: {subscription_id})',
        target_type='SUBSCRIPTION',
        target_id=subscription_id,
        details={'subscription_tier': subscription.tier, 'status': subscription.status}
    )

    return render_template('admin/subscriptions/detail.html',
        subscription=subscription,
        user=user,
        payments=payments,
        metrics=subscription_metrics,
        timeline=timeline
    )

@admin_bp.route('/subscriptions/<int:subscription_id>/edit', methods=['GET', 'POST'])
@require_admin_auth
@require_permission('subscriptions.edit')
def subscription_edit(subscription_id):
    """Edit subscription details"""

    subscription = Subscription.query.get_or_404(subscription_id)
    user = Patient.query.get(subscription.user_id)

    if request.method == 'POST':
        original_data = {
            'tier': subscription.tier,
            'status': subscription.status,
            'amount': subscription.amount,
            'billing_cycle': subscription.billing_cycle
        }

        # Update subscription
        subscription.tier = request.form.get('tier', subscription.tier)
        subscription.status = request.form.get('status', subscription.status)
        subscription.amount = float(request.form.get('amount', subscription.amount or 0))
        subscription.billing_cycle = request.form.get('billing_cycle', subscription.billing_cycle)
        subscription.notes = request.form.get('notes', subscription.notes)

        # Update user's subscription tier to match
        if user:
            user.subscription_tier = subscription.tier

        try:
            db.session.commit()

            # Log changes
            changes = {}
            for key, old_value in original_data.items():
                new_value = getattr(subscription, key)
                if old_value != new_value:
                    changes[key] = {'old': old_value, 'new': new_value}

            audit_logger.log_admin_action(
                'SUBSCRIPTION_MODIFIED',
                f'Updated subscription for {user.name if user else "Unknown"}',
                target_type='SUBSCRIPTION',
                target_id=subscription_id,
                severity='WARNING',
                details={'changes': changes}
            )

            flash(f'Subscription updated successfully', 'success')
            return redirect(url_for('admin.subscription_detail', subscription_id=subscription_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating subscription: {str(e)}', 'error')

    return render_template('admin/subscriptions/edit.html',
        subscription=subscription,
        user=user
    )

@admin_bp.route('/subscriptions/<int:subscription_id>/cancel', methods=['POST'])
@require_admin_auth
@require_permission('subscriptions.cancel')
def subscription_cancel(subscription_id):
    """Cancel subscription"""

    subscription = Subscription.query.get_or_404(subscription_id)
    user = Patient.query.get(subscription.user_id)
    reason = request.form.get('reason', '').strip()

    if not reason:
        flash('Cancellation reason is required', 'error')
        return redirect(url_for('admin.subscription_detail', subscription_id=subscription_id))

    try:
        # Update subscription status
        subscription.status = 'canceled'
        subscription.canceled_at = datetime.utcnow()
        subscription.cancellation_reason = reason

        # Downgrade user to free tier
        if user:
            user.subscription_tier = 'free'

        db.session.commit()

        # Log cancellation
        audit_logger.log_admin_action(
            'SUBSCRIPTION_CANCELED',
            f'Canceled subscription for {user.name if user else "Unknown"}',
            target_type='SUBSCRIPTION',
            target_id=subscription_id,
            severity='WARNING',
            details={'reason': reason, 'tier': subscription.tier}
        )

        flash(f'Subscription canceled successfully', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error canceling subscription: {str(e)}', 'error')

    return redirect(url_for('admin.subscription_detail', subscription_id=subscription_id))

@admin_bp.route('/subscriptions/<int:subscription_id>/reactivate', methods=['POST'])
@require_admin_auth
@require_permission('subscriptions.edit')
def subscription_reactivate(subscription_id):
    """Reactivate canceled subscription"""

    subscription = Subscription.query.get_or_404(subscription_id)
    user = Patient.query.get(subscription.user_id)

    try:
        # Reactivate subscription
        subscription.status = 'active'
        subscription.canceled_at = None
        subscription.cancellation_reason = None
        subscription.reactivated_at = datetime.utcnow()

        # Update user tier
        if user:
            user.subscription_tier = subscription.tier

        db.session.commit()

        # Log reactivation
        audit_logger.log_admin_action(
            'SUBSCRIPTION_REACTIVATED',
            f'Reactivated subscription for {user.name if user else "Unknown"}',
            target_type='SUBSCRIPTION',
            target_id=subscription_id,
            severity='INFO',
            details={'tier': subscription.tier}
        )

        flash(f'Subscription reactivated successfully', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error reactivating subscription: {str(e)}', 'error')

    return redirect(url_for('admin.subscription_detail', subscription_id=subscription_id))

@admin_bp.route('/subscriptions/create', methods=['GET', 'POST'])
@require_admin_auth
@require_permission('subscriptions.create')
def subscription_create():
    """Create new subscription"""

    if request.method == 'POST':
        user_id = int(request.form.get('user_id'))
        tier = request.form.get('tier', 'basic')
        amount = float(request.form.get('amount', 0))
        billing_cycle = request.form.get('billing_cycle', 'monthly')

        user = Patient.query.get_or_404(user_id)

        # Check if user already has an active subscription
        existing_sub = Subscription.query.filter_by(user_id=user_id, status='active').first()
        if existing_sub:
            flash('User already has an active subscription', 'error')
            return render_template('admin/subscriptions/create.html')

        try:
            # Create subscription
            subscription = Subscription(
                user_id=user_id,
                tier=tier,
                status='active',
                amount=amount,
                billing_cycle=billing_cycle,
                created_at=datetime.utcnow(),
                current_period_start=datetime.utcnow(),
                current_period_end=datetime.utcnow() + timedelta(
                    days=30 if billing_cycle == 'monthly' else 365
                )
            )

            db.session.add(subscription)

            # Update user tier
            user.subscription_tier = tier

            db.session.commit()

            # Log creation
            audit_logger.log_admin_action(
                'SUBSCRIPTION_CREATED',
                f'Created {tier} subscription for {user.name}',
                target_type='SUBSCRIPTION',
                target_id=subscription.id,
                severity='INFO',
                details={'tier': tier, 'amount': amount, 'billing_cycle': billing_cycle}
            )

            flash(f'Subscription created successfully for {user.name}', 'success')
            return redirect(url_for('admin.subscription_detail', subscription_id=subscription.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating subscription: {str(e)}', 'error')

    # Get users without active subscriptions
    users_without_subs = db.session.query(Patient)\
        .outerjoin(Subscription, and_(Patient.id == Subscription.user_id, Subscription.status == 'active'))\
        .filter(Subscription.id.is_(None)).all()

    return render_template('admin/subscriptions/create.html',
        available_users=users_without_subs
    )

@admin_bp.route('/subscriptions/analytics')
@require_admin_auth
@require_permission('subscriptions.analytics')
def subscription_analytics():
    """Subscription analytics dashboard"""

    # Get time period
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

    # Get comprehensive analytics
    analytics_data = {
        'revenue_analytics': get_revenue_analytics(start_date, end_date),
        'subscription_growth': get_subscription_growth_analytics(start_date, end_date),
        'tier_distribution': get_tier_distribution_analytics(),
        'churn_analytics': get_churn_analytics(start_date, end_date),
        'payment_analytics': get_payment_analytics(start_date, end_date),
        'ltv_analytics': get_ltv_analytics()
    }

    # Log analytics access
    audit_logger.log_admin_action(
        'SUBSCRIPTION_ANALYTICS_VIEW',
        f'Viewed subscription analytics dashboard (period: {period})',
        details={'period': period}
    )

    return render_template('admin/subscriptions/analytics.html',
        analytics=analytics_data,
        period=period,
        date_range={'start': start_date, 'end': end_date}
    )

@admin_bp.route('/subscriptions/export')
@require_admin_auth
@require_permission('subscriptions.export')
def subscriptions_export():
    """Export subscription data to CSV"""

    import csv
    import io

    # Get all subscriptions with user data
    subscriptions = db.session.query(Subscription, Patient)\
        .join(Patient, Subscription.user_id == Patient.id)\
        .order_by(desc(Subscription.created_at)).all()

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow([
        'Subscription ID', 'User Name', 'User Email', 'Tier', 'Status',
        'Amount', 'Billing Cycle', 'Created Date', 'Current Period Start',
        'Current Period End', 'Canceled Date', 'Stripe ID'
    ])

    # Write subscription data
    for subscription, user in subscriptions:
        writer.writerow([
            subscription.id,
            user.name,
            user.email,
            subscription.tier,
            subscription.status,
            subscription.amount or '',
            subscription.billing_cycle or '',
            subscription.created_at.strftime('%Y-%m-%d %H:%M:%S') if subscription.created_at else '',
            subscription.current_period_start.strftime('%Y-%m-%d') if subscription.current_period_start else '',
            subscription.current_period_end.strftime('%Y-%m-%d') if subscription.current_period_end else '',
            subscription.canceled_at.strftime('%Y-%m-%d %H:%M:%S') if subscription.canceled_at else '',
            subscription.stripe_subscription_id or ''
        ])

    output.seek(0)

    # Log export
    audit_logger.log_admin_action(
        'SUBSCRIPTION_DATA_EXPORT',
        f'Exported subscription data ({len(subscriptions)} records)',
        target_type='BULK_DATA',
        severity='WARNING',
        details={'record_count': len(subscriptions)}
    )

    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=subscriptions_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

@admin_bp.route('/api/subscriptions/charts')
@require_admin_auth
@require_permission('subscriptions.analytics')
def subscription_charts_api():
    """API endpoint for subscription chart data"""

    chart_type = request.args.get('type', 'revenue')
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

    if chart_type == 'revenue':
        data = get_revenue_chart_data(start_date, end_date)
    elif chart_type == 'growth':
        data = get_subscription_growth_chart_data(start_date, end_date)
    elif chart_type == 'tier_distribution':
        data = get_tier_distribution_chart_data()
    elif chart_type == 'churn':
        data = get_churn_chart_data(start_date, end_date)
    else:
        data = {}

    return jsonify(data)

# Helper functions for subscription analytics

def get_subscription_statistics():
    """Calculate comprehensive subscription statistics"""

    stats = {
        'total_subscriptions': Subscription.query.count(),
        'active_subscriptions': Subscription.query.filter_by(status='active').count(),
        'canceled_subscriptions': Subscription.query.filter_by(status='canceled').count(),
        'tier_breakdown': dict(
            db.session.query(Subscription.tier, func.count(Subscription.id))
            .filter(Subscription.status == 'active')
            .group_by(Subscription.tier).all()
        ),
        'monthly_revenue': calculate_monthly_revenue(),
        'average_revenue_per_user': calculate_arpu()
    }

    return stats

def calculate_subscription_metrics(subscription, payments):
    """Calculate detailed metrics for a subscription"""

    total_paid = sum(p.amount for p in payments if p.status == 'succeeded')
    payment_count = len([p for p in payments if p.status == 'succeeded'])

    # Calculate subscription age
    age_days = 0
    if subscription.created_at:
        age_days = (datetime.utcnow() - subscription.created_at).days

    return {
        'total_revenue': total_paid,
        'payment_count': payment_count,
        'average_payment': total_paid / payment_count if payment_count > 0 else 0,
        'subscription_age_days': age_days,
        'next_billing_date': subscription.current_period_end,
        'days_until_renewal': (subscription.current_period_end - datetime.utcnow()).days if subscription.current_period_end else 0
    }

def get_subscription_timeline(subscription):
    """Get timeline of subscription events"""

    timeline = []

    if subscription.created_at:
        timeline.append({
            'date': subscription.created_at,
            'event': 'Subscription Created',
            'type': 'created',
            'description': f'{subscription.tier.title()} subscription started'
        })

    if subscription.canceled_at:
        timeline.append({
            'date': subscription.canceled_at,
            'event': 'Subscription Canceled',
            'type': 'canceled',
            'description': f'Reason: {subscription.cancellation_reason}'
        })

    if subscription.reactivated_at:
        timeline.append({
            'date': subscription.reactivated_at,
            'event': 'Subscription Reactivated',
            'type': 'reactivated',
            'description': 'Subscription was reactivated'
        })

    # Add payment events
    payments = Payment.query.filter_by(user_id=subscription.user_id)\
        .order_by(Payment.created_at).all()

    for payment in payments:
        timeline.append({
            'date': payment.created_at,
            'event': f'Payment {payment.status.title()}',
            'type': 'payment_success' if payment.status == 'succeeded' else 'payment_failed',
            'description': f'${payment.amount} - {payment.description or "Subscription payment"}'
        })

    return sorted(timeline, key=lambda x: x['date'], reverse=True)

def calculate_monthly_revenue():
    """Calculate current monthly recurring revenue"""

    monthly_subs = Subscription.query.filter(
        Subscription.status == 'active',
        Subscription.billing_cycle == 'monthly'
    ).all()

    yearly_subs = Subscription.query.filter(
        Subscription.status == 'active',
        Subscription.billing_cycle == 'yearly'
    ).all()

    monthly_revenue = sum(s.amount or 0 for s in monthly_subs)
    yearly_monthly_revenue = sum((s.amount or 0) / 12 for s in yearly_subs)

    return monthly_revenue + yearly_monthly_revenue

def calculate_arpu():
    """Calculate Average Revenue Per User"""

    active_subs = Subscription.query.filter_by(status='active').all()
    if not active_subs:
        return 0

    total_revenue = sum(s.amount or 0 for s in active_subs)
    return total_revenue / len(active_subs)

def get_revenue_analytics(start_date, end_date):
    """Get revenue analytics for date range"""

    # Get payments in date range
    payments = Payment.query.filter(
        Payment.created_at >= start_date,
        Payment.created_at <= end_date,
        Payment.status == 'succeeded'
    ).all()

    total_revenue = sum(p.amount for p in payments)
    payment_count = len(payments)

    # Previous period comparison
    period_length = (end_date - start_date).days
    prev_start = start_date - timedelta(days=period_length)
    prev_payments = Payment.query.filter(
        Payment.created_at >= prev_start,
        Payment.created_at < start_date,
        Payment.status == 'succeeded'
    ).all()

    prev_revenue = sum(p.amount for p in prev_payments)
    growth_rate = 0
    if prev_revenue > 0:
        growth_rate = ((total_revenue - prev_revenue) / prev_revenue) * 100

    return {
        'total_revenue': total_revenue,
        'payment_count': payment_count,
        'average_payment': total_revenue / payment_count if payment_count > 0 else 0,
        'growth_rate': round(growth_rate, 2),
        'monthly_recurring_revenue': calculate_monthly_revenue()
    }

def get_subscription_growth_analytics(start_date, end_date):
    """Get subscription growth metrics"""

    # New subscriptions in period
    new_subs = Subscription.query.filter(
        Subscription.created_at >= start_date,
        Subscription.created_at <= end_date
    ).count()

    # Cancellations in period
    cancellations = Subscription.query.filter(
        Subscription.canceled_at >= start_date,
        Subscription.canceled_at <= end_date
    ).count()

    net_growth = new_subs - cancellations

    return {
        'new_subscriptions': new_subs,
        'cancellations': cancellations,
        'net_growth': net_growth,
        'growth_rate': (net_growth / max(new_subs, 1)) * 100
    }

def get_tier_distribution_analytics():
    """Get subscription tier distribution"""

    return dict(
        db.session.query(Subscription.tier, func.count(Subscription.id))
        .filter(Subscription.status == 'active')
        .group_by(Subscription.tier).all()
    )

def get_churn_analytics(start_date, end_date):
    """Calculate churn rate and analytics"""

    # Active subscriptions at start of period
    active_start = Subscription.query.filter(
        Subscription.created_at < start_date,
        or_(Subscription.canceled_at >= start_date, Subscription.canceled_at.is_(None))
    ).count()

    # Cancellations during period
    churned = Subscription.query.filter(
        Subscription.canceled_at >= start_date,
        Subscription.canceled_at <= end_date
    ).count()

    churn_rate = (churned / max(active_start, 1)) * 100

    return {
        'churn_rate': round(churn_rate, 2),
        'churned_count': churned,
        'retention_rate': round(100 - churn_rate, 2)
    }

def get_payment_analytics(start_date, end_date):
    """Get payment success/failure analytics"""

    payments = Payment.query.filter(
        Payment.created_at >= start_date,
        Payment.created_at <= end_date
    ).all()

    successful = len([p for p in payments if p.status == 'succeeded'])
    failed = len([p for p in payments if p.status == 'failed'])
    total = len(payments)

    success_rate = (successful / max(total, 1)) * 100

    return {
        'success_rate': round(success_rate, 2),
        'successful_payments': successful,
        'failed_payments': failed,
        'total_payments': total
    }

def get_ltv_analytics():
    """Calculate customer lifetime value analytics"""

    # Simple LTV calculation based on average subscription duration and revenue
    all_subs = Subscription.query.all()
    if not all_subs:
        return {'average_ltv': 0, 'ltv_by_tier': {}}

    # Calculate average subscription duration and revenue
    ltv_data = {}
    for tier in ['free', 'basic', 'premium', 'enterprise']:
        tier_subs = [s for s in all_subs if s.tier == tier]
        if tier_subs:
            avg_duration = sum(
                (s.canceled_at or datetime.utcnow() - s.created_at).days
                for s in tier_subs if s.created_at
            ) / len(tier_subs)
            avg_revenue = sum(s.amount or 0 for s in tier_subs) / len(tier_subs)
            ltv_data[tier] = avg_revenue * (avg_duration / 30)  # Monthly LTV

    overall_ltv = sum(ltv_data.values()) / len(ltv_data) if ltv_data else 0

    return {
        'average_ltv': round(overall_ltv, 2),
        'ltv_by_tier': {k: round(v, 2) for k, v in ltv_data.items()}
    }

def get_revenue_chart_data(start_date, end_date):
    """Get daily revenue chart data"""

    daily_revenue = db.session.query(
        func.date(Payment.created_at).label('date'),
        func.sum(Payment.amount).label('revenue')
    ).filter(
        Payment.created_at >= start_date,
        Payment.created_at <= end_date,
        Payment.status == 'succeeded'
    ).group_by(func.date(Payment.created_at)).all()

    return {
        'labels': [str(d.date) for d in daily_revenue],
        'data': [float(d.revenue) for d in daily_revenue]
    }

def get_subscription_growth_chart_data(start_date, end_date):
    """Get subscription growth chart data"""

    daily_new = db.session.query(
        func.date(Subscription.created_at).label('date'),
        func.count(Subscription.id).label('new_subs')
    ).filter(
        Subscription.created_at >= start_date,
        Subscription.created_at <= end_date
    ).group_by(func.date(Subscription.created_at)).all()

    daily_churn = db.session.query(
        func.date(Subscription.canceled_at).label('date'),
        func.count(Subscription.id).label('churned')
    ).filter(
        Subscription.canceled_at >= start_date,
        Subscription.canceled_at <= end_date
    ).group_by(func.date(Subscription.canceled_at)).all()

    return {
        'new_subscriptions': {
            'labels': [str(d.date) for d in daily_new],
            'data': [d.new_subs for d in daily_new]
        },
        'churn': {
            'labels': [str(d.date) for d in daily_churn],
            'data': [d.churned for d in daily_churn]
        }
    }

def get_tier_distribution_chart_data():
    """Get tier distribution chart data"""

    tier_data = get_tier_distribution_analytics()
    return {
        'labels': list(tier_data.keys()),
        'data': list(tier_data.values())
    }

def get_churn_chart_data(start_date, end_date):
    """Get churn rate chart data"""

    # Calculate weekly churn rates
    weekly_churn = []
    current_date = start_date

    while current_date < end_date:
        week_end = min(current_date + timedelta(days=7), end_date)

        # Active subs at start of week
        active_start = Subscription.query.filter(
            Subscription.created_at < current_date,
            or_(Subscription.canceled_at >= current_date, Subscription.canceled_at.is_(None))
        ).count()

        # Churned during week
        churned = Subscription.query.filter(
            Subscription.canceled_at >= current_date,
            Subscription.canceled_at < week_end
        ).count()

        churn_rate = (churned / max(active_start, 1)) * 100

        weekly_churn.append({
            'week': current_date.strftime('%Y-%m-%d'),
            'churn_rate': round(churn_rate, 2)
        })

        current_date = week_end

    return {
        'labels': [w['week'] for w in weekly_churn],
        'data': [w['churn_rate'] for w in weekly_churn]
    }