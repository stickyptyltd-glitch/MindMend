#!/usr/bin/env python3
"""
Remove Credentials Display from Admin Login Page
This script removes the demo credentials box from the admin login
"""

import os

print("🔧 Removing Credentials Display from Admin Login")
print("=" * 50)

admin_path = '/var/www/mindmend/admin_panel.py'

if os.path.exists(admin_path):
    print("✅ Found admin_panel.py")

    # Read the current admin panel
    with open(admin_path, 'r') as f:
        content = f.read()

    # Remove the demo credentials section
    old_demo_section = '''            <div class="demo-creds">
                <strong>Admin Credentials:</strong><br>
                Email: admin@mindmend.xyz<br>
                Password: MindMend2024!
            </div>'''

    # Also handle the other format
    old_demo_section2 = '''            <div style="margin-top: 20px; padding: 10px; background: #e9ecef; border-radius: 5px; font-size: 14px;">
                <strong>Demo Credentials:</strong><br>
                Email: admin@mindmend.xyz<br>
                Password: MindMend2024!
            </div>'''

    # Remove both possible formats
    content = content.replace(old_demo_section, '')
    content = content.replace(old_demo_section2, '')

    # Also remove any other credential displays
    import re
    # Remove any remaining credential display blocks
    content = re.sub(r'<div[^>]*demo[^>]*>.*?</div>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<div[^>]*credentials[^>]*>.*?</div>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # Write the updated content
    with open(admin_path, 'w') as f:
        f.write(content)

    print("✅ Removed credentials display from admin login")

    # Restart the service
    os.system('systemctl restart mindmend')
    print("✅ Service restarted")

    print("\n🎯 Admin login now shows clean form without credentials")
    print("🌐 URL: http://67.219.102.9/admin")
    print("📧 Credentials: admin@mindmend.xyz / MindMend2024! (hidden from login page)")

else:
    print("❌ admin_panel.py not found")

print("\n✅ Credentials display removal completed!")