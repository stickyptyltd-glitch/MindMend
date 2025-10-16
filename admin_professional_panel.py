"""
Enhanced Admin Panel for Professional Management
================================================
Admin tools for overseeing the professional onboarding system
"""

from flask import Blueprint, render_template_string, request, jsonify, redirect, url_for, flash, session
from models.database import (db, Professional, ProfessionalApplication, ProfessionalCredential,
                              SessionReview, ProfessionalPayment, Session, Patient, AdminAudit)
from datetime import datetime, timedelta, UTC
from sqlalchemy import func
import json

admin_professional_bp = Blueprint('admin_professional', __name__, url_prefix='/admin/professionals')


# ========================================
# ADMIN DASHBOARD OVERVIEW
# ========================================

@admin_professional_bp.route('/overview')
def overview():
    """Main admin overview of professional system"""
    # TODO: Add require_admin_auth decorator

    # Key metrics
    total_professionals = Professional.query.count()
    active_professionals = Professional.query.filter_by(is_active=True).count()
    pending_applications = ProfessionalApplication.query.filter_by(status='pending').count()
    pending_verifications = Professional.query.filter_by(verification_status='pending').count()

    # Recent activity
    recent_applications = ProfessionalApplication.query.order_by(
        ProfessionalApplication.created_at.desc()
    ).limit(5).all()

    recent_reviews = SessionReview.query.order_by(
        SessionReview.completed_at.desc()
    ).limit(10).all()

    # Compliance alerts
    expiry_threshold = datetime.now(UTC) + timedelta(days=30)
    expiring_licenses = Professional.query.filter(
        Professional.license_expiry <= expiry_threshold,
        Professional.license_expiry >= datetime.now(UTC),
        Professional.is_active == True
    ).all()

    # Revenue metrics
    current_month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_payments = db.session.query(
        func.sum(ProfessionalPayment.gross_earnings).label('gross'),
        func.sum(ProfessionalPayment.platform_fee).label('fees'),
        func.sum(ProfessionalPayment.net_earnings).label('net')
    ).filter(
        ProfessionalPayment.period_start >= current_month_start
    ).first()

    return render_template_string(ADMIN_OVERVIEW_TEMPLATE,
                                   total_professionals=total_professionals,
                                   active_professionals=active_professionals,
                                   pending_applications=pending_applications,
                                   pending_verifications=pending_verifications,
                                   recent_applications=recent_applications,
                                   recent_reviews=recent_reviews,
                                   expiring_licenses=expiring_licenses,
                                   monthly_payments=monthly_payments)


# ========================================
# SESSION REVIEW MANAGEMENT
# ========================================

@admin_professional_bp.route('/session-reviews')
def session_reviews():
    """View and manage all session reviews"""
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')

    query = SessionReview.query

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)

    reviews = query.order_by(
        SessionReview.priority.desc(),
        SessionReview.assigned_at.desc()
    ).limit(100).all()

    # Get statistics
    total_reviews = SessionReview.query.count()
    pending_reviews = SessionReview.query.filter_by(status='assigned').count()
    urgent_reviews = SessionReview.query.filter_by(status='assigned', priority='urgent').count()

    # Average review time
    avg_review_time = db.session.query(
        func.avg(SessionReview.review_duration_minutes)
    ).filter(SessionReview.status == 'completed').scalar()

    return render_template_string(SESSION_REVIEWS_TEMPLATE,
                                   reviews=reviews,
                                   status_filter=status_filter,
                                   priority_filter=priority_filter,
                                   total_reviews=total_reviews,
                                   pending_reviews=pending_reviews,
                                   urgent_reviews=urgent_reviews,
                                   avg_review_time=avg_review_time or 0)


