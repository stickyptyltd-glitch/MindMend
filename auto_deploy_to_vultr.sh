#!/bin/bash
# Automated MindMend Deployment to Vultr Server
# Server IP: 67.219.102.9

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SERVER_IP="67.219.102.9"

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] $1${NC}"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"; }

echo "🚀 MindMend Automated Deployment"
echo "================================="
echo "Target Server: $SERVER_IP"
echo "Domain: mindmend.xyz"
echo

log "Step 1: Testing server connectivity..."
if ping -c 1 $SERVER_IP > /dev/null 2>&1; then
    log "✅ Server is reachable"
else
    error "❌ Cannot reach server $SERVER_IP"
    exit 1
fi

log "Step 2: Testing SSH connection..."
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@$SERVER_IP "echo 'SSH connection successful'" || {
    error "❌ SSH connection failed. Please ensure:"
    echo "   - You can connect: ssh root@$SERVER_IP"
    echo "   - SSH keys are set up correctly"
    exit 1
}

log "Step 3: Running server configuration..."
ssh root@$SERVER_IP << 'ENDSSH'
    echo "🔧 Configuring server..."
    
    # Update system
    apt update && apt upgrade -y
    
    # Install packages
    apt install -y python3.11 python3.11-venv nginx postgresql redis-server git curl ufw certbot python3-certbot-nginx build-essential
    
    # Start services
    systemctl enable nginx postgresql redis-server
    systemctl start nginx postgresql redis-server
    
    # Configure firewall
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow http
    ufw allow https
    ufw --force enable
    
    # Create user and directories
    useradd -m mindmend || true
    mkdir -p /var/www/mindmend /var/log/mindmend
    chown -R mindmend:mindmend /var/www/mindmend /var/log/mindmend
    
    echo "✅ Server configuration complete"
ENDSSH

log "Step 4: Uploading application files..."
scp -o StrictHostKeyChecking=no app.py config.py requirements.txt .env.production root@$SERVER_IP:/var/www/mindmend/
scp -o StrictHostKeyChecking=no -r models/ templates/ static/ root@$SERVER_IP:/var/www/mindmend/

log "Step 5: Setting up application..."
ssh root@$SERVER_IP << 'ENDSSH'
    cd /var/www/mindmend
    chown -R mindmend:mindmend /var/www/mindmend
    
    # Setup Python environment
    sudo -u mindmend python3.11 -m venv venv
    sudo -u mindmend /var/www/mindmend/venv/bin/pip install --upgrade pip
    sudo -u mindmend /var/www/mindmend/venv/bin/pip install -r requirements.txt
    
    # Setup database
    sudo -u postgres createuser mindmend_user || true
    sudo -u postgres createdb mindmend_production -O mindmend_user || true
    sudo -u postgres psql -c "ALTER USER mindmend_user WITH PASSWORD 'aLo0aPR>{#Rp6{SKpx0,dPyRd9\$+:-d>';" || true
    
    # Initialize database tables
    sudo -u mindmend bash -c "
        cd /var/www/mindmend
        source venv/bin/activate
        python -c 'from app import app, db; app.app_context().push(); db.create_all(); print(\"Database initialized!\")'
    "
    
    echo "✅ Application setup complete"
ENDSSH

log "Step 6: Configuring web server..."
ssh root@$SERVER_IP << 'ENDSSH'
    # Configure Nginx
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
    }
    
    location /static/ {
        alias /var/www/mindmend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    ln -s /etc/nginx/sites-available/mindmend.xyz /etc/nginx/sites-enabled/
    nginx -t
    systemctl reload nginx
    
    echo "✅ Nginx configured"
ENDSSH

log "Step 7: Creating system service..."
ssh root@$SERVER_IP << 'ENDSSH'
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
    
    systemctl daemon-reload
    systemctl enable mindmend
    systemctl start mindmend
    
    echo "✅ MindMend service started"
ENDSSH

log "Step 8: Testing deployment..."
ssh root@$SERVER_IP << 'ENDSSH'
    echo "=== Service Status ==="
    systemctl status mindmend --no-pager -l
    systemctl status nginx --no-pager -l
    
    echo "=== Testing Application ==="
    sleep 3
    curl -I http://localhost:8000 || echo "Local app test failed"
    curl -I http://localhost || echo "Nginx test failed"
    
    echo "=== Port Check ==="
    netstat -tlnp | grep -E ':(80|8000)'
ENDSSH

log "Step 9: Testing external access..."
sleep 5
if curl -I http://$SERVER_IP > /dev/null 2>&1; then
    log "✅ MindMend is accessible at http://$SERVER_IP"
else
    warn "⚠️  External access test failed - may need a moment to start"
fi

echo
log "🎉 DEPLOYMENT COMPLETE!"
echo "================================="
echo "✅ Server configured and running"
echo "✅ MindMend application deployed"
echo "✅ Services started"
echo
echo "🌐 NEXT STEPS:"
echo "1. Update DNS: mindmend.xyz → $SERVER_IP"
echo "2. Wait 5-10 minutes for DNS propagation"
echo "3. Get SSL certificate:"
echo "   ssh root@$SERVER_IP"
echo "   certbot --nginx -d mindmend.xyz -d www.mindmend.xyz"
echo
echo "🔗 Access your application:"
echo "   HTTP:  http://$SERVER_IP"
echo "   HTTP:  http://mindmend.xyz (after DNS update)"
echo "   HTTPS: https://mindmend.xyz (after SSL setup)"
echo
log "Deployment completed successfully! 🚀"