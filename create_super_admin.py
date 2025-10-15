#!/usr/bin/env python3
"""
Create Super Admin Account
===========================
Creates a super admin account for the MindMend platform owner
"""

import sys
from app import app, db
from models.database import AdminUser
from werkzeug.security import generate_password_hash

def create_super_admin():
    """Create super admin account"""

    with app.app_context():
        # Check if super admin already exists
        existing = AdminUser.query.filter_by(role='super_admin').first()
        if existing:
            print(f"⚠️  Super admin already exists: {existing.email}")
            response = input("Do you want to create another super admin? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled.")
                return

        print("=" * 60)
        print("MindMend Super Admin Account Creation")
        print("=" * 60)
        print()

        # Get admin details
        email = input("Email address: ").strip().lower()
        if not email:
            print("❌ Email is required")
            return

        # Check if email already exists
        existing_email = AdminUser.query.filter_by(email=email).first()
        if existing_email:
            print(f"❌ Email {email} already exists with role: {existing_email.role}")
            return

        name = input("Full name: ").strip()
        if not name:
            print("❌ Name is required")
            return

        password = input("Password (min 8 characters): ").strip()
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            return

        password_confirm = input("Confirm password: ").strip()
        if password != password_confirm:
            print("❌ Passwords do not match")
            return

        print()
        print("Creating super admin account...")

        # Create admin user
        admin = AdminUser(
            email=email,
            name=name,
            role='super_admin',
            is_active=True,
            email_verified=True  # Auto-verify for super admin
        )
        admin.set_password(password)

        try:
            db.session.add(admin)
            db.session.commit()

            print()
            print("✅ Super admin account created successfully!")
            print()
            print("=" * 60)
            print("SUPER ADMIN CREDENTIALS")
            print("=" * 60)
            print(f"Email: {email}")
            print(f"Password: {password}")
            print(f"Role: super_admin")
            print(f"Permissions: ALL (wildcard '*')")
            print()
            print("Admin Panel: http://34.143.177.214/admin/login")
            print()
            print("⚠️  IMPORTANT: Store these credentials securely!")
            print("=" * 60)

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin: {e}")
            sys.exit(1)

if __name__ == '__main__':
    create_super_admin()
