#!/usr/bin/env python3
"""
Add User Registration Functionality
This script adds working user registration routes to the MindMend app
"""

import os

print("🔧 Adding User Registration Functionality")
print("=" * 45)

app_path = '/var/www/mindmend/app.py'

if os.path.exists(app_path):
    print("✅ Found app.py")

    with open(app_path, 'r') as f:
        content = f.read()

    # User registration routes to add
    registration_routes = '''
# User Registration and Authentication Routes

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            # Basic validation
            if not all([name, email, password, confirm_password]):
                flash('All fields are required', 'error')
            elif password != confirm_password:
                flash('Passwords do not match', 'error')
            elif len(password) < 6:
                flash('Password must be at least 6 characters', 'error')
            else:
                # Import database models
                try:
                    from models.database import db, Patient

                    # Check if user already exists
                    existing_user = Patient.query.filter_by(email=email).first()
                    if existing_user:
                        flash('Email already registered', 'error')
                    else:
                        # Create new user
                        new_user = Patient(
                            name=name,
                            email=email,
                            password_hash=generate_password_hash(password),
                            subscription_tier='free'
                        )

                        with app.app_context():
                            db.session.add(new_user)
                            db.session.commit()

                        flash('Registration successful! You can now login.', 'success')
                        return redirect(url_for('login'))

                except Exception as e:
                    flash(f'Registration error: {str(e)}', 'error')

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    # Registration form HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register - MindMend</title>
        <style>
            body { font-family: Arial; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 500px; margin: 50px auto; padding: 30px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
            h2 { color: #333; text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
            input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
            input:focus { border-color: #667eea; outline: none; }
            .btn { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-size: 16px; margin-top: 10px; }
            .btn:hover { background: #5a67d8; }
            .links { text-align: center; margin-top: 20px; }
            .links a { color: #667eea; text-decoration: none; margin: 0 10px; }
            .links a:hover { text-decoration: underline; }
            .flash { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .flash.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .flash.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧠 Join MindMend</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="name">Full Name</label>
                    <input type="text" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required minlength="6">
                </div>
                <div class="form-group">
                    <label for="confirm_password">Confirm Password</label>
                    <input type="password" id="confirm_password" name="confirm_password" required>
                </div>
                <button type="submit" class="btn">Create Account</button>
            </form>
            <div class="links">
                <a href="/login">Already have an account? Login</a> |
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            if not email or not password:
                flash('Email and password required', 'error')
            else:
                try:
                    from models.database import db, Patient

                    user = Patient.query.filter_by(email=email).first()
                    if user and check_password_hash(user.password_hash, password):
                        session['user_logged_in'] = True
                        session['user_email'] = email
                        session['user_name'] = user.name
                        flash('Login successful!', 'success')
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Invalid email or password', 'error')

                except Exception as e:
                    flash(f'Login error: {str(e)}', 'error')

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    # Login form HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - MindMend</title>
        <style>
            body { font-family: Arial; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 400px; margin: 100px auto; padding: 30px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
            h2 { color: #333; text-align: center; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
            input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
            input:focus { border-color: #667eea; outline: none; }
            .btn { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; width: 100%; font-size: 16px; }
            .btn:hover { background: #5a67d8; }
            .links { text-align: center; margin-top: 20px; }
            .links a { color: #667eea; text-decoration: none; margin: 0 10px; }
            .links a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🧠 MindMend Login</h2>
            <form method="POST">
                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            <div class="links">
                <a href="/register">Create Account</a> |
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if not session.get('user_logged_in'):
        return redirect(url_for('login'))

    user_name = session.get('user_name', 'User')
    user_email = session.get('user_email', '')

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - MindMend</title>
        <style>
            body {{ font-family: Arial; margin: 0; background: #f8f9fa; }}
            .header {{ background: #667eea; color: white; padding: 20px; }}
            .container {{ padding: 30px; max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; padding: 25px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .btn {{ background: #28a745; color: white; padding: 12px 20px; text-decoration: none; border-radius: 8px; margin: 10px; display: inline-block; }}
            .btn:hover {{ background: #218838; text-decoration: none; color: white; }}
            .logout {{ background: #dc3545; float: right; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧠 MindMend Dashboard</h1>
            <span>Welcome, {user_name}</span>
            <a href="/logout" class="btn logout">Logout</a>
        </div>
        <div class="container">
            <div class="card">
                <h3>✅ Welcome to MindMend!</h3>
                <p>You are successfully logged in as: <strong>{user_email}</strong></p>
                <p>Your mental health journey starts here.</p>
            </div>
            <div class="card">
                <h3>🚀 Available Features</h3>
                <a href="/therapy" class="btn">Start Therapy Session</a>
                <a href="/profile" class="btn">Manage Profile</a>
                <a href="/health" class="btn">Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user_logged_in', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))
'''

    # Add the routes before the main block
    if 'if __name__ == ' in content:
        content = content.replace('if __name__ == ', f'{registration_routes}\nif __name__ == ')
    else:
        content += registration_routes

    # Update the main homepage to include registration links
    if 'MindMend - Mental Health Support' in content:
        # Add navigation links to the homepage
        new_homepage = '''                <a href="/register" class="btn">Register Account</a>
                <a href="/login" class="btn">Login</a>'''

        content = content.replace('<a href="/admin" class="btn admin-btn">Admin Panel</a>',
                                f'<a href="/admin" class="btn admin-btn">Admin Panel</a>\n                {new_homepage}')

    # Write the updated content
    with open(app_path, 'w') as f:
        f.write(content)

    print("✅ Added user registration and login routes")

    # Restart the service
    os.system('systemctl restart mindmend')
    print("✅ Service restarted")

    print("\n🎯 User Registration URLs:")
    print("   Register: http://67.219.102.9/register")
    print("   Login: http://67.219.102.9/login")
    print("   Dashboard: http://67.219.102.9/dashboard")
    print("\n✅ User registration system ready!")

else:
    print("❌ app.py not found")