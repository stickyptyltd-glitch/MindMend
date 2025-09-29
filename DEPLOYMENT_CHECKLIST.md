# MindMend Production Deployment Checklist
## 🚀 Pre-Deployment Requirements

### 1. Server Setup
- [ ] Ubuntu 22.04 LTS server (minimum 8GB RAM, 4 vCPUs)
- [ ] Root access to the server
- [ ] Static IP address assigned
- [ ] SSH access configured

### 2. Domain Configuration  
- [ ] mindmend.xyz DNS A record points to server IP
- [ ] admin.mindmend.xyz DNS A record points to server IP
- [ ] DNS propagation completed (check with: `nslookup mindmend.xyz`)

### 3. Required Credentials/API Keys
- [ ] OpenAI API key
- [ ] Stripe secret and publishable keys
- [ ] Email credentials (Gmail app password recommended)
- [ ] Admin username and secure password

## 📋 Deployment Steps

### Step 1: Initial Server Setup (Run as root)
```bash
# Upload MindMend files to server
# Run server setup script
sudo chmod +x scripts/server-setup.sh
sudo ./scripts/server-setup.sh
```

### Step 2: Configure Environment (Run as mindmend user)
```bash
su - mindmend
cd MindMend
cp .env.production .env
nano .env  # Edit with your actual values
```

### Step 3: Deploy Application
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Step 4: Verify Deployment
- [ ] All Docker containers running: `docker-compose ps`
- [ ] Main app responding: `curl http://localhost:8000/health`
- [ ] Admin panel accessible: `https://admin.mindmend.xyz`
- [ ] SSL certificates valid
- [ ] AI models installed: `curl http://localhost:11434/api/tags`

### Step 5: Security Configuration
- [ ] Admin 2FA setup completed
- [ ] IP whitelist configured
- [ ] Monitoring alerts working
- [ ] Backup system active

## 🔐 Critical Security Notes
1. **Change default passwords** in .env file
2. **Set up proper SSL certificates** (Let's Encrypt recommended)
3. **Configure IP whitelist** for admin access
4. **Test emergency contact system**
5. **Verify HIPAA compliance** settings

## 📞 Emergency Contacts
- Technical Issues: sticky.pty.ltd@gmail.com
- Security Concerns: [Your security contact]
- Business Critical: [Your emergency contact]

## 🎯 Success Criteria
- [ ] Main application loads at https://mindmend.xyz
- [ ] Admin panel accessible at https://admin.mindmend.xyz
- [ ] AI therapy sessions working
- [ ] Payment processing functional
- [ ] Monitoring alerts active
- [ ] Backups running automatically