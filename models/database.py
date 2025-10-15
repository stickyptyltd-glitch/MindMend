from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import UserMixin

class Base(DeclarativeBase):
    pass

# Create the SQLAlchemy instance here to avoid circular imports
db = SQLAlchemy(model_class=Base)
from datetime import datetime, UTC
from sqlalchemy import Text, event
from werkzeug.security import generate_password_hash, check_password_hash

# Multi-tenant schema setup for platform integration (MindMend + Stop the Cycle)
# This allows shared infrastructure while maintaining data separation
# Note: Schemas are created in the migration script, not via event listeners

class Session(db.Model):
    """Model for therapy sessions"""
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)
    input_text = db.Column(Text, nullable=False)
    ai_response = db.Column(Text, nullable=False)
    alerts = db.Column(Text)  # JSON string of alerts
    video_analysis = db.Column(Text)  # JSON string of video analysis
    biometric_data = db.Column(Text)  # JSON string of biometric data
    exercises_assigned = db.Column(Text)  # JSON string of exercises
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    duration_minutes = db.Column(db.Integer)
    mood_before = db.Column(db.Integer)  # 1-10 scale
    mood_after = db.Column(db.Integer)  # 1-10 scale
    satisfaction_rating = db.Column(db.Integer)  # 1-5 scale
    notes = db.Column(Text)
    
    def __repr__(self):
        return f'<Session {self.id}: {self.patient_name} - {self.session_type}>'

class BiometricData(db.Model):
    """Model for biometric data from wearables"""
    id = db.Column(db.Integer, primary_key=True)
    heart_rate = db.Column(db.Integer)
    stress_level = db.Column(db.Float)  # 0-1 scale
    sleep_quality = db.Column(db.Float)  # 0-1 scale
    activity_level = db.Column(db.Integer)  # steps or activity units
    hrv_score = db.Column(db.Float)  # Heart rate variability
    blood_oxygen = db.Column(db.Float)
    temperature = db.Column(db.Float)
    raw_data = db.Column(Text)  # JSON string of raw device data
    device_type = db.Column(db.String(50))  # Apple Watch, Fitbit, etc.
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    def __repr__(self):
        return f'<BiometricData {self.id}: HR={self.heart_rate}, Stress={self.stress_level}>'

class VideoAnalysis(db.Model):
    """Model for video analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
    emotions_detected = db.Column(Text)  # JSON string of emotions
    microexpressions = db.Column(Text)  # JSON string of microexpressions
    eye_movement_patterns = db.Column(Text)  # JSON string of eye tracking
    facial_landmarks = db.Column(Text)  # JSON string of facial landmarks
    voice_analysis = db.Column(Text)  # JSON string of voice sentiment
    confidence_score = db.Column(db.Float)
    frame_timestamp = db.Column(db.Float)  # Timestamp within session
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    session = db.relationship('Session', backref=db.backref('video_analyses', lazy=True))
    
    def __repr__(self):
        return f'<VideoAnalysis {self.id}: Session {self.session_id}>'

class Exercise(db.Model):
    """Model for AI-generated therapeutic exercises"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=True)
    exercise_type = db.Column(db.String(50), nullable=False)  # breathing, mindfulness, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(Text, nullable=False)
    instructions = db.Column(Text, nullable=False)
    duration_minutes = db.Column(db.Integer)
    difficulty_level = db.Column(db.Integer)  # 1-5 scale
    tags = db.Column(db.String(200))  # comma-separated tags
    personalization_data = db.Column(Text)  # JSON string of personalization factors
    completion_status = db.Column(db.String(20), default='assigned')  # assigned, in_progress, completed
    effectiveness_rating = db.Column(db.Integer)  # 1-5 user rating
    completion_date = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    
    session = db.relationship('Session', backref=db.backref('exercises', lazy=True))
    
    def __repr__(self):
        return f'<Exercise {self.id}: {self.title}>'

