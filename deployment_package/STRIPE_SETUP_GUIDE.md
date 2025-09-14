# 🔑 Complete Stripe Setup Guide for MindMend

## Step-by-Step Configuration Checklist

### 📝 Step 1: Create Stripe Account & Get API Keys

1. **Visit Stripe Dashboard**:
   - Go to https://dashboard.stripe.com
   - Sign up or log in to your account

2. **Switch to Live Mode**:
   ```
   ⚠️ IMPORTANT: Toggle "Test data" to "Live data" in top right corner
   ```

3. **Get Your Live API Keys**:
   - Navigate to: **Developers** → **API keys**
   - Copy these keys:

   ```bash
   # Your Publishable Key (starts with pk_live_)
   pk_live_51AbC123DEf456GhI789jKl012MnO345pQr678StU901VwX234yZ567aBc890DeF123

   # Your Secret Key (click "Reveal live key token")  
   sk_live_51AbC123DEf456GhI789jKl012MnO345pQr678StU901VwX234yZ567aBc890DeF123
   ```

### 🎯 Step 2: Create Subscription Products

1. **Navigate to Products**:
   - Go to **Products** → **Add product**

2. **Create Premium Subscription**:
   ```
   Product name: MindMend Premium
   Description: Advanced AI therapy with human counselor access
   
   Pricing Model: Recurring
   
   Monthly Price:
   - Amount: $29.99
   - Billing interval: Monthly
   - Copy Price ID: price_1AbC123DEf456GhI789jKl0
   
   Yearly Price:  
   - Amount: $299.99
   - Billing interval: Yearly
   - Copy Price ID: price_1XyZ789AbC123DeF456GhI0
   ```

3. **Create Enterprise Subscription**:
   ```
   Product name: MindMend Enterprise
   Description: Complete mental health platform for organizations
   
   Monthly Price:
   - Amount: $99.99  
   - Billing interval: Monthly
   - Copy Price ID: price_1MnO345PqR678StU901VwX2
   
   Yearly Price:
   - Amount: $999.99
   - Billing interval: Yearly  
   - Copy Price ID: price_1DeF789GhI012JkL345MnO6
   ```

### 🔗 Step 3: Setup Webhook Endpoint

1. **Create Webhook**:
   - Go to **Developers** → **Webhooks**
   - Click **"Add endpoint"**

2. **Configure Endpoint**:
   ```
   Endpoint URL: https://mindmend.xyz/payment/webhook
   Description: MindMend Payment Processing
   Version: Latest API version
   ```

3. **Select Events** (check these boxes):
   ```
   ✅ customer.subscription.created
   ✅ customer.subscription.updated  
   ✅ customer.subscription.deleted
   ✅ invoice.payment_succeeded
   ✅ invoice.payment_failed
   ✅ payment_intent.succeeded
   ```

4. **Get Webhook Secret**:
   - After creating, click on your webhook
   - Click **"Reveal"** next to "Signing secret"
   - Copy: `whsec_1AbC123DEf456GhI789jKl012MnO345pQr678StU`

### ⚙️ Step 4: Update MindMend Configuration

**Edit `.env.production` file with your actual values:**

```bash
# Replace these with your ACTUAL Stripe keys from Step 1
STRIPE_SECRET_KEY=sk_live_51AbC123DEf456GhI789jKl012MnO345pQr678StU901VwX234yZ567aBc890DeF123
STRIPE_PUBLISHABLE_KEY=pk_live_51AbC123DEf456GhI789jKl012MnO345pQr678StU901VwX234yZ567aBc890DeF123
STRIPE_WEBHOOK_SECRET=whsec_1AbC123DEf456GhI789jKl012MnO345pQr678StU

# Also update your OpenAI key for AI features
OPENAI_API_KEY=sk-your_actual_openai_api_key_here
```

**Edit `models/subscription_manager.py` with your Price IDs:**

Find these lines and replace with your actual Price IDs from Step 2:

```python
# Premium subscription price IDs (around line 46-47)
'stripe_price_id_monthly': 'price_1AbC123DEf456GhI789jKl0',    # Your Premium Monthly
'stripe_price_id_yearly': 'price_1XyZ789AbC123DeF456GhI0',     # Your Premium Yearly

# Enterprise subscription price IDs (around line 73-74)  
'stripe_price_id_monthly': 'price_1MnO345PqR678StU901VwX2',    # Your Enterprise Monthly
'stripe_price_id_yearly': 'price_1DeF789GhI012JkL345MnO6',     # Your Enterprise Yearly
```

### 🧪 Step 5: Test Configuration

1. **Run deployment checks**:
   ```bash
   python deploy.py check
   ```

2. **Test payment system**:
   ```bash
   source mindmend_env/bin/activate
   python test_payment_system.py
   ```

You should see:
```
✅ Database tables recreated with payment models  
✅ Created test user: premium@mindmend.com
📋 Available Subscription Tiers:
  FREE: $0.0/month - Basic AI therapy sessions
  PREMIUM: $29.99/month - Advanced AI therapy with human counselor access  
  ENTERPRISE: $99.99/month - Complete mental health platform for organizations
✅ Payment System Ready for Production!
```

### 🚀 Step 6: Deploy to Production

Once all keys are configured:

```bash
# Deploy to your server
python deploy.py deploy

# Or manually if you prefer:
rsync -avz ./ mindmend@your_server:/var/www/mindmend/
ssh mindmend@your_server 'sudo systemctl restart mindmend'
```

### ✅ Verification Checklist

After deployment, verify:

- [ ] Website loads: https://mindmend.xyz
- [ ] Pricing page shows correct tiers: https://mindmend.xyz/pricing  
- [ ] User can create account and login
- [ ] Subscription upgrade process works
- [ ] Stripe checkout redirects correctly
- [ ] Webhook endpoint receives events (check Stripe dashboard)
- [ ] Payment confirmations appear in admin panel

### 🔧 Troubleshooting

**If payments fail:**
1. Check Stripe dashboard for error details
2. Verify webhook endpoint is accessible: `curl https://mindmend.xyz/payment/webhook`
3. Check application logs: `sudo tail -f /var/log/mindmend/error.log`
4. Verify Price IDs match your Stripe products

**Common Issues:**
- **"No such price"**: Price IDs in `subscription_manager.py` don't match Stripe
- **"Invalid webhook signature"**: Webhook secret in `.env.production` is wrong
- **"API key invalid"**: Using test keys instead of live keys, or incorrect keys

### 📞 Support

If you encounter issues:
1. Check the **Stripe Dashboard** → **Logs** for detailed error messages
2. Review **MindMend logs** at `/var/log/mindmend/error.log`
3. Verify all configuration matches this guide exactly

---

## 🎯 Quick Configuration Summary

**What you need from Stripe:**
1. **Secret Key**: `sk_live_51...` (from API Keys)
2. **Publishable Key**: `pk_live_51...` (from API Keys)  
3. **Webhook Secret**: `whsec_1...` (from Webhooks)
4. **Premium Monthly Price ID**: `price_1...` (from Products)
5. **Premium Yearly Price ID**: `price_1...` (from Products)
6. **Enterprise Monthly Price ID**: `price_1...` (from Products)
7. **Enterprise Yearly Price ID**: `price_1...` (from Products)

**Where to put them:**
- Keys 1-3: `.env.production` file
- Price IDs 4-7: `models/subscription_manager.py` file

Once configured, MindMend will have full Stripe payment processing with fraud detection and security features! 🎉