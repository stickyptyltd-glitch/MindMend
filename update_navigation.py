#!/usr/bin/env python3

# Update admin navigation to show consolidated interfaces

with open('/root/MindMend/templates/admin/base.html', 'r') as f:
    content = f.read()

# Define old navigation section to replace
old_nav = '''                <ul class="sidebar-nav">
                    <li><a href="{{ url_for('admin.dashboard') }}" {% if request.endpoint == 'admin.dashboard' %}class="active"{% endif %}>
                        <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                    </a></li>
                    <li><a href="{{ url_for('admin.api_keys') }}" {% if request.endpoint == 'admin.api_keys' %}class="active"{% endif %}>
                        <i class="fas fa-key me-2"></i>API Keys
                    </a></li>
                    <li><a href="{{ url_for('admin.platform_upgrades') }}" {% if request.endpoint == 'admin.platform_upgrades' %}class="active"{% endif %}>
                        <i class="fas fa-rocket me-2"></i>Platform Upgrades
                    </a></li>
                    <li><a href="{{ url_for('admin.business_settings') }}" {% if request.endpoint == 'admin.business_settings' %}class="active"{% endif %}>
                        <i class="fas fa-building me-2"></i>Business Settings
                    </a></li>
                    <li><a href="{{ url_for('admin.user_management') }}" {% if request.endpoint == 'admin.user_management' %}class="active"{% endif %}>
                        <i class="fas fa-users me-2"></i>Users & Counselors
                    </a></li>
                    <li><a href="{{ url_for('admin.financial_overview') }}" {% if request.endpoint == 'admin.financial_overview' %}class="active"{% endif %}>
                        <i class="fas fa-chart-line me-2"></i>Financial Overview
                    </a></li>
                    <li><a href="{{ url_for('admin.system_monitoring') }}" {% if request.endpoint == 'admin.system_monitoring' %}class="active"{% endif %}>
                        <i class="fas fa-server me-2"></i>System Monitoring
                    </a></li>
                    <li><a href="{{ url_for('admin.deployment_tools') }}" {% if request.endpoint == 'admin.deployment_tools' %}class="active"{% endif %}>
                        <i class="fas fa-cloud me-2"></i>Deployment Tools
                    </a></li>
                    <li><a href="{{ url_for('admin.ai_assistant') }}" {% if request.endpoint == 'admin.ai_assistant' %}class="active"{% endif %}>
                        <i class="fas fa-robot me-2"></i>AI Assistant
                    </a></li>
                    <li><a href="{{ url_for('admin.research_management') }}" {% if request.endpoint == 'admin.research_management' %}class="active"{% endif %}>
                        <i class="fas fa-microscope me-2"></i>Research & Data
                    </a></li>
                    <li><a href="{{ url_for('admin.ai_models') }}" {% if request.endpoint == 'admin.ai_models' %}class="active"{% endif %}>
                        <i class="fas fa-brain me-2"></i>AI Models
                    </a></li>
                    <li><a href="{{ url_for('admin.company_documents') }}" {% if request.endpoint == 'admin.company_documents' %}class="active"{% endif %}>
                        <i class="fas fa-file-contract me-2"></i>Company Documents
                    </a></li>
                </ul>'''

# Define new consolidated navigation
new_nav = '''                <ul class="sidebar-nav">
                    <!-- Main Dashboard -->
                    <li><a href="{{ url_for('admin.dashboard') }}" {% if request.endpoint == 'admin.dashboard' %}class="active"{% endif %}>
                        <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                    </a></li>

                    <!-- Consolidated Management Interfaces -->
                    <li class="nav-divider mt-3 mb-2">
                        <small class="text-muted px-3">MANAGEMENT SYSTEMS</small>
                    </li>
                    <li><a href="{{ url_for('admin.platform_management') }}" {% if request.endpoint == 'admin.platform_management' %}class="active"{% endif %}>
                        <i class="fas fa-users-cog me-2 text-primary"></i>Platform Management
                        <small class="d-block text-muted ms-4">Users • Research • Analytics</small>
                    </a></li>
                    <li><a href="{{ url_for('admin.ai_technology') }}" {% if request.endpoint == 'admin.ai_technology' %}class="active"{% endif %}>
                        <i class="fas fa-brain me-2 text-success"></i>AI & Technology
                        <small class="d-block text-muted ms-4">Models • Features • Integrations</small>
                    </a></li>
                    <li><a href="{{ url_for('admin.therapy_community') }}" {% if request.endpoint == 'admin.therapy_community' %}class="active"{% endif %}>
                        <i class="fas fa-heart me-2 text-danger"></i>Therapy & Community
                        <small class="d-block text-muted ms-4">Groups • Tools • Plans</small>
                    </a></li>

                    <!-- System Administration -->
                    <li class="nav-divider mt-3 mb-2">
                        <small class="text-muted px-3">SYSTEM ADMIN</small>
                    </li>
                    <li><a href="{{ url_for('admin.api_keys') }}" {% if request.endpoint == 'admin.api_keys' %}class="active"{% endif %}>
                        <i class="fas fa-key me-2"></i>API Keys
                    </a></li>
                    <li><a href="{{ url_for('admin.platform_upgrades') }}" {% if request.endpoint == 'admin.platform_upgrades' %}class="active"{% endif %}>
                        <i class="fas fa-rocket me-2"></i>Platform Upgrades
                    </a></li>
                    <li><a href="{{ url_for('admin.business_settings') }}" {% if request.endpoint == 'admin.business_settings' %}class="active"{% endif %}>
                        <i class="fas fa-building me-2"></i>Business Settings
                    </a></li>
                    <li><a href="{{ url_for('admin.financial_overview') }}" {% if request.endpoint == 'admin.financial_overview' %}class="active"{% endif %}>
                        <i class="fas fa-chart-line me-2"></i>Financial Overview
                    </a></li>
                    <li><a href="{{ url_for('admin.system_monitoring') }}" {% if request.endpoint == 'admin.system_monitoring' %}class="active"{% endif %}>
                        <i class="fas fa-server me-2"></i>System Monitoring
                    </a></li>
                    <li><a href="{{ url_for('admin.deployment_tools') }}" {% if request.endpoint == 'admin.deployment_tools' %}class="active"{% endif %}>
                        <i class="fas fa-cloud me-2"></i>Deployment Tools
                    </a></li>
                    <li><a href="{{ url_for('admin.company_documents') }}" {% if request.endpoint == 'admin.company_documents' %}class="active"{% endif %}>
                        <i class="fas fa-file-contract me-2"></i>Company Documents
                    </a></li>
                </ul>'''

# Replace the navigation
content = content.replace(old_nav, new_nav)

# Add CSS for navigation dividers
css_addition = '''
        .nav-divider {
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin: 10px 0;
            padding-top: 10px;
        }

        .sidebar-nav a small {
            font-size: 0.75rem;
            opacity: 0.7;
            margin-top: 2px;
        }

        .sidebar-nav a:hover small {
            opacity: 1;
        }'''

# Insert CSS before the closing </style>
content = content.replace('        }', '        }' + css_addition, 1)

# Write back to file
with open('/root/MindMend/templates/admin/base.html', 'w') as f:
    f.write(content)

print("✅ Updated admin navigation with consolidated interfaces")
print("✅ Added Platform Management (Users/Research/Analytics)")
print("✅ Added AI & Technology (Models/Features/Integrations)")
print("✅ Added Therapy & Community (Groups/Tools/Plans)")
print("✅ Organized navigation with clear sections and descriptions")
print("✅ Preserved all existing system administration links")
print("✅ Enhanced visual hierarchy with dividers and subcategories")