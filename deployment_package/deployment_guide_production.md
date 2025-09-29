# MindMend Production Deployment Guide

## Overview
Complete deployment guide for MindMend AI therapy platform on mindmend.xyz with admin panel on admin.mindmend.xyz.

## Prerequisites

### Server Requirements
- **Minimum**: 8GB RAM, 4 vCPUs, 160GB SSD, Ubuntu 22.04 LTS
- **Recommended**: 16GB RAM, 8 vCPUs, 320GB SSD
- **Network**: Static IP address, domain control

### Domain Setup
1. Point `mindmend.xyz` to your server IP
2. Point `admin.mindmend.xyz` to your server IP
3. Configure DNS A records with your domain registrar (Namecheap)

## Deployment Steps

### Step 1: Initial Server Setup

```bash
# Run as root
sudo ./scripts/server-setup.sh
```

This script will:
- Update system packages
- Install Docker and Docker Compose
- Configure firewall and security
- Create mindmend user
- Set up NVIDIA Docker (if GPU available)
- Configure monitoring and backup systems

### Step 2: Application Deployment

```bash
# Switch to mindmend user
su - mindmend

# Clone repository (or upload files)
# Configure environment variables
cp .env.production .env

# Edit environment variables
nano .env.production
```

**Required Environment Variables:**
```bash
# Database
POSTGRES_PASSWORD=your-secure-database-password

# API Keys
OPENAI_API_KEY=your-openai-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

# Admin Access
SUPER_ADMIN_ID=your-admin-username
SUPER_ADMIN_PASSWORD_HASH=your-bcrypt-hashed-password
ADMIN_IP_WHITELIST=your-ip-address/32,office-ip/32

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
ALERT_RECIPIENTS=your-alert-email@gmail.com
```

### Step 3: Deploy Services

```bash
# Run deployment script
./scripts/deploy.sh
```

This will:
- Set up SSL certificates
- Deploy Docker containers
- Install AI models (Ollama)
- Configure monitoring
- Set up automated backups
- Perform health checks

### Step 4: Admin Panel Setup

1. **Initial Admin Login:**
   - Visit `https://admin.mindmend.xyz/login`
   - Use credentials from environment variables
   - Set up 2FA when prompted

2. **IP Whitelist Configuration:**
   - Add your IP addresses to `ADMIN_IP_WHITELIST` in environment
   - Restart containers: `docker-compose restart`

3. **SSL Certificates:**
   - Replace self-signed certificates with proper SSL certificates
   - Use Let's Encrypt or your SSL provider
   - Update certificate paths in nginx configuration

### Step 5: AI Model Configuration

The deployment automatically installs these AI models:

- **llama2:7b** - General therapy conversations
- **mistral:7b** - Specialized counseling (CBT, DBT)
- **codellama:7b** - Research analysis

**Monitor model installation:**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# View model download progress
docker logs mindmend_ollama -f
```

## Security Configuration

### Admin Panel Security
- **Multi-factor Authentication** required for all admin users
- **IP Whitelisting** for admin subdomain
- **Rate limiting** on authentication endpoints
- **Session monitoring** with automatic logout
- **Audit logging** for all admin actions

### Application Security
- **HTTPS enforced** with HSTS headers
- **Content Security Policy** configured
- **HIPAA-compliant** logging and data handling
- **Automated security updates** enabled
- **Fail2ban** protection against brute force
- **Firewall** configured with minimal open ports

### AI Safety Guardrails
- **Crisis intervention** detection and escalation
- **Inappropriate content** filtering
- **Therapy boundary** enforcement
- **Privacy protection** for user information
- **Response validation** for therapeutic appropriateness

## Monitoring and Alerts

### Automated Monitoring
```bash
# Start monitoring daemon
./scripts/monitor.sh start

# Check status
./scripts/monitor.sh status

# Generate health report
./scripts/monitor.sh report
```

### Key Metrics Monitored
- **System Resources**: CPU, memory, disk usage
- **Application Performance**: Response times, error rates
- **AI Model Usage**: Performance and availability
- **Security Events**: Failed login attempts, suspicious activity
- **Business Metrics**: Active sessions, user engagement

### Alert Configuration
Alerts are sent via email for:
- **Critical**: Disk space >95%, service failures
- **Error**: High error rates, memory issues
- **Warning**: High CPU usage, slow response times

## Backup and Recovery

### Automated Backups
- **Database**: Daily PostgreSQL dumps
- **Files**: Daily tar archives of uploads
- **Retention**: 30 days of backups
- **Schedule**: 2 AM daily via cron

### Manual Backup
```bash
# Create immediate backup
./scripts/monitor.sh backup

