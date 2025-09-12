"""
Generate Mind Mend Admin Manual PDF
==================================
Creates a comprehensive user manual for administrators, managers, and counselors
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime

def create_admin_manual():
    """Generate the admin manual PDF"""
    
    # Create the PDF
    filename = "Mind_Mend_Admin_Manual.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667EEA'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667EEA'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#764BA2'),
        spaceAfter=10
    )
    
    # Title Page
    elements.append(Paragraph("Mind Mend Platform", title_style))
    elements.append(Paragraph("Comprehensive Admin Manual", title_style))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Version 2.0 - Enterprise Edition", styles['Normal']))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Paragraph("Sticky Pty Ltd", styles['Normal']))
    elements.append(PageBreak())
    
    # Table of Contents
    elements.append(Paragraph("Table of Contents", heading_style))
    toc_data = [
        ["1.", "Introduction and Overview", "3"],
        ["2.", "Security and Access Control", "5"],
        ["3.", "User Roles and Permissions", "8"],
        ["4.", "Admin Dashboard Guide", "12"],
        ["5.", "AI Fraud Detection System", "18"],
        ["6.", "User Management", "24"],
        ["7.", "Subscription Management", "30"],
        ["8.", "Financial Management", "36"],
        ["9.", "Platform Configuration", "42"],
        ["10.", "Counselor Management", "48"],
        ["11.", "System Monitoring", "54"],
        ["12.", "Troubleshooting Guide", "60"]
    ]
    
    toc_table = Table(toc_data, colWidths=[0.5*inch, 4*inch, 0.5*inch])
    toc_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(toc_table)
    elements.append(PageBreak())
    
    # Chapter 1: Introduction
    elements.append(Paragraph("1. Introduction and Overview", heading_style))
    elements.append(Paragraph(
        "Mind Mend is an enterprise-level mental health therapy platform designed to provide "
        "comprehensive AI-powered therapeutic support. This manual covers all administrative "
        "functions, security protocols, and management features.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("1.1 Key Features", subheading_style))
    features = [
        "• AI-powered therapy sessions with OpenAI GPT-4o integration",
        "• Real-time video assessment and emotion analysis",
        "• Comprehensive fraud detection and security monitoring",
        "• Multi-tier subscription management",
        "• Licensed counselor integration",
        "• HIPAA-compliant data handling",
        "• Advanced analytics and reporting"
    ]
    for feature in features:
        elements.append(Paragraph(feature, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("1.2 Platform Architecture", subheading_style))
    elements.append(Paragraph(
        "The platform is built on a secure, scalable architecture with role-based access control, "
        "real-time monitoring, and enterprise-grade security features. All data is encrypted "
        "at rest and in transit, with comprehensive audit logging.",
        styles['BodyText']
    ))
    elements.append(PageBreak())
    
    # Chapter 2: Security and Access Control
    elements.append(Paragraph("2. Security and Access Control", heading_style))
    elements.append(Paragraph(
        "Mind Mend implements a comprehensive security model with multiple layers of protection "
        "to ensure patient data privacy and platform integrity.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("2.1 Security Classes", subheading_style))
    
    # Security roles table
    security_data = [
        ["Role", "Security Level", "Session Timeout", "2FA Required", "IP Whitelist"],
        ["Super Admin", "100", "30 min", "Yes", "Yes"],
        ["Admin", "90", "60 min", "Yes", "No"],
        ["Manager", "70", "120 min", "No", "No"],
        ["Counselor", "50", "240 min", "No", "No"],
        ["Patient", "10", "480 min", "No", "No"]
    ]
    
    security_table = Table(security_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    security_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667EEA')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(security_table)
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("2.2 Password Requirements", subheading_style))
    password_req = [
        "• Super Admin: Minimum 16 characters with uppercase, lowercase, numbers, and special characters",
        "• Admin: Minimum 12 characters with complexity requirements",
        "• Manager: Minimum 10 characters",
        "• Counselor/Patient: Minimum 8 characters"
    ]
    for req in password_req:
        elements.append(Paragraph(req, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 3: User Roles and Permissions
    elements.append(Paragraph("3. User Roles and Permissions", heading_style))
    
    elements.append(Paragraph("3.1 Super Admin Permissions", subheading_style))
    super_admin_perms = [
        "• Full system access and configuration",
        "• API key management",
        "• Platform settings and upgrades",
        "• User management across all levels",
        "• Financial data access",
        "• Security configuration",
        "• Deployment management",
        "• Fraud detection system access"
    ]
    for perm in super_admin_perms:
        elements.append(Paragraph(perm, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("3.2 Admin Permissions", subheading_style))
    admin_perms = [
        "• User and counselor management",
        "• View financial reports",
        "• Access audit logs",
        "• Fraud detection monitoring",
        "• Generate platform reports",
        "• Handle support tickets"
    ]
    for perm in admin_perms:
        elements.append(Paragraph(perm, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("3.3 Manager Permissions", subheading_style))
    manager_perms = [
        "• Manage counselor schedules",
        "• View user analytics",
        "• Handle support tickets",
        "• Generate reports",
        "• Monitor platform usage"
    ]
    for perm in manager_perms:
        elements.append(Paragraph(perm, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 4: Admin Dashboard Guide
    elements.append(Paragraph("4. Admin Dashboard Guide", heading_style))
    
    elements.append(Paragraph("4.1 Accessing the Admin Panel", subheading_style))
    elements.append(Paragraph(
        "Navigate to /admin or /admin/login to access the admin panel. Use your assigned "
        "credentials to log in. Super admins and admins will be prompted for 2FA verification.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("4.2 Dashboard Components", subheading_style))
    dashboard_components = [
        "• Real-time Statistics: View active users, revenue, and system health",
        "• System Alerts: Monitor critical issues and warnings",
        "• Quick Actions: Access frequently used functions",
        "• Activity Feed: Recent platform activity and user actions",
        "• Performance Metrics: System performance and uptime statistics"
    ]
    for component in dashboard_components:
        elements.append(Paragraph(component, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("4.3 Navigation Menu", subheading_style))
    nav_items = [
        "• Dashboard: Main overview and statistics",
        "• API Keys: Configure external service integrations",
        "• Platform Upgrades: Access Level 3 and Enterprise features",
        "• Business Settings: Company and platform configuration",
        "• Users & Counselors: User management interface",
        "• Financial Overview: Revenue and payment analytics",
        "• System Monitoring: Health checks and performance",
        "• Deployment Tools: Production deployment options"
    ]
    for item in nav_items:
        elements.append(Paragraph(item, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 5: AI Fraud Detection
    elements.append(Paragraph("5. AI Fraud Detection System", heading_style))
    
    elements.append(Paragraph("5.1 Overview", subheading_style))
    elements.append(Paragraph(
        "The AI-powered fraud detection system monitors all platform activity in real-time, "
        "identifying suspicious patterns and automatically taking protective actions.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("5.2 Detection Categories", subheading_style))
    
    # Fraud detection table
    fraud_data = [
        ["Category", "Indicators", "Risk Score", "Auto Action"],
        ["Payment Fraud", "Rapid transactions, unusual amounts, card testing", "High", "Block transaction"],
        ["Account Fraud", "Suspicious emails, multiple failed logins", "Critical", "Lock account"],
        ["API Abuse", "Excessive requests, data scraping", "Medium", "Rate limit"],
        ["Session Hijacking", "Multiple concurrent sessions", "High", "Force logout"]
    ]
    
    fraud_table = Table(fraud_data, colWidths=[1.5*inch, 2.5*inch, 0.8*inch, 1.2*inch])
    fraud_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC143C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(fraud_table)
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("5.3 Risk Levels and Actions", subheading_style))
    risk_levels = [
        "• Critical (80-100): Immediate blocking and investigation",
        "• High (60-79): Require additional verification",
        "• Medium (40-59): Enhanced monitoring",
        "• Low (0-39): Standard monitoring"
    ]
    for level in risk_levels:
        elements.append(Paragraph(level, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 6: User Management
    elements.append(Paragraph("6. User Management", heading_style))
    
    elements.append(Paragraph("6.1 User Registration Process", subheading_style))
    elements.append(Paragraph(
        "New users can register through the platform with email verification. Admins can also "
        "manually create accounts and assign roles. All user data is encrypted and stored securely.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("6.2 Managing User Accounts", subheading_style))
    user_actions = [
        "• View all users: Access complete user list with filters",
        "• Edit user details: Update profile information and settings",
        "• Change subscription: Upgrade/downgrade user plans",
        "• Reset passwords: Force password reset for security",
        "• Suspend/activate: Temporarily disable or reactivate accounts",
        "• View activity: Check user session history and actions",
        "• Export data: Generate user reports for compliance"
    ]
    for action in user_actions:
        elements.append(Paragraph(action, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 7: Subscription Management
    elements.append(Paragraph("7. Subscription Management", heading_style))
    
    elements.append(Paragraph("7.1 Subscription Tiers", subheading_style))
    
    # Subscription table
    sub_data = [
        ["Tier", "Monthly Price", "Features", "User Limit"],
        ["Free", "$0", "Basic AI therapy, limited sessions", "1"],
        ["Premium", "$49", "Unlimited AI sessions, video assessment", "1"],
        ["Family", "$99", "All Premium features for up to 4 users", "4"],
        ["Enterprise", "Custom", "White label, API access, dedicated support", "Unlimited"]
    ]
    
    sub_table = Table(sub_data, colWidths=[1.2*inch, 1*inch, 2.8*inch, 1*inch])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667EEA')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("7.2 Managing Subscriptions", subheading_style))
    sub_management = [
        "• View active subscriptions with revenue metrics",
        "• Process upgrades and downgrades",
        "• Handle payment failures and retry logic",
        "• Configure trial periods and promotions",
        "• Set usage limits and quotas",
        "• Generate subscription reports"
    ]
    for item in sub_management:
        elements.append(Paragraph(item, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 8: Financial Management
    elements.append(Paragraph("8. Financial Management", heading_style))
    
    elements.append(Paragraph("8.1 Revenue Dashboard", subheading_style))
    elements.append(Paragraph(
        "The financial overview provides real-time revenue tracking, payment analytics, "
        "and forecasting tools. All financial data is updated hourly.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("8.2 Payment Processing", subheading_style))
    payment_info = [
        "• Stripe integration for credit/debit cards",
        "• PayPal support for alternative payments",
        "• Automatic retry for failed payments",
        "• PCI compliance through payment providers",
        "• Refund processing with audit trail",
        "• Chargeback handling and disputes"
    ]
    for info in payment_info:
        elements.append(Paragraph(info, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 9: Platform Configuration
    elements.append(Paragraph("9. Platform Configuration", heading_style))
    
    elements.append(Paragraph("9.1 API Keys Configuration", subheading_style))
    api_config = [
        "• OpenAI API Key: Required for AI therapy features",
        "• Stripe Keys: For payment processing",
        "• PayPal Credentials: Alternative payment method",
        "• Twilio: SMS notifications (optional)",
        "• SendGrid: Email delivery (optional)"
    ]
    for config in api_config:
        elements.append(Paragraph(config, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("9.2 Platform Settings", subheading_style))
    platform_settings = [
        "• Maintenance Mode: Temporarily disable platform access",
        "• Registration: Enable/disable new user signups",
        "• Feature Flags: Toggle specific features on/off",
        "• Email Templates: Customize system emails",
        "• Branding: Update logos and color schemes"
    ]
    for setting in platform_settings:
        elements.append(Paragraph(setting, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 10: Counselor Management
    elements.append(Paragraph("10. Counselor Management", heading_style))
    
    elements.append(Paragraph("10.1 Onboarding Counselors", subheading_style))
    counselor_onboard = [
        "• Verify credentials and licenses",
        "• Create counselor account with appropriate permissions",
        "• Assign specializations and availability",
        "• Configure payment rates and schedules",
        "• Provide platform training resources"
    ]
    for step in counselor_onboard:
        elements.append(Paragraph(step, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("10.2 Performance Monitoring", subheading_style))
    performance_metrics = [
        "• Session completion rates",
        "• Patient satisfaction scores",
        "• Response time metrics",
        "• Revenue per counselor",
        "• Compliance with protocols"
    ]
    for metric in performance_metrics:
        elements.append(Paragraph(metric, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 11: System Monitoring
    elements.append(Paragraph("11. System Monitoring", heading_style))
    
    elements.append(Paragraph("11.1 Health Checks", subheading_style))
    health_checks = [
        "• Server uptime and response times",
        "• Database performance metrics",
        "• API endpoint availability",
        "• Error rates and exceptions",
        "• Resource utilization (CPU, memory, disk)"
    ]
    for check in health_checks:
        elements.append(Paragraph(check, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("11.2 Alert Configuration", subheading_style))
    alerts = [
        "• Critical: System outages, security breaches",
        "• High: Payment failures, API errors",
        "• Medium: Performance degradation, high error rates",
        "• Low: Maintenance reminders, usage warnings"
    ]
    for alert in alerts:
        elements.append(Paragraph(alert, styles['BodyText']))
    elements.append(PageBreak())
    
    # Chapter 12: Troubleshooting
    elements.append(Paragraph("12. Troubleshooting Guide", heading_style))
    
    elements.append(Paragraph("12.1 Common Issues and Solutions", subheading_style))
    
    # Troubleshooting table
    trouble_data = [
        ["Issue", "Possible Cause", "Solution"],
        ["Users can't log in", "Password expired, account locked", "Reset password, check account status"],
        ["Payment failures", "Invalid card, insufficient funds", "Contact user, retry payment"],
        ["API errors", "Invalid keys, rate limits", "Verify API keys, check quotas"],
        ["Slow performance", "High traffic, database issues", "Scale resources, optimize queries"],
        ["Video not working", "Browser permissions, connectivity", "Check browser settings, network"]
    ]
    
    trouble_table = Table(trouble_data, colWidths=[1.8*inch, 2*inch, 2.2*inch])
    trouble_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6347')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(trouble_table)
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("12.2 Support Contacts", subheading_style))
    elements.append(Paragraph("Technical Support: support@mindmend.com.au", styles['BodyText']))
    elements.append(Paragraph("Emergency: +61 2 9000 0000 (24/7)", styles['BodyText']))
    elements.append(Paragraph("Documentation: https://docs.mindmend.com.au", styles['BodyText']))
    
    # Build PDF
    doc.build(elements)
    
    return filename

# Create the manual
if __name__ == "__main__":
    filename = create_admin_manual()
    print(f"Admin manual created: {filename}")