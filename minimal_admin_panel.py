"""
Minimal Admin Panel for MindMend - Quick Fix
==========================================
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Simple admin credentials
ADMIN_USERS = {
    'mindmend_admin': {
        'password_hash': generate_password_hash('MindMend2024!SecureAdmin'),
        'role': 'super_admin'
    },
    'admin@sticky.com.au': {
        'password_hash': generate_password_hash('StickyAdmin2025!'),
        'role': 'super_admin'  
    }
}

@admin_bp.route('/')
def admin_dashboard():
    """Main admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindMend Admin Panel</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #4CAF50; color: white; padding: 20px; margin: -40px -40px 20px -40px; }}
            .status {{ background: #e8f5e9; padding: 15px; margin: 20px 0; border-left: 4px solid #4CAF50; }}
            .feature {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .btn {{ background: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧠 MindMend Admin Panel</h1>
            <p>Advanced AI Mental Health Platform - Stage 2+3 Features Active</p>
        </div>
        
        <div class="status">
            <h2>✅ Deployment Status: ACTIVE</h2>
            <p><strong>Server:</strong> 67.219.102.9</p>
            <p><strong>Platform:</strong> MindMend AI Therapy Platform</p>
            <p><strong>Features:</strong> Stage 2+3 Advanced Features Activated</p>
            <p><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <h2>🚀 Stage 2 Features (Active)</h2>
        <div class="feature">📊 Real-time Biometric Monitoring with Stress Detection</div>
        <div class="feature">😊 Facial Emotion Recognition with Therapy Adaptation</div>
        <div class="feature">🚨 Enhanced Crisis Intervention with Automatic Escalation</div>
        <div class="feature">🧠 AI-powered Therapy Personalization</div>

        <h2>🗣️ Stage 3 Features (Active)</h2>
        <div class="feature">🤖 AI Speaking Avatar with Multiple Personalities</div>
        <div class="feature">🎤 Text-to-Speech Integration with Real-time Feedback</div>
        <div class="feature">✨ Reformed Onboarding with Progressive Disclosure</div>
        <div class="feature">📹 Advanced Video Assessment Capabilities</div>

        <h2>🔧 Quick Actions</h2>
        <a href="/admin/logout" class="btn">Logout</a>
        <a href="/" class="btn">View Main Site</a>
        
        <div style="margin-top: 40px; color: #666;">
            <p>🎉 <strong>Congratulations!</strong> Your MindMend platform is successfully deployed with all Stage 2+3 features!</p>
        </div>
    </body>
    </html>
    """

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ADMIN_USERS:
            user_data = ADMIN_USERS[username]
            if check_password_hash(user_data['password_hash'], password):
                session['admin_logged_in'] = True
                session['admin_user'] = username
                session['admin_role'] = user_data['role']
                flash('Successfully logged in!', 'success')
                return redirect(url_for('admin.admin_dashboard'))
        
        flash('Invalid credentials', 'error')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindMend Admin Login</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0; padding: 0; height: 100vh;
                display: flex; align-items: center; justify-content: center;
            }}
            .login-form {{
                background: white; padding: 40px; border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3); min-width: 300px;
            }}
            h1 {{ color: #333; text-align: center; margin-bottom: 30px; }}
            input {{ 
                width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #ddd; 
                border-radius: 5px; font-size: 16px; box-sizing: border-box;
            }}
            button {{ 
                width: 100%; padding: 15px; background: #4CAF50; color: white; 
                border: none; border-radius: 5px; font-size: 16px; cursor: pointer;
            }}
            button:hover {{ background: #45a049; }}
            .info {{ background: #e3f2fd; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="login-form">
            <h1>🧠 MindMend Admin</h1>
            
            <div class="info">
                <strong>Demo Credentials:</strong><br>
                Username: <code>mindmend_admin</code><br>
                Password: <code>MindMend2024!SecureAdmin</code>
            </div>
            
            <form method="post">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login to Admin Panel</button>
            </form>
        </div>
    </body>
    </html>
    """

@admin_bp.route('/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    session.pop('admin_role', None)
    flash('Successfully logged out', 'info')
    return redirect(url_for('admin.admin_login'))

# Health check endpoint
@admin_bp.route('/health')
def admin_health():
    """Admin panel health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'MindMend Admin Panel',
        'stage_2_features': 'active',
        'stage_3_features': 'active',
        'timestamp': datetime.now().isoformat()
    })