class Patient(UserMixin, db.Model):
    """Model for patient profiles"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    emergency_contact = db.Column(db.String(200))
    medical_history = db.Column(Text)
    therapy_goals = db.Column(Text)
    consent_video_analysis = db.Column(db.Boolean, default=False)
    consent_biometric_tracking = db.Column(db.Boolean, default=False)
    consent_data_sharing = db.Column(db.Boolean, default=False)
    premium_status = db.Column(db.Boolean, default=False)
    risk_level = db.Column(db.String(20), default='low')  # low, medium, high
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    last_session = db.Column(db.DateTime)
    subscription_tier = db.Column(db.String(20), default='free')  # free, premium, enterprise
    oauth_providers = db.Column(Text)  # JSON string of linked OAuth providers
    password_hash = db.Column(db.String(255))  # For traditional login
    email_verified = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Patient {self.id}: {self.name}>'

class Assessment(db.Model):
    """Model for comprehensive AI assessments"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=True)
    assessment_type = db.Column(db.String(50), nullable=False)  # initial, follow_up, crisis, video_assessment
    text_analysis = db.Column(Text)  # JSON string of text analysis
    video_analysis = db.Column(Text)  # JSON string of video analysis
    biometric_analysis = db.Column(Text)  # JSON string of biometric analysis
    multi_modal_score = db.Column(db.Float)  # Combined analysis score
    risk_factors = db.Column(Text)  # JSON string of identified risks
    recommendations = db.Column(Text)  # JSON string of recommendations
    intervention_required = db.Column(db.Boolean, default=False)
    human_review_required = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    completed = db.Column(db.Boolean, default=True)
    
    patient = db.relationship('Patient', backref=db.backref('assessments', lazy=True))
    
    def __repr__(self):
        return f'<Assessment {self.id}: {self.assessment_type}>'

class TherapistSession(db.Model):
    """Model for premium human therapist sessions"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    therapist_name = db.Column(db.String(100), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=50)
    session_type = db.Column(db.String(50))  # video, phone, in_person
    session_notes = db.Column(Text)
    patient_feedback = db.Column(Text)
    therapist_recommendations = db.Column(Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    cost = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='pending')
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    patient = db.relationship('Patient', backref=db.backref('therapist_sessions', lazy=True))

    def __repr__(self):
        return f'<TherapistSession {self.id}: {self.patient_id} - {self.therapist_name}>'


class AdminUser(db.Model):
    """Admin users for platform management (supports super-admin)."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin')  # admin, super_admin
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.email} ({self.role})>'


class Counselor(db.Model):
    """Counselor/therapist accounts for professional portal."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Counselor {self.email}>'


class AdminAudit(db.Model):
    """Audit log for admin actions."""
    id = db.Column(db.Integer, primary_key=True)
    admin_email = db.Column(db.String(255))
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(Text)
    ip_address = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<AdminAudit {self.admin_email} {self.action}>'


class EmailVerification(db.Model):
    """Stores verification tokens for accounts."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    token = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    expires_at = db.Column(db.DateTime)


class CounselorPosition(db.Model):
    """Model for configurable counselor positions and benefits"""
    id = db.Column(db.Integer, primary_key=True)
    position_type = db.Column(db.String(50), nullable=False, unique=True)  # full_time, contract, part_time
    title = db.Column(db.String(200), nullable=False)
    salary_range_min = db.Column(db.Float)  # For salary positions
    salary_range_max = db.Column(db.Float)  # For salary positions
    hourly_rate_min = db.Column(db.Float)  # For hourly positions
    hourly_rate_max = db.Column(db.Float)  # For hourly positions
    currency = db.Column(db.String(10), default='AUD')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    updated_by = db.Column(db.String(200))  # Email of admin who made changes

    def __repr__(self):
        return f'<CounselorPosition {self.position_type}: {self.title}>'

class CounselorBenefit(db.Model):
    """Model for configurable counselor benefits"""
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('counselor_position.id'), nullable=False)
    benefit_name = db.Column(db.String(200), nullable=False)
    benefit_description = db.Column(Text)
    benefit_category = db.Column(db.String(50))  # health, professional, financial, lifestyle
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)

    position = db.relationship('CounselorPosition', backref=db.backref('benefits', lazy=True))

    def __repr__(self):
        return f'<CounselorBenefit {self.benefit_name}>'

class CounselorRequirement(db.Model):
    """Model for configurable counselor requirements"""
    id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('counselor_position.id'), nullable=False)
    requirement_text = db.Column(db.String(500), nullable=False)
    requirement_category = db.Column(db.String(50))  # education, experience, technical, legal
    is_mandatory = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)

    position = db.relationship('CounselorPosition', backref=db.backref('requirements', lazy=True))

    def __repr__(self):
        return f'<CounselorRequirement {self.requirement_text[:50]}...>'

