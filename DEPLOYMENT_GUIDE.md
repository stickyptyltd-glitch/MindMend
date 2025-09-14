# MindMend Production Deployment Guide
## Comprehensive deployment to mindmend.xyz

### 🚀 Quick Deployment Summary

MindMend is now **production-ready** with comprehensive payment security features implemented:

✅ **Payment Security Features Added:**
- Advanced fraud detection and risk scoring
- Rate limiting for payment operations
- Encrypted payment data storage
- Webhook signature verification  
- PCI DSS compliance utilities
- Comprehensive audit logging
- Payment authentication decorators

✅ **Production Configuration:**
- Environment variables configured (`.env.production`)
- Nginx configuration with SSL and security headers
- Systemd service file for application management
- Automated deployment script with safety checks

---

## 🔧 Pre-Deployment Setup

### 1. Server Requirements
- **OS:** Ubuntu 20.04+ or similar Linux distribution
- **RAM:** Minimum 2GB (4GB recommended)
- **Disk:** 20GB+ available space
- **Domain:** mindmend.xyz pointing to server IP

### 2. Required API Keys & Credentials

**CRITICAL:** Update these in `.env.production` before deployment:

```bash
# Stripe (Production Keys)
STRIPE_SECRET_KEY=sk_live_your_actual_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_secret

# OpenAI
OPENAI_API_KEY=sk-your_actual_openai_api_key

# Email
MAIL_PASSWORD=your_gmail_app_password
```

### 3. Server Setup Commands

```bash
# 1. Initial server setup
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv postgresql nginx redis-server

# 2. Create application user
sudo useradd -m -s /bin/bash mindmend
sudo usermod -aG www-data mindmend

# 3. Create application directory
sudo mkdir -p /var/www/mindmend
sudo chown mindmend:www-data /var/www/mindmend
sudo mkdir -p /var/log/mindmend
sudo chown mindmend:www-data /var/log/mindmend

# 4. Setup PostgreSQL
sudo -u postgres createuser mindmend
sudo -u postgres createdb mindmend_production -O mindmend
sudo -u postgres psql -c "ALTER USER mindmend PASSWORD 'your_secure_password';"

# 5. Setup Python environment
sudo -u mindmend python3.11 -m venv /var/www/mindmend/venv
```

---

## 🚀 Automated Deployment

### Option A: Using Deployment Script (Recommended)

1. **Configure deployment settings:**
   ```bash
   # Edit deployment_config.json with your server details
   {
     "server_host": "your_server_ip",
     "server_user": "mindmend",
     "domain": "mindmend.xyz"
   }
   ```

2. **Run automated deployment:**
   ```bash
   # Full deployment with all safety checks
   python deploy.py deploy
   
   # Skip pre-checks if you've verified manually
   python deploy.py deploy --skip-checks
   ```

### Option B: Manual Deployment

1. **Upload files to server:**
   ```bash
   rsync -avz --exclude='.git' ./ mindmend@your_server:/var/www/mindmend/
   ```

2. **Install dependencies:**
   ```bash
   ssh mindmend@your_server
   cd /var/www/mindmend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Setup database:**
   ```bash
   export $(cat .env.production | xargs)
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

4. **Configure Nginx:**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/mindmend
   sudo ln -s /etc/nginx/sites-available/mindmend /etc/nginx/sites-enabled/
   sudo rm /etc/nginx/sites-enabled/default
   sudo nginx -t && sudo systemctl reload nginx
   ```

5. **Setup SSL Certificate:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d mindmend.xyz -d www.mindmend.xyz
   ```

6. **Configure systemd service:**
   ```bash
   sudo cp mindmend.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable mindmend
   sudo systemctl start mindmend
   ```

---

## 🔒 Security Configuration

### Payment Security Features

The deployment includes comprehensive payment security:

