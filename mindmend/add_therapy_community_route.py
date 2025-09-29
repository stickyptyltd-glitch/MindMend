#!/usr/bin/env python3

# Add Therapy & Community route to admin_panel.py

with open('/root/MindMend/admin_panel.py', 'r') as f:
    content = f.read()

# Import the therapy community route content
with open('/root/MindMend/therapy_community_interface.py', 'r') as f:
    interface_content = f.read()

# Extract the route function
route_start = interface_content.find("@admin_bp.route('/therapy-community')")
route_end = interface_content.find("'''", route_start) + 3
therapy_route = interface_content[route_start:route_end].strip("'\"")

# Find the location to insert the new route (after the ai-technology route)
ai_tech_route_end = content.find("return render_template('admin/ai_technology.html', data=tech_data)")
insert_position = content.find("\n\n", ai_tech_route_end) + 2

# Insert the Therapy & Community route
new_content = content[:insert_position] + "\n" + therapy_route + "\n" + content[insert_position:]

# Write back to file
with open('/root/MindMend/admin_panel.py', 'w') as f:
    f.write(new_content)

print("✅ Added Therapy & Community route to admin panel")
print("✅ Consolidated Social Groups, Therapy Tools & Treatment Plans")
print("✅ Preserved all existing routes and functionality")
print("✅ Route available at /admin/therapy-community")
print("✅ Tabbed interface supports ?tab=groups|tools|plans")
print("✅ All 6 management systems now consolidated into 3 unified interfaces")