class Professional(db.Model):
    """Model for licensed mental health professionals"""
    __tablename__ = 'professional'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Professional credentials
    license_type = db.Column(db.String(100))  # Clinical Psychologist, LMFT, LCSW, Psychiatrist
    license_number = db.Column(db.String(100))
    license_state = db.Column(db.String(100))  # State/country of licensure
    license_expiry = db.Column(db.Date)
    ahpra_registration = db.Column(db.String(100))  # For Australian professionals

    # Professional details
    phone = db.Column(db.String(20))
    specializations = db.Column(Text)  # JSON: trauma, anxiety, depression, couples, etc.
    languages = db.Column(Text)  # JSON array of languages spoken
    timezone = db.Column(db.String(50), default='Australia/Sydney')
    years_experience = db.Column(db.Integer)
    education = db.Column(Text)  # JSON: degrees, certifications
    bio = db.Column(Text)
    profile_image_url = db.Column(db.String(500))

    # Verification status
    verification_status = db.Column(db.String(50), default='pending')  # pending, verified, rejected
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.String(255))  # Admin email who verified
    rejection_reason = db.Column(Text)

    # Insurance and compliance
    insurance_provider = db.Column(db.String(200))
    insurance_policy_number = db.Column(db.String(100))
    insurance_expiry = db.Column(db.Date)
    professional_indemnity_amount = db.Column(db.Float)

    # Availability and scheduling
    availability = db.Column(Text)  # JSON: weekly schedule
    max_clients = db.Column(db.Integer, default=20)
    current_client_count = db.Column(db.Integer, default=0)
    accepts_new_clients = db.Column(db.Boolean, default=True)

    # Compensation
    hourly_rate = db.Column(db.Float)
    session_rate = db.Column(db.Float)
    platform_fee_percentage = db.Column(db.Float, default=15.0)  # Platform commission
    payment_method = db.Column(db.String(50), default='stripe')  # stripe, bank_transfer
    stripe_account_id = db.Column(db.String(255))  # Stripe Connect account

    # Performance metrics
    total_sessions = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    response_time_minutes = db.Column(db.Integer, default=0)  # Average response time
    completion_rate = db.Column(db.Float, default=100.0)  # Percentage of completed sessions

    # Status and activity
    is_active = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    onboarding_completed = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Professional {self.email} - {self.license_type}>'


class ProfessionalCredential(db.Model):
    """Model for storing and tracking professional credentials"""
    __tablename__ = 'professional_credential'
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)

    credential_type = db.Column(db.String(100), nullable=False)  # license, degree, certification, insurance
    credential_name = db.Column(db.String(200), nullable=False)
    issuing_organization = db.Column(db.String(200))
    credential_number = db.Column(db.String(100))
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)

    # Document storage
    document_url = db.Column(db.String(500))  # S3 URL or file path
    document_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.String(255))

    # Status
    status = db.Column(db.String(50), default='pending')  # pending, verified, expired, rejected
    notes = db.Column(Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    professional = db.relationship('Professional', backref=db.backref('credentials', lazy=True))

    def __repr__(self):
        return f'<ProfessionalCredential {self.credential_name} - {self.status}>'


class ProfessionalApplication(db.Model):
    """Model for professional application workflow"""
    __tablename__ = 'professional_application'
    id = db.Column(db.Integer, primary_key=True)

    # Applicant information
    email = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))

    # Application details
    position_type = db.Column(db.String(50))  # full_time, part_time, contract
    license_type = db.Column(db.String(100))
    license_number = db.Column(db.String(100))
    years_experience = db.Column(db.Integer)
    specializations = db.Column(Text)  # JSON array
    education = db.Column(Text)
    cover_letter = db.Column(Text)

    # Application status
    status = db.Column(db.String(50), default='pending')  # pending, under_review, approved, rejected
    reviewed_by = db.Column(db.String(255))  # Admin email
    reviewed_at = db.Column(db.DateTime)
    review_notes = db.Column(Text)

    # Documents submitted
    resume_url = db.Column(db.String(500))
    license_document_url = db.Column(db.String(500))
    additional_documents = db.Column(Text)  # JSON array of document URLs

    # Workflow
    interview_scheduled = db.Column(db.Boolean, default=False)
    interview_date = db.Column(db.DateTime)
    background_check_completed = db.Column(db.Boolean, default=False)
    reference_check_completed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<ProfessionalApplication {self.email} - {self.status}>'


