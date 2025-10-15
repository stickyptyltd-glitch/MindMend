"""
Professional Management System
===============================
Handles professional onboarding, verification, and management
"""

from flask import Blueprint, render_template_string, request, jsonify, redirect, url_for, flash, session
from models.database import db, Professional, ProfessionalApplication, ProfessionalCredential, SessionReview, ProfessionalPayment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, UTC
import json
import uuid
from functools import wraps
import logging

# Import email utility
try:
    from email_utils import send_email
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    logging.warning("Email utilities not available - email notifications disabled")

logger = logging.getLogger(__name__)

professional_mgmt_bp = Blueprint('professional_mgmt', __name__, url_prefix='/professional')


# ========================================
# EMAIL NOTIFICATION FUNCTIONS
# ========================================

def send_application_approval_email(application):
    """Send approval email with registration link"""
    if not EMAIL_AVAILABLE:
        logger.warning(f"Email not sent to {application.email} - email not configured")
        return

    try:
        registration_url = url_for('professional_mgmt.register',
                                    application_id=application.id,
                                    _external=True)

        subject = "Your MindMend Professional Application Has Been Approved!"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">Congratulations, {application.name}!</h2>

                <p>We're excited to inform you that your application to join the MindMend professional network has been <strong>approved</strong>!</p>

                <p>You can now complete your registration and set up your professional account by clicking the link below:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{registration_url}"
                       style="background-color: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                        Complete Registration
                    </a>
                </div>

                <p>This link will allow you to:</p>
                <ul>
                    <li>Set your account password</li>
                    <li>Complete your professional profile</li>
                    <li>Upload credential verification documents</li>
                    <li>Set your availability and rates</li>
                </ul>

                <p>Once your profile is complete and credentials verified, you'll be able to start reviewing AI therapy sessions and supporting our clients.</p>

                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Complete your registration within 7 days</li>
                    <li>Submit verification documents</li>
                    <li>Await credential verification (typically 2-3 business days)</li>
                    <li>Attend onboarding orientation</li>
                    <li>Start making an impact!</li>
                </ol>

                <p>If you have any questions, please contact our professional support team.</p>

                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The MindMend Team</strong>
                </p>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
                    <p>This link is valid for 7 days. If you did not apply to join MindMend's professional network, please disregard this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        send_email(application.email, subject, html_body)
        logger.info(f"Approval email sent to {application.email}")

    except Exception as e:
        logger.error(f"Failed to send approval email to {application.email}: {e}")


def send_application_rejection_email(application, reason=None):
    """Send rejection email with feedback"""
    if not EMAIL_AVAILABLE:
        logger.warning(f"Email not sent to {application.email} - email not configured")
        return

    try:
        subject = "Update on Your MindMend Professional Application"

        feedback_section = ""
        if reason:
            feedback_section = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0;">
                <h4 style="margin-top: 0;">Feedback:</h4>
                <p>{reason}</p>
            </div>
            """

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">Thank you for your application, {application.name}</h2>

                <p>Thank you for your interest in joining the MindMend professional network. After careful review, we regret to inform you that we are unable to move forward with your application at this time.</p>

                {feedback_section}

                <p>We encourage you to reapply in the future if your circumstances change or you gain additional qualifications.</p>

                <p><strong>You may reapply if you:</strong></p>
                <ul>
                    <li>Obtain additional licenses or certifications</li>
                    <li>Gain more clinical experience</li>
                    <li>Complete specialized mental health training</li>
                </ul>

                <p>We appreciate your interest in MindMend and wish you the best in your professional endeavors.</p>

                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The MindMend Team</strong>
                </p>
            </div>
        </body>
        </html>
        """

        send_email(application.email, subject, html_body)
        logger.info(f"Rejection email sent to {application.email}")

    except Exception as e:
        logger.error(f"Failed to send rejection email to {application.email}: {e}")


# ========================================
# AUTHENTICATION DECORATORS
# ========================================

def require_professional_auth(f):
    """Decorator to require professional authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'professional_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('professional_mgmt.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def require_admin_auth(f):
    """Decorator to require admin authentication for professional admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if admin is logged in
        if 'admin_user_id' not in session:
            flash('Admin authentication required', 'error')
            return redirect(url_for('admin.login', next=request.url))

        # Check if admin has professional management permissions
        admin_role = session.get('admin_role', '')
        if admin_role not in ['super_admin', 'support_admin']:
            flash('Insufficient permissions for professional management', 'error')
            return redirect(url_for('admin.dashboard'))

        return f(*args, **kwargs)
    return decorated_function


# ========================================
# PROFESSIONAL REGISTRATION & APPLICATION
# ========================================

