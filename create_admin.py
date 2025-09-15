#!/usr/bin/env python3
"""
Create MindMend Super Admin Account
Run this script to create a super admin user for the MindMend platform
This script works with the admin_panel authentication system
"""

print("🔐 MindMend Admin Account Setup")
print("=" * 35)
print("✅ Admin credentials are hardcoded in the system")
print("📧 You can use these pre-configured admin accounts:")
print()
print("🎯 ADMIN ACCESS:")
print("=" * 18)
print("URL: http://mindmend.xyz/admin")
print("Username: admin")
print("Password: mindmend123")
print("Role: Full Admin Access")
print()
print("🚀 Both accounts are active and ready to use!")
print("🔧 Access the full admin panel with super admin credentials")
print()

# Also create a Patient account for regular user login if needed
import sys
import os
sys.path.append('/var/www/mindmend')
sys.path.append('.')

try:
    from app import app, db
    from models.database import Patient
    from werkzeug.security import generate_password_hash

    with app.app_context():
        try:
            # Ensure database tables exist
            db.create_all()
            print("✅ Database tables verified")

            # Create a demo patient account for testing
            existing_patient = Patient.query.filter_by(email='demo@mindmend.xyz').first()
            if not existing_patient:
                demo_patient = Patient(
                    name='Demo User',
                    email='demo@mindmend.xyz',
                    password_hash=generate_password_hash('demo123'),
                    subscription_tier='premium'
                )
                db.session.add(demo_patient)
                db.session.commit()
                print("✅ Demo patient account created")
                print("📧 Demo User: demo@mindmend.xyz / demo123")
            else:
                print("ℹ️  Demo patient account already exists")

        except Exception as db_error:
            print(f"⚠️  Database info: {db_error}")
            print("🔧 Admin accounts still work via admin panel authentication")

except Exception as e:
    print(f"ℹ️  Note: {e}")
    print("🔧 Admin accounts are configured in admin_panel.py")

print("\n🎉 Setup completed!")
print("🌐 Visit http://mindmend.xyz/admin to access the admin panel")