class SessionReview(db.Model):
    """Model for professional review of AI therapy sessions"""
    __tablename__ = 'session_review'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)

    # Review details
    review_type = db.Column(db.String(50))  # routine, flagged, crisis, quality_check
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent

    # Assessment
    ai_quality_score = db.Column(db.Integer)  # 1-10 rating of AI response quality
    intervention_needed = db.Column(db.Boolean, default=False)
    risk_level = db.Column(db.String(20))  # low, medium, high, critical

    # Professional notes
    clinical_notes = db.Column(Text)  # Encrypted clinical observations
    recommendations = db.Column(Text)  # Recommendations for patient care
    action_taken = db.Column(db.String(100))  # contacted_patient, escalated, no_action, etc.

    # Follow-up
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.DateTime)
    follow_up_completed = db.Column(db.Boolean, default=False)

    # Time tracking
    review_duration_minutes = db.Column(db.Integer)
    assigned_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Status
    status = db.Column(db.String(50), default='assigned')  # assigned, in_progress, completed

    session = db.relationship('Session', backref=db.backref('reviews', lazy=True))
    professional = db.relationship('Professional', backref=db.backref('reviews', lazy=True))

    def __repr__(self):
        return f'<SessionReview {self.id} - Session {self.session_id}>'


class ProfessionalPayment(db.Model):
    """Model for tracking professional compensation"""
    __tablename__ = 'professional_payment'
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)

    # Payment period
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)

    # Earnings breakdown
    sessions_completed = db.Column(db.Integer, default=0)
    reviews_completed = db.Column(db.Integer, default=0)
    gross_earnings = db.Column(db.Float, nullable=False)
    platform_fee = db.Column(db.Float, nullable=False)
    net_earnings = db.Column(db.Float, nullable=False)

    # Payment details
    payment_method = db.Column(db.String(50))  # stripe, bank_transfer
    payment_status = db.Column(db.String(50), default='pending')  # pending, processing, paid, failed
    stripe_transfer_id = db.Column(db.String(255))

    # Invoice
    invoice_number = db.Column(db.String(100), unique=True)
    invoice_url = db.Column(db.String(500))

    # Timestamps
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    professional = db.relationship('Professional', backref=db.backref('payments', lazy=True))

    def __repr__(self):
        return f'<ProfessionalPayment {self.invoice_number} - ${self.net_earnings}>'


class ProfessionalAvailability(db.Model):
    """Model for managing professional schedules and availability"""
    __tablename__ = 'professional_availability'
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)

    # Schedule details
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Availability type
    availability_type = db.Column(db.String(50), default='regular')  # regular, one_time, recurring
    specific_date = db.Column(db.Date)  # For one-time availability

    # Status
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    professional = db.relationship('Professional', backref=db.backref('availability_slots', lazy=True))

    def __repr__(self):
        return f'<ProfessionalAvailability {self.professional_id} - Day {self.day_of_week}>'


class Subscription(db.Model):
    """Model for user subscriptions"""
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    tier = db.Column(db.String(50), nullable=False)  # free, premium, enterprise
    status = db.Column(db.String(50), default='active')  # active, canceled, expired, past_due
    start_date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    end_date = db.Column(db.DateTime)
    stripe_subscription_id = db.Column(db.String(255), unique=True)
    stripe_customer_id = db.Column(db.String(255))
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    canceled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    patient = db.relationship('Patient', backref=db.backref('subscriptions', lazy=True))

    def __repr__(self):
        return f'<Subscription {self.id}: {self.tier} - {self.status}>'

    @property
    def user_id(self):
        """Alias for patient_id for backward compatibility with admin panel"""
        return self.patient_id

    @user_id.setter
    def user_id(self, value):
        """Setter for user_id alias"""
        self.patient_id = value

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False
        if self.end_date and self.end_date < datetime.now(UTC):
            return False
        return True

