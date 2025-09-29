#!/usr/bin/env python3

# Create simple test versions of consolidated routes to debug issues

debug_routes = '''
@admin_bp.route('/platform-management-test')
@require_admin_auth
def platform_management_test():
    """Simple test version of platform management"""
    return "<h1>Platform Management Test - Working!</h1>"

@admin_bp.route('/ai-technology-test')
@require_admin_auth
def ai_technology_test():
    """Simple test version of AI technology"""
    return "<h1>AI Technology Test - Working!</h1>"

@admin_bp.route('/therapy-community-test')
@require_admin_auth
def therapy_community_test():
    """Simple test version of therapy community"""
    return "<h1>Therapy Community Test - Working!</h1>"
'''

# Add these test routes to admin_panel.py
with open('/root/MindMend/admin_panel.py', 'r') as f:
    content = f.read()

# Add the debug routes before the existing routes
insert_position = content.find('@admin_bp.route(\'/platform-management\')')
new_content = content[:insert_position] + debug_routes + '\n' + content[insert_position:]

with open('/root/MindMend/admin_panel.py', 'w') as f:
    f.write(new_content)

print("✅ Added debug test routes to admin panel")
print("✅ /admin/platform-management-test")
print("✅ /admin/ai-technology-test")
print("✅ /admin/therapy-community-test")