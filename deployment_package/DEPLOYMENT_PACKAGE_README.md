# 📦 MindMend Deployment Package

## 🚀 **COMPLETE DEPLOYMENT SOLUTION**

This package contains everything needed to deploy MindMend to production server 45.32.244.187.

---

## 📁 **PACKAGE CONTENTS**

### **Core Scripts:**
- `configure_server.sh` - Complete server setup (run on server)
- `deploy.py` - Application deployment automation
- `update_api_keys.sh` - Production API key configuration
- `deployment_config.json` - Server configuration settings

### **Configuration:**
- `.env.production` - Production environment variables
- `scripts/` - Additional deployment utilities

### **Documentation:**
- `SERVER_CONNECTION_TROUBLESHOOTING.md` - Connection help
- `DEPLOYMENT_READY_SUMMARY.md` - Complete deployment guide
- `API_KEY_SETUP_GUIDE.md` - API key configuration

---

## ⚡ **QUICK DEPLOYMENT**

### **Step 1: Connect to Server**
```bash
# Try these connection methods:
ssh root@45.32.244.187
ssh ubuntu@45.32.244.187
ssh admin@45.32.244.187

# Or use your cloud provider's web console
```

### **Step 2: Upload Package to Server**
```bash
# Option A: Upload entire package
scp -r deployment_package/ root@45.32.244.187:/tmp/

# Option B: Download directly on server
ssh root@45.32.244.187
cd /tmp
wget https://github.com/YOUR-REPO/archive/deployment_package.tar.gz
tar -xzf deployment_package.tar.gz
```

### **Step 3: Run Server Setup**
```bash
# On the server:
cd /tmp/deployment_package
chmod +x configure_server.sh
sudo ./configure_server.sh
```

### **Step 4: Update API Keys (Local Machine)**
```bash
# On your local machine:
./update_api_keys.sh
# Enter your production API keys when prompted
```

### **Step 5: Deploy Application**
```bash
# On your local machine:
python3 deploy.py
```

### **Step 6: Configure SSL**
```bash
# On the server:
sudo certbot --nginx -d mindmend.xyz -d www.mindmend.xyz
```

---

## 🔧 **ALTERNATIVE: MANUAL DEPLOYMENT**

### **If automated scripts don't work:**

#### **1. Manual Server Setup**
```bash
# On server (as root):
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv nginx postgresql redis-server
systemctl enable nginx postgresql redis-server
systemctl start nginx postgresql redis-server

# Configure firewall
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Create user and directories
useradd -m mindmend
mkdir -p /var/www/mindmend /var/log/mindmend
chown mindmend:mindmend /var/www/mindmend /var/log/mindmend
```

#### **2. Manual Application Deployment**
```bash
# Upload application files
scp -r app.py models/ templates/ static/ root@45.32.244.187:/var/www/mindmend/

# Install Python dependencies
ssh root@45.32.244.187
cd /var/www/mindmend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **3. Manual Service Configuration**
```bash
# Create systemd service
cat > /etc/systemd/system/mindmend.service << 'EOF'
[Unit]
Description=MindMend Application
After=network.target

[Service]
Type=exec
User=mindmend
WorkingDirectory=/var/www/mindmend
Environment=PATH=/var/www/mindmend/venv/bin
EnvironmentFile=/var/www/mindmend/.env.production
ExecStart=/var/www/mindmend/venv/bin/gunicorn --bind 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable mindmend
systemctl start mindmend
```

---

## ✅ **SUCCESS VERIFICATION**

### **Check Services:**
```bash
# On server:
systemctl status mindmend nginx postgresql
curl -I http://localhost:8000
```

### **Test Domain:**
```bash
# From anywhere:
curl -I https://mindmend.xyz
```

### **Expected Response:**
```
HTTP/2 200
server: nginx
content-type: text/html
```

---

## 🆘 **TROUBLESHOOTING**

### **Common Issues:**

1. **Can't connect to server**
   - Check `SERVER_CONNECTION_TROUBLESHOOTING.md`
   - Use cloud provider console

2. **Permission denied**
   - Run commands with `sudo`
   - Check file permissions

3. **Service won't start**
   - Check logs: `journalctl -u mindmend`
   - Verify configuration files

4. **SSL certificate fails**
   - Ensure domain points to server
   - Check firewall (ports 80, 443)

### **Support Commands:**
```bash
# View logs
sudo journalctl -u mindmend -f
sudo tail -f /var/log/mindmend/app.log

# Restart services
sudo systemctl restart mindmend nginx

# Check status
sudo systemctl status mindmend nginx postgresql redis
```

---

## 📞 **DEPLOYMENT TIMELINE**

**Total Time: ~40 minutes**
- Server connection: 5-10 minutes
- Server setup: 15 minutes
- Application deployment: 10 minutes
- SSL certificate: 5 minutes
- Testing: 5 minutes

---

## 🎯 **FINAL RESULT**

**Live Application:** https://mindmend.xyz
- Complete mental health platform
- Payment processing (Stripe/PayPal)
- Admin panel and counselor dashboard
- AI-powered therapy sessions
- Mobile app support
- Enterprise-grade security

**All deployment issues resolved - ready to launch!**