class Payment(db.Model):
    """Model for payment transactions"""
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(50), nullable=False)  # pending, succeeded, failed, refunded
    payment_method = db.Column(db.String(50))  # card, apple_pay, google_pay, etc.
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)
    stripe_charge_id = db.Column(db.String(255))
    failure_reason = db.Column(db.String(500))
    refund_amount = db.Column(db.Float, default=0.0)
    refunded_at = db.Column(db.DateTime)
    payment_metadata = db.Column(Text)  # JSON string for additional data (renamed from metadata)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    patient = db.relationship('Patient', backref=db.backref('payments', lazy=True))
    subscription = db.relationship('Subscription', backref=db.backref('payments', lazy=True))

    def __repr__(self):
        return f'<Payment {self.id}: ${self.amount} - {self.status}>'

    @property
    def user_id(self):
        """Alias for patient_id for backward compatibility with admin panel"""
        return self.patient_id

    @user_id.setter
    def user_id(self, value):
        """Setter for user_id alias"""
        self.patient_id = value

    @property
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == 'succeeded'


# ============================================================================
# PHASE 4: CLINICAL INTELLIGENCE & OUTCOMES TRACKING MODELS
# ============================================================================

class ClinicalAssessment(db.Model):
    """Model for standardized clinical assessment tools (PHQ-9, GAD-7, PSS-10, etc.)"""
    __tablename__ = 'clinical_assessment'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))

    # Assessment details
    assessment_type = db.Column(db.String(50), nullable=False)  # PHQ-9, GAD-7, PSS-10, WEMWBS
    total_score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    severity_level = db.Column(db.String(50))  # minimal, mild, moderate, severe, etc.

    # Individual item responses (JSON)
    item_responses = db.Column(Text)  # JSON array of individual question scores

    # Clinical interpretation
    clinical_interpretation = db.Column(Text)
    risk_flags = db.Column(Text)  # JSON array of identified risk factors
    recommended_actions = db.Column(Text)  # JSON array of recommendations

    # Metadata
    administered_by = db.Column(db.String(100))  # self, counselor, system
    administration_method = db.Column(db.String(50))  # online, interview, paper
    is_baseline = db.Column(db.Boolean, default=False)

    # Timestamps
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    patient = db.relationship('Patient', backref=db.backref('clinical_assessments', lazy=True))
    session = db.relationship('Session', backref=db.backref('clinical_assessments', lazy=True))

    def __repr__(self):
        return f'<ClinicalAssessment {self.assessment_type}: {self.total_score}/{self.max_score}>'

    @property
    def percentage_score(self):
        """Calculate percentage score"""
        if self.max_score > 0:
            return (self.total_score / self.max_score) * 100
        return 0


class OutcomeMeasure(db.Model):
    """Model for tracking treatment outcomes and progress metrics"""
    __tablename__ = 'outcome_measure'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    # Outcome details
    outcome_type = db.Column(db.String(100), nullable=False)  # symptom_reduction, goal_achievement, functioning_improvement
    outcome_name = db.Column(db.String(200), nullable=False)
    baseline_value = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    target_value = db.Column(db.Float)
    unit_of_measure = db.Column(db.String(50))  # score, percentage, frequency, duration

    # Progress tracking
    improvement_percentage = db.Column(db.Float)
    target_achievement_percentage = db.Column(db.Float)
    trend = db.Column(db.String(20))  # improving, stable, declining

    # Time tracking
    measurement_date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    baseline_date = db.Column(db.DateTime, nullable=False)
    target_date = db.Column(db.DateTime)

    # Clinical significance
    is_clinically_significant = db.Column(db.Boolean, default=False)
    clinical_notes = db.Column(Text)

    # Metadata
    measured_by = db.Column(db.String(100))  # system, counselor, patient
    data_source = db.Column(db.String(100))  # assessment, session, biometric, self_report

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    patient = db.relationship('Patient', backref=db.backref('outcome_measures', lazy=True))

    def __repr__(self):
        return f'<OutcomeMeasure {self.outcome_name}: {self.improvement_percentage}% improvement>'

    def calculate_improvement(self):
        """Calculate improvement percentage from baseline"""
        if self.baseline_value != 0:
            self.improvement_percentage = ((self.baseline_value - self.current_value) / abs(self.baseline_value)) * 100
        else:
            self.improvement_percentage = 0

        if self.target_value:
            progress = abs(self.current_value - self.baseline_value)
            total_needed = abs(self.target_value - self.baseline_value)
            if total_needed > 0:
                self.target_achievement_percentage = (progress / total_needed) * 100


