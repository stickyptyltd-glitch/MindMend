#!/usr/bin/env python3
"""
Create MindMend Super Admin Account
Run this script to create a super admin user for the MindMend platform
"""

import sys
import os
sys.path.append('/var/www/mindmend')
sys.path.append('.')

try:
    from app import app, db
    from models.database import Patient
    from werkzeug.security import generate_password_hash

    print("🔐 Creating MindMend Super Admin Account")
    print("=" * 40)

    with app.app_context():
        try:
            # Ensure database tables exist
            db.create_all()
            print("✅ Database tables verified")

            # Check if admin already exists
            existing_admin = Patient.query.filter_by(email='admin@mindmend.xyz').first()
            if existing_admin:
                print("⚠️  Admin account already exists!")
                print("📧 Email: admin@mindmend.xyz")
                print("🔓 Try logging in with your existing password")

                # Update password anyway
                existing_admin.password_hash = generate_password_hash('MindMend2024!')
                existing_admin.is_admin = True
                existing_admin.role = 'super_admin'
                db.session.commit()
                print("✅ Password updated to: MindMend2024!")

            else:
                # Create new super admin
                admin = Patient(
                    email='admin@mindmend.xyz',
                    password_hash=generate_password_hash('MindMend2024!'),
                    is_admin=True,
                    role='super_admin',
                    first_name='Super',
                    last_name='Admin',
                    subscription_tier='enterprise'
                )

                db.session.add(admin)
                db.session.commit()
                print("✅ Super admin created successfully!")

            print("\n🎯 LOGIN CREDENTIALS:")
            print("=" * 25)
            print("URL: http://mindmend.xyz/admin")
            print("Email: admin@mindmend.xyz")
            print("Password: MindMend2024!")
            print("Role: Super Admin")
            print("\n🚀 You can now access the full admin panel!")

        except Exception as db_error:
            print(f"❌ Database error: {db_error}")
            print("🔧 Attempting to fix database...")

            # Try to create tables and admin again
            try:
                db.create_all()
                admin = Patient(
                    email='admin@mindmend.xyz',
                    password_hash=generate_password_hash('MindMend2024!'),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin created after database fix!")
                print("📧 Email: admin@mindmend.xyz")
                print("🔓 Password: MindMend2024!")
            except Exception as fix_error:
                print(f"❌ Could not fix database: {fix_error}")
                sys.exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Make sure you're running this from the MindMend directory")
    print("📂 Try: cd /var/www/mindmend && python create_admin.py")
    sys.exit(1)

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

print("\n✅ Admin creation completed!")