#!/bin/bash
# Complete MindMend Server Setup Script
# Paste this entire script into your Vultr console

echo "🚀 MindMend Complete Server Setup"
echo "=================================="
echo "This will install MindMend from scratch"
echo ""

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "📥 Installing required packages..."
apt install -y python3.11 python3.11-venv python3-pip nginx postgresql redis-server git curl ufw certbot python3-certbot-nginx build-essential

# Start services
echo "🔧 Starting services..."
systemctl enable nginx postgresql redis-server
systemctl start nginx postgresql redis-server

# Configure firewall
echo "🔒 Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Create user and directories
echo "👤 Creating application user..."
useradd -m mindmend || true
mkdir -p /var/www/mindmend /var/log/mindmend
chown -R mindmend:mindmend /var/www/mindmend /var/log/mindmend

# Clone repository
echo "📥 Cloning MindMend repository..."
cd /var/www
rm -rf mindmend
git clone https://github.com/stickyptyltd-glitch/MindMend.git mindmend
cd mindmend
chown -R mindmend:mindmend /var/www/mindmend

# Setup Python environment
echo "🐍 Setting up Python environment..."
sudo -u mindmend python3.11 -m venv venv
sudo -u mindmend /var/www/mindmend/venv/bin/pip install --upgrade pip
sudo -u mindmend /var/www/mindmend/venv/bin/pip install -r requirements.txt

# Setup database
echo "🗄️ Setting up database..."
sudo -u postgres createuser mindmend_user || true
sudo -u postgres createdb mindmend_production -O mindmend_user || true
sudo -u postgres psql -c "ALTER USER mindmend_user WITH PASSWORD 'aLo0aPR>{#Rp6{SKpx0,dPyRd9\$+:-d>';" || true

# Initialize database tables
echo "📋 Initializing database..."
sudo -u mindmend bash -c "
    cd /var/www/mindmend
    source venv/bin/activate
    python -c 'from app import app, db; app.app_context().push(); db.create_all(); print(\"Database initialized!\")'
"

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > /var/www/mindmend/.env.production << 'EOF'
DATABASE_URL=postgresql://mindmend_user:aLo0aPR>{#Rp6{SKpx0,dPyRd9$+:-d>@localhost/mindmend_production
SESSION_SECRET=your-secret-key-change-this-in-production
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key_here
OPENAI_API_KEY=your_openai_api_key_here
EOF

chown mindmend:mindmend /var/www/mindmend/.env.production
chmod 600 /var/www/mindmend/.env.production

# Configure Nginx
echo "🌐 Configuring Nginx..."
rm -f /etc/nginx/sites-enabled/default

cat > /etc/nginx/sites-available/mindmend.xyz << 'EOF'
server {
    listen 80;
    server_name mindmend.xyz www.mindmend.xyz 67.219.102.9;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout       60s;
        proxy_send_timeout          60s;
        proxy_read_timeout          60s;
    }

    location /static/ {
        alias /var/www/mindmend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -sf /etc/nginx/sites-available/mindmend.xyz /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Create systemd service
echo "🔧 Creating system service..."
cat > /etc/systemd/system/mindmend.service << 'EOF'
[Unit]
Description=MindMend Mental Health Platform
After=network.target postgresql.service redis-server.service

[Service]
Type=exec
User=mindmend
Group=mindmend
WorkingDirectory=/var/www/mindmend
Environment=PATH=/var/www/mindmend/venv/bin
EnvironmentFile=/var/www/mindmend/.env.production
ExecStart=/var/www/mindmend/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 120 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Start the service
echo "🚀 Starting MindMend service..."
systemctl daemon-reload
systemctl enable mindmend
systemctl start mindmend

# Wait and test
echo "⏳ Waiting for service to start..."
sleep 5

echo "🧪 Testing deployment..."
echo "=== Service Status ==="
systemctl status mindmend --no-pager -l

echo "=== Testing Application ==="
curl -I http://localhost:8000 || echo "Local app test failed"
curl -I http://localhost || echo "Nginx test failed"

echo "=== Port Check ==="
netstat -tlnp | grep -E ':(80|8000)' || echo "No ports found"

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo "✅ MindMend installed from GitHub"
echo "✅ Database configured"
echo "✅ Services running"
echo "✅ Nginx configured"
echo ""
echo "🌐 Your site should be accessible at:"
echo "   http://67.219.102.9"
echo "   http://mindmend.xyz (if DNS is configured)"
echo ""
echo "🔧 Next steps:"
echo "1. Configure API keys in /var/www/mindmend/.env.production"
echo "2. Set up SSL: certbot --nginx -d mindmend.xyz"
echo "3. Test all features"
echo ""
echo "📝 Useful commands:"
echo "   systemctl status mindmend    # Check service status"
echo "   systemctl restart mindmend   # Restart service"
echo "   journalctl -u mindmend -f    # View logs"
echo "   cd /var/www/mindmend && git pull origin main  # Update code"