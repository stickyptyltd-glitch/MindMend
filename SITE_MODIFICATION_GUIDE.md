# 🔧 MindMend Site Modification & Upgrade Guide

## 🎯 **SAFE MODIFICATION WORKFLOW**

### **Method 1: Direct File Updates (Quick Changes)**

#### **1. Make Local Changes**
```bash
# Edit files locally on your machine
nano app.py  # or any file you want to modify
nano templates/index.html
nano static/css/style.css
```

#### **2. Upload Changed Files**
```bash
# Upload specific files you modified
scp app.py root@67.219.102.9:/var/www/mindmend/
scp templates/index.html root@67.219.102.9:/var/www/mindmend/templates/
scp -r static/ root@67.219.102.9:/var/www/mindmend/

# Fix permissions
ssh root@67.219.102.9 "chown -R mindmend:mindmend /var/www/mindmend"
```

#### **3. Restart Application**
```bash
# Restart MindMend to apply changes
ssh root@67.219.102.9 "systemctl restart mindmend"

# Check status
ssh root@67.219.102.9 "systemctl status mindmend"
```

---

### **Method 2: Full Redeployment (Major Changes)**

#### **1. Test Locally First**
```bash
# Test your changes locally
python app.py
# Visit http://localhost:5000 to test
```

#### **2. Create Backup**
```bash
ssh root@67.219.102.9 "
sudo -u postgres pg_dump mindmend_production > /tmp/backup_$(date +%Y%m%d_%H%M%S).sql
tar -czf /tmp/mindmend_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/mindmend
"
```

#### **3. Deploy New Version**
```bash
# Stop service temporarily
ssh root@67.219.102.9 "systemctl stop mindmend"

# Upload all files
scp -r * root@67.219.102.9:/var/www/mindmend/

# Update dependencies if needed
ssh root@67.219.102.9 "
cd /var/www/mindmend
sudo -u mindmend /var/www/mindmend/venv/bin/pip install -r requirements.txt
chown -R mindmend:mindmend /var/www/mindmend
systemctl start mindmend
"
```

---

### **Method 3: Git-Based Updates (Professional)**

#### **Setup Git Repository**
```bash
# On your server, initialize git
ssh root@67.219.102.9 "
cd /var/www/mindmend
git init
git remote add origin https://github.com/yourusername/mindmend.git
"

# On your local machine, commit changes
git add .
git commit -m "Updated feature X"
git push origin main
```

#### **Deploy Updates**
```bash
# Pull updates on server
ssh root@67.219.102.9 "
cd /var/www/mindmend
systemctl stop mindmend
git pull origin main
chown -R mindmend:mindmend /var/www/mindmend
systemctl start mindmend
"
```

---

## 🔄 **COMMON MODIFICATION SCENARIOS**

### **🎨 Frontend Changes (Templates/CSS/JS)**
```bash
# Edit templates locally
nano templates/index.html
nano static/css/custom.css

# Upload and restart (no service restart needed for static files)
scp templates/index.html root@67.219.102.9:/var/www/mindmend/templates/
scp -r static/ root@67.219.102.9:/var/www/mindmend/
ssh root@67.219.102.9 "chown -R mindmend:mindmend /var/www/mindmend"
```

### **🐍 Backend Changes (Python Code)**
```bash
# Edit Python files
nano app.py
nano models/therapy_ai_integration.py

# Upload and restart service
scp app.py root@67.219.102.9:/var/www/mindmend/
scp -r models/ root@67.219.102.9:/var/www/mindmend/
ssh root@67.219.102.9 "
chown -R mindmend:mindmend /var/www/mindmend
systemctl restart mindmend
systemctl status mindmend
"
```

### **📦 Adding New Dependencies**
```bash
# Update requirements.txt locally
echo "new-package==1.0.0" >> requirements.txt

# Upload and install
scp requirements.txt root@67.219.102.9:/var/www/mindmend/
ssh root@67.219.102.9 "
cd /var/www/mindmend
sudo -u mindmend /var/www/mindmend/venv/bin/pip install -r requirements.txt
systemctl restart mindmend
"
```

