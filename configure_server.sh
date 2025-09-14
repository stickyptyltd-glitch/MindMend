#!/bin/bash
# MindMend Server Configuration Script
# For server: 45.32.244.187
# Domain: mindmend.xyz

echo "🚀 Configuring MindMend Server: 45.32.244.187"
echo "=============================================="

# Update system packages
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "📋 Installing required packages..."
apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    ufw \
    htop \
    build-essential

# Configure firewall
echo "🔥 Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Create application user
echo "👤 Creating MindMend application user..."
useradd -m -s /bin/bash mindmend
usermod -aG sudo mindmend
usermod -aG www-data mindmend

# Create application directories
echo "📁 Setting up application directories..."
mkdir -p /var/www/mindmend
mkdir -p /var/log/mindmend
mkdir -p /var/backups/mindmend
chown -R mindmend:www-data /var/www/mindmend
chown -R mindmend:www-data /var/log/mindmend
chown -R mindmend:www-data /var/backups/mindmend
chmod -R 755 /var/www/mindmend
chmod -R 755 /var/log/mindmend

# Setup PostgreSQL
echo "🗄️  Configuring PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Generate secure database password
DB_PASSWORD=$(openssl rand -base64 32)
echo "Generated database password: $DB_PASSWORD"
echo "$DB_PASSWORD" > /root/mindmend_db_password.txt
chmod 600 /root/mindmend_db_password.txt

# Create database and user
sudo -u postgres createuser mindmend
sudo -u postgres createdb mindmend_production -O mindmend
sudo -u postgres psql -c "ALTER USER mindmend PASSWORD '$DB_PASSWORD';"

# Setup Python environment
echo "🐍 Setting up Python environment..."
sudo -u mindmend python3.11 -m venv /var/www/mindmend/venv
sudo -u mindmend /var/www/mindmend/venv/bin/pip install --upgrade pip

# Configure Redis
echo "⚡ Configuring Redis..."
systemctl start redis-server
systemctl enable redis-server

# Setup log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/mindmend << EOF
/var/log/mindmend/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 mindmend www-data
    postrotate
        systemctl reload mindmend > /dev/null 2>&1 || true
    endscript
}
EOF

# Create backup script
echo "💾 Setting up backup system..."
cat > /usr/local/bin/mindmend-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/mindmend"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="mindmend_backup_$DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup database
sudo -u postgres pg_dump mindmend_production > "$BACKUP_DIR/$BACKUP_NAME/database.sql"

# Backup application files
tar -czf "$BACKUP_DIR/$BACKUP_NAME/app_files.tar.gz" -C /var/www/mindmend .

# Backup logs
tar -czf "$BACKUP_DIR/$BACKUP_NAME/logs.tar.gz" -C /var/log/mindmend .

# Remove backups older than 30 days
find "$BACKUP_DIR" -type d -mtime +30 -name "mindmend_backup_*" -exec rm -rf {} +

echo "Backup completed: $BACKUP_NAME"
EOF

chmod +x /usr/local/bin/mindmend-backup.sh

# Setup cron job for backups
echo "⏰ Setting up automated backups..."
echo "0 2 * * * /usr/local/bin/mindmend-backup.sh" | crontab -

# Configure Nginx (basic setup, will be updated during deployment)
echo "🌐 Basic Nginx configuration..."
systemctl start nginx
systemctl enable nginx

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Create basic health check endpoint
mkdir -p /var/www/html
echo "MindMend Server Ready" > /var/www/html/index.html

echo "✅ Server configuration completed!"
echo ""
echo "📋 Server Information:"
echo "   IP Address: 45.32.244.187"
echo "   Domain: mindmend.xyz"
echo "   User: mindmend"
echo "   App Directory: /var/www/mindmend"
echo "   Database: mindmend_production"
echo "   Database Password: $DB_PASSWORD"
echo ""
echo "🔑 Important Notes:"
echo "   1. Database password saved to: /root/mindmend_db_password.txt"
echo "   2. Make sure DNS points mindmend.xyz to this server"
echo "   3. SSH key should be configured for 'mindmend' user"
echo "   4. Ready for MindMend deployment!"
echo ""
echo "🚀 Next steps:"
echo "   1. Update .env.production with database password"
echo "   2. Run: python deploy.py deploy"
echo "   3. Your platform will be live at https://mindmend.xyz"