@admin_professional_bp.route('/assign-review', methods=['POST'])
def assign_review():
    """Manually assign a session review to a professional"""
    data = request.get_json()

    try:
        review = SessionReview(
            session_id=data['session_id'],
            professional_id=data['professional_id'],
            priority=data.get('priority', 'normal'),
            review_type=data.get('review_type', 'manual_assignment'),
            status='assigned',
            assigned_at=datetime.now(UTC)
        )

        db.session.add(review)
        db.session.commit()

        # Log admin action
        audit = AdminAudit(
            admin_email=session.get('admin_email', 'system'),
            action='assign_session_review',
            details=json.dumps({
                'session_id': data['session_id'],
                'professional_id': data['professional_id'],
                'priority': data.get('priority')
            }),
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({'success': True, 'review_id': review.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ========================================
# PAYMENT MANAGEMENT
# ========================================

@admin_professional_bp.route('/payments')
def payments():
    """View and manage professional payments"""
    status_filter = request.args.get('status', 'all')

    query = ProfessionalPayment.query

    if status_filter != 'all':
        query = query.filter_by(payment_status=status_filter)

    payments = query.order_by(ProfessionalPayment.created_at.desc()).limit(100).all()

    # Calculate totals
    total_pending = db.session.query(
        func.sum(ProfessionalPayment.net_earnings)
    ).filter(ProfessionalPayment.payment_status == 'pending').scalar() or 0

    total_paid_this_month = db.session.query(
        func.sum(ProfessionalPayment.net_earnings)
    ).filter(
        ProfessionalPayment.payment_status == 'paid',
        ProfessionalPayment.paid_at >= datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0)
    ).scalar() or 0

    return render_template_string(PAYMENTS_TEMPLATE,
                                   payments=payments,
                                   status_filter=status_filter,
                                   total_pending=total_pending,
                                   total_paid_this_month=total_paid_this_month)


@admin_professional_bp.route('/generate-payments', methods=['POST'])
def generate_payments():
    """Generate payment records for the period"""
    period_start = datetime.fromisoformat(request.form.get('period_start'))
    period_end = datetime.fromisoformat(request.form.get('period_end'))

    try:
        # Get all active professionals
        professionals = Professional.query.filter_by(is_active=True).all()

        payments_created = 0

        for professional in professionals:
            # Calculate earnings for the period
            reviews = SessionReview.query.filter(
                SessionReview.professional_id == professional.id,
                SessionReview.status == 'completed',
                SessionReview.completed_at >= period_start,
                SessionReview.completed_at <= period_end
            ).all()

            if not reviews:
                continue

            # Calculate gross earnings (reviews * hourly_rate)
            # Assuming each review takes approximately 15 minutes
            total_minutes = sum([r.review_duration_minutes or 15 for r in reviews])
            gross_earnings = (total_minutes / 60) * (professional.hourly_rate or 120)

            platform_fee = gross_earnings * (professional.platform_fee_percentage / 100)
            net_earnings = gross_earnings - platform_fee

            # Create payment record
            payment = ProfessionalPayment(
                professional_id=professional.id,
                period_start=period_start,
                period_end=period_end,
                sessions_completed=0,  # Reviews only for now
                reviews_completed=len(reviews),
                gross_earnings=gross_earnings,
                platform_fee=platform_fee,
                net_earnings=net_earnings,
                payment_method=professional.payment_method,
                payment_status='pending',
                invoice_number=f"INV-{professional.id}-{period_start.strftime('%Y%m')}"
            )

            db.session.add(payment)
            payments_created += 1

        db.session.commit()

        # Log admin action
        audit = AdminAudit(
            admin_email=session.get('admin_email', 'system'),
            action='generate_professional_payments',
            details=json.dumps({
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'payments_created': payments_created
            }),
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()

        flash(f'Generated {payments_created} payment records', 'success')
        return redirect(url_for('admin_professional.payments'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error generating payments: {str(e)}', 'error')
        return redirect(url_for('admin_professional.payments'))


@admin_professional_bp.route('/process-payment/<int:payment_id>', methods=['POST'])
def process_payment(payment_id):
    """Mark a payment as processed"""
    payment = ProfessionalPayment.query.get_or_404(payment_id)

    try:
        payment.payment_status = 'paid'
        payment.paid_at = datetime.now(UTC)
        payment.stripe_transfer_id = request.form.get('stripe_transfer_id')

        db.session.commit()

        # Log admin action
        audit = AdminAudit(
            admin_email=session.get('admin_email', 'system'),
            action='process_professional_payment',
            details=json.dumps({
                'payment_id': payment_id,
                'professional_id': payment.professional_id,
                'amount': payment.net_earnings
            }),
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()

        flash(f'Payment processed successfully', 'success')
        return redirect(url_for('admin_professional.payments'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing payment: {str(e)}', 'error')
        return redirect(url_for('admin_professional.payments'))


# ========================================
# ANALYTICS & REPORTING
# ========================================

@admin_professional_bp.route('/analytics')
def analytics():
    """Professional system analytics"""

    # Professional performance metrics
    top_performers = db.session.query(
        Professional,
        func.count(SessionReview.id).label('review_count'),
        func.avg(SessionReview.ai_quality_score).label('avg_quality_score')
    ).join(
        SessionReview, Professional.id == SessionReview.professional_id
    ).filter(
        SessionReview.completed_at >= datetime.now(UTC) - timedelta(days=30)
    ).group_by(
        Professional.id
    ).order_by(
        func.count(SessionReview.id).desc()
    ).limit(10).all()

    # Session review trends (last 30 days)
    review_trends = db.session.query(
        func.date(SessionReview.completed_at).label('date'),
        func.count(SessionReview.id).label('count')
    ).filter(
        SessionReview.completed_at >= datetime.now(UTC) - timedelta(days=30),
        SessionReview.status == 'completed'
    ).group_by(
        func.date(SessionReview.completed_at)
    ).all()

    # Quality metrics
    quality_distribution = db.session.query(
        SessionReview.ai_quality_score,
        func.count(SessionReview.id).label('count')
    ).filter(
        SessionReview.completed_at >= datetime.now(UTC) - timedelta(days=30)
    ).group_by(
        SessionReview.ai_quality_score
    ).all()

    # Risk level distribution
    risk_distribution = db.session.query(
        SessionReview.risk_level,
        func.count(SessionReview.id).label('count')
    ).group_by(
        SessionReview.risk_level
    ).all()

    return render_template_string(ANALYTICS_TEMPLATE,
                                   top_performers=top_performers,
                                   review_trends=review_trends,
                                   quality_distribution=quality_distribution,
                                   risk_distribution=risk_distribution)


@admin_professional_bp.route('/export-report', methods=['POST'])
def export_report():
    """Export professional system report"""
    report_type = request.form.get('report_type')
    start_date = datetime.fromisoformat(request.form.get('start_date'))
    end_date = datetime.fromisoformat(request.form.get('end_date'))

    # TODO: Implement CSV/PDF export functionality
    # For now, return JSON data

    if report_type == 'performance':
        data = db.session.query(
            Professional.name,
            Professional.email,
            func.count(SessionReview.id).label('reviews'),
            func.avg(SessionReview.ai_quality_score).label('avg_score')
        ).join(
            SessionReview, Professional.id == SessionReview.professional_id
        ).filter(
            SessionReview.completed_at >= start_date,
            SessionReview.completed_at <= end_date
        ).group_by(
            Professional.id
        ).all()

        return jsonify({
            'success': True,
            'report_type': 'performance',
            'data': [{
                'name': d[0],
                'email': d[1],
                'reviews': d[2],
                'avg_score': float(d[3] or 0)
            } for d in data]
        })

    elif report_type == 'payments':
        payments = ProfessionalPayment.query.filter(
            ProfessionalPayment.period_start >= start_date,
            ProfessionalPayment.period_end <= end_date
        ).all()

        return jsonify({
            'success': True,
            'report_type': 'payments',
            'data': [{
                'professional_id': p.professional_id,
                'period': f"{p.period_start.date()} - {p.period_end.date()}",
                'gross': p.gross_earnings,
                'platform_fee': p.platform_fee,
                'net': p.net_earnings,
                'status': p.payment_status
            } for p in payments]
        })

    return jsonify({'success': False, 'error': 'Invalid report type'}), 400


# ========================================
# BULK OPERATIONS
# ========================================

@admin_professional_bp.route('/bulk-verify', methods=['POST'])
def bulk_verify():
    """Bulk verify multiple professionals"""
    professional_ids = request.form.getlist('professional_ids')

    try:
        count = 0
        for prof_id in professional_ids:
            professional = Professional.query.get(prof_id)
            if professional and professional.verification_status == 'pending':
                professional.verification_status = 'verified'
                professional.verified_at = datetime.now(UTC)
                professional.verified_by = session.get('admin_email', 'admin')
                professional.is_active = True
                count += 1

        db.session.commit()

        # Log admin action
        audit = AdminAudit(
            admin_email=session.get('admin_email', 'system'),
            action='bulk_verify_professionals',
            details=json.dumps({'count': count, 'ids': professional_ids}),
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()

        flash(f'Successfully verified {count} professionals', 'success')
        return redirect(url_for('admin_professional.overview'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error during bulk verification: {str(e)}', 'error')
        return redirect(url_for('admin_professional.overview'))


@admin_professional_bp.route('/bulk-send-reminders', methods=['POST'])
def bulk_send_reminders():
    """Send reminders to professionals with expiring credentials"""
    reminder_type = request.form.get('reminder_type')

    try:
        expiry_threshold = datetime.now(UTC) + timedelta(days=30)
        professionals = []

        if reminder_type == 'license':
            professionals = Professional.query.filter(
                Professional.license_expiry <= expiry_threshold,
                Professional.license_expiry >= datetime.now(UTC),
                Professional.is_active == True
            ).all()

        elif reminder_type == 'insurance':
            professionals = Professional.query.filter(
                Professional.insurance_expiry <= expiry_threshold,
                Professional.insurance_expiry >= datetime.now(UTC),
                Professional.is_active == True
            ).all()

        # TODO: Implement email sending
        # For now, just count

        flash(f'Reminder emails sent to {len(professionals)} professionals', 'success')

        # Log admin action
        audit = AdminAudit(
            admin_email=session.get('admin_email', 'system'),
            action='bulk_send_reminders',
            details=json.dumps({'reminder_type': reminder_type, 'count': len(professionals)}),
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()

        return redirect(url_for('professional_mgmt.admin_compliance_dashboard'))

    except Exception as e:
        flash(f'Error sending reminders: {str(e)}', 'error')
        return redirect(url_for('professional_mgmt.admin_compliance_dashboard'))


# ========================================
# TEMPLATES
# ========================================

ADMIN_OVERVIEW_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Professional Management Overview - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f6fa; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .container { max-width: 1400px; margin: 30px auto; padding: 0 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { margin: 0 0 10px 0; color: #7f8c8d; font-size: 14px; text-transform: uppercase; }
        .stat-card .value { font-size: 36px; font-weight: bold; color: #2c3e50; }
        .stat-card .subtext { color: #95a5a6; font-size: 12px; margin-top: 5px; }
        .section { background: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }
        th { background: #f8f9fa; font-weight: 600; color: #2c3e50; }
        .alert-box { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 20px; }
        .nav-links { margin-bottom: 20px; }
        .nav-links a { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }
        .nav-links a:hover { background: #2980b9; }
        .status-pending { color: #f39c12; font-weight: bold; }
        .status-approved { color: #27ae60; font-weight: bold; }
        .priority-urgent { color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Professional Management System</h1>
        <p>Admin Control Panel</p>
    </div>

    <div class="container">
        <div class="nav-links">
            <a href="{{ url_for('admin_professional.overview') }}">Overview</a>
            <a href="{{ url_for('professional_mgmt.admin_applications') }}">Applications</a>
            <a href="{{ url_for('professional_mgmt.admin_professionals') }}">Professionals</a>
            <a href="{{ url_for('admin_professional.session_reviews') }}">Session Reviews</a>
            <a href="{{ url_for('admin_professional.payments') }}">Payments</a>
            <a href="{{ url_for('admin_professional.analytics') }}">Analytics</a>
            <a href="{{ url_for('professional_mgmt.admin_compliance_dashboard') }}">Compliance</a>
        </div>

        {% if expiring_licenses %}
        <div class="alert-box">
            <strong>Warning:</strong> {{ expiring_licenses|length }} professional license(s) expiring within 30 days!
            <a href="{{ url_for('professional_mgmt.admin_compliance_dashboard') }}">View Details</a>
        </div>
        {% endif %}

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Professionals</h3>
                <div class="value">{{ total_professionals }}</div>
                <div class="subtext">{{ active_professionals }} active</div>
            </div>
            <div class="stat-card">
                <h3>Pending Applications</h3>
                <div class="value">{{ pending_applications }}</div>
                <div class="subtext">Awaiting review</div>
            </div>
            <div class="stat-card">
                <h3>Pending Verifications</h3>
                <div class="value">{{ pending_verifications }}</div>
                <div class="subtext">Credentials to verify</div>
            </div>
            <div class="stat-card">
                <h3>Monthly Revenue</h3>
                <div class="value">${{ "%.0f"|format(monthly_payments.fees or 0) }}</div>
                <div class="subtext">Platform fees this month</div>
            </div>
        </div>

        <div class="section">
            <h2>Recent Applications</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>License Type</th>
                        <th>Applied</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for app in recent_applications %}
                    <tr>
                        <td>{{ app.name }}</td>
                        <td>{{ app.email }}</td>
                        <td>{{ app.license_type }}</td>
                        <td>{{ app.created_at.strftime('%Y-%m-%d') }}</td>
                        <td class="status-{{ app.status }}">{{ app.status }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>Recent Session Reviews</h2>
            <table>
                <thead>
                    <tr>
                        <th>Review ID</th>
                        <th>Session</th>
                        <th>Professional</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Completed</th>
                    </tr>
                </thead>
                <tbody>
                    {% for review in recent_reviews %}
                    <tr>
                        <td>#{{ review.id }}</td>
                        <td>Session #{{ review.session_id }}</td>
                        <td>{{ review.professional.name if review.professional else 'N/A' }}</td>
                        <td class="priority-{{ review.priority }}">{{ review.priority }}</td>
                        <td>{{ review.status }}</td>
                        <td>{{ review.completed_at.strftime('%Y-%m-%d %H:%M') if review.completed_at else '-' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

SESSION_REVIEWS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Session Reviews Management - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .filters { margin-bottom: 20px; display: flex; gap: 15px; }
        .filters select { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .stats-bar { display: flex; gap: 20px; margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
        .stat-item { flex: 1; text-align: center; }
        .stat-item .label { color: #7f8c8d; font-size: 12px; }
        .stat-item .value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #34495e; color: white; }
        .priority-urgent { background: #e74c3c; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px; }
        .priority-high { background: #e67e22; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px; }
        .priority-normal { background: #3498db; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px; }
    </style>
</head>
<body>
    <h1>Session Reviews Management</h1>

    <div class="stats-bar">
        <div class="stat-item">
            <div class="label">Total Reviews</div>
            <div class="value">{{ total_reviews }}</div>
        </div>
        <div class="stat-item">
            <div class="label">Pending</div>
            <div class="value">{{ pending_reviews }}</div>
        </div>
        <div class="stat-item">
            <div class="label">Urgent</div>
            <div class="value">{{ urgent_reviews }}</div>
        </div>
        <div class="stat-item">
            <div class="label">Avg Review Time</div>
            <div class="value">{{ "%.0f"|format(avg_review_time) }}m</div>
        </div>
    </div>

    <div class="filters">
        <form method="GET">
            <select name="status" onchange="this.form.submit()">
                <option value="all" {{ 'selected' if status_filter == 'all' }}>All Statuses</option>
                <option value="assigned" {{ 'selected' if status_filter == 'assigned' }}>Assigned</option>
                <option value="in_progress" {{ 'selected' if status_filter == 'in_progress' }}>In Progress</option>
                <option value="completed" {{ 'selected' if status_filter == 'completed' }}>Completed</option>
            </select>
            <select name="priority" onchange="this.form.submit()">
                <option value="all" {{ 'selected' if priority_filter == 'all' }}>All Priorities</option>
                <option value="urgent" {{ 'selected' if priority_filter == 'urgent' }}>Urgent</option>
                <option value="high" {{ 'selected' if priority_filter == 'high' }}>High</option>
                <option value="normal" {{ 'selected' if priority_filter == 'normal' }}>Normal</option>
            </select>
        </form>
    </div>

    <table>
        <thead>
            <tr>
                <th>Review ID</th>
                <th>Session ID</th>
                <th>Professional</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Risk Level</th>
                <th>Quality Score</th>
                <th>Assigned</th>
                <th>Completed</th>
            </tr>
        </thead>
        <tbody>
            {% for review in reviews %}
            <tr>
                <td>#{{ review.id }}</td>
                <td>#{{ review.session_id }}</td>
                <td>{{ review.professional.name if review.professional else 'Unassigned' }}</td>
                <td><span class="priority-{{ review.priority }}">{{ review.priority|upper }}</span></td>
                <td>{{ review.status }}</td>
                <td>{{ review.risk_level or '-' }}</td>
                <td>{{ review.ai_quality_score or '-' }}</td>
                <td>{{ review.assigned_at.strftime('%Y-%m-%d %H:%M') if review.assigned_at else '-' }}</td>
                <td>{{ review.completed_at.strftime('%Y-%m-%d %H:%M') if review.completed_at else '-' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

PAYMENTS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Professional Payments - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { display: flex; gap: 20px; margin-bottom: 30px; }
        .summary-card { flex: 1; background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .summary-card .label { color: #7f8c8d; font-size: 14px; }
        .summary-card .amount { font-size: 32px; font-weight: bold; color: #2c3e50; }
        .actions { margin-bottom: 20px; }
        .actions button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #34495e; color: white; }
        .status-pending { color: #f39c12; font-weight: bold; }
        .status-paid { color: #27ae60; font-weight: bold; }
        .process-btn { background: #27ae60; color: white; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Professional Payments</h1>

    <div class="summary">
        <div class="summary-card">
            <div class="label">Pending Payments</div>
            <div class="amount">${{ "%.2f"|format(total_pending) }}</div>
        </div>
        <div class="summary-card">
            <div class="label">Paid This Month</div>
            <div class="amount">${{ "%.2f"|format(total_paid_this_month) }}</div>
        </div>
    </div>

    <div class="actions">
        <form method="POST" action="{{ url_for('admin_professional.generate_payments') }}" style="display: inline;">
            <label>Period Start:</label>
            <input type="datetime-local" name="period_start" required>
            <label>Period End:</label>
            <input type="datetime-local" name="period_end" required>
            <button type="submit">Generate Payments</button>
        </form>
    </div>

    <table>
        <thead>
            <tr>
                <th>Invoice #</th>
                <th>Professional</th>
                <th>Period</th>
                <th>Reviews</th>
                <th>Gross</th>
                <th>Platform Fee</th>
                <th>Net</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for payment in payments %}
            <tr>
                <td>{{ payment.invoice_number }}</td>
                <td>{{ payment.professional.name if payment.professional else 'N/A' }}</td>
                <td>{{ payment.period_start.strftime('%Y-%m-%d') }} - {{ payment.period_end.strftime('%Y-%m-%d') }}</td>
                <td>{{ payment.reviews_completed }}</td>
                <td>${{ "%.2f"|format(payment.gross_earnings) }}</td>
                <td>${{ "%.2f"|format(payment.platform_fee) }}</td>
                <td>${{ "%.2f"|format(payment.net_earnings) }}</td>
                <td class="status-{{ payment.payment_status }}">{{ payment.payment_status }}</td>
                <td>
                    {% if payment.payment_status == 'pending' %}
                    <form method="POST" action="{{ url_for('admin_professional.process_payment', payment_id=payment.id) }}" style="display: inline;">
                        <input type="text" name="stripe_transfer_id" placeholder="Stripe Transfer ID" size="20">
                        <button type="submit" class="process-btn">Process</button>
                    </form>
                    {% else %}
                    Paid {{ payment.paid_at.strftime('%Y-%m-%d') if payment.paid_at else '' }}
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

ANALYTICS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Professional Analytics - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { background: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }
        th { background: #f8f9fa; font-weight: 600; }
        .chart { background: #f8f9fa; padding: 20px; border-radius: 4px; margin: 15px 0; }
    </style>
</head>
<body>
    <h1>Professional System Analytics</h1>

    <div class="section">
        <h2>Top Performers (Last 30 Days)</h2>
        <table>
            <thead>
                <tr>
                    <th>Professional</th>
                    <th>License Type</th>
                    <th>Reviews Completed</th>
                    <th>Avg Quality Score</th>
                    <th>Rating</th>
                </tr>
            </thead>
            <tbody>
                {% for performer in top_performers %}
                <tr>
                    <td>{{ performer[0].name }}</td>
                    <td>{{ performer[0].license_type }}</td>
                    <td>{{ performer[1] }}</td>
                    <td>{{ "%.1f"|format(performer[2] or 0) }}/10</td>
                    <td>{{ "%.1f"|format(performer[0].average_rating) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>Review Trends (Last 30 Days)</h2>
        <div class="chart">
            {% for trend in review_trends %}
            <p>{{ trend[0] }}: {{ trend[1] }} reviews</p>
            {% endfor %}
        </div>
    </div>

    <div class="section">
        <h2>AI Quality Score Distribution</h2>
        <div class="chart">
            {% for quality in quality_distribution %}
            <p>Score {{ quality[0] }}: {{ quality[1] }} reviews</p>
            {% endfor %}
        </div>
    </div>

    <div class="section">
        <h2>Risk Level Distribution</h2>
        <div class="chart">
            {% for risk in risk_distribution %}
            <p>{{ risk[0] or 'Unknown' }}: {{ risk[1] }} cases</p>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""
