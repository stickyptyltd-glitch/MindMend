"""
Counselor Dashboard and Employment System
========================================
Human counselor management, scheduling, and monetization
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from datetime import datetime, timedelta
import uuid

counselor_bp = Blueprint('counselor', __name__, url_prefix='/counselor')


class CounselorManager:

    def __init__(self):
        self.counselors = {}  # In production, use database
        self.sessions = {}
        self.employment_applications = {}

    def register_counselor(self, counselor_data):
        """Register a new counselor"""
        counselor_id = str(uuid.uuid4())
        self.counselors[counselor_id] = {
            'id': counselor_id,
            'name': counselor_data['name'],
            'email': counselor_data['email'],
            'phone': counselor_data['phone'],
            'license_number': counselor_data['license_number'],
            'specializations': counselor_data['specializations'],
            'experience_years': counselor_data['experience_years'],
            'education': counselor_data['education'],
            'languages': counselor_data.get('languages', ['English']),
            'timezone': counselor_data.get('timezone', 'Australia/Sydney'),
            'availability': counselor_data.get('availability', {}),
            'rate_per_hour': counselor_data.get('rate_per_hour', 120),
            'bio': counselor_data.get('bio', ''),
            'profile_image': counselor_data.get('profile_image', ''),
            'verified': False,
            'active': False,
            'rating': 0.0,
            'total_sessions': 0,
            'created_at': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat()
        }
        return counselor_id

    def get_counselor_earnings(self, counselor_id, period='month'):
        """Calculate counselor earnings"""
        # In production, query database for actual session data
        base_earnings = {
            'week': 840,  # 7 sessions × $120
            'month': 3600,  # 30 sessions × $120
            'year': 43200  # 360 sessions × $120
        }

        return {
            'period': period,
            'gross_earnings': base_earnings.get(period, 0),
            'platform_fee':
            base_earnings.get(period, 0) * 0.15,  # 15% platform fee
            'net_earnings': base_earnings.get(period, 0) * 0.85,
            'sessions_completed': {
                'week': 7,
                'month': 30,
                'year': 360
            }.get(period, 0),
            'average_rating': 4.8,
            'next_payout': (datetime.utcnow() + timedelta(days=7)).isoformat()
        }


counselor_manager = CounselorManager()


@counselor_bp.route('/dashboard')
def dashboard():
    """Main counselor dashboard"""
    counselor_id = session.get('counselor_id')
    if not counselor_id:
        return redirect(url_for('counselor.login'))

    # Get counselor data and stats
    earnings = counselor_manager.get_counselor_earnings(counselor_id)

    dashboard_data = {
        'counselor':
        counselor_manager.counselors.get(counselor_id, {}),
        'earnings':
        earnings,
        'upcoming_sessions': [{
            'id':
            'sess_001',
            'client_name':
            'Client A',
            'session_type':
            'Individual Therapy',
            'scheduled_time':
            (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'duration':
            60,
            'fee':
            120
        }, {
            'id':
            'sess_002',
            'client_name':
            'Client B',
            'session_type':
            'Couples Therapy',
            'scheduled_time':
            (datetime.utcnow() + timedelta(hours=4)).isoformat(),
            'duration':
            90,
            'fee':
            180
        }],
        'recent_sessions': [{
            'id':
            'sess_completed_001',
            'client_name':
            'Client C',
            'session_type':
            'Individual Therapy',
            'completed_time':
            (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            'duration':
            60,
            'fee':
            120,
            'rating':
            5,
            'notes':
            'Great progress on anxiety management'
        }],
        'performance_metrics': {
            'client_satisfaction': 4.8,
            'session_completion_rate': 98.5,
            'response_time': '< 2 hours',
            'professional_development_hours': 12
        }
    }

    return render_template('counselor/dashboard.html', data=dashboard_data)


@counselor_bp.route('/employment')
def employment_opportunities():
    """Employment opportunities for counselors"""
    return render_template(
        'counselor/employment.html',
        opportunities={
            'full_time': {
                'title':
                'Senior Mental Health Counselor',
                'salary':
                '$85,000 - $110,000 AUD',
                'benefits': [
                    'Health insurance', 'Professional development allowance',
                    'Flexible working arrangements', 'Equipment provided',
                    '4 weeks annual leave'
                ],
                'requirements': [
                    'Masters in Psychology/Counseling',
                    'Current AHPRA registration',
                    '3+ years clinical experience',
                    'Telehealth experience preferred'
                ]
            },
            'contract': {
                'title':
                'Contract Therapist',
                'rate':
                '$100-150 AUD per hour',
                'benefits': [
                    'Flexible schedule', 'Platform support',
                    'Client matching service', 'Payment processing included'
                ],
                'requirements': [
                    'Valid counseling license',
                    'Professional indemnity insurance',
                    'Reliable internet connection', 'Quiet, professional space'
                ]
            },
            'part_time': {
                'title':
                'Part-Time Crisis Counselor',
                'rate':
                '$45-55 AUD per hour',
                'benefits': [
                    'Crisis intervention training provided',
                    '24/7 supervisor support', 'Continuing education credits',
                    'Employee assistance program'
                ],
                'requirements': [
                    'Crisis counseling certification',
                    'Available for weekend/evening shifts',
                    'Experience with high-risk clients',
                    'Strong emotional resilience'
                ]
            }
        })


@counselor_bp.route('/apply', methods=['GET', 'POST'])
def apply():
    """Apply for counselor position"""
    if request.method == 'POST':
        application_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'position': request.form.get('position'),
            'license_number': request.form.get('license_number'),
            'experience_years': int(request.form.get('experience_years', 0)),
            'specializations': request.form.getlist('specializations'),
            'education': request.form.get('education'),
            'cover_letter': request.form.get('cover_letter'),
            'availability': request.form.get('availability'),
            'resume_uploaded': request.files.get('resume') is not None,
            'submitted_at': datetime.utcnow().isoformat()
        }

        application_id = str(uuid.uuid4())
        counselor_manager.employment_applications[
            application_id] = application_data

        flash(
            'Application submitted successfully! We will review and contact you within 48 hours.',
            'success')
        return redirect(
            url_for('counselor.application_confirmation',
                    app_id=application_id))

    return render_template('counselor/apply.html')


@counselor_bp.route('/application-confirmation/<app_id>')
def application_confirmation(app_id):
    """Application confirmation page"""
    application = counselor_manager.employment_applications.get(app_id)
    if not application:
        flash('Application not found.', 'error')
        return redirect(url_for('counselor.employment_opportunities'))

    return render_template('counselor/confirmation.html',
                           application=application)


@counselor_bp.route('/schedule')
def schedule():
    """Counselor scheduling interface"""
    return render_template('counselor/schedule.html')


@counselor_bp.route('/clients')
def client_management():
    """Client management interface"""
    return render_template('counselor/clients.html')


@counselor_bp.route('/earnings')
def earnings():
    """Detailed earnings and payout information"""
    counselor_id = session.get('counselor_id', 'demo_counselor')

    earnings_data = {
        'current_month':
        counselor_manager.get_counselor_earnings(counselor_id, 'month'),
        'current_week':
        counselor_manager.get_counselor_earnings(counselor_id, 'week'),
        'yearly_total':
        counselor_manager.get_counselor_earnings(counselor_id, 'year'),
        'payout_history': [
            {
                'date': '2025-07-01',
                'amount': 3060,  # $3600 - 15% platform fee
                'status': 'Paid',
                'sessions': 30
            },
            {
                'date': '2025-06-01',
                'amount': 2805,
                'status': 'Paid',
                'sessions': 27
            }
        ],
        'tax_documents': [{
            'year': 2024,
            'document': '1099-NEC',
            'available': True,
            'download_url': '/counselor/tax-doc/2024'
        }]
    }

    return render_template('counselor/earnings.html', data=earnings_data)


@counselor_bp.route('/api/session-notes', methods=['POST'])
def save_session_notes():
    """Save session notes"""
    data = request.get_json()
    session_id = data.get('session_id')
    notes = data.get('notes')
    counselor_id = session.get('counselor_id')

    # In production, save to database with encryption
    session_notes = {
        'session_id': session_id,
        'counselor_id': counselor_id,
        'notes': notes,
        'timestamp': datetime.utcnow().isoformat(),
        'encrypted': True
    }

    return jsonify({
        'success': True,
        'message': 'Session notes saved securely',
        'note_id': str(uuid.uuid4())
    })


@counselor_bp.route('/api/availability', methods=['POST'])
def update_availability():
    """Update counselor availability"""
    data = request.get_json()
    counselor_id = session.get('counselor_id')

    if counselor_id and counselor_id in counselor_manager.counselors:
        counselor_manager.counselors[counselor_id]['availability'] = data.get(
            'availability', {})
        counselor_manager.counselors[counselor_id][
            'last_updated'] = datetime.utcnow().isoformat()

        return jsonify({
            'success': True,
            'message': 'Availability updated successfully'
        })

    return jsonify({'success': False, 'error': 'Counselor not found'}), 404


@counselor_bp.route('/training')
@counselor_bp.route('/professional-development')
def professional_development():
    """Professional development and training resources"""
    training_data = {
        'required_courses': [{
            'title': 'Digital Therapy Best Practices',
            'duration': '4 hours',
            'deadline': '2025-03-01',
            'completed': False,
            'credits': 4
        }, {
            'title': 'Crisis Intervention Online',
            'duration': '6 hours',
            'deadline': '2025-04-15',
            'completed': True,
            'credits': 6
        }],
        'available_courses': [{
            'title': 'Advanced CBT Techniques',
            'duration': '8 hours',
            'cost': 'Free for employees',
            'credits': 8,
            'provider': 'Mind Mend Academy'
        }, {
            'title': 'Trauma-Informed Care',
            'duration': '12 hours',
            'cost': 'Free for employees',
            'credits': 12,
            'provider': 'Australian Psychological Society'
        }],
        'continuing_education': {
            'required_hours_per_year': 20,
            'completed_this_year': 12,
            'remaining': 8,
            'deadline': '2025-12-31'
        }
    }

    return render_template('counselor/training.html', data=training_data)


@counselor_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Counselor login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # In production, verify against database
        # For demo, accept any email ending with @mindmend.com.au
        if email and email.endswith('@mindmend.com.au'):
            session['counselor_id'] = 'demo_counselor'
            session['counselor_email'] = email
            flash('Logged in successfully', 'success')
            return redirect(url_for('counselor.dashboard'))
        else:
            flash('Invalid credentials or not authorized', 'error')

    return render_template('counselor/login.html')


@counselor_bp.route('/logout')
def logout():
    """Counselor logout"""
    session.pop('counselor_id', None)
    session.pop('counselor_email', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('counselor.login'))
