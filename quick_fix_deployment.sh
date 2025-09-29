#!/usr/bin/env bash
# Quick fix deployment — upload only updated files and restart service
set -euo pipefail

SERVER_IP=${SERVER_IP:-"67.219.102.9"}
SSH_USER=${SSH_USER:-"root"}
DEST_DIR=${DEST_DIR:-"/var/www/mindmend"}

echo "🔧 Quick Fix Deployment"
echo "======================="
echo "Target: ${SSH_USER}@${SERVER_IP}:${DEST_DIR}"

echo "📤 Uploading updated backend files..."
scp -o StrictHostKeyChecking=no \
  app.py oauth_system.py models/database.py \
  ${SSH_USER}@${SERVER_IP}:${DEST_DIR}/

echo "📤 Uploading updated templates..."
scp -o StrictHostKeyChecking=no \
  templates/login.html \
  templates/register.html \
  templates/index.html \
  templates/ai_models.html \
  ${SSH_USER}@${SERVER_IP}:${DEST_DIR}/templates/

echo "🔁 Restarting service..."
ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SERVER_IP} \
  "cd ${DEST_DIR} && systemctl restart mindmend && systemctl status mindmend --no-pager || true"

echo "🩺 Health check (local on server)..."
ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SERVER_IP} \
  "curl -sS http://127.0.0.1:8000/health || echo 'Health endpoint unavailable'"

echo "🌐 Health check (public, may require DNS/SSL)..."
curl -sSI https://mindmend.xyz/health || true

echo "🌟 Quick fix deployment complete!"
