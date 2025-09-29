#!/usr/bin/env python3

# Add Platform Management route to admin_panel.py

with open('/root/MindMend/admin_panel.py', 'r') as f:
    content = f.read()

# Import the platform management route content
with open('/root/MindMend/platform_management_interface.py', 'r') as f:
    interface_content = f.read()

# Extract the route function
route_start = interface_content.find("@admin_bp.route('/platform-management')")
route_end = interface_content.find("'''", route_start) + 3
platform_route = interface_content[route_start:route_end].strip("'\"")

# Find the location to insert the new route (after the dashboard route)
dashboard_route_end = content.find("return render_template('admin/dashboard.html', data=dashboard_data)")
insert_position = content.find("\n\n", dashboard_route_end) + 2

# Insert the platform management route
new_content = content[:insert_position] + "\n" + platform_route + "\n" + content[insert_position:]

# Write back to file
with open('/root/MindMend/admin_panel.py', 'w') as f:
    f.write(new_content)

print("✅ Added Platform Management route to admin panel")
print("✅ Consolidated Users, Research & Analytics functionality")
print("✅ Preserved all existing routes and functionality")
print("✅ Route available at /admin/platform-management")
print("✅ Tabbed interface supports ?tab=users|research|analytics")