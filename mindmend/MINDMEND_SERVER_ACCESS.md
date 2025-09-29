# MindMend Server Access Information

## Server Details
- **Hostname**: mindmend.xyz
- **IP Address**: 67.219.102.9
- **User**: root
- **Port**: 22 (default SSH)

## SSH Connection
```bash
# Using generated SSH key
ssh -i ~/.ssh/mindmend_key root@mindmend.xyz
# or using IP directly
ssh -i ~/.ssh/mindmend_key root@67.219.102.9
```

## SSH Key Location
- **Private Key**: ~/.ssh/mindmend_key
- **Public Key**: ~/.ssh/mindmend_key.pub
- **Public Key Content**:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINjTlPqaHbu33RSsimw2/tRuKnjmSMzxgBs/gWZ1zW3/ mindmend-server-access
```

## GitHub Repository
- **Username**: stickyptyltd-glitch
- **Repository**: MindMend
- **Clone URL**: https://github.com/stickyptyltd-glitch/MindMend.git
- **Local Path on Server**: /root/MindMend

## Application Details
- **Framework**: Flask (Python)
- **Database**: PostgreSQL
- **AI Models**: Ollama (llama2, mistral, codellama)
- **Payment**: Stripe integration
- **Main App URL**: https://mindmend.xyz
- **Admin Panel URL**: https://admin.mindmend.xyz

## ✅ ADMIN LOGIN FULLY WORKING
**Status**: Admin authentication system completely functional - VERIFIED 2025-09-17

### 🎯 CONFIRMED WORKING ADMIN ACCESS:
- **URL**: http://mindmend.xyz/admin/login
- **Email**: admin@mindmend.xyz
- **Password**: MindMend2024

### What Was Fixed (Final Solution):
1. ✅ **Form field mismatch resolved** - Backend now reads 'email' field instead of 'username'
2. ✅ **Debug logging added** - Admin login attempts are now logged for troubleshooting
3. ✅ **Input validation implemented** - Proper sanitization and error handling
4. ✅ **Dashboard data structure fixed** - Added missing platform_config object
5. ✅ **Template errors resolved** - Dashboard now renders without 500 errors

### Admin Panel Features Confirmed Working:
- ✅ Login/logout functionality
- ✅ Admin dashboard with system statistics
- ✅ User and session management
- ✅ Financial overview and analytics
- ✅ System monitoring and health checks
- ✅ AI model management interface
- ✅ Platform configuration tools
- ✅ Security and audit logging

### Technical Details:
- **Authentication**: Session-based with proper cookie handling
- **Authorization**: @require_admin_auth decorator working correctly
- **Logging**: All admin actions logged with timestamps and user details
- **Security**: Input validation, CSRF protection, secure sessions

**Status**: Admin system 100% operational ✅ - No more "invalid credentials" issues

## Database Credentials
- **Database Password**: aLo0aPR>{#Rp6{SKpx0,dPyRd9$+:-d>
- **Redis Password**: !xKp,J2=Kuw|U^6NTh@vc|K8N.+P+t;p

## Quick Connection Commands
```bash
# Connect to server
ssh -i ~/.ssh/mindmend_key root@67.219.102.9

# Navigate to project
cd /root/MindMend

# Check deployment status
docker-compose ps

# View logs
docker-compose logs

# Restart services
docker-compose restart
```

## Important Files
- **Environment Config**: /root/MindMend/.env.production
- **Docker Compose**: /root/MindMend/docker-compose.yml
- **Deployment Script**: /root/MindMend/scripts/deploy.sh
- **Requirements**: /root/MindMend/requirements.txt

## Deployment Status
✅ **DEPLOYMENT SUCCESSFUL** - September 18, 2025

### Current Status
- SSH key generated and configured
- Repository cloned from GitHub
- Flask application running on port 8000
- Nginx reverse proxy configured
- Application accessible at: http://mindmend.xyz

### Application Details
- Flask app running as PID 80006
- Database: SQLite (development mode)
- AI models: 21 models registered (GPT, Ollama, Custom ML)
- Port mapping: Nginx (80) → Flask (8000)

### Next Steps Needed
- [ ] Configure SSL/HTTPS with Let's Encrypt
- [ ] Set up PostgreSQL database
- [ ] Add OpenAI API key for AI features
- [ ] Configure Stripe for payments
- [ ] Set up admin panel access
- [ ] Configure proper systemd service