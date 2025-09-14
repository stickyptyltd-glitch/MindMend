# ⚡ Quick Deployment Commands for MindMend

## 🎯 **AFTER YOU GET YOUR NEW SERVER IP**

Replace `YOUR-SERVER-IP` with your actual DigitalOcean droplet IP address.

### **Step 1: Test Connection**
```bash
ssh root@YOUR-SERVER-IP
# If prompted about authenticity, type "yes"
```

### **Step 2: One-Command Server Setup**
```bash
# Run this on your NEW server
curl -sSL https://raw.githubusercontent.com/mindmend-deployment/main/configure_server.sh | sudo bash
```

**OR if that doesn't work, manual setup:**
```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3.11 python3.11-venv nginx postgresql redis-server git curl ufw certbot python3-certbot-nginx

# Start services
systemctl enable nginx postgresql redis-server
systemctl start nginx postgresql redis-server

# Configure firewall
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

echo "✅ Server setup complete!"
```

### **Step 3: Upload MindMend**
```bash
# From your local machine, upload the application
scp -r deployment_package/ root@YOUR-SERVER-IP:/tmp/
scp -r app.py models/ templates/ static/ requirements.txt root@YOUR-SERVER-IP:/var/www/mindmend/
```

### **Step 4: Configure Application**
```bash
# On the server
cd /var/www/mindmend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy environment
cp /tmp/deployment_package/.env.production .env.production
```

### **Step 5: Start MindMend**
```bash
# Create systemd service
cp /tmp/deployment_package/mindmend.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable mindmend
systemctl start mindmend

# Configure nginx
cp /tmp/deployment_package/nginx.conf /etc/nginx/sites-available/mindmend.xyz
ln -s /etc/nginx/sites-available/mindmend.xyz /etc/nginx/sites-enabled/
systemctl reload nginx
```

### **Step 6: Get SSL Certificate**
```bash
# Configure SSL for mindmend.xyz (update DNS first!)
certbot --nginx -d mindmend.xyz -d www.mindmend.xyz
```

---

## 🔥 **SUPER QUICK VERSION**

**One-liner deployment (after server is created):**
```bash
ssh root@YOUR-SERVER-IP "curl -sSL https://deploy.mindmend.xyz/auto-deploy.sh | bash"
```

---

## 📋 **CHECKLIST**

- [ ] DigitalOcean droplet created
- [ ] Server IP obtained
- [ ] SSH connection working
- [ ] Server configured
- [ ] MindMend uploaded
- [ ] Services running
- [ ] DNS updated (mindmend.xyz → new IP)
- [ ] SSL certificate obtained
- [ ] Application tested

**Ready for the next step? Share your new server IP!**