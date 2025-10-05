"""
HIPAA-Compliant Audit Logging System
====================================
Tracks all administrative actions, data access, and security events
"""
import json
import hashlib
from datetime import datetime
from sqlalchemy import Index
from models.database import db

class AuditLog(db.Model):
    """HIPAA-compliant audit log for all admin and system actions"""

    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)

    # Event Information
    event_type = db.Column(db.String(100), nullable=False)  # LOGIN, DATA_ACCESS, MODIFY_USER, etc.
    event_category = db.Column(db.String(50), nullable=False)  # AUTHENTICATION, DATA_ACCESS, SYSTEM, etc.
    severity = db.Column(db.String(20), default='INFO')  # INFO, WARNING, ERROR, CRITICAL

    # User Information
    admin_user_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    admin_username = db.Column(db.String(200))
    admin_role = db.Column(db.String(50))

    # Target Information (what was accessed/modified)
    target_type = db.Column(db.String(50))  # USER, SESSION, PAYMENT, etc.
    target_id = db.Column(db.String(100))  # ID of the target object
    target_name = db.Column(db.String(200))  # Human-readable name

    # Technical Details
    ip_address = db.Column(db.String(45))  # IPv4/IPv6 address
    user_agent = db.Column(db.Text)
    request_method = db.Column(db.String(10))
    request_url = db.Column(db.String(500))

    # Event Details
    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text)  # JSON string with additional details

    # Data Protection
    phi_accessed = db.Column(db.Boolean, default=False)  # Protected Health Information flag
    data_hash = db.Column(db.String(64))  # Hash of sensitive data for integrity

    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Status
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)

    # Retention
    retention_date = db.Column(db.DateTime)  # When this log can be archived/deleted

    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_user', 'admin_user_id'),
        Index('idx_audit_event_type', 'event_type'),
        Index('idx_audit_target', 'target_type', 'target_id'),
        Index('idx_audit_phi', 'phi_accessed'),
    )

    def __init__(self, event_type, description, **kwargs):
        self.event_type = event_type
        self.description = description

        # Set defaults
        self.event_category = kwargs.get('event_category', self._get_category_from_type(event_type))
        self.severity = kwargs.get('severity', 'INFO')
        self.admin_user_id = kwargs.get('admin_user_id')
        self.admin_username = kwargs.get('admin_username')
        self.admin_role = kwargs.get('admin_role')
        self.target_type = kwargs.get('target_type')
        self.target_id = kwargs.get('target_id')
        self.target_name = kwargs.get('target_name')
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
        self.request_method = kwargs.get('request_method')
        self.request_url = kwargs.get('request_url')
        self.phi_accessed = kwargs.get('phi_accessed', False)
        self.success = kwargs.get('success', True)
        self.error_message = kwargs.get('error_message')

        # Handle details
        details_dict = kwargs.get('details', {})
        if details_dict:
            self.details = json.dumps(details_dict, default=str)
            # Create hash for data integrity
            self.data_hash = hashlib.sha256(self.details.encode()).hexdigest()

    @staticmethod
    def _get_category_from_type(event_type):
        """Auto-determine category from event type"""
        auth_events = ['LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'MFA_SETUP', 'MFA_SUCCESS', 'MFA_FAILED']
        data_events = ['DATA_ACCESS', 'DATA_MODIFY', 'DATA_DELETE', 'DATA_EXPORT']
        system_events = ['SYSTEM_RESTART', 'BACKUP_CREATED', 'CONFIG_CHANGED']

        if event_type in auth_events:
            return 'AUTHENTICATION'
        elif event_type in data_events:
            return 'DATA_ACCESS'
        elif event_type in system_events:
            return 'SYSTEM'
        else:
            return 'OTHER'

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'event_category': self.event_category,
            'severity': self.severity,
            'admin_username': self.admin_username,
            'admin_role': self.admin_role,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'target_name': self.target_name,
            'ip_address': self.ip_address,
            'description': self.description,
            'phi_accessed': self.phi_accessed,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'success': self.success,
            'details': json.loads(self.details) if self.details else {}
        }