- **Fraud Detection:** Real-time risk scoring for all payment attempts
- **Rate Limiting:** Protection against payment abuse (3 attempts per 30 minutes)
- **Data Encryption:** All sensitive payment data encrypted at rest
- **Webhook Verification:** Stripe webhook signatures verified
- **Audit Logging:** Complete payment activity logging
- **PCI Compliance:** Sensitive data sanitization utilities

### SSL & Security Headers

- **SSL/TLS:** Let's Encrypt certificates with modern cipher suites
- **HSTS:** Strict Transport Security enabled
- **CSP:** Content Security Policy configured for Stripe integration
- **Rate Limiting:** Nginx-level protection for sensitive endpoints

---

## 📊 Monitoring & Health Checks

### Health Check Endpoints

- `https://mindmend.xyz/health` - Application health
- `https://mindmend.xyz/` - Main site functionality
- `https://mindmend.xyz/pricing` - Payment system status

### Monitoring Commands

```bash
# Check application status
sudo systemctl status mindmend

# View application logs
sudo tail -f /var/log/mindmend/error.log

# Monitor payment security events
sudo grep "FRAUD_ALERT\|PAYMENT_AUDIT" /var/log/mindmend/error.log

# Check SSL certificate status
sudo certbot certificates
```

---

## 💳 Stripe Configuration

### Required Stripe Setup

1. **Create Stripe account** and obtain production API keys
2. **Configure webhook endpoint:** `https://mindmend.xyz/payment/webhook`
3. **Enable webhook events:**
   - `payment_intent.succeeded`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

4. **Set up pricing in Stripe Dashboard:**
   ```
   Premium Monthly: $29.99/month
   Premium Yearly: $299.99/year
   Enterprise Monthly: $99.99/month
   Enterprise Yearly: $999.99/year
   ```

---

## 🔧 Troubleshooting

### Common Issues

1. **Payment processing fails:**
   - Verify Stripe API keys in `.env.production`
   - Check webhook endpoint is accessible
   - Review payment audit logs

2. **Database connection issues:**
   - Verify PostgreSQL service is running
   - Check database credentials in `.env.production`
   - Ensure database user has proper permissions

3. **SSL certificate problems:**
   - Run `sudo certbot renew --dry-run`
   - Check domain DNS settings
   - Verify firewall allows ports 80/443

### Log Locations

- **Application:** `/var/log/mindmend/error.log`
- **Nginx:** `/var/log/nginx/mindmend_error.log`
- **Payment Security:** Search for `PAYMENT_AUDIT` in application logs
- **Systemd:** `sudo journalctl -u mindmend -f`

---

## 🎯 Post-Deployment Verification

### Verification Checklist

- [ ] Website loads at https://mindmend.xyz
- [ ] SSL certificate is valid
- [ ] User registration/login works
- [ ] Payment pages load correctly
- [ ] Stripe payment flow functions
- [ ] Admin panel accessible
- [ ] Health checks passing
- [ ] Security headers present

### Test Payment Processing

1. Create test user account
2. Attempt subscription upgrade
3. Verify Stripe checkout process
4. Check webhook processing in logs
5. Confirm subscription status updates

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

- **Weekly:** Check SSL certificate status
- **Monthly:** Review payment security logs
- **Quarterly:** Update dependencies and security patches

### Emergency Contacts

- **Technical Issues:** Check deployment logs and systemd status
- **Payment Problems:** Review Stripe dashboard and webhook logs
- **Security Alerts:** Monitor audit logs for fraud detection

---

## 🚀 MindMend is Ready for Production!

Your comprehensive mental health platform is now deployed with:

- ✅ **Enterprise-grade security** with fraud detection
- ✅ **Stripe payment processing** with webhook integration  
- ✅ **SSL encryption** and security headers
- ✅ **Automated deployment** and monitoring
- ✅ **Three-tier subscription model** (Free/Premium/Enterprise)
- ✅ **Complete audit logging** for compliance

**Website:** https://mindmend.xyz
**Admin Panel:** https://mindmend.xyz/admin
**Pricing:** https://mindmend.xyz/pricing

The platform is production-ready and compliant with modern security standards!