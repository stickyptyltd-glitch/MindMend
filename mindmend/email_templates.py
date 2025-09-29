#!/usr/bin/env python3

# Email Templates for MindMend Platform Launch Campaign

class EmailTemplates:
    """
    Professional email templates for MindMend Platform early registration system
    """

    @staticmethod
    def welcome_registration_email(user_name, user_email, user_role="", user_interest=""):
        """
        Thank you email sent immediately after registration
        """
        template = f"""
Subject: 🧠 Welcome to the MindMend Revolution - You're In!

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .logo {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .feature-highlight {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }}
        .cta-button {{
            display: inline-block;
            background: #ff6b6b;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">MindMend</div>
        <h2>🎉 Welcome to the Future of Mental Health!</h2>
    </div>

    <div class="content">
        <h3>Hi {user_name},</h3>

        <p><strong>Thank you for joining our exclusive early access program!</strong></p>

        <p>You're now among the first to know about MindMend - the revolutionary AI-powered mental health platform that's about to transform how we approach therapy and wellness.</p>

        <div class="feature-highlight">
            <h4>🚀 What You Can Expect:</h4>
            <ul>
                <li><strong>Advanced AI Emotion Recognition</strong> - Real-time microexpression analysis</li>
                <li><strong>Multi-Device Therapy Sessions</strong> - Connect from anywhere with secure linking</li>
                <li><strong>Biometric Health Monitoring</strong> - Stress, heart rate, and wellness tracking</li>
                <li><strong>Smart Video Assessment</strong> - AI-powered therapy progress analysis</li>
                <li><strong>Emergency Response System</strong> - Automatic crisis detection and support</li>
            </ul>
        </div>

        {"<p><strong>Professional Interest:</strong> " + user_role.title() + "</p>" if user_role else ""}
        {"<p><strong>Primary Focus:</strong> " + user_interest.replace('-', ' ').title() + "</p>" if user_interest else ""}

        <div class="feature-highlight">
            <h4>🎁 Early Access Benefits:</h4>
            <ul>
                <li>First access to beta testing (coming in 2-4 weeks)</li>
                <li>50% discount on first-year subscription</li>
                <li>Direct feedback channel with our development team</li>
                <li>Exclusive webinar invitation with platform demos</li>
                <li>Priority customer support and training</li>
            </ul>
        </div>

        <p>We'll keep you updated with:</p>
        <ul>
            <li>Development progress and feature previews</li>
            <li>Beta testing opportunities</li>
            <li>Launch date announcements</li>
            <li>Exclusive educational content on AI in mental health</li>
        </ul>

        <div style="text-align: center;">
            <a href="https://mindmend.xyz" class="cta-button">Visit Our Coming Soon Page</a>
        </div>

        <p>Have questions? Simply reply to this email - we read every message personally!</p>

        <p>Welcome aboard the MindMend journey!</p>

        <p><strong>The MindMend Team</strong><br>
        Revolutionizing Mental Health Technology</p>
    </div>

    <div class="footer">
        <p>MindMend Platform © 2024 | Built with ❤️ for mental health and wellness</p>
        <p><small>You received this email because you signed up for early access at mindmend.xyz</small></p>
    </div>
</body>
</html>
        """
        return template.strip()

    @staticmethod
    def launch_announcement_email(user_name, launch_date="Soon"):
        """
        Launch announcement email when platform goes live
        """
        template = f"""
Subject: 🚀 MindMend is LIVE! Your Early Access Awaits

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .logo {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .launch-banner {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            color: white;
            padding: 25px;
            text-align: center;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .cta-button {{
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 20px 40px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.2rem;
            margin: 20px 0;
        }}
        .discount-code {{
            background: #fff3cd;
            border: 2px dashed #ffc107;
            padding: 15px;
            text-align: center;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .feature-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }}
        .feature-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">MindMend</div>
        <h1>🎉 WE'RE LIVE!</h1>
        <h3>The Mental Health Revolution Starts Now</h3>
    </div>

    <div class="content">
        <div class="launch-banner">
            <h2>🚀 MindMend Platform is Now Available!</h2>
            <p style="font-size: 1.1rem; margin: 10px 0;">Your early access is ready - be among the first to experience the future of therapy</p>
        </div>

        <h3>Hi {user_name},</h3>

        <p><strong>The moment you've been waiting for is here!</strong></p>

        <p>MindMend is officially live and your exclusive early access account is ready. As promised, you get first access to all our revolutionary features plus special benefits.</p>

        <div class="discount-code">
            <h4>🎁 Your Exclusive Early Bird Discount</h4>
            <p><strong>Code: EARLY50</strong></p>
            <p>50% off your first year - Valid for 7 days only!</p>
        </div>

        <h4>✨ What's Available Right Now:</h4>

        <div class="feature-grid">
            <div class="feature-item">
                <strong>🧠 AI Emotion Analysis</strong><br>
                Real-time microexpression detection
            </div>
            <div class="feature-item">
                <strong>👥 Group Therapy</strong><br>
                Multi-device session linking
            </div>
            <div class="feature-item">
                <strong>📊 Progress Tracking</strong><br>
                Advanced analytics dashboard
            </div>
            <div class="feature-item">
                <strong>⌚ Biometric Sync</strong><br>
                Heart rate & stress monitoring
            </div>
            <div class="feature-item">
                <strong>🎥 Video Assessment</strong><br>
                Smart therapy evaluations
            </div>
            <div class="feature-item">
                <strong>🆘 Crisis Detection</strong><br>
                Automatic emergency alerts
            </div>
        </div>

        <div style="text-align: center;">
            <a href="https://mindmend.xyz/signup?code=EARLY50" class="cta-button">
                🚀 Start Your Free Trial Now
            </a>
        </div>

        <h4>🎯 Quick Start Guide:</h4>
        <ol>
            <li>Click the button above to access your account</li>
            <li>Complete your profile and preferences</li>
            <li>Take the 2-minute platform tour</li>
            <li>Start your first assessment or therapy session</li>
            <li>Connect your biometric devices (optional)</li>
        </ol>

        <p><strong>Need Help?</strong> Our support team is standing by:</p>
        <ul>
            <li>📧 Email: support@mindmend.xyz (Priority early access queue)</li>
            <li>💬 Live chat available 24/7 on the platform</li>
            <li>📞 Phone: 1-800-MINDMEND (early access hotline)</li>
        </ul>

        <p>Thank you for believing in MindMend from the beginning. We're excited to be part of your mental health journey!</p>

        <p><strong>The MindMend Team</strong><br>
        Making Mental Health Technology Accessible to Everyone</p>
    </div>

    <div class="footer">
        <p>MindMend Platform © 2024 | Built with ❤️ for mental health and wellness</p>
        <p><small>You're receiving this as an early access member. Manage preferences in your account.</small></p>
    </div>
</body>
</html>
        """
        return template.strip()

    @staticmethod
    def beta_testing_invite_email(user_name, beta_link=""):
        """
        Beta testing invitation email
        """
        template = f"""
Subject: 🧪 Exclusive: Beta Test MindMend Before Anyone Else!

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #9c27b0 0%, #673ab7 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .beta-badge {{
            background: #ff9800;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        .testing-focus {{
            background: white;
            padding: 20px;
            border: 2px solid #9c27b0;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .cta-button {{
            display: inline-block;
            background: #9c27b0;
            color: white;
            padding: 18px 35px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="beta-badge">🧪 BETA TESTING</div>
        <h2>You're Invited to Shape the Future!</h2>
        <p>Help us perfect MindMend before public release</p>
    </div>

    <div class="content">
        <h3>Hi {user_name},</h3>

        <p><strong>Congratulations! You've been selected for our exclusive beta testing program.</strong></p>

        <p>As one of our early access members, we'd love your feedback to help us perfect the MindMend platform before public launch.</p>

        <div class="testing-focus">
            <h4>🎯 What We Need Your Help Testing:</h4>
            <ul>
                <li><strong>AI Emotion Recognition Accuracy</strong> - Help us fine-tune detection algorithms</li>
                <li><strong>Multi-Device Session Linking</strong> - Test cross-platform connectivity</li>
                <li><strong>Video Assessment Quality</strong> - Validate therapy analysis features</li>
                <li><strong>Biometric Integration</strong> - Test with various wearable devices</li>
                <li><strong>User Experience Flow</strong> - Overall platform usability</li>
            </ul>
        </div>

        <h4>⏰ Beta Testing Details:</h4>
        <ul>
            <li><strong>Duration:</strong> 2 weeks (flexible scheduling)</li>
            <li><strong>Time Commitment:</strong> 30-60 minutes per week</li>
            <li><strong>Compensation:</strong> Free lifetime access + $100 credit</li>
            <li><strong>Group Size:</strong> Limited to 50 beta testers</li>
        </ul>

        <h4>🎁 Beta Tester Exclusive Benefits:</h4>
        <ul>
            <li>Lifetime free access to MindMend Platform</li>
            <li>$100 platform credit for premium features</li>
            <li>Direct line to development team</li>
            <li>Your name in our "Founding Community" recognition</li>
            <li>Priority access to all future features</li>
        </ul>

        <div style="text-align: center;">
            <a href="{beta_link or 'https://beta.mindmend.xyz/join'}" class="cta-button">
                🚀 Join Beta Testing Program
            </a>
        </div>

        <p><strong>What Happens Next?</strong></p>
        <ol>
            <li>Click the button above to confirm your participation</li>
            <li>Complete a brief pre-testing questionnaire (5 minutes)</li>
            <li>Receive your personalized beta access credentials</li>
            <li>Join our private beta tester Slack community</li>
            <li>Start testing at your convenience</li>
        </ol>

        <p><strong>Questions?</strong> Reply to this email or reach out to our beta coordinator at beta@mindmend.xyz</p>

        <p>Thank you for helping us build something truly revolutionary!</p>

        <p><strong>The MindMend Development Team</strong></p>
    </div>

    <div class="footer">
        <p>MindMend Platform © 2024 | Beta Testing Program</p>
        <p><small>This exclusive invitation expires in 48 hours</small></p>
    </div>
</body>
</html>
        """
        return template.strip()

    @staticmethod
    def progress_update_email(user_name, week_number=1):
        """
        Weekly development progress update email
        """
        updates = {
            1: {
                "milestone": "AI Engine Optimization",
                "progress": "85%",
                "features": ["Improved emotion detection accuracy", "Faster processing speeds", "Enhanced microexpression analysis"],
                "next_week": "Multi-device session testing"
            },
            2: {
                "milestone": "Cross-Platform Integration",
                "progress": "92%",
                "features": ["Seamless device linking", "WebRTC optimization", "Mobile app beta"],
                "next_week": "Biometric device integration"
            },
            3: {
                "milestone": "Security & Compliance",
                "progress": "95%",
                "features": ["HIPAA compliance certification", "End-to-end encryption", "Privacy controls"],
                "next_week": "Final testing phase"
            }
        }

        update_data = updates.get(week_number, updates[1])

        template = f"""
Subject: 📊 MindMend Development Update - Week {week_number}

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .progress-bar {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 20px;
            margin: 10px 0;
        }}
        .progress-fill {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            height: 100%;
            border-radius: 10px;
            width: {update_data['progress']};
            position: relative;
        }}
        .milestone-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #2196F3;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🚀 Development Progress Update</h2>
        <p>Week {week_number} - Building the Future of Mental Health</p>
    </div>

    <div class="content">
        <h3>Hi {user_name},</h3>

        <p>Great progress this week! Here's what the MindMend development team has been working on:</p>

        <div class="milestone-card">
            <h4>🎯 This Week's Milestone: {update_data['milestone']}</h4>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <p><strong>Progress: {update_data['progress']} Complete</strong></p>

            <h5>✅ Completed Features:</h5>
            <ul>
                {"".join(f"<li>{feature}</li>" for feature in update_data['features'])}
            </ul>

            <h5>🔜 Next Week Focus:</h5>
            <p>{update_data['next_week']}</p>
        </div>

        <p><strong>Estimated Launch:</strong> 2-3 weeks remaining</p>

        <p>Stay tuned for more updates!</p>

        <p><strong>The MindMend Team</strong></p>
    </div>
</body>
</html>
        """
        return template.strip()

