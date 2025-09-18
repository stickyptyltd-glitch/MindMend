#!/usr/bin/env python3

# Read the admin_panel.py file
with open('/root/MindMend/admin_panel.py', 'r') as f:
    content = f.read()

# 1. Remove the duplicate ai_models function (lines 327-338)
lines = content.split('\n')
filtered_lines = []
skip_mode = False
skip_count = 0

for i, line in enumerate(lines):
    # Start skipping from ai_models route
    if '@admin_bp.route(\'/ai-models\')' in line:
        skip_mode = True
        skip_count = 0
        continue

    # Count lines to skip (the entire function)
    if skip_mode:
        skip_count += 1
        # Skip until we find the next @admin_bp.route or end of function
        if line.strip().startswith('@admin_bp.route') or (skip_count > 15):
            skip_mode = False
            filtered_lines.append(line)
            continue
        else:
            continue

    filtered_lines.append(line)

# Rebuild content
content = '\n'.join(filtered_lines)

# 2. Remove duplicate AI models menu item from dashboard template
dashboard_template_path = '/root/MindMend/templates/admin/dashboard.html'
with open(dashboard_template_path, 'r') as f:
    dashboard_content = f.read()

# Remove lines containing admin.ai_models but keep admin.ai_model_manager
dashboard_lines = dashboard_content.split('\n')
dashboard_filtered = []

for line in dashboard_lines:
    # Skip lines that reference admin.ai_models but not ai_model_manager
    if 'admin.ai_models' in line and 'ai_model_manager' not in line:
        # Skip this line and the next 2 lines (icon and closing tag)
        continue
    dashboard_filtered.append(line)

dashboard_content = '\n'.join(dashboard_filtered)

# Write back the files
with open('/root/MindMend/admin_panel.py', 'w') as f:
    f.write(content)

with open(dashboard_template_path, 'w') as f:
    f.write(dashboard_content)

print("Admin panel consolidation completed successfully")
print("- Removed duplicate /ai-models route")
print("- Kept /ai-model-manager route")
print("- Updated dashboard navigation")
print("- Ready for Hugging Face integration")