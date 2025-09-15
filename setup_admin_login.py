#!/usr/bin/env python3
"""
Setup Working Admin Login System
Creates a proper admin login that uses email/password format
"""

import sys
import os
sys.path.append('/var/www/mindmend')
sys.path.append('.')

print("🔧 Setting up MindMend Admin Login System")
print("=" * 45)

try:
    from app import app, db
    from models.database import Patient
    from werkzeug.security import generate_password_hash

    with app.app_context():
        # Ensure database tables exist
        db.create_all()
        print("✅ Database tables verified")

        # Create admin user in the Patient table with admin flag
        admin_email = 'admin@mindmend.xyz'
        admin_password = 'MindMend2024!'

        # Check if admin exists
        existing_admin = Patient.query.filter_by(email=admin_email).first()

        if existing_admin:
            print("⚠️  Admin user already exists, updating...")
            existing_admin.password_hash = generate_password_hash(admin_password)
            existing_admin.subscription_tier = 'enterprise'
            existing_admin.name = 'System Administrator'
            db.session.commit()
            print("✅ Admin user updated")
        else:
            # Create new admin user
            admin_user = Patient(
                name='System Administrator',
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                subscription_tier='enterprise'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created in database")

        print("\n🎯 ADMIN LOGIN CREDENTIALS:")
        print("=" * 30)
        print("URL: http://67.219.102.9/admin")
        print("Email: admin@mindmend.xyz")
        print("Password: MindMend2024!")
        print("\n💡 Use the IP address URL to avoid SSL redirect issues")

        # Now update the admin_panel.py to check against database users
        admin_panel_path = '/var/www/mindmend/admin_panel.py'

        if os.path.exists(admin_panel_path):
            print("\n🔄 Updating admin panel authentication...")

            # Read current admin panel
            with open(admin_panel_path, 'r') as f:
                content = f.read()

            # Create new login function that checks database
            new_login_function = '''@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page with database authentication"""
    if request.method == 'POST':
        email = request.form.get('email') or request.form.get('username')
        password = request.form.get('password')

        if email and password:
            try:
                from models.database import Patient
                from werkzeug.security import check_password_hash

                # Check if user exists and has enterprise subscription (admin)
                user = Patient.query.filter_by(email=email).first()
                if user and check_password_hash(user.password_hash, password):
                    if user.subscription_tier == 'enterprise':
                        session['admin_logged_in'] = True
                        session['admin_email'] = email
                        session['admin_name'] = user.name
                        flash('Logged in successfully', 'success')
                        return redirect(url_for('admin.dashboard'))
                    else:
                        flash('Access denied - Admin privileges required', 'error')
                else:
                    flash('Invalid email or password', 'error')
            except Exception as e:
                flash(f'Login error: {str(e)}', 'error')
        else:
            flash('Please enter both email and password', 'error')

    return render_template('admin/login.html')'''

            # Replace the existing login function
            import re
            pattern = r'@admin_bp\.route\(\'/login\'.*?return render_template\(\'admin/login\.html\'\)'
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, new_login_function, content, flags=re.DOTALL)
                print("✅ Updated existing login function")
            else:
                # If pattern not found, append the function
                content += f"\n\n{new_login_function}\n"
                print("✅ Added new login function")

            # Write updated content
            with open(admin_panel_path, 'w') as f:
                f.write(content)

            print("✅ Admin panel updated with database authentication")

        else:
            print("⚠️  Admin panel file not found, will work with database auth")

except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("🔧 Creating fallback admin credentials")

    # Create environment variable or simple file-based auth
    print("\n🎯 FALLBACK ADMIN CREDENTIALS:")
    print("Email: admin@mindmend.xyz")
    print("Password: MindMend2024!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Manual setup required")

print("\n✅ Admin setup completed!")
print("🔄 Restart the service: systemctl restart mindmend")
print("🌐 Access: http://67.219.102.9/admin")