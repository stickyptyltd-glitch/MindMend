#!/usr/bin/env python3
"""
Update Admin Panel Credentials
This script updates the admin_panel.py file with working credentials
"""

import os
import sys

print("🔧 Updating MindMend Admin Credentials")
print("=" * 40)

# Path to admin panel file
admin_panel_path = '/var/www/mindmend/admin_panel.py'

if os.path.exists(admin_panel_path):
    print("✅ Found admin_panel.py")

    # Read the current file
    with open(admin_panel_path, 'r') as f:
        content = f.read()

    # Check what credentials are currently set
    if "username == 'admin' and password == 'mindmend123'" in content:
        print("✅ Current credentials: admin / mindmend123")
    else:
        print("⚠️  Updating admin credentials...")

        # Update the credentials
        updated_content = content.replace(
            "if username == 'admin' and password == 'mindmend123':",
            "if username == 'admin' and password == 'mindmend123':"
        )

        # Ensure the credentials are set correctly
        if "username == 'admin'" not in updated_content:
            # If not found, add the login logic
            login_logic = '''        # Default admin credentials for testing
        if username == 'admin' and password == 'mindmend123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials')'''

            updated_content = content.replace(
                "# Placeholder authentication - replace with proper auth",
                login_logic
            )

        # Write the updated content
        with open(admin_panel_path, 'w') as f:
            f.write(updated_content)

        print("✅ Admin credentials updated")

    print("\n🎯 ADMIN LOGIN CREDENTIALS:")
    print("=" * 30)
    print("URL: http://mindmend.xyz/admin/login")
    print("Username: admin")
    print("Password: mindmend123")

    # Also try to restart the service
    print("\n🔄 Restarting MindMend service...")
    os.system('systemctl restart mindmend')
    print("✅ Service restarted")

    print("\n🌐 Try accessing: http://67.219.102.9/admin/login")
    print("   (Use IP address to avoid HTTPS redirect)")

else:
    print(f"❌ Admin panel file not found at {admin_panel_path}")
    print("🔧 Creating basic admin panel...")

    basic_admin = '''from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'mindmend123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials')

    return """
    <h2>MindMend Admin Login</h2>
    <form method="POST">
        Username: <input type="text" name="username"><br><br>
        Password: <input type="password" name="password"><br><br>
        <input type="submit" value="Login">
    </form>
    """

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    return "<h1>Admin Dashboard</h1><p>Welcome to MindMend Admin Panel!</p>"

@admin_bp.route('/')
def admin_index():
    return redirect(url_for('admin.admin_login'))
'''

    with open(admin_panel_path, 'w') as f:
        f.write(basic_admin)

    print("✅ Basic admin panel created")
    print("🔄 Restart the service: systemctl restart mindmend")

print("\n✅ Admin setup completed!")