class InterventionTracking(db.Model):
    """Model for tracking AI-recommended interventions and their completion"""
    __tablename__ = 'intervention_tracking'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))

    # Intervention details
    intervention_type = db.Column(db.String(100), nullable=False)  # exercise, medication, therapy_technique, lifestyle_change
    intervention_name = db.Column(db.String(200), nullable=False)
    intervention_description = db.Column(Text)

    # AI recommendation details
    recommended_by = db.Column(db.String(100))  # ai_model_name, counselor, system
    recommendation_confidence = db.Column(db.Float)  # 0-1
    evidence_basis = db.Column(Text)  # Research citations or rationale

    # Tracking
    status = db.Column(db.String(50), default='recommended')  # recommended, accepted, in_progress, completed, declined, discontinued
    adherence_rate = db.Column(db.Float)  # 0-100 percentage
    completion_rate = db.Column(db.Float)  # 0-100 percentage

    # Effectiveness tracking
    pre_intervention_score = db.Column(db.Float)
    post_intervention_score = db.Column(db.Float)
    effectiveness_rating = db.Column(db.Integer)  # 1-5 patient rating
    clinical_effectiveness = db.Column(db.Float)  # Calculated effectiveness

    # Patient feedback
    patient_notes = db.Column(Text)
    barriers_encountered = db.Column(Text)  # JSON array of barriers
    facilitators = db.Column(Text)  # JSON array of things that helped

    # Timestamps
    recommended_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    discontinued_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    patient = db.relationship('Patient', backref=db.backref('intervention_tracking', lazy=True))
    session = db.relationship('Session', backref=db.backref('intervention_tracking', lazy=True))
    exercise = db.relationship('Exercise', backref=db.backref('intervention_tracking', lazy=True))

    def __repr__(self):
        return f'<InterventionTracking {self.intervention_name}: {self.status}>'

    def calculate_effectiveness(self):
        """Calculate intervention effectiveness"""
        if self.pre_intervention_score is not None and self.post_intervention_score is not None:
            if self.pre_intervention_score != 0:
                improvement = ((self.pre_intervention_score - self.post_intervention_score) / abs(self.pre_intervention_score)) * 100
                self.clinical_effectiveness = max(0, min(100, improvement))


class TreatmentOutcome(db.Model):
    """Model for comprehensive treatment outcome tracking"""
    __tablename__ = 'treatment_outcome'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    # Treatment period
    treatment_start_date = db.Column(db.DateTime, nullable=False)
    treatment_end_date = db.Column(db.DateTime)
    total_sessions = db.Column(db.Integer, default=0)

    # Outcome metrics
    primary_diagnosis = db.Column(db.String(200))
    treatment_modality = db.Column(db.String(100))  # CBT, DBT, mindfulness, etc.
    outcome_status = db.Column(db.String(50))  # in_progress, completed, discontinued, transferred

    # Clinical outcomes
    baseline_severity = db.Column(db.String(50))
    current_severity = db.Column(db.String(50))
    symptom_reduction_percentage = db.Column(db.Float)
    goals_achieved = db.Column(db.Integer, default=0)
    goals_total = db.Column(db.Integer, default=0)

    # Quality of life improvements
    functioning_improvement = db.Column(db.Float)  # Percentage
    wellbeing_improvement = db.Column(db.Float)  # Percentage
    quality_of_life_score = db.Column(db.Float)

    # Engagement metrics
    session_attendance_rate = db.Column(db.Float)  # Percentage
    homework_completion_rate = db.Column(db.Float)  # Percentage
    platform_engagement_score = db.Column(db.Float)  # 0-100

    # Crisis metrics
    crisis_events_prevented = db.Column(db.Integer, default=0)
    emergency_interventions = db.Column(db.Integer, default=0)
    hospitalization_prevented = db.Column(db.Boolean, default=False)

    # Patient satisfaction
    overall_satisfaction = db.Column(db.Float)  # 1-5 scale
    would_recommend = db.Column(db.Boolean)
    patient_testimonial = db.Column(Text)

    # Clinical significance
    meets_recovery_criteria = db.Column(db.Boolean, default=False)
    clinically_significant_change = db.Column(db.Boolean, default=False)
    reliable_change_index = db.Column(db.Float)

    # Follow-up
    relapse_within_3_months = db.Column(db.Boolean)
    relapse_within_6_months = db.Column(db.Boolean)
    follow_up_date = db.Column(db.DateTime)

    # Metadata
    outcome_assessed_by = db.Column(db.String(100))  # system, counselor, independent_evaluator
    assessment_date = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    patient = db.relationship('Patient', backref=db.backref('treatment_outcomes', lazy=True))

    def __repr__(self):
        return f'<TreatmentOutcome Patient {self.patient_id}: {self.outcome_status}>'

    @property
    def goal_achievement_rate(self):
        """Calculate goal achievement percentage"""
        if self.goals_total > 0:
            return (self.goals_achieved / self.goals_total) * 100
        return 0


