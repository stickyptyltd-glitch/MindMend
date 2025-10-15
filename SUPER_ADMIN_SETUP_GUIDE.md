# Super Admin Setup Guide
**Date**: October 15, 2025
**For**: MindMend Platform Owner

---

## 🎯 Quick Start

You now have two admin accounts ready:

1. **Super Admin** (YOU) - For production use
2. **General Admin Roles** - For delegating tasks to team members

---

## 🔐 Step 1: Create Your Super Admin Account

### Option A: Interactive Script (Recommended)

```bash
cd /home/mindmendxyz/MindMend
python3 create_super_admin.py
```

**You'll be prompted for**:
- Email address (e.g., your@email.com)
- Full name
- Password (min 8 characters)
- Password confirmation

The script will:
- ✅ Create super_admin account
- ✅ Auto-verify email
- ✅ Store hashed password
- ✅ Display credentials

### Option B: Direct Database Insert

If you prefer to create it directly in the database:

```bash
# Connect to PostgreSQL
kubectl exec -it deployment/postgres-75b54f6ff9-x29gj -n default -- \
  psql -U mindmend_user -d mindmend_production

# Generate password hash first (Python):
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('YOUR_PASSWORD'))"

# Then in psql:
INSERT INTO admin_user (email, name, password_hash, role, is_active, email_verified, created_at)
VALUES (
  'your@email.com',
  'Your Name',
  'PASTE_HASH_HERE',
  'super_admin',
  true,
  true,
  NOW()
);
```

---

## 📧 Step 2: Configure Email (Optional but Recommended)

Email is needed for:
- Professional application notifications
- Password resets
- System alerts
- Audit notifications

### Option A: Gmail SMTP (Easiest)

1. **Create Gmail App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Create app password for "Mail"
   - Copy the 16-character password

2. **Add to Kubernetes Secret**:
```bash
# Update secret with your Gmail credentials
kubectl patch secret mindmend-secrets -n default --type='json' -p='[
  {"op": "add", "path": "/data/EMAIL_HOST", "value": "'$(echo -n "smtp.gmail.com" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_PORT", "value": "'$(echo -n "587" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_USER", "value": "'$(echo -n "your-email@gmail.com" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_PASSWORD", "value": "'$(echo -n "your-app-password" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_FROM", "value": "'$(echo -n "MindMend <your-email@gmail.com>" | base64)'"}
]'
```

3. **Restart Backend Pods**:
```bash
kubectl rollout restart deployment/mindmend-backend -n default
```

### Option B: SendGrid (Production Recommended)

1. **Get SendGrid API Key**:
   - Sign up at https://sendgrid.com
   - Create API key
   - Verify sender email

2. **Configure Secret**:
```bash
kubectl patch secret mindmend-secrets -n default --type='json' -p='[
  {"op": "add", "path": "/data/EMAIL_HOST", "value": "'$(echo -n "smtp.sendgrid.net" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_PORT", "value": "'$(echo -n "587" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_USER", "value": "'$(echo -n "apikey" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_PASSWORD", "value": "'$(echo -n "YOUR_SENDGRID_API_KEY" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_FROM", "value": "'$(echo -n "MindMend <noreply@mindmend.xyz>" | base64)'"}
]'
```

### Option C: Custom SMTP Server

```bash
kubectl patch secret mindmend-secrets -n default --type='json' -p='[
  {"op": "add", "path": "/data/EMAIL_HOST", "value": "'$(echo -n "your.smtp.server" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_PORT", "value": "'$(echo -n "587" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_USER", "value": "'$(echo -n "username" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_PASSWORD", "value": "'$(echo -n "password" | base64)'"},
  {"op": "add", "path": "/data/EMAIL_FROM", "value": "'$(echo -n "MindMend <noreply@yourdomain.com>" | base64)'"}
]'
```

---

## 🎯 Step 3: Login and Test

### Login as Super Admin

1. **Access Admin Panel**:
   ```
   http://34.143.177.214/admin/login
   ```

2. **Enter Your Credentials**:
   - Email: (what you created)
   - Password: (what you set)

3. **Verify Permissions**:
   - You should see ALL admin menu items
   - Dashboard, Users, Finance, Subscriptions, AI, Professionals

