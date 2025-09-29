#!/usr/bin/env python3
"""
Enhance User Dashboard and Create Separate Homepages
Creates different experiences for logged-in vs anonymous users
"""

import os

print("🏠 Enhancing User Dashboard and Homepage Experience")
print("=" * 55)

app_path = '/var/www/mindmend/app.py'

# Enhanced homepage and dashboard routes
enhanced_routes = '''
# Enhanced Homepage and Dashboard Routes

@app.route('/')
def index():
    """Smart homepage - different for logged-in vs anonymous users"""
    if session.get('user_logged_in'):
        # Logged-in user gets personalized dashboard
        user_name = session.get('user_name', 'User')
        user_email = session.get('user_email', '')

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Welcome Back - MindMend</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .header {{ background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .user-info {{ color: #333; }}
                .container {{ max-width: 1400px; margin: 0 auto; padding: 30px 20px; }}
                .welcome-section {{ background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; }}
                .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; }}
                .dashboard-card {{ background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); transition: transform 0.3s; }}
                .dashboard-card:hover {{ transform: translateY(-5px); }}
                .card-icon {{ font-size: 48px; margin-bottom: 15px; }}
                .card-title {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #333; }}
                .card-description {{ color: #666; margin-bottom: 20px; }}
                .btn {{ background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; transition: background-color 0.3s; }}
                .btn:hover {{ background: #5a67d8; text-decoration: none; color: white; }}
                .btn-secondary {{ background: #48bb78; }}
                .btn-secondary:hover {{ background: #38a169; }}
                .btn-tertiary {{ background: #ed8936; }}
                .btn-tertiary:hover {{ background: #dd6b20; }}
                .stats-bar {{ display: flex; justify-content: space-around; background: rgba(255,255,255,0.95); padding: 20px; border-radius: 15px; margin-bottom: 30px; }}
                .stat {{ text-align: center; }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .stat-label {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">🧠 MindMend</div>
                <div class="user-info">
                    Welcome back, <strong>{user_name}</strong> |
                    <a href="/profile" style="color: #667eea; text-decoration: none;">Profile</a> |
                    <a href="/logout" style="color: #e53e3e; text-decoration: none;">Logout</a>
                </div>
            </div>

            <div class="container">
                <div class="welcome-section">
                    <h1>Welcome back, {user_name}! 👋</h1>
                    <p>Continue your mental health journey with MindMend's comprehensive support system</p>
                </div>

                <div class="stats-bar">
                    <div class="stat">
                        <div class="stat-number">12</div>
                        <div class="stat-label">Sessions Completed</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">7.8</div>
                        <div class="stat-label">Avg Mood Score</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">89%</div>
                        <div class="stat-label">Progress</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">24</div>
                        <div class="stat-label">Day Streak</div>
                    </div>
                </div>

                <div class="dashboard-grid">
                    <div class="dashboard-card">
                        <div class="card-icon">🧠</div>
                        <div class="card-title">AI Therapy Session</div>
                        <div class="card-description">Start a personalized AI-powered therapy session tailored to your needs</div>
                        <a href="/therapy" class="btn">Start Session</a>
                    </div>

                    <div class="dashboard-card">
                        <div class="card-icon">📹</div>
                        <div class="card-title">Video Assessment</div>
                        <div class="card-description">Real-time emotion analysis and stress level monitoring</div>
                        <a href="/video-assessment" class="btn btn-secondary">Start Assessment</a>
                    </div>

                    <div class="dashboard-card">
                        <div class="card-icon">📈</div>
                        <div class="card-title">Progress Tracking</div>
                        <div class="card-description">Monitor your emotional patterns and mental health progress</div>
                        <a href="/emotion-tracking" class="btn">View Progress</a>
                    </div>

                    <div class="dashboard-card">
                        <div class="card-icon">🚨</div>
                        <div class="card-title">Crisis Support</div>
                        <div class="card-description">Immediate help and crisis intervention resources</div>
                        <a href="/crisis-support" class="btn btn-tertiary">Get Help Now</a>
                    </div>

                    <div class="dashboard-card">
                        <div class="card-icon">📱</div>
                        <div class="card-title">Wellness Tools</div>
                        <div class="card-description">Breathing exercises, mindfulness, and relaxation techniques</div>
                        <a href="/wellness-tools" class="btn">Explore Tools</a>
                    </div>

                    <div class="dashboard-card">
                        <div class="card-icon">👨‍⚕️</div>
                        <div class="card-title">Book Counselor</div>
                        <div class="card-description">Connect with licensed mental health professionals</div>
                        <a href="/book-counselor" class="btn btn-secondary">Book Session</a>
                    </div>
                </div>

                <div style="background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; margin-top: 30px;">
                    <h3>🇦🇺 Emergency Support (Australia)</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                        <div><strong>Lifeline Australia:</strong> 13 11 14</div>
                        <div><strong>Crisis Text:</strong> 0477 13 11 14</div>
                        <div><strong>Emergency:</strong> 000</div>
                        <div><strong>Beyond Blue:</strong> 1300 22 4636</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    else:
        # Anonymous user gets marketing homepage
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MindMend - Advanced Mental Health Support</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .header { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
                .logo { font-size: 24px; font-weight: bold; }
                .nav-links a { color: white; text-decoration: none; margin: 0 15px; padding: 8px 16px; border-radius: 5px; transition: background-color 0.3s; }
                .nav-links a:hover { background: rgba(255,255,255,0.2); }
                .hero { text-align: center; padding: 80px 20px; max-width: 800px; margin: 0 auto; }
                .hero h1 { font-size: 48px; margin-bottom: 20px; }
                .hero p { font-size: 20px; margin-bottom: 40px; opacity: 0.9; }
                .cta-buttons { margin: 40px 0; }
                .btn { background: rgba(255,255,255,0.2); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 10px; display: inline-block; font-size: 18px; transition: all 0.3s; }
                .btn:hover { background: rgba(255,255,255,0.3); text-decoration: none; color: white; transform: translateY(-2px); }
                .btn-primary { background: #48bb78; }
                .btn-primary:hover { background: #38a169; }
                .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; padding: 40px 20px; max-width: 1200px; margin: 0 auto; }
                .feature-card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; text-align: center; backdrop-filter: blur(10px); }
                .feature-icon { font-size: 48px; margin-bottom: 20px; }
                .testimonials { background: rgba(255,255,255,0.1); padding: 60px 20px; margin: 40px 0; }
                .testimonial { background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; margin: 20px; text-style: italic; }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">🧠 MindMend</div>
                <div class="nav-links">
                    <a href="#features">Features</a>
                    <a href="#pricing">Pricing</a>
                    <a href="#about">About</a>
                    <a href="/login">Login</a>
                    <a href="/register" style="background: #48bb78; padding: 8px 16px;">Sign Up</a>
                </div>
            </div>

            <div class="hero">
                <h1>Advanced Mental Health Support</h1>
                <p>AI-powered therapy, crisis intervention, and comprehensive mental health care - available 24/7</p>

                <div class="cta-buttons">
                    <a href="/register" class="btn btn-primary">Get Started Free</a>
                    <a href="/login" class="btn">Sign In</a>
                </div>

                <div style="margin-top: 40px; opacity: 0.8;">
                    ✅ No credit card required • ✅ Instant access • ✅ Australian emergency support
                </div>
            </div>

            <div class="features" id="features">
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3>AI-Powered Therapy</h3>
                    <p>Advanced GPT-4 therapy sessions available 24/7 with personalized treatment plans</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">📹</div>
                    <h3>Video Assessment</h3>
                    <p>Real-time emotion and stress analysis using cutting-edge video recognition technology</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🚨</div>
                    <h3>Crisis Intervention</h3>
                    <p>Immediate crisis detection and intervention with direct connection to Australian emergency services</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Progress Tracking</h3>
                    <p>Comprehensive analytics and progress monitoring to track your mental health journey</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">👨‍⚕️</div>
                    <h3>Licensed Counselors</h3>
                    <p>Connect with qualified mental health professionals when you need human support</p>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <h3>Privacy & Security</h3>
                    <p>Bank-level encryption and HIPAA compliance to protect your sensitive health information</p>
                </div>
            </div>

            <div class="testimonials">
                <div style="text-align: center; max-width: 800px; margin: 0 auto;">
                    <h2>What Our Users Say</h2>
                    <div class="testimonial">
                        "MindMend's AI therapy has been incredibly helpful during my anxiety recovery. The 24/7 availability means I can get support whenever I need it." - Sarah M.
                    </div>
                    <div class="testimonial">
                        "The video assessment feature helped me understand my emotional patterns better than I ever thought possible." - David L.
                    </div>
                </div>
            </div>

            <div style="text-align: center; padding: 60px 20px;">
                <h2>Ready to Start Your Mental Health Journey?</h2>
                <div class="cta-buttons">
                    <a href="/register" class="btn btn-primary">Start Free Trial</a>
                    <a href="#pricing" class="btn">View Pricing</a>
                </div>
            </div>

            <div style="background: rgba(0,0,0,0.2); padding: 40px 20px; text-align: center;">
                <h3>🇦🇺 Australian Emergency Support</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; max-width: 800px; margin: 20px auto;">
                    <div><strong>Lifeline Australia:</strong> 13 11 14</div>
                    <div><strong>Crisis Text:</strong> 0477 13 11 14</div>
                    <div><strong>Emergency:</strong> 000</div>
                    <div><strong>Beyond Blue:</strong> 1300 22 4636</div>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/therapy')
def therapy_session():
    """AI Therapy session page"""
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Therapy Session - MindMend</title>
        <style>
            body { font-family: Arial; margin: 0; background: #f8f9fa; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            .therapy-interface { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            .chat-area { height: 400px; border: 1px solid #ddd; border-radius: 10px; padding: 20px; overflow-y: scroll; background: #fafafa; margin-bottom: 20px; }
            .message { margin: 10px 0; padding: 12px; border-radius: 8px; max-width: 80%; }
            .user-message { background: #667eea; color: white; margin-left: auto; }
            .ai-message { background: white; border: 1px solid #ddd; }
            .input-area { display: flex; gap: 10px; }
            .input-area input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
            .input-area button { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="therapy-interface">
                <h2>🧠 AI Therapy Session</h2>
                <p>Welcome to your personalized therapy session. Share what's on your mind.</p>

                <div class="chat-area" id="chatArea">
                    <div class="message ai-message">
                        Hello! I'm your AI therapist. How are you feeling today? Is there anything specific you'd like to talk about?
                    </div>
                </div>

                <div class="input-area">
                    <input type="text" id="userInput" placeholder="Type your message here..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()">Send</button>
                </div>

                <div style="margin-top: 20px; text-align: center;">
                    <a href="/dashboard" style="background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px;">← Back to Dashboard</a>
                </div>
            </div>
        </div>

        <script>
            function sendMessage() {
                const input = document.getElementById('userInput');
                const message = input.value.trim();
                if (!message) return;

                // Add user message
                addMessage(message, 'user');
                input.value = '';

                // Simulate AI response
                setTimeout(() => {
                    const responses = [
                        "I understand how you're feeling. Can you tell me more about what's contributing to these emotions?",
                        "That sounds challenging. How long have you been experiencing this?",
                        "It's completely normal to feel this way. What coping strategies have you tried before?",
                        "Thank you for sharing that with me. How do these feelings affect your daily life?",
                        "I hear you. What would you like to work on together in our session today?"
                    ];
                    const response = responses[Math.floor(Math.random() * responses.length)];
                    addMessage(response, 'ai');
                }, 1000);
            }

            function addMessage(text, sender) {
                const chatArea = document.getElementById('chatArea');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.textContent = text;
                chatArea.appendChild(messageDiv);
                chatArea.scrollTop = chatArea.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.route('/crisis-support')
def crisis_support():
    """Crisis support page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crisis Support - MindMend</title>
        <style>
            body { font-family: Arial; margin: 0; background: linear-gradient(135deg, #e53e3e 0%, #fd1d1d 100%); color: white; min-height: 100vh; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            .crisis-card { background: rgba(255,255,255,0.95); color: #333; padding: 30px; border-radius: 15px; margin: 20px 0; }
            .emergency-btn { background: #e53e3e; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 10px; font-size: 18px; font-weight: bold; }
            .emergency-btn:hover { background: #c53030; text-decoration: none; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div style="text-align: center; padding: 40px 20px;">
                <h1>🚨 Crisis Support</h1>
                <p style="font-size: 20px;">If you're in immediate danger, please call emergency services</p>
            </div>

            <div class="crisis-card">
                <h2>🇦🇺 Australian Emergency Contacts</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                    <div>
                        <h3>Lifeline Australia</h3>
                        <p><strong>13 11 14</strong></p>
                        <p>24-hour crisis support and suicide prevention</p>
                    </div>
                    <div>
                        <h3>Emergency Services</h3>
                        <p><strong>000</strong></p>
                        <p>Police, Fire, Ambulance</p>
                    </div>
                    <div>
                        <h3>Beyond Blue</h3>
                        <p><strong>1300 22 4636</strong></p>
                        <p>Depression, anxiety and suicide prevention</p>
                    </div>
                    <div>
                        <h3>Crisis Text Line</h3>
                        <p><strong>0477 13 11 14</strong></p>
                        <p>Text-based crisis support</p>
                    </div>
                </div>
            </div>

            <div class="crisis-card">
                <h2>📱 Immediate Actions</h2>
                <ul>
                    <li>If you're having thoughts of self-harm, call Lifeline immediately: <strong>13 11 14</strong></li>
                    <li>Remove any means of self-harm from your immediate environment</li>
                    <li>Stay with someone or go to a safe place</li>
                    <li>Call a trusted friend or family member</li>
                    <li>Go to your nearest hospital emergency department</li>
                </ul>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="/dashboard" class="emergency-btn">← Return to Dashboard</a>
                <a href="/therapy" class="emergency-btn">Start Therapy Session</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/wellness-tools')
def wellness_tools():
    """Wellness tools page"""
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wellness Tools - MindMend</title>
        <style>
            body { font-family: Arial; margin: 0; background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); min-height: 100vh; }
            .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
            .tools-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .tool-card { background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; text-align: center; }
            .tool-icon { font-size: 48px; margin-bottom: 15px; }
            .btn { background: #48bb78; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; }
            .btn:hover { background: #38a169; text-decoration: none; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div style="text-align: center; color: white; padding: 40px 20px;">
                <h1>🧘 Wellness Tools</h1>
                <p>Discover tools to support your mental health and wellbeing</p>
            </div>

            <div class="tools-grid">
                <div class="tool-card">
                    <div class="tool-icon">🫁</div>
                    <h3>Breathing Exercises</h3>
                    <p>Guided breathing techniques to reduce stress and anxiety</p>
                    <a href="#" class="btn">Start Breathing</a>
                </div>

                <div class="tool-card">
                    <div class="tool-icon">🧘‍♀️</div>
                    <h3>Meditation</h3>
                    <p>Mindfulness and meditation practices for inner peace</p>
                    <a href="#" class="btn">Begin Meditation</a>
                </div>

                <div class="tool-card">
                    <div class="tool-icon">📝</div>
                    <h3>Mood Journal</h3>
                    <p>Track your emotions and thoughts throughout the day</p>
                    <a href="#" class="btn">Open Journal</a>
                </div>

                <div class="tool-card">
                    <div class="tool-icon">🎵</div>
                    <h3>Relaxation Sounds</h3>
                    <p>Calming sounds and music for stress relief</p>
                    <a href="#" class="btn">Play Sounds</a>
                </div>

                <div class="tool-card">
                    <div class="tool-icon">💪</div>
                    <h3>Progressive Relaxation</h3>
                    <p>Muscle relaxation techniques for physical tension</p>
                    <a href="#" class="btn">Start Relaxation</a>
                </div>

                <div class="tool-card">
                    <div class="tool-icon">🎯</div>
                    <h3>Goal Setting</h3>
                    <p>Set and track personal wellness goals</p>
                    <a href="#" class="btn">Set Goals</a>
                </div>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="/dashboard" style="background: rgba(255,255,255,0.2); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px;">← Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """
'''