class ClinicalTrial(db.Model):
    """Model for A/B testing and clinical trial management"""
    __tablename__ = 'clinical_trial'
    id = db.Column(db.Integer, primary_key=True)

    # Trial details
    trial_name = db.Column(db.String(200), nullable=False, unique=True)
    trial_description = db.Column(Text)
    hypothesis = db.Column(Text)
    trial_type = db.Column(db.String(50))  # ab_test, rct, cohort_study

    # Trial configuration
    control_condition = db.Column(Text)  # JSON description of control
    experimental_condition = db.Column(Text)  # JSON description of experimental
    randomization_method = db.Column(db.String(50))  # simple, stratified, block

    # Status
    status = db.Column(db.String(50), default='draft')  # draft, active, completed, paused, terminated

    # Sample size
    target_sample_size = db.Column(db.Integer)
    current_sample_size = db.Column(db.Integer, default=0)
    control_group_size = db.Column(db.Integer, default=0)
    experimental_group_size = db.Column(db.Integer, default=0)

    # Outcomes
    primary_outcome_measure = db.Column(db.String(200))
    secondary_outcome_measures = db.Column(Text)  # JSON array

    # Results
    control_mean_outcome = db.Column(db.Float)
    experimental_mean_outcome = db.Column(db.Float)
    effect_size = db.Column(db.Float)  # Cohen's d
    p_value = db.Column(db.Float)
    confidence_interval_lower = db.Column(db.Float)
    confidence_interval_upper = db.Column(db.Float)

    # Statistical significance
    is_statistically_significant = db.Column(db.Boolean)
    is_clinically_significant = db.Column(db.Boolean)

    # Ethics and compliance
    ethics_approval_number = db.Column(db.String(100))
    ethics_approval_date = db.Column(db.Date)
    consent_required = db.Column(db.Boolean, default=True)

    # Dates
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    analysis_date = db.Column(db.DateTime)

    # Research team
    principal_investigator = db.Column(db.String(200))
    research_team = db.Column(Text)  # JSON array of team members

    # Publications
    published = db.Column(db.Boolean, default=False)
    publication_reference = db.Column(Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<ClinicalTrial {self.trial_name}: {self.status}>'


class TrialParticipant(db.Model):
    """Model for tracking trial participants and group assignment"""
    __tablename__ = 'trial_participant'
    id = db.Column(db.Integer, primary_key=True)
    trial_id = db.Column(db.Integer, db.ForeignKey('clinical_trial.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    # Assignment
    group_assignment = db.Column(db.String(50))  # control, experimental
    assignment_date = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    randomization_seed = db.Column(db.String(100))  # For reproducibility

    # Consent
    consent_given = db.Column(db.Boolean, default=False)
    consent_date = db.Column(db.DateTime)
    consent_withdrawn = db.Column(db.Boolean, default=False)
    withdrawal_date = db.Column(db.DateTime)

    # Participation
    status = db.Column(db.String(50), default='enrolled')  # enrolled, active, completed, withdrawn, lost_to_followup
    baseline_completed = db.Column(db.Boolean, default=False)
    endpoint_completed = db.Column(db.Boolean, default=False)

    # Outcomes
    baseline_measure = db.Column(db.Float)
    endpoint_measure = db.Column(db.Float)
    change_score = db.Column(db.Float)

    # Blinding
    is_blinded = db.Column(db.Boolean, default=True)
    unblinding_date = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    trial = db.relationship('ClinicalTrial', backref=db.backref('participants', lazy=True))
    patient = db.relationship('Patient', backref=db.backref('trial_participations', lazy=True))

    def __repr__(self):
        return f'<TrialParticipant Trial {self.trial_id}, Patient {self.patient_id}: {self.group_assignment}>'
