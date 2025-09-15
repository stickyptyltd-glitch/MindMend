#!/bin/bash

# Deploy MindMend from Git to Production Server
# This script pulls latest changes from git and deploys to mindmend.xyz

set -e

echo "🚀 Deploying MindMend from Git to Production"
echo "============================================="

SERVER_IP="67.219.102.9"
SERVER_USER="root"
APP_PATH="/var/www/mindmend"
REPO_URL="https://github.com/stickyptyltd-glitch/MindMend.git"

echo "📋 Deployment Configuration:"
echo "   Server: ${SERVER_IP}"
echo "   Path: ${APP_PATH}"
echo "   User: ${SERVER_USER}"
echo "   Repository: ${REPO_URL}"
echo ""

# Create deployment commands
DEPLOY_COMMANDS="
cd ${APP_PATH} && \
echo '📥 Pulling latest changes from git...' && \
git pull origin main && \
echo '📦 Installing dependencies...' && \
pip install -r requirements.txt && \
echo '🔄 Restarting MindMend service...' && \
systemctl restart mindmend.service && \
sleep 3 && \
echo '✅ Service restarted successfully' && \
systemctl status mindmend.service --no-pager -l
"

echo "🚀 Executing deployment on server..."
if timeout 60 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 ${SERVER_USER}@${SERVER_IP} "${DEPLOY_COMMANDS}"; then
    echo ""
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "🧪 Testing deployment..."

    # Test the deployment
    if curl -f -s https://mindmend.xyz/health > /dev/null; then
        echo "✅ Health check passed - https://mindmend.xyz is responding"
        echo ""
        echo "🌐 Your updated MindMend platform is now live at:"
        echo "   🏠 Main Site: https://mindmend.xyz"
        echo "   ⚕️  Health: https://mindmend.xyz/health"
        echo "   🔧 Admin: https://mindmend.xyz/admin"
        echo ""
        echo "🇦🇺 Australian emergency numbers are now active:"
        echo "   📞 Lifeline Australia: 13 11 14"
        echo "   💬 Crisis Text: 0477 13 11 14"
        echo "   🚨 Emergency: 000"
        echo "   💙 Beyond Blue: 1300 22 4636"
        echo ""
        echo "🎉 DEPLOYMENT SUCCESS!"
    else
        echo "⚠️  Health check failed - please verify manually"
    fi
else
    echo "❌ Deployment failed or timed out"
    echo "💡 Trying alternative deployment verification..."

    # Try to verify the current status
    if curl -f -s https://mindmend.xyz > /dev/null; then
        echo "✅ Site is still accessible at https://mindmend.xyz"
        echo "🔄 Changes may be deployed but service restart may have failed"
    else
        echo "❌ Site appears to be down - manual intervention may be required"
    fi
fi

echo ""
echo "📊 Final Status Check:"
echo "======================"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://mindmend.xyz)
RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" https://mindmend.xyz)
echo "HTTP Status: ${HTTP_STATUS}"
echo "Response Time: ${RESPONSE_TIME}s"
echo "Deployment completed at: $(date)"