@professional_mgmt_bp.route('/apply', methods=['GET', 'POST'])
def apply():
    """Professional application form"""
    if request.method == 'POST':
        try:
            # Collect application data
            application = ProfessionalApplication(
                email=request.form.get('email').strip().lower(),
                name=request.form.get('name'),
                phone=request.form.get('phone'),
                position_type=request.form.get('position_type'),
                license_type=request.form.get('license_type'),
                license_number=request.form.get('license_number'),
                years_experience=int(request.form.get('years_experience', 0)),
                specializations=json.dumps(request.form.getlist('specializations')),
                education=request.form.get('education'),
                cover_letter=request.form.get('cover_letter'),
                status='pending'
            )

            # Handle file uploads (in production, upload to S3)
            if 'resume' in request.files:
                resume = request.files['resume']
                if resume.filename:
                    # In production: upload to S3 and store URL
                    application.resume_url = f"/uploads/resumes/{uuid.uuid4()}_{resume.filename}"

            if 'license_document' in request.files:
                license_doc = request.files['license_document']
                if license_doc.filename:
                    application.license_document_url = f"/uploads/licenses/{uuid.uuid4()}_{license_doc.filename}"

            db.session.add(application)
            db.session.commit()

            flash('Application submitted successfully! We will review and contact you within 48 hours.', 'success')
            return jsonify({
                'success': True,
                'application_id': application.id,
                'message': 'Application submitted successfully'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

    # GET request - show application form
    return render_template_string(APPLICATION_FORM_TEMPLATE)


@professional_mgmt_bp.route('/register/<int:application_id>', methods=['GET', 'POST'])
def register(application_id):
    """Complete registration after application approval"""
    application = ProfessionalApplication.query.get_or_404(application_id)

    if application.status != 'approved':
        flash('Application not yet approved', 'warning')
        return redirect(url_for('professional_mgmt.apply'))

    if request.method == 'POST':
        try:
            # Create professional account
            professional = Professional(
                email=application.email,
                name=application.name,
                phone=application.phone,
                license_type=application.license_type,
                license_number=application.license_number,
                years_experience=application.years_experience,
                specializations=application.specializations,
                education=application.education,
                verification_status='pending',
                is_active=False,
                email_verified=False
            )

            # Set password
            password = request.form.get('password')
            professional.set_password(password)

            # Additional profile info
            professional.ahpra_registration = request.form.get('ahpra_registration')
            professional.license_state = request.form.get('license_state')
            professional.timezone = request.form.get('timezone', 'Australia/Sydney')
            professional.bio = request.form.get('bio')
            professional.hourly_rate = float(request.form.get('hourly_rate', 120))

            db.session.add(professional)
            db.session.commit()

            flash('Registration complete! Your account is pending verification.', 'success')
            return redirect(url_for('professional_mgmt.login'))

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

    return render_template_string(REGISTRATION_FORM_TEMPLATE, application=application)


@professional_mgmt_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Professional login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        professional = Professional.query.filter_by(email=email).first()
        if professional and professional.check_password(password):
            if not professional.is_active:
                flash('Your account is pending verification', 'warning')
                return redirect(url_for('professional_mgmt.login'))

            session['professional_id'] = professional.id
            session['professional_email'] = professional.email
            session['professional_name'] = professional.name
            flash('Logged in successfully', 'success')
            return redirect(url_for('professional_mgmt.dashboard'))

        flash('Invalid credentials', 'error')

    return render_template_string(LOGIN_FORM_TEMPLATE)


@professional_mgmt_bp.route('/logout')
def logout():
    """Professional logout"""
    session.pop('professional_id', None)
    session.pop('professional_email', None)
    session.pop('professional_name', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('professional_mgmt.login'))


# ========================================
# PROFESSIONAL DASHBOARD
# ========================================

@professional_mgmt_bp.route('/dashboard')
@require_professional_auth
def dashboard():
    """Main professional dashboard"""
    professional_id = session.get('professional_id')
    if not professional_id:
        return redirect(url_for('professional_mgmt.login'))

    professional = Professional.query.get_or_404(professional_id)

    # Get pending reviews
    pending_reviews = SessionReview.query.filter_by(
        professional_id=professional_id,
        status='assigned'
    ).order_by(SessionReview.priority.desc(), SessionReview.assigned_at).limit(10).all()

    # Get recent completed reviews
    completed_reviews = SessionReview.query.filter_by(
        professional_id=professional_id,
        status='completed'
    ).order_by(SessionReview.completed_at.desc()).limit(5).all()

    # Calculate earnings this month
    start_of_month = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_earnings = ProfessionalPayment.query.filter(
        ProfessionalPayment.professional_id == professional_id,
        ProfessionalPayment.period_start >= start_of_month
    ).first()

    dashboard_data = {
        'professional': professional,
        'pending_reviews': pending_reviews,
        'completed_reviews': completed_reviews,
        'monthly_earnings': monthly_earnings,
        'stats': {
            'total_sessions': professional.total_sessions,
            'average_rating': professional.average_rating,
            'response_time': professional.response_time_minutes,
            'completion_rate': professional.completion_rate
        }
    }

    return render_template_string(DASHBOARD_TEMPLATE, **dashboard_data)


@professional_mgmt_bp.route('/review/<int:session_id>', methods=['GET', 'POST'])
@require_professional_auth
def review_session(session_id):
    """Review an AI therapy session"""
    professional_id = session.get('professional_id')
    if not professional_id:
        return redirect(url_for('professional_mgmt.login'))

    from models.database import Session
    therapy_session = Session.query.get_or_404(session_id)

    if request.method == 'POST':
        try:
            # Create or update session review
            review = SessionReview.query.filter_by(
                session_id=session_id,
                professional_id=professional_id
            ).first()

            if not review:
                review = SessionReview(
                    session_id=session_id,
                    professional_id=professional_id,
                    assigned_at=datetime.now(UTC)
                )

            review.status = 'completed'
            review.completed_at = datetime.now(UTC)
            review.ai_quality_score = int(request.form.get('ai_quality_score', 5))
            review.intervention_needed = request.form.get('intervention_needed') == 'true'
            review.risk_level = request.form.get('risk_level', 'low')
            review.clinical_notes = request.form.get('clinical_notes')
            review.recommendations = request.form.get('recommendations')
            review.action_taken = request.form.get('action_taken', 'reviewed')
            review.follow_up_required = request.form.get('follow_up_required') == 'true'

            if not review.id:
                db.session.add(review)

            db.session.commit()

            flash('Review submitted successfully', 'success')
            return redirect(url_for('professional_mgmt.dashboard'))

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

    return render_template_string(REVIEW_SESSION_TEMPLATE, session=therapy_session)


# ========================================
# ADMIN PANEL - PROFESSIONAL MANAGEMENT
# ========================================

@professional_mgmt_bp.route('/admin/applications')
@require_admin_auth
def admin_applications():
    """Admin view of professional applications"""

    status_filter = request.args.get('status', 'pending')
    applications = ProfessionalApplication.query.filter_by(status=status_filter).order_by(
        ProfessionalApplication.created_at.desc()
    ).all()

    return render_template_string(ADMIN_APPLICATIONS_TEMPLATE, applications=applications, status_filter=status_filter)


@professional_mgmt_bp.route('/admin/application/<int:application_id>', methods=['GET', 'POST'])
@require_admin_auth
def admin_review_application(application_id):
    """Admin review of a professional application"""
    application = ProfessionalApplication.query.get_or_404(application_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'approve':
            application.status = 'approved'
            application.reviewed_by = session.get('admin_email', 'admin')
            application.reviewed_at = datetime.now(UTC)
            application.review_notes = request.form.get('review_notes')

            # Send approval email with registration link
            send_application_approval_email(application)

            flash(f'Application approved for {application.name}', 'success')

        elif action == 'reject':
            application.status = 'rejected'
            application.reviewed_by = session.get('admin_email', 'admin')
            application.reviewed_at = datetime.now(UTC)
            application.review_notes = request.form.get('review_notes')
            application.rejection_reason = request.form.get('rejection_reason', '')

            # Send rejection email
            send_application_rejection_email(application, application.rejection_reason)

            flash(f'Application rejected for {application.name}', 'info')

        elif action == 'schedule_interview':
            application.interview_scheduled = True
            application.interview_date = datetime.fromisoformat(request.form.get('interview_date'))

            flash(f'Interview scheduled for {application.name}', 'success')

        db.session.commit()
        return redirect(url_for('professional_mgmt.admin_applications'))

    return render_template_string(ADMIN_REVIEW_APPLICATION_TEMPLATE, application=application)


@professional_mgmt_bp.route('/admin/professionals')
@require_admin_auth
def admin_professionals():
    """Admin view of all professionals"""
    status_filter = request.args.get('status', 'all')

    query = Professional.query
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'pending':
        query = query.filter_by(verification_status='pending')
    elif status_filter == 'verified':
        query = query.filter_by(verification_status='verified')

    professionals = query.order_by(Professional.created_at.desc()).all()

    return render_template_string(ADMIN_PROFESSIONALS_TEMPLATE, professionals=professionals, status_filter=status_filter)


@professional_mgmt_bp.route('/admin/professional/<int:professional_id>', methods=['GET', 'POST'])
@require_admin_auth
def admin_manage_professional(professional_id):
    """Admin management of individual professional"""
    professional = Professional.query.get_or_404(professional_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'verify':
            professional.verification_status = 'verified'
            professional.verified_at = datetime.now(UTC)
            professional.verified_by = session.get('admin_email', 'admin')
            professional.is_active = True
            flash(f'{professional.name} has been verified and activated', 'success')

        elif action == 'deactivate':
            professional.is_active = False
            flash(f'{professional.name} has been deactivated', 'info')

        elif action == 'activate':
            professional.is_active = True
            flash(f'{professional.name} has been activated', 'success')

        elif action == 'update_rate':
            professional.hourly_rate = float(request.form.get('hourly_rate'))
            professional.platform_fee_percentage = float(request.form.get('platform_fee_percentage'))
            flash('Compensation updated', 'success')

        db.session.commit()
        return redirect(url_for('professional_mgmt.admin_professionals'))

    # Get professional's statistics
    total_reviews = SessionReview.query.filter_by(professional_id=professional_id).count()
    pending_reviews = SessionReview.query.filter_by(
        professional_id=professional_id,
        status='assigned'
    ).count()

    recent_payments = ProfessionalPayment.query.filter_by(
        professional_id=professional_id
    ).order_by(ProfessionalPayment.created_at.desc()).limit(5).all()

    return render_template_string(
        ADMIN_MANAGE_PROFESSIONAL_TEMPLATE,
        professional=professional,
        total_reviews=total_reviews,
        pending_reviews=pending_reviews,
        recent_payments=recent_payments
    )


@professional_mgmt_bp.route('/admin/compliance')
@require_admin_auth
def admin_compliance_dashboard():
    """Admin compliance monitoring dashboard"""
    # Find expiring credentials
    expiry_threshold = datetime.now(UTC) + timedelta(days=30)

    expiring_licenses = Professional.query.filter(
        Professional.license_expiry <= expiry_threshold,
        Professional.license_expiry >= datetime.now(UTC),
        Professional.is_active == True
    ).all()

    expiring_insurance = Professional.query.filter(
        Professional.insurance_expiry <= expiry_threshold,
        Professional.insurance_expiry >= datetime.now(UTC),
        Professional.is_active == True
    ).all()

    pending_verifications = Professional.query.filter_by(
        verification_status='pending'
    ).count()

    return render_template_string(
        ADMIN_COMPLIANCE_TEMPLATE,
        expiring_licenses=expiring_licenses,
        expiring_insurance=expiring_insurance,
        pending_verifications=pending_verifications
    )


# ========================================
# API ENDPOINTS
# ========================================

@professional_mgmt_bp.route('/api/professionals', methods=['GET'])
def api_get_professionals():
    """API endpoint to get professionals list"""
    professionals = Professional.query.filter_by(is_active=True).all()

    return jsonify({
        'success': True,
        'professionals': [{
            'id': p.id,
            'name': p.name,
            'license_type': p.license_type,
            'specializations': json.loads(p.specializations) if p.specializations else [],
            'languages': json.loads(p.languages) if p.languages else [],
            'average_rating': p.average_rating,
            'accepts_new_clients': p.accepts_new_clients,
            'hourly_rate': p.hourly_rate
        } for p in professionals]
    })


@professional_mgmt_bp.route('/api/assign-review', methods=['POST'])
def api_assign_review():
    """API endpoint to assign a session review to a professional"""
    data = request.get_json()
    session_id = data.get('session_id')
    professional_id = data.get('professional_id')
    priority = data.get('priority', 'normal')

    try:
        review = SessionReview(
            session_id=session_id,
            professional_id=professional_id,
            priority=priority,
            review_type='flagged',
            status='assigned',
            assigned_at=datetime.now(UTC)
        )

        db.session.add(review)
        db.session.commit()

        return jsonify({
            'success': True,
            'review_id': review.id,
            'message': 'Review assigned successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


# ========================================
# TEMPLATES
# ========================================

APPLICATION_FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Apply as a Mental Health Professional - MindMend</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        textarea { min-height: 100px; }
        button { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #2980b9; }
        .checkbox-group { display: flex; flex-wrap: wrap; gap: 15px; }
        .checkbox-group label { font-weight: normal; display: flex; align-items: center; width: auto; }
        .checkbox-group input { width: auto; margin-right: 5px; }
    </style>
</head>
<body>
    <h1>Apply as a Mental Health Professional</h1>
    <p>Join our team of licensed professionals providing oversight and support for AI-assisted therapy.</p>

    <form method="POST" enctype="multipart/form-data">
        <div class="form-group">
            <label>Full Name *</label>
            <input type="text" name="name" required>
        </div>

        <div class="form-group">
            <label>Email *</label>
            <input type="email" name="email" required>
        </div>

        <div class="form-group">
            <label>Phone</label>
            <input type="tel" name="phone">
        </div>

        <div class="form-group">
            <label>Position Type *</label>
            <select name="position_type" required>
                <option value="">Select position type</option>
                <option value="full_time">Full-Time</option>
                <option value="part_time">Part-Time</option>
                <option value="contract">Contract</option>
            </select>
        </div>

        <div class="form-group">
            <label>License Type *</label>
            <select name="license_type" required>
                <option value="">Select license type</option>
                <option value="Clinical Psychologist">Clinical Psychologist</option>
                <option value="LMFT">Licensed Marriage and Family Therapist (LMFT)</option>
                <option value="LCSW">Licensed Clinical Social Worker (LCSW)</option>
                <option value="Psychiatrist">Psychiatrist</option>
                <option value="Counselor">Licensed Professional Counselor</option>
            </select>
        </div>

        <div class="form-group">
            <label>License Number *</label>
            <input type="text" name="license_number" required>
        </div>

        <div class="form-group">
            <label>Years of Experience *</label>
            <input type="number" name="years_experience" min="0" required>
        </div>

        <div class="form-group">
            <label>Specializations (select all that apply)</label>
            <div class="checkbox-group">
                <label><input type="checkbox" name="specializations" value="anxiety"> Anxiety</label>
                <label><input type="checkbox" name="specializations" value="depression"> Depression</label>
                <label><input type="checkbox" name="specializations" value="trauma"> Trauma/PTSD</label>
                <label><input type="checkbox" name="specializations" value="couples"> Couples Therapy</label>
                <label><input type="checkbox" name="specializations" value="addiction"> Addiction</label>
                <label><input type="checkbox" name="specializations" value="eating_disorders"> Eating Disorders</label>
                <label><input type="checkbox" name="specializations" value="crisis"> Crisis Intervention</label>
            </div>
        </div>

        <div class="form-group">
            <label>Education *</label>
            <textarea name="education" placeholder="List your degrees, certifications, and educational background" required></textarea>
        </div>

        <div class="form-group">
            <label>Cover Letter *</label>
            <textarea name="cover_letter" placeholder="Tell us why you want to join MindMend and what makes you a great fit" required></textarea>
        </div>

        <div class="form-group">
            <label>Resume/CV *</label>
            <input type="file" name="resume" accept=".pdf,.doc,.docx" required>
        </div>

        <div class="form-group">
            <label>License Document</label>
            <input type="file" name="license_document" accept=".pdf,.jpg,.png">
        </div>

        <button type="submit">Submit Application</button>
    </form>
</body>
</html>
"""

REGISTRATION_FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Complete Your Registration - MindMend</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #2c3e50; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #27ae60; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #229954; }
    </style>
</head>
<body>
    <h1>Complete Your Registration</h1>
    <p>Congratulations {{ application.name }}! Your application has been approved.</p>

    <form method="POST">
        <div class="form-group">
            <label>Create Password *</label>
            <input type="password" name="password" required minlength="8">
        </div>

        <div class="form-group">
            <label>AHPRA Registration Number (for Australian professionals)</label>
            <input type="text" name="ahpra_registration">
        </div>

        <div class="form-group">
            <label>License State/Country *</label>
            <input type="text" name="license_state" required>
        </div>

        <div class="form-group">
            <label>Timezone *</label>
            <select name="timezone">
                <option value="Australia/Sydney">Australia/Sydney</option>
                <option value="Australia/Melbourne">Australia/Melbourne</option>
                <option value="America/New_York">America/New_York</option>
                <option value="America/Los_Angeles">America/Los_Angeles</option>
                <option value="Europe/London">Europe/London</option>
            </select>
        </div>

        <div class="form-group">
            <label>Professional Bio</label>
            <textarea name="bio" placeholder="Brief professional bio for your profile"></textarea>
        </div>

        <div class="form-group">
            <label>Hourly Rate (USD) *</label>
            <input type="number" name="hourly_rate" value="120" step="5" required>
        </div>

        <button type="submit">Complete Registration</button>
    </form>
</body>
</html>
"""

LOGIN_FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Professional Login - MindMend</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
        h1 { color: #2c3e50; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { width: 100%; background: #3498db; color: white; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #2980b9; }
        .links { text-align: center; margin-top: 20px; }
        .links a { color: #3498db; text-decoration: none; }
    </style>
</head>
<body>
    <h1>Professional Portal</h1>

    <form method="POST">
        <div class="form-group">
            <label>Email</label>
            <input type="email" name="email" required>
        </div>

        <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" required>
        </div>

        <button type="submit">Login</button>
    </form>

    <div class="links">
        <p><a href="{{ url_for('professional_mgmt.apply') }}">Apply to Join Our Team</a></p>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Professional Dashboard - MindMend</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        .header { background: #2c3e50; color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-card h3 { margin: 0; color: #7f8c8d; font-size: 14px; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: #2c3e50; margin: 10px 0; }
        .section { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { color: #2c3e50; margin-top: 0; }
        .review-item { border-bottom: 1px solid #ecf0f1; padding: 15px 0; }
        .review-item:last-child { border-bottom: none; }
        .priority-urgent { color: #e74c3c; font-weight: bold; }
        .priority-high { color: #e67e22; }
        button { background: #3498db; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #2980b9; }
        .logout { background: #e74c3c; padding: 10px 20px; border: none; border-radius: 4px; color: white; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Professional Dashboard</h1>
        <div>
            <span>Welcome, {{ professional.name }}</span>
            <a href="{{ url_for('professional_mgmt.logout') }}"><button class="logout">Logout</button></a>
        </div>
    </div>

    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <h3>Total Sessions</h3>
                <div class="value">{{ stats.total_sessions }}</div>
            </div>
            <div class="stat-card">
                <h3>Average Rating</h3>
                <div class="value">{{ "%.1f"|format(stats.average_rating) }}</div>
            </div>
            <div class="stat-card">
                <h3>Response Time</h3>
                <div class="value">{{ stats.response_time }}m</div>
            </div>
            <div class="stat-card">
                <h3>Completion Rate</h3>
                <div class="value">{{ "%.1f"|format(stats.completion_rate) }}%</div>
            </div>
        </div>

        {% if monthly_earnings %}
        <div class="section">
            <h2>This Month's Earnings</h2>
            <p>Gross: ${{ "%.2f"|format(monthly_earnings.gross_earnings) }}</p>
            <p>Platform Fee: ${{ "%.2f"|format(monthly_earnings.platform_fee) }}</p>
            <p><strong>Net Earnings: ${{ "%.2f"|format(monthly_earnings.net_earnings) }}</strong></p>
        </div>
        {% endif %}

        <div class="section">
            <h2>Pending Reviews ({{ pending_reviews|length }})</h2>
            {% for review in pending_reviews %}
            <div class="review-item">
                <span class="priority-{{ review.priority }}">{{ review.priority|upper }}</span> -
                Session #{{ review.session_id }} -
                <a href="{{ url_for('professional_mgmt.review_session', session_id=review.session_id) }}"><button>Review</button></a>
            </div>
            {% endfor %}
            {% if not pending_reviews %}
            <p>No pending reviews at this time.</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>Recently Completed Reviews</h2>
            {% for review in completed_reviews %}
            <div class="review-item">
                Session #{{ review.session_id }} - Completed {{ review.completed_at.strftime('%Y-%m-%d %H:%M') }} -
                Quality Score: {{ review.ai_quality_score }}/10
            </div>
            {% endfor %}
            {% if not completed_reviews %}
            <p>No completed reviews yet.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

REVIEW_SESSION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Review Session - MindMend</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 30px auto; padding: 20px; }
        .session-details { background: #ecf0f1; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        textarea { min-height: 100px; }
        button { background: #27ae60; color: white; padding: 12px 30px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #229954; }
        .conversation { background: white; padding: 20px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px; }
        .message { margin-bottom: 15px; padding: 10px; border-radius: 4px; }
        .user-message { background: #e3f2fd; }
        .ai-message { background: #f1f8e9; }
    </style>
</head>
<body>
    <h1>Review Therapy Session</h1>

    <div class="session-details">
        <p><strong>Session ID:</strong> {{ session.id }}</p>
        <p><strong>Patient:</strong> {{ session.patient_name }}</p>
        <p><strong>Session Type:</strong> {{ session.session_type }}</p>
        <p><strong>Date:</strong> {{ session.timestamp.strftime('%Y-%m-%d %H:%M') }}</p>
    </div>

    <div class="conversation">
        <h3>Conversation</h3>
        <div class="message user-message">
            <strong>Patient:</strong> {{ session.input_text }}
        </div>
        <div class="message ai-message">
            <strong>AI Response:</strong> {{ session.ai_response }}
        </div>
    </div>

    <form method="POST">
        <div class="form-group">
            <label>AI Quality Score (1-10)</label>
            <input type="number" name="ai_quality_score" min="1" max="10" value="5" required>
        </div>

        <div class="form-group">
            <label>Risk Level</label>
            <select name="risk_level" required>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
            </select>
        </div>

        <div class="form-group">
            <label>Intervention Needed?</label>
            <select name="intervention_needed">
                <option value="false">No</option>
                <option value="true">Yes</option>
            </select>
        </div>

        <div class="form-group">
            <label>Clinical Notes (Confidential)</label>
            <textarea name="clinical_notes" required></textarea>
        </div>

        <div class="form-group">
            <label>Recommendations</label>
            <textarea name="recommendations"></textarea>
        </div>

        <div class="form-group">
            <label>Action Taken</label>
            <select name="action_taken">
                <option value="reviewed">Reviewed - No action needed</option>
                <option value="contacted_patient">Contacted patient directly</option>
                <option value="escalated">Escalated to supervisor</option>
                <option value="modified_care_plan">Modified care plan</option>
            </select>
        </div>

        <div class="form-group">
            <label>Follow-up Required?</label>
            <select name="follow_up_required">
                <option value="false">No</option>
                <option value="true">Yes</option>
            </select>
        </div>

        <button type="submit">Submit Review</button>
    </form>
</body>
</html>
"""

ADMIN_APPLICATIONS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Professional Applications - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .filters { margin-bottom: 20px; }
        .filters a { padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }
        .filters a.active { background: #2c3e50; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #34495e; color: white; }
        .status-pending { color: #f39c12; }
        .status-approved { color: #27ae60; }
        .status-rejected { color: #e74c3c; }
        button { padding: 5px 10px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Professional Applications</h1>

    <div class="filters">
        <a href="?status=pending" class="{{ 'active' if status_filter == 'pending' }}">Pending</a>
        <a href="?status=approved" class="{{ 'active' if status_filter == 'approved' }}">Approved</a>
        <a href="?status=rejected" class="{{ 'active' if status_filter == 'rejected' }}">Rejected</a>
        <a href="?status=all" class="{{ 'active' if status_filter == 'all' }}">All</a>
    </div>

    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Email</th>
                <th>License Type</th>
                <th>Experience</th>
                <th>Applied</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for app in applications %}
            <tr>
                <td>{{ app.name }}</td>
                <td>{{ app.email }}</td>
                <td>{{ app.license_type }}</td>
                <td>{{ app.years_experience }} years</td>
                <td>{{ app.created_at.strftime('%Y-%m-%d') }}</td>
                <td class="status-{{ app.status }}">{{ app.status }}</td>
                <td>
                    <a href="{{ url_for('professional_mgmt.admin_review_application', application_id=app.id) }}">
                        <button>Review</button>
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

ADMIN_REVIEW_APPLICATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Review Application - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: 30px auto; padding: 20px; }
        .detail { background: #ecf0f1; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .detail p { margin: 10px 0; }
        .actions { margin-top: 30px; }
        button { padding: 12px 30px; margin-right: 10px; cursor: pointer; border: none; border-radius: 4px; font-size: 16px; }
        .approve { background: #27ae60; color: white; }
        .reject { background: #e74c3c; color: white; }
        .schedule { background: #3498db; color: white; }
        textarea { width: 100%; padding: 10px; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Review Application: {{ application.name }}</h1>

    <div class="detail">
        <p><strong>Email:</strong> {{ application.email }}</p>
        <p><strong>Phone:</strong> {{ application.phone }}</p>
        <p><strong>Position:</strong> {{ application.position_type }}</p>
        <p><strong>License Type:</strong> {{ application.license_type }}</p>
        <p><strong>License Number:</strong> {{ application.license_number }}</p>
        <p><strong>Experience:</strong> {{ application.years_experience }} years</p>
        <p><strong>Education:</strong></p>
        <p>{{ application.education }}</p>
        <p><strong>Cover Letter:</strong></p>
        <p>{{ application.cover_letter }}</p>
        {% if application.resume_url %}
        <p><strong>Resume:</strong> <a href="{{ application.resume_url }}">Download</a></p>
        {% endif %}
    </div>

    <div class="actions">
        <form method="POST" style="display: inline;">
            <input type="hidden" name="action" value="approve">
            <textarea name="review_notes" placeholder="Approval notes"></textarea>
            <button type="submit" class="approve">Approve Application</button>
        </form>

        <form method="POST" style="display: inline;">
            <input type="hidden" name="action" value="reject">
            <textarea name="review_notes" placeholder="Rejection reason"></textarea>
            <button type="submit" class="reject">Reject Application</button>
        </form>

        <form method="POST" style="display: inline;">
            <input type="hidden" name="action" value="schedule_interview">
            <input type="datetime-local" name="interview_date" required>
            <button type="submit" class="schedule">Schedule Interview</button>
        </form>
    </div>
</body>
</html>
"""

ADMIN_PROFESSIONALS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Manage Professionals - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .filters { margin-bottom: 20px; }
        .filters a { padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }
        .filters a.active { background: #2c3e50; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #34495e; color: white; }
        .active { color: #27ae60; font-weight: bold; }
        .inactive { color: #7f8c8d; }
        button { padding: 5px 10px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Manage Professionals</h1>

    <div class="filters">
        <a href="?status=all" class="{{ 'active' if status_filter == 'all' }}">All</a>
        <a href="?status=active" class="{{ 'active' if status_filter == 'active' }}">Active</a>
        <a href="?status=pending" class="{{ 'active' if status_filter == 'pending' }}">Pending Verification</a>
        <a href="?status=verified" class="{{ 'active' if status_filter == 'verified' }}">Verified</a>
    </div>

    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Email</th>
                <th>License Type</th>
                <th>Status</th>
                <th>Rating</th>
                <th>Total Sessions</th>
                <th>Joined</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for prof in professionals %}
            <tr>
                <td>{{ prof.name }}</td>
                <td>{{ prof.email }}</td>
                <td>{{ prof.license_type }}</td>
                <td class="{{ 'active' if prof.is_active else 'inactive' }}">
                    {{ 'Active' if prof.is_active else 'Inactive' }}
                </td>
                <td>{{ "%.1f"|format(prof.average_rating) }}</td>
                <td>{{ prof.total_sessions }}</td>
                <td>{{ prof.created_at.strftime('%Y-%m-%d') }}</td>
                <td>
                    <a href="{{ url_for('professional_mgmt.admin_manage_professional', professional_id=prof.id) }}">
                        <button>Manage</button>
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

ADMIN_MANAGE_PROFESSIONAL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Manage {{ professional.name }} - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 30px auto; padding: 20px; }
        .profile { background: #ecf0f1; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
        .stat-card { background: white; padding: 15px; border-radius: 4px; text-align: center; }
        .actions { margin-top: 30px; }
        button { padding: 10px 20px; margin-right: 10px; cursor: pointer; border: none; border-radius: 4px; color: white; }
        .verify { background: #27ae60; }
        .deactivate { background: #e74c3c; }
        .activate { background: #3498db; }
        input { padding: 8px; margin-right: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>Manage Professional: {{ professional.name }}</h1>

    <div class="profile">
        <p><strong>Email:</strong> {{ professional.email }}</p>
        <p><strong>License:</strong> {{ professional.license_type }} - {{ professional.license_number }}</p>
        <p><strong>AHPRA:</strong> {{ professional.ahpra_registration or 'N/A' }}</p>
        <p><strong>Status:</strong> {{ 'Active' if professional.is_active else 'Inactive' }}</p>
        <p><strong>Verification:</strong> {{ professional.verification_status }}</p>
        <p><strong>Hourly Rate:</strong> ${{ professional.hourly_rate }}</p>
        <p><strong>Platform Fee:</strong> {{ professional.platform_fee_percentage }}%</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>Total Reviews</h3>
            <p>{{ total_reviews }}</p>
        </div>
        <div class="stat-card">
            <h3>Pending</h3>
            <p>{{ pending_reviews }}</p>
        </div>
        <div class="stat-card">
            <h3>Avg Rating</h3>
            <p>{{ "%.1f"|format(professional.average_rating) }}</p>
        </div>
        <div class="stat-card">
            <h3>Completion</h3>
            <p>{{ "%.1f"|format(professional.completion_rate) }}%</p>
        </div>
    </div>

    <div class="actions">
        <h2>Actions</h2>

        {% if professional.verification_status == 'pending' %}
        <form method="POST" style="display: inline;">
            <input type="hidden" name="action" value="verify">
            <button type="submit" class="verify">Verify & Activate</button>
        </form>
        {% endif %}

        {% if professional.is_active %}
        <form method="POST" style="display: inline;">
            <input type="hidden" name="action" value="deactivate">
            <button type="submit" class="deactivate">Deactivate</button>
        </form>
        {% else %}
        <form method="POST" style="display: inline;">
            <input type="hidden" name="action" value="activate">
            <button type="submit" class="activate">Activate</button>
        </form>
        {% endif %}

        <form method="POST" style="display: inline; margin-left: 20px;">
            <input type="hidden" name="action" value="update_rate">
            <label>Hourly Rate:</label>
            <input type="number" name="hourly_rate" value="{{ professional.hourly_rate }}" step="5">
            <label>Platform Fee %:</label>
            <input type="number" name="platform_fee_percentage" value="{{ professional.platform_fee_percentage }}" step="0.5">
            <button type="submit">Update Compensation</button>
        </form>
    </div>

    <h2>Recent Payments</h2>
    <table>
        <thead>
            <tr>
                <th>Period</th>
                <th>Gross</th>
                <th>Platform Fee</th>
                <th>Net</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for payment in recent_payments %}
            <tr>
                <td>{{ payment.period_start.strftime('%Y-%m-%d') }} - {{ payment.period_end.strftime('%Y-%m-%d') }}</td>
                <td>${{ "%.2f"|format(payment.gross_earnings) }}</td>
                <td>${{ "%.2f"|format(payment.platform_fee) }}</td>
                <td>${{ "%.2f"|format(payment.net_earnings) }}</td>
                <td>{{ payment.payment_status }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

ADMIN_COMPLIANCE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Dashboard - Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .alert-section { background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin-bottom: 20px; }
        .alert-section h2 { color: #856404; margin-top: 0; }
        .warning-item { padding: 10px; border-bottom: 1px solid #ddd; }
        .critical { background: #f8d7da; }
        .stat-box { display: inline-block; background: white; padding: 20px; border-radius: 8px; margin-right: 20px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-box h3 { margin: 0; color: #7f8c8d; }
        .stat-box .value { font-size: 36px; font-weight: bold; color: #e74c3c; }
    </style>
</head>
<body>
    <h1>Compliance Dashboard</h1>

    <div>
        <div class="stat-box">
            <h3>Pending Verifications</h3>
            <div class="value">{{ pending_verifications }}</div>
        </div>
        <div class="stat-box">
            <h3>Expiring Licenses</h3>
            <div class="value">{{ expiring_licenses|length }}</div>
        </div>
        <div class="stat-box">
            <h3>Expiring Insurance</h3>
            <div class="value">{{ expiring_insurance|length }}</div>
        </div>
    </div>

    <div class="alert-section">
        <h2>Expiring Professional Licenses (Next 30 Days)</h2>
        {% for prof in expiring_licenses %}
        <div class="warning-item">
            <strong>{{ prof.name }}</strong> ({{ prof.email }}) -
            License expires: {{ prof.license_expiry.strftime('%Y-%m-%d') }}
        </div>
        {% else %}
        <p>No licenses expiring in the next 30 days.</p>
        {% endfor %}
    </div>

    <div class="alert-section">
        <h2>Expiring Insurance Policies (Next 30 Days)</h2>
        {% for prof in expiring_insurance %}
        <div class="warning-item">
            <strong>{{ prof.name }}</strong> ({{ prof.email }}) -
            Insurance expires: {{ prof.insurance_expiry.strftime('%Y-%m-%d') }}
        </div>
        {% else %}
        <p>No insurance policies expiring in the next 30 days.</p>
        {% endfor %}
    </div>
</body>
</html>
"""
