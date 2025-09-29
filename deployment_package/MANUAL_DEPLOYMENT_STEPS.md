# 👨‍💻 Manual Deployment Instructions for MindMend

## 🎯 **WHEN TO USE MANUAL DEPLOYMENT**
- Automated scripts fail or not accessible
- Need step-by-step control over deployment
- Troubleshooting specific issues
- Learning the deployment process

---

## 📋 **COMPLETE MANUAL DEPLOYMENT GUIDE**

### **PART 1: SERVER ACCESS & SETUP**

#### **1.1 Connect to Server**
```bash
# Try different connection methods
ssh root@45.32.244.187
ssh ubuntu@45.32.244.187
ssh -i /path/to/key root@45.32.244.187

# If connection fails, use cloud provider console
# DigitalOcean: Console access in droplet dashboard
# AWS: EC2 Instance Connect or Session Manager
# Vultr/Linode: Web console access
```

#### **1.2 System Update**
```bash
# Update system packages (run as root)
apt update && apt upgrade -y
```

#### **1.3 Install Required Packages**
```bash
# Install essential packages
apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-pip \
    python3.11-dev \
    build-essential \
    nginx \
    postgresql \
    postgresql-contrib \
    redis-server \
    git \
    curl \
    wget \
    unzip \
    ufw \
    certbot \
    python3-certbot-nginx
```

#### **1.4 Configure Services**
```bash
# Enable and start services
systemctl enable nginx
systemctl enable postgresql  
systemctl enable redis-server
systemctl start nginx
systemctl start postgresql
systemctl start redis-server

# Verify services are running
systemctl status nginx postgresql redis-server
```

#### **1.5 Configure Firewall**
```bash
# Configure UFW firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Verify firewall status
ufw status
```

### **PART 2: USER & DIRECTORY SETUP**

#### **2.1 Create MindMend User**
```bash
# Create system user for MindMend
useradd -m -s /bin/bash mindmend
usermod -aG sudo mindmend  # Optional: give sudo access
```

#### **2.2 Create Directories**
```bash
# Create application directories
mkdir -p /var/www/mindmend
mkdir -p /var/log/mindmend
mkdir -p /var/www/mindmend/uploads
mkdir -p /etc/mindmend

# Set ownership
chown -R mindmend:mindmend /var/www/mindmend
chown -R mindmend:mindmend /var/log/mindmend
chmod 755 /var/www/mindmend
chmod 755 /var/log/mindmend
```

### **PART 3: DATABASE SETUP**

#### **3.1 Configure PostgreSQL**
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user (in PostgreSQL shell)
CREATE USER mindmend_user WITH PASSWORD 'aLo0aPR>{#Rp6{SKpx0,dPyRd9$+:-d>';
CREATE DATABASE mindmend_production OWNER mindmend_user;
GRANT ALL PRIVILEGES ON DATABASE mindmend_production TO mindmend_user;
\q

# Test database connection
sudo -u mindmend psql -h localhost -U mindmend_user -d mindmend_production -c "SELECT version();"
```

### **PART 4: APPLICATION DEPLOYMENT**

#### **4.1 Upload Application Files**
```bash
# From your local machine, upload files
scp -r app.py root@45.32.244.187:/var/www/mindmend/
scp -r models/ root@45.32.244.187:/var/www/mindmend/
scp -r templates/ root@45.32.244.187:/var/www/mindmend/
scp -r static/ root@45.32.244.187:/var/www/mindmend/
scp requirements.txt root@45.32.244.187:/var/www/mindmend/
scp .env.production root@45.32.244.187:/var/www/mindmend/

# Alternative: Clone from repository
cd /var/www/mindmend
git clone https://github.com/YOUR-REPO/MindMend.git .
```

#### **4.2 Set Up Python Environment**
```bash
# Switch to mindmend user
sudo -u mindmend bash
cd /var/www/mindmend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test application loading
python -c "import app; print('Application loads successfully')"
```

#### **4.3 Configure Environment**
```bash
# Ensure .env.production has correct settings
cat > /var/www/mindmend/.env.production << 'EOF'
FLASK_ENV=production
SECRET_KEY=46b8274f5f6f10e63c883a39d94df308e30c762650e0383d7f2f3b8302173272
DATABASE_URL=postgresql://mindmend_user:aLo0aPR>{#Rp6{SKpx0,dPyRd9$+:-d>@localhost:5432/mindmend_production
DOMAIN=mindmend.xyz
OPENAI_API_KEY=your-openai-key-here
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
EOF

