# 🚀 YOUR VULTR SERVER DEPLOYMENT COMMANDS
## Server IP: 67.219.102.9

## ✅ **STEP 1: CONNECT TO YOUR SERVER**
```bash
ssh root@67.219.102.9
```
*If prompted about authenticity, type "yes"*

---

## 🔧 **STEP 2: QUICK SERVER SETUP**

### **Option A: Automated Setup (Recommended)**
```bash
# Run this on your Vultr server (67.219.102.9)
curl -sSL https://raw.githubusercontent.com/mindmend/deploy/main/setup.sh | bash

# If that doesn't work, try this:
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv nginx postgresql redis-server git curl ufw certbot python3-certbot-nginx build-essential
systemctl enable nginx postgresql redis-server
systemctl start nginx postgresql redis-server
ufw allow ssh && ufw allow http && ufw allow https && ufw --force enable
echo "✅ Server setup complete!"
```

### **Option B: Manual Commands (Copy/Paste Each)**
```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3.11 python3.11-venv python3.11-pip python3.11-dev build-essential nginx postgresql postgresql-contrib redis-server git curl wget unzip ufw certbot python3-certbot-nginx

# Enable and start services
systemctl enable nginx
systemctl enable postgresql
systemctl enable redis-server
systemctl start nginx
systemctl start postgresql
systemctl start redis-server

# Configure firewall
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Verify services
systemctl status nginx postgresql redis-server
```

---

## 📦 **STEP 3: UPLOAD MINDMEND**

### **From Your Local Machine:**
```bash
# Upload deployment package
scp -r deployment_package/ root@67.219.102.9:/tmp/

# Upload core application files
scp app.py config.py requirements.txt root@67.219.102.9:/tmp/
scp -r models/ templates/ static/ root@67.219.102.9:/tmp/
```

### **On Your Server (67.219.102.9):**
```bash
# Create directories
mkdir -p /var/www/mindmend
mkdir -p /var/log/mindmend
useradd -m mindmend
chown -R mindmend:mindmend /var/www/mindmend /var/log/mindmend

# Copy files
cp -r /tmp/app.py /tmp/models/ /tmp/templates/ /tmp/static/ /tmp/requirements.txt /var/www/mindmend/
cp /tmp/deployment_package/.env.production /var/www/mindmend/
chown -R mindmend:mindmend /var/www/mindmend
```

---

## 🐍 **STEP 4: SETUP PYTHON ENVIRONMENT**

```bash
# Switch to application directory
cd /var/www/mindmend

# Create virtual environment
sudo -u mindmend python3.11 -m venv venv

# Install dependencies
sudo -u mindmend /var/www/mindmend/venv/bin/pip install --upgrade pip
sudo -u mindmend /var/www/mindmend/venv/bin/pip install -r requirements.txt

# Test application loading
sudo -u mindmend /var/www/mindmend/venv/bin/python -c "import app; print('✅ MindMend app loads successfully!')"
```

---

## 🗄️ **STEP 5: SETUP DATABASE**

```bash
# Configure PostgreSQL
sudo -u postgres createuser mindmend_user
sudo -u postgres createdb mindmend_production -O mindmend_user
sudo -u postgres psql -c "ALTER USER mindmend_user WITH PASSWORD 'aLo0aPR>{#Rp6{SKpx0,dPyRd9\$+:-d>';"

# Initialize database tables
cd /var/www/mindmend
sudo -u mindmend bash -c "
source venv/bin/activate
python -c '
from app import app, db
with app.app_context():
    db.create_all()
    print(\"✅ Database tables created successfully!\")
'"
```

---

## 🌐 **STEP 6: CONFIGURE NGINX**

```bash
# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Create MindMend site
cat > /etc/nginx/sites-available/mindmend.xyz << 'EOF'
server {
    listen 80;
    server_name mindmend.xyz www.mindmend.xyz;
    return 301 https://\$server_name\$request_uri;
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
    
    # Proxy to application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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
nginx -t
systemctl reload nginx
```

---

## ⚙️ **STEP 7: CREATE SYSTEM SERVICE**

```bash
# Create systemd service
cat > /etc/systemd/system/mindmend.service << 'EOF'
[Unit]
Description=MindMend Mental Health Platform
After=network.target postgresql.service redis-server.service

[Service]
Type=exec
User=mindmend
Group=mindmend
WorkingDirectory=/var/www/mindmend
Environment=PATH=/var/www/mindmend/venv/bin
EnvironmentFile=/var/www/mindmend/.env.production
ExecStart=/var/www/mindmend/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Start MindMend service
systemctl daemon-reload
systemctl enable mindmend
systemctl start mindmend

# Check status
systemctl status mindmend
```

---

## 🔒 **STEP 8: UPDATE DNS (IMPORTANT!)**

**You need to update your domain DNS to point to your new server:**

1. **Go to your domain registrar** (where you bought mindmend.xyz)
2. **Update DNS records**:
   - **A Record**: mindmend.xyz → 67.219.102.9
   - **A Record**: www.mindmend.xyz → 67.219.102.9
3. **Wait 5-10 minutes** for DNS propagation

**Test DNS update:**
```bash
nslookup mindmend.xyz
# Should show: 67.219.102.9
```

---

## 🔐 **STEP 9: GET SSL CERTIFICATE**

```bash
# After DNS is updated, get SSL certificate
certbot --nginx -d mindmend.xyz -d www.mindmend.xyz

# Follow prompts:
# 1. Enter your email address
# 2. Agree to terms (Y)
# 3. Share email with EFF (Y/N - your choice)
# 4. Choose redirect to HTTPS (2)

# Test auto-renewal
certbot renew --dry-run
```

---

## ✅ **STEP 10: FINAL VERIFICATION**

```bash
# Check all services
systemctl status mindmend nginx postgresql redis-server

# Test local application
curl -I http://localhost:8000

# Test domain (after DNS update)
curl -I https://mindmend.xyz

# Check logs if needed
journalctl -u mindmend -f
tail -f /var/log/mindmend/app.log
```

---

## 🎉 **SUCCESS INDICATORS**

**You'll know it's working when:**
- ✅ `systemctl status mindmend` shows "active (running)"
- ✅ `curl -I http://localhost:8000` returns HTTP/1.1 200
- ✅ `https://mindmend.xyz` loads in your browser
- ✅ You can access the admin panel

**Your MindMend application will be live at: https://mindmend.xyz**

---

## 🆘 **NEED HELP?**

**If something fails:**
1. Check service status: `systemctl status mindmend`
2. Check logs: `journalctl -u mindmend -n 50`
3. Test database: `sudo -u mindmend psql -h localhost -U mindmend_user -d mindmend_production`
4. Restart services: `systemctl restart mindmend nginx`

**I'm here to help if you get stuck! Just share any error messages.**