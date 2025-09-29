#!/usr/bin/env python3
"""
Generate secure secrets for MindMend deployment
"""

import secrets
import string
import bcrypt
import getpass

def generate_secret_key(length=64):
    """Generate a secure random string"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password):
    """Generate bcrypt hash of password"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def main():
    print("🔐 MindMend Secret Generation Tool")
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
    
    # Get admin password
    print("\n👤 Admin Account Setup")
    admin_username = input("Enter admin username: ").strip()
    if not admin_username:
        admin_username = "admin"
    
    while True:
        admin_password = getpass.getpass("Enter admin password: ")
        admin_password_confirm = getpass.getpass("Confirm admin password: ")
        
        if admin_password == admin_password_confirm:
            if len(admin_password) >= 12:
                break
            else:
                print("❌ Password must be at least 12 characters long")
        else:
            print("❌ Passwords don't match")
    
    admin_password_hash = hash_password(admin_password)
    print("✅ Generated admin password hash")
    
    # Get IP address for whitelist
    print("\n🌐 Security Configuration")
    user_ip = input("Enter your IP address for admin whitelist (or press Enter to skip): ").strip()
    
    # Generate .env file
    env_content = f"""# MindMend Production Environment Configuration
# Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

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

# AI Model Configuration (REPLACE WITH YOUR ACTUAL KEYS)
OPENAI_API_KEY=sk-your-openai-api-key-here
HUGGINGFACE_API_KEY=hf_your-huggingface-token-here
OLLAMA_HOST=http://ollama:11434

# Payment Processing (REPLACE WITH YOUR ACTUAL KEYS)
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
MOBILE_JWT_SECRET={mobile_jwt_secret}"""

    if user_ip:
        env_content += f"\nADMIN_IP_WHITELIST={user_ip}/32"
    
    env_content += """

# Email Configuration (REPLACE WITH YOUR ACTUAL CREDENTIALS)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
ALERT_RECIPIENTS=alerts@yourdomain.com

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
    
    # Write .env file
    with open('.env.production', 'w') as f:
        f.write(env_content)
    
    print("\n✅ Generated .env.production file")
    print("\n⚠️  IMPORTANT: Edit .env.production and add your actual:")
    print("   - OpenAI API key")
    print("   - Stripe keys")
    print("   - Email credentials")
    print("   - PayPal credentials (if using)")
    print("\n🔐 Your admin credentials:")
    print(f"   Username: {admin_username}")
    print(f"   Password: {admin_password}")
    print("\n💡 Save these credentials securely - you'll need them to access the admin panel!")

if __name__ == "__main__":
    main()