### **🗄️ Database Schema Changes**
```bash
# Create migration script locally
nano migrate_db.py

# Upload and run migration
scp migrate_db.py root@67.219.102.9:/var/www/mindmend/
ssh root@67.219.102.9 "
cd /var/www/mindmend
sudo -u mindmend /var/www/mindmend/venv/bin/python migrate_db.py
systemctl restart mindmend
"
```

---

## 🛡️ **ZERO-DOWNTIME DEPLOYMENTS**

### **Blue-Green Deployment**
```bash
# Create staging environment
ssh root@67.219.102.9 "
cp -r /var/www/mindmend /var/www/mindmend-staging
cd /var/www/mindmend-staging
# Update files here first
# Test on different port
sudo -u mindmend /var/www/mindmend-staging/venv/bin/gunicorn --bind 127.0.0.1:8001 app:app &
"

# Test staging
curl -I http://67.219.102.9:8001

# Swap environments
ssh root@67.219.102.9 "
systemctl stop mindmend
mv /var/www/mindmend /var/www/mindmend-old
mv /var/www/mindmend-staging /var/www/mindmend
systemctl start mindmend
"
```

---

## 📊 **MONITORING & TROUBLESHOOTING**

### **Check Application Status**
```bash
# Service status
ssh root@67.219.102.9 "systemctl status mindmend nginx postgresql"

# View logs
ssh root@67.219.102.9 "
journalctl -u mindmend -f
tail -f /var/log/mindmend/app.log
tail -f /var/log/nginx/access.log
"

# Test application
curl -I https://mindmend.xyz
curl -I https://mindmend.xyz/admin
```

### **Performance Monitoring**
```bash
# Server resources
ssh root@67.219.102.9 "
htop
df -h
free -h
"

# Application performance
ssh root@67.219.102.9 "
ps aux | grep gunicorn
netstat -tlnp | grep :8000
"
```

---

## 🚀 **AUTOMATED DEPLOYMENT SCRIPT**

### **Create Update Script**
```bash
cat > update_mindmend.sh << 'EOF'
#!/bin/bash
# MindMend Update Script

set -e

SERVER="root@67.219.102.9"
APP_DIR="/var/www/mindmend"

echo "🔄 Starting MindMend update..."

# Create backup
ssh $SERVER "
sudo -u postgres pg_dump mindmend_production > /tmp/backup_\$(date +%Y%m%d_%H%M%S).sql
tar -czf /tmp/mindmend_backup_\$(date +%Y%m%d_%H%M%S).tar.gz $APP_DIR
"

# Upload files
echo "📤 Uploading files..."
rsync -avz --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' ./ $SERVER:$APP_DIR/

# Update dependencies and restart
ssh $SERVER "
cd $APP_DIR
sudo -u mindmend $APP_DIR/venv/bin/pip install -r requirements.txt
chown -R mindmend:mindmend $APP_DIR
systemctl restart mindmend
sleep 3
systemctl status mindmend
"

# Test application
echo "🧪 Testing application..."
if curl -s https://mindmend.xyz | grep -q "MindMend"; then
    echo "✅ Update successful! https://mindmend.xyz is working"
else
    echo "❌ Update failed! Check logs"
    exit 1
fi

echo "🎉 MindMend updated successfully!"
EOF

chmod +x update_mindmend.sh
```

### **Use the Update Script**
```bash
# Make your changes locally, then:
./update_mindmend.sh
```

---

## 🔧 **DEVELOPMENT WORKFLOW**

### **Recommended Process:**
1. **Local Development**: Make changes on your machine
2. **Local Testing**: Test with `python app.py`
3. **Staging Deploy**: Test on staging environment
4. **Backup Production**: Always backup before changes
5. **Production Deploy**: Use one of the methods above
6. **Monitor**: Check logs and functionality
7. **Rollback if needed**: Restore from backup

### **Hot Tips:**
- ✅ Always test locally first
- ✅ Use git for version control
- ✅ Keep backups before major changes
- ✅ Monitor logs after deployments
- ✅ Have a rollback plan
- ❌ Never edit files directly on the server
- ❌ Don't skip testing
- ❌ Don't deploy during high traffic

**Your MindMend site is now fully manageable and upgradeable! 🚀**