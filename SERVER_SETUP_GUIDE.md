# 🖥️ MindMend Server Setup & Deployment Guide

## Step 1: Get Your Server Ready

### Option A: Cloud Provider Setup (Recommended)

**Digital Ocean Droplet:**
```bash
# Create a new droplet:
# - Ubuntu 22.04 LTS
# - Minimum: 2GB RAM, 1 CPU, 50GB SSD
# - Recommended: 4GB RAM, 2 CPU, 80GB SSD
# - Add your SSH key for secure access
```

**AWS EC2 Instance:**
```bash
# Launch new EC2 instance:
# - Ubuntu Server 22.04 LTS
# - Instance type: t3.medium (2 vCPU, 4GB RAM) or larger
# - Security Group: Allow HTTP (80), HTTPS (443), SSH (22)
# - Create/use existing key pair
```

**Other Providers (Linode, Vultr, etc.):**
- Similar specs: Ubuntu 22.04+, 2GB+ RAM, SSH access

### Step 2: Initial Server Configuration

**Connect to your server:**
```bash
ssh root@YOUR_SERVER_IP
# Replace YOUR_SERVER_IP with your actual server IP address
```

**Run initial setup:**
```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3.11 python3.11-venv postgresql postgresql-contrib nginx redis-server certbot python3-certbot-nginx git curl

# Create application user
useradd -m -s /bin/bash mindmend
usermod -aG sudo mindmend
usermod -aG www-data mindmend

# Create application directories
mkdir -p /var/www/mindmend
chown mindmend:www-data /var/www/mindmend
mkdir -p /var/log/mindmend
chown mindmend:www-data /var/log/mindmend

# Setup PostgreSQL
sudo -u postgres createuser mindmend
sudo -u postgres createdb mindmend_production -O mindmend
sudo -u postgres psql -c "ALTER USER mindmend PASSWORD 'secure_random_password_here';"

# Setup Python environment
sudo -u mindmend python3.11 -m venv /var/www/mindmend/venv
```

## Step 3: Configure DNS

**Point your domain to your server:**
1. Go to your domain registrar (Namecheap, GoDaddy, etc.)
2. Update DNS records:
   ```
   A     @           YOUR_SERVER_IP
   A     www         YOUR_SERVER_IP
   CNAME mindmend    YOUR_SERVER_IP
   ```
3. Wait 5-60 minutes for DNS propagation

## Step 4: Update Deployment Configuration

**Edit `deployment_config.json`:**
```json
{
  "domain": "mindmend.xyz",
  "server_user": "mindmend", 
  "server_host": "YOUR_ACTUAL_SERVER_IP",
  "app_directory": "/var/www/mindmend",
  "python_version": "3.11",
  "database_host": "localhost",
  "database_name": "mindmend_production", 
  "ssl_enabled": true,
  "backup_enabled": true,
  "monitoring_enabled": true
}
```

**Update `.env.production` with your database password:**
```bash
# Update this line with the password you set above:
DATABASE_URL=postgresql://mindmend:secure_random_password_here@localhost:5432/mindmend_production
```

## Step 5: Deploy MindMend

**From your local machine, run deployment:**
```bash
python deploy.py deploy
```

**The deployment script will:**
1. ✅ Run pre-deployment safety checks
2. ✅ Create backup of any existing deployment  
3. ✅ Upload all application files to server
4. ✅ Install Python dependencies
5. ✅ Setup database tables
6. ✅ Configure Nginx with SSL
7. ✅ Setup systemd service
8. ✅ Start MindMend application
9. ✅ Verify deployment is working

## Step 6: Verify Deployment

**Check these URLs:**
- https://mindmend.xyz - Main website
- https://mindmend.xyz/pricing - Payment tiers
- https://mindmend.xyz/admin - Admin panel
- https://mindmend.xyz/health - Health check

**Monitor logs:**
```bash
# SSH to your server and check logs
ssh mindmend@YOUR_SERVER_IP
sudo tail -f /var/log/mindmend/error.log
sudo systemctl status mindmend
```

## Troubleshooting

**Common Issues:**

1. **"Connection refused" during deployment:**
   - Verify server IP is correct
   - Ensure SSH key is added to server
   - Check server is running and accessible

2. **SSL certificate issues:**
   - Verify DNS is pointing to server
   - Check domain name is correct
   - Wait for DNS propagation (up to 24 hours)

3. **Database connection errors:**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check database credentials in `.env.production`
   - Ensure database exists: `sudo -u postgres psql -l`

4. **Payment processing not working:**
   - Verify Stripe webhook endpoint: https://mindmend.xyz/payment/webhook
   - Check Stripe dashboard for webhook delivery status
   - Review payment logs: `grep "PAYMENT_AUDIT" /var/log/mindmend/error.log`

## Manual Deployment (Alternative)

**If automated deployment fails:**

```bash
# 1. Upload files manually
rsync -avz --exclude='.git' ./ mindmend@YOUR_SERVER_IP:/var/www/mindmend/

# 2. SSH to server and complete setup
ssh mindmend@YOUR_SERVER_IP

# 3. Install dependencies
cd /var/www/mindmend
source venv/bin/activate
pip install -r requirements.txt

# 4. Setup database
export $(cat .env.production | xargs)
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 5. Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/mindmend
sudo ln -sf /etc/nginx/sites-available/mindmend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# 6. Setup SSL
sudo certbot --nginx -d mindmend.xyz -d www.mindmend.xyz

# 7. Setup systemd service
sudo cp mindmend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mindmend
sudo systemctl start mindmend

# 8. Check status
sudo systemctl status mindmend
```

## Security Checklist

After deployment, verify:
- [ ] HTTPS is working (SSL certificate valid)
- [ ] HTTP redirects to HTTPS
- [ ] Admin panel requires authentication
- [ ] Payment processing is secured
- [ ] Database is not publicly accessible
- [ ] Server firewall is configured (only 22, 80, 443 open)
- [ ] Regular backups are configured
- [ ] Monitoring is active

## 🚀 Your MindMend Platform is Live!

Once deployed successfully:
- **Website**: https://mindmend.xyz
- **Admin Panel**: https://mindmend.xyz/admin  
- **API Health**: https://mindmend.xyz/health
- **Pricing**: https://mindmend.xyz/pricing

**Your enterprise-grade mental health platform is now serving users with secure payment processing and advanced AI capabilities!**