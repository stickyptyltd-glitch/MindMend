#!/usr/bin/env python3
"""
Setup production environment for MindMend deployment
"""

import secrets
import string
import bcrypt
from datetime import datetime

def generate_secret_key(length=64):
    """Generate a secure random string"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password):
    """Generate bcrypt hash of password"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def main():
    print("🔐 Setting up MindMend Production Environment")
    print("=" * 50)
    
    # Generate secure secrets
    flask_secret = generate_secret_key()
    session_secret = generate_secret_key()
    admin_secret = generate_secret_key()
    jwt_secret = generate_secret_key()
    mobile_jwt_secret = generate_secret_key()
    postgres_password = generate_secret_key(32)
    redis_password = generate_secret_key(32)
    
    print("✅ Generated secure random secrets")
    
    # Default admin credentials (CHANGE THESE!)
    admin_username = "mindmend_admin"
    admin_password = "MindMend2024!SecureAdmin"  # Strong default password
    admin_password_hash = hash_password(admin_password)
    
    print("✅ Generated admin credentials")
    print(f"   Default Username: {admin_username}")
    print(f"   Default Password: {admin_password}")
    print("   ⚠️  CHANGE THESE AFTER FIRST LOGIN!")
    
    # Generate .env.production file
    env_content = f"""# MindMend Production Environment Configuration
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# ⚠️  IMPORTANT: Update API keys and credentials before deployment!

# Flask Configuration
FLASK_ENV=production
SECRET_KEY={flask_secret}
SESSION_SECRET={session_secret}

# Database Configuration
POSTGRES_PASSWORD={postgres_password}
DATABASE_URL=postgresql://mindmend_user:{postgres_password}@postgres:5432/mindmend_production
SQLALCHEMY_DATABASE_URI=${{DATABASE_URL}}

# Redis Configuration
REDIS_PASSWORD={redis_password}

# Domain Configuration
DOMAIN=mindmend.xyz
SERVER_NAME=mindmend.xyz
PREFERRED_URL_SCHEME=https

# AI Model Configuration
# ⚠️  REPLACE WITH YOUR ACTUAL OPENAI API KEY
OPENAI_API_KEY=sk-your-openai-api-key-here
HUGGINGFACE_API_KEY=hf_your-huggingface-token-here
OLLAMA_HOST=http://ollama:11434

# Payment Processing  
# ⚠️  REPLACE WITH YOUR ACTUAL STRIPE KEYS
STRIPE_SECRET_KEY=sk_live_your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-publishable-key
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
PAYPAL_MODE=live

# Admin Security Configuration
SUPER_ADMIN_ID={admin_username}
SUPER_ADMIN_PASSWORD_HASH={admin_password_hash}
ADMIN_SECRET_KEY={admin_secret}
JWT_SECRET_KEY={jwt_secret}
MOBILE_JWT_SECRET={mobile_jwt_secret}
# ADMIN_IP_WHITELIST=your.ip.address/32,office.ip.address/32

# Email Configuration
# ⚠️  REPLACE WITH YOUR ACTUAL EMAIL CREDENTIALS
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=sticky.pty.ltd@gmail.com
MAIL_PASSWORD=your-gmail-app-password-here
ALERT_RECIPIENTS=sticky.pty.ltd@gmail.com

# Business Configuration
COMPANY_NAME="Sticky Pty Ltd"
COMPANY_EMAIL=sticky.pty.ltd@gmail.com
COMPANY_ADDRESS="Suite 329/98-100 Elizabeth Street, Melbourne, VIC, 3000"

# Performance Configuration
WORKERS=4
WORKER_CONNECTIONS=1000
MAX_REQUESTS=10000
TIMEOUT=120

# Security Configuration
FORCE_HTTPS=true
HSTS_MAX_AGE=31536000
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900

# Rate Limiting
RATE_LIMIT_STORAGE_URL=redis://:{redis_password}@redis:6379/0

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/var/www/mindmend/uploads

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/mindmend/app.log
ERROR_LOG=/var/log/mindmend/error.log
"""
    
    # Write .env.production file
    with open('.env.production', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Generated .env.production file")
    
    # Create credentials file for reference
    creds_content = f"""# MindMend Admin Credentials
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Admin Panel URL: https://admin.mindmend.xyz
Username: {admin_username}  
Password: {admin_password}

Database Password: {postgres_password}
Redis Password: {redis_password}

⚠️  IMPORTANT SECURITY NOTES:
1. Change admin password after first login
2. Add your IP to ADMIN_IP_WHITELIST in .env.production
3. Update all API keys with your actual values
4. Set up proper SSL certificates
5. Configure email credentials for alerts

🔑 Required API Keys to Update:
- OpenAI API Key (for AI models)
- Stripe Keys (for payments)
- Gmail App Password (for email alerts)
- PayPal Credentials (optional)
"""
    
    with open('ADMIN_CREDENTIALS.txt', 'w') as f:
        f.write(creds_content)
    
    print("✅ Saved admin credentials to ADMIN_CREDENTIALS.txt")
    
    print("\n🚀 Next Steps:")
    print("1. Edit .env.production with your actual API keys")
    print("2. Copy all files to your server")
    print("3. Run: sudo ./scripts/server-setup.sh")
    print("4. Run: ./scripts/deploy.sh")
    print("5. Access admin panel and change default password")

if __name__ == "__main__":
    main()