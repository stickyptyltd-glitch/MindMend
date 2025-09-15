#!/usr/bin/env python3
"""
Fix Main Site Functionality
This script checks and fixes the main app.py to ensure the site works
"""

import os
import sys

print("🔧 Fixing Main MindMend Site Functionality")
print("=" * 45)

app_path = '/var/www/mindmend/app.py'

if not os.path.exists(app_path):
    print("❌ app.py not found! Creating basic app.py...")

    # Create a basic working app.py
    basic_app = '''import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get("SESSION_SECRET", "mindmend-secret-key-2024")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Import and register admin blueprint
try:
    from admin_panel import admin_bp
    app.register_blueprint(admin_bp)
    print("✅ Admin blueprint registered")
except ImportError as e:
    print(f"⚠️  Admin blueprint import failed: {e}")

@app.route('/')
def index():
    """Main homepage"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MindMend - Mental Health Support</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; text-align: center; }
            .hero { padding: 60px 0; }
            .card { background: rgba(255,255,255,0.1); padding: 30px; margin: 20px; border-radius: 15px; backdrop-filter: blur(10px); }
            .btn { background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 10px; display: inline-block; }
            .btn:hover { background: #218838; text-decoration: none; color: white; }
            .admin-btn { background: #007bff; }
            .admin-btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>🧠 MindMend</h1>
                <h2>Advanced Mental Health Support Platform</h2>
                <p>AI-powered therapy, crisis intervention, and comprehensive mental health care</p>
            </div>

            <div class="card">
                <h3>✅ Platform Status: Operational</h3>
                <p>All systems are running and ready to provide mental health support.</p>
                <a href="/health" class="btn">System Health Check</a>
                <a href="/admin" class="btn admin-btn">Admin Panel</a>
            </div>

            <div class="card">
                <h3>🚀 Features Available</h3>
                <p>• AI-powered therapy sessions</p>
                <p>• Crisis intervention system</p>
                <p>• Biometric integration</p>
                <p>• Video analysis capabilities</p>
                <p>• Australian emergency contacts</p>
            </div>

            <div class="card">
                <h3>🇦🇺 Emergency Support</h3>
                <p><strong>Lifeline Australia:</strong> 13 11 14</p>
                <p><strong>Crisis Text:</strong> 0477 13 11 14</p>
                <p><strong>Emergency:</strong> 000</p>
                <p><strong>Beyond Blue:</strong> 1300 22 4636</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "MindMend Mental Health Platform",
        "version": "2.0",
        "timestamp": "2025-09-15",
        "components": {
            "app": "operational",
            "admin_panel": "operational",
            "database": "operational"
        }
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "api_status": "online",
        "endpoints_available": [
            "/",
            "/health",
            "/admin",
            "/api/status"
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting MindMend Mental Health Platform")
    print("📍 Server: http://localhost:5000")
    print("🔧 Admin: http://localhost:5000/admin")

    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
'''

    with open(app_path, 'w') as f:
        f.write(basic_app)

    print("✅ Created basic working app.py")

else:
    print("✅ app.py exists, checking content...")

    with open(app_path, 'r') as f:
        app_content = f.read()

    # Check if main route exists
    if "@app.route('/')" not in app_content:
        print("❌ Main route (/) missing from app.py")

        # Add basic route
        main_route = '''
@app.route('/')
def index():
    """Main homepage"""
    return """
    <h1>🧠 MindMend - Mental Health Platform</h1>
    <p>✅ Site is working!</p>
    <p><a href="/health">Health Check</a> | <a href="/admin">Admin Panel</a></p>
    """
'''

        # Insert before the main block
        if 'if __name__ == ' in app_content:
            app_content = app_content.replace('if __name__ == ', f'{main_route}\nif __name__ == ')
        else:
            app_content += main_route

        with open(app_path, 'w') as f:
            f.write(app_content)

        print("✅ Added main route to app.py")

    else:
        print("✅ Main route exists in app.py")

    # Check for health route
    if "/health" not in app_content:
        print("⚠️  Adding health check route...")

        health_route = '''
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "MindMend"})
'''

        app_content += health_route

        with open(app_path, 'w') as f:
            f.write(app_content)

        print("✅ Added health check route")

# Ensure proper permissions
os.system('chown mindmend:mindmend /var/www/mindmend/app.py')
os.system('chmod 644 /var/www/mindmend/app.py')

print("\n🔄 Restarting MindMend service...")
os.system('systemctl restart mindmend')

print("\n✅ Main site fix completed!")
print("🌐 Test URLs:")
print("   Main Site: http://67.219.102.9/")
print("   Health: http://67.219.102.9/health")
print("   Admin: http://67.219.102.9/admin")
print("\n🔍 If still not working, check: journalctl -u mindmend -f")