# Email sending functionality
class EmailSender:
    """
    Email sending functionality for MindMend platform
    """

    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587, sender_email="", sender_password=""):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_email, subject, html_content):
        """
        Send HTML email to recipient
        """
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Create HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()

            return {"success": True, "message": "Email sent successfully"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_welcome_email(self, user_data):
        """Send welcome email after registration"""
        template = EmailTemplates.welcome_registration_email(
            user_data.get('fullName', ''),
            user_data.get('email', ''),
            user_data.get('role', ''),
            user_data.get('interest', '')
        )

        return self.send_email(
            user_data['email'],
            "🧠 Welcome to the MindMend Revolution - You're In!",
            template
        )

    def send_launch_announcement(self, user_data):
        """Send launch announcement email"""
        template = EmailTemplates.launch_announcement_email(user_data.get('fullName', ''))

        return self.send_email(
            user_data['email'],
            "🚀 MindMend is LIVE! Your Early Access Awaits",
            template
        )

# Example usage and testing
if __name__ == "__main__":
    # Test email template generation
    templates = EmailTemplates()

    # Sample user data
    test_user = {
        'fullName': 'Dr. Sarah Johnson',
        'email': 'sarah.johnson@example.com',
        'role': 'therapist',
        'interest': 'ai-analysis'
    }

    print("=== WELCOME EMAIL TEMPLATE ===")
    welcome_email = templates.welcome_registration_email(
        test_user['fullName'],
        test_user['email'],
        test_user['role'],
        test_user['interest']
    )
    print(welcome_email[:500] + "...")

    print("\\n=== LAUNCH ANNOUNCEMENT TEMPLATE ===")
    launch_email = templates.launch_announcement_email(test_user['fullName'])
    print(launch_email[:500] + "...")

    print("\\n=== BETA TESTING INVITE TEMPLATE ===")
    beta_email = templates.beta_testing_invite_email(test_user['fullName'])
    print(beta_email[:500] + "...")

    print("\\nEmail templates generated successfully!")
    print("\\nTo send emails, configure EmailSender with SMTP credentials:")
    print("sender = EmailSender('smtp.gmail.com', 587, 'your_email@gmail.com', 'your_app_password')")
    print("result = sender.send_welcome_email(user_data)")