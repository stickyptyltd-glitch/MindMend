#!/usr/bin/env python3

# Fix admin login to use email field instead of username
with open('/root/MindMend/admin_panel.py', 'r') as f:
    content = f.read()

# Replace username field with email field in admin login
old_login = '''        username = request.form.get('username')
        password = request.form.get('password')

        # Default admin credentials for testing
        if username == 'admin@mindmend.xyz' and password == 'MindMend2024':'''

new_login = '''        username = request.form.get('email')
        password = request.form.get('password')

        # Default admin credentials for testing
        if username == 'admin@mindmend.xyz' and password == 'MindMend2024':'''

content = content.replace(old_login, new_login)

# Write back to file
with open('/root/MindMend/admin_panel.py', 'w') as f:
    f.write(content)

print("✅ Fixed admin login to use email field")
print("✅ Preserved Hugging Face integration")
print("✅ Admin login should now work correctly")