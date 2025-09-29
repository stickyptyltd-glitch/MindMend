# 🚀 MindMend Quick Deployment Guide

## ⚡ Fast Track Deployment (30 minutes)

### Prerequisites Check
- [ ] Ubuntu 22.04 server with root access
- [ ] mindmend.xyz and admin.mindmend.xyz DNS pointing to server
- [ ] OpenAI API key ready
- [ ] Stripe keys (if using payments)

### Step 1: Upload Files to Server
```bash
# Upload the entire MindMend directory to your server
scp -r MindMend/ root@your-server-ip:/root/
```

### Step 2: Initial Server Setup (5 minutes)
```bash
# SSH into your server as root
ssh root@your-server-ip

# Navigate to MindMend directory
cd /root/MindMend

# Run server setup script
chmod +x scripts/server-setup.sh
./scripts/server-setup.sh

# This will:
# - Install Docker, Docker Compose, security tools
# - Create mindmend user with proper permissions
# - Configure firewall and fail2ban
# - Set up monitoring and backup systems
```

### Step 3: Configure Environment (5 minutes)
```bash
# Switch to mindmend user
su - mindmend
cd MindMend

# Your .env.production file is already generated!
# IMPORTANT: Edit it with your actual API keys
nano .env.production

# Update these critical values:
# - OPENAI_API_KEY=sk-your-actual-openai-key
# - STRIPE_SECRET_KEY=sk_live_your-stripe-key (if using payments)
# - STRIPE_PUBLISHABLE_KEY=pk_live_your-stripe-key
# - MAIL_PASSWORD=your-gmail-app-password
# - ADMIN_IP_WHITELIST=your.ip.address/32 (for security)
```

### Step 4: Deploy Application (15 minutes)
```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh

# This will:
# ✅ Set up SSL certificates
# ✅ Build and start all Docker containers
# ✅ Initialize PostgreSQL database
# ✅ Download AI models (llama2, mistral, codellama)
# ✅ Configure Nginx reverse proxy
# ✅ Set up monitoring and backups
# ✅ Perform health checks
```

### Step 5: Access Your Platform (2 minutes)
```bash
# Check deployment status
docker-compose ps

# All containers should show "Up" status
# If any show "Exit" or "Restarting", check logs:
# docker-compose logs [container-name]
```

**🎉 Your platform is now live!**

- **Main Application**: https://mindmend.xyz
- **Admin Panel**: https://admin.mindmend.xyz

### Step 6: First Admin Login (3 minutes)

1. **Go to**: https://admin.mindmend.xyz
2. **Login with**:
   - Username: `mindmend_admin`
   - Password: `MindMend2024!SecureAdmin`
3. **Set up 2FA** when prompted
4. **Change your password** immediately
5. **Configure IP whitelist** in admin settings

---

## 🔧 Troubleshooting Quick Fixes

### Containers won't start?
```bash
# Check system resources
df -h && free -m

# View container logs
docker-compose logs

# Restart specific service
docker-compose restart [service-name]
```

### Can't access website?
```bash
# Check if services are running
curl http://localhost:8000/health
curl http://localhost:11434/api/tags

# Check nginx status
docker-compose logs nginx

# Verify DNS propagation
nslookup mindmend.xyz
```

### AI models not working?
```bash
# Check Ollama container
docker exec mindmend_ollama ollama list

# Restart Ollama if needed
docker-compose restart ollama

# Wait for models to download (can take 10-15 minutes)
docker logs mindmend_ollama -f
```

---

## 📞 Support

If you encounter any issues:
1. Check logs: `docker-compose logs`
2. Review the full deployment guide: `deployment_guide_production.md`
3. Contact: sticky.pty.ltd@gmail.com

## 🎯 Post-Deployment Tasks

- [ ] Test AI therapy sessions
- [ ] Verify payment processing (if enabled)
- [ ] Set up proper SSL certificates (Let's Encrypt)
- [ ] Configure email alerts
- [ ] Test backup system
- [ ] Review security settings
- [ ] Document admin procedures

---

**🎉 Congratulations! Your AI therapy platform is live!** 🎉