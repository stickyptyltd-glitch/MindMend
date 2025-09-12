# Mind Mend Deployment Guide
## Target: mind-mend.xyz → stickyplates.net (cPanel)

### Pre-Deployment Security & Testing Status ✓

**Security Audit Results:**
- ✓ 7 environment secrets properly configured
- ✓ Database connectivity verified (11 tables)
- ✓ OpenAI API integration functional
- ✓ Stripe payment keys configured
- ✓ Core endpoints responding (200/302 status codes)
- ✓ Static assets and logos secure (12 files)
- ✓ No LSP errors or code issues detected

## Deployment Steps for cPanel

### 1. File Structure Preparation
```
mind_mend/
├── public_html/          # Web root for mind-mend.xyz
│   ├── static/          # CSS, JS, images, logos
│   ├── templates/       # HTML templates
│   ├── .htaccess        # URL rewriting and security
│   └── index.php        # Entry point (redirects to Python)
├── app/                 # Python application (outside public_html)
│   ├── main.py         # Flask entry point
│   ├── app.py          # Main application
│   ├── admin_panel.py  # Admin interface
│   ├── models/         # AI models and database
│   ├── requirements.txt # Python dependencies
│   └── config.py       # Environment configuration
└── logs/               # Application logs
```

### 2. cPanel Configuration Requirements

**Python App Setup:**
- Python Version: 3.8+
- Entry Point: main.py
- Application Root: /app/
- Static Files: /public_html/static/

**Environment Variables:**
```bash
OPENAI_API_KEY=your_openai_key
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_PUBLISHABLE_KEY=your_stripe_public
DATABASE_URL=sqlite:///mind_mend.db
SESSION_SECRET=your_session_secret
FLASK_ENV=production
REPLIT_DOMAINS=mind-mend.xyz
```

### 3. Database Setup
- SQLite database file: `mind_mend.db`
- Location: `/app/` directory (secure, outside web root)
- Backup: Include in deployment package

### 4. DNS & Domain Configuration
```
mind-mend.xyz → CNAME → stickyplates.net
www.mind-mend.xyz → CNAME → stickyplates.net
```

### 5. SSL Certificate
- Enable AutoSSL in cPanel
- Force HTTPS redirects via .htaccess

### 6. Required .htaccess Configuration
```apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Static file handling
RewriteCond %{REQUEST_URI} ^/static/
RewriteRule ^static/(.*)$ /static/$1 [L]

# Python app routing
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /app.py/$1 [QSA,L]
```

### 7. Performance Optimization
- Enable gzip compression
- Set cache headers for static assets
- Configure Python app with proper WSGI server

### 8. Security Headers
```apache
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
```

## Post-Deployment Checklist

### Functional Testing:
- [ ] Homepage loads correctly
- [ ] Admin panel accessible
- [ ] AI therapy sessions working
- [ ] Payment integration functional
- [ ] Media pack downloads
- [ ] Company documents upload
- [ ] Email notifications
- [ ] Database operations

### Security Verification:
- [ ] HTTPS enabled
- [ ] Security headers active
- [ ] Admin authentication required
- [ ] Environment variables secure
- [ ] File permissions correct

### Performance Monitoring:
- [ ] Page load times < 3 seconds
- [ ] AI response times < 5 seconds
- [ ] Database queries optimized
- [ ] Static assets cached

## Support Information

**Business Details:**
- Company: Sticky Pty Ltd
- Address: Suite 329/98-100 Elizabeth Street, Melbourne, VIC, 3000
- Email: sticky.pty.ltd@gmail.com
- Domain: mind-mend.xyz → stickyplates.net

**Technical Stack:**
- Framework: Flask (Python)
- Database: SQLite
- AI: OpenAI GPT-4o
- Payments: Stripe
- Hosting: cPanel/Linux

## Backup & Recovery
- Database: Daily SQLite backups
- Code: Git repository maintained
- Assets: Media files backed up
- Logs: Rotated weekly

---
**Deployment Status:** Ready for Production
**Last Updated:** August 2, 2025
**Version:** Level 2 Enhanced with Admin AI