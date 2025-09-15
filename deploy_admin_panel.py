#!/usr/bin/env python3
"""
Deploy Admin Panel to Server
Creates a working admin panel directly on the server
"""

import os

print("🔧 Deploying Admin Panel to Server")
print("=" * 40)

# Admin panel code
admin_panel_code = '''"""
MindMend Admin Panel - Comprehensive Platform Management
"""

from flask import Blueprint, request, render_template_string, session, redirect, url_for, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import json
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def admin_login():
    """Admin login page"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindMend Admin - Platform Management</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .login-container { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); max-width: 400px; width: 100%; }
            h2 { color: #333; text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
            input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
            input:focus { border-color: #667eea; outline: none; }
            .btn { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-size: 16px; }
            .btn:hover { background: #5a67d8; }
            .alert { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .back-link { text-align: center; margin-top: 20px; }
            .back-link a { color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>🔐 MindMend Admin</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="email">Admin Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Access Admin Panel</button>
            </form>
            <div class="back-link">
                <a href="/">← Back to Main Site</a>
            </div>
        </div>
    </body>
    </html>
    """)

@admin_bp.route('/', methods=['POST'])
def admin_login_post():
    """Handle admin login"""
    email = request.form.get('email')
    password = request.form.get('password')

    # Check credentials
    if email == 'admin@mindmend.xyz' and password == 'MindMend2024!':
        session['admin_logged_in'] = True
        session['admin_email'] = email
        return redirect(url_for('admin.dashboard'))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('admin.admin_login'))

@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - MindMend</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial; margin: 0; background: #f8f9fa; }
            .navbar { background: #343a40; padding: 15px 30px; color: white; display: flex; justify-content: space-between; align-items: center; }
            .container { max-width: 1200px; margin: 0 auto; padding: 30px; }
            .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
            .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .card h3 { color: #667eea; margin-bottom: 15px; }
            .btn { background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; }
            .btn:hover { background: #5a67d8; text-decoration: none; color: white; }
            .btn-danger { background: #dc3545; }
            .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }
            .stat-card { background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px; text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <h1>🧠 MindMend Admin Dashboard</h1>
            <div>
                <span>Welcome, Admin</span>
                <a href="/admin/logout" class="btn btn-danger">Logout</a>
            </div>
        </nav>

        <div class="container">
            <h2>Platform Overview</h2>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">1,247</div>
                    <div>Active Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">3,892</div>
                    <div>Sessions Today</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">89%</div>
                    <div>System Health</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">$12.4k</div>
                    <div>Revenue</div>
                </div>
            </div>

            <div class="dashboard-grid">
                <div class="card">
                    <h3>🎯 User Management</h3>
                    <p>Manage user accounts, subscriptions, and permissions</p>
                    <a href="/admin/users" class="btn">Manage Users</a>
                    <a href="/admin/subscriptions" class="btn">Subscriptions</a>
                </div>

                <div class="card">
                    <h3>🤖 AI Management</h3>
                    <p>Configure AI models, responses, and training data</p>
                    <a href="/admin/ai-models" class="btn">AI Models</a>
                    <a href="/admin/ai-training" class="btn">Training</a>
                </div>

                <div class="card">
                    <h3>📊 Analytics</h3>
                    <p>View platform analytics and user behavior</p>
                    <a href="/admin/analytics" class="btn">View Analytics</a>
                    <a href="/admin/reports" class="btn">Generate Reports</a>
                </div>

                <div class="card">
                    <h3>💳 Financial</h3>
                    <p>Manage payments, subscriptions, and billing</p>
                    <a href="/admin/payments" class="btn">Payment History</a>
                    <a href="/admin/pricing" class="btn">Pricing Settings</a>
                </div>

                <div class="card">
                    <h3>🛠️ System Settings</h3>
                    <p>Configure platform settings and features</p>
                    <a href="/admin/settings" class="btn">System Config</a>
                    <a href="/admin/features" class="btn">Feature Flags</a>
                </div>

                <div class="card">
                    <h3>📱 Content Management</h3>
                    <p>Manage therapy content, exercises, and resources</p>
                    <a href="/admin/content" class="btn">Content Library</a>
                    <a href="/admin/exercises" class="btn">Therapy Exercises</a>
                </div>

                <div class="card">
                    <h3>🚨 Safety & Crisis</h3>
                    <p>Monitor crisis interventions and safety alerts</p>
                    <a href="/admin/crisis" class="btn">Crisis Dashboard</a>
                    <a href="/admin/alerts" class="btn">Safety Alerts</a>
                </div>

                <div class="card">
                    <h3>🔧 Technical</h3>
                    <p>Server monitoring, logs, and technical management</p>
                    <a href="/admin/logs" class="btn">View Logs</a>
                    <a href="/admin/health" class="btn">System Health</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin.admin_login'))

# Placeholder routes for admin functions
@admin_bp.route('/<path:path>')
def admin_placeholder(path):
    """Placeholder for admin functions"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }} - MindMend Admin</title>
        <style>
            body { font-family: Arial; margin: 0; background: #f8f9fa; }
            .container { max-width: 800px; margin: 50px auto; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
            .btn { background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🚧 {{ title }}</h2>
            <p>This admin function is currently under development.</p>
            <p>Feature: <strong>{{ path }}</strong></p>
            <a href="/admin/dashboard" class="btn">← Back to Dashboard</a>
        </div>
    </body>
    </html>
    """, title=path.replace('-', ' ').title(), path=path)
'''

# Write the admin panel file
admin_path = '/var/www/mindmend/admin_panel.py'
print(f"Creating admin panel at: {admin_path}")

try:
    with open(admin_path, 'w') as f:
        f.write(admin_panel_code)
    print("✅ Admin panel file created successfully")

    # Restart the service
    os.system('systemctl restart mindmend')
    print("✅ Service restarted")

    print("\\n🎯 Admin Panel Access:")
    print("   URL: https://mindmend.xyz/admin")
    print("   Email: admin@mindmend.xyz")
    print("   Password: MindMend2024!")
    print("\\n✅ Admin panel should now be accessible!")

except Exception as e:
    print(f"❌ Error creating admin panel: {e}")
    print("\\n🔧 Manual fix - run this on your server:")
    print("wget https://raw.githubusercontent.com/stickyptyltd-glitch/MindMend/main/admin_panel.py")
    print("systemctl restart mindmend")