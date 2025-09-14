#!/bin/bash
# MindMend API Keys Update Script
# ==============================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'  
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}$1${NC}"; }
warn() { echo -e "${YELLOW}$1${NC}"; }
error() { echo -e "${RED}$1${NC}"; exit 1; }

echo "🔐 MindMend Production API Keys Update"
echo "======================================"
echo

# Check if .env.production exists
if [[ ! -f .env.production ]]; then
    error "❌ .env.production file not found!"
fi

# Backup current env file
cp .env.production .env.production.backup
log "✅ Created backup: .env.production.backup"

echo "Please provide your production API keys:"
echo

# Get OpenAI API Key
echo -n "🤖 OpenAI API Key (sk-proj-... or sk-...): "
read -r OPENAI_KEY
if [[ ! $OPENAI_KEY =~ ^sk- ]]; then
    error "❌ Invalid OpenAI API key format (must start with sk-)"
fi

# Get Stripe Secret Key
echo -n "💳 Stripe Secret Key (sk_live_...): "
read -r STRIPE_SECRET
if [[ ! $STRIPE_SECRET =~ ^sk_live_ ]]; then
    error "❌ Invalid Stripe secret key format (must start with sk_live_)"
fi

# Get Stripe Publishable Key
echo -n "🔑 Stripe Publishable Key (pk_live_...): "
read -r STRIPE_PUBLIC
if [[ ! $STRIPE_PUBLIC =~ ^pk_live_ ]]; then
    error "❌ Invalid Stripe publishable key format (must start with pk_live_)"
fi

# Get Stripe Webhook Secret
echo -n "🔗 Stripe Webhook Secret (whsec_...): "
read -r STRIPE_WEBHOOK
if [[ ! $STRIPE_WEBHOOK =~ ^whsec_ ]]; then
    error "❌ Invalid Stripe webhook secret format (must start with whsec_)"
fi

echo
log "🔄 Updating API keys in .env.production..."

# Update the environment file
sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=${OPENAI_KEY}|" .env.production
sed -i "s|STRIPE_SECRET_KEY=.*|STRIPE_SECRET_KEY=${STRIPE_SECRET}|" .env.production
sed -i "s|STRIPE_PUBLISHABLE_KEY=.*|STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLIC}|" .env.production
sed -i "s|STRIPE_WEBHOOK_SECRET=.*|STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK}|" .env.production

echo
log "✅ API keys updated successfully!"
echo

# Run deployment checks
log "🔍 Running deployment validation..."
if python3 -c "from deploy import MindMendDeployment; d = MindMendDeployment(); d.pre_deployment_checks()"; then
    echo
    log "🚀 All checks passed! Ready for production deployment."
    echo
    log "Next Steps:"
    echo "1. Ensure server at 45.32.244.187 is configured"
    echo "2. Run: python3 deploy.py"
    echo "3. Configure SSL certificate"
    echo "4. Test the live application"
else
    warn "⚠️  Some deployment checks failed. Review the output above."
fi

echo
log "💾 Backup saved as: .env.production.backup"
echo "🔐 Production API keys configured successfully!"