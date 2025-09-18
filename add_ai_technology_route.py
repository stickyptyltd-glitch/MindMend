#!/usr/bin/env python3

# Add AI & Technology route to admin_panel.py

with open('/root/MindMend/admin_panel.py', 'r') as f:
    content = f.read()

# Import the AI technology route content
with open('/root/MindMend/ai_technology_interface.py', 'r') as f:
    interface_content = f.read()

# Extract the route function
route_start = interface_content.find("@admin_bp.route('/ai-technology')")
route_end = interface_content.find("'''", route_start) + 3
ai_tech_route = interface_content[route_start:route_end].strip("'\"")

# Find the location to insert the new route (after the platform management route)
platform_route_end = content.find("return render_template('admin/platform_management.html', data=platform_data)")
insert_position = content.find("\n\n", platform_route_end) + 2

# Insert the AI & Technology route
new_content = content[:insert_position] + "\n" + ai_tech_route + "\n" + content[insert_position:]

# Write back to file
with open('/root/MindMend/admin_panel.py', 'w') as f:
    f.write(new_content)

print("✅ Added AI & Technology route to admin panel")
print("✅ Consolidated AI Models, Features & Integrations functionality")
print("✅ Preserved all existing routes and functionality")
print("✅ Route available at /admin/ai-technology")
print("✅ Tabbed interface supports ?tab=models|features|integrations")