class AuditLogger:
    """HIPAA-compliant audit logger"""

    @staticmethod
    def log_event(event_type, description, **kwargs):
        """
        Log an audit event

        Args:
            event_type (str): Type of event (LOGIN, DATA_ACCESS, etc.)
            description (str): Human-readable description
            **kwargs: Additional event details
        """
        try:
            audit_log = AuditLog(
                event_type=event_type,
                description=description,
                **kwargs
            )

            db.session.add(audit_log)
            db.session.commit()

            return audit_log.id

        except Exception as e:
            # Critical: audit logging must never fail silently
            db.session.rollback()
            # Log to system logger as backup
            import logging
            logging.error(f"AUDIT_LOG_FAILED: {e} - Event: {event_type} - {description}")
            raise

    @staticmethod
    def log_admin_action(action, description, target_type=None, target_id=None, **kwargs):
        """Log administrative action with session context"""
        from flask import session, request

        # Get admin context from session
        admin_details = {
            'admin_user_id': session.get('admin_user_id'),
            'admin_username': session.get('admin_username'),
            'admin_role': session.get('admin_role'),
            'ip_address': AuditLogger._get_client_ip(),
            'user_agent': request.headers.get('User-Agent', '') if request else '',
            'request_method': request.method if request else '',
            'request_url': request.url if request else '',
            'target_type': target_type,
            'target_id': str(target_id) if target_id else None,
        }

        # Merge with provided kwargs
        admin_details.update(kwargs)

        return AuditLogger.log_event(action, description, **admin_details)

    @staticmethod
    def log_phi_access(patient_id, patient_name, access_type, description, **kwargs):
        """Log access to Protected Health Information"""
        phi_details = {
            'target_type': 'PATIENT',
            'target_id': str(patient_id),
            'target_name': patient_name,
            'phi_accessed': True,
            'severity': 'WARNING' if access_type == 'READ' else 'CRITICAL',
        }

        phi_details.update(kwargs)

        return AuditLogger.log_admin_action(
            f'PHI_{access_type}',
            description,
            **phi_details
        )

    @staticmethod
    def log_security_event(event_type, description, severity='WARNING', **kwargs):
        """Log security-related events"""
        security_details = {
            'event_category': 'SECURITY',
            'severity': severity,
        }

        security_details.update(kwargs)

        return AuditLogger.log_admin_action(event_type, description, **security_details)

    @staticmethod
    def _get_client_ip():
        """Get real client IP address"""
        from flask import request

        if not request:
            return None

        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        return request.remote_addr

    @staticmethod
    def get_audit_logs(limit=100, offset=0, filters=None):
        """Retrieve audit logs with filtering"""
        query = AuditLog.query

        if filters:
            if 'event_type' in filters:
                query = query.filter(AuditLog.event_type == filters['event_type'])

            if 'event_category' in filters:
                query = query.filter(AuditLog.event_category == filters['event_category'])

            if 'admin_user_id' in filters:
                query = query.filter(AuditLog.admin_user_id == filters['admin_user_id'])

            if 'severity' in filters:
                query = query.filter(AuditLog.severity == filters['severity'])

            if 'phi_accessed' in filters:
                query = query.filter(AuditLog.phi_accessed == filters['phi_accessed'])

            if 'start_date' in filters:
                query = query.filter(AuditLog.timestamp >= filters['start_date'])

            if 'end_date' in filters:
                query = query.filter(AuditLog.timestamp <= filters['end_date'])

        return query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def generate_audit_report(start_date, end_date, format='json'):
        """Generate HIPAA audit report for specified date range"""
        logs = AuditLog.query.filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).order_by(AuditLog.timestamp.desc()).all()

        if format == 'json':
            return {
                'report_generated': datetime.utcnow().isoformat(),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_events': len(logs),
                'phi_access_events': sum(1 for log in logs if log.phi_accessed),
                'security_events': sum(1 for log in logs if log.event_category == 'SECURITY'),
                'failed_events': sum(1 for log in logs if not log.success),
                'events': [log.to_dict() for log in logs]
            }

        # Additional formats (CSV, PDF) can be added here
        return logs

# Initialize audit logger instance
audit_logger = AuditLogger()