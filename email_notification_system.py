#!/usr/bin/env python3

"""
MindMend Email Notification System
Complete email automation for early access campaign
"""

import json
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify, render_template_string
import os
import logging
from email_templates import EmailTemplates, EmailSender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegistrationDatabase:
    """
    SQLite database for managing early access registrations
    """

    def __init__(self, db_path="mindmend_registrations.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the registration database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT,
                interest TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                welcome_email_sent BOOLEAN DEFAULT FALSE,
                launch_email_sent BOOLEAN DEFAULT FALSE,
                beta_invite_sent BOOLEAN DEFAULT FALSE,
                last_contact TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                recipient_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                campaign_data TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                campaign_id INTEGER,
                email_type TEXT,
                sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error_message TEXT,
                FOREIGN KEY (campaign_id) REFERENCES email_campaigns (id)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def add_registration(self, user_data):
        """Add new registration to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO registrations (full_name, email, role, interest)
                VALUES (?, ?, ?, ?)
            ''', (
                user_data.get('fullName', ''),
                user_data.get('email', ''),
                user_data.get('role', ''),
                user_data.get('interest', '')
            ))

            registration_id = cursor.lastrowid
            conn.commit()
            logger.info(f"New registration added: {user_data.get('email')} (ID: {registration_id})")
            return {"success": True, "id": registration_id}

        except sqlite3.IntegrityError:
            logger.warning(f"Duplicate registration attempt: {user_data.get('email')}")
            return {"success": False, "error": "Email already registered"}

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return {"success": False, "error": str(e)}

        finally:
            conn.close()

    def get_all_registrations(self):
        """Get all registrations from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM registrations ORDER BY registration_date DESC')
        registrations = cursor.fetchall()
        conn.close()

        # Convert to list of dictionaries
        columns = ['id', 'full_name', 'email', 'role', 'interest', 'registration_date',
                  'welcome_email_sent', 'launch_email_sent', 'beta_invite_sent',
                  'last_contact', 'status']

        return [dict(zip(columns, reg)) for reg in registrations]

    def mark_email_sent(self, email, email_type):
        """Mark specific email type as sent for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        column_map = {
            'welcome': 'welcome_email_sent',
            'launch': 'launch_email_sent',
            'beta': 'beta_invite_sent'
        }

        if email_type in column_map:
            cursor.execute(f'''
                UPDATE registrations
                SET {column_map[email_type]} = TRUE, last_contact = CURRENT_TIMESTAMP
                WHERE email = ?
            ''', (email,))
            conn.commit()

        conn.close()

class MindMendEmailSystem:
    """
    Complete email automation system for MindMend platform
    """

    def __init__(self, smtp_config=None):
        self.db = RegistrationDatabase()
        self.templates = EmailTemplates()

        # Default SMTP configuration (update with your credentials)
        self.smtp_config = smtp_config or {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'mindmend.platform@gmail.com',  # Update this
            'sender_password': 'your_app_password_here',     # Update this
            'sender_name': 'MindMend Platform'
        }

        self.email_sender = EmailSender(
            self.smtp_config['smtp_server'],
            self.smtp_config['smtp_port'],
            self.smtp_config['sender_email'],
            self.smtp_config['sender_password']
        )

    def process_new_registration(self, user_data):
        """Process new registration and send welcome email"""
        # Add to database
        result = self.db.add_registration(user_data)

        if result['success']:
            # Send welcome email
            email_result = self.send_welcome_email(user_data)

            if email_result['success']:
                self.db.mark_email_sent(user_data['email'], 'welcome')
                logger.info(f"Welcome email sent to {user_data['email']}")
            else:
                logger.error(f"Failed to send welcome email to {user_data['email']}: {email_result.get('error')}")

            return {
                'success': True,
                'registration_id': result['id'],
                'email_sent': email_result['success']
            }

        return result

    def send_welcome_email(self, user_data):
        """Send welcome email to new registrant"""
        try:
            template = self.templates.welcome_registration_email(
                user_data.get('fullName', ''),
                user_data.get('email', ''),
                user_data.get('role', ''),
                user_data.get('interest', '')
            )

            return self.email_sender.send_email(
                user_data['email'],
                "🧠 Welcome to the MindMend Revolution - You're In!",
                template
            )

        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return {"success": False, "error": str(e)}

    def send_launch_announcement_campaign(self):
        """Send launch announcement to all registered users"""
        registrations = self.db.get_all_registrations()
        launched_users = []
        failed_users = []

        for user in registrations:
            if not user['launch_email_sent'] and user['status'] == 'active':
                user_data = {
                    'fullName': user['full_name'],
                    'email': user['email']
                }

                template = self.templates.launch_announcement_email(user_data['fullName'])
                result = self.email_sender.send_email(
                    user['email'],
                    "🚀 MindMend is LIVE! Your Early Access Awaits",
                    template
                )

                if result['success']:
                    self.db.mark_email_sent(user['email'], 'launch')
                    launched_users.append(user['email'])
                    logger.info(f"Launch email sent to {user['email']}")
                else:
                    failed_users.append({'email': user['email'], 'error': result.get('error')})
                    logger.error(f"Failed to send launch email to {user['email']}")

        return {
            'success': True,
            'total_sent': len(launched_users),
            'failed_count': len(failed_users),
            'launched_users': launched_users,
            'failed_users': failed_users
        }

    def send_beta_invitations(self, max_invites=50):
        """Send beta testing invitations to early registrants"""
        registrations = self.db.get_all_registrations()
        beta_invites = []
        failed_invites = []
        invite_count = 0

        for user in registrations:
            if (not user['beta_invite_sent'] and
                user['status'] == 'active' and
                invite_count < max_invites):

                template = self.templates.beta_testing_invite_email(
                    user['full_name'],
                    "https://beta.mindmend.xyz/join"
                )

                result = self.email_sender.send_email(
                    user['email'],
                    "🧪 Exclusive: Beta Test MindMend Before Anyone Else!",
                    template
                )

                if result['success']:
                    self.db.mark_email_sent(user['email'], 'beta')
                    beta_invites.append(user['email'])
                    invite_count += 1
                    logger.info(f"Beta invite sent to {user['email']}")
                else:
                    failed_invites.append({'email': user['email'], 'error': result.get('error')})
                    logger.error(f"Failed to send beta invite to {user['email']}")

        return {
            'success': True,
            'total_sent': len(beta_invites),
            'failed_count': len(failed_invites),
            'beta_invites': beta_invites,
            'failed_invites': failed_invites
        }

    def send_progress_updates(self, week_number=1):
        """Send weekly progress updates to all users"""
        registrations = self.db.get_all_registrations()
        updated_users = []
        failed_updates = []

        for user in registrations:
            if user['status'] == 'active':
                template = self.templates.progress_update_email(
                    user['full_name'],
                    week_number
                )

                result = self.email_sender.send_email(
                    user['email'],
                    f"📊 MindMend Development Update - Week {week_number}",
                    template
                )

                if result['success']:
                    updated_users.append(user['email'])
                    logger.info(f"Progress update sent to {user['email']}")
                else:
                    failed_updates.append({'email': user['email'], 'error': result.get('error')})
                    logger.error(f"Failed to send progress update to {user['email']}")

        return {
            'success': True,
            'total_sent': len(updated_users),
            'failed_count': len(failed_updates),
            'updated_users': updated_users,
            'failed_updates': failed_updates
        }

    def get_campaign_statistics(self):
        """Get comprehensive campaign statistics"""
        registrations = self.db.get_all_registrations()

        total_registrations = len(registrations)
        active_users = len([u for u in registrations if u['status'] == 'active'])
        welcome_emails_sent = len([u for u in registrations if u['welcome_email_sent']])
        launch_emails_sent = len([u for u in registrations if u['launch_email_sent']])
        beta_invites_sent = len([u for u in registrations if u['beta_invite_sent']])

        # Role distribution
        role_stats = {}
        interest_stats = {}

        for user in registrations:
            role = user['role'] or 'not_specified'
            interest = user['interest'] or 'not_specified'

            role_stats[role] = role_stats.get(role, 0) + 1
            interest_stats[interest] = interest_stats.get(interest, 0) + 1

        return {
            'total_registrations': total_registrations,
            'active_users': active_users,
            'email_stats': {
                'welcome_emails_sent': welcome_emails_sent,
                'launch_emails_sent': launch_emails_sent,
                'beta_invites_sent': beta_invites_sent
            },
            'demographics': {
                'roles': role_stats,
                'interests': interest_stats
            },
            'recent_registrations': registrations[:10]  # Last 10 registrations
        }

# Flask web application for managing the email system
app = Flask(__name__)
email_system = MindMendEmailSystem()

@app.route('/api/register', methods=['POST'])
def register_user():
    """API endpoint for user registration"""
    user_data = request.get_json()

    required_fields = ['fullName', 'email']
    if not all(field in user_data for field in required_fields):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    result = email_system.process_new_registration(user_data)
    return jsonify(result)

@app.route('/api/admin/send-launch-campaign', methods=['POST'])
def send_launch_campaign():
    """Send launch announcement to all users"""
    result = email_system.send_launch_announcement_campaign()
    return jsonify(result)

@app.route('/api/admin/send-beta-invites', methods=['POST'])
def send_beta_invites():
    """Send beta testing invitations"""
    max_invites = request.json.get('max_invites', 50) if request.json else 50
    result = email_system.send_beta_invitations(max_invites)
    return jsonify(result)

@app.route('/api/admin/send-progress-update', methods=['POST'])
def send_progress_update():
    """Send weekly progress update"""
    week_number = request.json.get('week_number', 1) if request.json else 1
    result = email_system.send_progress_updates(week_number)
    return jsonify(result)

@app.route('/api/admin/statistics')
def get_statistics():
    """Get campaign statistics"""
    stats = email_system.get_campaign_statistics()
    return jsonify(stats)

@app.route('/api/admin/registrations')
def get_registrations():
    """Get all registrations"""
    registrations = email_system.db.get_all_registrations()
    return jsonify(registrations)

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard for email campaign management"""
    dashboard_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindMend Email Campaign Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .card { background: #f8f9fa; padding: 20px; margin: 10px 0; border-radius: 8px; }
            .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            .btn:hover { background: #0056b3; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .stat-item { background: white; padding: 15px; border-radius: 8px; text-align: center; }
        </style>
    </head>
    <body>
        <h1>🧠 MindMend Email Campaign Dashboard</h1>

        <div class="card">
            <h2>📊 Quick Stats</h2>
            <div class="stats" id="stats">
                <div class="stat-item">
                    <h3 id="totalRegistrations">-</h3>
                    <p>Total Registrations</p>
                </div>
                <div class="stat-item">
                    <h3 id="welcomeEmails">-</h3>
                    <p>Welcome Emails Sent</p>
                </div>
                <div class="stat-item">
                    <h3 id="launchEmails">-</h3>
                    <p>Launch Emails Sent</p>
                </div>
                <div class="stat-item">
                    <h3 id="betaInvites">-</h3>
                    <p>Beta Invites Sent</p>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📧 Campaign Actions</h2>
            <button class="btn" onclick="sendLaunchCampaign()">🚀 Send Launch Campaign</button>
            <button class="btn" onclick="sendBetaInvites()">🧪 Send Beta Invites (50)</button>
            <button class="btn" onclick="sendProgressUpdate()">📊 Send Progress Update</button>
            <button class="btn" onclick="exportRegistrations()">📥 Export Registrations</button>
        </div>

        <div class="card">
            <h2>👥 Recent Registrations</h2>
            <div id="recentRegistrations"></div>
        </div>

        <script>
            async function loadStats() {
                const response = await fetch('/api/admin/statistics');
                const stats = await response.json();

                document.getElementById('totalRegistrations').textContent = stats.total_registrations;
                document.getElementById('welcomeEmails').textContent = stats.email_stats.welcome_emails_sent;
                document.getElementById('launchEmails').textContent = stats.email_stats.launch_emails_sent;
                document.getElementById('betaInvites').textContent = stats.email_stats.beta_invites_sent;

                const recentDiv = document.getElementById('recentRegistrations');
                recentDiv.innerHTML = stats.recent_registrations.map(reg =>
                    `<p><strong>${reg.full_name}</strong> (${reg.email}) - ${reg.role || 'No role'} - ${reg.registration_date}</p>`
                ).join('');
            }

            async function sendLaunchCampaign() {
                if (!confirm('Send launch announcement to all registered users?')) return;

                const response = await fetch('/api/admin/send-launch-campaign', {method: 'POST'});
                const result = await response.json();

                alert(`Launch campaign sent! Success: ${result.total_sent}, Failed: ${result.failed_count}`);
                loadStats();
            }

            async function sendBetaInvites() {
                if (!confirm('Send beta invitations to eligible users?')) return;

                const response = await fetch('/api/admin/send-beta-invites', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({max_invites: 50})
                });
                const result = await response.json();

                alert(`Beta invites sent! Success: ${result.total_sent}, Failed: ${result.failed_count}`);
                loadStats();
            }

            async function sendProgressUpdate() {
                const week = prompt('Which week number?', '1');
                if (!week) return;

                const response = await fetch('/api/admin/send-progress-update', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({week_number: parseInt(week)})
                });
                const result = await response.json();

                alert(`Progress update sent! Success: ${result.total_sent}, Failed: ${result.failed_count}`);
            }

            async function exportRegistrations() {
                const response = await fetch('/api/admin/registrations');
                const registrations = await response.json();

                const csv = [
                    ['Name', 'Email', 'Role', 'Interest', 'Registration Date'],
                    ...registrations.map(reg => [
                        reg.full_name, reg.email, reg.role || '',
                        reg.interest || '', reg.registration_date
                    ])
                ].map(row => row.join(',')).join('\\n');

                const blob = new Blob([csv], {type: 'text/csv'});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'mindmend_registrations.csv';
                a.click();
            }

            // Load stats on page load
            loadStats();

            // Refresh stats every 30 seconds
            setInterval(loadStats, 30000);
        </script>
    </body>
    </html>
    '''
    return render_template_string(dashboard_html)

if __name__ == '__main__':
    print("🧠 MindMend Email Notification System")
    print("=" * 50)
    print(f"📊 Admin Dashboard: http://localhost:5001/admin/dashboard")
    print(f"📧 Registration API: POST /api/register")
    print(f"🚀 Launch Campaign: POST /api/admin/send-launch-campaign")
    print(f"🧪 Beta Invites: POST /api/admin/send-beta-invites")
    print(f"📈 Statistics API: GET /api/admin/statistics")
    print("=" * 50)
    print("⚠️  Remember to update SMTP credentials in smtp_config!")
    print("📝 Update sender_email and sender_password before sending emails")

    app.run(host='0.0.0.0', port=5001, debug=True)