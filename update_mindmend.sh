#!/bin/bash
# Update MindMend server with Stage 2+3 features
set -e

SERVER_IP="67.219.102.9"
SERVER_USER="root"

echo "🚀 Updating MindMend with Stage 2+3 Features"
echo "=============================================="

echo "📤 Uploading essential files..."

# Upload all critical files in one go
scp -o StrictHostKeyChecking=no \
    admin_panel.py \
    biometric_api.py \
    emotion_detection_api.py \
    crisis_intervention_api.py \
    speaking_avatar_api.py \
    app.py \
    ${SERVER_USER}@${SERVER_IP}:/var/www/mindmend/

# Upload models and static files
scp -o StrictHostKeyChecking=no models/database.py ${SERVER_USER}@${SERVER_IP}:/var/www/mindmend/models/
scp -o StrictHostKeyChecking=no static/js/speaking-avatar.js ${SERVER_USER}@${SERVER_IP}:/var/www/mindmend/static/js/ 
scp -o StrictHostKeyChecking=no templates/onboarding_reformed.html ${SERVER_USER}@${SERVER_IP}:/var/www/mindmend/templates/

echo "🔄 Restarting MindMend service..."

# Restart service with proper error handling
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
cd /var/www/mindmend
systemctl restart mindmend.service
sleep 3
systemctl status mindmend.service --no-pager -l
ENDSSH

echo "✅ Update completed!"

# Test the service
echo "🧪 Testing MindMend service..."
if curl -f -s http://${SERVER_IP}/ > /dev/null; then
    echo "✅ SUCCESS! MindMend is running with Stage 2+3 features"
    echo ""
    echo "🌐 Access your platform:"
    echo "   Main app: http://${SERVER_IP}/"
    echo "   Admin panel: http://${SERVER_IP}/admin"
    echo ""
    echo "🔑 Admin Login:"
    echo "   Username: mindmend_admin"
    echo "   Password: MindMend2024!SecureAdmin"
else
    echo "❌ Service test failed. Checking logs..."
    ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "journalctl -u mindmend.service -n 20 --no-pager"
fi