# View backup files
ls -la /opt/mindmend/backups/
```

### Disaster Recovery
1. **Database Recovery:**
   ```bash
   # Restore database
   gunzip -c backup_file.sql.gz | docker exec -i mindmend_postgres psql -U mindmend_user -d mindmend_production
   ```

2. **File Recovery:**
   ```bash
   # Extract files
   tar -xzf app_backup_DATE.tar.gz -C /var/www/mindmend/
   ```

## Maintenance

### Regular Updates
```bash
# Update system packages (automated)
sudo apt update && sudo apt upgrade -y

# Update Docker containers
docker-compose pull
docker-compose up -d

# Update AI models
docker exec mindmend_ollama ollama pull llama2:7b
docker exec mindmend_ollama ollama pull mistral:7b
```

### Log Rotation
- **Automatic**: Configured via logrotate
- **Retention**: 30 days
- **Location**: `/var/log/mindmend/`

### Performance Optimization
- **Database**: Regular VACUUM and ANALYZE
- **Docker**: Image cleanup via cron
- **Logs**: Automatic compression and rotation
- **Cache**: Redis configuration optimization

## Troubleshooting

### Common Issues

1. **Container Won't Start:**
   ```bash
   # Check logs
   docker-compose logs [service_name]
   
   # Check system resources
   df -h && free -m
   ```

2. **AI Models Not Responding:**
   ```bash
   # Restart Ollama
   docker-compose restart ollama
   
   # Check model status
   curl http://localhost:11434/api/tags
   ```

3. **Database Connection Issues:**
   ```bash
   # Check PostgreSQL
   docker exec mindmend_postgres pg_isready -U mindmend_user
   
   # View connection pool
   docker-compose logs postgres
   ```

4. **SSL Certificate Issues:**
   ```bash
   # Check certificate expiry
   openssl x509 -in /opt/mindmend/ssl/mindmend.xyz.crt -text -noout
   
   # Renew Let's Encrypt
   certbot renew --nginx
   ```

### Performance Issues

1. **High Memory Usage:**
   - Reduce AI model concurrent sessions
   - Increase swap space
   - Monitor for memory leaks

2. **Slow Response Times:**
   - Check AI model performance
   - Optimize database queries
   - Review nginx configuration

3. **High Error Rates:**
   - Check application logs
   - Review guardrail configurations
   - Monitor external API limits

## Support and Monitoring

### Health Check URLs
- **Main Application**: `https://mindmend.xyz/health`
- **Admin Panel**: `https://admin.mindmend.xyz/admin/health`
- **AI Models**: `http://localhost:11434/api/tags`

### Log Locations
- **Application**: `/var/log/mindmend/app.log`
- **Nginx**: `/var/log/nginx/`
- **System**: `/var/log/mindmend/system-monitor.log`
- **Security**: `/var/log/mindmend/security.log`

### Emergency Contacts
- **Technical Support**: sticky.pty.ltd@gmail.com
- **Security Issues**: security@mindmend.xyz
- **Business Critical**: [Your emergency contact]

## Post-Deployment Checklist

- [ ] All containers running and healthy
- [ ] SSL certificates installed and valid
- [ ] Admin panel accessible with 2FA
- [ ] AI models installed and responding
- [ ] Monitoring system active
- [ ] Backup system configured
- [ ] DNS records propagated
- [ ] Email alerts working
- [ ] Security scans completed
- [ ] Performance benchmarks recorded
- [ ] Documentation updated
- [ ] Stakeholders notified

## Production URL Structure

- **Main Application**: https://mindmend.xyz
- **Admin Panel**: https://admin.mindmend.xyz
- **API Endpoints**: https://mindmend.xyz/api/*
- **WebSocket**: wss://mindmend.xyz/socket.io/
- **Health Check**: https://mindmend.xyz/health

---

**Deployment completed successfully!** 

Your MindMend platform is now running in production with:
- ✅ Secure admin panel with 2FA
- ✅ AI-powered therapy sessions
- ✅ HIPAA-compliant security measures
- ✅ Automated monitoring and alerts
- ✅ Scalable Docker infrastructure
- ✅ Professional therapy guardrails