### Test Professional Management

1. **Navigate to Professional Management**:
   ```
   http://34.143.177.214/professional/admin/applications
   ```

2. **Verify Access**:
   - As super_admin, you should have full access
   - Can view applications
   - Can approve/reject
   - Can manage professionals

---

## 👥 Step 4: Delegate to Team Members (Optional)

Create additional admin accounts with specific roles:

### Finance Admin
```python
python3 -c "
from app import app, db
from models.database import AdminUser

with app.app_context():
    admin = AdminUser(
        email='finance@mindmend.xyz',
        name='Finance Team',
        role='finance_admin',
        is_active=True,
        email_verified=True
    )
    admin.set_password('SecurePassword123!')
    db.session.add(admin)
    db.session.commit()
    print('Finance admin created!')
"
```

### Support Admin
```python
python3 -c "
from app import app, db
from models.database import AdminUser

with app.app_context():
    admin = AdminUser(
        email='support@mindmend.xyz',
        name='Support Team',
        role='support_admin',
        is_active=True,
        email_verified=True
    )
    admin.set_password('SecurePassword123!')
    db.session.add(admin)
    db.session.commit()
    print('Support admin created!')
"
```

### AI Admin
```python
python3 -c "
from app import app, db
from models.database import AdminUser

with app.app_context():
    admin = AdminUser(
        email='ai@mindmend.xyz',
        name='AI Team',
        role='ai_admin',
        is_active=True,
        email_verified=True
    )
    admin.set_password('SecurePassword123!')
    db.session.add(admin)
    db.session.commit()
    print('AI admin created!')
"
```

---

## 🔐 Admin Roles & Permissions

### Your Role: `super_admin`

**Permissions**: `['*']` (ALL)

You can access:
- ✅ **Dashboard** - Full platform overview
- ✅ **Users** - View, edit, delete, impersonate all users
- ✅ **Finance** - Revenue, expenses, forecasting, reports
- ✅ **Subscriptions** - Manage all subscriptions and payments
- ✅ **AI Management** - Models, training, testing, deployment
- ✅ **Professional Management** - Applications, credentials, compliance
- ✅ **System** - Server health, logs, configurations
- ✅ **API Management** - API keys, rate limits, webhooks
- ✅ **Marketing** - Campaigns, emails, analytics
- ✅ **Compliance** - HIPAA, audit logs, security events

### Delegated Roles

#### `finance_admin` (Level 80)
- Finance dashboard
- Subscriptions & payments
- Revenue analytics
- User viewing (read-only)

#### `ai_admin` (Level 70)
- AI models & training
- Model deployment
- Performance analytics
- User viewing (read-only)

#### `support_admin` (Level 60)
- User management (full)
- User impersonation
- Support tickets
- Analytics viewing
- **Professional management** ✅

#### `content_admin` (Level 50)
- Marketing campaigns
- Email management
- Content publishing
- Analytics viewing

---

## 📊 What You Can Do Now

### Immediate Actions

1. ✅ **Login to Admin Panel**
   - http://34.143.177.214/admin/login
   - Use your super_admin credentials

2. ✅ **Review Platform Metrics**
   - Total users
   - Active sessions
   - Revenue (if any subscriptions)
   - System health

3. ✅ **Test Professional Portal**
   - http://34.143.177.214/professional/apply
   - Submit test application
   - Review and approve it
   - Check email sent (if configured)

4. ✅ **Manage Users**
   - View all users
   - Edit profiles
   - Manage subscriptions
   - Run analytics

### Weekly Tasks

- Monitor professional applications
- Review session quality (from professional reviews)
- Check compliance alerts (expiring licenses)
- Review financial reports
- Monitor AI performance

### Monthly Tasks

- Process professional payments
- Review platform analytics
- Update AI models if needed
- Compliance reporting
- User satisfaction surveys

---

## 🚀 Professional Recruitment Workflow

Once email is configured, you can start recruiting professionals:

### 1. Share Application Link
```
http://34.143.177.214/professional/apply
```

### 2. Review Applications
- Login as super_admin
- Navigate to `/professional/admin/applications`
- Review applicant credentials