# Set proper permissions
chown mindmend:mindmend /var/www/mindmend/.env.production
chmod 600 /var/www/mindmend/.env.production
```

### **PART 5: WEB SERVER CONFIGURATION**

#### **5.1 Configure Nginx**
```bash
# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Create MindMend site configuration
cat > /etc/nginx/sites-available/mindmend.xyz << 'EOF'
server {
    listen 80;
    server_name mindmend.xyz www.mindmend.xyz;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name mindmend.xyz www.mindmend.xyz;
    
    # SSL certificates (will be configured by certbot)
    ssl_certificate /etc/letsencrypt/live/mindmend.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mindmend.xyz/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Proxy to application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /var/www/mindmend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/mindmend.xyz /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl reload nginx
```

### **PART 6: SYSTEMD SERVICE**

#### **6.1 Create Service File**
```bash
cat > /etc/systemd/system/mindmend.service << 'EOF'
[Unit]
Description=MindMend Mental Health Platform
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=exec
User=mindmend
Group=mindmend
WorkingDirectory=/var/www/mindmend
Environment=PATH=/var/www/mindmend/venv/bin
EnvironmentFile=/var/www/mindmend/.env.production
ExecStart=/var/www/mindmend/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 120 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable mindmend
systemctl start mindmend

# Check service status
systemctl status mindmend
```

### **PART 7: SSL CERTIFICATE**

#### **7.1 Obtain SSL Certificate**
```bash
# Get Let's Encrypt certificate
certbot --nginx -d mindmend.xyz -d www.mindmend.xyz

# Follow prompts:
# 1. Enter email address
# 2. Agree to terms
# 3. Choose redirect option (recommended)

# Test auto-renewal
certbot renew --dry-run
```

### **PART 8: DATABASE INITIALIZATION**

#### **8.1 Initialize Application Database**
```bash
# Switch to mindmend user
sudo -u mindmend bash
cd /var/www/mindmend
source venv/bin/activate

# Initialize database tables
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
```

### **PART 9: FINAL VERIFICATION**

#### **9.1 Service Status Check**
```bash
# Check all services
systemctl status mindmend nginx postgresql redis-server

# Check logs
journalctl -u mindmend -f
tail -f /var/log/mindmend/app.log
```

#### **9.2 Application Testing**
```bash
# Test local application
curl -I http://localhost:8000

# Test through nginx
curl -I http://localhost

# Test HTTPS
curl -I https://mindmend.xyz

# Expected response:
# HTTP/2 200
# server: nginx
```

#### **9.3 Firewall Verification**
```bash
# Check open ports
ufw status
ss -tlnp | grep -E ':(80|443|8000|22)\s'

# Test external access
curl -I https://mindmend.xyz
```

---

## ✅ **SUCCESS CHECKLIST**

- [ ] Server accessible via SSH
- [ ] All packages installed
- [ ] Services running (nginx, postgresql, redis)
- [ ] Firewall configured
- [ ] Application files uploaded
- [ ] Python environment created
- [ ] Database configured and initialized  
- [ ] Nginx configured
- [ ] Systemd service running
- [ ] SSL certificate installed
- [ ] Application responding on https://mindmend.xyz

---

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Issue: Service won't start**
```bash
# Check logs
journalctl -u mindmend -n 50

# Common fixes
systemctl daemon-reload
systemctl restart mindmend
```

### **Issue: Permission errors**
```bash
# Fix ownership
chown -R mindmend:mindmend /var/www/mindmend
chmod 755 /var/www/mindmend
```

### **Issue: Database connection failed**
```bash
# Check PostgreSQL
systemctl status postgresql
sudo -u postgres psql -l

# Test connection
psql -h localhost -U mindmend_user -d mindmend_production
```

### **Issue: SSL certificate error**
```bash
# Check domain DNS
nslookup mindmend.xyz

# Retry certificate
certbot delete --cert-name mindmend.xyz
certbot --nginx -d mindmend.xyz -d www.mindmend.xyz
```

---

## 🎉 **DEPLOYMENT COMPLETE**

**Your MindMend application should now be live at: https://mindmend.xyz**

**Admin access**: https://mindmend.xyz/admin
**Payment testing**: Use Stripe test mode first
**Monitoring**: Check logs regularly for any issues

**Congratulations! MindMend is successfully deployed to production.**