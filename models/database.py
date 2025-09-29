from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import UserMixin

class Base(DeclarativeBase):
    pass

# Create the SQLAlchemy instance here to avoid circular imports
db = SQLAlchemy(model_class=Base)
from datetime import datetime
from sqlalchemy import Text
from werkzeug.security import generate_password_hash, check_password_hash

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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_session = db.Column(db.DateTime)
    subscription_tier = db.Column(db.String(20), default='free')  # free, premium, enterprise
    oauth_providers = db.Column(Text)  # JSON string of linked OAuth providers
    password_hash = db.Column(db.String(255))  # For traditional login
    
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AdminAudit {self.admin_email} {self.action}>'

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