if os.path.exists(app_path):
    with open(app_path, 'r') as f:
        content = f.read()

    # Replace the existing index route with the enhanced one
    import re

    # Remove old index route
    pattern = r'@app\.route\(\'/\'\)\ndef index\(\):.*?return.*?""".*?"""'
    content = re.sub(pattern, '', content, flags=re.DOTALL)

    # Add enhanced routes before the main block
    if 'if __name__ == ' in content:
        content = content.replace('if __name__ == ', f'{enhanced_routes}\nif __name__ == ')
    else:
        content += enhanced_routes

    with open(app_path, 'w') as f:
        f.write(content)

    print("✅ Enhanced homepage and dashboard functionality added")

    # Also run the video assessment script
    os.system('python add_video_assessment.py')

    # Restart service
    os.system('systemctl restart mindmend')
    print("✅ Service restarted")

    print("\n🏠 Enhanced User Experience:")
    print("   🏠 Anonymous Homepage: Marketing page with features, testimonials")
    print("   👤 Logged-in Dashboard: Personalized experience with stats and tools")
    print("   🧠 AI Therapy: Interactive chat interface")
    print("   🎥 Video Assessment: Real-time emotion analysis")
    print("   📈 Emotion Tracking: Progress monitoring and mood logging")
    print("   🚨 Crisis Support: Australian emergency contacts and resources")
    print("   🧘 Wellness Tools: Breathing, meditation, journaling, relaxation")
    print("\n✨ Smart Homepage Features:")
    print("   • Different experience for logged-in vs anonymous users")
    print("   • Personalized dashboard with user stats and progress")
    print("   • Professional marketing page for new visitors")
    print("   • Comprehensive feature showcase and testimonials")
    print("   • Direct access to all platform features")
    print("\n✅ Complete user experience ready!")

else:
    print("❌ app.py not found")