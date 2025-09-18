#!/usr/bin/env python3

# Read the admin_panel.py file
with open('/root/MindMend/admin_panel.py', 'r') as f:
    content = f.read()

# Replace the login function with the corrected version
old_login = '''    if request.method == 'POST':
        # Placeholder authentication - replace with proper auth
        username = request.form.get('username')
        password = request.form.get('password')

        # Default admin credentials for testing
        if username == 'admin@mindmend.xyz' and password == 'MindMend2024':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials')'''

new_login = '''    if request.method == 'POST':
        # Get form data - template uses 'email' field, not 'username'
        username = request.form.get('email')  # Fixed: template uses 'email' field
        password = request.form.get('password')

        # Debug logging for troubleshooting
        logger.info(f"Admin login attempt - Email: {username}, Password length: {len(password) if password else 0}")

        # Input validation
        if not username or not password:
            logger.warning("Admin login failed: Missing email or password")
            flash('Please enter both email and password', 'error')
            return render_template('admin/login.html')

        # Sanitize inputs
        username = username.strip().lower()

        # Default admin credentials for testing
        if username == 'admin@mindmend.xyz' and password == 'MindMend2024':
            session['admin_logged_in'] = True
            logger.info(f"Admin login successful for: {username}")
            return redirect(url_for('admin.dashboard'))
        else:
            logger.warning(f"Admin login failed for: {username}")
            flash('Invalid email or password', 'error')'''

# Replace the content
content = content.replace(old_login, new_login)

# Write back to file
with open('/root/MindMend/admin_panel.py', 'w') as f:
    f.write(content)

print("Admin panel login function updated successfully")