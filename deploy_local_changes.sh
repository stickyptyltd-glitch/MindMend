#!/bin/bash

# Deploy Local MindMend Changes to Production Server
# This script packages local changes and provides deployment options

set -e

SERVER_IP="67.219.102.9"
DEPLOYMENT_PACKAGE="mindmend_deployment_$(date +%Y%m%d_%H%M%S).tar.gz"

echo "🚀 MindMend Local Changes Deployment"
echo "===================================="
echo "Server: ${SERVER_IP}"
echo "Package: ${DEPLOYMENT_PACKAGE}"
echo ""

# Create deployment package
echo "📦 Creating deployment package..."
tar -czf "${DEPLOYMENT_PACKAGE}" \
    --exclude=__pycache__ \
    --exclude=.git \
    --exclude=.venv \
    --exclude=*.pyc \
    --exclude=*.log \
    --exclude=deployment_report.txt \
    --exclude=mindmend_deployment_*.tar.gz \
    app.py \
    models/ \
    templates/ \
    static/ \
    requirements.txt \
    config.py \
    admin_panel.py \
    payment_integration.py \
    counselor_dashboard.py \
    test_payment_system.py \
    test_advanced_systems.py

echo "✅ Package created: ${DEPLOYMENT_PACKAGE}"
echo "📊 Package size: $(du -h ${DEPLOYMENT_PACKAGE} | cut -f1)"

# Option 1: Try direct SCP upload
echo ""
echo "🔄 Attempting direct deployment..."

if timeout 30 scp -o StrictHostKeyChecking=no -o ConnectTimeout=10 "${DEPLOYMENT_PACKAGE}" root@${SERVER_IP}:/tmp/ 2>/dev/null; then
    echo "✅ Package uploaded successfully"

    # Deploy on server
    if timeout 60 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@${SERVER_IP} "
        cd /tmp &&
        tar -xzf ${DEPLOYMENT_PACKAGE} &&
        systemctl stop mindmend || true &&
        cp -r * /var/www/mindmend/ &&
        cd /var/www/mindmend &&
        chown -R mindmend:mindmend /var/www/mindmend &&
        sudo -u mindmend /var/www/mindmend/venv/bin/pip install -r requirements.txt &&
        systemctl start mindmend &&
        systemctl reload nginx &&
        rm -f /tmp/${DEPLOYMENT_PACKAGE}
    " 2>/dev/null; then
        echo "✅ Deployment completed successfully!"
        echo "🌐 Your changes are now live at https://mindmend.xyz"
    else
        echo "⚠️  Package uploaded but deployment command failed"
    fi
else
    echo "❌ Direct deployment failed"
    echo ""
    echo "🔧 ALTERNATIVE DEPLOYMENT OPTIONS:"
    echo ""
    echo "Option 1: Manual SCP Upload"
    echo "scp ${DEPLOYMENT_PACKAGE} root@${SERVER_IP}:/tmp/"
    echo ""
    echo "Option 2: Manual SSH Deployment"
    echo "ssh root@${SERVER_IP}"
    echo "cd /tmp && tar -xzf ${DEPLOYMENT_PACKAGE}"
    echo "systemctl stop mindmend"
    echo "cp -r * /var/www/mindmend/"
    echo "cd /var/www/mindmend && pip install -r requirements.txt"
    echo "systemctl start mindmend && systemctl reload nginx"
    echo ""
    echo "Option 3: Use web-based file manager (if available)"
    echo "Upload ${DEPLOYMENT_PACKAGE} through your hosting provider's control panel"
    echo ""
    echo "Option 4: Git-based deployment (if repo is set up)"
    echo "Push changes to git, then run on server: git pull origin main"
fi

echo ""
echo "📋 Deployment package ready: ${DEPLOYMENT_PACKAGE}"
echo "💡 If SSH isn't working, you can manually upload this package"
echo "🔧 The package contains all your latest local changes"