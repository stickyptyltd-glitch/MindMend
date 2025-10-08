
import sys
sys.path.append('/var/www/mindmend')
sys.path.append('.')

from app import app, db
from models.database import Patient
from werkzeug.security import generate_password_hash

with app.app_context():
    email = 'superadmin@mindmend.xyz'
    password = 'superadmin123'
    
    existing_admin = Patient.query.filter_by(email=email).first()
    if not existing_admin:
        admin_user = Patient(
            name='Super Admin',
            email=email,
            password_hash=generate_password_hash(password),
            subscription_tier='enterprise'
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user {email} created successfully.")
    else:
        print(f"Admin user {email} already exists.")

# Verify user creation
with app.app_context():
    print("--- Verifying User --- ")
    user = Patient.query.filter_by(email='superadmin@mindmend.xyz').first()
    if user:
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Subscription Tier: {user.subscription_tier}")
        print("-------------------------")
    else:
        print("Verification failed: User not found.")
