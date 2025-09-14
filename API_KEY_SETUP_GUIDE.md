# 🔐 MindMend Production API Keys Setup Guide

## 🎯 **REQUIRED API KEYS FOR PRODUCTION**

### 1. 🤖 OpenAI API Key
**Current Status**: ⚠️ Demo key placeholder
**File**: `.env.production` line 25

**Steps to Get Production Key:**
```bash
1. Go to: https://platform.openai.com/api-keys
2. Log in to your OpenAI account
3. Click "Create new secret key"
4. Name it "MindMend Production"
5. Copy the key (starts with sk-proj-... or sk-...)
```

**Update Command:**
```bash
# Replace the demo key in .env.production
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
```

### 2. 💳 Stripe API Keys (LIVE Environment)
**Current Status**: ⚠️ Placeholder values
**File**: `.env.production` lines 31-33

**Steps to Get Live Stripe Keys:**
```bash
1. Go to: https://dashboard.stripe.com/
2. Switch to "Live" mode (top right toggle)
3. Go to Developers > API keys
4. Copy both:
   - Secret key (sk_live_...)
   - Publishable key (pk_live_...)
5. Go to Developers > Webhooks > Add endpoint
6. Add endpoint: https://mindmend.xyz/webhook/stripe
7. Select events: payment_intent.succeeded, payment_intent.payment_failed
8. Copy the webhook secret (whsec_...)
```

**Update Commands:**
```bash
# Replace in .env.production
STRIPE_SECRET_KEY=sk_live_your_actual_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_stripe_publishable_key  
STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_secret
```

### 3. 📧 Email Configuration (Optional but Recommended)
**Current Status**: ✅ Configured for sticky.pty.ltd@gmail.com
**File**: `.env.production` lines 47-53

**If using different email:**
```bash
MAIL_USERNAME=your-production-email@domain.com
MAIL_PASSWORD=your-app-password-here
```

---

## 🚀 **QUICK SETUP SCRIPT**

Save this as `update_api_keys.sh` and run after getting your keys:

```bash
#!/bin/bash
echo "🔐 MindMend API Keys Update"

read -p "Enter your OpenAI API key (sk-...): " OPENAI_KEY
read -p "Enter your Stripe Secret Key (sk_live_...): " STRIPE_SECRET
read -p "Enter your Stripe Publishable Key (pk_live_...): " STRIPE_PUBLIC
read -p "Enter your Stripe Webhook Secret (whsec_...): " STRIPE_WEBHOOK

# Update .env.production
sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=${OPENAI_KEY}/" .env.production
sed -i "s/STRIPE_SECRET_KEY=.*/STRIPE_SECRET_KEY=${STRIPE_SECRET}/" .env.production  
sed -i "s/STRIPE_PUBLISHABLE_KEY=.*/STRIPE_PUBLISHABLE_KEY=${STRIPE_PUBLIC}/" .env.production
sed -i "s/STRIPE_WEBHOOK_SECRET=.*/STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK}/" .env.production

echo "✅ API keys updated successfully!"
echo "🚀 Ready for production deployment!"
```

---

## ✅ **VERIFICATION CHECKLIST**

After updating keys, run deployment checks:
```bash
python3 deploy.py --check-only
```

Expected results:
- ✅ OpenAI API key configured
- ✅ Stripe keys configured
- ✅ Production SECRET_KEY configured
- ⚠️  Cannot verify SSL certificate (normal until server is set up)

---

## 🔒 **SECURITY NOTES**

1. **Never commit real API keys to git**
2. **Use environment variables only**  
3. **Stripe live keys handle real money - test thoroughly**
4. **Keep webhook secrets secure**
5. **Monitor API usage and billing**

---

## 📞 **NEXT STEPS**

1. ✅ Get API keys from OpenAI and Stripe
2. ✅ Update `.env.production` with real values
3. ✅ Run deployment checks to verify
4. 🚀 Deploy to server once infrastructure is ready

**Ready for deployment once server at 45.32.244.187 is configured!**