### 3. Approve Qualified Applicants
- Click "Approve"
- Add review notes
- System sends approval email automatically

### 4. Professional Registers
- Receives email with registration link
- Sets password
- Completes profile
- Submits credentials

### 5. Verify Credentials
- Navigate to `/professional/admin/professional/<id>`
- Review submitted documents
- Verify license/credentials
- Activate professional

### 6. Professional Active
- Can login at `/professional/login`
- Reviews assigned AI sessions
- Provides clinical oversight
- Earns compensation

---

## 📧 Email Templates Included

Professional portal includes professional HTML email templates:

### Approval Email
- Congratulations message
- Registration link (7-day validity)
- Next steps guidance
- Professional branding

### Rejection Email
- Professional tone
- Constructive feedback (if provided)
- Reapplication guidance
- Encouragement

---

## 🔒 Security Best Practices

### For Super Admin Account

1. **Strong Password**:
   - Min 12 characters
   - Mix of letters, numbers, symbols
   - Don't reuse passwords

2. **Secure Storage**:
   - Use password manager
   - Don't share credentials
   - Rotate password quarterly

3. **Access Logging**:
   - All actions logged to audit trail
   - Review logs regularly
   - Monitor for suspicious activity

4. **IP Whitelisting** (Optional):
   - Configure in `admin/auth.py`
   - Restrict admin access by IP
   - Useful for corporate networks

### For Email Configuration

1. **Use App Passwords**:
   - Never use account password
   - Use app-specific passwords
   - Rotate periodically

2. **Secure SMTP**:
   - Always use TLS (port 587)
   - Never use plain SMTP (port 25)
   - Monitor email logs

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Super admin account created
- [ ] Can login to admin panel
- [ ] Dashboard displays metrics
- [ ] Can access all admin sections
- [ ] Email configured (optional)
- [ ] Email test successful (if configured)
- [ ] Professional portal accessible
- [ ] Can review professional applications
- [ ] Audit logging working
- [ ] All permissions functional

---

## 🐛 Troubleshooting

### Can't Login

**Issue**: "Invalid credentials" error

**Solutions**:
1. Verify email is lowercase
2. Check password was set correctly
3. Ensure `is_active=true` in database
4. Check AdminUser table exists

**Query to check**:
```sql
SELECT email, role, is_active FROM admin_user WHERE role='super_admin';
```

### Email Not Sending

**Issue**: Emails not being received

**Solutions**:
1. Check email configuration in secret
2. Verify SMTP credentials correct
3. Check application logs for errors
4. Test SMTP connection:
```bash
kubectl logs deployment/mindmend-backend -n default | grep -i email
```

### Permission Denied

**Issue**: "Insufficient permissions" message

**Solutions**:
1. Verify role is 'super_admin' (not 'admin')
2. Check session has admin_role set
3. Clear browser cookies and re-login
4. Verify decorators applied to routes

---

## 📞 Support

**Documentation**:
- Admin Panel: `/admin` routes
- Professional Portal: `PROFESSIONAL_PORTAL_COMPLETE.md`
- Endpoint Testing: `ENDPOINT_TESTING_RESULTS.md`

**Quick Commands**:
```bash
# Check admin users
kubectl exec -it deployment/postgres-75b54f6ff9-x29gj -n default -- \
  psql -U mindmend_user -d mindmend_production -c "SELECT * FROM admin_user;"

# Check email config
kubectl get secret mindmend-secrets -n default -o jsonpath='{.data.EMAIL_HOST}' | base64 -d

# View application logs
kubectl logs deployment/mindmend-backend -n default --tail=100

# Restart backend
kubectl rollout restart deployment/mindmend-backend -n default
```

---

## 🎉 You're All Set!

Your MindMend platform now has:

✅ **Super Admin Access** - Full control over platform
✅ **Role-Based Delegation** - Team member management ready
✅ **Professional Portal** - Licensed professional oversight
✅ **Email Notifications** - Automated communication
✅ **Comprehensive Analytics** - Full platform visibility
✅ **Enterprise Security** - Audit logging, access control

**Next Steps**: Choose your focus area and start managing your mental health platform!

---

**Created**: October 15, 2025
**Version**: 1.0
**Status**: Production Ready
